#!/usr/bin/env python3
"""
Database table creation script for Visual DM backend.

This script creates all necessary database tables by importing all models
and using the shared Base class.
"""

import os
import sys
import importlib.util
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_all_tables():
    """Create all database tables."""
    # Import the shared database module directly using importlib
    db_file_path = os.path.join(os.path.dirname(__file__), 'systems', 'shared', 'database.py')
    spec = importlib.util.spec_from_file_location("database_module", db_file_path)
    db_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(db_module)
    
    Base = db_module.Base
    engine = db_module.engine
    DATABASE_URL = db_module.DATABASE_URL
    
    print(f"Connecting to database: {DATABASE_URL}")
    print(f"Engine: {engine}")
    
    # Patch the import so character models use our Base
    import backend.systems.shared.database
    backend.systems.shared.database.Base = Base
    backend.systems.shared.database.engine = engine
    
    # Import all models to ensure they're registered with Base
    print("Importing character models...")
    from backend.systems.character_service.models import Character, CharacterProgression
    
    # Show which tables are registered
    print(f"Tables registered with Base: {list(Base.metadata.tables.keys())}")
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Test the connection
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Test querying the character table
        count = session.query(Character).count()
        print(f"✅ Character table verified - contains {count} characters")
        
        # Test querying the character progression table
        prog_count = session.query(CharacterProgression).count()
        print(f"✅ Character progression table verified - contains {prog_count} records")
        
    except Exception as e:
        print(f"❌ Error testing tables: {e}")
        return False
    finally:
        session.close()
    
    return True

if __name__ == "__main__":
    success = create_all_tables()
    if success:
        print("\n🎉 Database initialization completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1) 