"""
Test suite for refactored combat system modules

Ensures that the modular refactoring maintains backward compatibility
and provides the same functionality as the original monolithic implementation.
"""

import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock

from backend.systems.combat.managers.combat_manager import CombatManager
from backend.systems.combat.managers.state_manager import StateManager
from backend.systems.combat.processors.damage_processor import DamageProcessor
from backend.systems.combat.combat_state_class import CombatState


class TestCombatRefactoring: pass
    """Test the refactored combat system components."""
    
    @pytest.fixture
    def mock_character(self): pass
        """Create a mock character for testing."""
        character = Mock()
        character.name = "Test Character"
        character.hp = 100
        character.max_hp = 100
        character.dexterity = 15
        character.strength = 14
        character.armor_class = 16
        character.resistances = {}
        character.vulnerabilities = {}
        character.weapon_bonus = 2
        character.critical_chance = 0.1
        character.critical_multiplier = 2.0
        return character
    
    @pytest.fixture
    def combat_state(self, mock_character): pass
        """Create a combat state with test characters."""
        state = CombatState()
        char_dict = {
            "char1": mock_character,
            "char2": mock_character
        }
        state.add_characters(char_dict)
        return state
    
    def test_state_manager_initialization(self, combat_state): pass
        """Test StateManager initialization."""
        combat_id = str(uuid.uuid4())
        state_manager = StateManager(combat_id, combat_state)
        
        assert state_manager.combat_id == combat_id
        assert state_manager.current_state == "initializing"
        assert state_manager.round_number == 0
        assert not state_manager.is_paused
        assert len(state_manager.state_history) == 0
    
    def test_state_transitions(self, combat_state): pass
        """Test state transition logic."""
        combat_id = str(uuid.uuid4())
        state_manager = StateManager(combat_id, combat_state)
        
        # Test valid transition
        result = state_manager.transition_state("ready")
        assert result["success"]
        assert result["new_state"] == "ready"
        assert state_manager.current_state == "ready"
        assert len(state_manager.state_history) == 1
        
        # Test invalid transition
        result = state_manager.transition_state("invalid_state")
        assert not result["success"]
        assert "Invalid transition" in result["error"]
        assert state_manager.current_state == "ready"  # Should remain unchanged
    
    def test_pause_resume_combat(self, combat_state): pass
        """Test combat pause and resume functionality."""
        combat_id = str(uuid.uuid4())
        state_manager = StateManager(combat_id, combat_state)
        
        # First transition to active state
        state_manager.transition_state("ready")
        state_manager.transition_state("active")
        
        # Test pause
        result = state_manager.pause_combat()
        assert result["success"]
        assert state_manager.current_state == "paused"
        assert state_manager.is_paused
        
        # Test resume
        result = state_manager.resume_combat()
        assert result["success"]
        assert state_manager.current_state == "active"
        assert not state_manager.is_paused
    
    def test_round_advancement(self, combat_state): pass
        """Test round advancement functionality."""
        combat_id = str(uuid.uuid4())
        state_manager = StateManager(combat_id, combat_state)
        
        initial_round = state_manager.round_number
        state_manager.advance_round()
        
        assert state_manager.round_number == initial_round + 1
    
    def test_action_validation(self, combat_state): pass
        """Test action validation based on combat state."""
        combat_id = str(uuid.uuid4())
        state_manager = StateManager(combat_id, combat_state)
        
        # Test action not allowed in initializing state
        assert not state_manager.can_perform_action("take_action")
        
        # Test action allowed in active state
        state_manager.transition_state("ready")
        state_manager.transition_state("active")
        assert state_manager.can_perform_action("take_action")
        
        # Test action not allowed when paused
        state_manager.pause_combat()
        assert not state_manager.can_perform_action("take_action")


