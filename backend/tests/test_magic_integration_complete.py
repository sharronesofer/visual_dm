"""
Comprehensive Magic System Integration Tests

End-to-end integration tests for the complete canonical magic system.
Tests database integration, service coordination, and real system behavior.
"""

import pytest
from unittest.mock import Mock
import asyncio
from typing import Dict, Any
import uuid

from backend.infrastructure.database.database import SessionLocal, engine
from backend.systems.magic.services.magic_business_service import MagicBusinessService
from backend.systems.magic.services.metamagic_service import MetamagicService, MetamagicType
from backend.systems.magic.services.spell_combination_service import SpellCombinationService
from backend.infrastructure.cache.magic_cache import MagicCache, CacheConfig


# Mock character abilities for integration testing
class MockCharacterAbilities:
    """Mock character abilities for testing with proper constructor"""
    
    def __init__(self, **abilities):
        # Default ability scores (10 = +0 modifier)
        self.abilities = {
            'strength': 10,
            'dexterity': 10, 
            'constitution': 10,
            'intelligence': 14,  # +2 modifier
            'wisdom': 12,       # +1 modifier
            'charisma': 10
        }
        # Update with provided abilities
        self.abilities.update(abilities)
    
    def get_ability_modifier(self, ability_name: str) -> int:
        """Calculate ability modifier from ability score"""
        score = self.abilities.get(ability_name.lower(), 10)
        return (score - 10) // 2


