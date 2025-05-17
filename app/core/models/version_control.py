"""
Version control models for managing code version linkage with tasks and reviews.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Boolean, Index, UniqueConstraint, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
import enum

class VersionType(enum.Enum):
    MIGRATION = "migration"
    FEATURE = "feature"
    BUGFIX = "bugfix"
    RELEASE = "release"

class CodeVersion(BaseModel):
    """Model for tracking code versions (commits, branches, tags)."""
    __tablename__ = 'code_versions'
    __table_args__ = (
        Index('ix_code_versions_commit_hash', 'commit_hash'),
        Index('ix_code_versions_branch_name', 'branch_name'),
        Index('ix_code_versions_tag_name', 'tag_name'),
        UniqueConstraint('commit_hash', name='uq_code_versions_commit_hash'),
        {'extend_existing': True}
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)  # SHA-1 hash
    branch_name: Mapped[Optional[str]] = mapped_column(String(255))
    tag_name: Mapped[Optional[str]] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    commit_message: Mapped[str] = mapped_column(Text)
    commit_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    version_metadata: Mapped[dict] = mapped_column(JSON, default=dict)  # Additional version info
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    task_links = relationship('TaskVersionLink', back_populates='version', cascade='all, delete-orphan')
    review_links = relationship('ReviewVersionLink', back_populates='version', cascade='all, delete-orphan')

class VersionControl(CodeVersion):
    """
    Model for version control entries in the game.
    Fields:
        id (int): Primary key.
        version (str): Version string.
        description (str): Description of the version entry.
        version_type (VersionType): Type of version entry.
        metadata (dict): Additional metadata.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
    """
    __tablename__ = 'version_control'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    version: Mapped[str] = mapped_column(String(50), nullable=False, doc="Version string.")
    description: Mapped[Optional[str]] = mapped_column(Text, doc="Description of the version entry.")
    version_type: Mapped[VersionType] = mapped_column(Enum(VersionType), default=VersionType.RELEASE, doc="Type of version entry.")
    metadata: Mapped[dict] = mapped_column(JSON, default=dict, doc="Additional metadata.")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, doc="Creation timestamp.")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="Last update timestamp.")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the version control entry to a dictionary."""
        return {
            "id": self.id,
            "version": self.version,
            "description": self.description,
            "version_type": self.version_type.value if self.version_type else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class TaskVersionLink(BaseModel):
    """Model for linking tasks to code versions."""
    __tablename__ = 'task_version_links'
    __table_args__ = (
        Index('ix_task_version_links_task_id', 'task_id'),
        Index('ix_task_version_links_version_id', 'version_id'),
        UniqueConstraint('task_id', 'version_id', name='uq_task_version_links'),
        {'extend_existing': True}
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, nullable=False)
    version_id: Mapped[int] = mapped_column(Integer, ForeignKey('code_versions.id'), nullable=False)
    link_type: Mapped[str] = mapped_column(String(50), default='implementation')  # implementation, review, test, etc.
    link_metadata: Mapped[dict] = mapped_column(JSON, default=dict)  # Additional link metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    version = relationship('CodeVersion', back_populates='task_links')

class ReviewVersionLink(BaseModel):
    """Model for linking code reviews to code versions."""
    __tablename__ = 'review_version_links'
    __table_args__ = (
        Index('ix_review_version_links_review_id', 'review_id'),
        Index('ix_review_version_links_version_id', 'version_id'),
        UniqueConstraint('review_id', 'version_id', name='uq_review_version_links'),
        {'extend_existing': True}
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(Integer, nullable=False)
    version_id: Mapped[int] = mapped_column(Integer, ForeignKey('code_versions.id'), nullable=False)
    link_type: Mapped[str] = mapped_column(String(50), default='review')  # review, revision, approval, etc.
    link_metadata: Mapped[dict] = mapped_column(JSON, default=dict)  # Additional link metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    version = relationship('CodeVersion', back_populates='review_links') 