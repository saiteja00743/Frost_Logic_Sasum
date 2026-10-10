import uuid
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ..services.pdf_service import PDFService, PDFProcessingError
from ..database.db import save_document, get_document
from ..auth.deps import get_current_user

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Use DATA_DIR env var for Render persistent disk (/data/uploads), fallback to local uploads/
_data_dir = Path(os.environ.get("DATA_DIR", str(Path(__file__).resolve().parent.parent.parent)))
UPLOAD_DIR = _data_dir / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    filename = Path((file.filename or "contract.pdf").replace("\\", "/")).name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")
    file_bytes = await file.read(25 * 1024 * 1024 + 1)
    if not file_bytes:
        raise HTTPException(400, "Uploaded file is empty.")
    if len(file_bytes) > 25 * 1024 * 1024:
        raise HTTPException(413, "File exceeds the 25 MB limit.")
    try:
        pages_data, metadata = PDFService.extract_text_from_bytes(file_bytes)
    except PDFProcessingError as exc:
        raise HTTPException(422, str(exc))
    if any(not p["text"].strip() for p in pages_data):
        raise HTTPException(422, "Some pages have no searchable text. Apply OCR to scanned pages and upload again.")
    if len(pages_data) > 100 or metadata["total_chars"] > 250000:
        raise HTTPException(422, "This release supports up to 100 pages and 250,000 text characters per document.")
    doc_id = str(uuid.uuid4())
    file_size = len(file_bytes)
    saved_path = UPLOAD_DIR / f"{doc_id}.pdf"
    try:
        saved_path.write_bytes(file_bytes)
        save_document(doc_id=doc_id, filename=filename, total_pages=metadata["total_pages"],
                      file_size_bytes=file_size, word_count=metadata["total_words"],
                      file_path=str(saved_path), pages_data=pages_data, user_id=user_id)
    except Exception:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(503, "The contract could not be saved. Please retry.")

    return {
        "document_id": doc_id,
        "filename": filename,
        "total_pages": metadata["total_pages"],
        "file_size_bytes": file_size,
        "word_count": metadata["total_words"],
        "is_scanned_or_empty": metadata["is_scanned_or_empty"],
        "has_extractable_text": metadata["has_extractable_text"],
        "pages_preview": [
            {"page_number": p["page_number"], "word_count": p["word_count"], "char_count": p["char_count"]}
            for p in pages_data
        ],
    }


@router.get("/{doc_id}")
def get_document_details(
    doc_id: str,
    user_id: str = Depends(get_current_user),
):
    doc = get_document(doc_id, user_id=user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc
