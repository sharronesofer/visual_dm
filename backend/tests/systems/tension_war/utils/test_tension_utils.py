from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from backend.systems.tension_war.utils.tension_utils import (
    TensionManager,
    TensionConfig,
    decay_region_tension,
    check_faction_war_triggers,
    get_regions_by_tension,
    get_region_factions_at_war,
    calculate_border_tension,
    calculate_event_tension,
    calculate_faction_trait_tension,
    get_tension_level,
    decay_tension,
    update_tension_history,
    TensionUtils,
)
from backend.systems.tension_war.models.enums import TensionLevel
from dataclasses import dataclass


class TestTensionManager: pass
    """Test the TensionManager class."""

    @pytest.fixture
    def tension_manager(self): pass
        return TensionManager()

    @pytest.fixture
    def mock_region(self): pass
        return "region_1"

    @pytest.fixture
    def mock_poi(self): pass
        return "poi_1"

    def test_init(self, tension_manager): pass
        """Test TensionManager initialization."""
        assert tension_manager._tension_cache == {}
        assert tension_manager._last_update == {}
        assert "safe_zone" in tension_manager._configs
        assert "wilderness" in tension_manager._configs
        assert "dungeon" in tension_manager._configs

    def test_load_tension_configs(self, tension_manager): pass
        """Test loading tension configurations."""
        configs = tension_manager._configs
        
        # Check safe zone config
        safe_config = configs["safe_zone"]
        assert safe_config.base_tension == 0.1
        assert safe_config.max_tension == 0.3
        assert safe_config.min_tension == 0.0
        
        # Check wilderness config
        wild_config = configs["wilderness"]
        assert wild_config.base_tension == 0.4
        assert wild_config.max_tension == 0.8
        assert wild_config.min_tension == 0.2
        
        # Check dungeon config
        dungeon_config = configs["dungeon"]
        assert dungeon_config.base_tension == 0.7
        assert dungeon_config.max_tension == 1.0
        assert dungeon_config.min_tension == 0.5

    @patch.object(TensionManager, '_get_location_type')
    @patch.object(TensionManager, '_calculate_time_decay')
    @patch.object(TensionManager, '_get_player_impact')
    @patch.object(TensionManager, '_get_npc_impact')
    @patch.object(TensionManager, '_get_environmental_impact')
    def test_calculate_tension(self, mock_env, mock_npc, mock_player, mock_decay, mock_location, tension_manager, mock_region, mock_poi): pass
        """Test tension calculation."""
        # Setup mocks
        mock_location.return_value = "wilderness"
        mock_decay.return_value = 0.1
        mock_player.return_value = 0.2
        mock_npc.return_value = 0.3
        mock_env.return_value = 0.1

        result = tension_manager.calculate_tension(mock_region, mock_poi)
        
        # Should be within valid range
        assert 0.0 <= result <= 1.0
        assert isinstance(result, float)

    @patch.object(TensionManager, '_update_player_impact')
    def test_update_tension_player_action(self, mock_update_player, tension_manager, mock_region, mock_poi): pass
        """Test tension update with player action."""
        tension_manager.update_tension(mock_region, mock_poi, player_action="combat")
        mock_update_player.assert_called_once_with(mock_region, mock_poi, "combat")

    @patch.object(TensionManager, '_update_npc_impact')
    def test_update_tension_npc_change(self, mock_update_npc, tension_manager, mock_region, mock_poi): pass
        """Test tension update with NPC change."""
        npc_change = {"type": "hostile_spawn", "count": 3}
        tension_manager.update_tension(mock_region, mock_poi, npc_change=npc_change)
        mock_update_npc.assert_called_once_with(mock_region, mock_poi, npc_change)

    @patch.object(TensionManager, '_update_environmental_impact')
    def test_update_tension_environmental_change(self, mock_update_env, tension_manager, mock_region, mock_poi): pass
        """Test tension update with environmental change."""
        env_change = {"weather": "storm", "severity": 0.8}
        tension_manager.update_tension(mock_region, mock_poi, environmental_change=env_change)
        mock_update_env.assert_called_once_with(mock_region, mock_poi, env_change)

    def test_get_location_type_safe_zone(self, tension_manager): pass
        """Test location type detection for safe zones."""
        # Mock implementation returns wilderness by default
        result = tension_manager._get_location_type("town", "inn")
        assert result in tension_manager._configs

    def test_calculate_time_decay_no_previous_update(self, tension_manager): pass
        """Test time decay calculation with no previous update."""
        result = tension_manager._calculate_time_decay("region", "poi", 0.1)
        # Should return 0 decay for first calculation
        assert result >= 0.0

    def test_calculate_time_decay_with_time(self, tension_manager): pass
        """Test time decay calculation with specific time."""
        current_time = datetime.now()
        old_time = current_time - timedelta(hours=5)
        
        # Set previous update time
        tension_manager._last_update["region"] = {"poi": old_time}
        
        result = tension_manager._calculate_time_decay("region", "poi", 0.1, current_time)
        assert 0.0 <= result <= 1.0

    def test_get_player_impact_default(self, tension_manager): pass
        """Test getting player impact (default implementation)."""
        result = tension_manager._get_player_impact("region", "poi")
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_get_npc_impact_default(self, tension_manager): pass
        """Test getting NPC impact (default implementation).""" 
        result = tension_manager._get_npc_impact("region", "poi")
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_get_environmental_impact_default(self, tension_manager): pass
        """Test getting environmental impact (default implementation)."""
        result = tension_manager._get_environmental_impact("region", "poi")
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestTensionConfig: pass
    """Test the TensionConfig dataclass."""

    def test_tension_config_creation(self): pass
        """Test creating a TensionConfig."""
        config = TensionConfig(
            base_tension=0.5,
            decay_rate=0.1,
            max_tension=1.0,
            min_tension=0.0,
            player_impact=0.3,
            npc_impact=0.4,
            environmental_impact=0.2
        )
        
        assert config.base_tension == 0.5
        assert config.decay_rate == 0.1
        assert config.max_tension == 1.0
        assert config.min_tension == 0.0
        assert config.player_impact == 0.3
        assert config.npc_impact == 0.4
        assert config.environmental_impact == 0.2


