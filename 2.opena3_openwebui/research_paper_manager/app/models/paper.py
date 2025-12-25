"""
Paper Data Model - SQLAlchemy ORM
"""

from datetime import datetime

from sqlalchemy import JSON, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Paper(Base):
    """Akademisches Paper Model"""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True)
    arxiv_id = Column(String(20), unique=True, nullable=True)
    title = Column(String(500), nullable=False)
    authors = Column(Text, nullable=False)  # JSON string
    abstract = Column(Text)
    category = Column(String(50))  # cs.AI, physics.qm, etc.
    url = Column(String(500))
    pdf_url = Column(String(500))
    published_date = Column(Date)
    summary = Column(Text)  # AI-generated summary
    keywords = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)

    # Relationships
    tags = relationship("Tag", back_populates="paper", cascade="all, delete-orphan")
    collections = relationship("CollectionPaper", back_populates="paper", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "category": self.category,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "summary": self.summary,
            "keywords": self.keywords,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


class Tag(Base):
    """Tag/Label für Papers"""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    paper = relationship("Paper", back_populates="tags")

    def to_dict(self):
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "tag_name": self.tag_name,
            "created_at": self.created_at.isoformat(),
        }


class Collection(Base):
    """Paper Collection / Ordner"""

    __tablename__ = "collections"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    papers = relationship("CollectionPaper", back_populates="collection", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "paper_count": len(self.papers),
        }


class CollectionPaper(Base):
    """Association zwischen Collection und Paper"""

    __tablename__ = "collection_papers"

    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    collection = relationship("Collection", back_populates="papers")
    paper = relationship("Paper", back_populates="collections")

    def to_dict(self):
        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "paper_id": self.paper_id,
            "added_at": self.added_at.isoformat(),
        }
