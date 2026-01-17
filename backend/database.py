"""Database connection and session management for Neon Postgres."""

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Convert postgresql:// to postgresql+psycopg:// for psycopg3 driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Create engine with connection pooling
# Note: sslmode=require in URL handles SSL for Neon
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections after 5 minutes
    pool_timeout=30,  # Wait up to 30s for connection
)


def create_db_and_tables() -> None:
    """Create all database tables defined in models."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a database session for dependency injection.

    Usage:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
