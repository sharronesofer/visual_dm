"""
Social model for the game.
"""

from app.core.database import db
from app.core.models.base import BaseEntity

class Relationship(BaseEntity):
    """Model representing a relationship between two entities."""
    
    __tablename__ = 'relationships'
    
    # First entity (can be character or NPC)
    entity1_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    entity1_npc_id = db.Column(db.Integer, db.ForeignKey('npcs.id'))
    
    # Second entity (can be character or NPC)
    entity2_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    entity2_npc_id = db.Column(db.Integer, db.ForeignKey('npcs.id'))
    
    # Relationship details
    relationship_type = db.Column(db.String(50))  # friend, rival, enemy, etc.
    relationship_value = db.Column(db.Integer, default=0)  # -100 to 100
    
    def to_dict(self):
        """Convert the relationship to a dictionary.
        
        Returns:
            dict: The relationship as a dictionary
        """
        base_dict = super().to_dict()
        relationship_dict = {
            'entity1': {
                'character_id': self.entity1_character_id,
                'npc_id': self.entity1_npc_id
            },
            'entity2': {
                'character_id': self.entity2_character_id,
                'npc_id': self.entity2_npc_id
            },
            'details': {
                'type': self.relationship_type,
                'value': self.relationship_value
            }
        }
        return {**base_dict, **relationship_dict}

class Interaction(BaseEntity):
    """Model representing an interaction between two entities."""
    
    __tablename__ = 'interactions'
    
    # First entity (can be character or NPC)
    entity1_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    entity1_npc_id = db.Column(db.Integer, db.ForeignKey('npcs.id'))
    
    # Second entity (can be character or NPC)
    entity2_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    entity2_npc_id = db.Column(db.Integer, db.ForeignKey('npcs.id'))
    
    # Interaction details
    interaction_type = db.Column(db.String(50))  # conversation, trade, gift, etc.
    outcome = db.Column(db.String(50))  # success, failure, neutral
    impact = db.Column(db.Integer)  # -100 to 100
    
    def to_dict(self):
        """Convert the interaction to a dictionary.
        
        Returns:
            dict: The interaction as a dictionary
        """
        base_dict = super().to_dict()
        interaction_dict = {
            'entity1': {
                'character_id': self.entity1_character_id,
                'npc_id': self.entity1_npc_id
            },
            'entity2': {
                'character_id': self.entity2_character_id,
                'npc_id': self.entity2_npc_id
            },
            'details': {
                'type': self.interaction_type,
                'outcome': self.outcome,
                'impact': self.impact
            }
        }
        return {**base_dict, **interaction_dict}

class Reputation(BaseEntity):
    """Model representing an entity's reputation with a faction."""
    
    __tablename__ = 'reputations'
    
    # Entity (can be character or NPC)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    npc_id = db.Column(db.Integer, db.ForeignKey('npcs.id'))
    
    # Faction
    faction_id = db.Column(db.Integer, db.ForeignKey('factions.id'), nullable=False)
    faction = db.relationship('Faction', backref=db.backref('reputations', lazy=True))
    
    # Reputation details
    value = db.Column(db.Integer, default=0)  # -100 to 100
    rank = db.Column(db.String(50))  # hated, neutral, friendly, exalted, etc.
    
    def to_dict(self):
        """Convert the reputation to a dictionary.
        
        Returns:
            dict: The reputation as a dictionary
        """
        base_dict = super().to_dict()
        reputation_dict = {
            'character_id': self.character_id,
            'npc_id': self.npc_id,
            'faction_id': self.faction_id,
            'details': {
                'value': self.value,
                'rank': self.rank
            }
        }
        return {**base_dict, **reputation_dict} 