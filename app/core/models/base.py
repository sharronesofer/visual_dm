"""
Base model for all database models.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel as PydanticBaseModel, Field
from datetime import datetime
import uuid
from app.core.database import db
from sqlalchemy import Column, Integer, DateTime, MetaData
from sqlalchemy.orm import Mapped, mapped_column

# Create a naming convention for constraints
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=naming_convention)

class Base(db.Model):
    """Base class for all SQLAlchemy models"""
    __abstract__ = True
    metadata = metadata

class BaseModel(Base):
    """Base model class for all database models"""
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        """Save the model to the database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the model from the database"""
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        """Get a model instance by ID.
        
        Args:
            id: The ID of the model instance
            
        Returns:
            The model instance if found, None otherwise
        """
        return db.session.get(cls, id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

class BaseSchema(PydanticBaseModel):
    """Base schema for all Pydantic models."""
    class Config:
        """Pydantic model configuration."""
        from_attributes = True

class BaseStats(BaseSchema):
    """Base class for entity statistics."""
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

class BaseFeatures(BaseSchema):
    """Base class for entity features."""
    level: int = 1
    experience: int = 0
    hit_points: int = 10
    max_hit_points: int = 10
    armor_class: int = 10
    speed: int = 30

class BaseInventory(BaseSchema):
    """Base class for entity inventory."""
    items: List[str] = Field(default_factory=list)
    equipment: Dict[str, str] = Field(default_factory=dict)
    gold: int = 0

# See also: Infraction model in infraction.py for player misconduct tracking
# See also: Consequence model in consequence.py for punitive action tracking 