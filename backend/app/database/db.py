import sqlite3
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# Use DATA_DIR env var for Render persistent disk (/data), fallback to local data/
_data_dir = Path(os.environ.get("DATA_DIR", str(Path(__file__).resolve().parent.parent.parent / "data")))
_data_dir.mkdir(parents=True, exist_ok=True)
DB_PATH = _data_dir / "clauseguard.db"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
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

def save_document(doc_id: str, filename: str, total_pages: int, file_size_bytes: int,
                  word_count: int, file_path: str, pages_data: List[Dict[str, Any]]) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO documents 
            (id, filename, total_pages, file_size_bytes, word_count, file_path, raw_text_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            filename,
            total_pages,
            file_size_bytes,
            word_count,
            file_path,
            json.dumps(pages_data)
        ))
        conn.commit()

def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
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

def save_analysis(analysis_id: str, document_id: str, result: Dict[str, Any], engine_used: str) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO analyses
            (id, document_id, result_json, engine_used, risk_score, contract_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            analysis_id,
            document_id,
            json.dumps(result),
            engine_used,
            result.get("risk_score", 0),
            result.get("contract_type", "Agreement")
        ))
        conn.commit()

def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        if not row:
            return None
        data = json.loads(row["result_json"])
        data["analysis_id"] = row["id"]
        data["created_at"] = row["created_at"]
        return data

def get_latest_analysis_for_doc(document_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analyses WHERE document_id = ? ORDER BY created_at DESC LIMIT 1", (document_id,))
        row = cursor.fetchone()
        if not row:
            return None
        data = json.loads(row["result_json"])
        data["analysis_id"] = row["id"]
        data["created_at"] = row["created_at"]
        return data

def list_analyses(limit: int = 20) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.document_id, a.engine_used, a.risk_score, a.contract_type, a.created_at,
                   d.filename, d.total_pages
            FROM analyses a
            JOIN documents d ON a.document_id = d.id
            ORDER BY a.created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
