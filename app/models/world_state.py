from app import db
from datetime import datetime

class WorldEvent(db.Model):
    __tablename__ = 'world_events'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # e.g., 'kingdom_formation', 'faction_war', 'natural_disaster'
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.Integer, default=1)  # 1-10 scale
    affected_regions = db.Column(db.JSON)  # List of region IDs affected
    affected_factions = db.Column(db.JSON)  # List of faction IDs affected
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    region = db.relationship('Region', backref='world_events', lazy=True)
    
    def __init__(self, region_id, event_type, description, severity=1, affected_regions=None, affected_factions=None):
        self.region_id = region_id
        self.event_type = event_type
        self.description = description
        self.severity = severity
        self.affected_regions = affected_regions or []
        self.affected_factions = affected_factions or []
        
    def to_dict(self):
        return {
            "id": self.id,
            "region_id": self.region_id,
            "event_type": self.event_type,
            "description": self.description,
            "severity": self.severity,
            "affected_regions": self.affected_regions,
            "affected_factions": self.affected_factions,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class WorldState(db.Model):
    __tablename__ = 'world_states'
    
    id = db.Column(db.Integer, primary_key=True)
    current_era = db.Column(db.String(50), default='early')  # early, middle, late
    global_tension = db.Column(db.Integer, default=0)  # 0-100 scale
    major_events = db.Column(db.JSON)  # List of major event IDs
    kingdom_count = db.Column(db.Integer, default=0)
    last_major_shift = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "current_era": self.current_era,
            "global_tension": self.global_tension,
            "major_events": self.major_events,
            "kingdom_count": self.kingdom_count,
            "last_major_shift": self.last_major_shift.isoformat() if self.last_major_shift else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 