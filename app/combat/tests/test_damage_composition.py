# app/combat/tests/test_damage_composition.py
import unittest
from app.core.enums import DamageType
from app.core.models.combat import DamageComposition, ResistanceComponent, CombatStats, DamageEffectivenessMatrix
from app.combat.damage_calculator import DamageCalculator, DamageRoll, CriticalHitCalculator, DamageEvent, DamageModificationPipeline

class TestDamageComposition(unittest.TestCase):
    def test_add_and_total(self):
        comp = DamageComposition()
        comp.add(DamageType.FIRE, 10)
        comp.add(DamageType.PHYSICAL, 5)
        self.assertEqual(comp.total(), 15)
        self.assertEqual(comp[DamageType.FIRE], 10)
        self.assertEqual(comp[DamageType.PHYSICAL], 5)

    def test_combine(self):
        comp1 = DamageComposition({DamageType.FIRE: 10})
        comp2 = DamageComposition({DamageType.FIRE: 5, DamageType.PHYSICAL: 3})
        combined = comp1.combine(comp2)
        self.assertEqual(combined[DamageType.FIRE], 15)
        self.assertEqual(combined[DamageType.PHYSICAL], 3)

    def test_serialize_deserialize(self):
        comp = DamageComposition({DamageType.FIRE: 7, DamageType.POISON: 2})
        data = comp.serialize()
        comp2 = DamageComposition.deserialize(data)
        self.assertEqual(comp2[DamageType.FIRE], 7)
        self.assertEqual(comp2[DamageType.POISON], 2)

    def test_is_empty(self):
        comp = DamageComposition()
        self.assertTrue(comp.is_empty())
        comp.add(DamageType.FIRE, 1)
        self.assertFalse(comp.is_empty())

# Mock status system for testing DamageCalculator
class MockStatusSystem:
    def get_resistances(self, target_id):
        return {DamageType.FIRE.value: 0.5, DamageType.PHYSICAL.value: 0.0}
    def get_immunities(self, target_id):
        return []

class MockBattlefield:
    pass

class TestDamageCalculator(unittest.TestCase):
    def setUp(self):
        self.status_system = MockStatusSystem()
        self.battlefield = MockBattlefield()
        # Mock combat_stats_lookup
        class MockStats:
            def __init__(self, resistances=None, vulnerabilities=None):
                self.resistances = resistances or {}
                self.vulnerabilities = vulnerabilities or {}
        self.MockStats = MockStats

    def test_calculate_damage_multi_type(self):
        # No resistances/vulnerabilities (but MockStatusSystem applies 50% resistance to FIRE)
        calc = DamageCalculator(self.status_system, self.battlefield)
        comp = DamageComposition({DamageType.FIRE: 10, DamageType.PHYSICAL: 5})
        roll = calc.calculate_damage('attacker', 'target', comp)
        self.assertEqual(roll.composition[DamageType.FIRE], 5)
        self.assertEqual(roll.composition[DamageType.PHYSICAL], 5)

    def test_calculate_damage_with_resistance(self):
        # 50% fire resistance
        def lookup(_):
            return self.MockStats(resistances={"fire": 0.5})
        calc = DamageCalculator(self.status_system, self.battlefield, combat_stats_lookup=lookup)
        comp = DamageComposition({DamageType.FIRE: 10})
        roll = calc.calculate_damage('attacker', 'target', comp)
        self.assertEqual(roll.composition[DamageType.FIRE], 5)

    def test_calculate_damage_with_vulnerability(self):
        # 50% fire vulnerability
        def lookup(_):
            return self.MockStats(vulnerabilities={"fire": 0.5})
        calc = DamageCalculator(self.status_system, self.battlefield, combat_stats_lookup=lookup)
        comp = DamageComposition({DamageType.FIRE: 10})
        roll = calc.calculate_damage('attacker', 'target', comp)
        self.assertEqual(roll.composition[DamageType.FIRE], 15)

    def test_calculate_damage_with_both(self):
        # 30% resistance, 20% vulnerability
        def lookup(_):
            return self.MockStats(resistances={"fire": 0.3}, vulnerabilities={"fire": 0.2})
        calc = DamageCalculator(self.status_system, self.battlefield, combat_stats_lookup=lookup)
        comp = DamageComposition({DamageType.FIRE: 10})
        roll = calc.calculate_damage('attacker', 'target', comp)
        # 10 * (1 - 0.3 + 0.2) = 10 * 0.9 = 9
        self.assertEqual(roll.composition[DamageType.FIRE], 9)

    def test_calculate_damage_with_extreme_values(self):
        # Resistance > 1 (should clamp to 0 damage)
        def lookup(_):
            return self.MockStats(resistances={"fire": 1.5})
        calc = DamageCalculator(self.status_system, self.battlefield, combat_stats_lookup=lookup)
        comp = DamageComposition({DamageType.FIRE: 10})
        roll = calc.calculate_damage('attacker', 'target', comp)
        self.assertEqual(roll.composition[DamageType.FIRE], 0)
        # Vulnerability > 1 (should increase damage)
        def lookup2(_):
            return self.MockStats(vulnerabilities={"fire": 1.2})
        calc2 = DamageCalculator(self.status_system, self.battlefield, combat_stats_lookup=lookup2)
        comp2 = DamageComposition({DamageType.FIRE: 10})
        roll2 = calc2.calculate_damage('attacker', 'target', comp2)
        self.assertEqual(roll2.composition[DamageType.FIRE], 22)

