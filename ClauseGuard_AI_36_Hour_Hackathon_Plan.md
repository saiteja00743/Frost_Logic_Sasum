# ClauseGuard AI — 36-Hour Hackathon Implementation Plan

> **Problem statement:** Analyze legal or business documents to extract risks, deadlines, obligations and key clauses.  
> **Mission:** Build a working, polished MVP that turns documents into traceable findings and actionable next steps.  
> **Important:** A hackathon win cannot be guaranteed. Prioritize a reliable end-to-end demo, evidence-backed analysis, and clear communication of limitations.

---

## 1. Product Overview

**ClauseGuard AI** is an AI-powered contract and business-document intelligence platform.

Users upload a PDF and receive:
- A concise document summary
- Parties and their roles
- Key clauses
- Potential risks with source evidence
- Obligations and responsible parties
- Explicit dates and deadlines
- A downloadable analysis report

### Core workflow

**Upload → Extract → Analyze → Verify → Review → Export**

The app assists human review; it does not replace a qualified legal professional.

## 2. Product Differentiator

### Evidence-Linked Risk Analysis

Every finding should show:
1. **Finding:** What the system noticed
2. **Evidence:** The exact supporting passage
3. **Source:** Page number, when reliably available
4. **Explanation:** Why it may matter
5. **Suggested action:** What the user should verify or do
6. **Verification status:** Whether the quotation was matched against extracted text

Never fabricate clauses, quotations, dates, page numbers, or legal conclusions. If evidence cannot be verified, mark the finding as unverified.

### Obligation Tracker

Display the responsible party, obligation, source passage, deadline (if explicitly supported), and verification status. If the date cannot be determined reliably, show **“Needs verification”** rather than inventing one.

### Risk Dashboard

Group potential findings by priority, explain why each was flagged, and allow users to inspect the source text. Treat severity as a review aid—not an objective probability of legal harm.

## 3. Recommended Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| Frontend | React + Vite | User interface |
| Styling | Tailwind CSS | Responsive design |
| Icons | Lucide React | UI icons |
| Backend | Python + FastAPI | API and processing |
| PDF extraction | PyMuPDF | Page-level text extraction |
| AI | An available LLM API, e.g. OpenRouter | Structured analysis |
| Validation | Pydantic | Validate model output |
| Database | SQLite | Store analysis history |
| Charts | Recharts (optional) | Visual summaries |
| PDF export | ReportLab | Downloadable report |
| Version control | Git + GitHub | Collaboration and recovery |
| Deployment | Vercel + compatible Python hosting | Public demo |

Useful documentation:
- React: https://react.dev/
- FastAPI: https://fastapi.tiangolo.com/
- PyMuPDF: https://pymupdf.readthedocs.io/en/latest/
- Pydantic: https://docs.pydantic.dev/latest/
- OpenRouter: https://openrouter.ai/docs
- Tailwind CSS: https://tailwindcss.com/docs

**Do not train a model from scratch.** Use an available LLM API and focus on document processing, structured outputs, source verification, and a polished user experience.

## 4. Suggested Project Structure

```text
clauseguard-ai/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   │   ├── pdf_service.py
│   │   │   ├── analysis_service.py
│   │   │   └── verification_service.py
│   │   ├── schemas/
│   │   └── database/
│   └── requirements.txt
├── sample_documents/
├── README.md
└── .gitignore
```

Keep the structure simple. Get one end-to-end request working before creating unnecessary abstractions.

## 5. System Workflow

1. **Upload:** React sends a PDF to FastAPI.
2. **Validate:** Check file type, size, and whether text can be extracted.
3. **Extract:** Extract text page by page with PyMuPDF and retain page metadata.
4. **Analyze:** Send relevant text to the LLM and request schema-constrained JSON.
5. **Validate output:** Use Pydantic to reject malformed responses.
6. **Verify evidence:** Match each quoted passage against extracted text and associate it with the correct page.
7. **Store:** Save document metadata and analysis to SQLite.
8. **Display:** Render overview, risks, clauses, obligations, and deadlines in React.
9. **Export:** Generate a PDF report with findings and source references.

For long documents, process text in chunks and merge the findings. If a PDF is scanned and OCR is not implemented, show a clear message rather than pretending it was analyzed.

