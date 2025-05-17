"""
Social model for the game.
"""

from app.core.database import db
from app.core.models.base import BaseModel
from datetime import datetime
from sqlalchemy import Enum as SQLEnum, Index
from enum import Enum

def enum_values(enum):
    return [e.value for e in enum]

class EntityType(Enum):
    INDIVIDUAL = "individual"  # Character or NPC
    FACTION = "faction"
    PARTY_GROUP = "party_group"
    REGION = "region"
    POI = "poi"

class Relationship(BaseModel):
    """Model representing a relationship between any two entities."""
    __tablename__ = 'relationships'
    __table_args__ = (
        Index('ix_relationships_entity1', 'entity1_id', 'entity1_type'),
        Index('ix_relationships_entity2', 'entity2_id', 'entity2_type'),
        Index('ix_relationships_pair', 'entity1_id', 'entity1_type', 'entity2_id', 'entity2_type'),
        {'extend_existing': True}
    )

    # First entity (any type)
    entity1_id = db.Column(db.Integer, nullable=False)
    entity1_type = db.Column(SQLEnum(EntityType, values_callable=enum_values, name='entitytype', native_enum=False), nullable=False)

    # Second entity (any type)
    entity2_id = db.Column(db.Integer, nullable=False)
    entity2_type = db.Column(SQLEnum(EntityType, values_callable=enum_values, name='entitytype', native_enum=False), nullable=False)

    # Relationship details
    relationship_type = db.Column(db.String(50))  # friend, rival, enemy, etc.
    relationship_value = db.Column(db.Integer, default=0)  # -100 to 100

    def to_dict(self):
        base_dict = super().to_dict()
        relationship_dict = {
            'entity1_id': self.entity1_id,
            'entity1_type': self.entity1_type.value,
            'entity2_id': self.entity2_id,
            'entity2_type': self.entity2_type.value,
            'details': {
                'type': self.relationship_type,
                'value': self.relationship_value
            }
        }
        return {**base_dict, **relationship_dict}

class Interaction(BaseModel):
    """Model representing an interaction between any two entities."""
    __tablename__ = 'interactions'
    __table_args__ = (
        Index('ix_interactions_entity1', 'entity1_id', 'entity1_type'),
        Index('ix_interactions_entity2', 'entity2_id', 'entity2_type'),
        Index('ix_interactions_pair', 'entity1_id', 'entity1_type', 'entity2_id', 'entity2_type'),
        {'extend_existing': True}
    )

    # Initiator (Character)
    initiator_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=True)
    initiator = db.relationship('Character', back_populates='initiated_interactions', foreign_keys=[initiator_id])

    # First entity (any type)
    entity1_id = db.Column(db.Integer, nullable=False)
    entity1_type = db.Column(SQLEnum(EntityType, values_callable=enum_values, name='entitytype', native_enum=False), nullable=False)

    # Second entity (any type)
    entity2_id = db.Column(db.Integer, nullable=False)
    entity2_type = db.Column(SQLEnum(EntityType, values_callable=enum_values, name='entitytype', native_enum=False), nullable=False)

    # Interaction details
    interaction_type = db.Column(db.String(50))  # conversation, trade, gift, etc.
    outcome = db.Column(db.String(50))  # success, failure, neutral
    impact = db.Column(db.Integer)  # -100 to 100

    def to_dict(self):
        return {
            'id': self.id,
            'entity1_id': self.entity1_id,
            'entity1_type': self.entity1_type.value,
            'entity2_id': self.entity2_id,
            'entity2_type': self.entity2_type.value,
            'interaction_type': self.interaction_type,
            'outcome': self.outcome,
            'impact': self.impact,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Reputation(BaseModel):
    """Model representing reputation between any two entities of any type."""
    __tablename__ = 'reputations'
    __table_args__ = (
        Index('ix_reputations_source', 'source_entity_id', 'source_entity_type'),
        Index('ix_reputations_target', 'target_entity_id', 'target_entity_type'),
        Index('ix_reputations_pair', 'source_entity_id', 'source_entity_type', 'target_entity_id', 'target_entity_type'),
        {'extend_existing': True}
    )

    # Source entity (the one holding the reputation)
    source_entity_id = db.Column(db.Integer, nullable=False)
    source_entity_type = db.Column(SQLEnum(EntityType, values_callable=enum_values, name='entitytype', native_enum=False), nullable=False)

    # Target entity (the one being judged)
    target_entity_id = db.Column(db.Integer, nullable=False)
    target_entity_type = db.Column(SQLEnum(EntityType, values_callable=enum_values, name='entitytype', native_enum=False), nullable=False)

    # Reputation details
    value = db.Column(db.Integer, default=0)  # -100 to 100
    rank = db.Column(db.String(50))  # hated, neutral, friendly, exalted, etc.
    strength = db.Column(db.Integer, default=1)  # 0 (unknown) to 100 (well-known)
    last_updated = db.Column(db.DateTime, nullable=True)
    change_source = db.Column(db.String(100), nullable=True)
    context = db.Column(db.String(255), nullable=True)  # Optional: context for the relationship
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'strength') or self.strength is None:
            self.strength = 1
        if not hasattr(self, 'last_updated') or self.last_updated is None:
            self.last_updated = datetime.utcnow()
        if not hasattr(self, 'change_source') or self.change_source is None:
            self.change_source = 'system'

    def to_dict(self):
        base_dict = super().to_dict()
        reputation_dict = {
            'source_entity_id': self.source_entity_id,
            'source_entity_type': self.source_entity_type.value,
            'target_entity_id': self.target_entity_id,
            'target_entity_type': self.target_entity_type.value,
            'details': {
                'value': self.value,
                'rank': self.rank,
                'strength': self.strength,
                'last_updated': self.last_updated.isoformat() if self.last_updated else None,
                'change_source': self.change_source,
                'context': self.context
            }
        }
        return {**base_dict, **reputation_dict}

# NOTE: Migration required to convert existing reputation data to new schema and populate entity types/IDs accordingly. 

# NOTE: Migration required to convert existing relationship data to new schema and populate entity types/IDs accordingly. 