class TestResistanceComponent(unittest.TestCase):
    def test_add_and_query_permanent(self):
        rc = ResistanceComponent()
        rc.add_resistance("fire", 0.5)
        rc.add_vulnerability("cold", 0.2)
        self.assertAlmostEqual(rc.get_total_resistance("fire"), 0.5)
        self.assertAlmostEqual(rc.get_total_vulnerability("cold"), 0.2)

    def test_flat_and_percent(self):
        rc = ResistanceComponent()
        rc.add_resistance("fire", 0.3, kind="percent")
        rc.add_resistance("fire", 5, kind="flat")
        rc.add_vulnerability("fire", 0.2, kind="percent")
        rc.add_vulnerability("fire", 2, kind="flat")
        q = rc.query("fire")
        self.assertAlmostEqual(q["percent_resistance"], 0.3)
        self.assertAlmostEqual(q["flat_resistance"], 5)
        self.assertAlmostEqual(q["percent_vulnerability"], 0.2)
        self.assertAlmostEqual(q["flat_vulnerability"], 2)

    def test_stacking(self):
        rc = ResistanceComponent()
        rc.add_resistance("fire", 0.2)
        rc.add_resistance("fire", 0.3)
        self.assertAlmostEqual(rc.get_total_resistance("fire"), 0.5)
        rc.add_vulnerability("fire", 0.1)
        rc.add_vulnerability("fire", 0.2)
        self.assertAlmostEqual(rc.get_total_vulnerability("fire"), 0.3)

    def test_temporary_expiry(self):
        rc = ResistanceComponent()
        rc.add_resistance("fire", 0.5, duration=2)
        rc.tick()
        self.assertAlmostEqual(rc.get_total_resistance("fire"), 0.5)
        rc.tick()
        self.assertAlmostEqual(rc.get_total_resistance("fire"), 0.0)

    def test_remove(self):
        rc = ResistanceComponent()
        rc.add_resistance("fire", 0.5)
        rc.remove_resistance("fire", 0.5)
        self.assertAlmostEqual(rc.get_total_resistance("fire"), 0.0)

    def test_combatstats_integration(self):
        class DummyStats(CombatStats):
            def save(self):
                pass  # Override to avoid Flask app context
        stats = DummyStats()
        stats.resistance_component = ResistanceComponent()
        stats.set_resistance("fire", 0.4)
        stats.set_vulnerability("fire", 0.2)
        self.assertAlmostEqual(stats.get_resistance("fire"), 0.4)
        self.assertAlmostEqual(stats.get_vulnerability("fire"), 0.2)

