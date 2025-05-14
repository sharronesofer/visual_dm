from app.models import db
from datetime import datetime

class Relationship(db.Model):
    """Model for tracking relationships between characters and NPCs."""
    __tablename__ = 'relationships'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    npc_id = db.Column(db.Integer, db.ForeignKey('npcs.id'), nullable=False)
    relationship_type = db.Column(db.String(50))  # e.g., 'friend', 'enemy', 'neutral'
    loyalty_score = db.Column(db.Integer, default=0)  # -100 to 100
    trust_score = db.Column(db.Integer, default=0)  # -100 to 100
    interaction_history = db.Column(db.JSON)  # List of past interactions
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    character = db.relationship('Character', backref='npc_relationships')
    npc = db.relationship('NPC', backref='character_relationships')
    
    def __repr__(self):
        return f'<Relationship {self.character_id}-{self.npc_id}>' 