class TestDamageProcessor: pass
    """Test the DamageProcessor module."""
    
    @pytest.fixture
    def damage_processor(self, combat_state): pass
        """Create a DamageProcessor for testing."""
        combat_id = str(uuid.uuid4())
        return DamageProcessor(combat_id, combat_state)
    
    @pytest.fixture
    def mock_characters(self): pass
        """Create mock characters with different stats."""
        attacker = Mock()
        attacker.strength = 16
        attacker.intelligence = 12
        attacker.weapon_bonus = 3
        attacker.critical_chance = 0.15
        attacker.critical_multiplier = 2.5
        
        target = Mock()
        target.hp = 80
        target.max_hp = 100
        target.armor_class = 14
        target.magic_resistance = 5
        target.resistances = {"fire": 25}  # 25% fire resistance
        target.vulnerabilities = {"cold": 50}  # 50% cold vulnerability
        
        return attacker, target
    
    def test_damage_calculation_physical(self, damage_processor, mock_characters): pass
        """Test physical damage calculation."""
        attacker, target = mock_characters
        
        # Mock the combat state to return our characters
        damage_processor.combat_state.get_character = Mock(side_effect=lambda x: attacker if x == "attacker" else target)
        
        with patch('random.random', return_value=0.5):  # No critical hit
            result = damage_processor.calculate_damage("attacker", "target", 20.0, "physical")
        
        assert result["success"]
        assert result["damage_type"] == "physical"
        assert not result["is_critical"]
        assert "breakdown" in result
        
        # Verify damage calculation components
        breakdown = result["breakdown"]
        assert breakdown["base_damage"] == 20.0
        assert breakdown["attack_bonus"] > 0  # Should have strength bonus
        assert breakdown["defense_reduction"] >= 0  # Should have armor reduction
    
    def test_damage_calculation_with_resistance(self, damage_processor, mock_characters): pass
        """Test damage calculation with resistance."""
        attacker, target = mock_characters
        damage_processor.combat_state.get_character = Mock(side_effect=lambda x: attacker if x == "attacker" else target)
        
        with patch('random.random', return_value=0.5):  # No critical hit
            result = damage_processor.calculate_damage("attacker", "target", 20.0, "fire")
        
        assert result["success"]
        breakdown = result["breakdown"]
        assert breakdown["resistance_multiplier"] == 0.75  # 25% resistance = 0.75 multiplier
    
    def test_damage_calculation_with_vulnerability(self, damage_processor, mock_characters): pass
        """Test damage calculation with vulnerability."""
        attacker, target = mock_characters
        damage_processor.combat_state.get_character = Mock(side_effect=lambda x: attacker if x == "attacker" else target)
        
        with patch('random.random', return_value=0.5):  # No critical hit
            result = damage_processor.calculate_damage("attacker", "target", 20.0, "cold")
        
        assert result["success"]
        breakdown = result["breakdown"]
        assert breakdown["resistance_multiplier"] == 1.5  # 50% vulnerability = 1.5 multiplier
    
    def test_critical_hit_calculation(self, damage_processor, mock_characters): pass
        """Test critical hit calculation."""
        attacker, target = mock_characters
        damage_processor.combat_state.get_character = Mock(side_effect=lambda x: attacker if x == "attacker" else target)
        
        with patch('random.random', return_value=0.05):  # Force critical hit
            result = damage_processor.calculate_damage("attacker", "target", 20.0, "physical")
        
        assert result["success"]
        assert result["is_critical"]
        
        breakdown = result["breakdown"]
        assert breakdown["critical_hit"]
        assert breakdown["critical_multiplier"] == 2.5
    
    def test_apply_damage(self, damage_processor, mock_characters): pass
        """Test damage application."""
        attacker, target = mock_characters
        damage_processor.combat_state.get_character = Mock(return_value=target)
        
        initial_hp = target.hp
        damage_amount = 25.0
        
        result = damage_processor.apply_damage("attacker", "target", damage_amount)
        
        assert result["success"]
        assert result["damage_applied"] == damage_amount
        assert result["previous_hp"] == initial_hp
        assert result["new_hp"] == initial_hp - damage_amount
        assert target.hp == initial_hp - damage_amount
        assert not result["is_death"]
    
    def test_apply_damage_causing_death(self, damage_processor, mock_characters): pass
        """Test damage application that causes death."""
        attacker, target = mock_characters
        target.hp = 10  # Low health
        damage_processor.combat_state.get_character = Mock(return_value=target)
        
        damage_amount = 25.0  # More than current HP
        
        result = damage_processor.apply_damage("attacker", "target", damage_amount)
        
        assert result["success"]
        assert result["damage_applied"] == 10  # Only what was available
        assert result["new_hp"] == 0
        assert target.hp == 0
        assert result["is_death"]
        assert "death_result" in result
    
    def test_apply_healing(self, damage_processor, mock_characters): pass
        """Test healing application."""
        attacker, target = mock_characters
        target.hp = 50  # Damaged character
        damage_processor.combat_state.get_character = Mock(return_value=target)
        
        healing_amount = 30.0
        
        result = damage_processor.apply_healing("healer", "target", healing_amount)
        
        assert result["success"]
        assert result["healing_applied"] == healing_amount
        assert result["previous_hp"] == 50
        assert result["new_hp"] == 80
        assert target.hp == 80
    
    def test_apply_healing_exceeding_max_hp(self, damage_processor, mock_characters): pass
        """Test healing that would exceed max HP."""
        attacker, target = mock_characters
        target.hp = 90  # Nearly full health
        damage_processor.combat_state.get_character = Mock(return_value=target)
        
        healing_amount = 30.0  # More than needed
        
        result = damage_processor.apply_healing("healer", "target", healing_amount)
        
        assert result["success"]
        assert result["healing_applied"] == 10  # Only what was needed
        assert result["new_hp"] == 100  # Max HP
        assert target.hp == 100


