from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.infrastructure.models import BaseModel

class APIKey(BaseModel):
    __tablename__ = 'api_keys'
    id = Column(Integer, primary_key=True)
    key_hash = Column(String(255), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(String(255))

    user = relationship('User', backref='api_keys') 