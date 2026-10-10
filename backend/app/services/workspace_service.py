"""Durable action ledger and in-app reminders. One SQLite store on persistent disk.

Document content may live in Supabase; action writes and their audit events share
one transaction here. A remote database migration is needed for horizontal scale.
"""
import json
import sqlite3
import uuid
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from contextlib import contextmanager

from fastapi import HTTPException
from ..database import db


def now_iso():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect():
    with db._get_sqlite_conn() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 10000")
        yield conn


def init_workspace():
    with connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS contract_actions (
                id TEXT PRIMARY KEY, user_id TEXT NOT NULL, document_id TEXT NOT NULL,
                document_name TEXT NOT NULL, title TEXT NOT NULL, owner TEXT NOT NULL,
                due_date TEXT NOT NULL, timezone TEXT NOT NULL, renewal_date TEXT,
                notice_days INTEGER, notes TEXT NOT NULL, source_json TEXT NOT NULL,
                source_key TEXT, status TEXT NOT NULL DEFAULT 'open', version INTEGER NOT NULL DEFAULT 1,
                schedule_version INTEGER NOT NULL DEFAULT 1,
                confirmed_at TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                UNIQUE(user_id, source_key)
            );
            CREATE INDEX IF NOT EXISTS actions_owner_due ON contract_actions(user_id, due_date);
            CREATE TABLE IF NOT EXISTS action_events (
                id TEXT PRIMARY KEY, action_id TEXT NOT NULL REFERENCES contract_actions(id),
                user_id TEXT NOT NULL, kind TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS action_reminders (
                id TEXT PRIMARY KEY, action_id TEXT NOT NULL REFERENCES contract_actions(id),
                user_id TEXT NOT NULL, schedule_version INTEGER NOT NULL, milestone INTEGER NOT NULL,
                title TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL, read_at TEXT,
                UNIQUE(action_id, schedule_version, milestone)
            );
        """)


def unpack(row):
    result = dict(row)
    result["source"] = json.loads(result.pop("source_json"))
    result.pop("user_id", None)
    result.pop("source_key", None)
    return result


def event(conn, action_id, user_id, kind, detail):
    conn.execute("INSERT INTO action_events VALUES (?, ?, ?, ?, ?, ?)",
                 (str(uuid.uuid4()), action_id, user_id, kind, detail, now_iso()))


def require_action(conn, action_id, user_id):
    row = conn.execute("SELECT * FROM contract_actions WHERE id = ? AND user_id = ?",
                       (action_id, user_id)).fetchone()
    if not row:
        raise HTTPException(404, "Action not found")
    return row


def create_action(payload, user_id):
    doc = db.get_document(payload.document_id, user_id)
    if not doc:
        raise HTTPException(404, "Contract not found")
    source = {}
    source_key = None
    if payload.analysis_id:
        analysis = db.get_analysis(payload.analysis_id, user_id)
        if not analysis or analysis["document_id"] != payload.document_id:
            raise HTTPException(404, "Source analysis not found")
        deadline = next((d for d in analysis.get("deadlines", []) if d["id"] == payload.deadline_id), None)
        if not deadline:
            raise HTTPException(404, "Source deadline not found")
        source = {"analysis_id": payload.analysis_id, "deadline_id": payload.deadline_id,
                  "date_or_trigger": deadline["date_or_trigger"], "evidence": deadline["evidence"],
                  "verification_status": deadline.get("verification_status", "needs_review")}
        source_key = payload.analysis_id + ":" + payload.deadline_id
    values = payload.model_dump(mode="json", exclude={"confirmed", "analysis_id", "deadline_id"})
    stamp = now_iso()
    values.update(id=str(uuid.uuid4()), user_id=user_id, document_name=doc["filename"],
                  source_json=json.dumps(source), source_key=source_key,
                  confirmed_at=stamp, created_at=stamp, updated_at=stamp)
    try:
        with connect() as conn:
            columns = ",".join(values)
            conn.execute(f"INSERT INTO contract_actions ({columns}) VALUES ({','.join('?' for _ in values)})", tuple(values.values()))
            event(conn, values["id"], user_id, "confirmed", json.dumps({
                "owner": payload.owner, "due_date": str(payload.due_date), "timezone": payload.timezone,
                "renewal_date": str(payload.renewal_date) if payload.renewal_date else None,
                "notice_days": payload.notice_days, "note": payload.notes}))
            return unpack(require_action(conn, values["id"], user_id))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "This extracted deadline is already tracked. Edit its existing action.") from exc


def edit_action(action_id, payload, user_id):
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = require_action(conn, action_id, user_id)
        if row["version"] != payload.version:
            raise HTTPException(409, "This action changed. Refresh and try again.")
        if row["status"] != "open":
            raise HTTPException(409, "Reopen this action before editing its deadline.")
        values = payload.model_dump(mode="json", exclude={"version", "confirmed"})
        changed = {k: {"before": row[k], "after": v} for k, v in values.items() if row[k] != v}
        reset = any(k in changed for k in ("due_date", "timezone", "owner"))
        values.update(updated_at=now_iso(), confirmed_at=now_iso(), version=row["version"] + 1,
                      schedule_version=row["schedule_version"] + int(reset))
        conn.execute(f"UPDATE contract_actions SET {','.join(k + '=?' for k in values)} WHERE id=? AND user_id=?",
                     (*values.values(), action_id, user_id))
        event(conn, action_id, user_id, "updated", json.dumps(changed))
        return unpack(require_action(conn, action_id, user_id))


def change_status(action_id, payload, user_id):
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = require_action(conn, action_id, user_id)
        if row["version"] != payload.version:
            raise HTTPException(409, "This action changed. Refresh and try again.")
        if row["status"] == payload.status:
            raise HTTPException(409, "Action already has this status.")
        conn.execute("""UPDATE contract_actions SET status=?, version=version+1,
                        schedule_version=schedule_version+?, updated_at=? WHERE id=? AND user_id=?""",
                     (payload.status, int(payload.status == "open"), now_iso(), action_id, user_id))
        event(conn, action_id, user_id, payload.status, payload.note)
        return unpack(require_action(conn, action_id, user_id))


def deliver_reminders(user_id=None, now=None):
    """Persist one current milestone; catch up after downtime without a stale burst.

    INSERT OR IGNORE plus a unique schedule/milestone key prevents duplicate
    delivery across scheduler ticks. Completed/cancelled actions are excluded.
    """
    now = now or datetime.now(timezone.utc)
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        query = "SELECT * FROM contract_actions WHERE status='open'"
        rows = conn.execute(query + (" AND user_id=?" if user_id else ""), (user_id,) if user_id else ()).fetchall()
        for row in rows:
            today = now.astimezone(ZoneInfo(row["timezone"])).date()
            days = (date.fromisoformat(row["due_date"]) - today).days
            milestones = [m for m in (30, 7, 1, 0, -1) if days <= m]
            if not milestones:
                continue
            milestone = min(milestones)
            label = "Overdue" if days < 0 else "Due today" if days == 0 else f"Due in {days} days"
            conn.execute("""INSERT OR IGNORE INTO action_reminders
                (id, action_id, user_id, schedule_version, milestone, title, detail, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), row["id"], row["user_id"], row["schedule_version"], milestone,
                 f"{label}: {row['title']}", f"{row['owner']} · {row['document_name']} · {row['due_date']}", now.isoformat()))


