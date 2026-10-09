import uuid
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.pdf_service import PDFService, PDFProcessingError
from ..database.db import save_document, get_document

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only PDF files are supported.")

    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if file_size > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum limit of 25MB.")

    doc_id = str(uuid.uuid4())
    saved_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
    with open(saved_path, "wb") as f:
        f.write(file_bytes)

    try:
        pages_data, metadata = PDFService.extract_text_from_bytes(file_bytes)
    except PDFProcessingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error while extracting PDF: {str(e)}")

    if metadata.get("is_scanned_or_empty"):
        # Still store it, but return notice
        pass

    save_document(
        doc_id=doc_id,
        filename=file.filename,
        total_pages=metadata["total_pages"],
        file_size_bytes=file_size,
        word_count=metadata["total_words"],
        file_path=str(saved_path),
        pages_data=pages_data,
    )

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "total_pages": metadata["total_pages"],
        "file_size_bytes": file_size,
        "word_count": metadata["total_words"],
        "is_scanned_or_empty": metadata["is_scanned_or_empty"],
        "has_extractable_text": metadata["has_extractable_text"],
        "pages_preview": [
            {"page_number": p["page_number"], "word_count": p["word_count"], "char_count": p["char_count"]}
            for p in pages_data
        ]
    }

@router.get("/{doc_id}")
def get_document_details(doc_id: str):
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc
