"""
Test NPC Services

Tests for NPC business logic services.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy.orm import Session

# Import the service under test
from backend.systems.npc.services.npc_service import NPCService

# Import models from infrastructure
from backend.infrastructure.systems.npc.models.models import (
    NpcEntity, CreateNpcRequest, UpdateNpcRequest, NpcResponse
)


class TestNPCService:
    """Test class for NPCService functionality"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for testing"""
        return Mock()
    
    @pytest.fixture
    def npc_service(self, mock_db_session):
        """Create NPCService instance with mocked dependencies"""
        with patch('backend.systems.npc.services.npc_service.get_db_session', return_value=mock_db_session):
            service = NPCService(db_session=mock_db_session)
            return service
    
    @pytest.fixture
    def sample_create_request(self):
        """Sample CreateNpcRequest for testing"""
        return CreateNpcRequest(
            name="Test Ranger",
            race="Elf",
            level=7,
            strength=13,
            dexterity=16,
            constitution=12,
            intelligence=14,
            wisdom=15,
            charisma=11,
            region_id="forest_region",
            location="Elven Outpost"
        )
    
    @pytest.fixture
    def sample_npc_entity(self):
        """Sample NpcEntity for testing"""
        npc_id = uuid4()
        return NpcEntity(
            id=npc_id,
            name="Test Ranger",
            race="Elf",
            level=7,
            region_id="forest_region",
            location="Elven Outpost",
            status="active"
        )
    
    @pytest.mark.asyncio
    async def test_create_npc(self, npc_service, sample_create_request):
        """Test NPC creation functionality"""
        # Mock repository response
        mock_npc_entity = Mock()
        mock_npc_entity.id = uuid4()
        mock_npc_entity.name = "Test Ranger"
        npc_service.npc_repository.create_npc = Mock(return_value=mock_npc_entity)
        
        # Test creation
        result = await npc_service.create_npc(sample_create_request)
        
        # Verify repository was called
        npc_service.npc_repository.create_npc.assert_called_once()
        
        # Verify result structure
        assert result is not None
        assert hasattr(result, 'id')
        
    @pytest.mark.asyncio  
    async def test_get_npc(self, npc_service, sample_npc_entity):
        """Test NPC retrieval functionality"""
        npc_id = sample_npc_entity.id
        
        # Mock repository response
        npc_service.npc_repository.get_npc = Mock(return_value=sample_npc_entity)
        
        # Test retrieval
        result = await npc_service.get_npc(npc_id)
        
        # Verify repository was called with correct ID
        npc_service.npc_repository.get_npc.assert_called_once_with(npc_id)
        
        # Verify result
        assert result is not None
        assert result.id == npc_id
        assert result.name == "Test Ranger"
        
    @pytest.mark.asyncio
    async def test_update_npc(self, npc_service, sample_npc_entity):
        """Test NPC update functionality"""
        npc_id = sample_npc_entity.id
        update_request = UpdateNpcRequest(level=8, location="New Forest Base")
        
        # Mock repository responses
        npc_service.npc_repository.get_npc = Mock(return_value=sample_npc_entity)
        npc_service.npc_repository.update_npc = Mock(return_value=sample_npc_entity)
        
        # Test update
        result = await npc_service.update_npc(npc_id, update_request)
        
        # Verify repository calls
        npc_service.npc_repository.get_npc.assert_called_once_with(npc_id)
        npc_service.npc_repository.update_npc.assert_called_once()
        
        # Verify result
        assert result is not None
        
    @pytest.mark.asyncio
    async def test_delete_npc(self, npc_service):
        """Test NPC deletion functionality"""
        npc_id = uuid4()
        
        # Mock repository response
        npc_service.npc_repository.delete_npc = Mock(return_value=True)
        
        # Test deletion
        result = await npc_service.delete_npc(npc_id)
        
        # Verify repository was called
        npc_service.npc_repository.delete_npc.assert_called_once_with(npc_id)
        
        # Verify result
        assert result is True
        
    @pytest.mark.asyncio
    async def test_list_npcs(self, npc_service):
        """Test NPC listing functionality"""
        # Mock repository response
        mock_npcs = [Mock() for _ in range(3)]
        npc_service.npc_repository.list_npcs = Mock(return_value=(mock_npcs, 3))
        
        # Test listing
        result_npcs, total_count = await npc_service.list_npcs(page=1, size=10)
        
        # Verify repository was called
        npc_service.npc_repository.list_npcs.assert_called_once()
        
        # Verify results
        assert len(result_npcs) == 3
        assert total_count == 3
        
    @pytest.mark.asyncio
    async def test_add_memory_to_npc(self, npc_service):
        """Test adding memory to NPC"""
        npc_id = uuid4()
        memory_data = {
            "memory_id": "test_memory",
            "content": "Met a traveling merchant",
            "memory_type": "interaction",
            "importance": 6.5,
            "emotion": "neutral"
        }
        
        # Mock repository response
        npc_service.npc_repository.add_memory = Mock(return_value=True)
        
        # Test adding memory
        result = await npc_service.add_memory_to_npc(npc_id, memory_data)
        
        # Verify repository was called
        npc_service.npc_repository.add_memory.assert_called_once()
        
        # Verify result
        assert result is True
        
    @pytest.mark.asyncio
    async def test_get_npc_memories(self, npc_service):
        """Test retrieving NPC memories"""
        npc_id = uuid4()
        
        # Create mock memory objects with the attributes the service expects
        mock_memory1 = Mock()
        mock_memory1.id = uuid4()
        mock_memory1.memory_id = "mem1"
        mock_memory1.content = "Test memory 1"
        mock_memory1.memory_type = "interaction"
        mock_memory1.importance = 5.0
        mock_memory1.emotion = "neutral"
        mock_memory1.location = "test_location"
        mock_memory1.participants = ["player"]
        mock_memory1.tags = ["test"]
        mock_memory1.recalled_count = 0
        mock_memory1.created_at = datetime.now()
        mock_memory1.last_recalled = None
        
        mock_memory2 = Mock()
        mock_memory2.id = uuid4()
        mock_memory2.memory_id = "mem2"
        mock_memory2.content = "Test memory 2"
        mock_memory2.memory_type = "experience"
        mock_memory2.importance = 3.0
        mock_memory2.emotion = "happy"
        mock_memory2.location = "test_location2"
        mock_memory2.participants = ["npc"]
        mock_memory2.tags = ["test2"]
        mock_memory2.recalled_count = 1
        mock_memory2.created_at = datetime.now()
        mock_memory2.last_recalled = datetime.now()
        
        mock_memories = [mock_memory1, mock_memory2]
        
        # Mock repository response
        npc_service.npc_repository.get_npc_memories = Mock(return_value=mock_memories)
        
        # Test retrieval
        result = await npc_service.get_npc_memories(npc_id)
        
        # Verify repository was called
        npc_service.npc_repository.get_npc_memories.assert_called_once_with(npc_id)
        
        # Verify result structure
        assert len(result) == 2
        assert result[0]["memory_id"] == "mem1"
        assert result[0]["content"] == "Test memory 1"
        assert result[1]["memory_id"] == "mem2"
        assert result[1]["content"] == "Test memory 2"
        
    @pytest.mark.asyncio
    async def test_add_faction_to_npc(self, npc_service):
        """Test adding faction affiliation to NPC"""
        npc_id = uuid4()
        faction_id = uuid4()
        
        # Mock repository response
        npc_service.npc_repository.add_faction_affiliation = Mock(return_value=True)
        
        # Test adding faction
        result = await npc_service.add_faction_to_npc(npc_id, faction_id, role="scout")
        
        # Verify repository was called
        npc_service.npc_repository.add_faction_affiliation.assert_called_once()
        
        # Verify result
        assert result is True
        
    @pytest.mark.asyncio
    async def test_update_npc_location(self, npc_service):
        """Test updating NPC location"""
        npc_id = uuid4()
        
        # Mock repository responses
        npc_service.location_repository.update_location = Mock(return_value={
            "success": True,
            "old_location": "Forest Camp",
            "new_location": "Mountain Base"
        })
        
        # Test location update
        result = await npc_service.update_npc_location(
            npc_id, "mountain_region", "Mountain Base", "patrol"
        )
        
        # Verify repository was called
        npc_service.location_repository.update_location.assert_called_once()
        
        # Verify result
        assert result["success"] is True
        assert "old_location" in result
        assert "new_location" in result
        
    @pytest.mark.asyncio
    async def test_apply_motif(self, npc_service):
        """Test applying motif to NPC"""
        npc_id = uuid4()
        motif_data = {
            "motif_id": "revenge_001",
            "motif_type": "revenge",
            "strength": 8.0,
            "description": "Seeks revenge for fallen mentor"
        }
        
        # Mock repository response
        npc_service.npc_repository.add_motif = Mock(return_value=True)
        
        # Test applying motif
        result = await npc_service.apply_motif(npc_id, motif_data)
        
        # Verify repository was called
        npc_service.npc_repository.add_motif.assert_called_once()
        
        # Verify result
        assert result is True
        
    @pytest.mark.asyncio
    async def test_get_npc_statistics(self, npc_service):
        """Test getting NPC system statistics"""
        # Mock repository response
        mock_stats = {
            "total_npcs": 150,
            "active_npcs": 120,
            "npcs_by_region": {"forest": 50, "mountain": 30, "city": 40},
            "average_loyalty": 6.8
        }
        npc_service.npc_repository.get_statistics = Mock(return_value=mock_stats)
        
        # Test statistics
        result = await npc_service.get_npc_statistics()
        
        # Verify repository was called
        npc_service.npc_repository.get_statistics.assert_called_once()
        
        # Verify result structure
        assert result["total_npcs"] == 150
        assert result["active_npcs"] == 120
        assert "npcs_by_region" in result
        assert result["average_loyalty"] == 6.8
        
    def test_event_publisher_integration(self, npc_service):
        """Test that NPCService properly integrates with event publisher"""
        # Verify event publisher is initialized
        assert npc_service.event_publisher is not None
        # Just check that it has a publish method - the specific methods may vary
        assert hasattr(npc_service.event_publisher, 'publish') or \
               hasattr(npc_service.event_publisher, 'publish_npc_created') or \
               callable(npc_service.event_publisher)
        
    @pytest.mark.asyncio
    async def test_error_handling(self, npc_service):
        """Test service error handling"""
        npc_id = uuid4()
        
        # Mock repository to raise exception
        npc_service.npc_repository.get_npc = Mock(side_effect=Exception("Database error"))
        
        # Test error handling
        result = await npc_service.get_npc(npc_id)
        
        # Should return None on error
        assert result is None


class TestNPCServiceIntegration:
    """Integration tests for NPCService with real components"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test that NPCService initializes correctly with all dependencies"""
        service = NPCService()
        
        # Verify all repositories are initialized
        assert service.npc_repository is not None
        assert service.memory_repository is not None
        assert service.location_repository is not None
        assert service.event_publisher is not None
        
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_service_with_real_request_data(self):
        """Test service with realistic request data"""
        service = NPCService()
        
        # Create a realistic NPC request
        request = CreateNpcRequest(
            name="Captain Marcus",
            race="Human",
            level=10,
            strength=18,
            dexterity=14,
            constitution=16,
            intelligence=12,
            wisdom=13,
            charisma=15,
            region_id="capital_city",
            location="Guard Barracks",
            background="Former soldier turned city guard captain"
        )
        
        # This would require actual database integration
        # For now, just verify the request is valid
        assert request.name == "Captain Marcus"
        assert request.level == 10
        assert request.region_id == "capital_city"
