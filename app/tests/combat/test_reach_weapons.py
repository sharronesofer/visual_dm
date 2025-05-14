"""
Tests for reach weapon mechanics in combat.
"""

import pytest
from unittest.mock import Mock, patch
from app.combat.reach_weapons import ReachWeaponHandler
from app.core.models.combat import Combat, CombatParticipant

@pytest.fixture
def mock_combat():
    """Create a mock combat instance with a tactical grid."""
    combat = Mock(spec=Combat)
    combat.id = 1
    combat.tactical_grid = {
        (0, 0): {'terrain': 'plain'},
        (1, 0): {'terrain': 'plain'},
        (2, 0): {'terrain': 'wall', 'blocks_sight': True},
        (0, 1): {'terrain': 'plain'},
        (1, 1): {'terrain': 'plain'},
        (2, 1): {'terrain': 'plain'},
    }
    return combat

@pytest.fixture
def mock_participants():
    """Create mock combat participants with different weapons."""
    spear_wielder = Mock(spec=CombatParticipant)
    spear_wielder.id = 1
    spear_wielder.position = (0, 0)
    spear_wielder.status_effects = [{'type': 'reach_weapon', 'weapon_type': 'spear'}]

    pike_wielder = Mock(spec=CombatParticipant)
    pike_wielder.id = 2
    pike_wielder.position = (0, 1)
    pike_wielder.status_effects = [{'type': 'reach_weapon', 'weapon_type': 'pike'}]

    halberd_wielder = Mock(spec=CombatParticipant)
    halberd_wielder.id = 3
    halberd_wielder.position = (1, 0)
    halberd_wielder.status_effects = [{'type': 'reach_weapon', 'weapon_type': 'halberd'}]

    whip_wielder = Mock(spec=CombatParticipant)
    whip_wielder.id = 4
    whip_wielder.position = (1, 1)
    whip_wielder.status_effects = [{'type': 'reach_weapon', 'weapon_type': 'whip'}]

    return {
        'spear': spear_wielder,
        'pike': pike_wielder,
        'halberd': halberd_wielder,
        'whip': whip_wielder
    }

@pytest.fixture
def handler(mock_combat):
    """Create a ReachWeaponHandler instance with mocked combat."""
    with patch('app.combat.reach_weapons.Combat') as mock_combat_class:
        mock_combat_class.query.get.return_value = mock_combat
        return ReachWeaponHandler(mock_combat.id)

