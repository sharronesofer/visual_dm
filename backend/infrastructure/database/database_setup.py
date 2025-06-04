"""
Database Setup and Initialization

Handles database creation, table initialization, and migration for the equipment system.
This script ensures the database is properly set up for all equipment operations.
"""

import logging
from typing import Optional, List
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from .config import get_database_url, get_database_config
from .models.equipment_models import Base, EquipmentInstance, EquipmentTemplate, MagicalEffect, CharacterEquipmentSlot, EquipmentMaintenanceRecord

logger = logging.getLogger(__name__)


class DatabaseSetup:
    """Handles database initialization and setup for the equipment system."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database setup with optional custom URL."""
        self.database_url = database_url or get_database_url()
        self.config = get_database_config()
        self.engine = None
        self.SessionLocal = None
        
    def initialize_database(self, force_recreate: bool = False) -> bool:
        """
        Initialize the database with all required tables.
        
        Args:
            force_recreate: If True, drop existing tables and recreate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create engine
            engine_kwargs = {
                "echo": self.config.get("echo", False),
                "pool_pre_ping": self.config.get("pool_pre_ping", True)
            }
            
            # Add database-specific configurations
            if "connect_args" in self.config:
                engine_kwargs["connect_args"] = self.config["connect_args"]
                
            self.engine = create_engine(self.database_url, **engine_kwargs)
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info(f"Database connection established: {self._get_safe_url()}")
            
            # Check if tables exist
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            equipment_tables = [
                'equipment_instances',
                'applied_enchantments', 
                'maintenance_records'
            ]
            
            tables_exist = all(table in existing_tables for table in equipment_tables)
            
            if force_recreate or not tables_exist:
                logger.info("Creating database tables...")
                self._create_tables(force_recreate)
                
                # Insert default data
                self._insert_default_data()
                
                logger.info("Database initialization completed successfully")
            else:
                logger.info("Database tables already exist")
            
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def _create_tables(self, drop_existing: bool = False):
        """Create all database tables."""
        try:
            if drop_existing:
                logger.warning("Dropping existing tables...")
                Base.metadata.drop_all(bind=self.engine)
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create equipment system specific tables using raw SQL for compatibility
            with self.engine.connect() as conn:
                # Create equipment_instances table if not exists
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS equipment_instances (
                        id TEXT PRIMARY KEY,
                        character_id TEXT NOT NULL,
                        template_id TEXT NOT NULL,
                        slot TEXT NOT NULL,
                        current_durability INTEGER NOT NULL DEFAULT 100,
                        max_durability INTEGER NOT NULL DEFAULT 100,
                        usage_count INTEGER NOT NULL DEFAULT 0,
                        quality_tier TEXT NOT NULL DEFAULT 'basic',
                        rarity_tier TEXT NOT NULL DEFAULT 'common',
                        enchantment_seed INTEGER,
                        is_equipped BOOLEAN NOT NULL DEFAULT FALSE,
                        equipment_set TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create applied_enchantments table if not exists
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS applied_enchantments (
                        id TEXT PRIMARY KEY,
                        equipment_id TEXT NOT NULL,
                        enchantment_type TEXT NOT NULL,
                        magnitude REAL NOT NULL,
                        target_attribute TEXT,
                        is_active BOOLEAN NOT NULL DEFAULT TRUE,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (equipment_id) REFERENCES equipment_instances (id) ON DELETE CASCADE
                    )
                """))
                
                # Create maintenance_records table if not exists
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS maintenance_records (
                        id TEXT PRIMARY KEY,
                        equipment_id TEXT NOT NULL,
                        record_type TEXT NOT NULL,
                        durability_before INTEGER NOT NULL,
                        durability_after INTEGER NOT NULL,
                        cost INTEGER,
                        description TEXT,
                        performed_by TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (equipment_id) REFERENCES equipment_instances (id) ON DELETE CASCADE
                    )
                """))
                
                # Create indexes for performance
                self._create_indexes(conn)
                
                conn.commit()
                logger.info("Equipment system tables created successfully")
                
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def _create_indexes(self, conn):
        """Create database indexes for performance."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_equipment_character_id ON equipment_instances(character_id)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_template_id ON equipment_instances(template_id)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_slot ON equipment_instances(slot)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_set ON equipment_instances(equipment_set)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_equipped ON equipment_instances(is_equipped)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_character_equipped ON equipment_instances(character_id, is_equipped)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_quality_tier ON equipment_instances(quality_tier)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_rarity_tier ON equipment_instances(rarity_tier)",
            "CREATE INDEX IF NOT EXISTS idx_enchantment_equipment_id ON applied_enchantments(equipment_id)",
            "CREATE INDEX IF NOT EXISTS idx_enchantment_type ON applied_enchantments(enchantment_type)",
            "CREATE INDEX IF NOT EXISTS idx_enchantment_active ON applied_enchantments(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_maintenance_equipment_id ON maintenance_records(equipment_id)",
            "CREATE INDEX IF NOT EXISTS idx_maintenance_type ON maintenance_records(record_type)",
            "CREATE INDEX IF NOT EXISTS idx_maintenance_timestamp ON maintenance_records(timestamp)",
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
            except Exception as e:
                logger.warning(f"Error creating index: {e}")
    
    def _insert_default_data(self):
        """Insert default data needed for the equipment system."""
        try:
            with self.SessionLocal() as session:
                # Check if default data already exists
                result = session.execute(text("SELECT COUNT(*) as count FROM equipment_instances")).fetchone()
                if result and result.count > 0:
                    logger.info("Default equipment data already exists")
                    return
                
                # Insert some sample equipment for testing
                logger.info("Inserting default equipment data...")
                
                # This would normally load from template files, but for now we'll skip it
                # since the template loading is handled by the template repository
                
                session.commit()
                logger.info("Default data inserted successfully")
                
        except Exception as e:
            logger.error(f"Error inserting default data: {e}")
    
    def _get_safe_url(self) -> str:
        """Get database URL with password masked for logging."""
        try:
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(self.database_url)
            
            if parsed.password:
                # Replace password with asterisks
                netloc = f"{parsed.username}:***@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                
                safe_parsed = parsed._replace(netloc=netloc)
                return urlunparse(safe_parsed)
            
            return self.database_url
        except:
            return "database_url_parsing_failed"
    
    def test_database_connection(self) -> bool:
        """Test the database connection and basic operations."""
        try:
            if not self.engine:
                logger.error("Database engine not initialized")
                return False
            
            with self.engine.connect() as conn:
                # Test basic connection
                conn.execute(text("SELECT 1"))
                
                # Test equipment tables exist
                tables_result = conn.execute(text("""
                    SELECT name FROM sqlite_master WHERE type='table' AND name IN 
                    ('equipment_instances', 'applied_enchantments', 'maintenance_records')
                """)).fetchall()
                
                expected_tables = 3
                found_tables = len(tables_result)
                
                if found_tables < expected_tables:
                    logger.warning(f"Expected {expected_tables} equipment tables, found {found_tables}")
                    return False
                
                logger.info("Database connection and table verification successful")
                return True
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_session(self):
        """Get a database session."""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        return self.SessionLocal()


# Global database setup instance
database_setup = DatabaseSetup()


def initialize_equipment_database(force_recreate: bool = False) -> bool:
    """
    Initialize the equipment database.
    
    Args:
        force_recreate: If True, drop and recreate all tables
        
    Returns:
        True if successful, False otherwise
    """
    return database_setup.initialize_database(force_recreate)


def test_equipment_database() -> bool:
    """
    Test the equipment database connection and setup.
    
    Returns:
        True if database is properly set up, False otherwise
    """
    return database_setup.test_database_connection()


def get_equipment_database_session():
    """Get a database session for equipment operations."""
    return database_setup.get_session() 