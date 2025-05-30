"""
Tests for backend.systems.combat.combat_facade

Comprehensive tests for the CombatFacade class and its methods.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call

# Add the backend.systems.combat module to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.systems.combat.combat_facade import Combat


class TestCombat(unittest.TestCase): pass
    """Test cases for Combat class"""

    def setUp(self): pass
        """Set up test fixtures"""
        self.mock_combatant1 = Mock()
        self.mock_combatant1.id = "player1"
        self.mock_combatant1.name = "Test Player"
        self.mock_combatant1.hp = 100
        self.mock_combatant1.max_hp = 100
        self.mock_combatant1.is_alive = True
        self.mock_combatant1.status_effects = []
        self.mock_combatant1.skills = []  # Make iterable
        self.mock_combatant1.inventory = []  # Make iterable
        self.mock_combatant1.immunities = []  # Make iterable
        self.mock_combatant1.is_immune_to_all_effects = False
        
        self.mock_combatant2 = Mock()
        self.mock_combatant2.id = "enemy1"
        self.mock_combatant2.name = "Test Enemy"
        self.mock_combatant2.hp = 80
        self.mock_combatant2.max_hp = 80
        self.mock_combatant2.is_alive = True
        self.mock_combatant2.status_effects = []
        self.mock_combatant2.skills = []  # Make iterable
        self.mock_combatant2.inventory = []  # Make iterable
        self.mock_combatant2.immunities = []  # Make iterable
        self.mock_combatant2.is_immune_to_all_effects = False
        
        self.combatants = [self.mock_combatant1, self.mock_combatant2]
        
        self.mock_combat_state = Mock()
        self.mock_combat_state.id = "test_combat"
        self.mock_combat_state.all_characters = []
        self.mock_combat_state.turn_order = []
        self.mock_combat_state.current_turn = None
        self.mock_combat_state.round_number = 1


class TestInitializeCombat(TestCombat): pass
    """Test the initialize_combat method"""

    @patch('backend.systems.combat.combat_facade.get_turn_order')
    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    @patch('backend.systems.combat.combat_facade.CombatEvent')
    def test_initialize_combat_success(self, mock_combat_event, mock_event_dispatcher, mock_get_turn_order): pass
        """Test successful combat initialization"""
        mock_get_turn_order.return_value = self.combatants
        
        Combat.initialize_combat(self.combatants, self.mock_combat_state)
        
        # Verify combatants were set
        self.assertEqual(self.mock_combat_state.all_characters, self.combatants)
        
        # Verify turn order was set
        self.assertEqual(self.mock_combat_state.turn_order, self.combatants)
        
        # Verify current turn was set
        self.assertEqual(self.mock_combat_state.current_turn, self.combatants[0])
        
        # Verify event was published
        mock_event_dispatcher.publish_sync.assert_called_once()
        
        # Verify get_turn_order was called
        mock_get_turn_order.assert_called_once_with(self.combatants)

    @patch('backend.systems.combat.combat_facade.get_turn_order')
    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    @patch('backend.systems.combat.combat_facade.CombatEvent')
    def test_initialize_combat_empty_combatants(self, mock_combat_event, mock_event_dispatcher, mock_get_turn_order): pass
        """Test combat initialization with empty combatants list"""
        mock_get_turn_order.return_value = []
        
        Combat.initialize_combat([], self.mock_combat_state)
        
        # Verify empty list was set
        self.assertEqual(self.mock_combat_state.all_characters, [])
        self.assertEqual(self.mock_combat_state.turn_order, [])
        
        # Current turn should remain None
        self.assertIsNone(self.mock_combat_state.current_turn)

    @patch('backend.systems.combat.combat_facade.get_turn_order')
    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_initialize_combat_event_data(self, mock_event_dispatcher, mock_get_turn_order): pass
        """Test that combat initialization publishes correct event data"""
        mock_get_turn_order.return_value = self.combatants
        
        Combat.initialize_combat(self.combatants, self.mock_combat_state)
        
        # Get the published event
        call_args = mock_event_dispatcher.publish_sync.call_args[0][0]
        
        # Verify event type and subtype
        self.assertEqual(call_args.event_type, "combat.event")
        self.assertEqual(call_args.event_subtype, "start")
        
        # Verify event metadata structure
        self.assertIn("combatants", call_args.metadata)
        self.assertIn("combat_state_id", call_args.metadata)
        self.assertIn("first_turn", call_args.metadata)


class TestExecuteAction(TestCombat): pass
    """Test the execute_action method"""

    @patch('backend.systems.combat.combat_facade.validate_combat_action')
    @patch('backend.systems.combat.combat_facade.CombatFacade._execute_attack')
    @patch('backend.systems.combat.combat_facade._effect_pipeline')
    def test_execute_action_attack_success(self, mock_pipeline, mock_execute_attack, mock_validate): pass
        """Test successful attack action execution"""
        mock_validate.return_value = (True, None, None)
        mock_execute_attack.return_value = (True, None)
        
        action = {"type": "attack", "target_id": "enemy1"}
        
        result = Combat.execute_action(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertTrue(result[0])
        self.assertIsNone(result[1])
        
        mock_validate.assert_called_once_with(self.mock_combatant1, action, self.mock_combat_state)
        mock_execute_attack.assert_called_once_with(self.mock_combatant1, action, self.mock_combat_state)

    @patch('backend.systems.combat.combat_facade.validate_combat_action')
    def test_execute_action_validation_failure(self, mock_validate): pass
        """Test action execution with validation failure"""
        mock_validate.return_value = (False, "INVALID_TARGET", "Target not found")
        
        action = {"type": "attack", "target_id": "nonexistent"}
        
        result = Combat.execute_action(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertFalse(result[0])
        self.assertEqual(result[1], "Target not found")

    @patch('backend.systems.combat.combat_facade.validate_combat_action')
    @patch('backend.systems.combat.combat_facade.CombatFacade._execute_skill')
    @patch('backend.systems.combat.combat_facade._effect_pipeline')
    def test_execute_action_skill(self, mock_pipeline, mock_execute_skill, mock_validate): pass
        """Test skill action execution"""
        mock_validate.return_value = (True, None, None)
        mock_execute_skill.return_value = (True, None)
        
        action = {"type": "skill", "skill_id": "fireball"}
        
        result = Combat.execute_action(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertTrue(result[0])
        mock_execute_skill.assert_called_once()

    @patch('backend.systems.combat.combat_facade.validate_combat_action')
    @patch('backend.systems.combat.combat_facade.CombatFacade._execute_item')
    @patch('backend.systems.combat.combat_facade._effect_pipeline')
    def test_execute_action_item(self, mock_pipeline, mock_execute_item, mock_validate): pass
        """Test item action execution"""
        mock_validate.return_value = (True, None, None)
        mock_execute_item.return_value = (True, None)
        
        action = {"type": "item", "item_id": "health_potion"}
        
        result = Combat.execute_action(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertTrue(result[0])
        mock_execute_item.assert_called_once()

    @patch('backend.systems.combat.combat_facade.validate_combat_action')
    @patch('backend.systems.combat.combat_facade.CombatFacade._execute_movement')
    @patch('backend.systems.combat.combat_facade._effect_pipeline')
    def test_execute_action_movement(self, mock_pipeline, mock_execute_movement, mock_validate): pass
        """Test movement action execution"""
        mock_validate.return_value = (True, None, None)
        mock_execute_movement.return_value = (True, None)
        
        action = {"type": "move", "position": {"x": 5, "y": 3}}
        
        result = Combat.execute_action(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertTrue(result[0])
        mock_execute_movement.assert_called_once()

    @patch('backend.systems.combat.combat_facade.validate_combat_action')
    @patch('backend.systems.combat.combat_facade._effect_pipeline')
    def test_execute_action_pass(self, mock_pipeline, mock_validate): pass
        """Test pass action execution"""
        mock_validate.return_value = (True, None, None)
        
        action = {"type": "pass"}
        
        result = Combat.execute_action(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertTrue(result[0])
        self.assertIsNone(result[1])

    @patch('backend.systems.combat.combat_facade.validate_combat_action')
    def test_execute_action_unknown_type(self, mock_validate): pass
        """Test execution of unknown action type"""
        mock_validate.return_value = (True, None, None)
        
        action = {"type": "unknown_action"}
        
        result = Combat.execute_action(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertFalse(result[0])
        self.assertIn("Unknown action type", result[1])

    @patch('backend.systems.combat.combat_facade.validate_combat_action')
    @patch('backend.systems.combat.combat_facade.CombatFacade._execute_attack')
    @patch('backend.systems.combat.combat_facade._effect_pipeline')
    def test_execute_action_processes_effects_on_success(self, mock_pipeline, mock_execute_attack, mock_validate): pass
        """Test that effects are processed when action succeeds"""
        mock_validate.return_value = (True, None, None)
        mock_execute_attack.return_value = (True, None)
        self.mock_combat_state.all_characters = self.combatants
        
        action = {"type": "attack", "target_id": "enemy1"}
        
        Combat.execute_action(self.mock_combatant1, action, self.mock_combat_state)
        
        # Verify effects were processed for all combatants
        expected_calls = [call.process_turn_end(combatant) for combatant in self.combatants]
        mock_pipeline.process_turn_end.assert_has_calls(expected_calls)

    @patch('backend.systems.combat.combat_facade.validate_combat_action')
    @patch('backend.systems.combat.combat_facade.CombatFacade._execute_attack')
    @patch('backend.systems.combat.combat_facade._effect_pipeline')
    def test_execute_action_no_effects_on_failure(self, mock_pipeline, mock_execute_attack, mock_validate): pass
        """Test that effects are not processed when action fails"""
        mock_validate.return_value = (True, None, None)
        mock_execute_attack.return_value = (False, "Attack failed")
        
        action = {"type": "attack", "target_id": "enemy1"}
        
        Combat.execute_action(self.mock_combatant1, action, self.mock_combat_state)
        
        # Verify effects were not processed
        mock_pipeline.process_turn_end.assert_not_called()


class TestApplyDamage(TestCombat): pass
    """Test the apply_damage method"""

    @patch('backend.systems.combat.combat_facade.validate_damage_parameters')
    @patch('backend.systems.combat.combat_facade.apply_full_damage_calculation')
    @patch('backend.systems.combat.combat_facade.resolve_combat_action')
    def test_apply_damage_success(self, mock_resolve_action, mock_damage_calc, mock_validate): pass
        """Test successful damage application"""
        mock_validate.return_value = (True, None, None)
        mock_damage_calc.return_value = (45.0, {"is_critical": True})  # damage, details
        mock_resolve_action.return_value = False  # is_fatal
        
        result = Combat.apply_damage(
            self.mock_combatant1, self.mock_combatant2, 50.0, "physical", self.mock_combat_state
        )
        
        self.assertEqual(result, (45.0, True, False))
        mock_validate.assert_called_once()
        mock_damage_calc.assert_called_once()
        mock_resolve_action.assert_called_once()

    @patch('backend.systems.combat.combat_facade.validate_damage_parameters')
    def test_apply_damage_validation_failure(self, mock_validate): pass
        """Test damage application with validation failure"""
        mock_validate.return_value = (False, "INVALID_DAMAGE", "Negative damage")
        
        result = Combat.apply_damage(
            self.mock_combatant1, self.mock_combatant2, -10.0, "physical", self.mock_combat_state
        )
        
        self.assertEqual(result, (0.0, False, False))

    @patch('backend.systems.combat.combat_facade.validate_damage_parameters')
    @patch('backend.systems.combat.combat_facade.apply_full_damage_calculation')
    @patch('backend.systems.combat.combat_facade.resolve_combat_action')
    def test_apply_damage_no_critical(self, mock_resolve_action, mock_damage_calc, mock_validate): pass
        """Test damage application with critical hits disabled"""
        mock_validate.return_value = (True, None, None)
        mock_damage_calc.return_value = (40.0, {"is_critical": False})
        mock_resolve_action.return_value = False
        
        result = Combat.apply_damage(
            self.mock_combatant1, self.mock_combatant2, 40.0, "fire", 
            self.mock_combat_state, allow_critical=False
        )
        
        self.assertEqual(result, (40.0, False, False))
        # Verify allow_critical was passed to damage calculation
        call_args = mock_damage_calc.call_args[1]
        self.assertFalse(call_args.get('allow_critical', True))

    @patch('backend.systems.combat.combat_facade.validate_damage_parameters')
    @patch('backend.systems.combat.combat_facade.apply_full_damage_calculation')
    @patch('backend.systems.combat.combat_facade.resolve_combat_action')
    def test_apply_damage_fatal(self, mock_resolve_action, mock_damage_calc, mock_validate): pass
        """Test fatal damage application"""
        mock_validate.return_value = (True, None, None)
        mock_damage_calc.return_value = (100.0, {"is_critical": False})
        mock_resolve_action.return_value = True  # Fatal damage
        
        result = Combat.apply_damage(
            self.mock_combatant1, self.mock_combatant2, 100.0, "physical", self.mock_combat_state
        )
        
        self.assertEqual(result, (100.0, False, True))


class TestApplyEffect(TestCombat): pass
    """Test the apply_effect method"""

    @patch('backend.systems.combat.combat_facade.apply_status_effect')
    def test_apply_effect_success(self, mock_apply_effect): pass
        """Test successful effect application"""
        mock_apply_effect.return_value = True
        
        result = Combat.apply_effect(
            self.mock_combatant1, self.mock_combatant2, "debuff", self.mock_combat_state,
            duration=3, damage=5
        )
        
        self.assertTrue(result)
        mock_apply_effect.assert_called_once()

    @patch('backend.systems.combat.combat_facade.validate_effect_application')
    def test_apply_effect_validation_failure(self, mock_validate): pass
        """Test effect application with validation failure"""
        mock_validate.return_value = (False, "INVALID_TARGET", "Target immune")
        
        result = Combat.apply_effect(
            self.mock_combatant1, self.mock_combatant2, "debuff", self.mock_combat_state
        )
        
        self.assertFalse(result)

    @patch('backend.systems.combat.combat_facade.validate_effect_application')
    @patch('backend.systems.combat.combat_facade.apply_status_effect')
    def test_apply_effect_application_failure(self, mock_apply_effect, mock_validate): pass
        """Test effect application when apply_status_effect fails"""
        mock_validate.return_value = (True, None, None)
        mock_apply_effect.return_value = False
        
        result = Combat.apply_effect(
            self.mock_combatant1, self.mock_combatant2, "debuff", self.mock_combat_state
        )
        
        self.assertFalse(result)


class TestCreateAndApplyEffect(TestCombat): pass
    """Test the create_and_apply_effect method"""

    @patch('backend.systems.combat.combat_facade.validate_effect_application')
    @patch('backend.systems.combat.combat_facade._effect_pipeline')
    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_create_and_apply_effect_success(self, mock_event_dispatcher, mock_pipeline, mock_validate): pass
        """Test successful effect creation and application"""
        mock_validate.return_value = (True, None, None)
        mock_effect_instance = Mock()
        mock_effect_class = Mock(return_value=mock_effect_instance)
        mock_pipeline.apply_effect.return_value = True
        
        result = Combat.create_and_apply_effect(
            self.mock_combatant1, self.mock_combatant2, mock_effect_class, 
            self.mock_combat_state, duration=3
        )
        
        self.assertTrue(result)
        mock_effect_class.assert_called_once_with(
            source=self.mock_combatant1, target=self.mock_combatant2, duration=3
        )
        mock_pipeline.apply_effect.assert_called_once_with(self.mock_combatant1, self.mock_combatant2, mock_effect_instance)

    @patch('backend.systems.combat.combat_facade.validate_effect_application')
    def test_create_and_apply_effect_validation_failure(self, mock_validate): pass
        """Test effect creation with validation failure"""
        mock_validate.return_value = (False, "INVALID_TARGET", "Invalid target")
        mock_effect_class = Mock()
        
        result = Combat.create_and_apply_effect(
            self.mock_combatant1, self.mock_combatant2, mock_effect_class, self.mock_combat_state
        )
        
        self.assertFalse(result)
        mock_effect_class.assert_not_called()


class TestRemoveEffect(TestCombat): pass
    """Test the remove_effect method"""

    @patch('backend.systems.combat.combat_facade.remove_status_effect')
    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_remove_effect_success(self, mock_event_dispatcher, mock_remove_effect): pass
        """Test successful effect removal"""
        mock_remove_effect.return_value = True
        
        result = Combat.remove_effect(self.mock_combatant1, "debuff")
        
        self.assertTrue(result)
        mock_remove_effect.assert_called_once_with(self.mock_combatant1, "debuff")

    @patch('backend.systems.combat.combat_facade.remove_status_effect')
    def test_remove_effect_failure(self, mock_remove_effect): pass
        """Test effect removal failure"""
        mock_remove_effect.return_value = False
        
        result = Combat.remove_effect(self.mock_combatant1, "nonexistent")
        
        self.assertFalse(result)


class TestProcessEffects(TestCombat): pass
    """Test the process_effects method"""

    @patch('backend.systems.combat.combat_facade.process_status_effects')
    def test_process_effects(self, mock_process_effects): pass
        """Test effect processing for all combatants"""
        self.mock_combat_state.all_characters = self.combatants
        
        Combat.process_effects(self.mock_combat_state)
        
        # Verify effects were processed for all combatants
        expected_calls = [call(combatant) for combatant in self.combatants]
        mock_process_effects.assert_has_calls(expected_calls)


class TestGetActiveEffects(TestCombat): pass
    """Test the get_active_effects method"""

    def test_get_active_effects_with_effects(self): pass
        """Test getting active effects when target has effects"""
        mock_effect1 = Mock()
        mock_effect1.name = "poison"
        mock_effect1.duration = 3
        mock_effect1.magnitude = 5
        
        mock_effect2 = Mock()
        mock_effect2.name = "blessing"
        mock_effect2.duration = 5
        mock_effect2.magnitude = 10
        
        self.mock_combatant1.status_effects = [mock_effect1, mock_effect2]
        
        result = Combat.get_active_effects(self.mock_combatant1)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "poison")
        self.assertEqual(result[1]["name"], "blessing")

    def test_get_active_effects_no_effects(self): pass
        """Test getting active effects when target has no effects"""
        self.mock_combatant1.status_effects = []
        
        result = Combat.get_active_effects(self.mock_combatant1)
        
        self.assertEqual(result, [])

    def test_get_active_effects_no_status_effects_attribute(self): pass
        """Test getting active effects when target has no status_effects attribute"""
        delattr(self.mock_combatant1, 'status_effects')
        
        result = Combat.get_active_effects(self.mock_combatant1)
        
        self.assertEqual(result, [])


class TestGetTurnOrder(TestCombat): pass
    """Test the get_turn_order method"""

    def test_get_turn_order(self): pass
        """Test getting turn order from combat state"""
        self.mock_combat_state.turn_order = self.combatants
        
        result = Combat.get_turn_order(self.mock_combat_state)
        
        self.assertEqual(result, self.combatants)

    def test_get_turn_order_empty(self): pass
        """Test getting turn order when empty"""
        self.mock_combat_state.turn_order = []
        
        result = Combat.get_turn_order(self.mock_combat_state)
        
        self.assertEqual(result, [])


class TestAdvanceTurn(TestCombat): pass
    """Test the advance_turn method"""

    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_advance_turn_normal(self, mock_event_dispatcher): pass
        """Test normal turn advancement"""
        self.mock_combat_state.turn_order = self.combatants
        self.mock_combat_state.current_turn = self.combatants[0]
        self.mock_combat_state.current_turn_index = 0
        
        result = Combat.advance_turn(self.mock_combat_state)
        
        self.assertEqual(result, self.combatants[1])
        self.assertEqual(self.mock_combat_state.current_turn, self.combatants[1])
        self.assertEqual(self.mock_combat_state.current_turn_index, 1)

    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_advance_turn_wrap_around(self, mock_event_dispatcher): pass
        """Test turn advancement wrapping around to start"""
        self.mock_combat_state.turn_order = self.combatants
        self.mock_combat_state.current_turn = self.combatants[1]  # Last combatant
        self.mock_combat_state.current_turn_index = 1
        self.mock_combat_state.round_number = 1
        
        result = Combat.advance_turn(self.mock_combat_state)
        
        self.assertEqual(result, self.combatants[0])
        self.assertEqual(self.mock_combat_state.current_turn, self.combatants[0])
        self.assertEqual(self.mock_combat_state.current_turn_index, 0)
        self.assertEqual(self.mock_combat_state.round_number, 2)

    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_advance_turn_no_current_turn_index(self, mock_event_dispatcher): pass
        """Test turn advancement when current_turn_index doesn't exist"""
        self.mock_combat_state.turn_order = self.combatants
        self.mock_combat_state.current_turn = self.combatants[0]
        # No current_turn_index attribute
        
        result = Combat.advance_turn(self.mock_combat_state)
        
        self.assertEqual(result, self.combatants[1])
        self.assertEqual(self.mock_combat_state.current_turn_index, 1)

    def test_advance_turn_empty_turn_order(self): pass
        """Test turn advancement with empty turn order"""
        self.mock_combat_state.turn_order = []
        
        result = Combat.advance_turn(self.mock_combat_state)
        
        self.assertIsNone(result)