def workspace(user_id):
    deliver_reminders(user_id)
    with connect() as conn:
        actions = [unpack(r) for r in conn.execute("SELECT * FROM contract_actions WHERE user_id=? ORDER BY due_date, created_at", (user_id,))]
        # Superseded and closed schedules remain in the ledger, not the live inbox.
        reminders = [dict(r) for r in conn.execute("""SELECT r.* FROM action_reminders r
            JOIN contract_actions a ON a.id=r.action_id
            WHERE r.user_id=? AND a.user_id=? AND a.status='open'
            AND r.schedule_version=a.schedule_version ORDER BY r.created_at DESC LIMIT 100""", (user_id, user_id))]
    return {"actions": actions, "reminders": reminders,
            "reminder_channel": "in_app", "reminder_days": [30, 7, 1, 0],
            "demo": user_id.startswith("demo_")}


def action_events(action_id, user_id):
    with connect() as conn:
        require_action(conn, action_id, user_id)
        return [dict(r) for r in conn.execute("SELECT kind, detail, created_at FROM action_events WHERE action_id=? AND user_id=? ORDER BY rowid DESC", (action_id, user_id))]


def read_reminder(reminder_id, user_id):
    with connect() as conn:
        result = conn.execute("UPDATE action_reminders SET read_at=COALESCE(read_at, ?) WHERE id=? AND user_id=?", (now_iso(), reminder_id, user_id))
        if result.rowcount == 0:
            raise HTTPException(404, "Reminder not found")


def calendar_file(action_id, user_id):
    with connect() as conn:
        row = require_action(conn, action_id, user_id)
        if row["status"] != "open":
            raise HTTPException(409, "Calendar export is only available for open actions")
        row = dict(row)
    def escape(value):
        return str(value).replace("\\", "\\\\").replace("\r", "").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")
    due = date.fromisoformat(row["due_date"])
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ClauseGuard//Actions//EN", "CALSCALE:GREGORIAN",
             "BEGIN:VEVENT", f"UID:{action_id}@clauseguard", f"SEQUENCE:{row['version']}",
             "DTSTAMP:" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
             "DTSTART;VALUE=DATE:" + due.strftime("%Y%m%d"),
             "DTEND;VALUE=DATE:" + (due + timedelta(days=1)).strftime("%Y%m%d"),
             "SUMMARY:" + escape(row["title"]),
             "DESCRIPTION:" + escape(f"Owner: {row['owner']}\nContract: {row['document_name']}\n{row['notes']}\nConfirmed in ClauseGuard. This export does not sync changes.")]
    for days in (30, 7, 1, 0):
        lines.extend(["BEGIN:VALARM", f"TRIGGER:-P{days}D", "ACTION:DISPLAY", "DESCRIPTION:Contract deadline", "END:VALARM"])
    lines.extend(["END:VEVENT", "END:VCALENDAR"])
    # RFC 5545: fold at 75 octets without splitting a UTF-8 character.
    folded = []
    for line in lines:
        part = ""
        for char in line:
            if len((part + char).encode("utf-8")) > 75:
                folded.append(part)
                part = " "
            part += char
        folded.append(part)
    return "\r\n".join(folded) + "\r\n"
