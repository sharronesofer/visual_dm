"""
Review template schema definitions for standardizing code review processes.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, Text, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.models.base import BaseModel
from marshmallow import Schema, fields

class ReviewTemplate(BaseModel):
    """Model for defining structured review templates."""
    __tablename__ = 'review_templates'
    __table_args__ = (
        Index('ix_review_templates_name', 'name'),
        UniqueConstraint('name', name='uq_review_templates_name'),
        {'extend_existing': True}
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100))  # e.g., 'code', 'design', 'security'
    sections: Mapped[List[Dict]] = mapped_column(JSON, default=list)  # List of sections with questions
    metadata: Mapped[Dict] = mapped_column(JSON, default=dict)  # Additional template metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReviewTemplateSchema(Schema):
    """Marshmallow schema for serializing review templates."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    version = fields.Str(required=True)
    category = fields.Str()
    sections = fields.List(fields.Dict(), required=True)
    metadata = fields.Dict()
    is_active = fields.Boolean()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ReviewSection:
    """Structure for a review template section."""
    def __init__(self, title: str, description: str, questions: List[Dict[str, Any]]):
        self.title = title
        self.description = description
        self.questions = questions

class ReviewQuestion:
    """Structure for a review template question."""
    def __init__(self, 
                 text: str,
                 type: str,  # 'text', 'rating', 'boolean', 'choice'
                 required: bool = True,
                 options: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.text = text
        self.type = type
        self.required = required
        self.options = options or []
        self.metadata = metadata or {} 