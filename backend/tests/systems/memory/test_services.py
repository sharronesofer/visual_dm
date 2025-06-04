"""
Test module for memory services.

Tests the canonical memory services that provide the business logic layer
for memory operations, as agreed upon between the Development Bible and code.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import canonical memory services
try:
    from backend.systems.memory import MemoryManager, Memory, MemoryBehaviorInfluenceService, MemoryCrossSystemIntegrator
    from backend.systems.memory.memory_categories import MemoryCategory
except ImportError:
    pytest.skip(f"Memory services system not found", allow_module_level=True)


class TestMemoryServices:
    """Test class for memory services functionality"""
    
    def test_memory_manager_service(self):
        """Test MemoryManager as core service"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        # Verify it follows service pattern
        assert hasattr(manager, 'create_memory')
        assert hasattr(manager, 'add_memory')
        assert hasattr(manager, 'recall_memory')
        assert hasattr(manager, 'get_memory')
        assert hasattr(manager, 'get_memories_by_category')
        
        # Verify entity context is maintained
        assert manager.entity_id == "test_npc"
        assert manager.entity_type == "npc"
    
    def test_memory_behavior_influence_service(self):
        """Test MemoryBehaviorInfluenceService integration"""
        mock_manager = Mock(spec=MemoryManager)
        mock_manager.entity_id = "test_npc"
        mock_manager.entity_type = "npc"
        
        service = MemoryBehaviorInfluenceService(mock_manager)
        
        # Verify behavior influence methods exist
        assert hasattr(service, 'calculate_trust_level')
        assert hasattr(service, 'assess_risk')
        assert hasattr(service, 'identify_emotional_triggers')
        assert hasattr(service, 'calculate_faction_bias')
        
        # Verify service maintains memory manager reference
        assert service.memory_manager == mock_manager
    
    def test_memory_cross_system_integrator(self):
        """Test MemoryCrossSystemIntegrator service"""
        mock_manager = Mock(spec=MemoryManager)
        integrator = MemoryCrossSystemIntegrator(mock_manager)
        
        # Verify cross-system integration methods exist
        assert hasattr(integrator, 'sync_with_dialogue_system')
        assert hasattr(integrator, 'sync_with_faction_system')
        assert hasattr(integrator, 'sync_with_alliance_system')
        assert hasattr(integrator, 'handle_event')
        
        # Verify integrator maintains memory manager reference
        assert integrator.memory_manager == mock_manager
    
    @pytest.mark.asyncio
    async def test_service_coordination(self):
        """Test that services work together cohesively"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        behavior_service = MemoryBehaviorInfluenceService(manager)
        integrator = MemoryCrossSystemIntegrator(manager)
        
        # Create a memory through the manager
        memory = await manager.create_memory(
            content="Player helped me in battle",
            importance=0.8
        )
        
        # Verify the memory exists in manager
        assert memory.memory_id in manager.memories
        
        # Verify services can reference the memory
        assert manager.entity_id == "test_npc"
        
        # Services should be able to operate on the same memory manager
        assert behavior_service.memory_manager == manager
        assert integrator.memory_manager == manager
    
    @pytest.mark.asyncio
    async def test_behavior_influence_with_memories(self):
        """Test behavior influence service with actual memories"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        behavior_service = MemoryBehaviorInfluenceService(manager)
        
        # Add some test memories
        positive_memory = await manager.create_memory(
            content="Player helped defend village",
            category=MemoryCategory.ACHIEVEMENT,
            importance=0.8
        )
        
        negative_memory = await manager.create_memory(
            content="Player betrayed our agreement", 
            category=MemoryCategory.TRAUMA,
            importance=0.9
        )
        
        # Mock the memory retrieval for behavior analysis
        with patch.object(manager, 'get_memories_involving_entity', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [positive_memory, negative_memory]
            
            # Test trust calculation
            trust_result = await behavior_service.calculate_trust_level("player_123")
            
            assert hasattr(trust_result, 'entity_id')
            assert hasattr(trust_result, 'trust_level')
            assert hasattr(trust_result, 'confidence')
    
    @pytest.mark.asyncio
    async def test_cross_system_event_handling(self):
        """Test cross-system integration event handling"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        integrator = MemoryCrossSystemIntegrator(manager)
        
        # Test dialogue system event
        dialogue_event = {
            "type": "dialogue_completed",
            "participant_id": "player_123",
            "content": "Discussed quest details",
            "sentiment": "positive"
        }
        
        # Should handle event without errors
        result = await integrator.handle_event(dialogue_event)
        
        # Basic validation - should return some result
        assert result is not None
    
    def test_service_initialization_patterns(self):
        """Test that services follow consistent initialization patterns"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        # All services should accept a memory manager
        behavior_service = MemoryBehaviorInfluenceService(manager)
        integrator = MemoryCrossSystemIntegrator(manager)
        
        # All services should maintain reference to memory manager
        assert behavior_service.memory_manager == manager
        assert integrator.memory_manager == manager
        
        # Services should have consistent interface patterns
        assert hasattr(behavior_service, 'memory_manager')
        assert hasattr(integrator, 'memory_manager')