class TestCriticalHitCalculator(unittest.TestCase):
    def setUp(self):
        self.crit_calc = CriticalHitCalculator()
        class Dummy:
            pass
        self.attacker = Dummy()
        self.target = Dummy()
        self.attacker.critical_chance = 0.2
        self.attacker.critical_damage = 2.0
        self.target.status_effects = []

    def test_crit_chance_and_multiplier(self):
        self.assertAlmostEqual(self.crit_calc.get_critical_chance(self.attacker, self.target), 0.2)
        self.assertAlmostEqual(self.crit_calc.get_critical_multiplier(self.attacker, self.target), 2.0)
        # Clamp
        self.attacker.critical_chance = 2.0
        self.assertEqual(self.crit_calc.get_critical_chance(self.attacker, self.target), 0.5)
        self.attacker.critical_chance = 0.0
        self.assertEqual(self.crit_calc.get_critical_chance(self.attacker, self.target), 0.01)

    def test_crit_immunity(self):
        self.assertFalse(self.crit_calc.is_immune_to_critical(self.target))
        self.target.status_effects = [{'type': 'crit_immunity'}]
        self.assertTrue(self.crit_calc.is_immune_to_critical(self.target))

    def test_effect_registration_and_trigger(self):
        called = {}
        def effect_fn(attacker_id, target_id, context):
            called['triggered'] = True
            return {'type': 'special_crit'}
        self.crit_calc.register_critical_effect(effect_fn)
        effects = self.crit_calc.trigger_critical_effects('a', 't', {})
        self.assertTrue(called['triggered'])
        self.assertEqual(effects[0]['type'], 'special_crit')

    def test_get_critical_info(self):
        info = self.crit_calc.get_critical_info(self.attacker, self.target)
        self.assertIn('chance', info)
        self.assertIn('multiplier', info)
        self.assertIn('immune', info)
        self.assertIn('effects', info)

class TestDamageCalculatorCriticalIntegration(unittest.TestCase):
    def setUp(self):
        self.crit_calc = CriticalHitCalculator()
        class Dummy:
            pass
        self.attacker = Dummy()
        self.target = Dummy()
        self.attacker.critical_chance = 1.0  # Always crit for test
        self.attacker.critical_damage = 3.0
        self.target.status_effects = []
        self.target.resistances = {}
        self.target.vulnerabilities = {}
        def lookup(id):
            return self.attacker if id == 'a' else self.target
        self.calc = DamageCalculator(MockStatusSystem(), MockBattlefield(), combat_stats_lookup=lookup, crit_calculator=self.crit_calc)

    def test_crit_multiplier_applied(self):
        comp = DamageComposition({DamageType.FIRE: 10})
        roll = self.calc.calculate_damage('a', 't', comp, is_critical=True)
        self.assertEqual(roll.multiplier, 3.0)

    def test_crit_immunity_blocks_crit(self):
        self.target.status_effects = [{'type': 'crit_immunity'}]
        comp = DamageComposition({DamageType.FIRE: 10})
        roll = self.calc.calculate_damage('a', 't', comp, is_critical=True)
        self.assertEqual(roll.multiplier, 1.0)

    def test_crit_effects_triggered(self):
        called = {}
        def effect_fn(attacker_id, target_id, context):
            called['triggered'] = True
            return {'type': 'special_crit'}
        self.crit_calc.register_critical_effect(effect_fn)
        comp = DamageComposition({DamageType.FIRE: 10})
        roll = self.calc.calculate_damage('a', 't', comp, is_critical=True)
        self.assertTrue(called['triggered'])

class TestDamageModificationPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = DamageModificationPipeline()

    def test_pipeline_stages_and_modifiers(self):
        order = []
        def pre(event):
            order.append('pre')
            event.modified_damage = 10
        def type_mod(event):
            order.append('type')
            event.modified_damage += 2
        def resist(event):
            order.append('resist')
            event.modified_damage *= 2
        self.pipeline.register_modifier('PreCalculation', pre, priority=5)
        self.pipeline.register_modifier('TypeModification', type_mod, priority=10)
        self.pipeline.register_modifier('ResistanceApplication', resist, priority=1)
        event = DamageEvent('a', 't', 5)
        event = self.pipeline.run(event)
        self.assertEqual(order, ['pre', 'type', 'resist'])
        self.assertEqual(event.modified_damage, 24)

    def test_priority_order(self):
        call_order = []
        def mod1(event): call_order.append('mod1')
        def mod2(event): call_order.append('mod2')
        self.pipeline.register_modifier('PreCalculation', mod2, priority=10)
        self.pipeline.register_modifier('PreCalculation', mod1, priority=1)
        event = DamageEvent('a', 't', 1)
        self.pipeline.run(event)
        self.assertEqual(call_order, ['mod1', 'mod2'])

    def test_logging(self):
        def mod(event): event.modified_damage = 42
        self.pipeline.register_modifier('PreCalculation', mod)
        event = DamageEvent('a', 't', 1)
        event = self.pipeline.run(event)
        self.assertTrue(any('Modifier mod applied' in l['info'] for l in event.log))

    def test_delayed_dot(self):
        def dot(event):
            event.delayed = True
            event.delay_duration = 3.0
            event.modified_damage = 5
        self.pipeline.register_modifier('PostCalculation', dot)
        event = DamageEvent('a', 't', 1)
        event = self.pipeline.run(event)
        self.assertTrue(event.delayed)
        self.assertEqual(event.delay_duration, 3.0)
        self.assertEqual(event.modified_damage, 5)

class TestDamageCalculatorPipelineIntegration(unittest.TestCase):
    def setUp(self):
        self.pipeline = DamageModificationPipeline()
        def double(event):
            if event.stage == 'TypeModification':
                event.modified_damage = (event.modified_damage or 0) * 2
        self.pipeline.register_modifier('TypeModification', double)
        class Dummy:
            pass
        self.attacker = Dummy()
        self.target = Dummy()
        self.attacker.critical_chance = 0.0
        self.attacker.critical_damage = 2.0
        self.target.status_effects = []
        self.target.resistances = {}
        self.target.vulnerabilities = {}
        def lookup(id):
            return self.attacker if id == 'a' else self.target
        self.calc = DamageCalculator(MockStatusSystem(), MockBattlefield(), combat_stats_lookup=lookup, pipeline=self.pipeline)

    def test_pipeline_applied_in_calculate_damage(self):
        roll = self.calc.calculate_damage('a', 't', 5)
        self.assertEqual(roll.composition, 10)

class TestDamageEffectivenessMatrix(unittest.TestCase):
    def test_matrix_application(self):
        from app.core.models.combat import DamageEffectivenessMatrix, DamageComposition
        from app.core.enums import DamageType
        # Set up a matrix: fire vs. ice = 2.0, fire vs. fire = 0.5
        matrix = DamageEffectivenessMatrix()
        matrix.set_effectiveness(DamageType.FIRE, DamageType.ICE, 2.0)
        matrix.set_effectiveness(DamageType.FIRE, DamageType.FIRE, 0.5)
        comp = DamageComposition({DamageType.FIRE: 10, DamageType.ICE: 5})
        # Apply to ICE defender
        result = matrix.apply_to_composition(comp, DamageType.ICE)
        self.assertEqual(result[DamageType.FIRE], 20)
        self.assertEqual(result[DamageType.ICE], 5)
        # Apply to FIRE defender
        result2 = matrix.apply_to_composition(comp, DamageType.FIRE)
        self.assertEqual(result2[DamageType.FIRE], 5)
        self.assertEqual(result2[DamageType.ICE], 5)

    def test_integration_with_calculator(self):
        from app.core.models.combat import DamageEffectivenessMatrix, DamageComposition
        from app.core.enums import DamageType
        class Dummy:
            pass
        attacker = Dummy()
        target = Dummy()
        target.damage_type = DamageType.ICE
        target.resistances = {}  # Ensure no resistances
        target.vulnerabilities = {}
        matrix = DamageEffectivenessMatrix()
        matrix.set_effectiveness(DamageType.FIRE, DamageType.ICE, 2.0)
        def lookup(_):
            return target
        calc = DamageCalculator(MockStatusSystem(), MockBattlefield(), combat_stats_lookup=lookup, effectiveness_matrix=matrix)
        comp = DamageComposition({DamageType.FIRE: 10})
        roll = calc.calculate_damage('attacker', 'target', comp)
        self.assertEqual(roll.composition[DamageType.FIRE], 20)

if __name__ == '__main__':
    unittest.main() 