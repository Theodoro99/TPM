from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

"""Database configuration and session management.

This module provides:
- Database engine configuration
- Session factory creation
- Base class for SQLAlchemy models
- Database session dependency injection
"""

# Load environment variables
load_dotenv()

# Get database URL from environment variables or use default
# Changed from PostgreSQL to SQLite for easier local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./preventplus.db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
"""SQLAlchemy engine instance for database connectivity.

Configured with:
- DATABASE_URL from environment variables (defaults to SQLite)
- check_same_thread=False for SQLite compatibility
"""
# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""Session factory for creating database sessions.

Configured with:
- autocommit=False for explicit transaction control
- autoflush=False to prevent automatic flushes
- Bound to the configured engine
"""
# Create base class for models
Base = declarative_base()
"""Base class for all SQLAlchemy ORM models.

All database models should inherit from this class to be properly registered.
"""
# Dependency to get DB session
def get_db():
    """Dependency generator for database sessions.

    Yields:
        Session: A database session instance

    Ensures:
        Session is properly closed after use

    Usage:
        FastAPI dependencies can use this to get a database session:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
