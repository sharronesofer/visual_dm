"""
Unit tests for the Narrative Moderator

Tests the narrative intelligence weighting system as required by the Development Bible.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from backend.systems.chaos.core.narrative_moderator import (
    NarrativeModerator, NarrativeTheme, StoryBeat, NarrativePriority
)
from backend.systems.chaos.core.config import ChaosConfig


@pytest.fixture
def chaos_config():
    """Create a test chaos configuration"""
    config = ChaosConfig()
    return config


@pytest.fixture
def narrative_moderator(chaos_config):
    """Create a narrative moderator for testing"""
    return NarrativeModerator(chaos_config)


@pytest.fixture
def mock_narrative_context():
    """Create mock narrative context for testing"""
    mock_context = Mock()
    mock_context.current_story_beats = ["intro", "rising_action"]
    mock_context.dramatic_tension_level = 0.6
    mock_context.recent_major_events = ["political_crisis"]
    mock_context.narrative_themes = ["political_intrigue", "economic_drama"]
    mock_context.player_engagement_level = 0.7
    return mock_context


@pytest.fixture
def mock_pressure_data():
    """Create mock pressure data for testing"""
    mock_data = Mock()
    mock_data.pressure_sources = {
        'economic': 0.6,
        'political': 0.8,
        'social': 0.4,
        'environmental': 0.3,
        'diplomatic': 0.5,
        'temporal': 0.2
    }
    return mock_data


class TestNarrativeModeratorInitialization:
    """Test narrative moderator initialization and configuration"""
    
    def test_narrative_moderator_creation(self, chaos_config):
        """Test that narrative moderator can be created with proper defaults"""
        moderator = NarrativeModerator(chaos_config)
        
        assert moderator.config is chaos_config
        assert not moderator._initialized
        assert not moderator._running
        assert len(moderator.active_themes) == 0
        assert len(moderator.active_story_beats) == 0
        assert moderator.current_engagement == 0.7
        assert moderator.current_tension == 0.5
    
    @pytest.mark.asyncio
    async def test_initialization_loads_default_themes(self, narrative_moderator):
        """Test that initialization loads default narrative themes"""
        await narrative_moderator.initialize()
        
        assert narrative_moderator._initialized
        assert len(narrative_moderator.active_themes) > 0
        
        # Check that default themes are loaded
        theme_names = [theme.name for theme in narrative_moderator.active_themes.values()]
        assert "Political Intrigue" in theme_names
        assert "Economic Drama" in theme_names
        assert "Social Upheaval" in theme_names
        assert "Mystical Forces" in theme_names
    
    def test_event_compatibility_matrix(self, narrative_moderator):
        """Test that event compatibility matrix is initialized"""
        compatibility = narrative_moderator.event_theme_compatibility
        
        assert isinstance(compatibility, dict)
        assert 'economic_crisis' in compatibility
        assert 'political_upheaval' in compatibility
        assert 'temporal_anomaly' in compatibility
        
        # Check that values are reasonable
        for event_type, value in compatibility.items():
            assert 0.0 <= value <= 2.0


class TestNarrativeThemeManagement:
    """Test narrative theme management"""
    
    @pytest.mark.asyncio
    async def test_add_narrative_theme(self, narrative_moderator):
        """Test adding a new narrative theme"""
        await narrative_moderator.initialize()
        
        result = await narrative_moderator.add_narrative_theme(
            theme_id="test_theme",
            name="Test Theme",
            description="A test narrative theme",
            priority="central",
            weight_modifier=1.5,
            related_events=["economic_crisis", "political_upheaval"],
            duration_hours=24.0
        )
        
        assert result is True
        assert "test_theme" in narrative_moderator.active_themes
        
        theme = narrative_moderator.active_themes["test_theme"]
        assert theme.name == "Test Theme"
        assert theme.priority == NarrativePriority.CENTRAL
        assert theme.weight_modifier == 1.5
        assert "economic_crisis" in theme.related_events
        assert theme.is_active()
    
    @pytest.mark.asyncio
    async def test_add_theme_invalid_priority(self, narrative_moderator):
        """Test adding theme with invalid priority"""
        await narrative_moderator.initialize()
        
        result = await narrative_moderator.add_narrative_theme(
            theme_id="invalid_theme",
            name="Invalid Theme",
            description="Theme with invalid priority",
            priority="invalid_priority",
            weight_modifier=1.0,
            related_events=[]
        )
        
        assert result is False
        assert "invalid_theme" not in narrative_moderator.active_themes
    
    @pytest.mark.asyncio
    async def test_remove_narrative_theme(self, narrative_moderator):
        """Test removing a narrative theme"""
        await narrative_moderator.initialize()
        
        # Add a theme first
        await narrative_moderator.add_narrative_theme(
            theme_id="removable_theme",
            name="Removable Theme",
            description="A theme to be removed",
            priority="background",
            weight_modifier=1.0,
            related_events=[]
        )
        
        assert "removable_theme" in narrative_moderator.active_themes
        
        # Remove the theme
        result = await narrative_moderator.remove_narrative_theme("removable_theme")
        
        assert result is True
        assert "removable_theme" not in narrative_moderator.active_themes
    
    @pytest.mark.asyncio
    async def test_theme_expiration(self, narrative_moderator):
        """Test that themes expire correctly"""
        await narrative_moderator.initialize()
        
        # Add a theme with very short duration
        await narrative_moderator.add_narrative_theme(
            theme_id="short_theme",
            name="Short Theme",
            description="A short-lived theme",
            priority="supporting",
            weight_modifier=1.2,
            related_events=[],
            duration_hours=0.001  # Very short duration
        )
        
        assert "short_theme" in narrative_moderator.active_themes
        
        # Wait for expiration
        await asyncio.sleep(0.1)
        
        # Process cleanup
        await narrative_moderator._cleanup_expired_elements()
        
        assert "short_theme" not in narrative_moderator.active_themes


class TestStoryBeatManagement:
    """Test story beat management"""
    
    @pytest.mark.asyncio
    async def test_add_story_beat(self, narrative_moderator):
        """Test adding a story beat"""
        await narrative_moderator.initialize()
        
        result = await narrative_moderator.add_story_beat(
            beat_id="test_beat",
            name="Test Story Beat",
            description="A test story beat",
            drama_level=0.8,
            engagement_impact=0.3,
            chaos_compatibility=1.2,
            duration_hours=2.0
        )
        
        assert result is True
        assert "test_beat" in narrative_moderator.active_story_beats
        
        beat = narrative_moderator.active_story_beats["test_beat"]
        assert beat.name == "Test Story Beat"
        assert beat.drama_level == 0.8
        assert beat.engagement_impact == 0.3
        assert beat.chaos_compatibility == 1.2
        assert beat.is_active()
    
    @pytest.mark.asyncio
    async def test_story_beat_value_clamping(self, narrative_moderator):
        """Test that story beat values are clamped to valid ranges"""
        await narrative_moderator.initialize()
        
        result = await narrative_moderator.add_story_beat(
            beat_id="clamped_beat",
            name="Clamped Beat",
            description="Beat with out-of-range values",
            drama_level=2.0,  # Should be clamped to 1.0
            engagement_impact=-1.0,  # Should be clamped to -0.5
            chaos_compatibility=3.0,  # Should be clamped to 2.0
            duration_hours=1.0
        )
        
        assert result is True
        beat = narrative_moderator.active_story_beats["clamped_beat"]
        assert beat.drama_level == 1.0
        assert beat.engagement_impact == -0.5
        assert beat.chaos_compatibility == 2.0
    
    @pytest.mark.asyncio
    async def test_story_beat_expiration(self, narrative_moderator):
        """Test that story beats expire correctly"""
        await narrative_moderator.initialize()
        
        # Add a beat with very short duration
        await narrative_moderator.add_story_beat(
            beat_id="short_beat",
            name="Short Beat",
            description="A short-lived beat",
            drama_level=0.5,
            engagement_impact=0.1,
            chaos_compatibility=1.0,
            duration_hours=0.001  # Very short duration
        )
        
        assert "short_beat" in narrative_moderator.active_story_beats
        
        # Wait for expiration
        await asyncio.sleep(0.1)
        
        # Process cleanup
        await narrative_moderator._cleanup_expired_elements()
        
        assert "short_beat" not in narrative_moderator.active_story_beats


class TestEngagementAndTensionTracking:
    """Test engagement and tension level tracking"""
    
    @pytest.mark.asyncio
    async def test_update_engagement_level(self, narrative_moderator):
        """Test updating player engagement level"""
        await narrative_moderator.initialize()
        
        result = await narrative_moderator.update_engagement_level(0.9)
        
        assert result is True
        assert narrative_moderator.current_engagement == 0.9
        assert len(narrative_moderator.engagement_history) > 0
    
    @pytest.mark.asyncio
    async def test_update_tension_level(self, narrative_moderator):
        """Test updating dramatic tension level"""
        await narrative_moderator.initialize()
        
        result = await narrative_moderator.update_tension_level(0.3)
        
        assert result is True
        assert narrative_moderator.current_tension == 0.3
        assert len(narrative_moderator.tension_history) > 0
    
    @pytest.mark.asyncio
    async def test_engagement_clamping(self, narrative_moderator):
        """Test that engagement values are clamped to 0-1 range"""
        await narrative_moderator.initialize()
        
        # Test high value
        await narrative_moderator.update_engagement_level(2.0)
        assert narrative_moderator.current_engagement == 1.0
        
        # Test low value
        await narrative_moderator.update_engagement_level(-0.5)
        assert narrative_moderator.current_engagement == 0.0
    
    @pytest.mark.asyncio
    async def test_tension_clamping(self, narrative_moderator):
        """Test that tension values are clamped to 0-1 range"""
        await narrative_moderator.initialize()
        
        # Test high value
        await narrative_moderator.update_tension_level(1.5)
        assert narrative_moderator.current_tension == 1.0
        
        # Test low value
        await narrative_moderator.update_tension_level(-0.2)
        assert narrative_moderator.current_tension == 0.0


class TestTensionAndEngagementCalculation:
    """Test automatic tension and engagement calculation"""
    
    def test_calculate_current_tension_with_story_beats(self, narrative_moderator):
        """Test tension calculation with active story beats"""
        # Add high-drama story beat
        high_drama_beat = StoryBeat(
            beat_id="dramatic_beat",
            name="Dramatic Beat",
            description="High drama beat",
            drama_level=0.9,
            engagement_impact=0.2,
            chaos_compatibility=1.0,
            duration_hours=2.0,
            created_at=datetime.now()
        )
        narrative_moderator.active_story_beats["dramatic_beat"] = high_drama_beat
        
        tension = narrative_moderator._calculate_current_tension()
        
        # Base tension (0.5) + story beat contribution (0.9 * 0.2) = 0.68
        assert tension > 0.5
        assert tension <= 1.0
    
    def test_calculate_current_tension_with_themes(self, narrative_moderator):
        """Test tension calculation with high-priority themes"""
        # Add critical theme
        critical_theme = NarrativeTheme(
            theme_id="critical_theme",
            name="Critical Theme",
            description="Critical narrative theme",
            priority=NarrativePriority.CRITICAL,
            weight_modifier=2.0,
            active_until=None,
            related_events=[]
        )
        narrative_moderator.active_themes["critical_theme"] = critical_theme
        
        tension = narrative_moderator._calculate_current_tension()
        
        # Should be higher than base tension due to critical theme
        assert tension > 0.5
    
    def test_calculate_current_engagement_with_beats(self, narrative_moderator):
        """Test engagement calculation with story beats"""
        # Add engaging story beat
        engaging_beat = StoryBeat(
            beat_id="engaging_beat",
            name="Engaging Beat",
            description="High engagement beat",
            drama_level=0.6,
            engagement_impact=0.4,
            chaos_compatibility=1.0,
            duration_hours=2.0,
            created_at=datetime.now()
        )
        narrative_moderator.active_story_beats["engaging_beat"] = engaging_beat
        
        engagement = narrative_moderator._calculate_current_engagement()
        
        # Base engagement (0.7) + story beat contribution (0.4 * 0.15) = 0.76
        assert engagement > 0.7
        assert engagement <= 1.0


class TestEventWeightCalculation:
    """Test narrative event weight calculation"""
    
    @pytest.mark.asyncio
    async def test_get_event_weights_basic(self, narrative_moderator, mock_narrative_context, mock_pressure_data):
        """Test basic event weight calculation"""
        await narrative_moderator.initialize()
        
        weights = await narrative_moderator.get_event_weights(mock_narrative_context, mock_pressure_data)
        
        assert isinstance(weights, dict)
        assert len(weights) > 0
        assert narrative_moderator.metrics['weight_calculations'] > 0
    
    @pytest.mark.asyncio
    async def test_event_weights_with_matching_themes(self, narrative_moderator, mock_narrative_context, mock_pressure_data):
        """Test that matching themes increase event weights"""
        await narrative_moderator.initialize()
        
        # Add a central theme for political events
        await narrative_moderator.add_narrative_theme(
            theme_id="political_central",
            name="Political Central Theme",
            description="Central political theme",
            priority="central",
            weight_modifier=1.5,
            related_events=["political_upheaval"]
        )
        
        weights = await narrative_moderator.get_event_weights(mock_narrative_context, mock_pressure_data)
        
        # Should have increased weight for political events
        political_weight = weights.get("event_type_political_upheaval", 1.0)
        assert political_weight > 1.0
    
    @pytest.mark.asyncio
    async def test_event_weights_with_critical_themes(self, narrative_moderator, mock_narrative_context, mock_pressure_data):
        """Test that critical themes heavily modify weights"""
        await narrative_moderator.initialize()
        
        # Add a critical theme
        await narrative_moderator.add_narrative_theme(
            theme_id="critical_economic",
            name="Critical Economic Theme",
            description="Critical economic narrative",
            priority="critical",
            weight_modifier=2.0,
            related_events=["economic_crisis"]
        )
        
        weights = await narrative_moderator.get_event_weights(mock_narrative_context, mock_pressure_data)
        
        # Critical themes should significantly boost matching events
        economic_weight = weights.get("event_type_economic_crisis", 1.0)
        assert economic_weight >= 1.8  # Critical theme should provide significant boost
    
    def test_calculate_global_narrative_modifier_high_tension(self, narrative_moderator):
        """Test global modifier with high tension"""
        narrative_moderator.current_tension = 0.9  # Very high tension
        narrative_moderator.current_engagement = 0.7  # Normal engagement
        
        modifier = narrative_moderator._calculate_global_narrative_modifier()
        
        # High tension should reduce chaos
        assert modifier < 1.0
        assert narrative_moderator.metrics['tension_modifications'] > 0
    
    def test_calculate_global_narrative_modifier_low_engagement(self, narrative_moderator):
        """Test global modifier with low engagement"""
        narrative_moderator.current_tension = 0.5  # Normal tension
        narrative_moderator.current_engagement = 0.3  # Low engagement
        
        modifier = narrative_moderator._calculate_global_narrative_modifier()
        
        # Low engagement should increase chaos
        assert modifier > 1.0
        assert narrative_moderator.metrics['engagement_adjustments'] > 0
    
    def test_calculate_global_narrative_modifier_low_tension(self, narrative_moderator):
        """Test global modifier with low tension"""
        narrative_moderator.current_tension = 0.2  # Low tension
        narrative_moderator.current_engagement = 0.7  # Normal engagement
        
        modifier = narrative_moderator._calculate_global_narrative_modifier()
        
        # Low tension should increase chaos for excitement
        assert modifier > 1.0


class TestThemePriorities:
    """Test theme priority management"""
    
    @pytest.mark.asyncio
    async def test_set_theme_priority(self, narrative_moderator):
        """Test setting theme priority"""
        await narrative_moderator.initialize()
        
        result = await narrative_moderator.set_theme_priority("test_theme", 1.5)
        
        assert result is True
        assert narrative_moderator.theme_priorities["test_theme"] == 1.5
    
    @pytest.mark.asyncio
    async def test_theme_priority_clamping(self, narrative_moderator):
        """Test that theme priorities are clamped to valid range"""
        await narrative_moderator.initialize()
        
        # Test high value
        await narrative_moderator.set_theme_priority("high_theme", 5.0)
        assert narrative_moderator.theme_priorities["high_theme"] == 2.0
        
        # Test low value
        await narrative_moderator.set_theme_priority("low_theme", -1.0)
        assert narrative_moderator.theme_priorities["low_theme"] == 0.0


class TestNarrativeStatus:
    """Test narrative status reporting"""
    
    @pytest.mark.asyncio
    async def test_get_narrative_status(self, narrative_moderator):
        """Test getting narrative status"""
        await narrative_moderator.initialize()
        
        # Add some content for testing
        await narrative_moderator.add_narrative_theme(
            theme_id="status_theme",
            name="Status Theme",
            description="Theme for status testing",
            priority="supporting",
            weight_modifier=1.2,
            related_events=["test_event"]
        )
        
        await narrative_moderator.add_story_beat(
            beat_id="status_beat",
            name="Status Beat",
            description="Beat for status testing",
            drama_level=0.7,
            engagement_impact=0.2,
            chaos_compatibility=1.1,
            duration_hours=2.0
        )
        
        status = narrative_moderator.get_narrative_status()
        
        assert 'current_tension' in status
        assert 'current_engagement' in status
        assert 'active_themes' in status
        assert 'active_story_beats' in status
        assert 'metrics' in status
        
        # Check that our added content is present
        assert 'status_theme' in status['active_themes']
        assert 'status_beat' in status['active_story_beats']
        
        # Check theme details
        theme_status = status['active_themes']['status_theme']
        assert theme_status['name'] == "Status Theme"
        assert theme_status['priority'] == "supporting"
        assert theme_status['weight_modifier'] == 1.2
        assert theme_status['is_active'] is True
        
        # Check beat details
        beat_status = status['active_story_beats']['status_beat']
        assert beat_status['name'] == "Status Beat"
        assert beat_status['drama_level'] == 0.7
        assert beat_status['is_active'] is True


class TestNarrativeModeratorLifecycle:
    """Test narrative moderator lifecycle management"""
    
    @pytest.mark.asyncio
    async def test_start_stop_cycle(self, narrative_moderator):
        """Test starting and stopping the narrative moderator"""
        assert not narrative_moderator._running
        
        await narrative_moderator.start()
        assert narrative_moderator._running
        assert narrative_moderator._monitoring_task is not None
        
        await narrative_moderator.stop()
        assert not narrative_moderator._running
        assert narrative_moderator._monitoring_task.cancelled()
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_updates_analysis(self, narrative_moderator):
        """Test that monitoring loop updates narrative analysis"""
        await narrative_moderator.initialize()
        
        initial_tension_history_len = len(narrative_moderator.tension_history)
        initial_engagement_history_len = len(narrative_moderator.engagement_history)
        
        # Run one iteration of the analysis update
        await narrative_moderator._update_narrative_analysis()
        
        # Should have added to history
        assert len(narrative_moderator.tension_history) > initial_tension_history_len
        assert len(narrative_moderator.engagement_history) > initial_engagement_history_len
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_error_handling(self, narrative_moderator):
        """Test that monitoring loop handles errors gracefully"""
        await narrative_moderator.initialize()
        
        # Mock the analysis update to raise an error
        with patch.object(narrative_moderator, '_update_narrative_analysis', side_effect=Exception("Test error")):
            narrative_moderator._running = True
            
            # Start monitoring loop for short time
            task = asyncio.create_task(narrative_moderator._monitoring_loop())
            await asyncio.sleep(0.1)
            
            narrative_moderator._running = False
            await task
            
            # Should complete without raising exception
            assert True


class TestNarrativeThemeModel:
    """Test NarrativeTheme data model"""
    
    def test_narrative_theme_creation(self):
        """Test creating a narrative theme"""
        theme = NarrativeTheme(
            theme_id="test_theme",
            name="Test Theme",
            description="A test theme",
            priority=NarrativePriority.CENTRAL,
            weight_modifier=1.5,
            active_until=None,
            related_events=["event1", "event2"]
        )
        
        assert theme.theme_id == "test_theme"
        assert theme.priority == NarrativePriority.CENTRAL
        assert theme.weight_modifier == 1.5
        assert theme.is_active() is True
        assert len(theme.related_events) == 2
    
    def test_narrative_theme_expiration(self):
        """Test narrative theme expiration"""
        past_time = datetime.now() - timedelta(hours=1)
        
        theme = NarrativeTheme(
            theme_id="expired_theme",
            name="Expired Theme",
            description="An expired theme",
            priority=NarrativePriority.SUPPORTING,
            weight_modifier=1.0,
            active_until=past_time,
            related_events=[]
        )
        
        assert theme.is_active() is False


class TestStoryBeatModel:
    """Test StoryBeat data model"""
    
    def test_story_beat_creation(self):
        """Test creating a story beat"""
        beat = StoryBeat(
            beat_id="test_beat",
            name="Test Beat",
            description="A test beat",
            drama_level=0.8,
            engagement_impact=0.3,
            chaos_compatibility=1.2,
            duration_hours=3.0,
            created_at=datetime.now()
        )
        
        assert beat.beat_id == "test_beat"
        assert beat.drama_level == 0.8
        assert beat.engagement_impact == 0.3
        assert beat.chaos_compatibility == 1.2
        assert beat.is_active() is True
    
    def test_story_beat_expiration(self):
        """Test story beat expiration"""
        past_time = datetime.now() - timedelta(hours=2)
        
        beat = StoryBeat(
            beat_id="expired_beat",
            name="Expired Beat",
            description="An expired beat",
            drama_level=0.5,
            engagement_impact=0.1,
            chaos_compatibility=1.0,
            duration_hours=1.0,  # 1 hour duration, created 2 hours ago
            created_at=past_time
        )
        
        assert beat.is_active() is False


@pytest.mark.asyncio
async def test_integration_narrative_weighting():
    """Integration test for narrative weighting system"""
    config = ChaosConfig()
    moderator = NarrativeModerator(config)
    
    await moderator.initialize()
    
    # Add a critical political theme
    await moderator.add_narrative_theme(
        theme_id="political_crisis",
        name="Political Crisis Theme",
        description="Critical political narrative",
        priority="critical",
        weight_modifier=2.0,
        related_events=["political_upheaval", "faction_conflict"]
    )
    
    # Set high tension but low engagement
    await moderator.update_tension_level(0.9)
    await moderator.update_engagement_level(0.3)
    
    # Create mock contexts
    mock_context = Mock()
    mock_pressure = Mock()
    mock_pressure.pressure_sources = {'political': 0.8}
    
    # Get event weights
    weights = await moderator.get_event_weights(mock_context, mock_pressure)
    
    # Should have weights for political events
    assert len(weights) > 0
    
    # Critical theme should boost political events significantly
    political_weight = weights.get("event_type_political_upheaval", 1.0)
    assert political_weight > 1.5
    
    # Low engagement should increase overall chaos
    assert moderator.metrics['engagement_adjustments'] > 0 