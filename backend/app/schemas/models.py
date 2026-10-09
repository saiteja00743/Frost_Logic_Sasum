from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    page: Optional[int] = Field(None, description="1-indexed page number in the document")
    quote: str = Field(..., description="Quoted text extracted from the document")
    matched_text: Optional[str] = Field(None, description="Matched substring in source text if verified")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Verification confidence score")

class Risk(BaseModel):
    id: str = Field(..., description="Unique identifier for the risk item")
    title: str = Field(..., description="Short title describing the risk")
    severity: Literal["high", "medium", "low"] = Field(..., description="Risk severity level")
    category: str = Field("General", description="Category: Liability, Termination, Payment, Compliance, IP, etc.")
    explanation: str = Field(..., description="Why this clause matters or poses a risk")
    evidence: Evidence = Field(..., description="Source evidence quotation")
    recommended_action: str = Field(..., description="Actionable verification or renegotiation advice")
    verification_status: Literal["verified", "unverified", "needs_review"] = Field(
        "needs_review", description="Evidence verification status against extracted text"
    )

class Party(BaseModel):
    name: str = Field(..., description="Party name as stated in document")
    role: str = Field(..., description="Role: Customer, Vendor, Landlord, Tenant, Disclosing Party, etc.")
    obligations_count: Optional[int] = Field(0, description="Count of identified obligations")

class Obligation(BaseModel):
    id: str = Field(..., description="Unique identifier")
    responsible_party: str = Field(..., description="Party bound by the obligation")
    obligation: str = Field(..., description="Action or forbearance required")
    evidence: Evidence = Field(..., description="Supporting quotation")
    deadline: Optional[str] = Field("Needs verification", description="Explicit deadline or 'Needs verification'")
    is_conditional: bool = Field(False, description="Whether triggered by a specific event or condition")
    verification_status: Literal["verified", "unverified", "needs_review"] = Field(
        "needs_review", description="Verification status against source text"
    )

class Deadline(BaseModel):
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Description of the deadline or milestone")
    date_or_trigger: str = Field(..., description="Explicit date (e.g., 'October 15, 2026') or trigger condition")
    responsible_party: str = Field(..., description="Party responsible")
    evidence: Evidence = Field(..., description="Supporting quotation")
    is_explicit_date: bool = Field(True, description="True if explicit calendar date, False if event-based")
    verification_status: Literal["verified", "unverified", "needs_review"] = Field(
        "needs_review", description="Verification status"
    )

class KeyClause(BaseModel):
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Clause title, e.g., 'Indemnification', 'Limitation of Liability'")
    category: str = Field(..., description="Classification category")
    summary: str = Field(..., description="Plain-English summary of the clause")
    evidence: Evidence = Field(..., description="Supporting text quotation")
    impact: str = Field(..., description="Commercial or legal impact")

class DocumentPage(BaseModel):
    page_number: int
    text: str
    char_count: int

class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    total_pages: int
    file_size_bytes: int
    word_count: int
    created_at: str

class AnalysisResult(BaseModel):
    document_id: str
    document_name: str
    contract_type: str = "Commercial Agreement"
    total_pages: int
    word_count: int
    document_summary: str
    risk_score: int = Field(..., ge=0, le=100, description="Overall contract risk score from 0 (safe) to 100 (critical)")
    parties: List[Party] = []
    risks: List[Risk] = []
    obligations: List[Obligation] = []
    deadlines: List[Deadline] = []
    key_clauses: List[KeyClause] = []
    engine_used: str = "Intelligent Legal Analysis Engine"
    created_at: str
    verification_summary: dict = Field(default_factory=dict)

class AnalyzeRequest(BaseModel):
    document_id: str
    api_key: Optional[str] = None
    provider: Optional[Literal["openrouter", "openai", "gemini", "auto"]] = "auto"
    custom_model: Optional[str] = None
