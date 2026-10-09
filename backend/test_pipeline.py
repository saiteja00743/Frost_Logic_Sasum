import sys
import asyncio
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.services.pdf_service import PDFService
from app.services.verification_service import VerificationService
from app.services.analysis_service import AnalysisService
from app.services.report_service import ReportService
from app.database.db import init_db, save_document, save_analysis, get_analysis

async def run_pipeline_test():
    print("--- 1. Testing Database Initialization ---")
    init_db()
    print("Database initialized successfully.")

    print("\n--- 2. Testing PDF Extraction ---")
    msa_path = backend_dir.parent / "sample_documents" / "CloudScale_Enterprise_SaaS_MSA.pdf"
    pages, meta = PDFService.extract_text_from_file(str(msa_path))
    print(f"Extracted {meta['total_pages']} pages, {meta['total_words']} words.")
    assert meta["total_pages"] == 4, f"Expected 4 pages, got {meta['total_pages']}"
    assert meta["has_extractable_text"] is True

    print("\n--- 3. Testing Evidence Verification ---")
    quote = "Customer shall pay Provider the annual subscription fees in the amount of $120,000 USD"
    status, page, match, conf = VerificationService.verify_quote(quote, 2, pages)
    print(f"Quote match status: {status}, Page: {page}, Confidence: {conf}")
    assert status == "verified"
    assert page == 2

    # Negative test (fabricated quote)
    bogus_quote = "This company shall pay one million bitcoins to Mars colony"
    b_status, b_page, _, _ = VerificationService.verify_quote(bogus_quote, 1, pages)
    print(f"Fabricated quote status: {b_status} (Expected: unverified)")
    assert b_status == "unverified"

    print("\n--- 4. Testing End-to-End Analysis ---")
    result = await AnalysisService.analyze_document(
        doc_id="test-doc-123",
        filename="CloudScale_Enterprise_SaaS_MSA.pdf",
        pages_data=pages
    )
    print(f"Contract Type: {result['contract_type']}")
    print(f"Risk Score: {result['risk_score']} / 100")
    print(f"Identified Parties: {[p['name'] for p in result['parties']]}")
    print(f"Identified Risks: {len(result['risks'])}")
    print(f"Identified Obligations: {len(result['obligations'])}")
    print(f"Identified Deadlines: {len(result['deadlines'])}")
    print(f"Identified Key Clauses: {len(result['key_clauses'])}")
    verif = result["verification_summary"]
    print(f"Audit Rate: {verif['verification_rate_percent']}% verified ({verif['verified_count']} of {verif['total_items_checked']})")

    print("\n--- 5. Testing Database Persistence ---")
    save_document("test-doc-123", "CloudScale_Enterprise_SaaS_MSA.pdf", meta["total_pages"], 6596, meta["total_words"], str(msa_path), pages)
    save_analysis("test-analysis-123", "test-doc-123", result, result["engine_used"])
    saved_data = get_analysis("test-analysis-123")
    assert saved_data is not None
    assert saved_data["document_id"] == "test-doc-123"
    print("Database save and retrieve verified.")

    print("\n--- 6. Testing ReportLab PDF Generation ---")
    pdf_bytes = ReportService.generate_pdf_report(result)
    print(f"Report generated: {len(pdf_bytes)} bytes.")
    assert len(pdf_bytes) > 2000

    print("\n==========================================")
    print(">>> ALL BACKEND PIPELINE TESTS PASSED! <<<")
    print("==========================================")

if __name__ == "__main__":
    asyncio.run(run_pipeline_test())
