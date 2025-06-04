"""
Migration System for Visual DM Database

This module provides comprehensive database migration capabilities including
schema versioning, data transformation, and rollback mechanisms.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import hashlib

from sqlalchemy import text, MetaData, Table, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext

from backend.infrastructure.database import get_db, engine
from backend.infrastructure.validation.data_validation import ValidationService


class MigrationStatus(Enum):
    """Migration execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationInfo:
    """Information about a migration"""
    version: str
    name: str
    description: str
    created_at: datetime
    status: MigrationStatus
    checksum: str
    execution_time: Optional[float] = None
    error_message: Optional[str] = None


class MigrationTracker:
    """Tracks migration execution and status"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Ensure migration tracking table exists"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS migration_history (
            id SERIAL PRIMARY KEY,
            version VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50) NOT NULL,
            checksum VARCHAR(64) NOT NULL,
            execution_time REAL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.db.execute(text(create_table_sql))
        self.db.commit()
    
    def record_migration(self, migration: MigrationInfo):
        """Record migration execution"""
        insert_sql = """
        INSERT INTO migration_history 
        (version, name, description, status, checksum, execution_time, error_message)
        VALUES (:version, :name, :description, :status, :checksum, :execution_time, :error_message)
        ON CONFLICT (version) DO UPDATE SET
            status = :status,
            execution_time = :execution_time,
            error_message = :error_message,
            updated_at = CURRENT_TIMESTAMP
        """
        
        self.db.execute(text(insert_sql), {
            'version': migration.version,
            'name': migration.name,
            'description': migration.description,
            'status': migration.status.value,
            'checksum': migration.checksum,
            'execution_time': migration.execution_time,
            'error_message': migration.error_message
        })
        self.db.commit()
    
    def get_migration_status(self, version: str) -> Optional[MigrationStatus]:
        """Get status of a specific migration"""
        result = self.db.execute(
            text("SELECT status FROM migration_history WHERE version = :version"),
            {'version': version}
        ).fetchone()
        
        return MigrationStatus(result[0]) if result else None
    
    def get_completed_migrations(self) -> List[str]:
        """Get list of completed migration versions"""
        results = self.db.execute(
            text("SELECT version FROM migration_history WHERE status = 'completed' ORDER BY created_at")
        ).fetchall()
        
        return [row[0] for row in results]
    
    def get_migration_history(self) -> List[MigrationInfo]:
        """Get complete migration history"""
        results = self.db.execute(
            text("""
                SELECT version, name, description, status, checksum, 
                       execution_time, error_message, created_at
                FROM migration_history 
                ORDER BY created_at
            """)
        ).fetchall()
        
        return [
            MigrationInfo(
                version=row[0],
                name=row[1],
                description=row[2],
                status=MigrationStatus(row[3]),
                checksum=row[4],
                execution_time=row[5],
                error_message=row[6],
                created_at=row[7]
            )
            for row in results
        ]


class DataTransformer:
    """Handles data transformation during migrations"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.validation_service = ValidationService(self.db)
    
    def transform_character_data(self, old_format: Dict[str, Any]) -> Dict[str, Any]:
        """Transform character data from old to new format"""
        new_format = old_format.copy()
        
        # Example transformation: convert old stats format to new attributes format (ability_scores)
        if 'stats' in old_format and 'ability_scores' not in old_format:
            stats = old_format['stats']  # Reading from old format
            new_format['ability_scores'] = {
                'STR': stats.get('strength', 10),
                'DEX': stats.get('dexterity', 10),
                'CON': stats.get('constitution', 10),
                'INT': stats.get('intelligence', 10),
                'WIS': stats.get('wisdom', 10),
                'CHA': stats.get('charisma', 10)
            }
            del new_format['stats']
        
        # Convert old location format
        if 'location' in old_format and isinstance(old_format['location'], str):
            # Convert string location to UUID reference
            new_format['current_location'] = old_format['location']
            del new_format['location']
        
        return new_format
    
    def transform_region_data(self, old_format: Dict[str, Any]) -> Dict[str, Any]:
        """Transform region data from old to new format"""
        new_format = old_format.copy()
        
        # Convert old coordinate format
        if 'x' in old_format and 'y' in old_format:
            new_format['coordinates'] = {
                'x': old_format['x'],
                'y': old_format['y'],
                'z': old_format.get('z', 0)
            }
            for coord in ['x', 'y', 'z']:
                if coord in new_format:
                    del new_format[coord]
        
        # Convert old biome format
        if 'biome' in old_format and 'biome_type' not in old_format:
            new_format['biome_type'] = old_format['biome']
            del new_format['biome']
        
        return new_format
    
    def validate_transformed_data(self, entity_type: str, data: Dict[str, Any]) -> bool:
        """Validate transformed data"""
        result = self.validation_service.validate_entity(entity_type, data)
        if not result.is_valid:
            logging.error(f"Validation failed for {entity_type}: {result.errors}")
            return False
        return True


