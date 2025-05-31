from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declared_attr
import datetime
from backend.infrastructure.shared.database import Base

class BaseModel(Base):
    """Base model class for all entities in the application.
    
    This abstract base class provides common columns and functionality
    for all models. All domain models should inherit from this class.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    @declared_attr
    def __tablename__(cls):
        """Automatically generates table name based on class name."""
        return cls.__name__.lower()
    
    def as_dict(self):
        """Converts the model instance to a dictionary."""
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            result[c.name] = value
        return result
    
    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__} {self.id}>" 