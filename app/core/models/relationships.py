"""
Model relationships for the game.
"""

from sqlalchemy import Table, Column, Integer, ForeignKey, String, JSON, Index
from sqlalchemy.orm import relationship
from app.core.database import db
from app.core.models.base import BaseModel

# Import all models at the top level
from app.core.models.user import User
from app.core.models.character import Character
from app.core.models.region import Region
from app.core.models.party import Party
from app.core.models.status import StatusEffect
from app.core.models.spell import Spell
from app.core.models.quest import Quest
from app.core.models.inventory import InventoryItem
from app.core.models.social import SocialInteraction
from app.core.models.combat import CombatStats
from app.core.models.save import SaveGame

# Many-to-many relationship tables
character_party = Table(
    'character_party',
    BaseModel.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('party_id', Integer, ForeignKey('parties.id'), primary_key=True),
    Index('ix_character_party_character_id', 'character_id'),
    Index('ix_character_party_party_id', 'party_id')
)

character_quest = Table(
    'character_quest',
    BaseModel.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('quest_id', Integer, ForeignKey('quests.id'), primary_key=True),
    Index('ix_character_quests_composite', 'character_id', 'quest_id')
)

character_spell = Table(
    'character_spell',
    BaseModel.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('spell_id', Integer, ForeignKey('spells.id'), primary_key=True),
    Index('ix_character_spell_character_id', 'character_id')
)

party_quest = Table(
    'party_quest',
    BaseModel.metadata,
    Column('party_id', Integer, ForeignKey('parties.id'), primary_key=True),
    Column('quest_id', Integer, ForeignKey('quests.id'), primary_key=True),
    Index('ix_party_quest_party_id', 'party_id')
)

party_region = Table(
    'party_region',
    BaseModel.metadata,
    Column('party_id', Integer, ForeignKey('parties.id'), primary_key=True),
    Column('region_id', Integer, ForeignKey('regions.id'), primary_key=True),
    Index('ix_party_region_composite', 'party_id', 'region_id')
)

def setup_relationships():
    """Set up model relationships."""
    from app.core.models.character import Character
    from app.core.models.party import Party
    from app.core.models.region import Region
    from app.core.models.spell import Spell
    from app.core.models.user import User
    
    # Character relationships
    Character.parties = relationship('Party', secondary=character_party, back_populates='members')
    Character.user = relationship('User', back_populates='characters')
    Character.current_region = relationship('Region', foreign_keys=[Character.current_region_id], lazy='selectin')
    Character.spells = relationship('Spell', secondary=character_spell, back_populates='characters')
    
    # Party relationships
    Party.members = relationship('Character', secondary=character_party, back_populates='parties')
    Party.quests = relationship('app.core.models.quest.Quest', secondary=party_quest, back_populates='parties')
    Party.regions = relationship('Region', secondary=party_region, back_populates='parties')
    
    # Region relationships
    Region.parties = relationship('Party', secondary=party_region, back_populates='regions')
    Region.characters = relationship('Character', back_populates='current_region')
    
    # Quest relationships
    Quest.parties = relationship('Party', secondary=party_quest, back_populates='quests')
    
    # Spell relationships
    Spell.characters = relationship('Character', secondary=character_spell, back_populates='spells')

    # User relationships
    User.characters = relationship('Character', back_populates='user')