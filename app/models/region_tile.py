from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class RegionTile(db.Model):
    __tablename__ = 'region_tiles'
    
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    terrain_type = Column(String(50), nullable=False)
    danger_level = Column(Integer, default=1)
    discovered = Column(Boolean, default=False)
    poi_id = Column(Integer, ForeignKey('points_of_interest.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    region = relationship('Region', backref='tiles', lazy=True)
    poi = relationship('PointOfInterest', backref='tiles', lazy=True)
    
    def __init__(self, region_id, x, y, terrain_type, danger_level=1, discovered=False, poi_id=None):
        self.region_id = region_id
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.danger_level = danger_level
        self.discovered = discovered
        self.poi_id = poi_id
        
    def to_dict(self):
        return {
            "id": self.id,
            "region_id": self.region_id,
            "x": self.x,
            "y": self.y,
            "terrain_type": self.terrain_type,
            "danger_level": self.danger_level,
            "discovered": self.discovered,
            "poi_id": self.poi_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 