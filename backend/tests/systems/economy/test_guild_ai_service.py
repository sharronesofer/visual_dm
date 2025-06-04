"""
Test Guild AI Service

This module tests the intelligent guild behavior, autonomous decision-making,
and complete guild system integration with factions and economy.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from uuid import uuid4, UUID
from typing import Dict, Any, List

from backend.systems.economy.services.guild_ai_service import (
    GuildAIService, GuildPersonality, ExpansionStrategy, PricingStrategy,
    ExpansionOption, CompetitionThreat, AllianceProposal, ManipulationPlan
)
from backend.infrastructure.database.economy.advanced_models import MerchantGuildEntity


class TestGuildAIService:
    """Test suite for Guild AI Service functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.guild_ai_service = GuildAIService(self.mock_db_session)
        
        # Create mock guild
        self.mock_guild = Mock(spec=MerchantGuildEntity)
        self.mock_guild.id = uuid4()
        self.mock_guild.name = "Test Merchant Guild"
        self.mock_guild.total_wealth = 10000.0
        self.mock_guild.territory_control = ["region_1", "region_2"]
        self.mock_guild.controlled_markets = ["market_1", "market_2"]
        self.mock_guild.market_share = 0.4
        self.mock_guild.pricing_influence = 0.6
        self.mock_guild.coordination_level = 0.7
        self.mock_guild.allied_guilds = []
        self.mock_guild.rival_guilds = []
        self.mock_guild.is_active = True
    
    def test_guild_personality_determination(self):
        """Test that guild personality is correctly determined."""
        # Test aggressive personality (high influence + market share)
        self.mock_guild.pricing_influence = 0.8
        self.mock_guild.market_share = 0.6
        self.mock_guild.allied_guilds = []
        
        personality = self.guild_ai_service.get_guild_personality(self.mock_guild)
        assert personality == GuildPersonality.AGGRESSIVE
        
        # Test diplomatic personality (many allies)
        self.mock_guild.allied_guilds = [uuid4(), uuid4(), uuid4()]
        personality = self.guild_ai_service.get_guild_personality(self.mock_guild)
        assert personality == GuildPersonality.DIPLOMATIC
        
        # Test innovative personality (high coordination)
        self.mock_guild.allied_guilds = []
        self.mock_guild.coordination_level = 0.9
        personality = self.guild_ai_service.get_guild_personality(self.mock_guild)
        assert personality == GuildPersonality.INNOVATIVE
        
        # Test conservative personality (default)
        self.mock_guild.coordination_level = 0.5
        self.mock_guild.pricing_influence = 0.3
        self.mock_guild.market_share = 0.2
        personality = self.guild_ai_service.get_guild_personality(self.mock_guild)
        assert personality == GuildPersonality.CONSERVATIVE
    
    def test_expansion_opportunity_evaluation(self):
        """Test that expansion opportunities are properly evaluated."""
        # Mock database query
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = self.mock_guild
        
        # Test expansion evaluation
        expansion_options = self.guild_ai_service.evaluate_expansion_opportunities(self.mock_guild.id)
        
        # Should return list of expansion options
        assert isinstance(expansion_options, list)
        
        # If options exist, they should have required attributes
        if expansion_options:
            option = expansion_options[0]
            assert isinstance(option, ExpansionOption)
            assert hasattr(option, 'region_id')
            assert hasattr(option, 'priority_score')
            assert hasattr(option, 'expansion_cost')
            assert hasattr(option, 'expected_profit')
            assert hasattr(option, 'risk_level')
            assert hasattr(option, 'strategic_value')
    
    def test_pricing_strategy_planning(self):
        """Test that pricing strategies are properly planned."""
        # Mock database query
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = self.mock_guild
        
        # Test pricing strategy planning
        pricing_strategy = self.guild_ai_service.plan_pricing_strategy(self.mock_guild.id)
        
        # Should return strategy plan
        assert isinstance(pricing_strategy, dict)
        assert "guild_id" in pricing_strategy
        assert "strategy" in pricing_strategy
        assert "personality" in pricing_strategy
        assert "pricing_adjustments" in pricing_strategy
        
        # Strategy should be valid
        valid_strategies = [s.value for s in PricingStrategy]
        assert pricing_strategy["strategy"] in valid_strategies
    
    def test_competition_threat_assessment(self):
        """Test that competitive threats are properly assessed."""
        # Mock database query
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = self.mock_guild
        
        # Add rival guilds for testing
        rival_guild = Mock(spec=MerchantGuildEntity)
        rival_guild.id = uuid4()
        rival_guild.total_wealth = 15000.0
        rival_guild.territory_control = ["region_1", "region_3"]  # Overlap with mock_guild
        
        self.mock_guild.rival_guilds = [rival_guild.id]
        
        # Mock rival guild query
        def mock_query_side_effect(*args):
            mock_query = Mock()
            if args[0] == MerchantGuildEntity:
                mock_filter = Mock()
                mock_filter.first.return_value = rival_guild
                mock_query.filter.return_value = mock_filter
            return mock_query
        
        self.mock_db_session.query.side_effect = mock_query_side_effect
        
        # Test threat assessment
        threats = self.guild_ai_service.assess_competition_threats(self.mock_guild.id)
        
        # Should return list of threats
        assert isinstance(threats, list)
        
        # If threats exist, they should have required attributes
        if threats:
            threat = threats[0]
            assert isinstance(threat, CompetitionThreat)
            assert hasattr(threat, 'threat_id')
            assert hasattr(threat, 'threat_type')
            assert hasattr(threat, 'severity')
            assert hasattr(threat, 'recommended_response')
            assert 0.0 <= threat.severity <= 1.0
    
    def test_alliance_proposal_generation(self):
        """Test that alliance proposals are properly generated."""
        # Mock database query for main guild
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = self.mock_guild
        
        # Create potential ally
        potential_ally = Mock(spec=MerchantGuildEntity)
        potential_ally.id = uuid4()
        potential_ally.total_wealth = 8000.0
        potential_ally.territory_control = ["region_3", "region_4"]
        potential_ally.market_share = 0.3
        potential_ally.pricing_influence = 0.5
        potential_ally.coordination_level = 0.6
        
        # Mock query for potential allies
        def mock_query_side_effect(*args):
            mock_query = Mock()
            if args[0] == MerchantGuildEntity:
                mock_query.filter.return_value.all.return_value = [potential_ally]
                mock_query.filter.return_value.first.return_value = self.mock_guild
            return mock_query
        
        self.mock_db_session.query.side_effect = mock_query_side_effect
        
        # Set guild to diplomatic personality for alliance testing
        self.mock_guild.allied_guilds = [uuid4(), uuid4()]  # Make diplomatic
        
        # Test alliance proposals
        proposals = self.guild_ai_service.propose_alliances(self.mock_guild.id)
        
        # Should return list of proposals
        assert isinstance(proposals, list)
        
        # If proposals exist, they should have required attributes
        if proposals:
            proposal = proposals[0]
            assert isinstance(proposal, AllianceProposal)
            assert hasattr(proposal, 'target_guild_id')
            assert hasattr(proposal, 'alliance_type')
            assert hasattr(proposal, 'mutual_benefit_score')
            assert hasattr(proposal, 'trust_level')
            assert hasattr(proposal, 'success_probability')
            assert 0.0 <= proposal.success_probability <= 1.0
    
    def test_market_manipulation_planning(self):
        """Test that market manipulation strategies are properly planned."""
        # Mock database query
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = self.mock_guild
        
        # Set guild to aggressive personality for manipulation testing
        self.mock_guild.pricing_influence = 0.8
        self.mock_guild.market_share = 0.7
        
        # Test market manipulation planning
        manipulation_plan = self.guild_ai_service.execute_market_manipulation(self.mock_guild.id)
        
        # Should return manipulation plan
        assert isinstance(manipulation_plan, ManipulationPlan)
        assert hasattr(manipulation_plan, 'manipulation_type')
        assert hasattr(manipulation_plan, 'target_markets')
        assert hasattr(manipulation_plan, 'expected_impact')
        assert hasattr(manipulation_plan, 'execution_cost')
        assert hasattr(manipulation_plan, 'risk_level')
        assert hasattr(manipulation_plan, 'success_probability')
        
        # Values should be within expected ranges
        assert 0.0 <= manipulation_plan.risk_level <= 1.0
        assert 0.0 <= manipulation_plan.success_probability <= 1.0
        assert manipulation_plan.execution_cost >= 0.0
    
    def test_guild_ai_tick_processing(self):
        """Test that guild AI tick processing works correctly."""
        # Mock database query
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = self.mock_guild
        
        # Test AI tick processing
        result = self.guild_ai_service.process_guild_ai_tick(self.mock_guild.id)
        
        # Should return processing results
        assert isinstance(result, dict)
        assert "guild_id" in result
        assert "actions_taken" in result
        assert "decisions_made" in result
        
        # Actions and decisions should be lists
        assert isinstance(result["actions_taken"], list)
        assert isinstance(result["decisions_made"], list)
    
    def test_personality_config_loading(self):
        """Test that personality configurations are properly loaded."""
        config = self.guild_ai_service.guild_ai_config
        
        # Should have personality traits
        assert "personality_traits" in config
        
        # Should have all personality types
        for personality in GuildPersonality:
            assert personality.value in config["personality_traits"]
            
            personality_config = config["personality_traits"][personality.value]
            
            # Should have required traits
            assert "expansion_rate" in personality_config
            assert "risk_tolerance" in personality_config
            assert "cooperation_willingness" in personality_config
            assert "competition_aggression" in personality_config
            
            # Values should be in valid ranges
            assert 0.0 <= personality_config["expansion_rate"] <= 1.0
            assert 0.0 <= personality_config["risk_tolerance"] <= 1.0
            assert 0.0 <= personality_config["cooperation_willingness"] <= 1.0
            assert 0.0 <= personality_config["competition_aggression"] <= 1.0
    
    def test_strategic_value_calculation(self):
        """Test strategic value calculation for regions."""
        # Test strategic value calculation
        strategic_value = self.guild_ai_service._calculate_strategic_value(self.mock_guild, "region_3")
        
        # Should return value between 0 and 1
        assert 0.0 <= strategic_value <= 1.0
        assert isinstance(strategic_value, float)
    
    def test_mutual_benefit_calculation(self):
        """Test mutual benefit calculation for alliances."""
        # Create second guild for testing
        guild2 = Mock(spec=MerchantGuildEntity)
        guild2.territory_control = ["region_3", "region_4"]
        guild2.total_wealth = 8000.0
        guild2.market_share = 0.3
        
        # Test mutual benefit calculation
        mutual_benefit = self.guild_ai_service._calculate_mutual_benefit(self.mock_guild, guild2)
        
        # Should return value between 0 and 1
        assert 0.0 <= mutual_benefit <= 1.0
        assert isinstance(mutual_benefit, float)
    
    def test_manipulation_cost_calculation(self):
        """Test market manipulation cost calculation."""
        manipulation_type = "price_fixing"
        target_markets = ["market_1", "market_2"]
        
        # Test cost calculation
        cost = self.guild_ai_service._calculate_manipulation_cost(
            self.mock_guild, manipulation_type, target_markets
        )
        
        # Should return positive cost
        assert cost > 0.0
        assert isinstance(cost, float)
        
        # Cost should be reasonable relative to guild wealth
        assert cost <= self.mock_guild.total_wealth * 5.0  # Max 5x wealth
    
    def test_expansion_execution(self):
        """Test expansion execution functionality."""
        expansion_option = ExpansionOption(
            region_id="region_5",
            priority_score=0.8,
            expansion_cost=2000.0,
            expected_profit=3000.0,
            risk_level=0.4,
            competition_level=0.3,
            strategic_value=0.7,
            reasoning="High profit potential"
        )
        
        initial_wealth = self.mock_guild.total_wealth
        initial_territories = len(self.mock_guild.territory_control)
        
        # Test expansion execution
        self.guild_ai_service._execute_expansion(self.mock_guild, expansion_option)
        
        # Should have committed changes
        assert self.mock_db_session.commit.called
        
        # Wealth should be reduced by expansion cost
        expected_wealth = initial_wealth - expansion_option.expansion_cost
        assert self.mock_guild.total_wealth == expected_wealth
    
    def test_threat_response(self):
        """Test threat response functionality."""
        threat = CompetitionThreat(
            threat_id="test_threat",
            threat_type="territorial_competition",
            severity=0.8,
            source_guild_id=uuid4(),
            affected_regions=["region_1"],
            recommended_response="defensive_pricing",
            urgency=0.7
        )
        
        # Test threat response
        response = self.guild_ai_service._respond_to_threat(self.mock_guild, threat)
        
        # Should return response description
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Should have committed changes
        assert self.mock_db_session.commit.called
    
    def test_alliance_attempt(self):
        """Test alliance formation attempt."""
        proposal = AllianceProposal(
            target_guild_id=uuid4(),
            alliance_type="trade_agreement",
            mutual_benefit_score=0.7,
            trust_level=0.8,
            strategic_alignment=0.6,
            proposed_terms={"duration": "indefinite"},
            success_probability=0.75
        )
        
        # Test alliance attempt
        success = self.guild_ai_service._attempt_alliance(self.mock_guild, proposal)
        
        # Should return boolean
        assert isinstance(success, bool)
        
        # Should have attempted database commit
        assert self.mock_db_session.commit.called or self.mock_db_session.rollback.called
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with non-existent guild
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Should handle gracefully
        expansion_options = self.guild_ai_service.evaluate_expansion_opportunities(uuid4())
        assert expansion_options == []
        
        pricing_strategy = self.guild_ai_service.plan_pricing_strategy(uuid4())
        assert "error" in pricing_strategy
        
        threats = self.guild_ai_service.assess_competition_threats(uuid4())
        assert threats == []
        
        proposals = self.guild_ai_service.propose_alliances(uuid4())
        assert proposals == []
    
    def teardown_method(self):
        """Clean up after tests."""
        self.mock_db_session.reset_mock()


if __name__ == "__main__":
    pytest.main([__file__]) 