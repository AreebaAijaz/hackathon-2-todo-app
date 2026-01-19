"""API routes for the Todo application."""

from .auth import router as auth_router
from .tasks import router as tasks_router
from .chat import router as chat_router

__all__ = ["auth_router", "tasks_router", "chat_router"]