class MigrationScript:
    """Base class for migration scripts"""
    
    def __init__(self, version: str, name: str, description: str):
        self.version = version
        self.name = name
        self.description = description
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum for migration integrity"""
        content = f"{self.version}{self.name}{self.description}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def up(self, db: Session) -> None:
        """Execute migration (override in subclasses)"""
        raise NotImplementedError
    
    def down(self, db: Session) -> None:
        """Rollback migration (override in subclasses)"""
        raise NotImplementedError
    
    def validate(self, db: Session) -> bool:
        """Validate migration can be executed"""
        return True


class CreateCharacterEntitiesTable(MigrationScript):
    """Migration to create character entities table"""
    
    def __init__(self):
        super().__init__(
            version="001",
            name="create_character_entities",
            description="Create character entities table with comprehensive character data"
        )
    
    def up(self, db: Session) -> None:
        """Create character entities table"""
        create_sql = """
        CREATE TABLE IF NOT EXISTS character_entities (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            character_type VARCHAR(100) DEFAULT 'player',
            level INTEGER DEFAULT 1,
            experience_points INTEGER DEFAULT 0,
            hit_points_current INTEGER DEFAULT 1,
            hit_points_maximum INTEGER DEFAULT 1,
            race VARCHAR(100),
            alignment VARCHAR(50),
            languages JSONB,
            proficiencies JSONB,
            faction_memberships JSONB,
            relationships JSONB,
            reputation JSONB,
            current_status VARCHAR(50) DEFAULT 'alive',
            conditions JSONB,
            resources JSONB,
            status VARCHAR(50) DEFAULT 'active',
            properties JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        
        CREATE INDEX IF NOT EXISTS idx_character_name ON character_entities(name);
        CREATE INDEX IF NOT EXISTS idx_character_type ON character_entities(character_type);
        CREATE INDEX IF NOT EXISTS idx_character_location ON character_entities(current_location);
        CREATE INDEX IF NOT EXISTS idx_character_status ON character_entities(status);
        """
        
        db.execute(text(create_sql))
        db.commit()
    
    def down(self, db: Session) -> None:
        """Drop character entities table"""
        db.execute(text("DROP TABLE IF EXISTS character_entities CASCADE;"))
        db.commit()


class CreateRegionEntitiesTable(MigrationScript):
    """Migration to create region entities table"""
    
    def __init__(self):
        super().__init__(
            version="002",
            name="create_region_entities",
            description="Create region entities table for world geography"
        )
    
    def up(self, db: Session) -> None:
        """Create region entities table"""
        create_sql = """
        CREATE TABLE IF NOT EXISTS region_entities (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            coordinates JSONB,
            biome_type VARCHAR(100),
            climate_data JSONB,
            resource_abundance JSONB,
            political_control UUID,
            population_density INTEGER DEFAULT 0,
            development_level VARCHAR(50) DEFAULT 'wilderness',
            trade_routes JSONB,
            status VARCHAR(50) DEFAULT 'active',
            properties JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        
        CREATE INDEX IF NOT EXISTS idx_region_name ON region_entities(name);
        CREATE INDEX IF NOT EXISTS idx_region_coordinates ON region_entities USING GIN(coordinates);
        CREATE INDEX IF NOT EXISTS idx_region_biome ON region_entities(biome_type);
        CREATE INDEX IF NOT EXISTS idx_region_political_control ON region_entities(political_control);
        """
        
        db.execute(text(create_sql))
        db.commit()
    
    def down(self, db: Session) -> None:
        """Drop region entities table"""
        db.execute(text("DROP TABLE IF EXISTS region_entities CASCADE;"))
        db.commit()


class MigrationEngine:
    """Main migration execution engine"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.tracker = MigrationTracker(self.db)
        self.transformer = DataTransformer(self.db)
        self.migrations = self._load_migrations()
        self.logger = logging.getLogger(__name__)
    
    def _load_migrations(self) -> Dict[str, MigrationScript]:
        """Load all available migrations"""
        return {
            "001": CreateCharacterEntitiesTable(),
            "002": CreateRegionEntitiesTable(),
            # Add more migrations here
        }
    
    def get_pending_migrations(self) -> List[MigrationScript]:
        """Get list of pending migrations"""
        completed = set(self.tracker.get_completed_migrations())
        pending = []
        
        for version in sorted(self.migrations.keys()):
            if version not in completed:
                pending.append(self.migrations[version])
        
        return pending
    
    def execute_migration(self, migration: MigrationScript) -> bool:
        """Execute a single migration"""
        start_time = datetime.now()
        
        migration_info = MigrationInfo(
            version=migration.version,
            name=migration.name,
            description=migration.description,
            created_at=start_time,
            status=MigrationStatus.RUNNING,
            checksum=migration.checksum
        )
        
        try:
            # Record migration start
            self.tracker.record_migration(migration_info)
            
            # Validate migration can be executed
            if not migration.validate(self.db):
                raise Exception("Migration validation failed")
            
            # Execute migration
            self.logger.info(f"Executing migration {migration.version}: {migration.name}")
            migration.up(self.db)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Record success
            migration_info.status = MigrationStatus.COMPLETED
            migration_info.execution_time = execution_time
            self.tracker.record_migration(migration_info)
            
            self.logger.info(f"Migration {migration.version} completed in {execution_time:.2f}s")
            return True
            
        except Exception as e:
            # Record failure
            migration_info.status = MigrationStatus.FAILED
            migration_info.error_message = str(e)
            migration_info.execution_time = (datetime.now() - start_time).total_seconds()
            self.tracker.record_migration(migration_info)
            
            self.logger.error(f"Migration {migration.version} failed: {e}")
            return False
    
    def rollback_migration(self, migration: MigrationScript) -> bool:
        """Rollback a migration"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Rolling back migration {migration.version}: {migration.name}")
            migration.down(self.db)
            
            # Update migration status
            migration_info = MigrationInfo(
                version=migration.version,
                name=migration.name,
                description=migration.description,
                created_at=start_time,
                status=MigrationStatus.ROLLED_BACK,
                checksum=migration.checksum,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            self.tracker.record_migration(migration_info)
            
            self.logger.info(f"Migration {migration.version} rolled back successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback of migration {migration.version} failed: {e}")
            return False
    
    def migrate_to_latest(self) -> bool:
        """Execute all pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            self.logger.info("No pending migrations")
            return True
        
        self.logger.info(f"Executing {len(pending)} pending migrations")
        
        for migration in pending:
            if not self.execute_migration(migration):
                self.logger.error(f"Migration failed at {migration.version}, stopping")
                return False
        
        self.logger.info("All migrations completed successfully")
        return True
    
    def migrate_to_version(self, target_version: str) -> bool:
        """Migrate to a specific version"""
        completed = set(self.tracker.get_completed_migrations())
        target_versions = []
        
        # Determine which migrations to run
        for version in sorted(self.migrations.keys()):
            if version <= target_version and version not in completed:
                target_versions.append(version)
        
        if not target_versions:
            self.logger.info(f"Already at or past version {target_version}")
            return True
        
        # Execute migrations
        for version in target_versions:
            migration = self.migrations[version]
            if not self.execute_migration(migration):
                return False
        
        return True
    
    def rollback_to_version(self, target_version: str) -> bool:
        """Rollback to a specific version"""
        completed = self.tracker.get_completed_migrations()
        
        # Find migrations to rollback (in reverse order)
        to_rollback = []
        for version in reversed(completed):
            if version > target_version:
                to_rollback.append(version)
        
        if not to_rollback:
            self.logger.info(f"Already at or before version {target_version}")
            return True
        
        # Execute rollbacks
        for version in to_rollback:
            if version in self.migrations:
                migration = self.migrations[version]
                if not self.rollback_migration(migration):
                    return False
        
        return True
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get overall migration status"""
        history = self.tracker.get_migration_history()
        pending = self.get_pending_migrations()
        
        return {
            'current_version': history[-1].version if history else None,
            'total_migrations': len(self.migrations),
            'completed_migrations': len([h for h in history if h.status == MigrationStatus.COMPLETED]),
            'pending_migrations': len(pending),
            'failed_migrations': len([h for h in history if h.status == MigrationStatus.FAILED]),
            'history': [
                {
                    'version': h.version,
                    'name': h.name,
                    'status': h.status.value,
                    'execution_time': h.execution_time,
                    'created_at': h.created_at.isoformat() if h.created_at else None
                }
                for h in history
            ]
        }


class PerformanceMonitor:
    """Monitor migration performance and database health"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def check_table_sizes(self) -> Dict[str, Dict[str, Any]]:
        """Check sizes of all tables"""
        size_query = """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
        """
        
        results = self.db.execute(text(size_query)).fetchall()
        
        return {
            row[1]: {
                'size_pretty': row[2],
                'size_bytes': row[3]
            }
            for row in results
        }
    
    def check_index_usage(self) -> Dict[str, Dict[str, Any]]:
        """Check index usage statistics"""
        index_query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
        ORDER BY idx_scan DESC;
        """
        
        results = self.db.execute(text(index_query)).fetchall()
        
        return {
            f"{row[1]}.{row[2]}": {
                'scans': row[3],
                'tuples_read': row[4],
                'tuples_fetched': row[5]
            }
            for row in results
        }
    
    def check_query_performance(self) -> List[Dict[str, Any]]:
        """Check slow query performance"""
        # This requires pg_stat_statements extension
        slow_query = """
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            rows
        FROM pg_stat_statements
        WHERE mean_time > 100  -- queries taking more than 100ms on average
        ORDER BY mean_time DESC
        LIMIT 10;
        """
        
        try:
            results = self.db.execute(text(slow_query)).fetchall()
            return [
                {
                    'query': row[0][:100] + '...' if len(row[0]) > 100 else row[0],
                    'calls': row[1],
                    'total_time': row[2],
                    'mean_time': row[3],
                    'rows': row[4]
                }
                for row in results
            ]
        except SQLAlchemyError:
            # pg_stat_statements not available
            return [] 