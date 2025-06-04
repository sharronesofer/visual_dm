"""
Tests for Faction Expansion Service

Comprehensive test suite for faction expansion strategies and mechanics.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from typing import Dict, Any

from backend.systems.faction.services.expansion_service import (
    FactionExpansionService,
    ExpansionStrategy,
    ExpansionAttempt,
    get_faction_expansion_service
)
from backend.infrastructure.models.faction.models import FactionEntity


class TestFactionExpansionService:
    """Test suite for FactionExpansionService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.expansion_service = FactionExpansionService()
        self.mock_faction = self._create_mock_faction()
        self.target_region_id = uuid4()
    
    def _create_mock_faction(self, **kwargs) -> FactionEntity:
        """Create a mock faction with default attributes"""
        defaults = {
            "id": uuid4(),
            "name": "Test Faction",
            "hidden_ambition": 3,
            "hidden_integrity": 3,
            "hidden_discipline": 3,
            "hidden_impulsivity": 3,
            "hidden_pragmatism": 3,
            "hidden_resilience": 3
        }
        defaults.update(kwargs)
        
        faction = MagicMock(spec=FactionEntity)
        faction.id = defaults["id"]
        faction.name = defaults["name"]
        
        # Mock get_hidden_attributes method
        faction.get_hidden_attributes.return_value = {
            "hidden_ambition": defaults["hidden_ambition"],
            "hidden_integrity": defaults["hidden_integrity"],
            "hidden_discipline": defaults["hidden_discipline"],
            "hidden_impulsivity": defaults["hidden_impulsivity"],
            "hidden_pragmatism": defaults["hidden_pragmatism"],
            "hidden_resilience": defaults["hidden_resilience"]
        }
        
        return faction
    
    def test_determine_expansion_strategy_military(self):
        """Test military strategy selection for aggressive, low-integrity factions"""
        # High ambition, low integrity, high impulsivity should favor military
        faction = self._create_mock_faction(
            hidden_ambition=6,
            hidden_integrity=0,
            hidden_impulsivity=6
        )
        
        with patch('random.randint', return_value=0):  # Remove randomness
            strategy = self.expansion_service.determine_expansion_strategy(faction)
        
        assert strategy == ExpansionStrategy.MILITARY
    
    def test_determine_expansion_strategy_economic(self):
        """Test economic strategy selection for pragmatic, disciplined factions"""
        # High pragmatism, high discipline, moderate ambition should favor economic
        faction = self._create_mock_faction(
            hidden_pragmatism=6,
            hidden_discipline=6,
            hidden_ambition=4
        )
        
        with patch('random.randint', return_value=0):  # Remove randomness
            strategy = self.expansion_service.determine_expansion_strategy(faction)
        
        assert strategy == ExpansionStrategy.ECONOMIC
    
    def test_determine_expansion_strategy_cultural(self):
        """Test cultural strategy selection for honorable, patient factions"""
        # High integrity, low impulsivity, high resilience should favor cultural
        faction = self._create_mock_faction(
            hidden_integrity=6,
            hidden_impulsivity=0,
            hidden_resilience=6
        )
        
        with patch('random.randint', return_value=0):  # Remove randomness
            strategy = self.expansion_service.determine_expansion_strategy(faction)
        
        assert strategy == ExpansionStrategy.CULTURAL
    
    def test_get_expansion_aggressiveness_high(self):
        """Test high aggressiveness calculation"""
        faction = self._create_mock_faction(
            hidden_ambition=6,
            hidden_impulsivity=6,
            hidden_integrity=0,
            hidden_resilience=6
        )
        
        aggressiveness = self.expansion_service.get_expansion_aggressiveness(faction)
        
        # Should be close to 1.0 for max aggressive attributes
        assert aggressiveness >= 0.8
        assert aggressiveness <= 1.0
    
    def test_get_expansion_aggressiveness_low(self):
        """Test low aggressiveness calculation"""
        faction = self._create_mock_faction(
            hidden_ambition=0,
            hidden_impulsivity=0,
            hidden_integrity=6,
            hidden_resilience=0
        )
        
        aggressiveness = self.expansion_service.get_expansion_aggressiveness(faction)
        
        # Should be close to 0.0 for least aggressive attributes
        assert aggressiveness >= 0.0
        assert aggressiveness <= 0.2
    
    def test_should_attempt_expansion_true(self):
        """Test expansion attempt decision for aggressive faction"""
        faction = self._create_mock_faction(
            hidden_ambition=6,
            hidden_impulsivity=6
        )
        
        with patch('random.random', return_value=0.5):
            should_expand = self.expansion_service.should_attempt_expansion(faction)
        
        assert should_expand is True
    
    def test_should_attempt_expansion_false(self):
        """Test expansion attempt decision for peaceful faction"""
        faction = self._create_mock_faction(
            hidden_ambition=0,
            hidden_impulsivity=0
        )
        
        with patch('random.random', return_value=0.5):
            should_expand = self.expansion_service.should_attempt_expansion(faction)
        
        assert should_expand is False
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_military_success(self):
        """Test successful military expansion"""
        faction = self._create_mock_faction(
            hidden_ambition=6,
            hidden_discipline=6,
            hidden_resilience=6
        )
        
        # Mock territory service
        with patch.object(self.expansion_service, 'territory_service') as mock_territory:
            mock_territory.claim_territory = AsyncMock()
            
            # Mock successful roll
            with patch('random.uniform', return_value=0.8):
                result = await self.expansion_service.attempt_expansion(
                    faction, self.target_region_id, ExpansionStrategy.MILITARY
                )
        
        assert result.success is True
        assert result.strategy_used == ExpansionStrategy.MILITARY
        assert result.target_region_id == self.target_region_id
        assert result.effectiveness > 0.6
        assert "successfully conquered" in result.reason.lower()
        
        # Verify territory service was called
        mock_territory.claim_territory.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_military_failure(self):
        """Test failed military expansion"""
        faction = self._create_mock_faction(
            hidden_ambition=1,
            hidden_discipline=1,
            hidden_resilience=1
        )
        
        # Mock failed roll
        with patch('random.uniform', return_value=0.3):
            result = await self.expansion_service.attempt_expansion(
                faction, self.target_region_id, ExpansionStrategy.MILITARY
            )
        
        assert result.success is False
        assert result.strategy_used == ExpansionStrategy.MILITARY
        assert result.effectiveness <= 0.6
        assert "failed" in result.reason.lower()
        assert "military_casualties" in result.consequences
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_economic_success(self):
        """Test successful economic expansion"""
        faction = self._create_mock_faction(
            hidden_pragmatism=6,
            hidden_discipline=6,
            hidden_ambition=5
        )
        
        # Mock influence service
        with patch.object(self.expansion_service, 'influence_service') as mock_influence:
            mock_influence.update_region_influence = AsyncMock()
            
            # Mock successful market conditions
            with patch('random.uniform', return_value=0.9):
                result = await self.expansion_service.attempt_expansion(
                    faction, self.target_region_id, ExpansionStrategy.ECONOMIC
                )
        
        assert result.success is True
        assert result.strategy_used == ExpansionStrategy.ECONOMIC
        assert result.effectiveness > 0.5
        assert "economic dominance" in result.reason.lower()
        assert "economic_dependency" in result.consequences
        
        # Verify influence service was called
        mock_influence.update_region_influence.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_economic_failure(self):
        """Test failed economic expansion"""
        faction = self._create_mock_faction(
            hidden_pragmatism=1,
            hidden_discipline=1,
            hidden_ambition=1
        )
        
        # Mock poor market conditions
        with patch('random.uniform', return_value=0.6):
            result = await self.expansion_service.attempt_expansion(
                faction, self.target_region_id, ExpansionStrategy.ECONOMIC
            )
        
        assert result.success is False
        assert result.strategy_used == ExpansionStrategy.ECONOMIC
        assert result.effectiveness <= 0.5
        assert "market resistance" in result.reason.lower()
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_cultural_success(self):
        """Test successful cultural expansion"""
        faction = self._create_mock_faction(
            hidden_integrity=6,
            hidden_impulsivity=0,
            hidden_resilience=6
        )
        
        # Mock influence service
        with patch.object(self.expansion_service, 'influence_service') as mock_influence:
            mock_influence.update_region_influence = AsyncMock()
            
            # Mock good cultural receptiveness
            with patch('random.uniform', return_value=0.8):
                result = await self.expansion_service.attempt_expansion(
                    faction, self.target_region_id, ExpansionStrategy.CULTURAL
                )
        
        assert result.success is True
        assert result.strategy_used == ExpansionStrategy.CULTURAL
        assert result.effectiveness > 0.45
        assert "cultural influence" in result.reason.lower()
        assert "npc_conversion_rate" in result.consequences
        
        # Verify influence service was called
        mock_influence.update_region_influence.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_cultural_failure(self):
        """Test failed cultural expansion"""
        faction = self._create_mock_faction(
            hidden_integrity=1,
            hidden_impulsivity=6,
            hidden_resilience=1
        )
        
        # Mock poor cultural receptiveness
        with patch('random.uniform', return_value=0.4):
            result = await self.expansion_service.attempt_expansion(
                faction, self.target_region_id, ExpansionStrategy.CULTURAL
            )
        
        assert result.success is False
        assert result.strategy_used == ExpansionStrategy.CULTURAL
        assert result.effectiveness <= 0.45
        assert "local resistance" in result.reason.lower()
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_auto_strategy(self):
        """Test expansion with automatic strategy selection"""
        faction = self._create_mock_faction(
            hidden_ambition=6,
            hidden_integrity=0,
            hidden_impulsivity=6,
            hidden_discipline=6,  # Add high discipline for better military coordination
            hidden_resilience=6   # Add high resilience for military endurance
        )
        
        # Mock territory service for military expansion
        with patch.object(self.expansion_service, 'territory_service') as mock_territory:
            mock_territory.claim_territory = AsyncMock()
            
            with patch('random.randint', return_value=0):  # Remove strategy randomness
                with patch('random.uniform', return_value=0.9):  # Ensure success with higher roll
                    result = await self.expansion_service.attempt_expansion(
                        faction, self.target_region_id
                    )
        
        # Should automatically choose military strategy for aggressive faction
        assert result.strategy_used == ExpansionStrategy.MILITARY
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_attempt_expansion_invalid_strategy(self):
        """Test expansion with invalid strategy raises error"""
        faction = self._create_mock_faction()
        
        # Create a mock strategy that's not in the enum
        invalid_strategy = MagicMock()
        invalid_strategy.value = "invalid"
        
        with pytest.raises(ValueError, match="Unknown expansion strategy"):
            await self.expansion_service.attempt_expansion(
                faction, self.target_region_id, invalid_strategy
            )


