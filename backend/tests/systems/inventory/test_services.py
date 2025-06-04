"""
Test module for inventory.services

Tests the business services according to Development_Bible.md standards.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4, UUID
from datetime import datetime

from backend.systems.inventory.services import (
    InventoryService,
    InventoryRepositoryInterface,
    create_inventory_service
)
from backend.systems.inventory.models import (
    CreateInventoryRequest,
    UpdateInventoryRequest,
    InventoryResponse,
    InventoryModel
)


class MockConfigLoader:
    """Mock configuration loader for testing."""
    
    def get_validation_rules(self):
        return {
            "max_name_length": 255,
            "min_name_length": 1,
            "max_description_length": 1000,
            "allowed_status_values": ["active", "inactive", "maintenance", "archived", "corrupted"]
        }
    
    def get_defaults(self):
        return {
            "status": "active",
            "is_active": True
        }
    
    def get_pagination_config(self):
        return {
            "max_page_size": 100,
            "min_page_size": 1
        }
    
    def can_transition_status(self, from_status, to_status):
        valid_transitions = {
            "active": ["inactive", "maintenance", "archived"],
            "inactive": ["active", "archived"],
            "maintenance": ["active", "inactive"],
            "archived": [],
            "corrupted": ["maintenance", "archived"]
        }
        return to_status in valid_transitions.get(from_status, [])
    
    def allows_operations(self, status):
        return status in ["active"]


class MockRepository:
    """Mock repository for testing services."""
    
    def __init__(self):
        self.inventories = {}
        
    async def create(self, data):
        inventory = InventoryModel(
            id=uuid4(),
            name=data["name"],
            description=data.get("description"),
            status=data.get("status", "active"),
            properties=data.get("properties", {}),
            created_at=datetime.utcnow(),
            is_active=True
        )
        self.inventories[inventory.id] = inventory
        return inventory
        
    async def get_by_id(self, inventory_id):
        return self.inventories.get(inventory_id)
        
    async def get_by_name(self, name):
        for inventory in self.inventories.values():
            if inventory.name == name:
                return inventory
        return None
        
    async def get_by_name_and_owner(self, name, owner_id):
        for inventory in self.inventories.values():
            if inventory.name == name and getattr(inventory, 'owner_id', None) == owner_id:
                return inventory
        return None
        
    async def update(self, inventory_id, data):
        inventory = self.inventories.get(inventory_id)
        if inventory:
            for key, value in data.items():
                setattr(inventory, key, value)
        return inventory
        
    async def delete(self, inventory_id):
        if inventory_id in self.inventories:
            del self.inventories[inventory_id]
            return True
        return False
        
    async def list(self, page=1, size=50, status=None, search=None):
        items = list(self.inventories.values())
        if status:
            items = [i for i in items if i.status == status]
        if search:
            items = [i for i in items if search.lower() in i.name.lower()]
        
        start = (page - 1) * size
        end = start + size
        return items[start:end], len(items)
        
    async def get_statistics(self):
        return {"total": len(self.inventories)}


class TestInventoryService:
    """Test suite for inventory service."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock repository for testing."""
        return MockRepository()
    
    @pytest.fixture
    def mock_config_loader(self):
        """Mock config loader for testing."""
        return MockConfigLoader()
    
    @pytest.fixture
    def inventory_service(self, mock_repository, mock_config_loader):
        """Create inventory service with mocks."""
        service = InventoryService(mock_repository)
        service.config_loader = mock_config_loader
        return service
    
    @pytest.fixture
    def sample_create_request(self):
        """Sample create request data."""
        return CreateInventoryRequest(
            name="Test Inventory",
            description="Test description",
            properties={"capacity": 50}
        )
    
    @pytest.mark.asyncio
    async def test_create_inventory_success(self, inventory_service, sample_create_request):
        """Test successful inventory creation."""
        result = await inventory_service.create_inventory(sample_create_request)
        
        assert isinstance(result, InventoryResponse)
        assert result.name == "Test Inventory"
        assert result.description == "Test description"
        assert result.status == "active"
        assert result.is_active is True
    
    @pytest.mark.asyncio
    async def test_create_inventory_duplicate_name(self, inventory_service, sample_create_request):
        """Test inventory creation with duplicate name fails."""
        await inventory_service.create_inventory(sample_create_request)
        
        with pytest.raises(ValueError, match="already exists"):
            await inventory_service.create_inventory(sample_create_request)
    
    @pytest.mark.asyncio
    async def test_get_inventory_by_id(self, inventory_service, sample_create_request):
        """Test getting inventory by ID."""
        created = await inventory_service.create_inventory(sample_create_request)
        
        result = await inventory_service.get_inventory_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.name == created.name
    
    @pytest.mark.asyncio
    async def test_get_inventory_not_found(self, inventory_service):
        """Test getting non-existent inventory returns None."""
        result = await inventory_service.get_inventory_by_id(uuid4())
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_inventory(self, inventory_service, sample_create_request):
        """Test updating inventory."""
        created = await inventory_service.create_inventory(sample_create_request)
        
        update_request = UpdateInventoryRequest(
            name="Updated Name",
            description="Updated description"
        )
        
        result = await inventory_service.update_inventory(created.id, update_request)
        
        assert result.name == "Updated Name"
        assert result.description == "Updated description"
        assert result.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_update_inventory_not_found(self, inventory_service):
        """Test updating non-existent inventory fails."""
        update_request = UpdateInventoryRequest(name="New Name")
        
        with pytest.raises(ValueError, match="not found"):
            await inventory_service.update_inventory(uuid4(), update_request)
    
    @pytest.mark.asyncio
    async def test_update_inventory_invalid_status_transition(self, inventory_service, sample_create_request):
        """Test updating inventory with invalid status transition."""
        created = await inventory_service.create_inventory(sample_create_request)
        
        update_request = UpdateInventoryRequest(status="archived")
        # First set to maintenance to get to archived state
        await inventory_service.update_inventory(created.id, UpdateInventoryRequest(status="maintenance"))
        await inventory_service.update_inventory(created.id, UpdateInventoryRequest(status="archived"))
        
        # Now try invalid transition from archived
        with pytest.raises(ValueError, match="Cannot transition"):
            await inventory_service.update_inventory(created.id, UpdateInventoryRequest(status="active"))
    
    @pytest.mark.asyncio
    async def test_delete_inventory(self, inventory_service, sample_create_request):
        """Test deleting inventory."""
        created = await inventory_service.create_inventory(sample_create_request)
        
        result = await inventory_service.delete_inventory(created.id)
        
        assert result is True
        
        # Verify it's deleted
        retrieved = await inventory_service.get_inventory_by_id(created.id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_delete_inventory_not_found(self, inventory_service):
        """Test deleting non-existent inventory fails."""
        with pytest.raises(ValueError, match="not found"):
            await inventory_service.delete_inventory(uuid4())
    
    @pytest.mark.asyncio
    async def test_delete_inventory_wrong_status(self, inventory_service, sample_create_request):
        """Test deleting inventory with wrong status fails."""
        created = await inventory_service.create_inventory(sample_create_request)
        
        # Change to inactive status (not allowed for operations)
        await inventory_service.update_inventory(created.id, UpdateInventoryRequest(status="inactive"))
        
        with pytest.raises(ValueError, match="Cannot delete"):
            await inventory_service.delete_inventory(created.id)
    
    @pytest.mark.asyncio
    async def test_list_inventories(self, inventory_service):
        """Test listing inventories with pagination."""
        # Create test inventories
        for i in range(5):
            request = CreateInventoryRequest(name=f"Inventory {i}")
            await inventory_service.create_inventory(request)
        
        inventories, total = await inventory_service.list_inventories(page=1, size=3)
        
        assert len(inventories) == 3
        assert total == 5
        assert all(isinstance(inv, InventoryResponse) for inv in inventories)
    
    @pytest.mark.asyncio
    async def test_list_inventories_with_filters(self, inventory_service):
        """Test listing inventories with status filter."""
        # Create test inventories with different statuses
        request1 = CreateInventoryRequest(name="Active Inventory")
        request2 = CreateInventoryRequest(name="Test Inventory")
        
        created1 = await inventory_service.create_inventory(request1)
        created2 = await inventory_service.create_inventory(request2)
        
        # Change one to inactive
        await inventory_service.update_inventory(created2.id, UpdateInventoryRequest(status="inactive"))
        
        # Test status filter
        inventories, total = await inventory_service.list_inventories(status="active")
        assert len(inventories) == 1
        assert inventories[0].name == "Active Inventory"
        
        # Test search filter
        inventories, total = await inventory_service.list_inventories(search="active")
        assert len(inventories) == 1
        assert inventories[0].name == "Active Inventory"
    
    @pytest.mark.asyncio
    async def test_get_inventory_statistics(self, inventory_service):
        """Test getting inventory statistics."""
        # Create some test data
        for i in range(3):
            request = CreateInventoryRequest(name=f"Test {i}")
            await inventory_service.create_inventory(request)
        
        stats = await inventory_service.get_inventory_statistics()
        assert stats["total"] == 3


class TestInventoryServiceFactory:
    """Test the service factory function."""
    
    def test_create_inventory_service(self):
        """Test creating inventory service through factory."""
        mock_repository = Mock(spec=InventoryRepositoryInterface)
        
        service = create_inventory_service(mock_repository)
        
        assert isinstance(service, InventoryService)
        assert service.repository == mock_repository


# Service tests focus on:
# - Business logic implementation
# - Integration with repositories and configuration
# - Error handling and validation
# - State transitions and business rules
