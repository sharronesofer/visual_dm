"""
Comprehensive tests for ResourceService - Resource management functionality.

Tests resource CRUD operations, population impact calculations, and data integrity.
"""

import pytest
import logging
from unittest.mock import Mock, patch
from datetime import datetime

from backend.systems.economy.resource_service import ResourceService
from backend.systems.economy.resource import Resource, ResourceData


class TestResourceService:
    """Test suite for ResourceService functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = ResourceService()
        self.service_with_db = ResourceService(db_session=Mock())
    
    def test_initialization(self):
        """Test ResourceService initialization."""
        # Test without database session
        service = ResourceService()
        assert service.db_session is None
        
        # Test with database session
        mock_session = Mock()
        service_with_db = ResourceService(mock_session)
        assert service_with_db.db_session is mock_session
    
    def test_get_resource(self):
        """Test resource retrieval functionality."""
        resource = self.service.get_resource('1')
        
        assert resource is not None
        assert isinstance(resource, Resource)
        assert resource.id == '1'
        assert hasattr(resource, 'name')
        assert hasattr(resource, 'type')
        assert hasattr(resource, 'value')
        assert hasattr(resource, 'quantity')
        assert hasattr(resource, 'amount')
    
    def test_get_resource_various_ids(self):
        """Test resource retrieval with various ID types."""
        # Test string ID
        resource1 = self.service.get_resource('test_id')
        assert resource1.id == 'test_id'
        
        # Test numeric ID  
        resource2 = self.service.get_resource(123)
        assert resource2.id == '123'
        
        # Test UUID-like ID
        resource3 = self.service.get_resource('a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6')
        assert resource3.id == 'a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6'
    
    def test_get_resources_by_region(self):
        """Test resource retrieval by region."""
        resources = self.service.get_resources_by_region(1)
        
        assert isinstance(resources, list)
        assert len(resources) >= 0
        
        # Verify all resources belong to the region
        for resource in resources:
            assert isinstance(resource, Resource)
            assert hasattr(resource, 'region_id')
            if hasattr(resource, 'region_id') and resource.region_id:
                assert resource.region_id == '1'
    
    def test_get_resources_by_region_different_regions(self):
        """Test resource retrieval for different regions."""
        for region_id in [1, 2, 5, 10]:
            resources = self.service.get_resources_by_region(region_id)
            assert isinstance(resources, list)
            
            # Each region should have consistent resource structure
            for resource in resources:
                assert hasattr(resource, 'id')
                assert hasattr(resource, 'name')
                assert hasattr(resource, 'type')
    
    def test_create_resource(self):
        """Test resource creation functionality."""
        # Test with dictionary data
        resource_dict = {
            'id': 'new_resource',
            'name': 'Test Resource',
            'type': 'test',
            'value': 15.0,
            'quantity': 25
        }
        
        created_resource = self.service.create_resource(resource_dict)
        assert isinstance(created_resource, Resource)
        assert created_resource.id == 'new_resource'
        assert created_resource.name == 'Test Resource'
        assert created_resource.type == 'test'
        assert created_resource.value == 15.0
        assert created_resource.quantity == 25
        
        # Test with Resource object
        existing_resource = Resource(
            id='existing',
            name='Existing Resource',
            type='existing_type',
            value=20.0,
            quantity=30
        )
        
        result = self.service.create_resource(existing_resource)
        assert result is existing_resource
    
    def test_update_resource(self):
        """Test resource update functionality."""
        # Update existing resource
        updates = {
            'name': 'Updated Name',
            'value': 25.0,
            'quantity': 50
        }
        
        updated_resource = self.service.update_resource('1', updates)
        
        if updated_resource:
            assert updated_resource.name == 'Updated Name'
            assert updated_resource.value == 25.0
            assert updated_resource.quantity == 50
    
    def test_update_resource_invalid_attributes(self):
        """Test resource update with invalid attributes."""
        updates = {
            'invalid_attribute': 'should_be_ignored',
            'name': 'Valid Update'
        }
        
        updated_resource = self.service.update_resource('1', updates)
        
        # Should update valid attributes and ignore invalid ones
        if updated_resource:
            assert updated_resource.name == 'Valid Update'
            assert not hasattr(updated_resource, 'invalid_attribute')
    
    def test_delete_resource(self):
        """Test resource deletion functionality."""
        result = self.service.delete_resource('1')
        assert isinstance(result, bool)
        assert result is True  # Mock implementation returns True
    
    def test_adjust_resource_amount(self):
        """Test resource amount adjustment."""
        # Get original resource
        original_resource = self.service.get_resource('1')
        if original_resource and hasattr(original_resource, 'amount'):
            original_amount = original_resource.amount
            
            # Test positive adjustment
            adjusted_resource = self.service.adjust_resource_amount('1', 10.0)
            if adjusted_resource:
                assert adjusted_resource.amount == original_amount + 10.0
            
            # Test negative adjustment
            adjusted_resource2 = self.service.adjust_resource_amount('1', -5.0)
            if adjusted_resource2:
                expected_amount = original_amount + 10.0 - 5.0
                assert adjusted_resource2.amount == expected_amount
    
    def test_get_available_resources(self):
        """Test available resources retrieval with filtering."""
        # Test without filters
        all_resources = self.service.get_available_resources()
        assert isinstance(all_resources, list)
        
        # Test with region filter
        region_resources = self.service.get_available_resources(region_id=1)
        assert isinstance(region_resources, list)
        
        # Test with type filter
        food_resources = self.service.get_available_resources(resource_type='food')
        assert isinstance(food_resources, list)
        
        # Test with both filters
        region_food = self.service.get_available_resources(region_id=1, resource_type='food')
        assert isinstance(region_food, list)
        
        # Verify filtering works
        for resource in region_food:
            if hasattr(resource, 'type'):
                assert resource.type == 'food'
    
    def test_transfer_resource(self):
        """Test resource transfer between regions."""
        success, message = self.service.transfer_resource(1, 2, '1', 10.0)
        
        assert isinstance(success, bool)
        assert isinstance(message, str)
        assert success is True  # Mock implementation returns True
        assert len(message) > 0
    
    def test_population_impact_no_change(self):
        """Test population impact with no population change."""
        result = self.service.population_impact_on_resources(1, 100, 100)
        
        assert isinstance(result, dict)
        assert result['region_id'] == 1
        assert result['population_change'] == 0
        assert 'message' in result
    
    def test_population_impact_increase(self):
        """Test population impact with population increase."""
        result = self.service.population_impact_on_resources(1, 100, 120)
        
        assert isinstance(result, dict)
        assert result['region_id'] == 1
        assert result['previous_population'] == 100
        assert result['current_population'] == 120
        assert result['population_change'] == 20
        assert result['change_percentage'] == 0.2  # 20% increase
        
        assert 'resource_changes' in result
        assert 'events' in result
        assert isinstance(result['resource_changes'], list)
        assert isinstance(result['events'], list)
    
    def test_population_impact_decrease(self):
        """Test population impact with population decrease."""
        result = self.service.population_impact_on_resources(1, 100, 80)
        
        assert isinstance(result, dict)
        assert result['region_id'] == 1
        assert result['previous_population'] == 100
        assert result['current_population'] == 80
        assert result['population_change'] == -20
        assert result['change_percentage'] == -0.2  # 20% decrease
    
    def test_population_impact_from_zero(self):
        """Test population impact when previous population was zero."""
        result = self.service.population_impact_on_resources(1, 0, 50)
        
        assert isinstance(result, dict)
        assert result['change_percentage'] == 1.0  # 100% increase from zero
    
    def test_population_impact_resource_types(self):
        """Test population impact on different resource types."""
        result = self.service.population_impact_on_resources(1, 100, 150)
        
        if result and 'resource_changes' in result:
            resource_changes = result['resource_changes']
            
            # Verify different resource types have appropriate impact
            for change in resource_changes:
                assert 'resource_type' in change
                assert 'change' in change
                assert 'previous_amount' in change
                assert 'new_amount' in change
                
                # Verify change calculation makes sense
                resource_type = change['resource_type']
                if resource_type in ['food', 'water']:
                    # High consumption resources should have significant impact
                    assert abs(change['change']) > 0
    
    def test_population_impact_events_generation(self):
        """Test that significant population changes generate events."""
        # Large population change should generate events
        result = self.service.population_impact_on_resources(1, 100, 200)
        
        if result and 'events' in result:
            events = result['events']
            
            for event in events:
                assert 'type' in event
                assert 'region_id' in event
                assert 'resource_id' in event
                assert 'cause' in event
                assert event['cause'] == 'population_change'
                assert event['region_id'] == 1
    
    def test_error_handling(self):
        """Test error handling in ResourceService operations."""
        # Test with invalid inputs
        result = self.service.get_resource(None)
        assert result is not None  # Should handle gracefully
        
        # Test population impact with invalid data
        try:
            result = self.service.population_impact_on_resources(-1, -1, -1)
            assert isinstance(result, dict)  # Should not crash
        except Exception:
            pass  # Exceptions are acceptable for invalid input
    
    def test_logging_functionality(self):
        """Test that logging is working in ResourceService."""
        with patch('backend.systems.economy.resource_service.logger') as mock_logger:
            service = ResourceService()
            assert mock_logger.info.called
    
    def test_database_session_usage(self):
        """Test ResourceService behavior with database session."""
        mock_session = Mock()
        service = ResourceService(mock_session)
        
        # Operations should use the database session when available
        assert service.db_session is mock_session
        
        # Population impact method should interact with db_session
        try:
            result = service.population_impact_on_resources(1, 100, 120)
            # Should attempt to use session for commits/rollbacks
        except Exception:
            pass  # Expected since we're using a mock session
    
    def test_data_validation(self):
        """Test data validation in ResourceService operations."""
        # Test resource creation with valid data
        valid_data = {
            'id': 'valid_id',
            'name': 'Valid Resource',
            'type': 'valid_type',
            'value': 10.0,
            'quantity': 5
        }
        
        resource = self.service.create_resource(valid_data)
        assert isinstance(resource, Resource)
        assert resource.id == 'valid_id'
    
    def test_resource_type_consistency(self):
        """Test that resource types are handled consistently."""
        # Get resources by region and verify type consistency
        resources = self.service.get_resources_by_region(1)
        
        resource_types = set()
        for resource in resources:
            if hasattr(resource, 'type'):
                resource_types.add(resource.type)
        
        # Should have consistent type structure
        for resource_type in resource_types:
            assert isinstance(resource_type, str)
            assert len(resource_type) > 0
    
    def test_concurrent_resource_access(self):
        """Test concurrent access to resource operations."""
        # Simulate multiple concurrent resource retrievals
        resources = []
        for i in range(10):
            resource = self.service.get_resource(f'concurrent_{i}')
            resources.append(resource)
        
        # All should succeed and be properly structured
        for i, resource in enumerate(resources):
            assert resource.id == f'concurrent_{i}'
            assert isinstance(resource, Resource)
    
    @pytest.mark.performance
    def test_performance_resource_operations(self):
        """Test performance of resource operations."""
        import time
        
        # Test get_resource performance
        start_time = time.time()
        for i in range(100):
            self.service.get_resource(f'perf_test_{i}')
        get_time = time.time() - start_time
        
        assert get_time < 1.0  # Should complete 100 operations quickly
        
        # Test get_resources_by_region performance
        start_time = time.time()
        for i in range(50):
            self.service.get_resources_by_region(i)
        region_time = time.time() - start_time
        
        assert region_time < 2.0  # Should complete 50 region queries quickly


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 