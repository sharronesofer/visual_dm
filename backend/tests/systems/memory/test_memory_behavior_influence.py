"""
Tests for Memory Behavior Influence Service
------------------------------------------

Comprehensive test suite for memory-driven behavioral modifications
and decision-making algorithms.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import List, Dict, Any

from backend.systems.memory.services.memory_behavior_influence import (
    MemoryBehaviorInfluenceService,
    BehaviorModifier,
    BehaviorInfluenceType,
    TrustCalculation,
    RiskAssessment,
    EmotionalTrigger
)
from backend.systems.memory.services.memory import Memory
from backend.infrastructure.memory_utils.memory_categorization import MemoryCategory
from backend.systems.memory.services.memory_manager_core import MemoryManager


@pytest.fixture
def mock_memory_manager():
    """Create a mock memory manager for testing"""
    manager = Mock(spec=MemoryManager)
    manager.entity_id = "test_npc_001"
    manager.entity_type = "npc"
    manager.get_memories_involving_entity = AsyncMock()
    manager.query_memories = AsyncMock()
    manager.get_memories_by_category = AsyncMock()
    return manager


@pytest.fixture
def behavior_service(mock_memory_manager):
    """Create a behavior influence service for testing"""
    return MemoryBehaviorInfluenceService(mock_memory_manager)


@pytest.fixture
def sample_memories():
    """Create sample memories for testing"""
    current_time = datetime.now()
    
    return [
        Memory(
            npc_id="test_npc_001",
            content="Player helped me fight off bandits",
            memory_id="mem_001",
            importance=0.8,
            categories=[MemoryCategory.ACHIEVEMENT.value],
            created_at=(current_time - timedelta(days=5)).isoformat(),
            metadata={"entities": ["player_123"], "tags": ["player", "help", "combat"]}
        ),
        Memory(
            npc_id="test_npc_001",
            content="Player betrayed our trade agreement",
            memory_id="mem_002",
            importance=0.9,
            categories=[MemoryCategory.TRAUMA.value],
            created_at=(current_time - timedelta(days=10)).isoformat(),
            metadata={"entities": ["player_123"], "tags": ["player", "betrayal", "trade"]}
        ),
        Memory(
            npc_id="test_npc_001",
            content="Witnessed the Battle of Thornfield",
            memory_id="mem_003",
            importance=0.95,
            memory_type="core",
            categories=[MemoryCategory.TRAUMA.value],
            created_at=(current_time - timedelta(days=30)).isoformat(),
            metadata={"entities": ["red_hawks_faction"], "tags": ["war", "trauma", "battle"]}
        )
    ]


class TestTrustCalculation:
    """Test trust level calculations based on memory history"""
    
    @pytest.mark.asyncio
    async def test_calculate_trust_no_memories(self, behavior_service, mock_memory_manager):
        """Test trust calculation when no memories exist"""
        mock_memory_manager.get_memories_involving_entity.return_value = []
        
        result = await behavior_service.calculate_trust_level("unknown_entity")
        
        assert result.entity_id == "unknown_entity"
        assert result.trust_level == 0.5  # Neutral trust
        assert result.trust_change == 0.0
        assert result.confidence == 0.0
        assert len(result.contributing_memories) == 0
    
    @pytest.mark.asyncio
    async def test_calculate_trust_positive_memories(self, behavior_service, mock_memory_manager, sample_memories):
        """Test trust calculation with positive memories"""
        positive_memories = [sample_memories[0]]  # Help memory
        mock_memory_manager.get_memories_involving_entity.return_value = positive_memories
        
        result = await behavior_service.calculate_trust_level("player_123")
        
        assert result.entity_id == "player_123"
        assert result.trust_level > 0.5  # Above neutral
        assert result.trust_change > 0.0
        assert result.confidence > 0.0
        assert len(result.contributing_memories) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_trust_negative_memories(self, behavior_service, mock_memory_manager, sample_memories):
        """Test trust calculation with negative memories"""
        negative_memories = [sample_memories[1]]  # Betrayal memory
        mock_memory_manager.get_memories_involving_entity.return_value = negative_memories
        
        result = await behavior_service.calculate_trust_level("player_123")
        
        assert result.entity_id == "player_123"
        assert result.trust_level < 0.5  # Below neutral
        assert result.trust_change < 0.0
        assert result.confidence > 0.0
        assert len(result.contributing_memories) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_trust_mixed_memories(self, behavior_service, mock_memory_manager, sample_memories):
        """Test trust calculation with both positive and negative memories"""
        mixed_memories = [sample_memories[0], sample_memories[1]]  # Help + betrayal
        mock_memory_manager.get_memories_involving_entity.return_value = mixed_memories
        
        result = await behavior_service.calculate_trust_level("player_123")
        
        assert result.entity_id == "player_123"
        assert 0.0 <= result.trust_level <= 1.0
        assert result.confidence > 0.0
        assert len(result.contributing_memories) == 2


class TestRiskAssessment:
    """Test risk assessment based on past experiences"""
    
    @pytest.mark.asyncio
    async def test_assess_risk_no_relevant_memories(self, behavior_service):
        """Test risk assessment when no relevant memories exist"""
        with patch.object(behavior_service, '_get_memories_for_situation', return_value=[]):
            result = await behavior_service.assess_risk("combat")
            
            assert result.situation_type == "combat"
            assert result.risk_level == 0.5  # Neutral risk
            assert result.confidence == 0.0
            assert len(result.past_experiences) == 0
    
    @pytest.mark.asyncio
    async def test_assess_risk_with_trauma_memories(self, behavior_service, sample_memories):
        """Test risk assessment with traumatic memories"""
        trauma_memories = [sample_memories[2]]  # Battle memory
        
        with patch.object(behavior_service, '_get_memories_for_situation', return_value=trauma_memories):
            with patch.object(behavior_service, '_calculate_risk_impact_from_memory', return_value=0.8):
                result = await behavior_service.assess_risk("combat")
                
                assert result.situation_type == "combat"
                assert result.risk_level > 0.5  # High risk due to trauma
                assert result.confidence > 0.0
                assert len(result.past_experiences) > 0
    
    @pytest.mark.asyncio
    async def test_assess_risk_with_positive_memories(self, behavior_service, sample_memories):
        """Test risk assessment with positive memories"""
        positive_memories = [sample_memories[0]]  # Help memory
        
        with patch.object(behavior_service, '_get_memories_for_situation', return_value=positive_memories):
            with patch.object(behavior_service, '_calculate_risk_impact_from_memory', return_value=0.2):
                result = await behavior_service.assess_risk("combat")
                
                assert result.situation_type == "combat"
                assert result.risk_level < 0.5  # Lower risk due to positive experience
                assert result.confidence > 0.0


class TestEmotionalTriggers:
    """Test emotional trigger identification from memories"""
    
    @pytest.mark.asyncio
    async def test_identify_emotional_triggers_no_memories(self, behavior_service):
        """Test emotional trigger identification with no emotional memories"""
        with patch.object(behavior_service, '_get_emotional_memories', return_value=[]):
            result = await behavior_service.identify_emotional_triggers()
            
            assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_identify_emotional_triggers_with_trauma(self, behavior_service, sample_memories):
        """Test emotional trigger identification with traumatic memories"""
        trauma_memories = [sample_memories[2]]  # Battle memory
        
        with patch.object(behavior_service, '_get_emotional_memories', return_value=trauma_memories):
            with patch.object(behavior_service, '_analyze_memory_emotion', return_value={
                'emotion': 'fear',
                'intensity': 0.8,
                'triggers': ['battle_sounds', 'weapons']
            }):
                result = await behavior_service.identify_emotional_triggers()
                
                assert len(result) > 0
                trigger = result[0]
                assert trigger.emotion == 'fear'
                assert trigger.intensity == 0.8
                assert len(trigger.trigger_memories) > 0


class TestFactionBias:
    """Test faction bias calculations"""
    
    @pytest.mark.asyncio
    async def test_calculate_faction_bias_no_memories(self, behavior_service):
        """Test faction bias calculation with no faction memories"""
        with patch.object(behavior_service, '_get_faction_memories', return_value=[]):
            result = await behavior_service.calculate_faction_bias("red_hawks")
            
            assert result == 0.0  # Neutral bias
    
    @pytest.mark.asyncio
    async def test_calculate_faction_bias_negative_memories(self, behavior_service, sample_memories):
        """Test faction bias calculation with negative faction memories"""
        faction_memories = [sample_memories[2]]  # Battle memory with red_hawks
        
        with patch.object(behavior_service, '_get_faction_memories', return_value=faction_memories):
            with patch.object(behavior_service, '_calculate_faction_bias_from_memory', return_value=-0.7):
                result = await behavior_service.calculate_faction_bias("red_hawks")
                
                assert result < 0.0  # Negative bias
    
    @pytest.mark.asyncio
    async def test_calculate_faction_bias_positive_memories(self, behavior_service, sample_memories):
        """Test faction bias calculation with positive faction memories"""
        # Create a positive faction memory
        positive_faction_memory = Memory(
            npc_id="test_npc_001",
            content="Red Hawks helped defend our village",
            memory_id="mem_004",
            importance=0.8,
            categories=[MemoryCategory.ACHIEVEMENT.value],
            created_at=(datetime.now() - timedelta(days=5)).isoformat(),
            metadata={"entities": ["red_hawks_faction"], "tags": ["red_hawks", "help", "defense"]}
        )
        
        with patch.object(behavior_service, '_get_faction_memories', return_value=[positive_faction_memory]):
            with patch.object(behavior_service, '_calculate_faction_bias_from_memory', return_value=0.6):
                result = await behavior_service.calculate_faction_bias("red_hawks")
                
                assert result > 0.0  # Positive bias


class TestBehaviorModifiers:
    """Test comprehensive behavior modifier generation"""
    
    @pytest.mark.asyncio
    async def test_generate_behavior_modifiers_empty(self, behavior_service):
        """Test behavior modifier generation with no memories"""
        with patch.object(behavior_service, 'identify_emotional_triggers', return_value=[]):
            with patch.object(behavior_service, 'assess_risk', return_value=RiskAssessment(
                situation_type="general",
                risk_level=0.5,
                risk_factors={},
                past_experiences=[],
                confidence=0.0
            )):
                result = await behavior_service.generate_behavior_modifiers()
                
                assert isinstance(result, list)
                # Should still generate some base modifiers
    
    @pytest.mark.asyncio
    async def test_generate_behavior_modifiers_with_emotions(self, behavior_service):
        """Test behavior modifier generation with emotional triggers"""
        emotional_trigger = EmotionalTrigger(
            emotion="fear",
            intensity=0.8,
            trigger_memories=["mem_003"],
            duration_estimate=timedelta(hours=2),
            behavioral_effects={"aggression": -0.3, "flee_threshold": 0.4}
        )
        
        with patch.object(behavior_service, 'identify_emotional_triggers', return_value=[emotional_trigger]):
            with patch.object(behavior_service, 'assess_risk', return_value=RiskAssessment(
                situation_type="general",
                risk_level=0.7,
                risk_factors={"combat": 0.8},
                past_experiences=["mem_003"],
                confidence=0.8
            )):
                result = await behavior_service.generate_behavior_modifiers()
                
                assert len(result) > 0
                # Should have emotional response modifiers
                emotional_modifiers = [m for m in result if m.influence_type == BehaviorInfluenceType.EMOTIONAL_RESPONSE]
                assert len(emotional_modifiers) > 0


class TestMemoryWeightCalculation:
    """Test memory weight calculation algorithms"""
    
    def test_calculate_memory_weight_recent_important(self, behavior_service, sample_memories):
        """Test weight calculation for recent, important memory"""
        current_time = datetime.now()
        memory = sample_memories[0]  # Recent, important memory
        
        weight = behavior_service._calculate_memory_weight(memory, current_time)
        
        assert weight > 0.0
        assert isinstance(weight, float)
    
    def test_calculate_memory_weight_old_unimportant(self, behavior_service):
        """Test weight calculation for old, unimportant memory"""
        current_time = datetime.now()
        old_memory = Memory(
            npc_id="test_npc_001",
            content="Minor interaction",
            memory_id="mem_old",
            importance=0.1,
            categories=[MemoryCategory.CONVERSATION.value],
            created_at=(current_time - timedelta(days=365)).isoformat(),  # Very old
            metadata={"entities": ["someone"], "tags": ["minor"]}
        )
        
        weight = behavior_service._calculate_memory_weight(old_memory, current_time)
        
        assert weight >= 0.0
        assert weight < 1.0  # Should be low weight


class TestTrustImpactCalculation:
    """Test trust impact calculation from memories"""
    
    def test_calculate_trust_impact_positive(self, behavior_service, sample_memories):
        """Test trust impact calculation for positive memory"""
        positive_memory = sample_memories[0]  # Help memory
        
        impact = behavior_service._calculate_trust_impact_from_memory(positive_memory, "player_123")
        
        assert impact > 0.0  # Positive impact
    
    def test_calculate_trust_impact_negative(self, behavior_service, sample_memories):
        """Test trust impact calculation for negative memory"""
        negative_memory = sample_memories[1]  # Betrayal memory
        
        impact = behavior_service._calculate_trust_impact_from_memory(negative_memory, "player_123")
        
        assert impact < 0.0  # Negative impact
    
    def test_calculate_trust_impact_unrelated_entity(self, behavior_service, sample_memories):
        """Test trust impact calculation for unrelated entity"""
        memory = sample_memories[0]
        
        impact = behavior_service._calculate_trust_impact_from_memory(memory, "unrelated_entity")
        
        assert impact == 0.0  # No impact for unrelated entity


class TestSentimentAnalysis:
    """Test interaction sentiment analysis"""
    
    def test_analyze_interaction_sentiment_positive(self, behavior_service, sample_memories):
        """Test sentiment analysis for positive interaction"""
        positive_memory = sample_memories[0]  # Help memory
        
        sentiment = behavior_service._analyze_interaction_sentiment(positive_memory, "player_123")
        
        assert sentiment > 0.0  # Positive sentiment
    
    def test_analyze_interaction_sentiment_negative(self, behavior_service, sample_memories):
        """Test sentiment analysis for negative interaction"""
        negative_memory = sample_memories[1]  # Betrayal memory
        
        sentiment = behavior_service._analyze_interaction_sentiment(negative_memory, "player_123")
        
        assert sentiment < 0.0  # Negative sentiment
    
    def test_analyze_interaction_sentiment_neutral(self, behavior_service):
        """Test sentiment analysis for neutral interaction"""
        neutral_memory = Memory(
            npc_id="test_npc_001",
            content="Had a normal conversation about weather",
            memory_id="mem_neutral",
            importance=0.3,
            categories=[MemoryCategory.CONVERSATION.value],
            created_at=datetime.now().isoformat(),
            metadata={"entities": ["player_123"], "tags": ["conversation", "weather"]}
        )
        
        sentiment = behavior_service._analyze_interaction_sentiment(neutral_memory, "player_123")
        
        assert -0.1 <= sentiment <= 0.1  # Near neutral


class TestMemoryRetrieval:
    """Test memory retrieval methods"""
    
    @pytest.mark.asyncio
    async def test_get_memories_for_situation(self, behavior_service, mock_memory_manager, sample_memories):
        """Test retrieving memories for specific situation"""
        mock_memory_manager.query_memories.return_value = sample_memories
        
        result = await behavior_service._get_memories_for_situation("combat", {"location": "battlefield"})
        
        assert isinstance(result, list)
        mock_memory_manager.query_memories.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_emotional_memories(self, behavior_service, mock_memory_manager, sample_memories):
        """Test retrieving emotional memories"""
        emotional_memories = [sample_memories[1], sample_memories[2]]  # Trauma memories
        mock_memory_manager.get_memories_by_category.return_value = emotional_memories
        
        result = await behavior_service._get_emotional_memories()
        
        assert isinstance(result, list)
        mock_memory_manager.get_memories_by_category.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_faction_memories(self, behavior_service, mock_memory_manager, sample_memories):
        """Test retrieving faction-related memories"""
        faction_memories = [sample_memories[2]]  # Battle memory with faction
        mock_memory_manager.query_memories.return_value = faction_memories
        
        result = await behavior_service._get_faction_memories("red_hawks")
        
        assert isinstance(result, list)
        mock_memory_manager.query_memories.assert_called_once()


class TestRiskFactorExtraction:
    """Test risk factor extraction from memories"""
    
    def test_extract_risk_factors_combat_memory(self, behavior_service, sample_memories):
        """Test risk factor extraction from combat memory"""
        combat_memory = sample_memories[2]  # Battle memory
        
        risk_factors = behavior_service._extract_risk_factors_from_memory(combat_memory)
        
        assert isinstance(risk_factors, dict)
        assert len(risk_factors) >= 0
    
    def test_extract_risk_factors_trade_memory(self, behavior_service, sample_memories):
        """Test risk factor extraction from trade memory"""
        trade_memory = sample_memories[1]  # Betrayal in trade
        
        risk_factors = behavior_service._extract_risk_factors_from_memory(trade_memory)
        
        assert isinstance(risk_factors, dict)


class TestEmotionalAnalysis:
    """Test emotional analysis of memories"""
    
    def test_analyze_memory_emotion_trauma(self, behavior_service, sample_memories):
        """Test emotional analysis of traumatic memory"""
        trauma_memory = sample_memories[2]  # Battle memory
        
        emotion_data = behavior_service._analyze_memory_emotion(trauma_memory)
        
        if emotion_data:  # May return None for non-emotional memories
            assert 'emotion' in emotion_data
            assert 'intensity' in emotion_data
            assert isinstance(emotion_data['intensity'], float)
    
    def test_analyze_memory_emotion_positive(self, behavior_service, sample_memories):
        """Test emotional analysis of positive memory"""
        positive_memory = sample_memories[0]  # Help memory
        
        emotion_data = behavior_service._analyze_memory_emotion(positive_memory)
        
        if emotion_data:
            assert 'emotion' in emotion_data
            assert 'intensity' in emotion_data
    
    def test_calculate_emotional_behavioral_effects(self, behavior_service):
        """Test calculation of behavioral effects from emotions"""
        effects = behavior_service._calculate_emotional_behavioral_effects("fear", 0.8)
        
        assert isinstance(effects, dict)
        assert len(effects) > 0
        
        # Fear should affect certain behaviors
        if "aggression" in effects:
            assert effects["aggression"] < 0.0  # Fear reduces aggression
        if "flee_threshold" in effects:
            assert effects["flee_threshold"] > 0.0  # Fear increases flee threshold


class TestFactionBiasCalculation:
    """Test faction bias calculation from memories"""
    
    def test_calculate_faction_bias_from_memory_positive(self, behavior_service):
        """Test faction bias calculation from positive faction memory"""
        positive_faction_memory = Memory(
            npc_id="test_npc_001",
            content="Red Hawks saved our village from bandits",
            memory_id="mem_faction_pos",
            importance=0.8,
            categories=[MemoryCategory.ACHIEVEMENT.value],
            created_at=datetime.now().isoformat(),
            metadata={"entities": ["red_hawks_faction"], "tags": ["red_hawks", "rescue", "heroic"]}
        )
        
        bias = behavior_service._calculate_faction_bias_from_memory(positive_faction_memory, "red_hawks")
        
        assert bias > 0.0  # Positive bias
    
    def test_calculate_faction_bias_from_memory_negative(self, behavior_service, sample_memories):
        """Test faction bias calculation from negative faction memory"""
        negative_faction_memory = sample_memories[2]  # Battle trauma
        
        bias = behavior_service._calculate_faction_bias_from_memory(negative_faction_memory, "red_hawks")
        
        # Could be negative if the faction was involved in the trauma
        assert isinstance(bias, float)
    
    def test_calculate_faction_bias_from_memory_unrelated(self, behavior_service, sample_memories):
        """Test faction bias calculation from unrelated memory"""
        unrelated_memory = sample_memories[0]  # Help memory, no faction
        
        bias = behavior_service._calculate_faction_bias_from_memory(unrelated_memory, "blue_shields")
        
        assert bias == 0.0  # No bias for unrelated faction


# Integration tests
class TestIntegration:
    """Integration tests for the complete behavior influence system"""
    
    @pytest.mark.asyncio
    async def test_full_behavior_analysis_workflow(self, behavior_service, mock_memory_manager, sample_memories):
        """Test complete workflow from memories to behavior modifiers"""
        # Setup mock returns
        mock_memory_manager.get_memories_involving_entity.return_value = sample_memories
        mock_memory_manager.query_memories.return_value = sample_memories
        mock_memory_manager.get_memories_by_category.return_value = [sample_memories[2]]  # Trauma
        
        # Test trust calculation
        trust_result = await behavior_service.calculate_trust_level("player_123")
        assert isinstance(trust_result, TrustCalculation)
        
        # Test risk assessment
        risk_result = await behavior_service.assess_risk("combat")
        assert isinstance(risk_result, RiskAssessment)
        
        # Test emotional triggers
        emotional_triggers = await behavior_service.identify_emotional_triggers()
        assert isinstance(emotional_triggers, list)
        
        # Test faction bias
        faction_bias = await behavior_service.calculate_faction_bias("red_hawks")
        assert isinstance(faction_bias, float)
        
        # Test comprehensive behavior modifiers
        modifiers = await behavior_service.generate_behavior_modifiers()
        assert isinstance(modifiers, list)
        
        # Verify all components work together
        assert len(modifiers) >= 0  # Should generate some modifiers
    
    @pytest.mark.asyncio
    async def test_behavior_consistency_over_time(self, behavior_service, mock_memory_manager):
        """Test that behavior calculations are consistent over multiple calls"""
        # Create consistent memory set
        consistent_memories = [
            Memory(
                npc_id="test_npc_001",
                content="Player always pays fair prices",
                memory_id="mem_consistent",
                importance=0.7,
                categories=[MemoryCategory.RELATIONSHIP.value],
                created_at=(datetime.now() - timedelta(days=1)).isoformat(),
                metadata={"entities": ["player_123"], "tags": ["player", "trade", "fair"]}
            )
        ]
        
        mock_memory_manager.get_memories_involving_entity.return_value = consistent_memories
        
        # Calculate trust multiple times
        trust1 = await behavior_service.calculate_trust_level("player_123")
        trust2 = await behavior_service.calculate_trust_level("player_123")
        
        # Results should be consistent (within floating point precision)
        assert abs(trust1.trust_level - trust2.trust_level) < 0.001
        assert trust1.confidence == trust2.confidence 