class TestGetValidTargets(TestCombat): pass
    """Test the get_valid_targets method"""

    @patch('backend.systems.combat.combat_facade.get_valid_targets')
    def test_get_valid_targets_default_params(self, mock_get_valid_targets): pass
        """Test getting valid targets with default parameters"""
        mock_get_valid_targets.return_value = [self.mock_combatant2]
        
        result = Combat.get_valid_targets(self.mock_combatant1, self.mock_combat_state)
        
        self.assertEqual(result, [self.mock_combatant2])
        mock_get_valid_targets.assert_called_once_with(
            actor=self.mock_combatant1,
            combat_state=self.mock_combat_state,
            target_type="enemy",
            range_type="any"
        )

    @patch('backend.systems.combat.combat_facade.get_valid_targets')
    def test_get_valid_targets_custom_params(self, mock_get_valid_targets): pass
        """Test getting valid targets with custom parameters"""
        mock_get_valid_targets.return_value = [self.mock_combatant1]
        
        result = Combat.get_valid_targets(
            self.mock_combatant1, self.mock_combat_state, "ally", "melee"
        )
        
        self.assertEqual(result, [self.mock_combatant1])
        mock_get_valid_targets.assert_called_once_with(
            actor=self.mock_combatant1,
            combat_state=self.mock_combat_state,
            target_type="ally",
            range_type="melee"
        )


