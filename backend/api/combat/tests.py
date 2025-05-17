import unittest
from .combat_system import (
    ActionType, DamageType, CombatantType, StatusEffectType, TerrainType,
    StatusEffect, Combatant, CombatLog, CombatManager
)


class TestStatusEffect(unittest.TestCase):
    """Tests for the StatusEffect class"""
    
    def test_create_status_effect(self):
        """Test creating a status effect"""
        effect = StatusEffect(
            effect_type=StatusEffectType.POISONED,
            duration=3,
            source_id="attacker_123",
            intensity=2,
            effects={"damage_per_turn": 5}
        )
        
        self.assertEqual(effect.effect_type, StatusEffectType.POISONED)
        self.assertEqual(effect.duration, 3)
        self.assertEqual(effect.source_id, "attacker_123")
        self.assertEqual(effect.intensity, 2)
        self.assertEqual(effect.effects, {"damage_per_turn": 5})
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization of status effects"""
        original = StatusEffect(
            effect_type=StatusEffectType.STUNNED,
            duration=2,
            source_id="attacker_456",
            intensity=1
        )
        
        # Convert to dict
        data = original.to_dict()
        
        # Convert back from dict
        restored = StatusEffect.from_dict(data)
        
        # Verify fields match
        self.assertEqual(restored.effect_type, original.effect_type)
        self.assertEqual(restored.duration, original.duration)
        self.assertEqual(restored.source_id, original.source_id)
        self.assertEqual(restored.intensity, original.intensity)
        self.assertEqual(restored.effects, original.effects)


class TestCombatant(unittest.TestCase):
    """Tests for the Combatant class"""
    
    def setUp(self):
        """Set up test combatants"""
        self.fighter = Combatant(
            id="fighter_1",
            name="Aragorn",
            type=CombatantType.PLAYER,
            initiative_bonus=3,
            hp=45,
            max_hp=45,
            armor_class=16,
            stats={
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 13,
                "charisma": 14
            }
        )
        
        self.goblin = Combatant(
            id="goblin_1",
            name="Goblin Scout",
            type=CombatantType.MONSTER,
            initiative_bonus=2,
            hp=12,
            max_hp=12,
            armor_class=13,
            stats={
                "strength": 10,
                "dexterity": 14,
                "constitution": 10,
                "intelligence": 8,
                "wisdom": 8,
                "charisma": 8
            }
        )
    
    def test_roll_initiative(self):
        """Test initiative rolling"""
        # Roll initiative for both combatants
        fighter_roll = self.fighter.roll_initiative()
        goblin_roll = self.goblin.roll_initiative()
        
        # Check that initiative roll is within expected range
        self.assertTrue(4 <= fighter_roll <= 23)  # 1 + 3 to 20 + 3
        self.assertTrue(3 <= goblin_roll <= 22)   # 1 + 2 to 20 + 2
        
        # Check that initiative roll is stored
        self.assertEqual(self.fighter.initiative_roll, fighter_roll)
        self.assertEqual(self.goblin.initiative_roll, goblin_roll)
    
    def test_add_status_effect(self):
        """Test adding status effects to a combatant"""
        # Add a status effect
        effect = StatusEffect(
            effect_type=StatusEffectType.POISONED,
            duration=3,
            source_id="trap_1"
        )
        
        # Initially, there should be no status effects
        self.assertEqual(len(self.fighter.status_effects), 0)
        
        # Add the effect and check it was added
        added = self.fighter.add_status_effect(effect)
        self.assertTrue(added)
        self.assertEqual(len(self.fighter.status_effects), 1)
        self.assertEqual(self.fighter.status_effects[0].effect_type, StatusEffectType.POISONED)
        
        # Add another effect of the same type but higher intensity
        effect2 = StatusEffect(
            effect_type=StatusEffectType.POISONED,
            duration=2,
            source_id="trap_2",
            intensity=2
        )
        
        # Should update the existing effect, not add a new one
        added = self.fighter.add_status_effect(effect2)
        self.assertFalse(added)  # Not a new effect
        self.assertEqual(len(self.fighter.status_effects), 1)  # Still only one effect
        self.assertEqual(self.fighter.status_effects[0].intensity, 2)  # But intensity is updated
        self.assertEqual(self.fighter.status_effects[0].duration, 3)  # Duration remains the longer one
    
    def test_remove_status_effect(self):
        """Test removing status effects from a combatant"""
        # Add two different status effects
        effect1 = StatusEffect(
            effect_type=StatusEffectType.POISONED,
            duration=3,
            source_id="trap_1"
        )
        
        effect2 = StatusEffect(
            effect_type=StatusEffectType.FRIGHTENED,
            duration=2,
            source_id="monster_1"
        )
        
        self.fighter.add_status_effect(effect1)
        self.fighter.add_status_effect(effect2)
        self.assertEqual(len(self.fighter.status_effects), 2)
        
        # Remove the first effect
        removed = self.fighter.remove_status_effect(StatusEffectType.POISONED)
        self.assertTrue(removed)
        self.assertEqual(len(self.fighter.status_effects), 1)
        self.assertEqual(self.fighter.status_effects[0].effect_type, StatusEffectType.FRIGHTENED)
        
        # Try to remove a non-existent effect
        removed = self.fighter.remove_status_effect(StatusEffectType.STUNNED)
        self.assertFalse(removed)
        self.assertEqual(len(self.fighter.status_effects), 1)
    
    def test_process_turn_start(self):
        """Test processing the start of a combatant's turn"""
        # Add a status effect with 1 round duration
        effect = StatusEffect(
            effect_type=StatusEffectType.STUNNED,
            duration=1,
            source_id="spell_1"
        )
        
        self.fighter.add_status_effect(effect)
        self.assertEqual(len(self.fighter.status_effects), 1)
        
        # Use up some action points
        self.fighter.use_action(ActionType.ACTION)
        self.fighter.use_action(ActionType.BONUS_ACTION)
        
        # Process turn start - should remove the expired effect and reset action points
        removed_effects = self.fighter.process_turn_start()
        
        self.assertEqual(removed_effects, 1)
        self.assertEqual(len(self.fighter.status_effects), 0)
        self.assertEqual(self.fighter.action_points[ActionType.ACTION], 1)
        self.assertEqual(self.fighter.action_points[ActionType.BONUS_ACTION], 1)
    
    def test_can_take_action(self):
        """Test checking if a combatant can take an action"""
        # Initially can take all actions
        self.assertTrue(self.fighter.can_take_action(ActionType.ACTION))
        self.assertTrue(self.fighter.can_take_action(ActionType.MOVEMENT))
        
        # Use up the action
        self.fighter.use_action(ActionType.ACTION)
        
        # Should now be unable to take an action
        self.assertFalse(self.fighter.can_take_action(ActionType.ACTION))
        self.assertTrue(self.fighter.can_take_action(ActionType.MOVEMENT))
        
        # Add a stunned effect
        effect = StatusEffect(
            effect_type=StatusEffectType.STUNNED,
            duration=2,
            source_id="spell_1"
        )
        
        self.fighter.add_status_effect(effect)
        
        # Stunned characters can't take any actions
        self.assertFalse(self.fighter.can_take_action(ActionType.ACTION))
        self.assertFalse(self.fighter.can_take_action(ActionType.MOVEMENT))
        self.assertFalse(self.fighter.can_take_action(ActionType.BONUS_ACTION))
        self.assertFalse(self.fighter.can_take_action(ActionType.REACTION))
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization of combatants"""
        # Add a status effect
        effect = StatusEffect(
            effect_type=StatusEffectType.POISONED,
            duration=3,
            source_id="trap_1"
        )
        
        self.fighter.add_status_effect(effect)
        self.fighter.roll_initiative()
        
        # Convert to dict
        data = self.fighter.to_dict()
        
        # Convert back from dict
        restored = Combatant.from_dict(data)
        
        # Verify fields match
        self.assertEqual(restored.id, self.fighter.id)
        self.assertEqual(restored.name, self.fighter.name)
        self.assertEqual(restored.type, self.fighter.type)
        self.assertEqual(restored.hp, self.fighter.hp)
        self.assertEqual(restored.max_hp, self.fighter.max_hp)
        self.assertEqual(restored.armor_class, self.fighter.armor_class)
        self.assertEqual(restored.stats, self.fighter.stats)
        self.assertEqual(restored.initiative_roll, self.fighter.initiative_roll)
        self.assertEqual(len(restored.status_effects), len(self.fighter.status_effects))
        self.assertEqual(restored.status_effects[0].effect_type, self.fighter.status_effects[0].effect_type)


class TestCombatManager(unittest.TestCase):
    """Tests for the CombatManager class"""
    
    def setUp(self):
        """Set up a combat manager with some combatants"""
        self.manager = CombatManager()
        
        # Create some combatants
        self.fighter = Combatant(
            id="fighter_1",
            name="Aragorn",
            type=CombatantType.PLAYER,
            initiative_bonus=3,
            hp=45,
            max_hp=45,
            armor_class=16,
            stats={
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 13,
                "charisma": 14
            }
        )
        
        self.wizard = Combatant(
            id="wizard_1",
            name="Gandalf",
            type=CombatantType.PLAYER,
            initiative_bonus=1,
            hp=30,
            max_hp=30,
            armor_class=12,
            stats={
                "strength": 10,
                "dexterity": 12,
                "constitution": 12,
                "intelligence": 18,
                "wisdom": 16,
                "charisma": 15
            }
        )
        
        self.goblin = Combatant(
            id="goblin_1",
            name="Goblin Scout",
            type=CombatantType.MONSTER,
            initiative_bonus=2,
            hp=12,
            max_hp=12,
            armor_class=13,
            stats={
                "strength": 10,
                "dexterity": 14,
                "constitution": 10,
                "intelligence": 8,
                "wisdom": 8,
                "charisma": 8
            }
        )
        
        # Add combatants to the manager
        self.manager.add_combatant(self.fighter)
        self.manager.add_combatant(self.wizard)
        self.manager.add_combatant(self.goblin)
    
    def test_start_combat(self):
        """Test starting combat and setting up initiative order"""
        # Start combat
        self.manager.start_combat()
        
        # Check that combat is active
        self.assertTrue(self.manager.combat_active)
        
        # Check round number is 1
        self.assertEqual(self.manager.round_number, 1)
        
        # Check initiative order is set up
        self.assertEqual(len(self.manager.initiative_order), 3)
        
        # Check that current turn index is 0
        self.assertEqual(self.manager.current_turn_index, 0)
        
        # Check that current combatant is set correctly
        current = self.manager.get_current_combatant()
        self.assertIsNotNone(current)
        self.assertEqual(current.id, self.manager.initiative_order[0])
    
    def test_next_turn(self):
        """Test advancing to the next turn"""
        # Start combat
        self.manager.start_combat()
        
        # Manually set initiative order for predictable testing
        self.manager.initiative_order = [self.fighter.id, self.goblin.id, self.wizard.id]
        self.manager.current_turn_index = 0
        
        # Check current combatant is fighter
        current = self.manager.get_current_combatant()
        self.assertEqual(current.id, self.fighter.id)
        
        # Advance to next turn
        next_combatant = self.manager.next_turn()
        
        # Check current turn index is 1
        self.assertEqual(self.manager.current_turn_index, 1)
        
        # Check current combatant is goblin
        self.assertEqual(next_combatant.id, self.goblin.id)
        
        # Advance to next turn again
        next_combatant = self.manager.next_turn()
        
        # Check current turn index is 2
        self.assertEqual(self.manager.current_turn_index, 2)
        
        # Check current combatant is wizard
        self.assertEqual(next_combatant.id, self.wizard.id)
        
        # Advance once more to wrap around to a new round
        next_combatant = self.manager.next_turn()
        
        # Check current turn index is 0 (wrapped around)
        self.assertEqual(self.manager.current_turn_index, 0)
        
        # Check round number has increased
        self.assertEqual(self.manager.round_number, 2)
        
        # Check current combatant is fighter again
        self.assertEqual(next_combatant.id, self.fighter.id)
    
    def test_attack_roll(self):
        """Test making attack rolls"""
        # Make a normal attack roll
        roll, hits, is_critical = self.manager.attack_roll(
            attacker=self.fighter,
            target=self.goblin,
            attack_bonus=5,
            advantage=False,
            disadvantage=False
        )
        
        # Check the roll is in the expected range
        self.assertTrue(6 <= roll <= 25)  # (1 + 5) to (20 + 5)
        
        # Hits if roll >= target AC (13)
        self.assertEqual(hits, roll >= 13 or is_critical)
        
        # Critical on natural 20 (roll - attack_bonus == 20)
        self.assertEqual(is_critical, roll - 5 == 20)
        
        # Force a critical hit by manipulating the random roll
        import random
        original_randint = random.randint
        try:
            # Mock random.randint to always return 20
            random.randint = lambda a, b: 20
            
            roll, hits, is_critical = self.manager.attack_roll(
                attacker=self.fighter,
                target=self.goblin,
                attack_bonus=5,
                advantage=False,
                disadvantage=False
            )
            
            # Check it's a critical hit
            self.assertEqual(roll, 25)  # 20 + 5
            self.assertTrue(hits)
            self.assertTrue(is_critical)
        finally:
            # Restore original randint
            random.randint = original_randint
    
    def test_calculate_damage(self):
        """Test calculating damage"""
        # Calculate normal damage
        damage, details = self.manager.calculate_damage(
            attacker=self.fighter,
            target=self.goblin,
            damage_roll=10,
            damage_type=DamageType.SLASHING,
            critical=False
        )
        
        # Check damage is as expected
        self.assertEqual(damage, 10)
        self.assertEqual(details["base_damage"], 10)
        self.assertEqual(details["critical"], False)
        
        # Calculate critical damage
        damage, details = self.manager.calculate_damage(
            attacker=self.fighter,
            target=self.goblin,
            damage_roll=10,
            damage_type=DamageType.SLASHING,
            critical=True
        )
        
        # Critical should double the damage
        self.assertEqual(damage, 20)
        self.assertEqual(details["base_damage"], 10)
        self.assertEqual(details["critical"], True)
        
        # Add a status effect that adds damage
        effect = StatusEffect(
            effect_type=StatusEffectType.CHARMED,
            duration=3,
            source_id=self.fighter.id,
            effects={"damage_bonus": 5}
        )
        
        self.fighter.add_status_effect(effect)
        
        # Calculate damage with status effect
        damage, details = self.manager.calculate_damage(
            attacker=self.fighter,
            target=self.goblin,
            damage_roll=10,
            damage_type=DamageType.SLASHING,
            critical=False
        )
        
        # Damage should include the bonus from the status effect
        self.assertEqual(damage, 15)
    
    def test_apply_damage(self):
        """Test applying damage to a target"""
        original_hp = self.goblin.hp
        
        # Apply damage
        result = self.manager.apply_damage(
            target=self.goblin,
            damage=5,
            details={"damage_type": "slashing"}
        )
        
        # Check HP was reduced
        self.assertEqual(self.goblin.hp, original_hp - 5)
        
        # Check result contains expected values
        self.assertEqual(result["target_id"], self.goblin.id)
        self.assertEqual(result["damage_taken"], 5)
        self.assertEqual(result["original_hp"], original_hp)
        self.assertEqual(result["new_hp"], original_hp - 5)
        
        # Apply damage that would reduce HP below 0
        large_damage = self.goblin.hp + 10
        result = self.manager.apply_damage(
            target=self.goblin,
            damage=large_damage,
            details={"damage_type": "slashing"}
        )
        
        # HP should be clamped to 0
        self.assertEqual(self.goblin.hp, 0)
    
    def test_perform_attack(self):
        """Test performing a complete attack"""
        import random
        original_randint = random.randint
        
        try:
            # Mock random.randint to control attack roll and damage roll
            mock_rolls = [15, 8]  # First for attack, second for damage
            mock_roll_index = 0
            
            def mock_randint(a, b):
                nonlocal mock_roll_index
                value = mock_rolls[mock_roll_index]
                mock_roll_index = (mock_roll_index + 1) % len(mock_rolls)
                return value
            
            random.randint = mock_randint
            
            original_hp = self.goblin.hp
            
            # Perform attack
            result = self.manager.perform_attack(
                attacker_id=self.fighter.id,
                target_id=self.goblin.id,
                attack_bonus=5,
                damage_dice="1d8+3",
                damage_type=DamageType.SLASHING
            )
            
            # Check attack hits (15 + 5 = 20, which is > goblin AC 13)
            self.assertTrue(result["hits"])
            self.assertFalse(result["is_critical"])
            
            # Check damage
            self.assertEqual(result["damage"]["damage_taken"], 11)  # 8 + 3
            self.assertEqual(result["damage"]["original_hp"], original_hp)
            self.assertEqual(result["damage"]["new_hp"], original_hp - 11)
            
            # Check HP was actually reduced
            self.assertEqual(self.goblin.hp, original_hp - 11)
            
            # Check action was used
            self.assertEqual(self.fighter.action_points[ActionType.ACTION], 0)
        finally:
            # Restore original randint
            random.randint = original_randint
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization of combat manager"""
        # Start combat
        self.manager.start_combat()
        
        # Set some terrain
        self.manager.set_terrain((1, 1), TerrainType.DIFFICULT)
        self.manager.set_terrain((2, 2), TerrainType.COVER_HALF)
        
        # Convert to dict
        data = self.manager.to_dict()
        
        # Convert back from dict
        restored = CombatManager.from_dict(data)
        
        # Verify fields match
        self.assertEqual(len(restored.combatants), len(self.manager.combatants))
        self.assertEqual(restored.initiative_order, self.manager.initiative_order)
        self.assertEqual(restored.current_turn_index, self.manager.current_turn_index)
        self.assertEqual(restored.round_number, self.manager.round_number)
        self.assertEqual(restored.combat_active, self.manager.combat_active)
        
        # Check terrain
        self.assertEqual(restored.get_terrain((1, 1)), TerrainType.DIFFICULT)
        self.assertEqual(restored.get_terrain((2, 2)), TerrainType.COVER_HALF)


if __name__ == "__main__":
    unittest.main() 