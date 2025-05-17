"""
Core models package initialization.
"""

from app.core.database import db
from app.core.models.base import BaseModel
from app.core.models.combat import CombatStats, Combat, CombatParticipant, CombatAction, CombatState
from app.core.models.infraction import Infraction
from app.core.models.consequence import Consequence
from app.core.models.api_key import APIKey
from .poi_evolution import POIState, POITransition, POIHistory
from .world import World, Region, Resource, Faction
from .save import SaveGame
from app.social.models.social import Reputation, Relationship, Interaction, EntityType
from app.core.models.user import User
from app.core.models.role import Role
from app.core.models.permission import Permission

__all__ = [
    'db',
    'BaseModel',
    'CombatStats',
    'Combat',
    'CombatParticipant',
    'CombatAction',
    'CombatState',
    'SaveGame',
    'Infraction',
    'Consequence',
    'APIKey',
    'POIState',
    'POITransition',
    'POIHistory',
    'World',
    'Region',
    'Resource',
    'Faction',
    'Reputation',
    'Relationship',
    'Interaction',
    'EntityType',
    'Permission',
] 