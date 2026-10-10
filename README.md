# ClauseGuard — Vendor Contracts & Renewal Actions

ClauseGuard helps small businesses turn vendor and SaaS agreements into confirmed deadlines, owned actions, reminders and recorded outcomes.

**Workflow:** upload → review source → confirm date and owner → receive reminders → record outcome.

The workspace includes a contract register, searchable actions, an in-app reminder inbox, calendar downloads and an activity history. Existing contract analysis and PDF reports remain available.

## Run an isolated local demo (Windows / PowerShell)

The demo uses local storage and disables external AI and database connections. Prepared sample agreements work without API keys.

```powershell
cd backend
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe run_demo.py
```

In another terminal:

```powershell
cd frontend
npm install
$env:API_PROXY_TARGET='http://127.0.0.1:8010'
$env:VITE_SUPABASE_URL=''
$env:VITE_SUPABASE_ANON_KEY=''
npm run dev -- --host 127.0.0.1 --port 5174
```

Open http://127.0.0.1:5174. Choose **Add contract**, select the CloudScale sample, and use **Review & track** on an extracted deadline. Confirm an owner and date, then return to **Workspace**. You can also create a manual action from the Contracts tab.

Demo data and its session signing secret live in `backend/data/demo` (git-ignored). Browser sessions last up to seven days. Signing out or clearing browser storage loses access to that demo session; data is not automatically deleted or migrated to a signed-in account. Use sample documents for demonstrations.

## Configure an authenticated pilot

Use `backend/.env.example` and `frontend/.env.example` as references; keep secrets out of Git. Configure Supabase authentication, turn demo off, and use a persistent data directory. A Supabase service key is only needed for the optional remote document store; authentication can be paired with local SQLite storage.

```powershell
cd backend
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The development frontend proxies `/api` to port 8000 by default. Production builds use `VITE_API_BASE_URL` or the endpoint configured in Settings. Do not put a Supabase service key in frontend environment variables.

See [PRODUCT.md](PRODUCT.md) for storage requirements, source-verification semantics, pilot limitations and rollout guidance. This version uses in-app reminders and calendar exports; it does not send emails or contact vendors.

### Before merging into a live deployment

- Configure backend `SUPABASE_URL` and, for legacy HS256 tokens, `SUPABASE_JWT_SECRET`. Configure frontend `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` from the same project, then rebuild the frontend. Keep `ALLOW_DEMO=false` for the authenticated pilot.
- Set frontend `VITE_API_BASE_URL` to the backend origin and backend `ALLOWED_ORIGINS` to the exact frontend origin.
- Mount persistent storage at `DATA_DIR` and run one backend instance. The historical Render manifests specify `plan: free` together with a disk; this combination is unsupported. Select a disk-capable hosting plan before deployment. See [Render persistent disks](https://render.com/docs/disks). Do not rely on free ephemeral storage for customer contracts or reminders.
- Back up existing data before release. Older records without a verified owner are intentionally inaccessible; migrate ownership only after validating the original owner.
- In staging, sign in, upload a sample, review the summary, confirm an action, download its calendar and PDF, then restart the backend and verify persistence. Live authentication and external AI integrations require this staging check.

GitHub Actions runs the offline backend regression suite and frontend lint/build on pull requests and release-branch pushes.

## Verify

```powershell
backend/.venv/Scripts/python.exe backend/test_product.py
cd frontend
npm run build
npm run lint
```

The regression suite uses temporary storage and disables external services. It does not touch deployment data or keys.

## Stack

React + Vite + Tailwind; Python FastAPI; PyMuPDF; ReportLab; SQLite; optional Supabase authentication and document storage; optional OpenRouter, OpenAI, Gemini or Groq analysis.

Text PDFs: up to 25 MB, 100 pages and 250,000 extracted characters. Source matching supports human review; it does not establish legal correctness. Dates must be confirmed before reminders are scheduled.
