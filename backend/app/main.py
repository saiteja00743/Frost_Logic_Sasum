from dotenv import load_dotenv
load_dotenv()  # Load .env before any os.getenv() calls

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import logging
import os
from contextlib import suppress

from .database.db import init_db
from .routes.health import router as health_router
from .routes.documents import router as documents_router
from .routes.analysis import router as analysis_router
from .routes.history import router as history_router
from .routes.workspace import router as workspace_router
from .services.workspace_service import init_workspace, deliver_reminders


async def reminder_loop():
    while True:
        try:
            await asyncio.to_thread(deliver_reminders)
        except Exception:
            logging.exception("In-app reminder delivery failed; retrying on next tick")
        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    init_workspace()
    reminders = asyncio.create_task(reminder_loop())
    print("[ClauseGuard AI] Database initialized successfully.")
    try:
        yield
    finally:
        reminders.cancel()
        with suppress(asyncio.CancelledError):
            await reminders

app = FastAPI(
    title="ClauseGuard AI API",
    description="Automated Legal Document Intelligence, Evidence-Linked Risk Extraction & Obligation Tracking",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration — allow Vercel frontend + localhost dev
ALLOWED_ORIGINS = [
    "https://frost-logic-sasum.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]
if os.getenv("ALLOWED_ORIGINS"):
    ALLOWED_ORIGINS = [origin.strip() for origin in os.environ["ALLOWED_ORIGINS"].split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(analysis_router)
app.include_router(history_router)
app.include_router(workspace_router)

@app.get("/")
def root():
    return {
        "app": "ClauseGuard AI Backend API",
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
