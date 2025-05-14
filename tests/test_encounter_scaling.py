import pytest
from app.combat.encounter_scaling import EncounterScaler, PartyRole, EncounterDifficulty
from app.core.rules.balance_constants import BASE_AC, BASE_HIT_DIE, BASE_ATTACK_BONUS

@pytest.fixture
def scaler():
    return EncounterScaler()

@pytest.fixture
def balanced_party():
    return [
        {  # Tank
            'level': 5,
            'max_hp': 50,
            'armor_class': 18,
            'damage_bonus': 3,
            'attack_bonus': BASE_ATTACK_BONUS + 3,
            'support_abilities': [],
            'control_abilities': []
        },
        {  # Damage
            'level': 5,
            'max_hp': 35,
            'armor_class': 15,
            'damage_bonus': 8,
            'attack_bonus': BASE_ATTACK_BONUS + 5,
            'support_abilities': [],
            'control_abilities': []
        },
        {  # Support
            'level': 5,
            'max_hp': 40,
            'armor_class': 16,
            'damage_bonus': 2,
            'healing_bonus': 5,
            'support_abilities': ['heal', 'buff', 'protect'],
            'control_abilities': []
        },
        {  # Control
            'level': 5,
            'max_hp': 38,
            'armor_class': 15,
            'damage_bonus': 4,
            'spell_dc': 15,
            'support_abilities': [],
            'control_abilities': ['stun', 'slow', 'web']
        }
    ]

@pytest.fixture
def balanced_enemies():
    return [
        {  # Tank
            'level': 5,
            'max_hp': 45,
            'armor_class': 17,
            'damage_bonus': 3,
            'role': 'tank'
        },
        {  # Damage
            'level': 5,
            'max_hp': 30,
            'armor_class': 14,
            'damage_bonus': 7,
            'role': 'damage'
        },
        {  # Support
            'level': 5,
            'max_hp': 35,
            'armor_class': 15,
            'damage_bonus': 2,
            'healing_bonus': 4,
            'role': 'support'
        }
    ]

def test_determine_party_roles(scaler, balanced_party):
    roles = scaler.determine_party_roles(balanced_party)
    assert roles[PartyRole.TANK] == 1
    assert roles[PartyRole.DAMAGE] == 1
    assert roles[PartyRole.SUPPORT] == 1
    assert roles[PartyRole.CONTROL] == 1

def test_calculate_party_strength(scaler, balanced_party):
    metrics = scaler.calculate_party_strength(balanced_party)
    assert metrics["total"] == 20  # 4 characters * level 5
    assert metrics["average_level"] == 5.0
    assert len(metrics["roles"]) == 4
    assert metrics["offensive_power"] > 0
    assert metrics["defensive_power"] > 0

def test_calculate_enemy_strength(scaler, balanced_enemies):
    metrics = scaler.calculate_enemy_strength(balanced_enemies)
    assert metrics["total"] == 15  # 3 characters * level 5
    assert metrics["average_level"] == 5.0
    assert len(metrics["roles"]) == 4
    assert metrics["offensive_power"] > 0
    assert metrics["defensive_power"] > 0

def test_recommend_adjustment_balanced(scaler, balanced_party, balanced_enemies):
    adjustment = scaler.recommend_adjustment(balanced_party, balanced_enemies)
    # Should recommend adding one enemy since party has 4 members vs 3 enemies
    assert len(adjustment["add_enemies"]) == 1
    assert adjustment["remove_enemies"] == 0
    # Stats should be roughly balanced (close to 1.0)
    assert 0.8 <= adjustment["modify_stats"]["hp"] <= 1.2
    assert 0.8 <= adjustment["modify_stats"]["damage"] <= 1.2
    assert 0.8 <= adjustment["modify_stats"]["armor_class"] <= 1.2

def test_recommend_adjustment_easy_difficulty(scaler, balanced_party, balanced_enemies):
    adjustment = scaler.recommend_adjustment(
        balanced_party,
        balanced_enemies,
        target_difficulty=EncounterDifficulty.EASY
    )
    # Stats should be lower for easy difficulty
    assert adjustment["modify_stats"]["hp"] < 1.0
    assert adjustment["modify_stats"]["damage"] < 1.0
    assert adjustment["modify_stats"]["armor_class"] < 1.0

