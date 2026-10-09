import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Response
from ..schemas.models import AnalyzeRequest
from ..database.db import get_document, save_analysis, get_analysis
from ..services.analysis_service import AnalysisService
from ..services.report_service import ReportService

router = APIRouter(prefix="/api", tags=["analysis"])

@router.post("/analyze")
async def analyze_document(request: AnalyzeRequest):
    doc = get_document(request.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if not doc.get("pages"):
        raise HTTPException(status_code=400, detail="Document contains no extractable text pages.")

    try:
        analysis_data = await AnalysisService.analyze_document(
            doc_id=request.document_id,
            filename=doc["filename"],
            pages_data=doc["pages"],
            api_key=request.api_key,
            provider=request.provider,
            custom_model=request.custom_model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    analysis_id = str(uuid.uuid4())
    save_analysis(
        analysis_id=analysis_id,
        document_id=request.document_id,
        result=analysis_data,
        engine_used=analysis_data.get("engine_used", "ClauseGuard Engine")
    )
    analysis_data["analysis_id"] = analysis_id

    return analysis_data

@router.get("/analyses/{analysis_id}")
def get_analysis_result(analysis_id: str):
    data = get_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="Analysis result not found.")
    return data

@router.get("/analyses/{analysis_id}/report")
def download_pdf_report(analysis_id: str):
    data = get_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="Analysis result not found.")

    try:
        pdf_bytes = ReportService.generate_pdf_report(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")

    doc_name = data.get("document_name", "Agreement").replace(".pdf", "")
    filename = f"ClauseGuard_Report_{doc_name}_{analysis_id[:8]}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
