import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from ..database.db import list_analyses, save_document, get_document, save_analysis
from ..services.pdf_service import PDFService
from ..services.analysis_service import AnalysisService
from ..auth.deps import get_current_user

router = APIRouter(prefix="/api", tags=["history_and_samples"])


# Resolve sample_documents directory robustly
def get_sample_docs_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parents[3] / "sample_documents",
        Path(__file__).resolve().parents[2] / "sample_documents",
        Path.cwd() / "sample_documents",
        Path.cwd().parent / "sample_documents",
    ]
    for p in candidates:
        if p.exists() and (p / "CloudScale_Enterprise_SaaS_MSA.pdf").exists():
            return p
    return candidates[0]


SAMPLE_DOCS_DIR = get_sample_docs_dir()


@router.get("/history")
def get_analysis_history(
    limit: int = 20,
    user_id: str = Depends(get_current_user),
):
    """Return the authenticated user's analysis history."""
    return list_analyses(limit=limit, user_id=user_id)


@router.get("/samples")
def get_available_samples():
    """Sample contracts list — public, no auth required."""
    return [
        {
            "id": "saas_msa",
            "name": "CloudScale_Enterprise_SaaS_MSA.pdf",
            "type": "Master Services Agreement (MSA)",
            "description": "High-risk enterprise software agreement with aggressive 60-day auto-renewal, unilateral indemnity, and uncapped consequential exposures.",
            "pages": 4,
            "highlight": "High Risk — Unilateral Indemnity & Auto-Renewal",
        },
        {
            "id": "commercial_lease",
            "name": "MetroTower_Commercial_Office_Lease.pdf",
            "type": "Commercial Lease Agreement",
            "description": "Commercial tenancy lease with security deposit forfeiture, maintenance liability, late interest rates, and insurance requirements.",
            "pages": 3,
            "highlight": "Medium Risk — Deposit Forfeiture & Maintenance",
        },
        {
            "id": "mutual_nda",
            "name": "Apex_Innovations_Mutual_NDA.pdf",
            "type": "Non-Disclosure Agreement (NDA)",
            "description": "Bilateral confidentiality agreement covering proprietary technical trade secrets, 5-year survival period, and non-solicitation.",
            "pages": 2,
            "highlight": "Standard Risk — 5-Year Survival & Return of Data",
        },
    ]


from typing import Optional
from pydantic import BaseModel

class SampleLoadRequest(BaseModel):
    api_key: Optional[str] = None
    provider: Optional[str] = "auto"
    custom_model: Optional[str] = None


@router.post("/sample/load/{sample_key}")
async def load_and_analyze_sample(
    sample_key: str,
    payload: Optional[SampleLoadRequest] = None,
    user_id: str = Depends(get_current_user),
):
    sample_files = {
        "saas_msa": "CloudScale_Enterprise_SaaS_MSA.pdf",
        "commercial_lease": "MetroTower_Commercial_Office_Lease.pdf",
        "mutual_nda": "Apex_Innovations_Mutual_NDA.pdf",
    }

    if sample_key not in sample_files:
        raise HTTPException(status_code=404, detail="Sample agreement not found.")

    filename = sample_files[sample_key]
    pdf_path = SAMPLE_DOCS_DIR / filename

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample PDF file {filename} does not exist on disk.")

    pages_data, metadata = PDFService.extract_text_from_file(str(pdf_path))
    doc_id = str(uuid.uuid4())

    save_document(
        doc_id=doc_id,
        filename=filename,
        total_pages=metadata["total_pages"],
        file_size_bytes=pdf_path.stat().st_size,
        word_count=metadata["total_words"],
        file_path=str(pdf_path),
        pages_data=pages_data,
        user_id=user_id,
    )

    api_key = payload.api_key if payload else None
    provider = payload.provider if payload else "auto"
    custom_model = payload.custom_model if payload else None

    analysis_data = await AnalysisService.analyze_document(
        doc_id=doc_id,
        filename=filename,
        pages_data=pages_data,
        api_key=api_key,
        provider=provider,
        custom_model=custom_model,
    )

    analysis_id = str(uuid.uuid4())
    save_analysis(
        analysis_id=analysis_id,
        document_id=doc_id,
        result=analysis_data,
        engine_used=analysis_data.get("engine_used", "ClauseGuard Engine"),
        user_id=user_id,
    )
    analysis_data["analysis_id"] = analysis_id
    analysis_data["document_id"] = doc_id

    return analysis_data