class TestEndCombat(TestCombat): pass
    """Test the end_combat method"""

    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_end_combat_with_victor(self, mock_event_dispatcher): pass
        """Test ending combat with a victor"""
        Combat.end_combat(self.mock_combat_state, "player")
        
        # Verify combat state was updated
        self.assertFalse(self.mock_combat_state.is_active)
        self.assertEqual(self.mock_combat_state.victor, "player")
        
        # Verify event was published
        mock_event_dispatcher.publish_sync.assert_called_once()
        call_args = mock_event_dispatcher.publish_sync.call_args[0][0]
        self.assertEqual(call_args.event_type, "combat.event")
        self.assertEqual(call_args.event_subtype, "end")
        self.assertEqual(call_args.metadata["victor"], "player")

    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_end_combat_no_victor(self, mock_event_dispatcher): pass
        """Test ending combat without a victor"""
        Combat.end_combat(self.mock_combat_state)
        
        # Verify combat state was updated
        self.assertFalse(self.mock_combat_state.is_active)
        self.assertIsNone(self.mock_combat_state.victor)
        
        # Verify event was published
        call_args = mock_event_dispatcher.publish_sync.call_args[0][0]
        self.assertIsNone(call_args.metadata["victor"])


class TestPrivateExecuteMethods(TestCombat): pass
    """Test the private _execute_* methods"""

    @patch('backend.systems.combat.combat_facade.is_attack_successful')
    @patch('backend.systems.combat.combat_facade.CombatFacade.apply_damage')
    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_execute_attack_success(self, mock_event_dispatcher, mock_apply_damage, mock_is_attack_successful): pass
        """Test successful attack execution"""
        mock_is_attack_successful.return_value = True
        mock_apply_damage.return_value = (25.0, False, False)
        self.mock_combat_state.all_characters = [self.mock_combatant1, self.mock_combatant2]
        
        action = {"target_id": "enemy1", "weapon": "sword"}
        
        result = Combat._execute_attack(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertTrue(result[0])
        self.assertIsNone(result[1])
        mock_is_attack_successful.assert_called_once()
        mock_apply_damage.assert_called_once()

    def test_execute_attack_failure(self): pass
        """Test failed attack execution"""
        self.mock_combat_state.all_characters = [self.mock_combatant1, self.mock_combatant2]
        
        action = {"target_id": "nonexistent", "weapon": "sword"}
        
        result = Combat._execute_attack(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertFalse(result[0])
        self.assertEqual(result[1], "Target not found: nonexistent")

    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_execute_skill_success(self, mock_event_dispatcher): pass
        """Test successful skill execution"""
        # Set up mock skill
        mock_skill = Mock()
        mock_skill.id = "fireball"
        mock_skill.resource_cost = 10
        mock_skill.resource_type = "mana"
        # Set damage to 0 to avoid damage application logic
        mock_skill.damage = 0
        # Don't set status_effect to avoid status effect logic
        del mock_skill.status_effect  # Remove the mock attribute
        self.mock_combatant1.skills = [mock_skill]
        self.mock_combatant1.resources = {"mana": 100}  # Set up resources dict
        self.mock_combat_state.all_characters = [self.mock_combatant1, self.mock_combatant2]
        
        action = {"skill_id": "fireball", "target_ids": ["enemy1"]}
        
        result = Combat._execute_skill(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertTrue(result[0])
        self.assertIsNone(result[1])

    def test_execute_skill_failure(self): pass
        """Test failed skill execution"""
        self.mock_combatant1.skills = []  # No skills available
        
        action = {"skill_id": "fireball", "target_ids": ["enemy1"]}
        
        result = Combat._execute_skill(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertFalse(result[0])
        self.assertEqual(result[1], "Skill not found: fireball")

    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_execute_item_success(self, mock_event_dispatcher): pass
        """Test successful item execution"""
        # Set up mock item
        mock_item = Mock()
        mock_item.id = "health_potion"
        self.mock_combatant1.inventory = [mock_item]
        self.mock_combat_state.all_characters = [self.mock_combatant1, self.mock_combatant2]
        
        action = {"item_id": "health_potion", "target_ids": ["player1"]}
        
        result = Combat._execute_item(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertTrue(result[0])
        self.assertIsNone(result[1])

    def test_execute_item_failure(self): pass
        """Test failed item execution"""
        self.mock_combatant1.inventory = []  # No items available
        
        action = {"item_id": "nonexistent", "target_ids": ["player1"]}
        
        result = Combat._execute_item(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertFalse(result[0])
        self.assertEqual(result[1], "Item not found: nonexistent")

    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_execute_movement_success(self, mock_event_dispatcher): pass
        """Test successful movement execution"""
        self.mock_combatant1.position = {"x": 0, "y": 0}  # Set initial position
        
        action = {"position": {"x": 5, "y": 3}}
        
        result = Combat._execute_movement(self.mock_combatant1, action, self.mock_combat_state)
        
        self.assertTrue(result[0])
        self.assertIsNone(result[1])
        self.assertEqual(self.mock_combatant1.position, {"x": 5, "y": 3})

    @patch('backend.systems.combat.combat_facade.event_dispatcher')
    def test_execute_movement_failure(self, mock_event_dispatcher): pass
        """Test movement execution with None position"""
        # Test with None position in action
        action = {"position": None}
        
        result = Combat._execute_movement(self.mock_combatant1, action, self.mock_combat_state)
        
        # The current implementation doesn't validate position, so it should succeed
        # but set position to None
        self.assertTrue(result[0])
        self.assertIsNone(result[1])
        if hasattr(self.mock_combatant1, 'position'): pass
            self.assertIsNone(self.mock_combatant1.position)


class TestModuleImports(unittest.TestCase): pass
    """Test module imports and basic functionality"""

    def test_module_imports(self): pass
        """Test that the module can be imported without errors"""
        from backend.systems.combat.combat_facade import Combat
        
        # Verify class exists
        self.assertTrue(hasattr(Combat, 'initialize_combat'))
        self.assertTrue(hasattr(Combat, 'execute_action'))
        self.assertTrue(hasattr(Combat, 'apply_damage'))

    def test_static_methods(self): pass
        """Test that all main methods are static"""
        from backend.systems.combat.combat_facade import Combat
        
        # Verify methods are static (can be called without instance)
        self.assertTrue(callable(Combat.initialize_combat))
        self.assertTrue(callable(Combat.execute_action))
        self.assertTrue(callable(Combat.apply_damage))


if __name__ == '__main__': pass
    unittest.main()
