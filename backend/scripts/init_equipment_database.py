#!/usr/bin/env python3
"""
Equipment Database Initialization Script

Initializes the equipment database with all required tables, indexes, and default data.
Used for development setup and testing.
"""

import sys
import logging
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from infrastructure.database.database_setup import (
    initialize_equipment_database,
    test_equipment_database,
    database_setup
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize the equipment database."""
    print("🔧 Equipment Database Initialization")
    print("=" * 50)
    
    try:
        # Test if database is already initialized
        print("📋 Testing existing database connection...")
        if test_equipment_database():
            print("✅ Database already initialized and working!")
            
            # Ask if user wants to recreate
            recreate = input("\n🔄 Recreate database tables? (y/N): ").lower().strip()
            if recreate in ['y', 'yes']:
                print("\n🚧 Recreating database tables...")
                success = initialize_equipment_database(force_recreate=True)
            else:
                print("📊 Database left unchanged.")
                return True
        else:
            print("🆕 Initializing new database...")
            success = initialize_equipment_database()
        
        if success:
            print("\n✅ Database initialization completed successfully!")
            
            # Test the database
            print("\n🧪 Testing database functionality...")
            if test_equipment_database():
                print("✅ Database test passed!")
                
                # Show database info
                print(f"\n📍 Database URL: {database_setup._get_safe_url()}")
                print(f"📊 Database Type: {'SQLite' if 'sqlite' in database_setup.database_url else 'Other'}")
                
                return True
            else:
                print("❌ Database test failed!")
                return False
        else:
            print("❌ Database initialization failed!")
            return False
            
    except Exception as e:
        print(f"💥 Error during database initialization: {e}")
        logger.exception("Database initialization error")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 