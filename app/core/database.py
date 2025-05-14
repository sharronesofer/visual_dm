"""
Database configuration and initialization.
"""

from flask_migrate import Migrate
from flask import Flask
from typing import Optional
import os
from app.core.db_base import db
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask-Migrate
migrate = Migrate()

def init_db(app: Flask) -> None:
    """
    Initialize database with Flask application.

    Args:
        app: Flask application instance
    """
    # Configure SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///app.db"  # Default to SQLite for development
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = app.debug  # Log SQL queries in debug mode

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models for migrations
    from app.core.models.combat import Combat, CombatState, CombatParticipant, CombatAction, CombatStats
    from app.core.models.user import User
    from app.core.models.role import Role
    from app.core.models.session import Session
    from app.core.models.world import World
    from app.core.models.region import Region
    from app.core.models.resource import Resource
    from app.core.models.trade_route import TradeRoute
    from app.core.models.base_model import BaseModel
    from app.core.models.quest import Quest, QuestStage, QuestDependency, QuestReward, QuestWorldImpact
    from app.core.models.npc import NPC
    from app.core.models.character import Character
    from app.core.models.party import Party
    from app.core.models.location import Location
    from app.core.models.faction import Faction
    from app.core.models.weather_system import WeatherSystem
    from app.core.models.world_event import WorldEvent
    from app.core.models.status import StatusEffect
    from app.core.models.location_version import LocationVersion
    from app.core.models.npc_version import NPCVersion
    from app.core.models.world_state import WorldState
    from app.core.models.version_control import VersionControl
    from app.core.models.quest_progress import QuestProgress
    from app.core.models.npc_activity_system import NPCActivitySystem
    from app.core.models.quest_system import QuestSystem
    from app.core.models.season_system import SeasonSystem
    from app.core.models.time_system import TimeSystem
    from app.core.models.consequence import Consequence
    from app.core.models.base import Base
    from app.core.models.infraction import Infraction
    from app.core.models.permission import Permission
    from app.core.models.item import Item
    # from app.core.models.relationships import Relationships
    from app.core.models.magic import Spell
    # from app.core.models.equipment import Equipment
    from app.core.models.save import SaveGame
    from app.core.models.point_of_interest import PointOfInterest
    from app.core.models.development import DevelopmentSystem
    from app.core.models.action import Action
    from app.core.models.npc_backstory import NPCBackstory
    from app.core.models.rumor import Rumor
    from app.core.models.memory import Memory
    # from app.core.models.game_state import GameState
    # from app.core.models.feats import Feats

    # Create tables
    with app.app_context():
        db.create_all()

        # Create default roles
        Role.create_default_roles()

def create_tables(app: Flask) -> None:
    """
    Create all database tables.

    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.create_all()

def drop_tables(app: Flask) -> None:
    """
    Drop all database tables.

    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()

def get_engine_url() -> str:
    """
    Get database engine URL from environment.

    Returns:
        Database URL string
    """
    return os.getenv("DATABASE_URL", "sqlite:///app.db")

def get_connection() -> Optional[SQLAlchemy]:
    """
    Get database connection.

    Returns:
        SQLAlchemy instance if initialized, None otherwise
    """
    return db if db.get_app() else None

def get_db():
    """
    Get database instance.

    Returns:
        SQLAlchemy: Database instance
    """
    return db

def create_all_tables():
    """Create all tables in the database (for development/manual migration)."""
    db.create_all() 