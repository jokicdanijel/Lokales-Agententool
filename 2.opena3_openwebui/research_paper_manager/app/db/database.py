"""
Database Configuration and Session Management

This module provides database initialization, session management, and connection
pooling for the Research Paper Manager application.

Features:
    - Thread-safe engine singleton pattern
    - Automatic session factory creation
    - Context manager support for automatic cleanup
    - Comprehensive error handling and logging
    - Support for SQLite and PostgreSQL
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app.models.paper import Base
import os
import logging
import threading
from typing import Optional, Generator
from contextlib import contextmanager
from time import sleep

# Configure logging
logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_SessionLocal = None
_lock = threading.Lock()


def _create_engine(db_path: str):
    """
    Create database engine with appropriate configuration.

    Args:
        db_path: Database connection string or file path

    Returns:
        SQLAlchemy Engine instance

    Raises:
        ValueError: If database path is invalid
    """
    if not db_path:
        raise ValueError("Database path cannot be empty")

    logger.debug(f"Creating engine for: {db_path}")

    try:
        if db_path.endswith('.db') or ':memory:' in db_path:
            # SQLite configuration
            engine = create_engine(
                f'sqlite:///{db_path}',
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=os.getenv('SQL_ECHO', 'False').lower() == 'true'
            )
            logger.info(f"✅ SQLite engine created: {db_path}")
        else:
            # PostgreSQL or other database
            engine = create_engine(
                db_path,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                echo=os.getenv('SQL_ECHO', 'False').lower() == 'true'
            )
            logger.info(f"✅ PostgreSQL engine created")

        # Enable foreign keys for SQLite
        if db_path.endswith('.db') or ':memory:' in db_path:
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        return engine

    except SQLAlchemyError as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def init_db(db_path: Optional[str] = None) -> tuple:
    """
    Initialize database and create all tables.

    This function should be called once at application startup.
    It uses thread-safe singleton pattern to ensure only one engine is created.

    Args:
        db_path: Path to SQLite database file or connection string.
                If None, uses DB_PATH environment variable or default.

    Returns:
        Tuple of (engine, SessionLocal) for use in application

    Raises:
        SQLAlchemyError: If database initialization fails
    """
    global _engine, _SessionLocal

    if db_path is None:
        db_path = os.getenv('DB_PATH', './research_papers.db')

    # Thread-safe initialization
    with _lock:
        if _engine is not None:
            logger.debug("Engine already initialized, returning existing")
            return _engine, _SessionLocal

        try:
            # Create engine
            _engine = _create_engine(db_path)

            # Create session factory
            _SessionLocal = sessionmaker(
                bind=_engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False
            )

            # Create all tables
            Base.metadata.create_all(_engine)
            logger.info(f"✅ Database initialized: {db_path}")

            return _engine, _SessionLocal

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise


def get_engine(db_path: Optional[str] = None):
    """
    Get or create global database engine.

    Thread-safe singleton pattern with double-checked locking.

    Args:
        db_path: Database path (optional, only used on first call)

    Returns:
        SQLAlchemy Engine instance
    """
    global _engine

    if _engine is None:
        with _lock:
            if _engine is None:
                if db_path is None:
                    db_path = os.getenv('DB_PATH', './research_papers.db')
                _engine = _create_engine(db_path)

    return _engine


def get_session_factory(db_path: Optional[str] = None):
    """
    Get or create session factory.

    Args:
        db_path: Database path (optional, only used on first call)

    Returns:
        SQLAlchemy sessionmaker instance
    """
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_engine(db_path)
        with _lock:
            if _SessionLocal is None:
                _SessionLocal = sessionmaker(
                    bind=engine,
                    autoflush=False,
                    autocommit=False,
                    expire_on_commit=False
                )

    return _SessionLocal


def get_session(db_path: Optional[str] = None, max_retries: int = 3) -> Session:
    """
    Get new database session with retry logic.

    Args:
        db_path: Database path (optional)
        max_retries: Number of connection retry attempts

    Returns:
        SQLAlchemy Session instance

    Raises:
        OperationalError: If connection fails after max retries
    """
    SessionLocal = get_session_factory(db_path)

    for attempt in range(max_retries):
        try:
            session = SessionLocal()
            # Test connection
            session.execute("SELECT 1")
            logger.debug(f"Session created successfully (attempt {attempt + 1})")
            return session

        except OperationalError as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                sleep(0.5 * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"Failed to create session after {max_retries} attempts")
                raise

        except Exception as e:
            logger.error(f"Unexpected error creating session: {e}")
            raise


@contextmanager
def get_db_session(db_path: Optional[str] = None) -> Generator[Session, None, None]:
    """
    Context manager for automatic session cleanup.

    Usage:
        with get_db_session() as session:
            papers = session.query(Paper).all()

    Args:
        db_path: Database path (optional)

    Yields:
        SQLAlchemy Session instance

    Raises:
        Exception: Any exception raised within context
    """
    session = get_session(db_path)
    try:
        yield session
    except Exception as e:
        logger.error(f"Error in database session: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug("Session closed")


def close_db():
    """
    Close global engine and cleanup resources.

    Should be called at application shutdown.
    """
    global _engine, _SessionLocal

    with _lock:
        if _engine is not None:
            try:
                _engine.dispose()
                logger.info("✅ Database engine disposed")
            except Exception as e:
                logger.error(f"Error disposing engine: {e}")
            finally:
                _engine = None
                _SessionLocal = None
