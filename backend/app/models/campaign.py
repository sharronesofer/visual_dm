from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.app.models.base import BaseModel

class Campaign(BaseModel):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 