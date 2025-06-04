"""
Tests for Memory Cross-System Integration Service
-----------------------------------------------

Comprehensive test suite for memory-driven cross-system behavioral modifications
affecting economy, factions, combat, and social systems.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import List, Dict, Any

from backend.systems.memory.services.cross_system_integration import (
    MemoryCrossSystemIntegrator,
    EconomicBehaviorModification,
    FactionBehaviorModification,
    CombatBehaviorModification,
    SocialBehaviorModification
)
from backend.systems.memory.services.memory_behavior_influence import (
    MemoryBehaviorInfluenceService,
    BehaviorModifier,
    BehaviorInfluenceType,
    TrustCalculation
)


@pytest.fixture
def mock_behavior_influence_service():
    """Create a mock behavior influence service for testing"""
    service = Mock(spec=MemoryBehaviorInfluenceService)
    service.entity_id = "test_npc_001"
    service.entity_type = "npc"
    service.generate_behavior_modifiers = AsyncMock()
    service.calculate_faction_bias = AsyncMock()
    service.calculate_trust_level = AsyncMock()
    return service


@pytest.fixture
def cross_system_integrator(mock_behavior_influence_service):
    """Create a cross-system integrator for testing"""
    return MemoryCrossSystemIntegrator(mock_behavior_influence_service)


@pytest.fixture
def sample_behavior_modifiers():
    """Create sample behavior modifiers for testing"""
    return [
        BehaviorModifier(
            influence_type=BehaviorInfluenceType.RISK_ASSESSMENT,
            modifier_value=0.6,
            confidence=0.8,
            source_memories=["mem_001"],
            context="high_risk_situation"
        ),
        BehaviorModifier(
            influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
            modifier_value=0.7,
            confidence=0.9,
            source_memories=["mem_002"],
            context="anger_towards_betrayer"
        ),
        BehaviorModifier(
            influence_type=BehaviorInfluenceType.TRUST,
            modifier_value=-0.5,
            confidence=0.7,
            source_memories=["mem_003"],
            context="trust_broken"
        )
    ]


class TestEconomicBehaviorModifications:
    """Test economic behavior modifications from memory analysis"""
    
    @pytest.mark.asyncio
    async def test_get_economic_behavior_modifications_default(self, cross_system_integrator, mock_behavior_influence_service):
        """Test economic behavior modifications with default values"""
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = []
        
        result = await cross_system_integrator.get_economic_behavior_modifications()
        
        assert isinstance(result, EconomicBehaviorModification)
        assert result.base_price_modifier == 1.0  # Default
        assert 0.0 <= result.trade_willingness <= 1.0
        assert result.risk_premium >= 0.0
        assert isinstance(result.preferred_customers, list)
        assert isinstance(result.blacklisted_customers, list)
    
    @pytest.mark.asyncio
    async def test_get_economic_behavior_modifications_risk_averse(self, cross_system_integrator, mock_behavior_influence_service):
        """Test economic behavior modifications with high risk assessment"""
        risk_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.RISK_ASSESSMENT,
            modifier_value=0.8,  # High risk
            confidence=0.9,
            source_memories=["mem_risk"],
            context="high_risk_trading"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [risk_modifier]
        
        result = await cross_system_integrator.get_economic_behavior_modifications()
        
        assert result.risk_premium > 0.0  # Should add risk premium
        assert result.trade_willingness < 0.7  # Should reduce willingness
        assert 0.5 <= result.base_price_modifier <= 2.0  # Within bounds
    
    @pytest.mark.asyncio
    async def test_get_economic_behavior_modifications_emotional_anger(self, cross_system_integrator, mock_behavior_influence_service):
        """Test economic behavior modifications with anger emotion"""
        anger_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
            modifier_value=0.7,
            confidence=0.8,
            source_memories=["mem_anger"],
            context="anger towards customer"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [anger_modifier]
        
        result = await cross_system_integrator.get_economic_behavior_modifications()
        
        # Anger should increase prices and reduce trade willingness
        assert result.base_price_modifier > 1.0
        assert result.trade_willingness < 0.7
    
    @pytest.mark.asyncio
    async def test_get_economic_behavior_modifications_emotional_fear(self, cross_system_integrator, mock_behavior_influence_service):
        """Test economic behavior modifications with fear emotion"""
        fear_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
            modifier_value=0.6,
            confidence=0.8,
            source_memories=["mem_fear"],
            context="fear of economic loss"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [fear_modifier]
        
        result = await cross_system_integrator.get_economic_behavior_modifications()
        
        # Fear should reduce trade willingness and increase risk premium
        assert result.trade_willingness < 0.7
        assert result.risk_premium > 0.0
    
    @pytest.mark.asyncio
    async def test_get_economic_behavior_modifications_emotional_joy(self, cross_system_integrator, mock_behavior_influence_service):
        """Test economic behavior modifications with joy emotion"""
        joy_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
            modifier_value=0.5,
            confidence=0.7,
            source_memories=["mem_joy"],
            context="joy from successful trade"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [joy_modifier]
        
        result = await cross_system_integrator.get_economic_behavior_modifications()
        
        # Joy should increase trade willingness and potentially reduce prices
        assert result.trade_willingness > 0.7
        assert result.base_price_modifier <= 1.0  # Better deals when happy


class TestFactionBehaviorModifications:
    """Test faction-related behavior modifications from memory analysis"""
    
    @pytest.mark.asyncio
    async def test_get_faction_behavior_modifications_neutral(self, cross_system_integrator, mock_behavior_influence_service):
        """Test faction behavior modifications with neutral faction bias"""
        known_factions = ["red_hawks", "blue_shields", "green_cloaks"]
        mock_behavior_influence_service.calculate_faction_bias.return_value = 0.0  # Neutral
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = []
        
        result = await cross_system_integrator.get_faction_behavior_modifications(known_factions)
        
        assert isinstance(result, FactionBehaviorModification)
        assert len(result.faction_loyalties) == len(known_factions)
        assert len(result.diplomatic_stance) == len(known_factions)
        
        # All should be neutral
        for faction_id in known_factions:
            assert result.faction_loyalties[faction_id] == 0.0
            assert result.diplomatic_stance[faction_id] == "neutral"
        
        assert 0.0 <= result.rebellion_likelihood <= 1.0
        assert 0.0 <= result.influence_resistance <= 1.0
    
    @pytest.mark.asyncio
    async def test_get_faction_behavior_modifications_high_loyalty(self, cross_system_integrator, mock_behavior_influence_service):
        """Test faction behavior modifications with high faction loyalty"""
        known_factions = ["red_hawks"]
        mock_behavior_influence_service.calculate_faction_bias.return_value = 0.8  # High loyalty
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = []
        
        result = await cross_system_integrator.get_faction_behavior_modifications(known_factions)
        
        assert result.faction_loyalties["red_hawks"] == 0.8
        assert result.diplomatic_stance["red_hawks"] == "allied"
    
    @pytest.mark.asyncio
    async def test_get_faction_behavior_modifications_hostile(self, cross_system_integrator, mock_behavior_influence_service):
        """Test faction behavior modifications with hostile faction relationship"""
        known_factions = ["red_hawks"]
        mock_behavior_influence_service.calculate_faction_bias.return_value = -0.8  # Hostile
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = []
        
        result = await cross_system_integrator.get_faction_behavior_modifications(known_factions)
        
        assert result.faction_loyalties["red_hawks"] == -0.8
        assert result.diplomatic_stance["red_hawks"] == "hostile"
    
    @pytest.mark.asyncio
    async def test_get_faction_behavior_modifications_with_anger(self, cross_system_integrator, mock_behavior_influence_service):
        """Test faction behavior modifications with anger emotion affecting rebellion"""
        known_factions = ["red_hawks"]
        mock_behavior_influence_service.calculate_faction_bias.return_value = 0.0
        
        anger_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
            modifier_value=0.7,
            confidence=0.8,
            source_memories=["mem_anger"],
            context="anger towards authority"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [anger_modifier]
        
        result = await cross_system_integrator.get_faction_behavior_modifications(known_factions)
        
        # Anger should increase rebellion likelihood and influence resistance
        assert result.rebellion_likelihood > 0.1  # Above base
        assert result.influence_resistance > 0.5  # Above base
    
    @pytest.mark.asyncio
    async def test_get_faction_behavior_modifications_with_fear(self, cross_system_integrator, mock_behavior_influence_service):
        """Test faction behavior modifications with fear emotion affecting compliance"""
        known_factions = ["red_hawks"]
        mock_behavior_influence_service.calculate_faction_bias.return_value = 0.0
        
        fear_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
            modifier_value=0.6,
            confidence=0.8,
            source_memories=["mem_fear"],
            context="fear of faction retaliation"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [fear_modifier]
        
        result = await cross_system_integrator.get_faction_behavior_modifications(known_factions)
        
        # Fear should reduce rebellion likelihood and influence resistance
        assert result.rebellion_likelihood < 0.1  # Below base
        assert result.influence_resistance < 0.5  # Below base


class TestCombatBehaviorModifications:
    """Test combat behavior modifications from memory analysis"""
    
    @pytest.mark.asyncio
    async def test_get_combat_behavior_modifications_default(self, cross_system_integrator, mock_behavior_influence_service):
        """Test combat behavior modifications with default values"""
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = []
        mock_behavior_influence_service.calculate_trust_level.return_value = TrustCalculation(
            entity_id="ally_001",
            trust_level=0.5,
            trust_change=0.0,
            contributing_memories=[],
            confidence=0.0
        )
        
        result = await cross_system_integrator.get_combat_behavior_modifications()
        
        assert isinstance(result, CombatBehaviorModification)
        assert result.aggression_modifier == 1.0  # Default
        assert 0.0 <= result.flee_threshold <= 1.0
        assert result.combat_caution >= 0.0
        assert isinstance(result.ally_recognition, dict)
        assert isinstance(result.enemy_priority, dict)
        assert isinstance(result.berserker_triggers, list)
    
    @pytest.mark.asyncio
    async def test_get_combat_behavior_modifications_with_trauma(self, cross_system_integrator, mock_behavior_influence_service):
        """Test combat behavior modifications with trauma affecting combat"""
        trauma_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
            modifier_value=0.8,
            confidence=0.9,
            source_memories=["mem_trauma"],
            context="fear from battle trauma"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [trauma_modifier]
        mock_behavior_influence_service.calculate_trust_level.return_value = TrustCalculation(
            entity_id="ally_001",
            trust_level=0.5,
            trust_change=0.0,
            contributing_memories=[],
            confidence=0.0
        )
        
        result = await cross_system_integrator.get_combat_behavior_modifications()
        
        # Trauma should reduce aggression and increase flee threshold
        assert result.aggression_modifier < 1.0
        assert result.flee_threshold > 0.3  # Higher than default
        assert result.combat_caution > 0.5
    
    @pytest.mark.asyncio
    async def test_get_combat_behavior_modifications_with_anger(self, cross_system_integrator, mock_behavior_influence_service):
        """Test combat behavior modifications with anger increasing aggression"""
        anger_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
            modifier_value=0.7,
            confidence=0.8,
            source_memories=["mem_anger"],
            context="anger towards enemies"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [anger_modifier]
        mock_behavior_influence_service.calculate_trust_level.return_value = TrustCalculation(
            entity_id="ally_001",
            trust_level=0.5,
            trust_change=0.0,
            contributing_memories=[],
            confidence=0.0
        )
        
        result = await cross_system_integrator.get_combat_behavior_modifications()
        
        # Anger should increase aggression and reduce flee threshold
        assert result.aggression_modifier > 1.0
        assert result.flee_threshold < 0.3
    
    @pytest.mark.asyncio
    async def test_get_combat_behavior_modifications_with_high_trust_ally(self, cross_system_integrator, mock_behavior_influence_service):
        """Test combat behavior modifications with trusted ally"""
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = []
        mock_behavior_influence_service.calculate_trust_level.return_value = TrustCalculation(
            entity_id="trusted_ally",
            trust_level=0.9,
            trust_change=0.4,
            contributing_memories=[("mem_help", 0.8)],
            confidence=0.9
        )
        
        result = await cross_system_integrator.get_combat_behavior_modifications("trusted_ally")
        
        # High trust should be reflected in ally recognition
        assert "trusted_ally" in result.ally_recognition
        assert result.ally_recognition["trusted_ally"] == 0.9


class TestSocialBehaviorModifications:
    """Test social behavior modifications from memory analysis"""
    
    @pytest.mark.asyncio
    async def test_get_social_behavior_modifications_default(self, cross_system_integrator, mock_behavior_influence_service):
        """Test social behavior modifications with default values"""
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = []
        
        result = await cross_system_integrator.get_social_behavior_modifications()
        
        assert isinstance(result, SocialBehaviorModification)
        assert 0.0 <= result.social_openness <= 1.0
        assert isinstance(result.conversation_topics, dict)
        assert isinstance(result.relationship_priorities, dict)
        assert isinstance(result.rumor_credibility, dict)
        assert result.social_influence >= 0.0
    
    @pytest.mark.asyncio
    async def test_get_social_behavior_modifications_with_trust_issues(self, cross_system_integrator, mock_behavior_influence_service):
        """Test social behavior modifications with trust issues affecting openness"""
        trust_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.TRUST,
            modifier_value=-0.6,  # Low trust
            confidence=0.8,
            source_memories=["mem_betrayal"],
            context="trust_broken_by_betrayal"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [trust_modifier]
        
        result = await cross_system_integrator.get_social_behavior_modifications()
        
        # Low trust should reduce social openness
        assert result.social_openness < 0.5
    
    @pytest.mark.asyncio
    async def test_get_social_behavior_modifications_with_positive_emotions(self, cross_system_integrator, mock_behavior_influence_service):
        """Test social behavior modifications with positive emotions increasing openness"""
        joy_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
            modifier_value=0.7,
            confidence=0.8,
            source_memories=["mem_joy"],
            context="joy from social success"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [joy_modifier]
        
        result = await cross_system_integrator.get_social_behavior_modifications()
        
        # Joy should increase social openness and influence
        assert result.social_openness > 0.5
        assert result.social_influence > 0.5


class TestEntityTrustCalculation:
    """Test entity trust calculation for specific contexts"""
    
    @pytest.mark.asyncio
    async def test_calculate_entity_trust_for_context(self, cross_system_integrator, mock_behavior_influence_service):
        """Test calculating trust for specific entity and context"""
        expected_trust = TrustCalculation(
            entity_id="player_123",
            trust_level=0.8,
            trust_change=0.3,
            contributing_memories=[("mem_help", 0.8)],
            confidence=0.9
        )
        mock_behavior_influence_service.calculate_trust_level.return_value = expected_trust
        
        result = await cross_system_integrator.calculate_entity_trust_for_context("player_123", "trade")
        
        assert result == expected_trust
        mock_behavior_influence_service.calculate_trust_level.assert_called_once_with("player_123", "trade")


class TestOpportunityRecognition:
    """Test opportunity recognition factors from memory analysis"""
    
    @pytest.mark.asyncio
    async def test_get_opportunity_recognition_factors_no_memories(self, cross_system_integrator, mock_behavior_influence_service):
        """Test opportunity recognition with no relevant memories"""
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = []
        
        result = await cross_system_integrator.get_opportunity_recognition_factors("trade")
        
        assert isinstance(result, dict)
        assert "base_recognition" in result
        assert result["base_recognition"] == 0.5  # Default
    
    @pytest.mark.asyncio
    async def test_get_opportunity_recognition_factors_with_positive_memories(self, cross_system_integrator, mock_behavior_influence_service):
        """Test opportunity recognition with positive past experiences"""
        opportunity_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.OPPORTUNITY_RECOGNITION,
            modifier_value=0.7,
            confidence=0.8,
            source_memories=["mem_success"],
            context="successful_trade_opportunity"
        )
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [opportunity_modifier]
        
        result = await cross_system_integrator.get_opportunity_recognition_factors("trade")
        
        assert result["opportunity_sensitivity"] > 0.5  # Should be enhanced
        assert result["confidence_bonus"] > 0.0


class TestComprehensiveBehaviorProfile:
    """Test comprehensive behavior profile generation"""
    
    @pytest.mark.asyncio
    async def test_get_comprehensive_behavior_profile(self, cross_system_integrator, mock_behavior_influence_service):
        """Test generating a complete behavior profile across all systems"""
        known_factions = ["red_hawks", "blue_shields"]
        
        # Setup mock returns
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = []
        mock_behavior_influence_service.calculate_faction_bias.return_value = 0.0
        mock_behavior_influence_service.calculate_trust_level.return_value = TrustCalculation(
            entity_id="test_entity",
            trust_level=0.5,
            trust_change=0.0,
            contributing_memories=[],
            confidence=0.0
        )
        
        result = await cross_system_integrator.get_comprehensive_behavior_profile(known_factions)
        
        assert isinstance(result, dict)
        assert "economic" in result
        assert "faction" in result
        assert "combat" in result
        assert "social" in result
        assert "entity_id" in result
        assert "timestamp" in result
        
        # Verify each system's modifications are included
        assert isinstance(result["economic"], EconomicBehaviorModification)
        assert isinstance(result["faction"], FactionBehaviorModification)
        assert isinstance(result["combat"], CombatBehaviorModification)
        assert isinstance(result["social"], SocialBehaviorModification)
    
    @pytest.mark.asyncio
    async def test_get_comprehensive_behavior_profile_with_context(self, cross_system_integrator, mock_behavior_influence_service):
        """Test generating behavior profile with specific context"""
        known_factions = ["red_hawks"]
        context = "wartime_scenario"
        
        # Setup mock returns
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = []
        mock_behavior_influence_service.calculate_faction_bias.return_value = 0.0
        mock_behavior_influence_service.calculate_trust_level.return_value = TrustCalculation(
            entity_id="test_entity",
            trust_level=0.5,
            trust_change=0.0,
            contributing_memories=[],
            confidence=0.0
        )
        
        result = await cross_system_integrator.get_comprehensive_behavior_profile(known_factions, context)
        
        assert result["context"] == context
        assert "economic" in result
        assert "faction" in result
        assert "combat" in result
        assert "social" in result


# Integration tests
class TestCrossSystemIntegration:
    """Integration tests for the complete cross-system integration"""
    
    @pytest.mark.asyncio
    async def test_full_integration_workflow(self, cross_system_integrator, mock_behavior_influence_service, sample_behavior_modifiers):
        """Test complete workflow across all systems"""
        known_factions = ["red_hawks", "blue_shields"]
        
        # Setup comprehensive mock returns
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = sample_behavior_modifiers
        mock_behavior_influence_service.calculate_faction_bias.return_value = 0.3  # Slightly positive
        mock_behavior_influence_service.calculate_trust_level.return_value = TrustCalculation(
            entity_id="player_123",
            trust_level=0.7,
            trust_change=0.2,
            contributing_memories=[("mem_help", 0.8)],
            confidence=0.8
        )
        
        # Test each system individually
        economic = await cross_system_integrator.get_economic_behavior_modifications()
        faction = await cross_system_integrator.get_faction_behavior_modifications(known_factions)
        combat = await cross_system_integrator.get_combat_behavior_modifications()
        social = await cross_system_integrator.get_social_behavior_modifications()
        
        # Verify all systems return valid modifications
        assert isinstance(economic, EconomicBehaviorModification)
        assert isinstance(faction, FactionBehaviorModification)
        assert isinstance(combat, CombatBehaviorModification)
        assert isinstance(social, SocialBehaviorModification)
        
        # Test comprehensive profile
        profile = await cross_system_integrator.get_comprehensive_behavior_profile(known_factions)
        
        assert profile["economic"] == economic
        assert profile["faction"] == faction
        assert profile["combat"] == combat
        assert profile["social"] == social
    
    @pytest.mark.asyncio
    async def test_behavior_consistency_across_systems(self, cross_system_integrator, mock_behavior_influence_service):
        """Test that behavior modifications are consistent across systems"""
        # Setup consistent emotional state (fear)
        fear_modifier = BehaviorModifier(
            influence_type=BehaviorInfluenceType.EMOTIONAL_RESPONSE,
            modifier_value=0.8,
            confidence=0.9,
            source_memories=["mem_trauma"],
            context="fear from traumatic experience"
        )
        
        mock_behavior_influence_service.generate_behavior_modifiers.return_value = [fear_modifier]
        mock_behavior_influence_service.calculate_faction_bias.return_value = 0.0
        mock_behavior_influence_service.calculate_trust_level.return_value = TrustCalculation(
            entity_id="test_entity",
            trust_level=0.5,
            trust_change=0.0,
            contributing_memories=[],
            confidence=0.0
        )
        
        # Get modifications from all systems
        economic = await cross_system_integrator.get_economic_behavior_modifications()
        faction = await cross_system_integrator.get_faction_behavior_modifications(["red_hawks"])
        combat = await cross_system_integrator.get_combat_behavior_modifications()
        social = await cross_system_integrator.get_social_behavior_modifications()
        
        # Fear should consistently affect behavior across systems
        # Economic: reduced trade willingness, increased risk premium
        assert economic.trade_willingness < 0.7
        assert economic.risk_premium > 0.0
        
        # Faction: reduced rebellion likelihood (fear of consequences)
        assert faction.rebellion_likelihood < 0.1
        
        # Combat: reduced aggression, higher flee threshold
        assert combat.aggression_modifier < 1.0
        assert combat.flee_threshold > 0.3
        
        # Social: reduced openness
        assert social.social_openness < 0.5 