def test_recommend_adjustment_hard_difficulty(scaler, balanced_party, balanced_enemies):
    adjustment = scaler.recommend_adjustment(
        balanced_party,
        balanced_enemies,
        target_difficulty=EncounterDifficulty.HARD
    )
    # Stats should be higher for hard difficulty
    assert adjustment["modify_stats"]["hp"] > 1.0
    assert adjustment["modify_stats"]["damage"] > 1.0
    assert adjustment["modify_stats"]["armor_class"] > 1.0

def test_recommend_adjustment_deadly_difficulty(scaler, balanced_party, balanced_enemies):
    adjustment = scaler.recommend_adjustment(
        balanced_party,
        balanced_enemies,
        target_difficulty=EncounterDifficulty.DEADLY
    )
    # Stats should be significantly higher for deadly difficulty
    assert adjustment["modify_stats"]["hp"] >= 1.2
    assert adjustment["modify_stats"]["damage"] >= 1.2
    assert adjustment["modify_stats"]["armor_class"] >= 1.1

def test_adjust_enemies_add(scaler):
    initial_enemies = [{
        'level': 5,
        'max_hp': 40,
        'armor_class': 15,
        'damage_bonus': 5
    }]
    
    adjustment = {
        'add_enemies': [
            {'role': PartyRole.TANK, 'level': 5},
            {'role': PartyRole.DAMAGE, 'level': 5}
        ],
        'modify_stats': {
            'hp': 1.2,
            'damage': 1.1,
            'armor_class': 1.1
        }
    }
    
    new_enemies = scaler.adjust_enemies(initial_enemies, adjustment)
    assert len(new_enemies) == 3
    # Check that new enemies have appropriate stats for their roles
    tank = next(e for e in new_enemies if e.get('role') == 'tank')
    assert tank['hp'] > tank['level'] * BASE_HIT_DIE  # Tank should have above average HP
    damage = next(e for e in new_enemies if e.get('role') == 'damage')
    assert damage['damage_bonus'] > damage['level'] // 2  # Damage dealer should have high damage

def test_adjust_enemies_remove(scaler):
    initial_enemies = [
        {'level': 5, 'max_hp': 40, 'armor_class': 15, 'damage_bonus': 5},
        {'level': 5, 'max_hp': 35, 'armor_class': 14, 'damage_bonus': 6},
        {'level': 5, 'max_hp': 45, 'armor_class': 16, 'damage_bonus': 4}
    ]
    
    adjustment = {
        'remove_enemies': 2,
        'modify_stats': {
            'hp': 1.0,
            'damage': 1.0,
            'armor_class': 1.0
        }
    }
    
    new_enemies = scaler.adjust_enemies(initial_enemies, adjustment)
    assert len(new_enemies) == 1  # Should keep at least one enemy

def test_adjust_enemies_modify_stats(scaler):
    initial_enemies = [{
        'level': 5,
        'max_hp': 40,
        'armor_class': 15,
        'damage_bonus': 5
    }]
    
    adjustment = {
        'modify_stats': {
            'hp': 1.5,
            'damage': 1.3,
            'armor_class': 1.2
        }
    }
    
    new_enemies = scaler.adjust_enemies(initial_enemies, adjustment)
    assert len(new_enemies) == 1
    modified = new_enemies[0]
    assert modified['hp'] == int(40 * 1.5)
    assert modified['damage_bonus'] == int(5 * 1.3)
    assert modified['armor_class'] == int(15 * 1.2)

def test_empty_party_and_enemies(scaler):
    metrics = scaler.calculate_party_strength([])
    assert metrics["total"] == 0
    assert metrics["average_level"] == 0
    assert not metrics["roles"]
    
    metrics = scaler.calculate_enemy_strength([])
    assert metrics["total"] == 0
    assert metrics["average_level"] == 0
    assert not metrics["roles"] 