class TestReachWeaponHandler:
    """Test suite for ReachWeaponHandler class."""

    def test_get_attack_range(self, handler, mock_participants):
        """Test attack range calculation for different weapons."""
        # Test spear range
        assert handler._get_attack_range(mock_participants['spear']) == 2

        # Test pike range
        assert handler._get_attack_range(mock_participants['pike']) == 3

        # Test halberd range
        assert handler._get_attack_range(mock_participants['halberd']) == 2

        # Test whip range
        assert handler._get_attack_range(mock_participants['whip']) == 2

        # Test default range for participant without reach weapon
        participant = Mock(spec=CombatParticipant)
        participant.status_effects = []
        assert handler._get_attack_range(participant) == 1

    def test_has_minimum_range(self, handler, mock_participants):
        """Test minimum range requirements."""
        # Only pike should have minimum range
        assert handler._has_minimum_range(mock_participants['pike']) is True
        assert handler._has_minimum_range(mock_participants['spear']) is False
        assert handler._has_minimum_range(mock_participants['halberd']) is False
        assert handler._has_minimum_range(mock_participants['whip']) is False

    def test_get_reach_weapon_type(self, handler, mock_participants):
        """Test weapon type identification."""
        assert handler._get_reach_weapon_type(mock_participants['spear']) == 'spear'
        assert handler._get_reach_weapon_type(mock_participants['pike']) == 'pike'
        assert handler._get_reach_weapon_type(mock_participants['halberd']) == 'halberd'
        assert handler._get_reach_weapon_type(mock_participants['whip']) == 'whip'

        # Test participant without reach weapon
        participant = Mock(spec=CombatParticipant)
        participant.status_effects = []
        assert handler._get_reach_weapon_type(participant) is None

    def test_check_reach_attack_valid(self, handler, mock_participants):
        """Test attack validation logic."""
        with patch('app.combat.reach_weapons.CombatParticipant') as mock_participant_class:
            # Test valid attack within range
            mock_participant_class.query.get.side_effect = lambda id: (
                mock_participants['spear'] if id == 1 else Mock(spec=CombatParticipant, position=(1, 0))
            )
            is_valid, reason = handler.check_reach_attack_valid(1, 2)
            assert is_valid is True
            assert reason is None

            # Test attack out of range
            target = Mock(spec=CombatParticipant, position=(3, 3))
            mock_participant_class.query.get.side_effect = lambda id: (
                mock_participants['spear'] if id == 1 else target
            )
            is_valid, reason = handler.check_reach_attack_valid(1, 2)
            assert is_valid is False
            assert "out of range" in reason

            # Test pike's minimum range requirement
            close_target = Mock(spec=CombatParticipant, position=(0, 2))
            mock_participant_class.query.get.side_effect = lambda id: (
                mock_participants['pike'] if id == 1 else close_target
            )
            is_valid, reason = handler.check_reach_attack_valid(1, 2)
            assert is_valid is False
            assert "too close" in reason

    def test_apply_reach_weapon_effects(self, handler, mock_participants):
        """Test weapon-specific effects application."""
        with patch('app.combat.reach_weapons.CombatParticipant') as mock_participant_class:
            # Test spear effects
            mock_participant_class.query.get.return_value = mock_participants['spear']
            effects = handler.apply_reach_weapon_effects(1, 'normal')
            assert effects['damage_multiplier'] == 1.2

            effects = handler.apply_reach_weapon_effects(1, 'opportunity')
            assert effects['damage_multiplier'] == 1.5

            # Test halberd effects
            mock_participant_class.query.get.return_value = mock_participants['halberd']
            effects = handler.apply_reach_weapon_effects(1, 'normal')
            assert effects['armor_penetration'] == 0.2

            effects = handler.apply_reach_weapon_effects(1, 'charge')
            assert effects['damage_multiplier'] == 1.3

            # Test pike effects
            mock_participant_class.query.get.return_value = mock_participants['pike']
            effects = handler.apply_reach_weapon_effects(1, 'normal')
            assert effects['damage_multiplier'] == 1.1
            assert effects['critical_range_bonus'] == 1

            # Test whip effects
            mock_participant_class.query.get.return_value = mock_participants['whip']
            effects = handler.apply_reach_weapon_effects(1, 'normal')
            assert effects['status_effect_chance'] == 0.2
            assert effects['pull_strength'] == 1

    def test_get_threatened_hexes(self, handler, mock_participants):
        """Test threatened hex calculation."""
        with patch('app.combat.reach_weapons.CombatParticipant') as mock_participant_class:
            # Test spear threatened hexes
            mock_participant_class.query.get.return_value = mock_participants['spear']
            hexes = handler.get_threatened_hexes(1)
            assert len(hexes) > 0
            # Verify that hexes within range 2 are included
            assert (1, 0) in hexes
            assert (0, 1) in hexes

            # Test pike threatened hexes
            mock_participant_class.query.get.return_value = mock_participants['pike']
            hexes = handler.get_threatened_hexes(2)
            assert len(hexes) > 0
            # Verify that hexes within range 3 are included, but not adjacent hexes
            assert (0, 4) in hexes  # Far hex
            assert (0, 2) not in hexes  # Adjacent hex (minimum range)

    def test_calculate_distance(self, handler):
        """Test hex grid distance calculation."""
        assert handler._calculate_distance((0, 0), (1, 0)) == 1
        assert handler._calculate_distance((0, 0), (2, 0)) == 2
        assert handler._calculate_distance((0, 0), (1, 1)) == 2
        assert handler._calculate_distance((0, 0), (2, 2)) == 4

    def test_get_line(self, handler):
        """Test line calculation between hexes."""
        # Test straight line
        line = handler._get_line((0, 0), (2, 0))
        assert line == [(0, 0), (1, 0), (2, 0)]

        # Test diagonal line
        line = handler._get_line((0, 0), (2, 2))
        assert len(line) == 5  # Should include intermediate points
        assert line[0] == (0, 0)
        assert line[-1] == (2, 2)

    def test_has_line_of_sight(self, handler, mock_combat):
        """Test line of sight checking."""
        # Test clear line of sight
        assert handler._has_line_of_sight((0, 0), (1, 1)) is True

        # Test blocked by wall
        assert handler._has_line_of_sight((0, 0), (2, 0)) is False

        # Test with no tactical grid
        handler.combat.tactical_grid = None
        assert handler._has_line_of_sight((0, 0), (2, 0)) is True 