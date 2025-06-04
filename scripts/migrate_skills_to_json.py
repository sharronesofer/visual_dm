#!/usr/bin/env python3
"""
Skill Migration Script
---------------------
Migrates character skills from the old database table model to the new JSON-based approach.
This script should be run once to transition existing data.

Usage:
    python scripts/migrate_skills_to_json.py
"""

import os
import sys
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.infrastructure.database import get_db_session
from backend.systems.character.models.character import Character
from backend.infrastructure.config_loaders.character_config_loader import config_loader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_character_skills():
    """
    Migrate character skills from the old many-to-many relationship 
    to the new JSON-based approach.
    """
    try:
        # Get database session
        db_session = next(get_db_session())
        
        logger.info("Starting character skills migration...")
        
        # Check if old skill tables exist
        result = db_session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('skills', 'character_skills') 
            AND table_schema = DATABASE()
        """))
        
        existing_tables = [row[0] for row in result.fetchall()]
        
        if 'skills' not in existing_tables or 'character_skills' not in existing_tables:
            logger.info("Old skill tables not found. Migration not needed.")
            return
        
        # Get all characters with their current skills
        characters_with_skills = db_session.execute(text("""
            SELECT 
                c.id, 
                c.name, 
                c.uuid,
                GROUP_CONCAT(s.name) as skill_names
            FROM characters c
            LEFT JOIN character_skills cs ON c.id = cs.character_id
            LEFT JOIN skills s ON cs.skill_id = s.id
            GROUP BY c.id, c.name, c.uuid
        """))
        
        migrated_count = 0
        
        for row in characters_with_skills.fetchall():
            character_id, character_name, character_uuid, skill_names_str = row
            
            # Skip characters with no skills
            if not skill_names_str:
                continue
                
            skill_names = skill_names_str.split(',')
            
            # Build new skills JSON structure
            skills_json = {}
            
            for skill_name in skill_names:
                skill_name = skill_name.strip()
                
                # Validate skill exists in new configuration
                skill_info = config_loader.get_skill_info(skill_name)
                if skill_info:
                    canonical_name = skill_info["name"]
                    skills_json[canonical_name] = {
                        "proficient": True,
                        "expertise": False,
                        "bonus": 0
                    }
                else:
                    # Keep unknown skills as-is for manual review
                    skills_json[skill_name] = {
                        "proficient": True,
                        "expertise": False,
                        "bonus": 0
                    }
                    logger.warning(f"Unknown skill '{skill_name}' found for character {character_name}")
            
            # Update character with new skills JSON
            db_session.execute(text("""
                UPDATE characters 
                SET skills = :skills_json 
                WHERE id = :character_id
            """), {
                'skills_json': str(skills_json).replace("'", '"'),  # Convert to JSON string
                'character_id': character_id
            })
            
            migrated_count += 1
            logger.info(f"Migrated skills for character '{character_name}' ({len(skills_json)} skills)")
        
        # Commit the changes
        db_session.commit()
        logger.info(f"Successfully migrated {migrated_count} characters")
        
        # Optional: Back up old tables before dropping
        backup_old_tables(db_session)
        
        db_session.close()
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if 'db_session' in locals():
            db_session.rollback()
            db_session.close()
        raise

def backup_old_tables(db_session):
    """
    Create backup copies of the old skill tables before dropping them.
    """
    try:
        logger.info("Creating backup tables...")
        
        # Create backup of skills table
        db_session.execute(text("""
            CREATE TABLE skills_backup AS SELECT * FROM skills
        """))
        
        # Create backup of character_skills junction table
        db_session.execute(text("""
            CREATE TABLE character_skills_backup AS SELECT * FROM character_skills
        """))
        
        db_session.commit()
        logger.info("Backup tables created: skills_backup, character_skills_backup")
        
        # Optional: Drop old tables (commented out for safety)
        # db_session.execute(text("DROP TABLE character_skills"))
        # db_session.execute(text("DROP TABLE skills"))
        # logger.info("Old skill tables dropped")
        
    except Exception as e:
        logger.warning(f"Failed to create backup tables: {e}")

def verify_migration():
    """
    Verify that the migration was successful by checking some characters.
    """
    try:
        db_session = next(get_db_session())
        
        # Check a few characters to ensure their skills were migrated
        result = db_session.execute(text("""
            SELECT name, skills 
            FROM characters 
            WHERE skills IS NOT NULL AND skills != '{}' 
            LIMIT 5
        """))
        
        logger.info("Verification - Characters with migrated skills:")
        for row in result.fetchall():
            character_name, skills_json = row
            logger.info(f"  {character_name}: {skills_json}")
        
        db_session.close()
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")

if __name__ == "__main__":
    try:
        migrate_character_skills()
        verify_migration()
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("1. Test the application to ensure skills work correctly")
        print("2. If everything looks good, you can safely drop the old tables:")
        print("   - DROP TABLE character_skills;")
        print("   - DROP TABLE skills;")
        print("3. Remove the backup tables when you're confident:")
        print("   - DROP TABLE character_skills_backup;")
        print("   - DROP TABLE skills_backup;")
        print("\nOld character_skills relationships have been converted to JSON format.")
        print("Characters now store skill proficiencies directly in their 'skills' JSON field.")
        
    except Exception as e:
        print(f"\nMIGRATION FAILED: {e}")
        print("\nThe database has been rolled back to its previous state.")
        print("Please review the error and try again.")
        sys.exit(1) 