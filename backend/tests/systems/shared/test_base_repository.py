from backend.systems.shared.database.base import Base
from backend.systems.shared.database.base import Base
from dataclasses import field
"""
Tests for backend.systems.shared.database.base_repository

Comprehensive tests for the BaseRepository class.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession

# Import the required classes
from backend.systems.shared.database.base import Base

# Fix the BaseRepository import using direct file loading to avoid directory conflict
import sys
import importlib.util

# Load BaseRepository directly from the .py file 
spec = importlib.util.spec_from_file_location(
    "base_repository", 
    "/Users/Sharrone/Visual_DM/backend/systems/shared/database/base_repository.py"
)
base_repo_module = importlib.util.module_from_spec(spec)
sys.modules["base_repository_direct"] = base_repo_module
spec.loader.exec_module(base_repo_module)
BaseRepository = base_repo_module.BaseRepository

# Create a test model for testing
class TestModel(Base): pass
    __tablename__ = 'test_model_repo'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    value = Column(Integer)


# Create a concrete repository for testing
class TestRepository(BaseRepository[TestModel]): pass
    def __init__(self, session: AsyncSession): pass
        super().__init__(session, TestModel)


def test_module_imports(): pass
    """Test that the module can be imported without errors."""
    from backend.systems.shared.database.base_repository import BaseRepository
    assert BaseRepository is not None


class TestBaseRepository: pass
    """Test class for BaseRepository"""
    
    def setup_method(self): pass
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.repository = TestRepository(self.mock_session)
    
    def test_repository_initialization(self): pass
        """Test repository initialization."""
        assert self.repository.session is self.mock_session
        assert self.repository.model_class is TestModel
    
    @pytest.mark.asyncio
    async def test_create(self): pass
        """Test creating a new entity."""
        # Mock the entity creation
        mock_entity = TestModel(id=1, name="test", value=100)
        
        # Mock session methods
        self.mock_session.add = Mock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Mock the model class constructor
        with patch.object(TestModel, '__new__', return_value=mock_entity): pass
            result = await self.repository.create(name="test", value=100)
        
        assert result is mock_entity
        self.mock_session.add.assert_called_once_with(mock_entity)
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once_with(mock_entity)
    
    @pytest.mark.asyncio
    async def test_get_by_id_found(self): pass
        """Test getting entity by ID when found."""
        mock_entity = Mock(spec=TestModel)
        mock_entity.id = 1
        mock_entity.name = "test"
        mock_entity.value = 100
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_entity
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.get_by_id(1)
        
        assert result is mock_entity
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self): pass
        """Test getting entity by ID when not found."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.get_by_id(999)
        
        assert result is None
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_no_pagination(self): pass
        """Test getting all entities without pagination."""
        mock_entity1 = Mock(spec=TestModel)
        mock_entity1.id = 1
        mock_entity1.name = "test1"
        mock_entity1.value = 100
        
        mock_entity2 = Mock(spec=TestModel)
        mock_entity2.id = 2
        mock_entity2.name = "test2"
        mock_entity2.value = 200
        
        mock_entities = [mock_entity1, mock_entity2]
        mock_scalars = Mock()
        mock_scalars.all.return_value = mock_entities
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.get_all()
        
        assert result == mock_entities
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self): pass
        """Test getting all entities with pagination."""
        mock_entity = Mock(spec=TestModel)
        mock_entity.id = 1
        mock_entity.name = "test1"
        mock_entity.value = 100
        mock_entities = [mock_entity]
        mock_scalars = Mock()
        mock_scalars.all.return_value = mock_entities
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.get_all(limit=10, offset=5)
        
        assert result == mock_entities
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_criteria_with_matches(self): pass
        """Test getting entities by criteria with matches."""
        mock_entity = Mock(spec=TestModel)
        mock_entity.id = 1
        mock_entity.name = "test"
        mock_entity.value = 100
        mock_entities = [mock_entity]
        mock_scalars = Mock()
        mock_scalars.all.return_value = mock_entities
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.get_by_criteria(name="test", value=100)
        
        assert result == mock_entities
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_criteria_no_matches(self): pass
        """Test getting entities by criteria with no matches."""
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.get_by_criteria(name="nonexistent")
        
        assert result == []
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_criteria_invalid_field(self): pass
        """Test getting entities by criteria with invalid field."""
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        # Should ignore invalid fields
        result = await self.repository.get_by_criteria(invalid_field="value")
        
        assert result == []
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_existing_entity(self): pass
        """Test updating an existing entity."""
        mock_entity = Mock(spec=TestModel)
        mock_entity.id = 1
        mock_entity.name = "old_name"
        mock_entity.value = 100
        
        # Mock get_by_id to return the entity
        with patch.object(self.repository, 'get_by_id', return_value=mock_entity): pass
            self.mock_session.commit = AsyncMock()
            self.mock_session.refresh = AsyncMock()
            
            result = await self.repository.update(1, name="new_name", value=200)
        
        assert result is mock_entity
        assert mock_entity.name == "new_name"
        assert mock_entity.value == 200
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once_with(mock_entity)
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_entity(self): pass
        """Test updating a nonexistent entity."""
        # Mock get_by_id to return None
        with patch.object(self.repository, 'get_by_id', return_value=None): pass
            result = await self.repository.update(999, name="new_name")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_invalid_field(self): pass
        """Test updating with invalid field."""
        mock_entity = Mock(spec=TestModel)
        mock_entity.id = 1
        mock_entity.name = "test"
        mock_entity.value = 100
        original_name = mock_entity.name
        
        # Mock get_by_id to return the entity
        with patch.object(self.repository, 'get_by_id', return_value=mock_entity): pass
            self.mock_session.commit = AsyncMock()
            self.mock_session.refresh = AsyncMock()
            
            result = await self.repository.update(1, invalid_field="value")
        
        assert result is mock_entity
        assert mock_entity.name == original_name  # Should not change
        self.mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_existing_entity(self): pass
        """Test deleting an existing entity."""
        mock_entity = Mock(spec=TestModel)
        mock_entity.id = 1
        mock_entity.name = "test"
        mock_entity.value = 100
        
        # Mock get_by_id to return the entity
        with patch.object(self.repository, 'get_by_id', return_value=mock_entity): pass
            self.mock_session.delete = AsyncMock()
            self.mock_session.commit = AsyncMock()
            
            result = await self.repository.delete(1)
        
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_entity)
        self.mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_entity(self): pass
        """Test deleting a nonexistent entity."""
        # Mock get_by_id to return None
        with patch.object(self.repository, 'get_by_id', return_value=None): pass
            result = await self.repository.delete(999)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_exists_true(self): pass
        """Test exists method when entity exists."""
        mock_entity = Mock(spec=TestModel)
        mock_entity.id = 1
        mock_entity.name = "test"
        mock_entity.value = 100
        
        # Mock get_by_id to return the entity
        with patch.object(self.repository, 'get_by_id', return_value=mock_entity): pass
            result = await self.repository.exists(1)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_exists_false(self): pass
        """Test exists method when entity doesn't exist."""
        # Mock get_by_id to return None
        with patch.object(self.repository, 'get_by_id', return_value=None): pass
            result = await self.repository.exists(999)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_count_with_criteria(self): pass
        """Test counting entities with criteria."""
        mock_result = Mock()
        mock_result.scalar.return_value = 5
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.count(name="test")
        
        assert result == 5
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_no_criteria(self): pass
        """Test counting all entities."""
        mock_result = Mock()
        mock_result.scalar.return_value = 10
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.count()
        
        assert result == 10
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bulk_create(self): pass
        """Test bulk creating entities."""
        entities_data = [
            {"name": "test1", "value": 100},
            {"name": "test2", "value": 200}
        ]
        
        mock_entity1 = Mock(spec=TestModel)
        mock_entity1.id = 1
        mock_entity1.name = "test1"
        mock_entity1.value = 100
        
        mock_entity2 = Mock(spec=TestModel)
        mock_entity2.id = 2
        mock_entity2.name = "test2"
        mock_entity2.value = 200
        
        mock_entities = [mock_entity1, mock_entity2]
        
        self.mock_session.add = Mock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Mock the model class constructor
        with patch.object(TestModel, '__new__', side_effect=mock_entities): pass
            result = await self.repository.bulk_create(entities_data)
        
        assert len(result) == 2
        assert self.mock_session.add.call_count == 2
        self.mock_session.commit.assert_called_once()
        assert self.mock_session.refresh.call_count == 2
    
    @pytest.mark.asyncio
    async def test_bulk_update(self): pass
        """Test bulk updating entities."""
        updates = [
            {"id": 1, "name": "updated1"},
            {"id": 2, "name": "updated2"},
            {"id": 999, "name": "nonexistent"}  # This should not be updated
        ]
        
        mock_entity1 = Mock(spec=TestModel)
        mock_entity1.id = 1
        mock_entity1.name = "updated1"
        mock_entity1.value = 100
        
        mock_entity2 = Mock(spec=TestModel)
        mock_entity2.id = 2
        mock_entity2.name = "updated2"
        mock_entity2.value = 200
        
        # Mock update method to return entities for existing IDs, None for nonexistent
        async def mock_update(entity_id, **kwargs): pass
            if entity_id == 1: pass
                return mock_entity1
            elif entity_id == 2: pass
                return mock_entity2
            else: pass
                return None
        
        with patch.object(self.repository, 'update', side_effect=mock_update): pass
            result = await self.repository.bulk_update(updates)
        
        assert result == 2  # Only 2 entities should be updated
    
    @pytest.mark.asyncio
    async def test_bulk_update_empty_updates(self): pass
        """Test bulk updating with empty update data."""
        updates = [
            {"id": 1},  # No fields to update
            {"name": "test"}  # No ID
        ]
        
        with patch.object(self.repository, 'update') as mock_update: pass
            result = await self.repository.bulk_update(updates)
        
        assert result == 0
        mock_update.assert_not_called()
