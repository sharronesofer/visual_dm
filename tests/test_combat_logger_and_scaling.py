import pytest
from app.combat.combat_logger import CombatLogger
from app.combat.encounter_scaling import EncounterScaler

def test_combat_logger_basic():
    logger = CombatLogger()
    logger.log_attack(1, 2, 'slash', 10, 'hit', 1)
    logger.log_attack(1, 2, 'stab', 20, 'critical', 2)
    logger.log_attack(2, 1, 'bite', 0, 'miss', 2)
    logger.log_status_effect(1, 'poisoned', 'applied', 1)
    logger.log_status_effect(1, 'poisoned', 'expired', 3)
    logger.log_event('custom', {'foo': 'bar'})
    log = logger.get_log()
    assert len(log) == 6
    stats = logger.get_statistics()
    assert stats['total_attacks'] == 3
    assert stats['total_damage'] == 30
    assert stats['critical_hits'] == 1
    assert stats['misses'] == 1
    assert stats['status_effects_applied'] == 1
    assert stats['status_effects_expired'] == 1
    summary = logger.get_summary()
    assert 'Total Attacks' in summary
    assert 'Critical Hits' in summary

def test_encounter_scaler_balanced():
    scaler = EncounterScaler()
    party = [{'level': 3}, {'level': 2}]
    enemies = [{'level': 2}, {'level': 3}]
    adj = scaler.recommend_adjustment(party, enemies)
    assert adj.get('balanced')

def test_encounter_scaler_party_stronger():
    scaler = EncounterScaler()
    party = [{'level': 5}, {'level': 5}]
    enemies = [{'level': 2}, {'level': 2}]
    adj = scaler.recommend_adjustment(party, enemies)
    assert adj.get('add_enemies') == 1
    assert adj['modify_stats']['hp'] > 1.0

def test_encounter_scaler_enemies_stronger():
    scaler = EncounterScaler()
    party = [{'level': 1}, {'level': 1}]
    enemies = [{'level': 4}, {'level': 4}]
    adj = scaler.recommend_adjustment(party, enemies)
    assert adj.get('remove_enemies') == 1
    assert adj['modify_stats']['hp'] < 1.0

def test_encounter_scaler_adjust_enemies():
    scaler = EncounterScaler()
    enemies = [{'name': 'Goblin', 'level': 2, 'hp': 10, 'damage': 3}]
    adj = {'add_enemies': 2, 'modify_stats': {'hp': 2.0, 'damage': 2.0}}
    new_enemies = scaler.adjust_enemies(enemies, adj)
    assert len(new_enemies) == 3
    for e in new_enemies:
        assert e['hp'] >= 10
        assert e['damage'] >= 3
    adj2 = {'remove_enemies': 2}
    fewer_enemies = scaler.adjust_enemies(new_enemies, adj2)
    assert len(fewer_enemies) == 1 