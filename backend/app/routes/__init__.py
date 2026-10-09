from .health import router as health_router
from .documents import router as documents_router
from .analysis import router as analysis_router
from .history import router as history_router

__all__ = [
    "health_router",
    "documents_router",
    "analysis_router",
    "history_router",
]
