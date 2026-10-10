"""
ClauseGuard AI — Hybrid Database Layer.
If SUPABASE_URL and SUPABASE_SERVICE_KEY are provided, it uses Supabase.
Otherwise, it automatically falls back to local SQLite with zero configuration,
ensuring zero-downtime deployment on Render/local environments without requiring external DB setup.
"""
import os
import json
import sqlite3
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
        USE_SUPABASE = False

# ── SQLite Setup (Zero-config fallback) ─────────────────────────────────────────
_data_dir = Path(os.environ.get("DATA_DIR", str(Path(__file__).resolve().parent.parent.parent / "data")))
_data_dir.mkdir(parents=True, exist_ok=True)
DB_PATH = _data_dir / "clauseguard.db"


def _get_sqlite_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    if USE_SUPABASE and _supabase_client:
        try:
            _supabase_client.table("documents").select("id").limit(1).execute()
            print("[ClauseGuard AI] Connected to Supabase Database ✓")
            return
        except Exception as e:
            print(f"[ClauseGuard AI] Supabase test query failed: {e}")

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
        conn.commit()
    print("[ClauseGuard AI] SQLite Database initialized (Zero-config mode) ✓")


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
        payload = {
            "id": doc_id,
            "filename": filename,
            "total_pages": total_pages,
            "file_size_bytes": file_size_bytes,
            "word_count": word_count,
            "file_path": file_path,
            "raw_text_json": pages_data,
            "user_id": uid,
        }
        _supabase_client.table("documents").upsert(payload).execute()
        return

    # SQLite
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
            file_path,
            json.dumps(pages_data)
        ))
        conn.commit()


def get_document(doc_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if USE_SUPABASE and _supabase_client:
        query = _supabase_client.table("documents").select("*").eq("id", doc_id)
        res = query.maybe_single().execute()
        if not res or not res.data:
            return None
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

    # SQLite
    with _get_sqlite_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
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

    # SQLite
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


def get_analysis(analysis_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if USE_SUPABASE and _supabase_client:
        query = _supabase_client.table("analyses").select("*").eq("id", analysis_id)
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
        cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
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
        if user_id:
            query = query.eq("user_id", user_id)
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
            cursor.execute("SELECT * FROM analyses WHERE document_id = ? ORDER BY created_at DESC LIMIT 1", (document_id,))
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
