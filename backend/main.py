"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables
from models import Task  # noqa: F401 - Import to register models
from routes.auth import router as auth_router
from routes.tasks import router as tasks_router

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - runs on startup and shutdown."""
    # Startup: Create database tables
    create_db_and_tables()
    print("Database tables created/verified")
    yield
    # Shutdown: cleanup if needed
    print("Application shutting down")


app = FastAPI(
    title="Todo API",
    description="Phase II: Full-Stack Todo Application with Authentication",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)


@app.get("/")
def root():
    """Root endpoint - health check."""
    return {"status": "ok", "message": "Todo API is running"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
