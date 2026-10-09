# ClauseGuard AI — Legal Document & Contract Intelligence Platform

> **Problem Statement:** Analyze legal and business documents to extract risks, deadlines, obligations, and key clauses with verifiable source evidence.  
> **Mission:** Deliver an end-to-end MVP that turns agreements into traceable findings, verified source quotations, and actionable next steps.

---

## 🌟 Key Differentiators

### 1. Evidence-Linked Risk Analysis
Unlike traditional LLM wrappers that hallucinate clauses or invent page numbers:
- Every finding includes an **exact verbatim quotation** from the contract.
- The **Verification Service** matches each quote programmatically against the extracted page text.
- Findings are labeled with **`Verified (Page X)`** or flagged as **`Unverified / Needs Review`**.
- An interactive **Document Viewer** highlights the quote in the source text in real-time.

### 2. Contractual Obligations Tracker
- Assigns responsibilities per contracting party.
- Extracts explicit deadlines and notice windows (e.g. *Net 30*, *60 days prior to renewal*).
- Never invents dates—marks ambiguous timelines honestly as **`Needs verification`**.

### 3. Executive ReportLab PDF Export
- Generates downloadable, executive-ready PDF audit reports with contract metadata, risk score meters, parties table, obligation matrix, and legal disclaimers.

### 4. Zero-Friction Demo Mode & Multi-LLM Support
- **Built-in Intelligent Heuristic Legal Engine:** 100% functional out-of-the-box with zero API key or cost needed.
- **LLM API Integration:** OpenRouter (Claude 3.5 Sonnet, Gemini 2.0 Flash), OpenAI (GPT-4o), or Google Gemini configurable via `.env` or in-app Settings modal.
- **3 Prepared Sample Agreements:** Enterprise SaaS MSA, Commercial Office Lease, and Mutual NDA preloaded for 1-click evaluation.

---

## 🏗️ Architecture & Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 19 + Vite + Tailwind CSS v4 | Responsive glassmorphism interface |
| **Icons** | Lucide React | Modern visual indicators |
| **Backend** | Python 3.13 + FastAPI + Uvicorn | Async REST API & orchestrator |
| **PDF Extraction** | PyMuPDF (`pymupdf`) | High-fidelity page-by-page text extraction |
| **Evidence Verification** | Custom Python Verifier (`difflib` + N-gram) | Verbatim quotation and page matching |
| **PDF Report Generation** | ReportLab | Executive PDF audit exports |
| **Database** | SQLite | Document metadata and analysis persistence |
| **AI Integration** | OpenRouter / OpenAI / Gemini / Heuristic | Schema-constrained contract analysis |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** (Python 3.13 tested)
- **Node.js 18+** (Node v25.4 tested) and **npm**

### 2. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt

# Run unit tests to verify the pipeline:
python test_pipeline.py

# Start the FastAPI server (default: port 8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
Access the application in your browser at `http://127.0.0.1:5173`.

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check and LLM configuration status |
| `/api/documents` | POST | Upload and extract PDF document page-by-page |
| `/api/documents/{id}` | GET | Retrieve document metadata and page texts |
| `/api/analyze` | POST | Analyze document and verify evidence |
| `/api/analyses/{id}` | GET | Retrieve stored analysis result |
| `/api/analyses/{id}/report` | GET | Download styled ReportLab PDF report |
| `/api/history` | GET | Retrieve list of recent contract audits |
| `/api/samples` | GET | List available sample contracts |
| `/api/sample/load/{key}` | POST | 1-click analyze a sample contract |

---

## 📁 Project Structure

```text
clauseguard-ai/
├── frontend/                     # React + Vite + Tailwind v4 UI
│   ├── src/
│   │   ├── components/           # Navbar, HeroUpload, RiskDashboard, etc.
│   │   ├── services/             # API client
│   │   ├── App.jsx               # Main application coordinator
│   │   └── index.css             # Design tokens & glassmorphism styling
│   └── package.json
├── backend/                      # FastAPI Python backend
│   ├── app/
│   │   ├── main.py               # Application entrypoint & CORS
│   │   ├── database/             # SQLite DB layer
│   │   ├── routes/               # API endpoints
│   │   ├── schemas/              # Pydantic data models
│   │   └── services/             # PDF, Verification, Analysis, ReportLab
│   ├── sample_documents/         # Realistic sample agreements
│   ├── requirements.txt
│   └── test_pipeline.py          # Automated verification test suite
├── sample_documents/             # Pre-generated PDF agreements
├── ClauseGuard_AI_36_Hour_Hackathon_Plan.md
└── README.md
```

---

## ⏱️ 3-Minute Demo Script

1. **Problem (0:00–0:30):**  
   Commercial contracts are packed with hidden risks, uncapped indemnities, and strict renewal notice windows that are easy to miss.
2. **Solution (0:30–0:50):**  
   ClauseGuard AI transforms legal agreements into verified findings, plain-English impact summaries, and actionable next steps.
3. **Live Demo (0:50–1:50):**  
   - Click **"CloudScale Enterprise SaaS MSA"** for instant 1-click audit.
   - Review the **Risk Score (62/100)** and executive summary.
   - Expand a **High Risk** (Unilateral Indemnification) and show the **`Verified (Page 3)`** badge.
   - Click **"Locate in Source"** to inspect the live quotation highlighted inside the document text.
   - Open the **Obligations Tracker** to see assigned duties and renewal windows.
   - Click **"Download PDF Report"** to export the ReportLab executive document.
4. **Differentiation & Impact (1:50–3:00):**  
   Highlight the programmatic evidence verification guarantee: Zero hallucination, evidence traceability, and human-in-the-loop auditability.
