"""
Test module for inventory system service factories.

Tests service factory functions according to Development_Bible.md standards.
"""

import pytest
from unittest.mock import Mock
from backend.systems.inventory.services import (
    create_inventory_service,
    InventoryRepositoryInterface
)


class TestInventoryServiceFactory:
    """Test service factory functions for inventory system."""
    
    def test_create_inventory_service_with_repository(self):
        """Test creating inventory service with repository."""
        mock_repository = Mock(spec=InventoryRepositoryInterface)
        
        service = create_inventory_service(mock_repository)
        
        assert service is not None
        assert service.repository == mock_repository
    
    def test_create_inventory_service_with_none_repository_fails(self):
        """Test creating inventory service with None repository fails."""
        with pytest.raises((TypeError, ValueError)):
            create_inventory_service(None)
    
    def test_factory_creates_configured_service(self):
        """Test that factory creates properly configured service."""
        mock_repository = Mock(spec=InventoryRepositoryInterface)
        
        service = create_inventory_service(mock_repository)
        
        # Verify service has required attributes
        assert hasattr(service, 'repository')
        assert hasattr(service, 'create_inventory')
        assert hasattr(service, 'get_inventory_by_id')
        assert hasattr(service, 'update_inventory')
        assert hasattr(service, 'delete_inventory')
        assert hasattr(service, 'list_inventories')
    
    def test_factory_service_methods_are_callable(self):
        """Test that factory-created service methods are callable."""
        mock_repository = Mock(spec=InventoryRepositoryInterface)
        
        service = create_inventory_service(mock_repository)
        
        # Verify all service methods are callable
        assert callable(service.create_inventory)
        assert callable(service.get_inventory_by_id)
        assert callable(service.update_inventory)
        assert callable(service.delete_inventory)
        assert callable(service.list_inventories)
        assert callable(service.get_inventory_statistics)


class TestInventoryServiceConfiguration:
    """Test service configuration and dependencies."""
    
    def test_service_dependency_injection(self):
        """Test that service properly injects dependencies."""
        mock_repository = Mock(spec=InventoryRepositoryInterface)
        
        service = create_inventory_service(mock_repository)
        
        # Service should have the injected repository
        assert service.repository is mock_repository
    
    def test_service_configuration_defaults(self):
        """Test that service has appropriate configuration defaults."""
        mock_repository = Mock(spec=InventoryRepositoryInterface)
        
        service = create_inventory_service(mock_repository)
        
        # Service should have reasonable defaults
        # (These would be implementation-specific)
        assert service is not None
        
        # Configuration loading should be possible
        # (This would test actual config integration when implemented)
        assert True  # Placeholder for configuration tests


# Service factory tests focus on:
# - Dependency injection patterns
# - Service configuration and setup
# - Factory method behavior
# - Integration point validation