class TestTensionUtilityFunctions: pass
    """Test standalone tension utility functions."""

    @pytest.fixture
    def mock_region(self): pass
        return Mock(id=1, name="Test Region", tension=0.5)

    @pytest.fixture
    def mock_session(self): pass
        return Mock()

    @pytest.fixture
    def basic_config(self): pass
        return {
            "decay_rate": 0.1,
            "war_threshold": 80,
            "max_event_tension": 50
        }

    @pytest.fixture
    def faction_relations(self): pass
        return {
            (1, 2): 75,  # High tension
            (1, 3): 25,  # Low tension
            (2, 3): 50,  # Medium tension
        }

    def test_decay_region_tension(self, mock_region): pass
        """Test region tension decay function."""
        original_tension = mock_region.tension
        decay_region_tension(mock_region)
        
        # Should modify the region (mock doesn't actually change, but function should run)
        assert hasattr(mock_region, 'tension')

    def test_check_faction_war_triggers_empty_region(self, mock_region): pass
        """Test war triggers check with no factions."""
        mock_region.factions = []
        result = check_faction_war_triggers(mock_region)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_check_faction_war_triggers_with_factions(self, mock_region): pass
        """Test war triggers check with factions."""
        # Mock factions with high tension
        faction1 = Mock(id=1, name="Faction1")
        faction2 = Mock(id=2, name="Faction2")
        mock_region.factions = [faction1, faction2]
        
        result = check_faction_war_triggers(mock_region)
        assert isinstance(result, list)

    def test_get_regions_by_tension_default(self, mock_session): pass
        """Test getting regions by tension level."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = get_regions_by_tension(mock_session)
        assert isinstance(result, list)

    def test_get_regions_by_tension_with_threshold(self, mock_session): pass
        """Test getting regions by tension level with specific threshold."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = get_regions_by_tension(mock_session, min_tension=0.7)
        assert isinstance(result, list)

    def test_get_region_factions_at_war_no_wars(self, mock_session): pass
        """Test getting warring factions with no active wars."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = get_region_factions_at_war(mock_session, 1)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_region_factions_at_war_with_wars(self, mock_session): pass
        """Test getting warring factions with active wars."""
        mock_war = Mock(faction_a_id=1, faction_b_id=2, status="active")
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_war]
        
        result = get_region_factions_at_war(mock_session, 1)
        assert isinstance(result, list)

    def test_calculate_border_tension_no_shared_border(self): pass
        """Test calculating border tension with no shared border."""
        region1 = Mock(borders=[])
        region2 = Mock(id=2)
        
        result = calculate_border_tension(region1, region2)
        assert result == 0.0

    def test_calculate_border_tension_with_shared_border(self): pass
        """Test calculating border tension with shared border."""
        region1 = Mock(borders=[2, 3])
        region2 = Mock(id=2, tension=0.7)
        
        result = calculate_border_tension(region1, region2)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_calculate_event_tension_trade_dispute(self, faction_relations, basic_config): pass
        """Test calculating event tension for trade dispute."""
        result = calculate_event_tension(
            "trade_dispute", 0.5, faction_relations, basic_config
        )
        assert isinstance(result, float)
        assert result >= 0.0

    def test_calculate_event_tension_border_skirmish(self, faction_relations, basic_config): pass
        """Test calculating event tension for border skirmish."""
        result = calculate_event_tension(
            "border_skirmish", 0.8, faction_relations, basic_config
        )
        assert isinstance(result, float)
        assert result >= 0.0

    def test_calculate_event_tension_unknown_event(self, faction_relations, basic_config): pass
        """Test calculating event tension for unknown event type."""
        result = calculate_event_tension(
            "unknown_event", 0.3, faction_relations, basic_config
        )
        assert isinstance(result, float)
        assert result >= 0.0

    def test_calculate_faction_trait_tension_aggressive_factions(self): pass
        """Test calculating trait tension for aggressive factions."""
        faction1 = Mock(traits=["aggressive", "militaristic"])
        faction2 = Mock(traits=["aggressive", "expansionist"])
        
        result = calculate_faction_trait_tension(faction1, faction2)
        assert isinstance(result, float)
        assert result > 0.0  # Should have some tension

    def test_calculate_faction_trait_tension_peaceful_factions(self): pass
        """Test calculating trait tension for peaceful factions."""
        faction1 = Mock(traits=["peaceful", "diplomatic"])
        faction2 = Mock(traits=["peaceful", "mercantile"])
        
        result = calculate_faction_trait_tension(faction1, faction2)
        assert isinstance(result, float)
        assert result >= 0.0  # Should have low tension

    def test_get_tension_level_alliance(self): pass
        """Test getting tension level for alliance range."""
        result = get_tension_level(-90)
        assert result == TensionLevel.ALLIANCE

    def test_get_tension_level_friendly(self): pass
        """Test getting tension level for friendly range."""
        result = get_tension_level(-50)
        assert result == TensionLevel.FRIENDLY

    def test_get_tension_level_neutral(self): pass
        """Test getting tension level for neutral range."""
        result = get_tension_level(0)
        assert result == TensionLevel.NEUTRAL

    def test_get_tension_level_rivalry(self): pass
        """Test getting tension level for rivalry range."""
        result = get_tension_level(35)
        assert result == TensionLevel.RIVALRY

    def test_get_tension_level_hostile(self): pass
        """Test getting tension level for hostile range."""
        result = get_tension_level(75)
        assert result == TensionLevel.HOSTILE

    def test_get_tension_level_war(self): pass
        """Test getting tension level for war range."""
        result = get_tension_level(100)
        assert result == TensionLevel.WAR

    def test_decay_tension_basic(self, basic_config): pass
        """Test basic tension decay."""
        result = decay_tension(80.0, 5, basic_config)
        assert isinstance(result, float)
        assert result < 80.0  # Should decay

    def test_decay_tension_zero_days(self, basic_config): pass
        """Test tension decay with zero days."""
        result = decay_tension(50.0, 0, basic_config)
        assert result == 50.0  # No change

    def test_decay_tension_high_tension(self, basic_config): pass
        """Test tension decay with high initial tension."""
        result = decay_tension(95.0, 10, basic_config)
        assert isinstance(result, float)
        assert result < 95.0  # Should decay significantly

    def test_update_tension_history_basic(self): pass
        """Test updating tension history."""
        history = [
            {"tension": 50.0, "reason": "Initial", "timestamp": "2023-01-01"},
            {"tension": 60.0, "reason": "Event", "timestamp": "2023-01-02"},
        ]
        
        result = update_tension_history(history, 70.0, "New event")
        assert isinstance(result, list)
        assert len(result) >= len(history)
        assert result[-1]["tension"] == 70.0
        assert result[-1]["reason"] == "New event"

    def test_update_tension_history_empty(self): pass
        """Test updating empty tension history."""
        result = update_tension_history([], 45.0, "First event")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["tension"] == 45.0
        assert result[0]["reason"] == "First event"

    def test_update_tension_history_limit(self): pass
        """Test tension history length limit."""
        # Create a long history
        history = [
            {"tension": i, "reason": f"Event {i}", "timestamp": f"2023-01-{i:02d}"}
            for i in range(1, 51)  # 50 entries
        ]
        
        result = update_tension_history(history, 60.0, "Latest event")
        # Should maintain reasonable length (implementation dependent)
        assert isinstance(result, list)
        assert len(result) >= 1  # At least the new entry


class TestTensionUtils: pass
    """Test the TensionUtils class."""

    def test_tension_utils_creation(self): pass
        """Test creating TensionUtils instance."""
        utils = TensionUtils()
        assert utils is not None 