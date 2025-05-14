"""
Base model class with common functionality for all game models.
"""

from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar
from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declared_attr
from flask import current_app
from ..database import db

T = TypeVar('T', bound='BaseModel')

class BaseModel(db.Model):
    """Abstract base model class."""

    __abstract__ = True

    # Common columns for all models
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()

    def to_dict(self, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Args:
            exclude: List of fields to exclude

        Returns:
            Dictionary representation of model
        """
        exclude = exclude or []
        mapper = inspect(self.__class__)
        result = {}
        
        for column in mapper.columns:
            if column.key not in exclude:
                value = getattr(self, column.key)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.key] = value
                
        return result

    @classmethod
    def get_by_id(cls: Type[T], id: Any) -> Optional[T]:
        """
        Get model instance by ID.

        Args:
            id: Instance ID

        Returns:
            Model instance if found, None otherwise
        """
        return cls.query.filter_by(id=id, is_active=True).first()

    @classmethod
    def get_paginated(
        cls: Type[T],
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[T], int]:
        """
        Get paginated list of model instances.

        Args:
            page: Page number
            per_page: Items per page
            filters: Filter conditions

        Returns:
            Tuple of (items, total)
        """
        query = cls.query.filter_by(is_active=True)
        
        if filters:
            for key, value in filters.items():
                if key.endswith('__gt'):
                    field = key[:-4]
                    query = query.filter(getattr(cls, field) > value)
                elif key.endswith('__gte'):
                    field = key[:-5]
                    query = query.filter(getattr(cls, field) >= value)
                elif key.endswith('__lt'):
                    field = key[:-4]
                    query = query.filter(getattr(cls, field) < value)
                elif key.endswith('__lte'):
                    field = key[:-5]
                    query = query.filter(getattr(cls, field) <= value)
                elif key.endswith('__in'):
                    field = key[:-4]
                    query = query.filter(getattr(cls, field).in_(value))
                elif key.endswith('__like'):
                    field = key[:-6]
                    query = query.filter(getattr(cls, field).like(f"%{value}%"))
                else:
                    query = query.filter(getattr(cls, key) == value)
        
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return items, total

    def save(self) -> None:
        """Save model instance to database."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to save {self.__class__.__name__}: {str(e)}")
            db.session.rollback()
            raise

    def update(self, **kwargs: Any) -> None:
        """
        Update model instance attributes.

        Args:
            **kwargs: Attributes to update
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.save()
        except Exception as e:
            current_app.logger.error(f"Failed to update {self.__class__.__name__}: {str(e)}")
            raise

    def delete(self, soft: bool = True) -> None:
        """
        Delete model instance.

        Args:
            soft: Whether to perform soft delete
        """
        try:
            if soft:
                self.is_active = False
                self.save()
            else:
                db.session.delete(self)
                db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to delete {self.__class__.__name__}: {str(e)}")
            db.session.rollback()
            raise

    @classmethod
    def create(cls: Type[T], **kwargs: Any) -> T:
        """
        Create new model instance.

        Args:
            **kwargs: Instance attributes

        Returns:
            New model instance
        """
        try:
            instance = cls(**kwargs)
            instance.save()
            return instance
        except Exception as e:
            current_app.logger.error(f"Failed to create {cls.__name__}: {str(e)}")
            raise

    def __repr__(self) -> str:
        """Get string representation of model."""
        return f"<{self.__class__.__name__} {self.id}>" 