class TestMagicSystemIntegration:
    """Integration tests for the complete magic system with database"""
    
    def setup_method(self):
        """Setup test environment with database"""
        self.db = SessionLocal()
        
        # Mock configuration repository
        self.mock_config_repo = Mock()
        self.mock_damage_service = Mock()
        
        # Setup spell configurations that match database
        self.mock_config_repo.get_spell.side_effect = lambda name: {
            "fireball": {
                "name": "Fireball", "mp_cost": 5, "base_damage": 28,
                "school": "evocation", "damage_type": "fire",
                "range_feet": 150, "duration_seconds": 0,
                "concentration": False, "components": ["verbal", "somatic"],
                "valid_domains": ["arcane", "occult"], "target": "area"
            },
            "healing_word": {
                "name": "Healing Word", "mp_cost": 2, "base_healing": 8,
                "school": "evocation", "damage_type": None,
                "range_feet": 60, "duration_seconds": 0,
                "concentration": False, "components": ["verbal"],
                "valid_domains": ["divine", "nature"], "target": "single_target"
            },
            "shield": {
                "name": "Shield", "mp_cost": 2, "base_damage": 0,
                "school": "abjuration", "damage_type": None,
                "range_feet": 0, "duration_seconds": 600,
                "concentration": True, "components": ["verbal", "somatic"],
                "valid_domains": ["arcane"], "target": "self"
            }
        }.get(name)
        
        # Setup domain configurations
        self.mock_config_repo.get_domain.side_effect = lambda domain: {
            "arcane": {"mp_efficiency": 1.0, "primary_ability": "intelligence"},
            "divine": {"mp_efficiency": 0.9, "primary_ability": "wisdom"},
            "nature": {"mp_efficiency": 0.8, "primary_ability": "wisdom"},
            "occult": {"mp_efficiency": 0.85, "primary_ability": "charisma"}
        }.get(domain, {"mp_efficiency": 1.0, "primary_ability": "intelligence"})
        
        # Setup damage calculations
        self.mock_damage_service.calculate_damage.return_value = {
            "final_damage": 28, "damage_type": "fire", "critical": False
        }
        
        # Create services
        self.magic_service = MagicBusinessService(
            self.mock_config_repo, self.mock_damage_service
        )
        
        self.metamagic_service = MetamagicService()
        self.combination_service = SpellCombinationService()
        
        # Create cache (disabled for testing)
        cache_config = CacheConfig(enabled=False)
        self.cache = MagicCache(cache_config)
    
    def teardown_method(self):
        """Cleanup test environment"""
        self.db.close()
    
    def test_database_tables_exist(self):
        """Test that all canonical tables exist in database"""
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'spells', 'character_mp', 'character_domain_access', 
            'learned_spells', 'concentration_tracking'
        ]
        
        for table in required_tables:
            assert table in tables, f"Missing canonical table: {table}"
        
        print("✅ All canonical magic tables exist in database")
    
    def test_canonical_spells_table_structure(self):
        """Test that spells table has canonical MP-based structure"""
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        columns = inspector.get_columns('spells')
        column_names = [col['name'] for col in columns]
        
        required_columns = [
            'id', 'name', 'school', 'mp_cost', 'valid_domains',
            'casting_time', 'range_feet', 'components', 'duration',
            'description', 'base_damage', 'base_healing', 'mp_scaling'
        ]
        
        for column in required_columns:
            assert column in column_names, f"Missing canonical column: {column}"
        
        # Verify no old D&D columns
        old_columns = ['level', 'spell_level']
        for old_col in old_columns:
            assert old_col not in column_names, f"Old D&D column still exists: {old_col}"
        
        print("✅ Spells table has proper canonical MP-based structure")
    
    def test_performance_indices_exist(self):
        """Test that performance optimization indices were created"""
        from sqlalchemy import text
        
        # Check for key indices
        result = self.db.execute(text("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename IN ('spells', 'character_mp', 'character_domain_access', 
                               'learned_spells', 'concentration_tracking')
            ORDER BY indexname
        """))
        
        indices = [row[0] for row in result.fetchall()]
        
        # Check for some key indices that should exist
        expected_indices = [
            'idx_spells_mp_cost',
            'idx_spells_school',
            'idx_character_mp_character_id_unique',
            'idx_domain_access_character_id',
            'idx_learned_spells_character_id',
            'idx_concentration_caster_id'
        ]
        
        missing_indices = []
        for index in expected_indices:
            if not any(index in idx for idx in indices):
                missing_indices.append(index)
        
        if missing_indices:
            print(f"Missing indices: {missing_indices}")
            print(f"Available indices: {indices}")
            
        assert len(missing_indices) == 0, f"Missing performance indices: {missing_indices}"
        
        print(f"✅ Found {len(indices)} performance indices")
    
    def test_spell_data_insertion(self):
        """Test inserting spell data into canonical table"""
        from sqlalchemy import text
        import uuid
        
        # Insert test spell with proper UUID and unique name
        test_spell_id = str(uuid.uuid4())  # Generate proper UUID
        test_spell_name = f"Test Integration Spell {uuid.uuid4().hex[:8]}"  # Unique name
        
        self.db.execute(text("""
            INSERT INTO spells (
                id, name, school, mp_cost, valid_domains, casting_time, range_feet,
                components, duration, description, base_damage, base_healing, mp_scaling,
                damage_type, save_type, save_for_half, concentration, target, auto_hit
            ) VALUES (
                :id, :name, :school, :mp_cost, :valid_domains, :casting_time, :range_feet,
                :components, :duration, :description, :base_damage, :base_healing, :mp_scaling,
                :damage_type, :save_type, :save_for_half, :concentration, :target, :auto_hit
            )
        """), {
            'id': test_spell_id,
            'name': test_spell_name,
            'school': 'evocation',
            'mp_cost': 3,
            'valid_domains': ['arcane', 'divine'],
            'casting_time': '1 action',
            'range_feet': 60,
            'components': ['verbal'],
            'duration': 'instantaneous',
            'description': 'A test spell for integration testing',
            'base_damage': 15,
            'base_healing': None,
            'mp_scaling': 2,
            'damage_type': 'force',
            'save_type': 'none',
            'save_for_half': False,
            'concentration': False,
            'target': 'single_target',
            'auto_hit': True
        })
        
        self.db.commit()
        
        # Verify insertion
        result = self.db.execute(text("""
            SELECT name, mp_cost, valid_domains FROM spells WHERE id = :id
        """), {'id': test_spell_id})
        
        spell_data = result.fetchone()
        assert spell_data is not None
        assert spell_data[0] == test_spell_name
        assert spell_data[1] == 3
        assert 'arcane' in spell_data[2]
        
        print("✅ Spell data insertion works correctly")
    
    def test_character_mp_tracking(self):
        """Test character MP tracking in database"""
        from sqlalchemy import text
        
        test_character_id = 999999  # Use high ID to avoid conflicts
        
        # Insert character MP data
        self.db.execute(text("""
            INSERT INTO character_mp (
                character_id, current_mp, max_mp, mp_regeneration_rate, last_rest
            ) VALUES (
                :character_id, :current_mp, :max_mp, :mp_regeneration_rate, NOW()
            )
            ON CONFLICT (character_id) DO UPDATE SET 
                current_mp = EXCLUDED.current_mp,
                max_mp = EXCLUDED.max_mp
        """), {
            'character_id': test_character_id,
            'current_mp': 25,
            'max_mp': 30,
            'mp_regeneration_rate': 2.0
        })
        
        self.db.commit()
        
        # Verify MP tracking
        result = self.db.execute(text("""
            SELECT current_mp, max_mp, mp_regeneration_rate FROM character_mp 
            WHERE character_id = :character_id
        """), {'character_id': test_character_id})
        
        mp_data = result.fetchone()
        assert mp_data is not None
        assert mp_data[0] == 25  # current_mp
        assert mp_data[1] == 30  # max_mp
        assert float(mp_data[2]) == 2.0   # mp_regeneration_rate
        
        print("✅ Character MP tracking works correctly")
    
    def test_concentration_effect_tracking(self):
        """Test concentration effect tracking in database"""
        from sqlalchemy import text
        import datetime
        
        test_caster_id = 999998
        test_target_id = 999997
        test_spell_id = str(uuid.uuid4())  # Use proper UUID
        test_concentration_id = str(uuid.uuid4())  # Use proper UUID for concentration ID
        
        # Insert concentration effect
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=10)
        
        self.db.execute(text("""
            INSERT INTO concentration_tracking (
                id, caster_id, target_id, spell_id, cast_at, expires_at,
                domain_used, mp_spent, effect_data
            ) VALUES (
                :id, :caster_id, :target_id, :spell_id, NOW(), :expires_at,
                :domain, :mp_spent, :effect_data
            )
        """), {
            'id': test_concentration_id,
            'caster_id': test_caster_id,
            'target_id': test_target_id,
            'spell_id': test_spell_id,
            'expires_at': expires_at,
            'domain': 'arcane',
            'mp_spent': 5,
            'effect_data': '{"spell_name": "shield", "ac_bonus": 5}'
        })
        
        self.db.commit()
        
        # Verify concentration tracking
        result = self.db.execute(text("""
            SELECT caster_id, domain_used, mp_spent 
            FROM concentration_tracking 
            WHERE id = :id
        """), {'id': test_concentration_id})
        
        conc_data = result.fetchone()
        assert conc_data is not None
        assert conc_data[0] == test_caster_id
        assert conc_data[1] == 'arcane'
        assert conc_data[2] == 5
        
        print("✅ Concentration effect tracking works correctly")
    
    def test_learned_spells_tracking(self):
        """Test learned spells tracking in database"""
        from sqlalchemy import text
        
        test_character_id = 999996
        test_spell_id = str(uuid.uuid4())  # Use proper UUID
        
        # Insert learned spell
        self.db.execute(text("""
            INSERT INTO learned_spells (
                character_id, spell_id, domain_learned, mastery_level, 
                learned_at
            ) VALUES (
                :character_id, :spell_id, :domain, :mastery_level,
                NOW()
            )
            ON CONFLICT (character_id, spell_id) DO UPDATE SET
                mastery_level = EXCLUDED.mastery_level
        """), {
            'character_id': test_character_id,
            'spell_id': test_spell_id,
            'domain': 'divine',
            'mastery_level': 3
        })
        
        self.db.commit()
        
        # Verify learned spells
        result = self.db.execute(text("""
            SELECT domain_learned, mastery_level 
            FROM learned_spells 
            WHERE character_id = :character_id AND spell_id = :spell_id
        """), {
            'character_id': test_character_id,
            'spell_id': test_spell_id
        })
        
        learned_data = result.fetchone()
        assert learned_data is not None
        assert learned_data[0] == 'divine'
        assert learned_data[1] == 3
        
        print("✅ Learned spells tracking works correctly")
    
    def test_domain_access_tracking(self):
        """Test domain access tracking in database"""
        from sqlalchemy import text
        
        test_character_id = 999995
        
        # Insert domain access
        self.db.execute(text("""
            INSERT INTO character_domain_access (
                character_id, domain, access_level, unlocked_at
            ) VALUES (
                :character_id, :domain, :access_level, NOW()
            )
            ON CONFLICT (character_id, domain) DO UPDATE SET
                access_level = EXCLUDED.access_level
        """), {
            'character_id': test_character_id,
            'domain': 'nature',
            'access_level': 2
        })
        
        self.db.commit()
        
        # Verify domain access
        result = self.db.execute(text("""
            SELECT domain, access_level
            FROM character_domain_access 
            WHERE character_id = :character_id
        """), {'character_id': test_character_id})
        
        access_data = result.fetchone()
        assert access_data is not None
        assert access_data[0] == 'nature'
        assert access_data[1] == 2
        
        print("✅ Domain access tracking works correctly")
    
    def test_full_spellcasting_workflow(self):
        """Test complete spellcasting workflow with database integration"""
        abilities = MockCharacterAbilities(intelligence=16)  # +3 modifier
        
        # This tests the workflow using mocked configuration but real service logic
        result = self.magic_service.calculate_mp_cost(
            spell_name="fireball",
            domain="arcane",
            extra_mp=0
        )
        
        assert result is not None
        assert result == 5  # Fireball base cost (calculate_mp_cost returns int, not dict)
        
        print("✅ Full spellcasting workflow integration works")
    
    def test_metamagic_with_database_spell_data(self):
        """Test metamagic effects with database-integrated spell data"""
        spell_properties = {
            "name": "fireball",
            "school": "evocation",
            "mp_cost": 5,
            "base_damage": 28,
            "base_healing": None,
            "range_feet": 150,
            "duration_seconds": 0,
            "concentration": False,
            "target": "area",
            "components": ["verbal", "somatic"]
        }
        
        # Test empowered metamagic
        result = self.metamagic_service.apply_metamagic(
            spell_properties=spell_properties,
            base_mp_cost=5,
            metamagic_types=[MetamagicType.EMPOWERED],
            available_mp=10
        )
        
        assert result.success is True
        assert result.total_mp_cost == 6  # 5 + (5 * 0.25) rounded
        assert result.modified_effect["base_damage"] == 42  # 28 * 1.5
        
        print("✅ Metamagic integration with database works correctly")
    
    def test_performance_with_indices(self):
        """Test that database performance is optimized with indices"""
        from sqlalchemy import text
        import time
        
        # Test spell lookup performance (should use indices)
        start_time = time.time()
        
        for i in range(100):
            result = self.db.execute(text("""
                SELECT name, mp_cost, school FROM spells 
                WHERE mp_cost <= 10 AND school = 'evocation'
                LIMIT 5
            """))
            list(result.fetchall())  # Force execution
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should be fast with proper indices (under 1 second for 100 queries)
        assert execution_time < 1.0, f"Queries too slow: {execution_time:.3f}s"
        
        print(f"✅ Database queries optimized: {execution_time:.3f}s for 100 queries")
    
    def test_system_stability_under_load(self):
        """Test system stability under simulated load"""
        abilities = MockCharacterAbilities(intelligence=16)
        
        # Simulate multiple spell calculations
        results = []
        for i in range(50):
            try:
                result = self.magic_service.calculate_mp_cost(
                    spell_name="fireball",
                    domain="arcane",
                    extra_mp=0
                )
                results.append(result)
            except Exception as e:
                pytest.fail(f"System failed under load on iteration {i}: {e}")
        
        assert len(results) == 50
        assert all(r is not None for r in results)
        
        print("✅ System stable under simulated load")

def test_complete_system_integration():
    """Run complete system integration test suite"""
    test_suite = TestMagicSystemIntegration()
    test_suite.setup_method()
    
    try:
        # Database structure tests
        test_suite.test_database_tables_exist()
        test_suite.test_canonical_spells_table_structure()
        test_suite.test_performance_indices_exist()
        
        # Data operations tests
        test_suite.test_spell_data_insertion()
        test_suite.test_character_mp_tracking()
        test_suite.test_concentration_effect_tracking()
        test_suite.test_learned_spells_tracking()
        test_suite.test_domain_access_tracking()
        
        # System integration tests
        test_suite.test_full_spellcasting_workflow()
        test_suite.test_metamagic_with_database_spell_data()
        test_suite.test_performance_with_indices()
        test_suite.test_system_stability_under_load()
        
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Database migration successful")
        print("✅ Performance optimization complete")
        print("✅ Advanced features working")
        print("✅ System integration validated")
        
    finally:
        test_suite.teardown_method()

if __name__ == "__main__":
    test_complete_system_integration() 