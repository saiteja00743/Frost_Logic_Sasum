"""
ClauseGuard AI — Supabase database layer.
Replaces the old SQLite db.py. All queries are user-scoped via Supabase RLS.
"""
import os
import json
from typing import Optional, List, Dict, Any

from supabase import create_client, Client

# ── Supabase client (service-role key bypasses RLS for server-side writes) ──
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY: str = os.environ.get("SUPABASE_SERVICE_KEY", "")

_client: Optional[Client] = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment."
            )
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _client


# ── Compatibility shim: init_db() is a no-op now (Supabase handles schema) ──
def init_db() -> None:
    # Verify connection at startup
    try:
        client = get_supabase()
        client.table("documents").select("id").limit(1).execute()
        print("[ClauseGuard AI] Supabase connection verified ✓")
    except Exception as e:
        print(f"[ClauseGuard AI] Supabase connection warning: {e}")


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
    client = get_supabase()
    payload = {
        "id": doc_id,
        "filename": filename,
        "total_pages": total_pages,
        "file_size_bytes": file_size_bytes,
        "word_count": word_count,
        "file_path": file_path,
        "raw_text_json": pages_data,  # Supabase accepts native Python lists/dicts for JSONB
        "user_id": user_id,
    }
    client.table("documents").upsert(payload).execute()


def get_document(doc_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    client = get_supabase()
    query = client.table("documents").select("*").eq("id", doc_id)
    if user_id:
        query = query.eq("user_id", user_id)
    res = query.maybe_single().execute()
    if not res.data:
        return None
    row = res.data
    return {
        "id": row["id"],
        "filename": row["filename"],
        "total_pages": row["total_pages"],
        "file_size_bytes": row["file_size_bytes"],
        "word_count": row["word_count"],
        "file_path": row["file_path"],
        "pages": row["raw_text_json"],  # already parsed (JSONB)
        "created_at": row["created_at"],
    }


# ─────────────────────── Analyses ─────────────────────────────────────────────

def save_analysis(
    analysis_id: str,
    document_id: str,
    result: Dict[str, Any],
    engine_used: str,
    user_id: Optional[str] = None,
) -> None:
    client = get_supabase()
    payload = {
        "id": analysis_id,
        "document_id": document_id,
        "result_json": result,
        "engine_used": engine_used,
        "risk_score": result.get("risk_score", 0),
        "contract_type": result.get("contract_type", "Agreement"),
        "user_id": user_id,
    }
    client.table("analyses").upsert(payload).execute()


def get_analysis(analysis_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    client = get_supabase()
    query = client.table("analyses").select("*").eq("id", analysis_id)
    if user_id:
        query = query.eq("user_id", user_id)
    res = query.maybe_single().execute()
    if not res.data:
        return None
    row = res.data
    data = row["result_json"]
    data["analysis_id"] = row["id"]
    data["created_at"] = row["created_at"]
    data["document_id"] = row["document_id"]
    return data


def get_latest_analysis_for_doc(document_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    client = get_supabase()
    query = (
        client.table("analyses")
        .select("*")
        .eq("document_id", document_id)
        .order("created_at", desc=True)
        .limit(1)
    )
    if user_id:
        query = query.eq("user_id", user_id)
    res = query.execute()
    if not res.data:
        return None
    row = res.data[0]
    data = row["result_json"]
    data["analysis_id"] = row["id"]
    data["created_at"] = row["created_at"]
    return data


def list_analyses(limit: int = 20, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    client = get_supabase()
    query = (
        client.table("analyses")
        .select("id, document_id, engine_used, risk_score, contract_type, created_at, documents(filename, total_pages)")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if user_id:
        query = query.eq("user_id", user_id)
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
