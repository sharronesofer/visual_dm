"""
Equipment-Only Database Setup

Simple database setup that only creates equipment-related tables without
conflicting with other system database models.
"""

import logging
import sqlite3
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class EquipmentDatabase:
    """Simple equipment database manager."""
    
    def __init__(self, db_path: str = "equipment.db"):
        """Initialize with database path."""
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Connect to the database."""
        try:
            # Create directory if needed
            db_file = Path(self.db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            
            logger.info(f"Connected to equipment database: {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def initialize_tables(self, force_recreate: bool = False):
        """Create equipment tables."""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            if force_recreate:
                # Drop existing tables
                cursor.execute("DROP TABLE IF EXISTS maintenance_records")
                cursor.execute("DROP TABLE IF EXISTS applied_enchantments")
                cursor.execute("DROP TABLE IF EXISTS equipment_instances")
            
            # Create equipment_instances table
            cursor.execute("""
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
            """)
            
            # Create applied_enchantments table
            cursor.execute("""
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
            """)
            
            # Create maintenance_records table
            cursor.execute("""
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
            """)
            
            # Create indexes
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
                cursor.execute(index_sql)
            
            self.connection.commit()
            logger.info("Equipment tables and indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def test_connection(self):
        """Test database connection and table existence."""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            # Test basic operation
            cursor.execute("SELECT 1")
            
            # Check that all tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN 
                ('equipment_instances', 'applied_enchantments', 'maintenance_records')
            """)
            
            tables = cursor.fetchall()
            if len(tables) < 3:
                logger.error(f"Expected 3 tables, found {len(tables)}")
                return False
            
            logger.info("Database connection and tables verified")
            return True
            
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute a query and return results."""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = None):
        """Execute an update/insert/delete query."""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        self.connection.commit()
        return cursor.rowcount
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None


# Global equipment database instance
equipment_db = EquipmentDatabase()


def get_equipment_db():
    """Get the equipment database instance."""
    if not equipment_db.connection:
        if not equipment_db.connect():
            raise Exception("Cannot connect to equipment database")
        
        # Initialize tables if needed
        if not equipment_db.test_connection():
            equipment_db.initialize_tables()
    
    return equipment_db


def initialize_equipment_db(force_recreate: bool = False):
    """Initialize the equipment database."""
    db = get_equipment_db()
    return db.initialize_tables(force_recreate)


def test_equipment_db():
    """Test the equipment database."""
    try:
        db = get_equipment_db()
        return db.test_connection()
    except:
        return False 