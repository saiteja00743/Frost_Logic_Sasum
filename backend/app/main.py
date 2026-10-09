from dotenv import load_dotenv
load_dotenv()  # Load .env before any os.getenv() calls

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .database.db import init_db
from .routes.health import router as health_router
from .routes.documents import router as documents_router
from .routes.analysis import router as analysis_router
from .routes.history import router as history_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    print("[ClauseGuard AI] Database initialized successfully.")
    yield

app = FastAPI(
    title="ClauseGuard AI API",
    description="Automated Legal Document Intelligence, Evidence-Linked Risk Extraction & Obligation Tracking",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(analysis_router)
app.include_router(history_router)

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
