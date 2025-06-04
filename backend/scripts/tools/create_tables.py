#!/usr/bin/env python3
"""
Database table creation script for Visual DM backend.

This script creates all necessary database tables by importing all models
and using the shared Base class.
"""

import os
import sys
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_all_tables():
    """Create all database tables."""
    # Import the database components from the new infrastructure location
    from backend.infrastructure.shared.database import get_database_manager, sync_database
    from backend.infrastructure.shared.database.base import Base
    from backend.infrastructure.shared.database.session import get_db
    
    print("Initializing database manager...")
    
    # Initialize and sync database
    try:
        sync_database()
        print("Database synchronization completed")
    except Exception as e:
        print(f"Database sync failed: {e}")
        return False
    
    # Import all models to ensure they're registered with Base
    print("Importing character models...")
    try:
        from backend.systems.character.models import Character
        # from backend.systems.character.models.character_progression import CharacterProgression
        print("Character models imported successfully")
    except Exception as e:
        print(f"Warning: Could not import all character models: {e}")
    
    # Show which tables are registered
    if hasattr(Base, 'metadata') and Base.metadata.tables:
        print(f"Tables registered with Base: {list(Base.metadata.tables.keys())}")
    else:
        print("No tables found registered with Base")
    
    # Test the database connection
    print("Testing database connection...")
    try:
        # Get a database session to test
        db_session = next(get_db())
        
        # Test querying the character table if it exists
        try:
            count = db_session.query(Character).count()
            print(f"✅ Character table verified - contains {count} characters")
        except Exception as e:
            print(f"Warning: Could not query character table: {e}")
        
        db_session.close()
        
    except Exception as e:
        print(f"❌ Error testing database connection: {e}")
        return False
    
    print("✅ Database validation completed successfully!")
    return True

if __name__ == "__main__":
    success = create_all_tables()
    if success:
        print("\n🎉 Database initialization completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1) 