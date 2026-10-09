import os
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
def get_health():
    has_openrouter = bool(os.getenv("OPENROUTER_API_KEY", "").strip())
    has_openai = bool(os.getenv("OPENAI_API_KEY", "").strip())
    has_gemini = bool(os.getenv("GEMINI_API_KEY", "").strip())

    return {
        "status": "ok",
        "service": "ClauseGuard AI Backend",
        "version": "1.0.0",
        "llm_configured": has_openrouter or has_openai or has_gemini,
        "providers_available": {
            "openrouter": has_openrouter,
            "openai": has_openai,
            "gemini": has_gemini,
            "heuristic_engine": True
        }
    }
