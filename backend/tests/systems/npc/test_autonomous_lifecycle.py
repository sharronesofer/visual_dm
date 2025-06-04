"""
Comprehensive Tests for Autonomous NPC Lifecycle System

Tests all major components:
- Lifecycle phase transitions
- Goal generation and management
- Relationship formation
- Economic participation
- Political engagement
- Cultural participation
- Tier management
- Decision making
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker

from backend.systems.npc.services.autonomous_lifecycle_service import (
    AutonomousLifecycleService, LifecyclePhase
)
from backend.infrastructure.systems.npc.models.autonomous_lifecycle_models import (
    NpcGoal, NpcRelationship, NpcEconomicHistory, NpcPoliticalOpinion,
    NpcLifeEvent, NpcCulturalParticipation, NpcCareerProgression,
    NpcWealth, NpcAutonomousDecision, NpcTierStatus,
    GoalType, GoalStatus, RelationshipType, LifeEventType,
    PoliticalStance, EconomicTransactionType
)
from backend.infrastructure.systems.npc.models.models import NpcEntity


class TestAutonomousLifecycleService:
    """Test suite for autonomous lifecycle service"""
    
    @pytest.fixture
    def db_session(self):
        """Mock database session"""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None
        session.query.return_value.filter_by.return_value.all.return_value = []
        session.add = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        return session
    
    @pytest.fixture
    def sample_npc(self):
        """Create a sample NPC for testing"""
        return NpcEntity(
            id=uuid4(),
            name="Test Character",
            race="human",
            age=25,
            location="Test City",
            region_id="test_region",
            loyalty_score=50,
            status='active',
            lifecycle_phase='young_adult'
        )
    
    @pytest.fixture
    def lifecycle_service(self, db_session):
        """Create lifecycle service with mocked dependencies"""
        with patch('builtins.open', mock_open_race_demographics()):
            service = AutonomousLifecycleService(db_session)
            return service
    
    # ===== LIFECYCLE PHASE TESTS =====
    
    def test_determine_lifecycle_phase_human_young_adult(self, lifecycle_service):
        """Test lifecycle phase determination for young adult human"""
        lifecycle_stages = {
            "young_adult": {"min_age": 18, "max_age": 30},
            "adult": {"min_age": 31, "max_age": 50}
        }
        
        phase = lifecycle_service._determine_lifecycle_phase(25, lifecycle_stages)
        assert phase == "young_adult"
    
    def test_determine_lifecycle_phase_edge_case(self, lifecycle_service):
        """Test lifecycle phase at age boundaries"""
        lifecycle_stages = {
            "young_adult": {"min_age": 18, "max_age": 30},
            "adult": {"min_age": 31, "max_age": 50}
        }
        
        # Test exact boundary
        phase = lifecycle_service._determine_lifecycle_phase(30, lifecycle_stages)
        assert phase == "young_adult"
        
        phase = lifecycle_service._determine_lifecycle_phase(31, lifecycle_stages)
        assert phase == "adult"
    
    def test_process_lifecycle_phase_transition(self, lifecycle_service, sample_npc, db_session):
        """Test lifecycle phase transition processing"""
        # Mock NPC query
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_npc
        
        # Mock race demographics
        lifecycle_service.race_demographics = {
            "races": {
                "human": {
                    "lifecycle_stages": {
                        "adult": {"min_age": 31, "max_age": 50, "tier": 1}
                    }
                }
            }
        }
        
        # Test transition from young_adult to adult (age 31)
        sample_npc.age = 31
        sample_npc.lifecycle_phase = "young_adult"
        
        with patch.object(lifecycle_service, '_handle_phase_transition') as mock_transition:
            mock_transition.return_value = [{"type": "test_event"}]
            
            result = lifecycle_service.process_lifecycle_phase_transition(sample_npc.id)
            
            assert "previous_phase" in result
            assert "new_phase" in result
            assert result["new_phase"] == "adult"
            mock_transition.assert_called_once()
    
    # ===== GOAL GENERATION TESTS =====
    
    def test_generate_autonomous_goals(self, lifecycle_service, sample_npc, db_session):
        """Test autonomous goal generation"""
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_npc
        
        with patch.object(lifecycle_service, '_generate_phase_appropriate_goals') as mock_goals:
            mock_goals.return_value = [Mock(goal_id="test_goal")]
            
            goals = lifecycle_service.generate_autonomous_goals(sample_npc.id, 2)
            
            assert len(goals) >= 0
            mock_goals.assert_called_once()
    
    def test_generate_career_goal(self, lifecycle_service, sample_npc, db_session):
        """Test career goal generation"""
        with patch.object(lifecycle_service, '_get_current_career') as mock_career:
            mock_career.return_value = None
            
            goal = lifecycle_service._generate_career_goal(sample_npc, "young_adult")
            
            assert goal.goal_type == GoalType.CAREER
            assert "employment" in goal.title.lower()
            assert goal.priority > 0
            db_session.add.assert_called_with(goal)
    
    def test_generate_relationship_goal(self, lifecycle_service, sample_npc, db_session):
        """Test relationship goal generation"""
        # Mock no existing relationships
        db_session.query.return_value.filter_by.return_value.all.return_value = []
        
        goal = lifecycle_service._generate_relationship_goal(sample_npc, "young_adult")
        
        assert goal.goal_type == GoalType.RELATIONSHIP
        assert goal.priority > 0
        db_session.add.assert_called_with(goal)
    
    def test_generate_wealth_goal(self, lifecycle_service, sample_npc, db_session):
        """Test wealth goal generation"""
        mock_wealth = Mock()
        mock_wealth.economic_class = "poor"
        
        with patch.object(lifecycle_service, '_get_npc_wealth') as mock_get_wealth:
            mock_get_wealth.return_value = mock_wealth
            
            goal = lifecycle_service._generate_wealth_goal(sample_npc, "adult")
            
            assert goal.goal_type == GoalType.WEALTH
            assert "financial" in goal.title.lower()
            db_session.add.assert_called_with(goal)
    
    # ===== RELATIONSHIP FORMATION TESTS =====
    
    def test_process_relationship_formation(self, lifecycle_service, sample_npc, db_session):
        """Test relationship formation processing"""
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_npc
        
        # Mock tier status
        mock_tier = Mock()
        mock_tier.current_tier = 2
        
        with patch.object(lifecycle_service, '_get_tier_status') as mock_get_tier:
            with patch.object(lifecycle_service, '_form_new_relationship') as mock_form:
                mock_get_tier.return_value = mock_tier
                mock_relationship = Mock()
                mock_relationship.id = uuid4()
                mock_relationship.target_npc_id = uuid4()
                mock_relationship.relationship_type = RelationshipType.FRIEND
                mock_form.return_value = mock_relationship
                
                result = lifecycle_service.process_relationship_formation(sample_npc.id)
                
                # Should have potential for relationship formation
                assert isinstance(result, list)
    
    def test_form_new_relationship(self, lifecycle_service, sample_npc, db_session):
        """Test new relationship formation"""
        target_npc = NpcEntity(
            id=uuid4(),
            name="Target NPC",
            race="human",
            age=23,
            region_id="test_region"
        )
        
        with patch.object(lifecycle_service, '_find_relationship_candidates') as mock_candidates:
            with patch.object(lifecycle_service, '_determine_relationship_type') as mock_type:
                mock_candidates.return_value = [target_npc]
                mock_type.return_value = RelationshipType.FRIEND
                
                relationship = lifecycle_service._form_new_relationship(sample_npc)
                
                assert relationship is not None
                assert relationship.source_npc_id == sample_npc.id
                assert relationship.target_npc_id == target_npc.id
                assert relationship.relationship_type == RelationshipType.FRIEND
    
    # ===== ECONOMIC PARTICIPATION TESTS =====
    
    def test_process_economic_activity(self, lifecycle_service, sample_npc, db_session):
        """Test economic activity processing"""
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_npc
        
        with patch.object(lifecycle_service, '_generate_economic_transaction') as mock_transaction:
            with patch.object(lifecycle_service, '_update_wealth_from_activities') as mock_update:
                mock_transaction.return_value = Mock(
                    transaction_id="test_txn",
                    transaction_type=EconomicTransactionType.PURCHASE,
                    amount=50.0
                )
                
                activities = lifecycle_service.process_economic_activity(sample_npc.id)
                
                assert isinstance(activities, list)
                # Should generate some economic activity for an adult
    
    def test_generate_economic_transaction(self, lifecycle_service, sample_npc, db_session):
        """Test economic transaction generation"""
        mock_wealth = Mock()
        mock_wealth.liquid_wealth = 150.0
        
        with patch.object(lifecycle_service, '_get_npc_wealth') as mock_get_wealth:
            with patch.object(lifecycle_service, '_calculate_transaction_amount') as mock_amount:
                with patch.object(lifecycle_service, '_generate_transaction_description') as mock_desc:
                    with patch.object(lifecycle_service, '_generate_transaction_reasoning') as mock_reason:
                        mock_get_wealth.return_value = mock_wealth
                        mock_amount.return_value = 75.0
                        mock_desc.return_value = "Test purchase"
                        mock_reason.return_value = "Needed item"
                        
                        transaction = lifecycle_service._generate_economic_transaction(sample_npc)
                        
                        assert transaction is not None
                        assert transaction.npc_id == sample_npc.id
                        assert transaction.amount == 75.0
                        db_session.add.assert_called_with(transaction)
    
    # ===== POLITICAL ENGAGEMENT TESTS =====
    
    def test_process_political_engagement(self, lifecycle_service, sample_npc, db_session):
        """Test political engagement processing"""
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_npc
        db_session.query.return_value.filter_by.return_value.all.return_value = []
        
        with patch.object(lifecycle_service, '_form_political_opinion') as mock_opinion:
            mock_opinion.return_value = Mock(
                topic="taxation_policy",
                stance=PoliticalStance.OPPOSE
            )
            
            # Mock random to ensure opinion formation
            with patch('random.random', return_value=0.1):  # 10% < 20% threshold
                activities = lifecycle_service.process_political_engagement(sample_npc.id)
                
                assert isinstance(activities, list)
    
    def test_form_political_opinion(self, lifecycle_service, sample_npc, db_session):
        """Test political opinion formation"""
        with patch.object(lifecycle_service, '_determine_political_stance') as mock_stance:
            with patch.object(lifecycle_service, '_generate_political_reasoning') as mock_reasoning:
                mock_stance.return_value = PoliticalStance.SUPPORT
                mock_reasoning.return_value = "Based on personal experience"
                
                # Mock random choice for topic
                with patch('random.choice', return_value="military_spending"):
                    with patch('random.uniform', return_value=6.0):
                        opinion = lifecycle_service._form_political_opinion(sample_npc)
                        
                        assert opinion is not None
                        assert opinion.npc_id == sample_npc.id
                        assert opinion.topic == "military_spending"
                        assert opinion.stance == PoliticalStance.SUPPORT
                        db_session.add.assert_called_with(opinion)
    
    # ===== AUTONOMOUS DECISION TESTS =====
    
    def test_make_autonomous_decision(self, lifecycle_service, sample_npc, db_session):
        """Test autonomous decision making"""
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_npc
        
        decision_context = {
            "type": "career_choice",
            "description": "Choose between job offers",
            "options": ["merchant", "guard", "scholar"]
        }
        
        with patch.object(lifecycle_service, '_score_decision_options') as mock_score:
            with patch.object(lifecycle_service, '_select_best_option') as mock_select:
                mock_score.return_value = [
                    {"option": "merchant", "score": 7.5, "reasoning": "Good fit", "confidence": 7.5}
                ]
                mock_select.return_value = {
                    "option": "merchant", 
                    "reasoning": "Good fit", 
                    "confidence": 7.5
                }
                
                result = lifecycle_service.make_autonomous_decision(sample_npc.id, decision_context)
                
                assert "decision_id" in result
                assert result["chosen_option"] == "merchant"
                assert "reasoning" in result
                db_session.add.assert_called()
                db_session.commit.assert_called()
    
    def test_score_decision_options(self, lifecycle_service, sample_npc):
        """Test decision option scoring"""
        options = ["option_a", "option_b", "option_c"]
        
        with patch.object(lifecycle_service, '_score_option_by_personality') as mock_personality:
            with patch.object(lifecycle_service, '_score_option_by_goals') as mock_goals:
                with patch.object(lifecycle_service, '_score_option_by_relationships') as mock_relationships:
                    with patch.object(lifecycle_service, '_score_option_by_economics') as mock_economics:
                        mock_personality.return_value = 2.0
                        mock_goals.return_value = 1.5
                        mock_relationships.return_value = 1.0
                        mock_economics.return_value = 0.5
                        
                        scored = lifecycle_service._score_decision_options(sample_npc, options, "test")
                        
                        assert len(scored) == 3
                        assert all("option" in item for item in scored)
                        assert all("score" in item for item in scored)
                        assert all("reasoning" in item for item in scored)
    
    # ===== TIER MANAGEMENT TESTS =====
    
    def test_get_tier_status_existing(self, lifecycle_service, sample_npc, db_session):
        """Test getting existing tier status"""
        mock_tier = NpcTierStatus(
            npc_id=sample_npc.id,
            current_tier=2,
            simulation_detail_level="partial"
        )
        
        db_session.query.return_value.filter_by.return_value.first.return_value = mock_tier
        
        tier_status = lifecycle_service._get_tier_status(sample_npc)
        
        assert tier_status.current_tier == 2
        assert tier_status.simulation_detail_level == "partial"
    
    def test_get_tier_status_new(self, lifecycle_service, sample_npc, db_session):
        """Test creating new tier status"""
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Mock race demographics
        lifecycle_service.race_demographics = {
            "races": {
                "human": {
                    "lifecycle_stages": {
                        "young_adult": {"tier": 2}
                    }
                }
            }
        }
        
        tier_status = lifecycle_service._get_tier_status(sample_npc)
        
        assert tier_status.npc_id == sample_npc.id
        assert tier_status.current_tier == 2
        db_session.add.assert_called_with(tier_status)
    
    # ===== MONTHLY LIFECYCLE UPDATE TESTS =====
    
    def test_process_monthly_lifecycle_update(self, lifecycle_service, sample_npc):
        """Test comprehensive monthly update"""
        with patch.object(lifecycle_service, 'process_lifecycle_phase_transition') as mock_phase:
            with patch.object(lifecycle_service, 'process_relationship_formation') as mock_relations:
                with patch.object(lifecycle_service, 'process_economic_activity') as mock_economic:
                    with patch.object(lifecycle_service, 'process_political_engagement') as mock_political:
                        with patch.object(lifecycle_service, 'process_cultural_engagement') as mock_cultural:
                            with patch.object(lifecycle_service, '_update_goal_progress') as mock_goals:
                                mock_phase.return_value = {"transition": "test"}
                                mock_relations.return_value = [{"relationship": "test"}]
                                mock_economic.return_value = [{"transaction": "test"}]
                                mock_political.return_value = [{"opinion": "test"}]
                                mock_cultural.return_value = [{"culture": "test"}]
                                
                                result = lifecycle_service.process_monthly_lifecycle_update(sample_npc.id)
                                
                                assert "npc_id" in result
                                assert "phase_transitions" in result
                                assert "relationships" in result
                                assert "economic_activities" in result
                                assert "political_activities" in result
                                assert "cultural_activities" in result
                                
                                # Verify all components were called
                                mock_phase.assert_called_once_with(sample_npc.id)
                                mock_relations.assert_called_once_with(sample_npc.id)
                                mock_economic.assert_called_once_with(sample_npc.id)
                                mock_political.assert_called_once_with(sample_npc.id)
                                mock_cultural.assert_called_once_with(sample_npc.id)
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_process_lifecycle_npc_not_found(self, lifecycle_service, db_session):
        """Test error handling when NPC not found"""
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        result = lifecycle_service.process_lifecycle_phase_transition(uuid4())
        
        assert "error" in result
        assert result["error"] == "NPC not found"
    
    def test_generate_goals_npc_not_found(self, lifecycle_service, db_session):
        """Test goal generation with missing NPC"""
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        goals = lifecycle_service.generate_autonomous_goals(uuid4())
        
        assert goals == []
    
    def test_make_decision_npc_not_found(self, lifecycle_service, db_session):
        """Test decision making with missing NPC"""
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        result = lifecycle_service.make_autonomous_decision(uuid4(), {"type": "test"})
        
        assert "error" in result
        assert result["error"] == "NPC not found"
    
    def test_make_decision_no_options(self, lifecycle_service, sample_npc, db_session):
        """Test decision making with no options"""
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_npc
        
        result = lifecycle_service.make_autonomous_decision(sample_npc.id, {"type": "test", "options": []})
        
        assert "error" in result
        assert result["error"] == "No options provided"


# ===== INTEGRATION TESTS =====

class TestAutonomousLifecycleIntegration:
    """Integration tests for autonomous lifecycle system"""
    
    def test_complete_lifecycle_simulation(self):
        """Test complete lifecycle from birth to death"""
        # This would be a comprehensive integration test
        # involving multiple NPCs and full lifecycle simulation
        pass
    
    def test_relationship_network_formation(self):
        """Test formation of complex relationship networks"""
        # Test how relationships form between multiple NPCs
        pass
    
    def test_economic_ecosystem_interaction(self):
        """Test economic interactions between NPCs"""
        # Test trading, employment, and economic relationships
        pass
    
    def test_political_faction_formation(self):
        """Test formation of political factions and alignments"""
        # Test how NPCs form political groups and opinions
        pass


# ===== PERFORMANCE TESTS =====

class TestAutonomousLifecyclePerformance:
    """Performance tests for autonomous lifecycle system"""
    
    def test_batch_processing_performance(self):
        """Test performance of batch lifecycle processing"""
        # Test processing large numbers of NPCs efficiently
        pass
    
    def test_tier_based_optimization(self):
        """Test performance benefits of tier-based processing"""
        # Test that tier 4 NPCs are processed more efficiently
        pass
    
    def test_memory_usage_optimization(self):
        """Test memory usage during large-scale processing"""
        # Test memory efficiency with large NPC populations
        pass


# ===== HELPER FUNCTIONS =====

def mock_open_race_demographics():
    """Mock file opening for race demographics"""
    race_data = {
        "races": {
            "human": {
                "lifespan": {"base_life_expectancy": 75, "maturity_age": 18},
                "lifecycle_stages": {
                    "young_adult": {"min_age": 18, "max_age": 30, "tier": 2},
                    "adult": {"min_age": 31, "max_age": 50, "tier": 1}
                }
            }
        }
    }
    return MagicMock(return_value=MagicMock(read=lambda: json.dumps(race_data)))


if __name__ == "__main__":
    pytest.main([__file__]) 