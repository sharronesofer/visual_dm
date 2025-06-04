"""
Test NPC Models

Tests for NPC database models and Pydantic schemas.
"""

import pytest
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session

# Test database setup
from backend.tests.conftest import test_db_session

# Import models from infrastructure
from backend.infrastructure.systems.npc.models.models import (
    NpcEntity, NpcMemory, NpcFactionAffiliation, NpcRumor,
    NpcLocationHistory, NpcMotif, CreateNpcRequest, 
    UpdateNpcRequest, NpcResponse
)

class TestNPCModels:
    """Test class for NPC SQLAlchemy models"""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session"""
        from backend.infrastructure.database import get_db
        session = next(get_db())
        yield session
        session.close()
    
    @pytest.fixture
    def sample_npc_data(self):
        """Sample NPC data for testing"""
        return {
            "name": "Test Warrior",
            "race": "Human",
            "level": 5,
            "strength": 15,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 13,
            "charisma": 11,
            "region_id": "test_region",
            "location": "Village Center",
            "status": "active",
            "loyalty_score": 7,
            "goodwill": 3
        }
    
    def test_npc_entity_creation(self, db_session, sample_npc_data):
        """Test NPC entity creation and basic fields"""
        npc = NpcEntity(**sample_npc_data)
        
        # Test basic attributes
        assert npc.name == "Test Warrior"
        assert npc.race == "Human" 
        assert npc.level == 5
        assert npc.strength == 15
        assert npc.loyalty_score == 7
        assert isinstance(npc.id, UUID)
        assert isinstance(npc.created_at, datetime)
        
    def test_npc_entity_relationships(self, db_session, sample_npc_data):
        """Test NPC entity relationships with other models"""
        npc = NpcEntity(**sample_npc_data)
        
        # Test memories relationship
        memory = NpcMemory(
            npc_id=npc.id,
            memory_id="test_memory",
            content="Test memory content", 
            memory_type="conversation",
            importance=7.5
        )
        npc.memories.append(memory)
        
        assert len(npc.memories) == 1
        assert npc.memories[0].content == "Test memory content"
        assert npc.memories[0].npc_id == npc.id
        
    def test_npc_memory_model(self):
        """Test NPC memory model creation and validation"""
        npc_id = uuid4()
        memory = NpcMemory(
            npc_id=npc_id,
            memory_id="mem_001",
            content="Had a conversation with the merchant",
            memory_type="interaction", 
            importance=6.0,
            emotion="friendly",
            location="Market Square",
            participants=["merchant_bob", "player"]
        )
        
        assert memory.npc_id == npc_id
        assert memory.memory_id == "mem_001"
        assert memory.importance == 6.0
        assert memory.emotion == "friendly"
        assert "merchant_bob" in memory.participants
        assert memory.recalled_count == 0
        
    def test_npc_faction_affiliation_model(self):
        """Test NPC faction affiliation model"""
        npc_id = uuid4()
        faction_id = uuid4()
        
        affiliation = NpcFactionAffiliation(
            npc_id=npc_id,
            faction_id=faction_id,
            role="member",
            loyalty=8.5,
            status="active"
        )
        
        assert affiliation.npc_id == npc_id
        assert affiliation.faction_id == faction_id
        assert affiliation.role == "member"
        assert affiliation.loyalty == 8.5
        assert affiliation.status == "active"
        
    def test_npc_rumor_model(self):
        """Test NPC rumor model"""
        npc_id = uuid4()
        
        rumor = NpcRumor(
            npc_id=npc_id,
            rumor_id="rumor_001",
            content="Strange lights seen in the forest",
            source="traveling_merchant",
            credibility=6.5,
            spread_chance=0.3
        )
        
        assert rumor.npc_id == npc_id
        assert rumor.rumor_id == "rumor_001"
        assert rumor.credibility == 6.5
        assert rumor.spread_chance == 0.3
        assert rumor.times_shared == 0
        
    def test_npc_location_history_model(self):
        """Test NPC location history model"""
        npc_id = uuid4()
        
        location_history = NpcLocationHistory(
            npc_id=npc_id,
            region_id="region_001",
            location="Old Town",
            travel_motive="trade",
            activity="shopping"
        )
        
        assert location_history.npc_id == npc_id
        assert location_history.region_id == "region_001" 
        assert location_history.location == "Old Town"
        assert location_history.travel_motive == "trade"
        assert isinstance(location_history.arrival_time, datetime)
        
    def test_npc_motif_model(self):
        """Test NPC motif model"""
        npc_id = uuid4()
        
        motif = NpcMotif(
            npc_id=npc_id,
            motif_id="motif_001",
            motif_type="revenge",
            strength=7.5,
            description="Seeking revenge for fallen comrades",
            status="active",
            entropy=0.1
        )
        
        assert motif.npc_id == npc_id
        assert motif.motif_type == "revenge"
        assert motif.strength == 7.5
        assert motif.status == "active"
        assert motif.entropy == 0.1


class TestNPCPydanticSchemas:
    """Test class for NPC Pydantic schemas"""
    
    def test_create_npc_request_schema(self):
        """Test CreateNpcRequest Pydantic schema"""
        request_data = {
            "name": "Test Wizard",
            "race": "Elf",
            "level": 8,
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 18,
            "wisdom": 15,
            "charisma": 13,
            "region_id": "magic_district",
            "location": "Wizard Tower"
        }
        
        request = CreateNpcRequest(**request_data)
        
        assert request.name == "Test Wizard"
        assert request.race == "Elf"
        assert request.intelligence == 18
        assert request.region_id == "magic_district"
        
    def test_update_npc_request_schema(self):
        """Test UpdateNpcRequest Pydantic schema"""
        update_data = {
            "level": 9,
            "location": "New Magic Tower",
            "loyalty": 8
        }
        
        request = UpdateNpcRequest(**update_data)
        
        assert request.level == 9
        assert request.location == "New Magic Tower"
        assert request.loyalty == 8
        # Fields not provided should be None
        assert request.name is None
        
    def test_npc_response_schema(self):
        """Test NpcResponse Pydantic schema"""
        npc_id = uuid4()
        response_data = {
            "id": npc_id,
            "name": "Test Paladin",
            "race": "Human",
            "class_name": "Paladin",
            "level": 6,
            "strength": 16,
            "dexterity": 10,
            "constitution": 15,
            "intelligence": 12,
            "wisdom": 14,
            "charisma": 17,
            "region_id": "holy_district",
            "location": "Temple",
            "status": "active",
            "loyalty": 9,
            "goodwill": 5,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        response = NpcResponse(**response_data)
        
        assert response.id == npc_id
        assert response.name == "Test Paladin"
        assert response.charisma == 17
        assert response.status == "active"
        assert isinstance(response.created_at, datetime)
        
    def test_schema_validation_errors(self):
        """Test that schemas properly validate input data"""
        # Test missing required fields
        with pytest.raises(ValueError):
            CreateNpcRequest(name="Test")  # Missing required fields
            
        # Test invalid data types
        with pytest.raises(ValueError):
            CreateNpcRequest(
                name="Test",
                race="Human", 
                class_name="Fighter",
                level="invalid_level"  # Should be int
            )
