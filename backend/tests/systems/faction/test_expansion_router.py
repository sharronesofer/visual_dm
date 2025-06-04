"""
Tests for Faction Expansion Router

Test suite for faction expansion API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.systems.faction.routers.expansion_router import (
    expansion_router,
    attempt_expansion,
    get_faction_expansion_profile,
    get_region_expansion_opportunities,
    simulate_bulk_expansion
)
from backend.systems.faction.services.expansion_service import (
    ExpansionStrategy,
    ExpansionAttempt
)
from backend.infrastructure.schemas.faction.expansion_schemas import (
    ExpansionAttemptRequest,
    ExpansionStrategyType,
    FactionExpansionProfileRequest,
    RegionExpansionOpportunitiesRequest,
    BulkExpansionSimulationRequest
)
from backend.infrastructure.models.faction.models import FactionEntity, FactionResponse


class TestExpansionRouterEndpoints:
    """Test expansion router endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.faction_id = uuid4()
        self.target_region_id = uuid4()
        self.mock_db = MagicMock()
        self.mock_expansion_service = MagicMock()
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_success(self):
        """Test successful expansion attempt endpoint"""
        # Setup request
        request = ExpansionAttemptRequest(
            faction_id=self.faction_id,
            target_region_id=self.target_region_id,
            strategy=ExpansionStrategyType.MILITARY,
            force_attempt=False
        )
        
        # Mock faction service
        mock_faction_service = MagicMock()
        mock_faction_response = FactionResponse(
            id=self.faction_id,
            name="Test Faction",
            description="Test Description",
            status="active",
            properties={},
            created_at="2023-01-01T00:00:00",
            updated_at=None,
            is_active=True,
            hidden_ambition=3,
            hidden_integrity=3,
            hidden_discipline=3,
            hidden_impulsivity=3,
            hidden_pragmatism=3,
            hidden_resilience=3
        )
        mock_faction_service.get_faction_by_id = AsyncMock(return_value=mock_faction_response)
        
        # Mock faction entity
        mock_faction_entity = MagicMock(spec=FactionEntity)
        mock_faction_entity.id = self.faction_id
        mock_faction_entity.name = "Test Faction"
        mock_faction_entity.is_active = True
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_faction_entity
        
        # Mock expansion service
        self.mock_expansion_service.should_attempt_expansion.return_value = True
        expansion_result = ExpansionAttempt(
            success=True,
            strategy_used=ExpansionStrategy.MILITARY,
            target_region_id=self.target_region_id,
            cost=0.8,
            effectiveness=0.75,
            reason="Successful conquest",
            consequences={"casualties": 100}
        )
        self.mock_expansion_service.attempt_expansion = AsyncMock(return_value=expansion_result)
        
        # Mock FactionService constructor
        with patch('backend.systems.faction.routers.expansion_router.FactionService') as mock_faction_service_class:
            mock_faction_service_class.return_value = mock_faction_service
            
            # Execute endpoint
            response = await attempt_expansion(
                request=request,
                expansion_service=self.mock_expansion_service,
                db=self.mock_db
            )
        
        # Verify response
        assert response.success is True
        assert response.strategy_used == ExpansionStrategyType.MILITARY
        assert response.faction_id == self.faction_id
        assert response.target_region_id == self.target_region_id
        assert response.effectiveness == 0.75
        
        # Verify service calls
        self.mock_expansion_service.attempt_expansion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_faction_not_found(self):
        """Test expansion attempt with non-existent faction"""
        request = ExpansionAttemptRequest(
            faction_id=self.faction_id,
            target_region_id=self.target_region_id,
            strategy=ExpansionStrategyType.MILITARY,
            force_attempt=False
        )
        
        # Mock faction service returning None
        mock_faction_service = MagicMock()
        mock_faction_service.get_faction_by_id = AsyncMock(return_value=None)
        
        with patch('backend.systems.faction.routers.expansion_router.FactionService') as mock_faction_service_class:
            mock_faction_service_class.return_value = mock_faction_service
            
            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await attempt_expansion(
                    request=request,
                    expansion_service=self.mock_expansion_service,
                    db=self.mock_db
                )
            
            assert exc_info.value.status_code == 404
            assert "not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_not_motivated(self):
        """Test expansion attempt when faction is not motivated to expand"""
        request = ExpansionAttemptRequest(
            faction_id=self.faction_id,
            target_region_id=self.target_region_id,
            strategy=ExpansionStrategyType.MILITARY,
            force_attempt=False
        )
        
        # Mock faction service
        mock_faction_service = MagicMock()
        mock_faction_response = FactionResponse(
            id=self.faction_id,
            name="Peaceful Faction",
            description="Test Description",
            status="active",
            properties={},
            created_at="2023-01-01T00:00:00",
            updated_at=None,
            is_active=True,
            hidden_ambition=3,
            hidden_integrity=3,
            hidden_discipline=3,
            hidden_impulsivity=3,
            hidden_pragmatism=3,
            hidden_resilience=3
        )
        mock_faction_service.get_faction_by_id = AsyncMock(return_value=mock_faction_response)
        
        # Mock faction entity
        mock_faction_entity = MagicMock(spec=FactionEntity)
        mock_faction_entity.id = self.faction_id
        mock_faction_entity.name = "Peaceful Faction"
        mock_faction_entity.is_active = True
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_faction_entity
        
        # Mock expansion service - faction not motivated
        self.mock_expansion_service.should_attempt_expansion.return_value = False
        
        with patch('backend.systems.faction.routers.expansion_router.FactionService') as mock_faction_service_class:
            mock_faction_service_class.return_value = mock_faction_service
            
            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await attempt_expansion(
                    request=request,
                    expansion_service=self.mock_expansion_service,
                    db=self.mock_db
                )
            
            assert exc_info.value.status_code == 400
            assert "not currently motivated to expand" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_force_override(self):
        """Test expansion attempt with force override"""
        request = ExpansionAttemptRequest(
            faction_id=self.faction_id,
            target_region_id=self.target_region_id,
            strategy=ExpansionStrategyType.ECONOMIC,
            force_attempt=True  # Force attempt even if not motivated
        )
        
        # Mock faction service
        mock_faction_service = MagicMock()
        mock_faction_response = FactionResponse(
            id=self.faction_id,
            name="Forced Faction",
            description="Test Description",
            status="active",
            properties={},
            created_at="2023-01-01T00:00:00",
            updated_at=None,
            is_active=True,
            hidden_ambition=3,
            hidden_integrity=3,
            hidden_discipline=3,
            hidden_impulsivity=3,
            hidden_pragmatism=3,
            hidden_resilience=3
        )
        mock_faction_service.get_faction_by_id = AsyncMock(return_value=mock_faction_response)
        
        # Mock faction entity
        mock_faction_entity = MagicMock(spec=FactionEntity)
        mock_faction_entity.id = self.faction_id
        mock_faction_entity.name = "Forced Faction"
        mock_faction_entity.is_active = True
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_faction_entity
        
        # Mock expansion service - faction not motivated but forced
        self.mock_expansion_service.should_attempt_expansion.return_value = False
        expansion_result = ExpansionAttempt(
            success=False,
            strategy_used=ExpansionStrategy.ECONOMIC,
            target_region_id=self.target_region_id,
            cost=0.4,
            effectiveness=0.3,
            reason="Forced expansion failed",
            consequences={"market_resistance": True}
        )
        self.mock_expansion_service.attempt_expansion = AsyncMock(return_value=expansion_result)
        
        with patch('backend.systems.faction.routers.expansion_router.FactionService') as mock_faction_service_class:
            mock_faction_service_class.return_value = mock_faction_service
            
            # Should succeed despite faction not being motivated
            response = await attempt_expansion(
                request=request,
                expansion_service=self.mock_expansion_service,
                db=self.mock_db
            )
        
        assert response.success is False
        assert response.strategy_used == ExpansionStrategyType.ECONOMIC
        self.mock_expansion_service.attempt_expansion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_faction_expansion_profile_success(self):
        """Test successful faction expansion profile retrieval"""
        # Mock faction entity
        mock_faction_entity = MagicMock(spec=FactionEntity)
        mock_faction_entity.id = self.faction_id
        mock_faction_entity.name = "Profile Faction"
        mock_faction_entity.is_active = True
        mock_faction_entity.get_hidden_attributes.return_value = {
            "hidden_ambition": 5,
            "hidden_integrity": 2,
            "hidden_discipline": 4,
            "hidden_impulsivity": 3,
            "hidden_pragmatism": 4,
            "hidden_resilience": 3
        }
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_faction_entity
        
        # Mock expansion service methods
        self.mock_expansion_service.determine_expansion_strategy.return_value = ExpansionStrategy.MILITARY
        self.mock_expansion_service.get_expansion_aggressiveness.return_value = 0.7
        self.mock_expansion_service.should_attempt_expansion.return_value = True
        
        # Execute endpoint
        response = await get_faction_expansion_profile(
            faction_id=self.faction_id,
            expansion_service=self.mock_expansion_service,
            db=self.mock_db
        )
        
        # Verify response
        assert response.faction_id == self.faction_id
        assert response.faction_name == "Profile Faction"
        assert response.primary_strategy == ExpansionStrategyType.MILITARY
        assert response.aggressiveness == 0.7
        assert response.should_expand is True
        assert "military" in response.strategy_scores
        assert "economic" in response.strategy_scores
        assert "cultural" in response.strategy_scores
        assert len(response.hidden_attributes) == 6
    
    @pytest.mark.asyncio
    async def test_get_faction_expansion_profile_not_found(self):
        """Test expansion profile for non-existent faction"""
        # Mock database query returning None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_faction_expansion_profile(
                faction_id=self.faction_id,
                expansion_service=self.mock_expansion_service,
                db=self.mock_db
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_region_expansion_opportunities_success(self):
        """Test successful region expansion opportunities retrieval"""
        # Mock factions
        mock_factions = []
        for i in range(3):
            faction = MagicMock(spec=FactionEntity)
            faction.id = uuid4()
            faction.name = f"Faction {i+1}"
            faction.is_active = True
            faction.get_hidden_attributes.return_value = {
                "hidden_ambition": 3 + i,
                "hidden_integrity": 3,
                "hidden_discipline": 3,
                "hidden_impulsivity": 3,
                "hidden_pragmatism": 3,
                "hidden_resilience": 3
            }
            mock_factions.append(faction)
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = mock_factions
        
        # Mock expansion service methods
        self.mock_expansion_service.determine_expansion_strategy.side_effect = [
            ExpansionStrategy.MILITARY,
            ExpansionStrategy.ECONOMIC,
            ExpansionStrategy.CULTURAL
        ]
        self.mock_expansion_service.get_expansion_aggressiveness.side_effect = [0.8, 0.6, 0.4]
        
        # Execute endpoint
        response = await get_region_expansion_opportunities(
            region_id=self.target_region_id,
            max_factions=5,
            expansion_service=self.mock_expansion_service,
            db=self.mock_db
        )
        
        # Verify response
        assert response.region_id == self.target_region_id
        assert len(response.opportunities) == 3
        assert response.total_factions_analyzed == 3
        
        # Verify opportunities are sorted by likelihood (highest first)
        likelihoods = [opp.likelihood for opp in response.opportunities]
        assert likelihoods == sorted(likelihoods, reverse=True)
        
        # Verify first opportunity has highest aggressiveness
        assert response.opportunities[0].aggressiveness == 0.8
    
    @pytest.mark.asyncio
    async def test_simulate_bulk_expansion_success(self):
        """Test successful bulk expansion simulation"""
        request = BulkExpansionSimulationRequest(
            faction_ids=[self.faction_id],
            simulation_steps=2,
            allow_concurrent_expansion=True
        )
        
        # Mock faction entity
        mock_faction_entity = MagicMock(spec=FactionEntity)
        mock_faction_entity.id = self.faction_id
        mock_faction_entity.name = "Simulation Faction"
        mock_faction_entity.is_active = True
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.all.return_value = [mock_faction_entity]
        
        # Mock expansion service
        self.mock_expansion_service.should_attempt_expansion.return_value = True
        expansion_result = ExpansionAttempt(
            success=True,
            strategy_used=ExpansionStrategy.MILITARY,
            target_region_id=uuid4(),
            cost=0.8,
            effectiveness=0.7,
            reason="Simulation conquest",
            consequences={"test": "value"}
        )
        self.mock_expansion_service.attempt_expansion = AsyncMock(return_value=expansion_result)
        
        # Execute endpoint
        response = await simulate_bulk_expansion(
            request=request,
            expansion_service=self.mock_expansion_service,
            db=self.mock_db
        )
        
        # Verify response
        assert response.steps_completed == 2
        assert response.total_attempts == 2  # 2 steps * 1 faction
        assert response.successful_attempts == 2
        assert len(response.expansion_results) == 2
        assert str(self.faction_id) in response.final_faction_territories
        assert len(response.final_faction_territories[str(self.faction_id)]) == 2
    
    @pytest.mark.asyncio
    async def test_simulate_bulk_expansion_missing_faction(self):
        """Test bulk simulation with missing faction"""
        missing_faction_id = uuid4()
        request = BulkExpansionSimulationRequest(
            faction_ids=[self.faction_id, missing_faction_id],
            simulation_steps=1,
            allow_concurrent_expansion=True
        )
        
        # Mock database query returning only one faction
        mock_faction_entity = MagicMock(spec=FactionEntity)
        mock_faction_entity.id = self.faction_id
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [mock_faction_entity]
        
        # Should raise HTTPException for missing faction
        with pytest.raises(HTTPException) as exc_info:
            await simulate_bulk_expansion(
                request=request,
                expansion_service=self.mock_expansion_service,
                db=self.mock_db
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail)
        assert str(missing_faction_id) in str(exc_info.value.detail)


class TestExpansionRouterIntegration:
    """Integration tests for expansion router"""
    
    @pytest.mark.asyncio
    async def test_expansion_router_dependency_injection(self):
        """Test that router properly injects dependencies"""
        # This test verifies the dependency injection pattern used in the router
        # In a real test environment, this would use the actual FastAPI test client
        
        # Mock the dependencies
        mock_db = MagicMock()
        mock_expansion_service = MagicMock()
        
        # Test that the router can handle dependency injection
        assert callable(get_faction_expansion_profile)
        assert callable(attempt_expansion)
        assert callable(get_region_expansion_opportunities)
        assert callable(simulate_bulk_expansion)
        
        # Verify router configuration
        assert expansion_router.prefix == "/expansion"
        assert "faction-expansion" in expansion_router.tags


if __name__ == "__main__":
    pytest.main([__file__]) 