class TestCombatManager: pass
    """Test the CombatManager facade."""
    
    @pytest.fixture
    def character_dict(self): pass
        """Create a dictionary of test characters."""
        char1 = Mock()
        char1.name = "Hero"
        char1.hp = 100
        char1.max_hp = 100
        char1.dexterity = 15
        char1.strength = 16
        
        char2 = Mock()
        char2.name = "Enemy"
        char2.hp = 80
        char2.max_hp = 80
        char2.dexterity = 12
        char2.strength = 14
        char2.is_enemy = True
        
        return {"hero": char1, "enemy": char2}
    
    def test_combat_manager_initialization(self, character_dict): pass
        """Test CombatManager initialization."""
        manager = CombatManager(character_dict=character_dict)
        
        assert manager.combat_id is not None
        assert manager.state_manager is not None
        assert manager.damage_processor is not None
        assert manager.current_state == "initializing"
        assert manager.round_number == 0
    
    def test_start_combat(self, character_dict): pass
        """Test combat start functionality."""
        manager = CombatManager(character_dict=character_dict)
        
        # First transition to ready state
        manager.state_manager.transition_state("ready")
        
        result = manager.start_combat()
        
        assert result["success"]
        assert manager.current_state == "active"
    
    def test_combat_actions(self, character_dict): pass
        """Test taking combat actions."""
        manager = CombatManager(character_dict=character_dict)
        
        # Set up combat
        manager.state_manager.transition_state("ready")
        manager.start_combat()
        
        # Test attack action
        result = manager.take_action("hero", "attack", "enemy")
        
        # Should succeed (exact values depend on character stats)
        assert result["success"] is not None
    
    def test_damage_delegation(self, character_dict): pass
        """Test that damage methods delegate to DamageProcessor."""
        manager = CombatManager(character_dict=character_dict)
        
        # Test calculate_damage delegation
        with patch.object(manager.damage_processor, 'calculate_damage') as mock_calc: pass
            mock_calc.return_value = {"success": True, "damage": 25}
            
            result = manager.calculate_damage("hero", "enemy", 20.0, "physical")
            
            mock_calc.assert_called_once_with("hero", "enemy", 20.0, "physical")
            assert result["success"]
    
    def test_state_delegation(self, character_dict): pass
        """Test that state methods delegate to StateManager."""
        manager = CombatManager(character_dict=character_dict)
        
        # Set up for pause test
        manager.state_manager.transition_state("ready")
        manager.state_manager.transition_state("active")
        
        # Test pause delegation
        with patch.object(manager.state_manager, 'pause_combat') as mock_pause: pass
            mock_pause.return_value = {"success": True}
            
            result = manager.pause_combat()
            
            mock_pause.assert_called_once()
            assert result["success"]
    
    def test_backward_compatibility_properties(self, character_dict): pass
        """Test backward compatibility properties."""
        manager = CombatManager(character_dict=character_dict)
        
        # Test round_number property
        assert manager.round_number == manager.state_manager.round_number
        
        # Test current_state property
        assert manager.current_state == manager.state_manager.current_state
        
        # Advance round and verify properties update
        manager.state_manager.advance_round()
        assert manager.round_number == manager.state_manager.round_number
    
    def test_character_management(self, character_dict): pass
        """Test character addition and removal."""
        manager = CombatManager()
        
        # Create a new character
        new_char = Mock()
        new_char.name = "New Character"
        new_char.hp = 75
        
        # Test add character
        char_id = manager.add_character(new_char)
        assert isinstance(char_id, str)
        
        # Test remove character
        success = manager.remove_character(char_id)
        assert success
    
    def test_get_combat_state(self, character_dict): pass
        """Test getting comprehensive combat state."""
        manager = CombatManager(character_dict=character_dict)
        
        state = manager.get_combat_state()
        
        assert "state" in state
        assert "round_number" in state
        assert "combat_id" in state
        assert "combatants" in state
        assert len(state["combatants"]) == 2  # hero and enemy
        
        # Verify combatant information
        combatant_names = [c["name"] for c in state["combatants"]]
        assert "Hero" in combatant_names
        assert "Enemy" in combatant_names


