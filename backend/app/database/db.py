"""
ClauseGuard AI — Hybrid Database Layer.
If SUPABASE_URL and SUPABASE_SERVICE_KEY are provided, it uses Supabase.
Otherwise, it automatically falls back to local SQLite with zero configuration,
ensuring zero-downtime deployment on Render/local environments without requiring external DB setup.
"""
import os
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict, Any

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY: str = os.environ.get("SUPABASE_SERVICE_KEY", "")

USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_SERVICE_KEY and SUPABASE_URL != "https://your-project-ref.supabase.co")

_supabase_client = None

if USE_SUPABASE:
    try:
        from supabase import create_client, Client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        print(f"[ClauseGuard AI] Supabase initialization failed ({e}), falling back to SQLite.")
        raise RuntimeError("Configured Supabase storage could not initialize") from e

# ── SQLite Setup (Zero-config fallback) ─────────────────────────────────────────
_data_dir = Path(os.environ.get("DATA_DIR", str(Path(__file__).resolve().parent.parent.parent / "data")))
_data_dir.mkdir(parents=True, exist_ok=True)
DB_PATH = _data_dir / "clauseguard.db"


@contextmanager
def _get_sqlite_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db() -> None:
    if USE_SUPABASE and _supabase_client:
        try:
            _supabase_client.table("documents").select("id").limit(1).execute()
            print("[ClauseGuard AI] Connected to Supabase Database")
            return
        except Exception as e:
            print(f"[ClauseGuard AI] Supabase test query failed: {e}")
            raise

    # Fallback to SQLite initialization
    with _get_sqlite_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'guest_user',
                filename TEXT NOT NULL,
                total_pages INTEGER NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                word_count INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                raw_text_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'guest_user',
                document_id TEXT NOT NULL,
                result_json TEXT NOT NULL,
                engine_used TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                contract_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
        """)
        for table in ("documents", "analyses"):
            columns = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})")}
            if "user_id" not in columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id TEXT DEFAULT 'guest_user'")
        conn.commit()
    print("[ClauseGuard AI] SQLite Database initialized (Zero-config mode)")


# ─────────────────────── Documents ────────────────────────────────────────────

def save_document(
    doc_id: str,
    filename: str,
    total_pages: int,
    file_size_bytes: int,
    word_count: int,
    file_path: str,
    pages_data: List[Dict[str, Any]],
    user_id: Optional[str] = None,
) -> None:
    uid = user_id or "guest_user"
    if USE_SUPABASE and _supabase_client:
        try:
            payload = {
                "id": doc_id,
                "filename": filename,
                "total_pages": total_pages,
                "file_size_bytes": file_size_bytes,
                "word_count": word_count,
                "file_path": str(file_path),
                "raw_text_json": pages_data,
                "user_id": uid,
            }
            _supabase_client.table("documents").upsert(payload).execute()
            return
        except Exception as e:
            print(f"[ClauseGuard AI] Supabase save_document failed ({e}), falling back to SQLite.")
            raise

    # SQLite
    try:
        with _get_sqlite_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO documents 
                (id, user_id, filename, total_pages, file_size_bytes, word_count, file_path, raw_text_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                uid,
                filename,
                total_pages,
                file_size_bytes,
                word_count,
                str(file_path),
                json.dumps(pages_data)
            ))
            conn.commit()
    except Exception as e:
        print(f"[ClauseGuard AI] SQLite save_document error: {e}")
        raise


def get_document(doc_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if USE_SUPABASE and _supabase_client:
        try:
            query = _supabase_client.table("documents").select("*").eq("id", doc_id).eq("user_id", user_id or "guest_user")
            res = query.maybe_single().execute()
            if res and res.data:
                row = res.data
                return {
                    "id": row["id"],
                    "filename": row["filename"],
                    "total_pages": row["total_pages"],
                    "file_size_bytes": row["file_size_bytes"],
                    "word_count": row["word_count"],
                    "file_path": row["file_path"],
                    "pages": row["raw_text_json"],
                    "created_at": row["created_at"],
                }
        except Exception as e:
            print(f"[ClauseGuard AI] Supabase get_document error: {e}, falling back to SQLite.")
            raise

    # SQLite
    try:
        with _get_sqlite_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id or "guest_user"))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "filename": row["filename"],
                "total_pages": row["total_pages"],
                "file_size_bytes": row["file_size_bytes"],
                "word_count": row["word_count"],
                "file_path": row["file_path"],
                "pages": json.loads(row["raw_text_json"]),
                "created_at": row["created_at"]
            }
    except Exception as e:
        print(f"[ClauseGuard AI] SQLite get_document error: {e}")
        raise
        return None


# ─────────────────────── Analyses ─────────────────────────────────────────────

def save_analysis(
    analysis_id: str,
    document_id: str,
    result: Dict[str, Any],
    engine_used: str,
    user_id: Optional[str] = None,
) -> None:
    uid = user_id or "guest_user"
    if USE_SUPABASE and _supabase_client:
        try:
            payload = {
                "id": analysis_id,
                "document_id": document_id,
                "result_json": result,
                "engine_used": engine_used,
                "risk_score": result.get("risk_score", 0),
                "contract_type": result.get("contract_type", "Agreement"),
                "user_id": uid,
            }
            _supabase_client.table("analyses").upsert(payload).execute()
            return
        except Exception as e:
            print(f"[ClauseGuard AI] Supabase save_analysis failed ({e}), falling back to SQLite.")
            raise

    # SQLite
    try:
        with _get_sqlite_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO analyses
                (id, user_id, document_id, result_json, engine_used, risk_score, contract_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                uid,
                document_id,
                json.dumps(result),
                engine_used,
                result.get("risk_score", 0),
                result.get("contract_type", "Agreement")
            ))
            conn.commit()
    except Exception as e:
        print(f"[ClauseGuard AI] SQLite save_analysis error: {e}")
        raise


def get_analysis(analysis_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if USE_SUPABASE and _supabase_client:
        query = _supabase_client.table("analyses").select("*").eq("id", analysis_id).eq("user_id", user_id or "guest_user")
        res = query.maybe_single().execute()
        if not res or not res.data:
            return None
        row = res.data
        data = row["result_json"]
        data["analysis_id"] = row["id"]
        data["created_at"] = row["created_at"]
        data["document_id"] = row["document_id"]
        return data

    # SQLite
    with _get_sqlite_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id or "guest_user"))
        row = cursor.fetchone()
        if not row:
            return None
        data = json.loads(row["result_json"])
        data["analysis_id"] = row["id"]
        data["created_at"] = row["created_at"]
        data["document_id"] = row["document_id"]
        return data


def get_latest_analysis_for_doc(document_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if USE_SUPABASE and _supabase_client:
        query = (
            _supabase_client.table("analyses")
            .select("*")
            .eq("document_id", document_id)
            .order("created_at", desc=True)
            .limit(1)
        )
        query = query.eq("user_id", user_id or "guest_user")
        res = query.execute()
        if not res or not res.data:
            return None
        row = res.data[0]
        data = row["result_json"]
        data["analysis_id"] = row["id"]
        data["created_at"] = row["created_at"]
        return data

    # SQLite
    with _get_sqlite_conn() as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM analyses WHERE document_id = ? AND user_id = ? ORDER BY created_at DESC LIMIT 1", (document_id, user_id))
        else:
            cursor.execute("SELECT * FROM analyses WHERE document_id = ? AND user_id = ? ORDER BY created_at DESC LIMIT 1", (document_id, "guest_user"))
        row = cursor.fetchone()
        if not row:
            return None
        data = json.loads(row["result_json"])
        data["analysis_id"] = row["id"]
        data["created_at"] = row["created_at"]
        return data


def list_analyses(limit: int = 20, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    # Strict per-user isolation: if no user_id is provided, never expose any analyses
    if not user_id:
        return []

    if USE_SUPABASE and _supabase_client:
        query = (
            _supabase_client.table("analyses")
            .select("id, document_id, engine_used, risk_score, contract_type, created_at, documents(filename, total_pages)")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
        )
        res = query.execute()
        rows = res.data or []

        result = []
        for row in rows:
            doc_info = row.get("documents") or {}
            result.append({
                "id": row["id"],
                "document_id": row["document_id"],
                "engine_used": row["engine_used"],
                "risk_score": row["risk_score"],
                "contract_type": row["contract_type"],
                "created_at": row["created_at"],
                "filename": doc_info.get("filename", ""),
                "total_pages": doc_info.get("total_pages", 0),
            })
        return result

    # SQLite
    with _get_sqlite_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.document_id, a.engine_used, a.risk_score, a.contract_type, a.created_at,
                   d.filename, d.total_pages
            FROM analyses a
            JOIN documents d ON a.document_id = d.id
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC
            LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def list_contracts(user_id: str):
    if USE_SUPABASE and _supabase_client:
        rows = []
        offset = 0
        while True:
            batch = (_supabase_client.table("documents")
                     .select("id,filename,total_pages,created_at").eq("user_id", user_id)
                     .order("created_at", desc=True).range(offset, offset + 499).execute().data or [])
            rows.extend(batch)
            if len(batch) < 500:
                break
            offset += 500
    else:
        with _get_sqlite_conn() as conn:
            rows = [dict(r) for r in conn.execute(
                "SELECT id,filename,total_pages,created_at FROM documents WHERE user_id=? ORDER BY created_at DESC", (user_id,))]
    for row in rows:
        analysis = get_latest_analysis_for_doc(row["id"], user_id)
        row["analysis_id"] = analysis.get("analysis_id") if analysis else None
        row["contract_type"] = analysis.get("contract_type", "Agreement") if analysis else "Awaiting analysis"
        row["deadline_count"] = len(analysis.get("deadlines", [])) if analysis else 0
    return rows