class TestExpansionStrategy:
    """Test ExpansionStrategy enum"""
    
    def test_expansion_strategy_values(self):
        """Test that expansion strategy enum has correct values"""
        assert ExpansionStrategy.MILITARY.value == "military"
        assert ExpansionStrategy.ECONOMIC.value == "economic"
        assert ExpansionStrategy.CULTURAL.value == "cultural"


class TestExpansionAttempt:
    """Test ExpansionAttempt dataclass"""
    
    def test_expansion_attempt_creation(self):
        """Test creating an ExpansionAttempt"""
        target_id = uuid4()
        consequences = {"test": "value"}
        
        attempt = ExpansionAttempt(
            success=True,
            strategy_used=ExpansionStrategy.MILITARY,
            target_region_id=target_id,
            cost=0.8,
            effectiveness=0.75,
            reason="Test reason",
            consequences=consequences
        )
        
        assert attempt.success is True
        assert attempt.strategy_used == ExpansionStrategy.MILITARY
        assert attempt.target_region_id == target_id
        assert attempt.cost == 0.8
        assert attempt.effectiveness == 0.75
        assert attempt.reason == "Test reason"
        assert attempt.consequences == consequences


class TestExpansionServiceFactory:
    """Test expansion service factory function"""
    
    def test_get_faction_expansion_service(self):
        """Test that factory returns a FactionExpansionService instance"""
        service = get_faction_expansion_service()
        assert isinstance(service, FactionExpansionService)
    
    def test_get_faction_expansion_service_new_instance(self):
        """Test that factory returns new instances"""
        service1 = get_faction_expansion_service()
        service2 = get_faction_expansion_service()
        assert service1 is not service2


