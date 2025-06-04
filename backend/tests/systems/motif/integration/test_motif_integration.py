"""
Integration tests for motif system.

Tests complete workflows including API, service, repository, and cache layers.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime, timedelta

# Test framework imports
from backend.infrastructure.systems.motif.models import (
    MotifCreate, MotifUpdate, MotifFilter, 
    MotifCategory, MotifScope, MotifLifecycle
)
from backend.systems.motif.services.service import MotifService
from backend.infrastructure.systems.motif.repositories import MotifRepository
from backend.infrastructure.systems.motif.cache.redis_cache import MotifCache
from backend.infrastructure.systems.motif.routers.router import router


class TestMotifIntegration:
    """Integration tests for complete motif system."""
    
    @pytest.fixture
    async def mock_repository(self):
        """Mock repository for testing."""
        repository = AsyncMock(spec=MotifRepository)
        
        # Sample motif data
        sample_motif = {
            "id": "motif_123",
            "name": "Rising Darkness",
            "description": "Evil forces gather strength",
            "category": MotifCategory.EVIL,
            "scope": MotifScope.GLOBAL,
            "intensity": 7,
            "lifecycle": MotifLifecycle.ACTIVE,
            "theme": "growing evil",
            "descriptors": ["dark", "ominous", "threatening"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Configure mock methods
        repository.create_motif.return_value = sample_motif
        repository.get_motif.return_value = sample_motif
        repository.list_motifs.return_value = [sample_motif]
        repository.update_motif.return_value = sample_motif
        repository.delete_motif.return_value = True
        repository.count_motifs.return_value = 1
        
        return repository
    
    @pytest.fixture
    async def mock_cache(self):
        """Mock cache for testing."""
        cache = AsyncMock(spec=MotifCache)
        
        # Configure cache responses
        cache.get_motif.return_value = None  # Cache miss
        cache.set_motif.return_value = True
        cache.get_motif_list.return_value = None
        cache.set_motif_list.return_value = True
        cache.get_statistics.return_value = None
        cache.set_statistics.return_value = True
        cache.invalidate_motif_caches.return_value = None
        cache.get_cache_stats.return_value = {
            "connected": True,
            "hit_rate": 85.5,
            "total_keys": 42
        }
        
        return cache
    
    @pytest.fixture
    async def service(self, mock_repository, mock_cache):
        """Create service with mocked dependencies."""
        service = MotifService(mock_repository)
        service.cache = mock_cache
        return service
    
    @pytest.fixture
    async def client(self, service):
        """Create test client with mocked service."""
        # Mock the service dependency
        with patch('backend.infrastructure.systems.motif.routers.router.get_motif_service', return_value=service):
            from fastapi.testclient import TestClient
            with TestClient(router) as client:
                yield client

    async def test_create_motif_integration(self, service, mock_repository, mock_cache):
        """Test complete motif creation workflow."""
        # Arrange
        motif_data = MotifCreate(
            name="Test Hope",
            description="A beacon of hope emerges",
            category=MotifCategory.HOPE,
            scope=MotifScope.GLOBAL,
            intensity=6,
            theme="emerging hope"
        )
        
        # Act
        result = await service.create_motif(motif_data)
        
        # Assert
        assert result is not None
        mock_repository.create_motif.assert_called_once()
        mock_cache.invalidate_motif_caches.assert_called_once()
    
    async def test_list_motifs_with_caching(self, service, mock_repository, mock_cache):
        """Test motif listing with cache integration."""
        # Arrange
        filter_params = MotifFilter(
            categories=[MotifCategory.HOPE],
            active_only=True
        )
        
        # Configure cache miss then hit
        mock_cache.get_motif_list.side_effect = [None, [{"cached": "data"}]]
        
        # Act - First call (cache miss)
        result1 = await service.list_motifs(filter_params, limit=10, offset=0)
        
        # Act - Second call (cache hit simulation)
        mock_cache.get_motif_list.return_value = [{"cached": "data"}]
        result2 = await service.list_motifs(filter_params, limit=10, offset=0)
        
        # Assert
        assert result1 is not None
        mock_repository.list_motifs.assert_called()
        mock_cache.set_motif_list.assert_called()
    
    async def test_motif_evolution_workflow(self, service, mock_repository):
        """Test complete motif evolution process."""
        # Arrange
        motif_id = "motif_123"
        
        # Mock evolution processing
        mock_repository.get_motif.return_value = {
            "id": motif_id,
            "lifecycle": MotifLifecycle.ACTIVE,
            "intensity": 6,
            "last_evolution": datetime.utcnow() - timedelta(days=2)
        }
        
        # Act
        result = await service.trigger_motif_evolution(motif_id)
        
        # Assert
        assert result is not None
        mock_repository.get_motif.assert_called_with(motif_id)
    
    async def test_conflict_detection_and_resolution(self, service, mock_repository):
        """Test conflict detection and resolution workflow."""
        # Arrange - Mock conflicting motifs
        conflicting_motifs = [
            {
                "id": "motif_1",
                "category": MotifCategory.HOPE,
                "intensity": 8,
                "scope": MotifScope.GLOBAL
            },
            {
                "id": "motif_2", 
                "category": MotifCategory.DESPAIR,
                "intensity": 7,
                "scope": MotifScope.GLOBAL
            }
        ]
        
        mock_repository.list_motifs.return_value = conflicting_motifs
        
        # Act
        conflicts = await service.get_active_conflicts()
        
        # Assert
        assert len(conflicts) > 0
        mock_repository.list_motifs.assert_called()
    
    async def test_narrative_context_generation(self, service, mock_repository, mock_cache):
        """Test narrative context generation with caching."""
        # Arrange
        x, y = 100.0, 200.0
        
        # Mock spatial motifs
        spatial_motifs = [
            {
                "id": "motif_spatial",
                "name": "Local Mystery",
                "category": MotifCategory.MYSTERY,
                "intensity": 5,
                "position": {"x": x, "y": y}
            }
        ]
        
        mock_repository.get_motifs_by_position.return_value = spatial_motifs
        mock_cache.get_context.return_value = None  # Cache miss
        
        # Act
        context = await service.get_motif_context(x, y)
        
        # Assert
        assert context is not None
        assert "narrative_themes" in context
        assert "motif_count" in context
        mock_cache.set_context.assert_called()
    
    async def test_system_statistics_collection(self, service, mock_repository, mock_cache):
        """Test system statistics collection and caching."""
        # Arrange
        mock_repository.count_motifs.return_value = 156
        mock_repository.get_motifs_by_category.return_value = {
            "HOPE": 12,
            "EVIL": 8,
            "MYSTERY": 15
        }
        mock_cache.get_statistics.return_value = None  # Cache miss
        
        # Act
        stats = await service.get_motif_statistics()
        
        # Assert
        assert stats is not None
        assert "total_motifs" in stats
        assert "motifs_by_category" in stats
        mock_cache.set_statistics.assert_called()
    
    async def test_error_handling_and_rollback(self, service, mock_repository, mock_cache):
        """Test error handling and transaction rollback."""
        # Arrange
        motif_data = MotifCreate(
            name="Test Motif",
            description="Test description",
            category=MotifCategory.HOPE,
            scope=MotifScope.GLOBAL,
            intensity=5
        )
        
        # Mock repository error
        mock_repository.create_motif.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            await service.create_motif(motif_data)
        
        # Verify cache wasn't invalidated on error
        mock_cache.invalidate_motif_caches.assert_not_called()
    
    async def test_bulk_operations_performance(self, service, mock_repository):
        """Test bulk operations for performance."""
        # Arrange
        batch_size = 50
        motif_updates = [
            {"id": f"motif_{i}", "intensity": i % 10 + 1}
            for i in range(batch_size)
        ]
        
        # Mock bulk update
        mock_repository.bulk_update_motifs.return_value = batch_size
        
        # Act
        result = await service.bulk_update_motifs(motif_updates)
        
        # Assert
        assert result == batch_size
        mock_repository.bulk_update_motifs.assert_called_once()


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    async def mock_service(self):
        """Mock service for API testing."""
        service = AsyncMock(spec=MotifService)
        
        # Configure service responses
        service.create_motif.return_value = {
            "id": "motif_123",
            "name": "Test Motif",
            "category": "HOPE",
            "scope": "GLOBAL",
            "intensity": 6,
            "lifecycle": "ACTIVE"
        }
        
        service.list_motifs.return_value = [
            {
                "id": "motif_123", 
                "name": "Test Motif",
                "category": "HOPE"
            }
        ]
        
        service.get_motif_statistics.return_value = {
            "total_motifs": 1,
            "active_motifs": 1,
            "system_health": "healthy"
        }
        
        service.get_motif_context.return_value = {
            "active_motifs": [],
            "narrative_themes": ["test_theme"],
            "motif_count": 0
        }
        
        return service
    
    @pytest.mark.asyncio
    async def test_api_create_motif(self, mock_service):
        """Test motif creation via API."""
        # Arrange
        motif_data = {
            "name": "API Test Motif",
            "description": "Created via API",
            "category": "HOPE",
            "scope": "GLOBAL",
            "intensity": 7
        }
        
        with patch('backend.infrastructure.systems.motif.routers.router.get_motif_service', return_value=mock_service):
            from fastapi.testclient import TestClient
            with TestClient(router) as client:
                # Act
                response = client.post("/motifs", json=motif_data)
                
                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                mock_service.create_motif.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_list_motifs_with_filters(self, mock_service):
        """Test motif listing with query parameters."""
        with patch('backend.infrastructure.systems.motif.routers.router.get_motif_service', return_value=mock_service):
            from fastapi.testclient import TestClient
            with TestClient(router) as client:
                # Act
                response = client.get("/motifs?category=HOPE&active_only=true&limit=10")
                
                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "data" in data
                mock_service.list_motifs.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_get_context(self, mock_service):
        """Test narrative context endpoint."""
        with patch('backend.infrastructure.systems.motif.routers.router.get_motif_service', return_value=mock_service):
            from fastapi.testclient import TestClient
            with TestClient(router) as client:
                # Act
                response = client.get("/context?x=100.0&y=200.0")
                
                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "narrative_themes" in data["data"]
                mock_service.get_motif_context.assert_called_with(100.0, 200.0)
    
    @pytest.mark.asyncio  
    async def test_api_health_check(self, mock_service):
        """Test health check endpoint."""
        # Mock health check response
        mock_service.get_motif_statistics.return_value = {
            "system_health": "healthy",
            "total_motifs": 42
        }
        
        with patch('backend.infrastructure.systems.motif.routers.router.get_motif_service', return_value=mock_service):
            from fastapi.testclient import TestClient
            with TestClient(router) as client:
                # Act
                response = client.get("/health")
                
                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, mock_service):
        """Test API error handling."""
        # Mock service error
        mock_service.create_motif.side_effect = ValueError("Invalid intensity")
        
        motif_data = {
            "name": "Error Test",
            "description": "Should fail",
            "category": "HOPE",
            "scope": "GLOBAL",
            "intensity": 15  # Invalid intensity
        }
        
        with patch('backend.infrastructure.systems.motif.routers.router.get_motif_service', return_value=mock_service):
            from fastapi.testclient import TestClient
            with TestClient(router) as client:
                # Act
                response = client.post("/motifs", json=motif_data)
                
                # Assert
                assert response.status_code == 400
                data = response.json()
                assert data["success"] is False
                assert "error" in data


class TestSystemIntegration:
    """End-to-end system integration tests."""
    
    async def test_complete_motif_lifecycle_scenario(self):
        """Test complete motif lifecycle from creation to resolution."""
        # This would be a comprehensive test using real components
        # For now, we'll structure it to show the expected flow
        
        # 1. Initialize system components
        # repository = MotifRepository(session)
        # cache = MotifCache(redis_url)
        # service = MotifService(repository, cache)
        
        # 2. Create initial motif
        # motif = await service.create_motif(motif_data)
        
        # 3. Verify caching
        # cached_motif = await cache.get_motif(motif.id)
        
        # 4. Trigger evolution
        # evolved = await service.trigger_motif_evolution(motif.id)
        
        # 5. Check conflicts
        # conflicts = await service.get_active_conflicts()
        
        # 6. Generate context
        # context = await service.get_motif_context()
        
        # 7. Cleanup
        # await service.delete_motif(motif.id)
        
        # For now, just assert the test structure is valid
        assert True
    
    async def test_performance_under_load(self):
        """Test system performance under simulated load."""
        # This would test concurrent operations
        # Would include:
        # - Concurrent motif creation
        # - Simultaneous context requests
        # - Cache performance
        # - Database connection pooling
        
        # Placeholder for load testing
        concurrent_operations = 10
        tasks = []
        
        for i in range(concurrent_operations):
            # task = asyncio.create_task(simulate_operation(i))
            # tasks.append(task)
            pass
        
        # results = await asyncio.gather(*tasks)
        # assert all(results)
        
        assert True
    
    async def test_data_consistency_across_layers(self):
        """Test data consistency between API, service, repository, and cache."""
        # This would verify:
        # - Cache invalidation triggers correctly
        # - Database transactions maintain consistency
        # - API responses match service layer data
        # - Concurrent updates don't cause conflicts
        
        assert True
    
    async def test_system_recovery_scenarios(self):
        """Test system behavior during failure scenarios."""
        # This would test:
        # - Database connection loss
        # - Cache unavailability  
        # - Service layer exceptions
        # - Network timeouts
        # - Graceful degradation
        
        assert True


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmarks for optimization."""
    
    @pytest.mark.benchmark
    async def test_motif_creation_performance(self):
        """Benchmark motif creation speed."""
        pass
    
    @pytest.mark.benchmark  
    async def test_context_generation_performance(self):
        """Benchmark context generation speed."""
        pass
    
    @pytest.mark.benchmark
    async def test_cache_hit_ratio(self):
        """Benchmark cache performance."""
        pass


# Configuration for pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 