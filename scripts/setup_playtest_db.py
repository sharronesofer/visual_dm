#!/usr/bin/env python3
"""
Playtest Database Setup Script

Creates all necessary tables for faction system playtesting.
Handles both PostgreSQL and SQLite for different playtesting scenarios.
"""

import os
import sys
from pathlib import Path

# Add project root and backend to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Create Base if not available
try:
    from backend.infrastructure.database import Base
except ImportError:
    # Fallback - create our own Base
    Base = declarative_base()

# Import faction models
from backend.infrastructure.models.faction.models import FactionEntity, AllianceEntity, BetrayalEntity

def setup_postgresql_playtest():
    """Setup PostgreSQL database for playtesting"""
    print("🐘 Setting up PostgreSQL for faction playtesting...")
    
    # PostgreSQL connection
    DATABASE_URL = "postgresql://playtest:playtest123@localhost:5432/dreamforge_playtest"
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connection successful!")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Faction tables created successfully!")
        
        # Create a sample faction for testing
        Session = sessionmaker(bind=engine)
        with Session() as session:
            sample_faction = FactionEntity(
                name="Test Faction Alpha",
                description="A test faction for playtesting",
                status="active",
                hidden_ambition=7,
                hidden_integrity=4,
                hidden_discipline=8,
                hidden_impulsivity=3,
                hidden_pragmatism=6,
                hidden_resilience=5
            )
            
            session.add(sample_faction)
            session.commit()
            print(f"✅ Sample faction created: {sample_faction.name} (ID: {sample_faction.id})")
        
        return DATABASE_URL
        
    except Exception as e:
        print(f"❌ PostgreSQL setup failed: {e}")
        print("💡 Consider using SQLite setup instead")
        return None

def setup_sqlite_playtest():
    """Setup SQLite database for playtesting"""
    print("💾 Setting up SQLite for faction playtesting...")
    
    # SQLite connection (file-based)
    db_path = Path(__file__).parent.parent / "playtest_faction.db"
    DATABASE_URL = f"sqlite:///{db_path}"
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Faction tables created successfully!")
        
        # Create sample factions for testing
        Session = sessionmaker(bind=engine)
        with Session() as session:
            sample_factions = [
                FactionEntity(
                    name="The Iron Consortium",
                    description="A militaristic faction focused on expansion",
                    status="active",
                    hidden_ambition=9,
                    hidden_integrity=4,
                    hidden_discipline=8,
                    hidden_impulsivity=6,
                    hidden_pragmatism=7,
                    hidden_resilience=8
                ),
                FactionEntity(
                    name="Peaceful Traders Guild",
                    description="A diplomatic faction focused on commerce",
                    status="active",
                    hidden_ambition=3,
                    hidden_integrity=9,
                    hidden_discipline=7,
                    hidden_impulsivity=2,
                    hidden_pragmatism=8,
                    hidden_resilience=6
                ),
                FactionEntity(
                    name="Shadow Covenant",
                    description="A secretive faction with hidden agendas",
                    status="active",
                    hidden_ambition=8,
                    hidden_integrity=2,
                    hidden_discipline=9,
                    hidden_impulsivity=4,
                    hidden_pragmatism=9,
                    hidden_resilience=7
                )
            ]
            
            for faction in sample_factions:
                session.add(faction)
            
            session.commit()
            print(f"✅ Created {len(sample_factions)} sample factions for playtesting")
        
        print(f"📁 Database file: {db_path}")
        return DATABASE_URL
        
    except Exception as e:
        print(f"❌ SQLite setup failed: {e}")
        return None

def verify_constraints():
    """Verify that the 1-10 constraints are working"""
    print("🔍 Verifying hidden attribute constraints...")
    
    db_path = Path(__file__).parent.parent / "playtest_faction.db"
    DATABASE_URL = f"sqlite:///{db_path}"
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Test valid values (should work)
            valid_faction = FactionEntity(
                name="Constraint Test Valid",
                description="Testing valid constraints",
                hidden_ambition=5,
                hidden_integrity=10,
                hidden_discipline=1,
                hidden_impulsivity=7,
                hidden_pragmatism=3,
                hidden_resilience=9
            )
            session.add(valid_faction)
            session.commit()
            print("✅ Valid constraints (1-10) work correctly")
            
            # Test invalid values (should be caught by application logic)
            try:
                invalid_faction = FactionEntity(
                    name="Constraint Test Invalid",
                    description="Testing invalid constraints",
                    hidden_ambition=15,  # Invalid - above 10
                    hidden_integrity=0,  # Invalid - below 1
                    hidden_discipline=5
                )
                session.add(invalid_faction)
                session.commit()
                print("⚠️  Database constraints not enforced (SQLite limitation)")
            except Exception as e:
                print("✅ Database constraints working correctly")
    
    except Exception as e:
        print(f"❌ Constraint verification failed: {e}")

def main():
    """Main setup function"""
    print("🎮 Dreamforge Faction System - Playtest Database Setup")
    print("=" * 60)
    
    choice = input("Choose database type:\n1. PostgreSQL (recommended)\n2. SQLite (simple)\n3. Verify constraints\n> ")
    
    if choice == "1":
        url = setup_postgresql_playtest()
        if url:
            print(f"\n🎯 Ready for playtesting!")
            print(f"Database URL: {url}")
            print("You can now run faction tests and API endpoints")
    elif choice == "2":
        url = setup_sqlite_playtest()
        if url:
            print(f"\n🎯 Ready for playtesting!")
            print(f"Database URL: {url}")
            print("You can now run faction tests and API endpoints")
    elif choice == "3":
        verify_constraints()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main() 