class TestExpansionServiceIntegration:
    """Integration tests for expansion service with other systems"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        self.expansion_service = FactionExpansionService()
    
    @pytest.mark.asyncio
    async def test_military_expansion_integration(self):
        """Test military expansion integrates with territory service"""
        faction = MagicMock(spec=FactionEntity)
        faction.id = uuid4()
        faction.name = "Test Military Faction"
        faction.get_hidden_attributes.return_value = {
            "hidden_ambition": 6,
            "hidden_integrity": 2,
            "hidden_discipline": 5,
            "hidden_impulsivity": 4,
            "hidden_pragmatism": 3,
            "hidden_resilience": 5
        }
        
        target_region_id = uuid4()
        
        # Mock territory service method
        with patch.object(self.expansion_service, 'territory_service') as mock_territory:
            mock_territory.claim_territory = AsyncMock()
            
            # Ensure successful military expansion
            with patch('random.uniform', return_value=0.9):
                result = await self.expansion_service._attempt_military_expansion(
                    faction, target_region_id
                )
        
        assert result.success is True
        
        # Verify territory service was called with correct parameters
        mock_territory.claim_territory.assert_called_once()
        call_args = mock_territory.claim_territory.call_args
        assert call_args[1]['faction_id'] == faction.id
        assert call_args[1]['faction_name'] == faction.name
        assert call_args[1]['claim_method'] == "military_conquest"
        assert 'expansion_strategy' in call_args[1]['claim_details']
    
    @pytest.mark.asyncio
    async def test_economic_expansion_integration(self):
        """Test economic expansion integrates with influence service"""
        faction = MagicMock(spec=FactionEntity)
        faction.id = uuid4()
        faction.get_hidden_attributes.return_value = {
            "hidden_ambition": 4,
            "hidden_integrity": 4,
            "hidden_discipline": 6,
            "hidden_impulsivity": 2,
            "hidden_pragmatism": 6,
            "hidden_resilience": 4
        }
        
        target_region_id = uuid4()
        
        # Mock influence service method
        with patch.object(self.expansion_service, 'influence_service') as mock_influence:
            mock_influence.update_region_influence = AsyncMock()
            
            # Ensure successful economic expansion
            with patch('random.uniform', return_value=0.8):
                result = await self.expansion_service._attempt_economic_expansion(
                    faction, target_region_id
                )
        
        assert result.success is True
        
        # Verify influence service was called with correct parameters
        mock_influence.update_region_influence.assert_called_once()
        call_args = mock_influence.update_region_influence.call_args
        assert call_args[1]['faction_id'] == faction.id
        assert call_args[1]['region_id'] == target_region_id
        assert call_args[1]['influence_type'] == "economic"
    
    @pytest.mark.asyncio
    async def test_cultural_expansion_integration(self):
        """Test cultural expansion integrates with influence service"""
        faction = MagicMock(spec=FactionEntity)
        faction.id = uuid4()
        faction.get_hidden_attributes.return_value = {
            "hidden_ambition": 3,
            "hidden_integrity": 6,
            "hidden_discipline": 4,
            "hidden_impulsivity": 1,
            "hidden_pragmatism": 3,
            "hidden_resilience": 6
        }
        
        target_region_id = uuid4()
        
        # Mock influence service method
        with patch.object(self.expansion_service, 'influence_service') as mock_influence:
            mock_influence.update_region_influence = AsyncMock()
            
            # Ensure successful cultural expansion
            with patch('random.uniform', return_value=0.7):
                result = await self.expansion_service._attempt_cultural_expansion(
                    faction, target_region_id
                )
        
        assert result.success is True
        
        # Verify influence service was called with correct parameters
        mock_influence.update_region_influence.assert_called_once()
        call_args = mock_influence.update_region_influence.call_args
        assert call_args[1]['faction_id'] == faction.id
        assert call_args[1]['region_id'] == target_region_id
        assert call_args[1]['influence_type'] == "cultural"


if __name__ == "__main__":
    pytest.main([__file__]) 