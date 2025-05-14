from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.db_base import Base
from datetime import datetime

class TradeRoute(Base):
    __tablename__ = 'trade_routes'
    id = Column(Integer, primary_key=True)
    origin_region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    destination_region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    volume = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    status = Column(String(20), default='active')
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    origin_region = relationship('Region', foreign_keys=[origin_region_id])
    destination_region = relationship('Region', foreign_keys=[destination_region_id])
    resource = relationship('Resource') 