## 6. Suggested API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Check backend status |
| `/api/documents` | POST | Upload and register a document |
| `/api/documents/{id}` | GET | Retrieve document metadata |
| `/api/analyze` | POST | Analyze a document |
| `/api/analyses/{id}` | GET | Retrieve a saved analysis |
| `/api/analyses/{id}/report` | GET | Download the PDF report |
| `/api/history` | GET | List recent analyses |

Build only what is needed for the demo. The first critical path is **Upload → Analyze → Display → Export**.

## 7. Analysis Output Schema (Concept)

```json
{
  "document_summary": "A concise summary based on the source document.",
  "parties": [
    {
      "name": "Party name as written in the document",
      "role": "Customer, provider, or unknown"
    }
  ],
  "risks": [
    {
      "title": "Potential issue",
      "severity": "low",
      "explanation": "Why this may deserve review",
      "evidence": {
        "page": 1,
        "quote": "Exact text copied from the source"
      },
      "recommended_action": "A practical verification step",
      "verification_status": "verified"
    }
  ],
  "obligations": [],
  "deadlines": [],
  "key_clauses": []
}
```

This is a conceptual example. Define real Pydantic models and enforce allowed values in the implementation. The backend—not the LLM alone—must verify evidence and page references.

## 8. Prompting Rules for the LLM

Use instructions along these lines:

```text
You are a document-analysis assistant. Analyze only the supplied document.

Identify:
1. A concise summary.
2. Parties and roles.
3. Important clauses.
4. Potential risks that warrant review.
5. Obligations and responsible parties.
6. Explicit dates and deadlines.
7. Missing, unclear, or ambiguous information.

Rules:
- Do not invent clauses, quotations, dates, parties, or page numbers.
- Every finding must include supporting source text.
- Distinguish explicit facts from interpretations.
- Mark uncertain information for human review.
- Do not claim a clause is illegal without appropriate jurisdiction-specific support.
- Return null or an appropriate verification status when information is missing.
- Follow the requested JSON schema.
- This output supports human review and is not definitive legal advice.
```

A prompt does not guarantee accuracy. Verify quotations programmatically against the source text and keep uncertainty visible.

## 9. 36-Hour Schedule

### Hours 0–2: Setup
- Create GitHub repository.
- Set up React/Vite and FastAPI.
- Configure CORS and environment variables.
- Implement `/api/health`.
- Confirm React can call the backend.

**Checkpoint:** Frontend and backend communicate.

### Hours 2–6: PDF processing
- Add PDF upload and validation.
- Extract text page by page.
- Handle invalid, empty, and unsupported PDFs.
- Show extracted text or document metadata.

**Checkpoint:** A real text-based PDF is extracted correctly.

### Hours 6–11: AI engine
- Connect the LLM API.
- Define Pydantic response models.
- Generate summary, risks, clauses, obligations, and deadlines.
- Add basic chunking for longer documents.
- Handle API errors and malformed output.

**Checkpoint:** A PDF produces valid structured analysis.

### Hours 11–17: Dashboard
- Build summary cards.
- Display risk findings and source passages.
- Add clauses, obligations, and deadlines views.
- Add loading, empty, and error states.

**Checkpoint:** A user can understand the output without developer assistance.

### Hours 17–22: Evidence verification
- Match quotations against extracted page text.
- Check source-page references.
- Mark unsupported findings as unverified.
- Link each finding to its source passage.

**Checkpoint:** Findings are traceable to document text or clearly marked unverified.

### Hours 22–26: Export and history
- Generate PDF reports.
- Add download functionality.
- Store basic analysis metadata and history if time permits.

**Checkpoint:** A useful report can be downloaded.

### Hours 26–30: Testing and deployment
- Test at least three documents.
- Check dates, source passages, and unsupported claims.
- Test invalid and scanned PDFs.
- Protect API keys.
- Deploy and test the complete workflow.

**Checkpoint:** The deployed demo works end to end.

### Hours 30–33: Polish
- Improve responsive layout and typography.
- Add clear status and progress indicators.
- Remove confusing or unfinished UI.
- Avoid risky last-minute features.

### Hours 33–36: Pitch and fallback
- Rehearse a three-minute demo.
- Prepare slides and architecture diagram.
- Keep a pre-analyzed sample ready in case the API fails.
- Freeze features and fix critical bugs.

## 10. UI Plan

### Landing / Upload
Headline: **Understand Every Clause. Spot Risks Before They Cost You.**

Supporting copy: “Analyze business agreements, identify potential risks, track obligations, and generate evidence-backed reports.”

Primary action: **Analyze a Document**

