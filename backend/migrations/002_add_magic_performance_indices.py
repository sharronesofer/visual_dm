#!/usr/bin/env python3
"""
Performance Optimization Migration: Add Database Indices for Magic System

This migration adds strategic database indices to improve query performance
for common magic system operations:

- Spell lookups by domain, school, MP cost
- Character data lookups (MP, domains, learned spells)
- Concentration effect queries
- Frequently joined relationships

Usage:
    python 002_add_magic_performance_indices.py [--dry-run]
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.infrastructure.database.database import DATABASE_URL, engine, SessionLocal
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

class MagicPerformanceIndices:
    """Creates performance indices for magic system tables"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        
    def log(self, message: str):
        """Log migration progress"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def index_exists(self, db: Session, index_name: str) -> bool:
        """Check if an index already exists"""
        try:
            inspector = inspect(engine)
            
            # For PostgreSQL
            if 'postgresql' in str(engine.url):
                result = db.execute(text("""
                    SELECT indexname FROM pg_indexes 
                    WHERE indexname = :index_name
                """), {'index_name': index_name})
                return result.fetchone() is not None
            
            # For SQLite
            else:
                # SQLite doesn't have a simple way to check index existence
                # We'll just try to create and handle the error
                return False
                
        except Exception as e:
            self.log(f"Error checking index {index_name}: {e}")
            return False
    
    def create_index(self, db: Session, index_sql: str, index_name: str) -> bool:
        """Create an index if it doesn't exist"""
        if self.index_exists(db, index_name):
            self.log(f"Index {index_name} already exists, skipping")
            return True
        
        if self.dry_run:
            self.log(f"DRY RUN: Would create index {index_name}")
            self.log(f"SQL: {index_sql}")
            return True
        
        try:
            db.execute(text(index_sql))
            self.log(f"Created index: {index_name}")
            return True
        except Exception as e:
            self.log(f"Error creating index {index_name}: {e}")
            return False
    
    def create_spell_indices(self, db: Session):
        """Create indices for spell table lookups"""
        self.log("Creating spell table indices...")
        
        indices = [
            # Domain-based spell lookups (most common query)
            {
                'name': 'idx_spells_valid_domains',
                'sql': 'CREATE INDEX idx_spells_valid_domains ON spells USING GIN (valid_domains)'
                if 'postgresql' in str(engine.url) else
                'CREATE INDEX idx_spells_valid_domains ON spells (valid_domains)'
            },
            
            # School-based filtering
            {
                'name': 'idx_spells_school',
                'sql': 'CREATE INDEX idx_spells_school ON spells (school)'
            },
            
            # MP cost filtering for spell selection
            {
                'name': 'idx_spells_mp_cost',
                'sql': 'CREATE INDEX idx_spells_mp_cost ON spells (mp_cost)'
            },
            
            # School + MP cost composite index for common queries
            {
                'name': 'idx_spells_school_mp_cost',
                'sql': 'CREATE INDEX idx_spells_school_mp_cost ON spells (school, mp_cost)'
            },
            
            # Damage spell lookups
            {
                'name': 'idx_spells_damage_type',
                'sql': 'CREATE INDEX idx_spells_damage_type ON spells (damage_type)'
            },
            
            # Concentration spell filtering
            {
                'name': 'idx_spells_concentration',
                'sql': 'CREATE INDEX idx_spells_concentration ON spells (concentration)'
            },
            
            # Range-based spell queries
            {
                'name': 'idx_spells_range',
                'sql': 'CREATE INDEX idx_spells_range ON spells (range_feet)'
            },
            
            # Name lookup for spell resolution
            {
                'name': 'idx_spells_name_unique',
                'sql': 'CREATE UNIQUE INDEX idx_spells_name_unique ON spells (name)'
            }
        ]
        
        for index in indices:
            self.create_index(db, index['sql'], index['name'])
    
    def create_character_mp_indices(self, db: Session):
        """Create indices for character MP table"""
        self.log("Creating character MP indices...")
        
        indices = [
            # Primary character lookup
            {
                'name': 'idx_character_mp_character_id_unique',
                'sql': 'CREATE UNIQUE INDEX idx_character_mp_character_id_unique ON character_mp (character_id)'
            },
            
            # MP level queries for filtering characters
            {
                'name': 'idx_character_mp_current_mp',
                'sql': 'CREATE INDEX idx_character_mp_current_mp ON character_mp (current_mp)'
            },
            
            # Rest time tracking
            {
                'name': 'idx_character_mp_last_rest',
                'sql': 'CREATE INDEX idx_character_mp_last_rest ON character_mp (last_rest)'
            },
            
            # Composite for MP status queries
            {
                'name': 'idx_character_mp_current_max',
                'sql': 'CREATE INDEX idx_character_mp_current_max ON character_mp (current_mp, max_mp)'
            }
        ]
        
        for index in indices:
            self.create_index(db, index['sql'], index['name'])
    
    def create_domain_access_indices(self, db: Session):
        """Create indices for character domain access"""
        self.log("Creating domain access indices...")
        
        indices = [
            # Character domain lookups (most common)
            {
                'name': 'idx_domain_access_character_id',
                'sql': 'CREATE INDEX idx_domain_access_character_id ON character_domain_access (character_id)'
            },
            
            # Domain-based queries
            {
                'name': 'idx_domain_access_domain',
                'sql': 'CREATE INDEX idx_domain_access_domain ON character_domain_access (domain)'
            },
            
            # Access level filtering
            {
                'name': 'idx_domain_access_access_level',
                'sql': 'CREATE INDEX idx_domain_access_access_level ON character_domain_access (access_level)'
            },
            
            # Composite for character-domain queries
            {
                'name': 'idx_domain_access_char_domain_unique',
                'sql': 'CREATE UNIQUE INDEX idx_domain_access_char_domain_unique ON character_domain_access (character_id, domain)'
            },
            
            # Unlock time tracking
            {
                'name': 'idx_domain_access_unlocked_at',
                'sql': 'CREATE INDEX idx_domain_access_unlocked_at ON character_domain_access (unlocked_at)'
            }
        ]
        
        for index in indices:
            self.create_index(db, index['sql'], index['name'])
    
    def create_learned_spells_indices(self, db: Session):
        """Create indices for learned spells table"""
        self.log("Creating learned spells indices...")
        
        indices = [
            # Character spell lookups (primary query pattern)
            {
                'name': 'idx_learned_spells_character_id',
                'sql': 'CREATE INDEX idx_learned_spells_character_id ON learned_spells (character_id)'
            },
            
            # Spell-based lookups
            {
                'name': 'idx_learned_spells_spell_id',
                'sql': 'CREATE INDEX idx_learned_spells_spell_id ON learned_spells (spell_id)'
            },
            
            # Domain filtering for learned spells
            {
                'name': 'idx_learned_spells_domain',
                'sql': 'CREATE INDEX idx_learned_spells_domain ON learned_spells (domain_learned)'
            },
            
            # Unique constraint on character-spell pair
            {
                'name': 'idx_learned_spells_char_spell_unique',
                'sql': 'CREATE UNIQUE INDEX idx_learned_spells_char_spell_unique ON learned_spells (character_id, spell_id)'
            },
            
            # Mastery level queries
            {
                'name': 'idx_learned_spells_mastery',
                'sql': 'CREATE INDEX idx_learned_spells_mastery ON learned_spells (mastery_level)'
            },
            
            # Learn time tracking
            {
                'name': 'idx_learned_spells_learned_at',
                'sql': 'CREATE INDEX idx_learned_spells_learned_at ON learned_spells (learned_at)'
            },
            
            # Composite for character-domain spell queries
            {
                'name': 'idx_learned_spells_char_domain',
                'sql': 'CREATE INDEX idx_learned_spells_char_domain ON learned_spells (character_id, domain_learned)'
            }
        ]
        
        for index in indices:
            self.create_index(db, index['sql'], index['name'])
    
    def create_concentration_indices(self, db: Session):
        """Create indices for concentration tracking"""
        self.log("Creating concentration tracking indices...")
        
        indices = [
            # Caster-based lookups (most common)
            {
                'name': 'idx_concentration_caster_id',
                'sql': 'CREATE INDEX idx_concentration_caster_id ON concentration_tracking (caster_id)'
            },
            
            # Spell-based queries
            {
                'name': 'idx_concentration_spell_id',
                'sql': 'CREATE INDEX idx_concentration_spell_id ON concentration_tracking (spell_id)'
            },
            
            # Target-based lookups
            {
                'name': 'idx_concentration_target_id',
                'sql': 'CREATE INDEX idx_concentration_target_id ON concentration_tracking (target_id)'
            },
            
            # Active effect queries (expiration time)
            {
                'name': 'idx_concentration_expires_at',
                'sql': 'CREATE INDEX idx_concentration_expires_at ON concentration_tracking (expires_at)'
            },
            
            # Cast time tracking
            {
                'name': 'idx_concentration_cast_at',
                'sql': 'CREATE INDEX idx_concentration_cast_at ON concentration_tracking (cast_at)'
            },
            
            # Domain tracking for concentration effects
            {
                'name': 'idx_concentration_domain',
                'sql': 'CREATE INDEX idx_concentration_domain ON concentration_tracking (domain_used)'
            },
            
            # MP cost analysis
            {
                'name': 'idx_concentration_mp_spent',
                'sql': 'CREATE INDEX idx_concentration_mp_spent ON concentration_tracking (mp_spent)'
            },
            
            # Composite for active effect queries
            {
                'name': 'idx_concentration_caster_active',
                'sql': 'CREATE INDEX idx_concentration_caster_active ON concentration_tracking (caster_id, expires_at)'
            }
        ]
        
        for index in indices:
            self.create_index(db, index['sql'], index['name'])
    
    def create_foreign_key_indices(self, db: Session):
        """Create indices on foreign key columns for join performance"""
        self.log("Creating foreign key indices...")
        
        # These indices help with JOIN operations
        indices = [
            # Learned spells -> spells FK
            {
                'name': 'idx_learned_spells_spell_fk',
                'sql': 'CREATE INDEX idx_learned_spells_spell_fk ON learned_spells (spell_id)'
            },
            
            # Concentration -> spells FK
            {
                'name': 'idx_concentration_spell_fk',
                'sql': 'CREATE INDEX idx_concentration_spell_fk ON concentration_tracking (spell_id)'
            }
        ]
        
        for index in indices:
            self.create_index(db, index['sql'], index['name'])
    
    def create_partial_indices(self, db: Session):
        """Create partial indices for specific query patterns"""
        if 'postgresql' in str(engine.url):
            self.log("Creating PostgreSQL partial indices...")
            
            # PostgreSQL partial indices (advanced filtering)
            # Active concentration effects (not expired)
            self.create_index(db, """
                CREATE INDEX idx_concentration_active_only 
                ON concentration_tracking (caster_id, cast_at) 
                WHERE expires_at IS NULL OR expires_at > cast_at
            """, "idx_concentration_active_only")
            
            # High MP cost spells
            self.create_index(db, """
                CREATE INDEX idx_spells_high_cost 
                ON spells (mp_cost, school) 
                WHERE mp_cost >= 10
            """, "idx_spells_high_cost")
            
            # Concentration spells only
            self.create_index(db, """
                CREATE INDEX idx_spells_concentration_only 
                ON spells (school, mp_cost) 
                WHERE concentration = true
            """, "idx_spells_concentration_only")
            
            # Damage spells only
            self.create_index(db, """
                CREATE INDEX idx_spells_damage_only 
                ON spells (damage_type, mp_cost) 
                WHERE base_damage IS NOT NULL AND base_damage > 0
            """, "idx_spells_damage_only")
            
            # Note: Using static comparisons to avoid immutable function issues
        else:
            self.log("Partial indices not supported on SQLite, skipping")
    
    def analyze_tables(self, db: Session):
        """Update table statistics for query optimization"""
        if self.dry_run:
            self.log("DRY RUN: Would analyze table statistics")
            return
        
        self.log("Analyzing table statistics...")
        
        tables = [
            'spells', 'character_mp', 'character_domain_access',
            'learned_spells', 'concentration_tracking'
        ]
        
        for table in tables:
            try:
                if 'postgresql' in str(engine.url):
                    db.execute(text(f"ANALYZE {table}"))
                else:
                    db.execute(text(f"ANALYZE {table}"))
                self.log(f"Analyzed table: {table}")
            except Exception as e:
                self.log(f"Error analyzing table {table}: {e}")
    
    def run_migration(self):
        """Execute the performance optimization migration"""
        self.log("Starting magic system performance optimization migration...")
        self.log(f"Database URL: {DATABASE_URL}")
        self.log(f"Dry run: {self.dry_run}")
        
        db = SessionLocal()
        try:
            # Create all indices
            self.create_spell_indices(db)
            self.create_character_mp_indices(db)
            self.create_domain_access_indices(db)
            self.create_learned_spells_indices(db)
            self.create_concentration_indices(db)
            self.create_foreign_key_indices(db)
            self.create_partial_indices(db)
            
            # Commit all index creation
            if not self.dry_run:
                db.commit()
                self.log("All indices created successfully")
            
            # Update table statistics
            self.analyze_tables(db)
            
            if not self.dry_run:
                db.commit()
            
            self.log("Performance optimization migration completed successfully!")
            self.log("Magic system queries should now be significantly faster.")
            
            return True
            
        except Exception as e:
            self.log(f"Migration failed: {e}")
            import traceback
            traceback.print_exc()
            if not self.dry_run:
                db.rollback()
            return False
            
        finally:
            db.close()

def main():
    """Main migration entry point"""
    parser = argparse.ArgumentParser(description="Add performance indices to magic system")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without executing")
    
    args = parser.parse_args()
    
    migration = MagicPerformanceIndices(dry_run=args.dry_run)
    success = migration.run_migration()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 