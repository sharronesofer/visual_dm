#!/usr/bin/env python3
"""
Migration Script: Convert D&D Spell Slot Magic System to Canonical MP System

This migration script transforms the magic system from D&D spell slots to the
canonical MP-based system as defined in the Development Bible.

IMPORTANT: This migration makes irreversible changes to the database structure.
Make sure to backup your database before running this migration.

Usage:
    python 001_migrate_magic_to_canonical_mp_system.py [--dry-run] [--backup-dir path]
    
Options:
    --dry-run      Show what would be changed without making actual changes
    --backup-dir   Directory to store backup files (default: ./migration_backups)
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.infrastructure.database.database import DATABASE_URL, engine, SessionLocal
from sqlalchemy import text, inspect, MetaData, Table, Column, Integer, String, Boolean, DateTime, ARRAY, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Session
import uuid

class MagicSystemMigration:
    """Handles migration from D&D spell slots to canonical MP system"""
    
    def __init__(self, dry_run: bool = False, backup_dir: str = "./migration_backups"):
        self.dry_run = dry_run
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def log(self, message: str):
        """Log migration progress"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def backup_table_data(self, db: Session, table_name: str):
        """Backup table data to JSON file"""
        backup_file = self.backup_dir / f"{table_name}_{self.timestamp}.json"
        
        try:
            # Check if table exists
            inspector = inspect(engine)
            if table_name not in inspector.get_table_names():
                self.log(f"Table {table_name} does not exist, skipping backup")
                return None
            
            # Query all data
            result = db.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            columns = result.keys()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert non-serializable types
                    if hasattr(value, 'isoformat'):  # datetime
                        value = value.isoformat()
                    elif hasattr(value, '__dict__'):  # complex objects
                        value = str(value)
                    row_dict[col] = value
                data.append(row_dict)
            
            # Save to file
            with open(backup_file, 'w') as f:
                json.dump({
                    'table': table_name,
                    'timestamp': self.timestamp,
                    'row_count': len(data),
                    'data': data
                }, f, indent=2)
            
            self.log(f"Backed up {len(data)} rows from {table_name} to {backup_file}")
            return backup_file
            
        except Exception as e:
            self.log(f"Error backing up {table_name}: {e}")
            return None
    
    def check_old_tables_exist(self, db: Session) -> bool:
        """Check if old D&D magic tables exist"""
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        old_tables = ['spell_slots', 'spellbooks', 'prepared_spells', 'known_spells']
        existing_old_tables = [table for table in old_tables if table in table_names]
        
        if existing_old_tables:
            self.log(f"Found old D&D magic tables: {existing_old_tables}")
            return True
        else:
            self.log("No old D&D magic tables found")
            return False
    
    def backup_old_system(self, db: Session):
        """Backup all data from the old D&D magic system"""
        self.log("Starting backup of old D&D magic system data...")
        
        old_tables = ['spell_slots', 'spellbooks', 'prepared_spells', 'known_spells', 'spells']
        backup_files = []
        
        for table in old_tables:
            backup_file = self.backup_table_data(db, table)
            if backup_file:
                backup_files.append(backup_file)
        
        self.log(f"Backup completed. Files saved to: {self.backup_dir}")
        return backup_files
    
    def drop_old_tables(self, db: Session):
        """Drop old D&D magic system tables"""
        if self.dry_run:
            self.log("DRY RUN: Would drop old D&D magic tables")
            return
        
        self.log("Dropping old D&D magic system tables...")
        
        old_tables = ['spell_slots', 'spellbooks', 'prepared_spells', 'known_spells']
        
        for table in old_tables:
            try:
                db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                self.log(f"Dropped table: {table}")
            except Exception as e:
                self.log(f"Error dropping table {table}: {e}")
        
        db.commit()
    
    def create_canonical_tables(self, db: Session):
        """Create new canonical magic system tables using DDL"""
        if self.dry_run:
            self.log("DRY RUN: Would create canonical magic tables")
            return
        
        self.log("Creating canonical magic system tables...")
        
        try:
            # Check which database type we're using
            db_url = str(engine.url)
            is_postgres = 'postgresql' in db_url
            
            # Check existing tables and their structure
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            # Handle spells table migration/creation
            if 'spells' in existing_tables:
                # Check if spells table has canonical structure
                columns = inspector.get_columns('spells')
                column_names = [col['name'] for col in columns]
                
                if 'mp_cost' not in column_names:
                    self.log("Converting existing spells table to canonical structure...")
                    # Backup existing spells data
                    self.backup_table_data(db, 'spells')
                    
                    # Drop and recreate spells table with canonical structure
                    db.execute(text("DROP TABLE spells CASCADE"))
                    self.log("Dropped old spells table")
                    
                    # Create canonical spells table
                    self._create_canonical_spells_table(db, is_postgres)
                else:
                    self.log("Spells table already has canonical structure")
            else:
                # Create new canonical spells table
                self._create_canonical_spells_table(db, is_postgres)
            
            # Create character_mp table (if it doesn't exist)
            if 'character_mp' not in existing_tables:
                self.log("Creating character_mp table...")
                if is_postgres:
                    db.execute(text("""
                        CREATE TABLE character_mp (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            character_id INTEGER NOT NULL UNIQUE,
                            current_mp INTEGER NOT NULL,
                            max_mp INTEGER NOT NULL,
                            mp_regeneration_rate FLOAT NOT NULL DEFAULT 1.0,
                            last_rest TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    db.execute(text("""
                        CREATE TABLE character_mp (
                            id TEXT PRIMARY KEY,
                            character_id INTEGER NOT NULL UNIQUE,
                            current_mp INTEGER NOT NULL,
                            max_mp INTEGER NOT NULL,
                            mp_regeneration_rate REAL NOT NULL DEFAULT 1.0,
                            last_rest TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                self.log("Created character_mp table")
            
            # Create character_domain_access table (if it doesn't exist)
            if 'character_domain_access' not in existing_tables:
                self.log("Creating character_domain_access table...")
                if is_postgres:
                    db.execute(text("""
                        CREATE TABLE character_domain_access (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            character_id INTEGER NOT NULL,
                            domain VARCHAR(50) NOT NULL,
                            access_level INTEGER NOT NULL DEFAULT 1,
                            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(character_id, domain)
                        )
                    """))
                else:
                    db.execute(text("""
                        CREATE TABLE character_domain_access (
                            id TEXT PRIMARY KEY,
                            character_id INTEGER NOT NULL,
                            domain VARCHAR(50) NOT NULL,
                            access_level INTEGER NOT NULL DEFAULT 1,
                            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(character_id, domain)
                        )
                    """))
                self.log("Created character_domain_access table")
            
            # Create learned_spells table (if it doesn't exist)
            if 'learned_spells' not in existing_tables:
                self.log("Creating learned_spells table...")
                if is_postgres:
                    db.execute(text("""
                        CREATE TABLE learned_spells (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            character_id INTEGER NOT NULL,
                            spell_id UUID NOT NULL,
                            domain_learned VARCHAR(50) NOT NULL,
                            learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            mastery_level INTEGER DEFAULT 1,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(character_id, spell_id)
                        )
                    """))
                else:
                    db.execute(text("""
                        CREATE TABLE learned_spells (
                            id TEXT PRIMARY KEY,
                            character_id INTEGER NOT NULL,
                            spell_id TEXT NOT NULL,
                            domain_learned VARCHAR(50) NOT NULL,
                            learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            mastery_level INTEGER DEFAULT 1,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(character_id, spell_id)
                        )
                    """))
                self.log("Created learned_spells table")
            
            # Create concentration_tracking table (if it doesn't exist)
            if 'concentration_tracking' not in existing_tables:
                self.log("Creating concentration_tracking table...")
                if is_postgres:
                    db.execute(text("""
                        CREATE TABLE concentration_tracking (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            caster_id INTEGER NOT NULL,
                            spell_id UUID NOT NULL,
                            target_id INTEGER,
                            cast_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            expires_at TIMESTAMP,
                            domain_used VARCHAR(50) NOT NULL,
                            mp_spent INTEGER NOT NULL,
                            effect_data JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    db.execute(text("""
                        CREATE TABLE concentration_tracking (
                            id TEXT PRIMARY KEY,
                            caster_id INTEGER NOT NULL,
                            spell_id TEXT NOT NULL,
                            target_id INTEGER,
                            cast_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            expires_at TIMESTAMP,
                            domain_used VARCHAR(50) NOT NULL,
                            mp_spent INTEGER NOT NULL,
                            effect_data TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                self.log("Created concentration_tracking table")
            
            db.commit()
            self.log("Canonical magic tables created successfully")
            
        except Exception as e:
            self.log(f"Error creating canonical tables: {e}")
            db.rollback()
            raise
    
    def _create_canonical_spells_table(self, db: Session, is_postgres: bool):
        """Create the canonical spells table with proper MP-based structure"""
        self.log("Creating canonical spells table...")
        if is_postgres:
            db.execute(text("""
                CREATE TABLE spells (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) UNIQUE NOT NULL,
                    school VARCHAR(50) NOT NULL,
                    mp_cost INTEGER NOT NULL,
                    valid_domains TEXT[] NOT NULL,
                    casting_time VARCHAR(100) NOT NULL,
                    range_feet INTEGER NOT NULL,
                    components TEXT[] NOT NULL,
                    duration VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    base_damage INTEGER,
                    base_healing INTEGER,
                    mp_scaling INTEGER,
                    healing_scaling INTEGER,
                    damage_type VARCHAR(50),
                    save_type VARCHAR(50) DEFAULT 'none',
                    save_for_half BOOLEAN DEFAULT FALSE,
                    save_negates BOOLEAN DEFAULT FALSE,
                    concentration BOOLEAN DEFAULT FALSE,
                    duration_seconds INTEGER,
                    area_of_effect VARCHAR(100),
                    target VARCHAR(100),
                    auto_hit BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
        else:  # SQLite
            db.execute(text("""
                CREATE TABLE spells (
                    id TEXT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    school VARCHAR(50) NOT NULL,
                    mp_cost INTEGER NOT NULL,
                    valid_domains TEXT NOT NULL,
                    casting_time VARCHAR(100) NOT NULL,
                    range_feet INTEGER NOT NULL,
                    components TEXT NOT NULL,
                    duration VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    base_damage INTEGER,
                    base_healing INTEGER,
                    mp_scaling INTEGER,
                    healing_scaling INTEGER,
                    damage_type VARCHAR(50),
                    save_type VARCHAR(50) DEFAULT 'none',
                    save_for_half BOOLEAN DEFAULT 0,
                    save_negates BOOLEAN DEFAULT 0,
                    concentration BOOLEAN DEFAULT 0,
                    duration_seconds INTEGER,
                    area_of_effect VARCHAR(100),
                    target VARCHAR(100),
                    auto_hit BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
        self.log("Created canonical spells table")
    
    def migrate_spell_data(self, db: Session):
        """Load canonical spell data from configuration"""
        if self.dry_run:
            self.log("DRY RUN: Would migrate spell data to canonical format")
            return
        
        self.log("Loading canonical spell data...")
        
        # Check database type for array handling
        db_url = str(engine.url)
        is_postgres = 'postgresql' in db_url
        
        # Load canonical spell data
        spells_file = Path(__file__).parent.parent.parent / "data" / "systems" / "magic" / "spells.json"
        
        if spells_file.exists():
            with open(spells_file) as f:
                spells_data = json.load(f)
            
            for spell_name, spell_config in spells_data.get("spells", {}).items():
                # Check if spell already exists
                result = db.execute(text("SELECT id FROM spells WHERE name = :name"), {'name': spell_name})
                existing_spell = result.fetchone()
                
                if not existing_spell:
                    # Insert new canonical spell
                    spell_id = str(uuid.uuid4())
                    
                    # Handle PostgreSQL array format properly
                    if is_postgres:
                        valid_domains = spell_config.get("valid_domains", ["arcane"])
                        components = spell_config.get("components", ["verbal"])
                    else:
                        valid_domains = json.dumps(spell_config.get("valid_domains", ["arcane"]))
                        components = json.dumps(spell_config.get("components", ["verbal"]))
                    
                    db.execute(text("""
                        INSERT INTO spells (
                            id, name, school, mp_cost, valid_domains, casting_time, range_feet,
                            components, duration, description, base_damage, base_healing, mp_scaling,
                            damage_type, save_type, save_for_half, concentration, target, auto_hit
                        ) VALUES (
                            :id, :name, :school, :mp_cost, :valid_domains, :casting_time, :range_feet,
                            :components, :duration, :description, :base_damage, :base_healing, :mp_scaling,
                            :damage_type, :save_type, :save_for_half, :concentration, :target, :auto_hit
                        )
                    """), {
                        'id': spell_id,
                        'name': spell_name,
                        'school': spell_config.get("school", "unknown"),
                        'mp_cost': spell_config.get("mp_cost", 5),
                        'valid_domains': valid_domains,
                        'casting_time': spell_config.get("casting_time", "1 action"),
                        'range_feet': spell_config.get("range_feet", 30),
                        'components': components,
                        'duration': spell_config.get("duration", "instantaneous"),
                        'description': spell_config.get("description", f"Canonical {spell_name} spell"),
                        'base_damage': spell_config.get("base_damage"),
                        'base_healing': spell_config.get("base_healing"),
                        'mp_scaling': spell_config.get("mp_scaling", 1),
                        'damage_type': spell_config.get("damage_type"),
                        'save_type': spell_config.get("save_type", "none"),
                        'save_for_half': spell_config.get("save_for_half", False),
                        'concentration': spell_config.get("concentration", False),
                        'target': spell_config.get("target", "single_target"),
                        'auto_hit': spell_config.get("auto_hit", False)
                    })
                    
                    self.log(f"Added canonical spell: {spell_name}")
            
            db.commit()
            self.log("Spell data migration completed")
        else:
            self.log(f"Warning: Canonical spells file not found at {spells_file}")
    
    def create_sample_character_data(self, db: Session):
        """Create sample character MP and domain data for testing"""
        if self.dry_run:
            self.log("DRY RUN: Would create sample character data")
            return
        
        self.log("Creating sample character data for testing...")
        
        # Create sample character MP tracking
        sample_characters = [1, 2, 3]  # Assume these character IDs exist
        
        for char_id in sample_characters:
            # Check if MP tracking already exists
            result = db.execute(text("SELECT id FROM character_mp WHERE character_id = :char_id"), 
                              {'char_id': char_id})
            existing_mp = result.fetchone()
            
            if not existing_mp:
                mp_id = str(uuid.uuid4())
                db.execute(text("""
                    INSERT INTO character_mp (id, character_id, current_mp, max_mp, mp_regeneration_rate)
                    VALUES (:id, :character_id, :current_mp, :max_mp, :mp_regeneration_rate)
                """), {
                    'id': mp_id,
                    'character_id': char_id,
                    'current_mp': 50,
                    'max_mp': 100,
                    'mp_regeneration_rate': 2.0
                })
                self.log(f"Created MP tracking for character {char_id}")
            
            # Create domain access
            domains = ["arcane", "divine", "nature"]
            for i, domain in enumerate(domains):
                result = db.execute(text("""
                    SELECT id FROM character_domain_access 
                    WHERE character_id = :char_id AND domain = :domain
                """), {'char_id': char_id, 'domain': domain})
                existing_access = result.fetchone()
                
                if not existing_access:
                    access_id = str(uuid.uuid4())
                    db.execute(text("""
                        INSERT INTO character_domain_access (id, character_id, domain, access_level)
                        VALUES (:id, :character_id, :domain, :access_level)
                    """), {
                        'id': access_id,
                        'character_id': char_id,
                        'domain': domain,
                        'access_level': i + 1
                    })
                    self.log(f"Created {domain} domain access for character {char_id}")
        
        db.commit()
        self.log("Sample character data created")
    
    def run_migration(self):
        """Execute the full migration process"""
        self.log(f"Starting magic system migration to canonical MP system...")
        self.log(f"Database URL: {DATABASE_URL}")
        self.log(f"Dry run: {self.dry_run}")
        self.log(f"Backup directory: {self.backup_dir}")
        
        db = SessionLocal()
        try:
            # Step 1: Check current state
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            canonical_tables = ['spells', 'character_mp', 'character_domain_access', 'learned_spells', 'concentration_tracking']
            missing_canonical = [table for table in canonical_tables if table not in existing_tables]
            
            # Check if spells table has canonical structure
            spells_needs_migration = False
            if 'spells' in existing_tables:
                columns = inspector.get_columns('spells')
                column_names = [col['name'] for col in columns]
                if 'mp_cost' not in column_names:
                    spells_needs_migration = True
                    self.log("Spells table exists but has old D&D structure - needs conversion")
            
            if missing_canonical or spells_needs_migration:
                if missing_canonical:
                    self.log(f"Missing canonical tables: {missing_canonical}")
                if spells_needs_migration:
                    self.log("Spells table structure needs canonical conversion")
                    
                self.log("Proceeding with canonical table creation/migration...")
                
                # Check if we have old D&D tables to backup first
                if self.check_old_tables_exist(db):
                    # Step 2: Backup old system
                    self.backup_old_system(db)
                    
                    # Step 3: Drop old tables
                    self.drop_old_tables(db)
                
                # Step 4: Create missing canonical tables
                self.create_canonical_tables(db)
                
                # Step 5: Migrate spell data
                self.migrate_spell_data(db)
                
                # Step 6: Create sample data
                self.create_sample_character_data(db)
                
            elif not missing_canonical and not spells_needs_migration:
                self.log("All canonical tables already exist.")
                self.log("Checking if sample data needs to be added...")
                
                # Check if we have any character data
                result = db.execute(text("SELECT COUNT(*) FROM character_mp"))
                char_count = result.scalar()
                
                if char_count == 0:
                    self.log("No character data found. Adding sample data...")
                    self.create_sample_character_data(db)
                else:
                    self.log(f"Found {char_count} character MP records. Migration already complete.")
                    return True
            
            self.log("Migration completed successfully!")
            self.log("The magic system is now using the canonical MP-based system.")
            
            return True
            
        except Exception as e:
            self.log(f"Migration failed: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return False
            
        finally:
            db.close()

def main():
    """Main migration entry point"""
    parser = argparse.ArgumentParser(description="Migrate magic system to canonical MP-based system")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without executing")
    parser.add_argument("--backup-dir", default="./migration_backups", help="Backup directory")
    
    args = parser.parse_args()
    
    migration = MagicSystemMigration(dry_run=args.dry_run, backup_dir=args.backup_dir)
    success = migration.run_migration()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 