### Analysis dashboard
- Document name and summary
- Parties
- Potential risks by review priority
- Key clauses
- Obligations table
- Deadline list or timeline
- Source evidence panel
- Report download

### Design direction
- Neutral light background
- Deep navy primary color
- Teal accent
- Clear severity labels
- Accessible contrast and readable typography
- Responsive layout

## 11. Testing Checklist

Test against documents with known expected answers.

- [ ] Payment terms are extracted correctly.
- [ ] Renewal conditions and notice periods are correct.
- [ ] Termination conditions are represented accurately.
- [ ] Explicit dates have correct values and source pages.
- [ ] Missing dates are not invented.
- [ ] Ambiguous obligations are flagged.
- [ ] Every quotation matches the extracted source text.
- [ ] Page references are correct.
- [ ] Invalid PDFs produce helpful errors.
- [ ] Scanned PDFs are handled honestly or OCR is supported.
- [ ] Long documents do not crash the service.
- [ ] API failures produce useful messages.
- [ ] API keys are never exposed in frontend code.
- [ ] PDF report export works.
- [ ] The deployed application works from upload through export.

Do not claim an accuracy percentage unless it has been measured against a documented test set.

## 12. Priority Matrix

| Priority | Feature | Target |
|---|---|---|
| P0 | PDF upload and text extraction | Required |
| P0 | Summary and key clauses | Required |
| P0 | Risk and obligation extraction | Required |
| P0 | Source evidence and page references | Required |
| P0 | Working end-to-end UI | Required |
| P0 | Basic reliability checks | Required |
| P1 | PDF report export | Strongly recommended |
| P1 | Deadline visualization | Strongly recommended |
| P1 | Analysis history | If time allows |
| P2 | Ask questions about a contract | Only after core MVP |
| P2 | Authentication | Only if required |
| P3 | Complex workflow automation | Skip for this hackathon |

## 13. Three-Minute Demo Script

**0:00–0:30 — Problem**  
“Business agreements contain payment terms, renewal conditions, deadlines, and obligations. Reviewing them manually takes time, and overlooking a condition can be costly.”

**0:30–0:50 — Solution**  
“ClauseGuard AI turns business documents into structured, evidence-backed findings and actionable next steps.”

**0:50–1:40 — Live demo**
1. Upload a prepared sample agreement.
2. Show the summary.
3. Open a potential risk.
4. Show its supporting quotation and page reference.
5. Show an obligation and deadline.
6. Export the report.

**1:40–2:10 — Differentiation**  
“Rather than presenting unsupported AI conclusions, ClauseGuard links findings to source passages, verifies quotations, and flags uncertain information for human review.”

Make this claim only after those checks work in the application.

**2:10–2:35 — Impact**  
“Our goal is to make business-document review faster, more structured, and easier to verify.”

**2:35–3:00 — Close**  
“ClauseGuard AI turns complex agreements into understandable findings, traceable evidence, and actionable next steps.”

## 14. Team Division

For a team of three or four:

- **Developer 1:** PDF extraction, AI integration, backend.
- **Developer 2:** React dashboard and UI.
- **Developer 3:** Evidence verification, tests, and export.
- **Developer 4 (if available):** Integration, deployment, and pitch.

Agree on the API schema early. Commit working code regularly and integrate before the final hours.

For solo development, follow the schedule sequentially.

## 15. What Not to Build

Avoid these unless the required MVP is already stable:
- Training a custom model
- Multi-tenant enterprise architecture
- Complex role-based permissions
- Electronic signatures
- A complete legal research engine
- Every possible file format
- Advanced OCR for every scan type
- Autonomous agents and complicated workflows

A complete, tested MVP is better than many unfinished features.

## 16. Immediate Next Steps

1. Create the `clauseguard-ai` repository.
2. Create `frontend/` and `backend/`.
3. Make FastAPI's health endpoint work.
4. Connect React to the backend.
5. Upload a PDF and extract its text.
6. Connect the LLM and validate structured output.
7. Build the dashboard around real analysis results.
8. Add evidence verification and report export.
9. Test the complete workflow.
10. Deploy and rehearse the pitch.

### Before implementation, decide:
- **Team size:** Solo / 2 / 3–4 / 5+
- **Development environment:** Laptop + VS Code / Browser / Other
- **LLM access:** OpenRouter / OpenAI / Gemini / Multiple / No API key yet

**Build order:** reliable workflow first, evidence-backed differentiation second, polish third.
