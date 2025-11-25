"""
Database Configuration and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.models.paper import Base
import os


def init_db(db_path: str = None):
    """
    Initialize database and create tables

    Args:
        db_path: Path to SQLite database file
    """
    if db_path is None:
        db_path = os.getenv('DB_PATH', './research_papers.db')

    # Create engine
    if db_path.endswith('.db') or ':memory:' in db_path:
        # SQLite
        engine = create_engine(
            f'sqlite:///{db_path}',
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )
    else:
        # PostgreSQL or other
        engine = create_engine(db_path)

    # Create all tables
    Base.metadata.create_all(engine)

    print(f"✅ Database initialized: {db_path}")
    return engine


def get_session(db_path: str = None) -> Session:
    """
    Get new database session

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLAlchemy Session
    """
    if db_path is None:
        db_path = os.getenv('DB_PATH', './research_papers.db')

    engine = create_engine(
        f'sqlite:///{db_path}',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
    )

    Session = sessionmaker(bind=engine)
    return Session()


# Global engine (initialized once)
_engine = None

def get_engine(db_path: str = None):
    """Get or create global engine"""
    global _engine

    if _engine is None:
        if db_path is None:
            db_path = os.getenv('DB_PATH', './research_papers.db')

        _engine = create_engine(
            f'sqlite:///{db_path}',
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )

    return _engine
