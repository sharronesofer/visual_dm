"""
Database initialization module with comprehensive error handling.
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
    ProgrammingError,
    DataError
)
from sqlalchemy.orm import Session
from app.core.database import db
from app.core.utils.error_utils import DatabaseError
from app.models.region import Region
from app.models.faction import Faction
from app.models.point_of_interest import PointOfInterest
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def init_db() -> bool:
    """
    Initialize the database with proper error handling.
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        logger.info("Starting database initialization...")
        
        # Create all tables
        logger.info("Creating database tables...")
        db.create_all()
        
        # Initialize default data
        logger.info("Initializing default data...")
        _init_default_data()
        
        # Commit all changes
        logger.info("Committing database changes...")
        db.session.commit()
        logger.info("Database initialization completed successfully")
        return True

    except IntegrityError as e:
        logger.error(f"Database integrity error during initialization: {str(e)}")
        db.session.rollback()
        raise DatabaseError(
            message="Database integrity constraint violation",
            details={"error": str(e), "type": "integrity_error"}
        )
        
    except OperationalError as e:
        logger.error(f"Database connection error during initialization: {str(e)}")
        db.session.rollback()
        raise DatabaseError(
            message="Database connection error",
            details={"error": str(e), "type": "connection_error"}
        )
        
    except ProgrammingError as e:
        logger.error(f"Database programming error during initialization: {str(e)}")
        db.session.rollback()
        raise DatabaseError(
            message="Database programming error",
            details={"error": str(e), "type": "programming_error"}
        )
        
    except DataError as e:
        logger.error(f"Database data error during initialization: {str(e)}")
        db.session.rollback()
        raise DatabaseError(
            message="Database data error",
            details={"error": str(e), "type": "data_error"}
        )
        
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during initialization: {str(e)}")
        db.session.rollback()
        raise DatabaseError(
            message="Database error",
            details={"error": str(e), "type": "sqlalchemy_error"}
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        db.session.rollback()
        raise DatabaseError(
            message="Unexpected database error",
            details={"error": str(e), "type": "unexpected_error"}
        )

def _init_default_data() -> None:
    """
    Initialize default data in the database.
    
    Raises:
        DatabaseError: If there's an error initializing default data
    """
    try:
        # Create a starting faction
        logger.info("Creating initial faction...")
        faction = Faction(
            name="The Free Alliance",
            description="A coalition of free cities and settlements working together for mutual prosperity.",
            faction_type="merchant",
            properties={
                "trade_routes": 5,
                "diplomatic_influence": 75
            }
        )
        faction.power_level = 12
        faction.resources = {
            "gold": 1000,
            "influence": 75,
            "manpower": 500
        }
        faction.goals = ["Maintain peace", "Expand trade routes"]
        db.session.add(faction)
        db.session.flush()  # Get the faction ID
        logger.info(f"Created faction: {faction.name}")

        # Create a starting region
        logger.info("Creating initial region...")
        region = Region(
            name="Haven Valley",
            description="A peaceful valley nestled between protective mountains, known for its fertile lands and welcoming people.",
            region_type="settlement",
            properties={
                "population": 5000,
                "climate": "temperate",
                "terrain": "valley"
            },
            faction_id=faction.id
        )
        region.is_starting_region = True
        region.weather = {"current": "clear", "forecast": "sunny"}
        region.resources = {"wood": 100, "stone": 100, "food": 200}
        region.events = []
        region.discovered_pois = []
        db.session.add(region)
        db.session.flush()  # Get the region ID
        logger.info(f"Created region: {region.name}")

        # Create points of interest
        logger.info("Creating points of interest...")
        pois = [
            PointOfInterest(
                name="Haven Market Square",
                description="The bustling heart of Haven Valley, where traders and citizens gather.",
                poi_type="marketplace",
                region_id=region.id,
                coordinates={"x": 0, "y": 0},
                properties={
                    "vendor_count": 10,
                    "specialty": "general goods"
                },
                is_discovered=True
            ),
            PointOfInterest(
                name="Warrior's Rest Inn",
                description="A cozy inn where adventurers gather to share tales and find work.",
                poi_type="inn",
                region_id=region.id,
                coordinates={"x": 2, "y": 1},
                properties={
                    "rooms": 8,
                    "quest_board": True
                },
                is_discovered=True
            )
        ]
        
        for poi in pois:
            db.session.add(poi)
            logger.info(f"Created POI: {poi.name}")
    except Exception as e:
        logger.error(f"Error initializing default data: {str(e)}")
        raise DatabaseError(
            message="Failed to initialize default data",
            details={"error": str(e)}
        )

if __name__ == "__main__":
    try:
        success = init_db()
        if not success:
            logger.error("Database initialization failed")
            exit(1)
    except DatabaseError as e:
        logger.error(f"Database error during initialization: {e.message}")
        logger.error(f"Error details: {e.details}")
        exit(1)
    except Exception as e:
        logger.error(f"Fatal error during database initialization: {str(e)}")
        exit(1) 