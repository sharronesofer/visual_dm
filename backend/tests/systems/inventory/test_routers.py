"""
Test services for inventory system.

Tests the business services component according to Development_Bible.md standards.
Routers are infrastructure concerns and should be tested in infrastructure tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4, UUID
from datetime import datetime

from backend.systems.inventory.services import InventoryService, InventoryRepositoryInterface
from backend.systems.inventory.models import (
    CreateInventoryRequest,
    UpdateInventoryRequest,
    InventoryResponse
)


class MockInventoryRepository:
    """Mock repository for testing business services"""
    
    def __init__(self):
        self.inventories = {}
        
    async def create(self, data):
        from backend.systems.inventory.models import InventoryModel
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
        
    async def get_by_id(self, inventory_id: UUID):
        return self.inventories.get(inventory_id)
        
    async def get_by_name(self, name: str):
        for inventory in self.inventories.values():
            if inventory.name == name:
                return inventory
        return None
        
    async def get_by_name_and_owner(self, name: str, owner_id: UUID):
        for inventory in self.inventories.values():
            if inventory.name == name and getattr(inventory, 'owner_id', None) == owner_id:
                return inventory
        return None
        
    async def update(self, inventory_id: UUID, data):
        inventory = self.inventories.get(inventory_id)
        if inventory:
            for key, value in data.items():
                setattr(inventory, key, value)
        return inventory
        
    async def delete(self, inventory_id: UUID):
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


class TestInventoryServices:
    """Test suite for inventory business services."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock repository for testing."""
        return MockInventoryRepository()
    
    @pytest.fixture
    def inventory_service(self, mock_repository):
        """Create inventory service with mock repository."""
        return InventoryService(mock_repository)
    
    @pytest.fixture
    def sample_create_request(self):
        """Sample create request data."""
        return CreateInventoryRequest(
            name="Test Inventory",
            description="Test description",
            properties={"test": "value"}
        )
    
    @pytest.mark.asyncio
    async def test_create_inventory_success(self, inventory_service, sample_create_request):
        """Test successful inventory creation."""
        response = await inventory_service.create_inventory(sample_create_request)
        
        assert isinstance(response, InventoryResponse)
        assert response.name == "Test Inventory"
        assert response.description == "Test description"
        assert response.status == "active"
        assert response.is_active is True
    
    @pytest.mark.asyncio
    async def test_create_inventory_duplicate_name(self, inventory_service, sample_create_request):
        """Test inventory creation with duplicate name fails."""
        # Create first inventory
        await inventory_service.create_inventory(sample_create_request)
        
        # Try to create another with same name
        with pytest.raises(ValueError, match="already exists"):
            await inventory_service.create_inventory(sample_create_request)
    
    @pytest.mark.asyncio
    async def test_get_inventory_by_id(self, inventory_service, sample_create_request):
        """Test getting inventory by ID."""
        created = await inventory_service.create_inventory(sample_create_request)
        
        retrieved = await inventory_service.get_inventory_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
    
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
        
        updated = await inventory_service.update_inventory(created.id, update_request)
        
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
        assert updated.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_update_inventory_not_found(self, inventory_service):
        """Test updating non-existent inventory fails."""
        update_request = UpdateInventoryRequest(name="New Name")
        
        with pytest.raises(ValueError, match="not found"):
            await inventory_service.update_inventory(uuid4(), update_request)
    
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


# Business logic tests focus on:
# - Service layer functionality
# - Business rule validation  
# - Integration between services and repositories
# - Error handling for business rules
