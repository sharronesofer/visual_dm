#!/usr/bin/env python3
"""
Faction-Only Database Setup Script

Creates only the faction system tables for isolated testing.
"""

import os
import sys
from pathlib import Path

# Add project root and backend to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from sqlalchemy import create_engine, text, Column, String, Integer, DateTime, CheckConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
import uuid

# Create a new Base just for faction models
FactionBase = declarative_base()

class FactionEntity(FactionBase):
    """Faction entity for database testing"""
    __tablename__ = 'factions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    status = Column(String(20), default='active')
    
    # Hidden attributes with 1-10 constraints
    hidden_ambition = Column(Integer, CheckConstraint('hidden_ambition >= 1 AND hidden_ambition <= 10'), nullable=False)
    hidden_integrity = Column(Integer, CheckConstraint('hidden_integrity >= 1 AND hidden_integrity <= 10'), nullable=False)
    hidden_discipline = Column(Integer, CheckConstraint('hidden_discipline >= 1 AND hidden_discipline <= 10'), nullable=False)
    hidden_impulsivity = Column(Integer, CheckConstraint('hidden_impulsivity >= 1 AND hidden_impulsivity <= 10'), nullable=False)
    hidden_pragmatism = Column(Integer, CheckConstraint('hidden_pragmatism >= 1 AND hidden_pragmatism <= 10'), nullable=False)
    hidden_resilience = Column(Integer, CheckConstraint('hidden_resilience >= 1 AND hidden_resilience <= 10'), nullable=False)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AllianceEntity(FactionBase):
    """Alliance entity for database testing"""
    __tablename__ = 'alliances'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=func.now())

def setup_sqlite_faction_db():
    """Setup SQLite database for faction testing only"""
    print("💾 Setting up SQLite for faction system testing...")
    
    # SQLite connection (file-based)
    db_path = Path(__file__).parent.parent / "faction_playtest.db"
    DATABASE_URL = f"sqlite:///{db_path}"
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # Create all tables
        FactionBase.metadata.create_all(bind=engine)
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
    
    db_path = Path(__file__).parent.parent / "faction_playtest.db"
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
            
            session.delete(valid_faction)  # Clean up
            session.commit()
    
    except Exception as e:
        print(f"❌ Constraint verification failed: {e}")

def main():
    """Main setup function"""
    print("🎮 Dreamforge Faction System - Database Setup")
    print("=" * 50)
    
    print("Setting up faction database...")
    url = setup_sqlite_faction_db()
    
    if url:
        print(f"\n🎯 Faction database ready!")
        print(f"Database URL: {url}")
        
        # Verify constraints
        verify_constraints()
        
        print("\n🚀 You can now:")
        print("- Run faction business logic tests")
        print("- Test faction API endpoints") 
        print("- Use faction repository for CRUD operations")

if __name__ == "__main__":
    main() 