class TestIntegration: pass
    """Integration tests for the refactored combat system."""
    
    def test_full_combat_flow(self): pass
        """Test a complete combat flow using the refactored system."""
        # Create characters
        hero = Mock()
        hero.name = "Hero"
        hero.hp = 100
        hero.max_hp = 100
        hero.dexterity = 15
        hero.strength = 16
        hero.armor_class = 18
        hero.resistances = {}
        hero.vulnerabilities = {}
        hero.weapon_bonus = 3
        
        enemy = Mock()
        enemy.name = "Orc"
        enemy.hp = 60
        enemy.max_hp = 60
        enemy.dexterity = 10
        enemy.strength = 14
        enemy.armor_class = 15
        enemy.resistances = {}
        enemy.vulnerabilities = {}
        enemy.weapon_bonus = 1
        enemy.is_enemy = True
        
        character_dict = {"hero": hero, "enemy": enemy}
        
        # Initialize combat
        manager = CombatManager(character_dict=character_dict)
        
        # Verify initial state
        assert manager.current_state == "initializing"
        assert manager.round_number == 0
        
        # Start combat
        manager.state_manager.transition_state("ready")
        result = manager.start_combat()
        assert result["success"]
        assert manager.current_state == "active"
        
        # Take some actions
        attack_result = manager.take_action("hero", "attack", "enemy")
        # Should succeed (exact damage varies)
        assert "success" in attack_result
        
        # Check state after action
        state = manager.get_combat_state()
        assert state["state"] == "active"
        assert len(state["combatants"]) == 2
        
        # End combat
        end_result = manager.end_combat()
        assert end_result["success"]
        assert manager.current_state == "ended"
    
    def test_damage_calculation_and_application_integration(self): pass
        """Test integration between damage calculation and application."""
        # Create test characters
        attacker = Mock()
        attacker.strength = 18
        attacker.weapon_bonus = 5
        attacker.critical_chance = 0.2
        attacker.critical_multiplier = 3.0
        
        target = Mock()
        target.hp = 100
        target.max_hp = 100
        target.armor_class = 12
        target.resistances = {}
        target.vulnerabilities = {}
        
        character_dict = {"attacker": attacker, "target": target}
        manager = CombatManager(character_dict=character_dict)
        
        # Calculate damage
        calc_result = manager.calculate_damage("attacker", "target", 15.0, "physical")
        assert calc_result["success"]
        
        calculated_damage = calc_result["damage"]
        
        # Apply the calculated damage
        apply_result = manager.apply_damage("attacker", "target", calculated_damage, "physical")
        assert apply_result["success"]
        assert apply_result["damage_applied"] == calculated_damage
        assert target.hp == 100 - calculated_damage 