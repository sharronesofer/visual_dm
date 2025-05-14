from datetime import datetime
from app.models import db
from app.models.region import Region

class Event(db.Model):
    """Model for tracking world events."""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # e.g., 'quest', 'combat', 'social'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    npc_id = db.Column(db.Integer, db.ForeignKey('npcs.id'))
    quest_id = db.Column(db.Integer, db.ForeignKey('quests.id'))
    
    # Relationships
    region = db.relationship('Region', backref='events')
    character = db.relationship('Character', backref='events')
    npc = db.relationship('NPC', backref='events')
    quest = db.relationship('Quest', backref='events')
    
    def __repr__(self):
        return f'<Event {self.title}>' 