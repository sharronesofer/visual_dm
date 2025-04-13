from app.combat.combat_class import CombatAction, Combatant
from app.combat.status_effects_utils import tick_status_effects
from app.data.party_utils import abandon_party
import random

def resolve_turn(combatant: Combatant, targets: list, action_data=None, battlefield=None):
    if combatant.should_abandon():
        abandon_party(combatant.character_id)
        return {
            "character_id": combatant.character_id,
            "action": "abandon_party",
            "result": f"{combatant.character_id} fled due to loyalty loss."
        }

    tick_status_effects(combatant)

    if not targets:
        return {"character_id": combatant.character_id, "action": "idle", "result": "No valid targets"}

    target = targets[0]
    action = action_data or {"name": "basic_attack", "base_damage": 10, "mp_cost": 0}
    combat_action = CombatAction(combatant, target, action, battlefield)
    return combat_action.resolve()


def combat_loop(party, enemies, rounds=5):
    log = []
    all_units = party + enemies

    for _ in range(rounds):
        for unit in all_units:
            targets = enemies if unit in party else party
            if not targets:
                continue
            result = resolve_turn(unit, targets)
            log.append(result)

    return log


def start_combat(encounter_name, player_party, enemy_party):
    battle_id = f"battle_{player_party[0].get('id')}_{enemy_party[0].get('id')}"
    party_objs = [Combatant(p["id"], p) for p in player_party]
    enemy_objs = [Combatant(e["id"], e) for e in enemy_party]
    return battle_id, {"party": party_objs, "enemies": enemy_objs}

def roll_d20():
    return random.randint(1, 20)

def roll_initiative(dexterity):
    return random.randint(1, 20) + ((dexterity - 10) // 2)

def resolve_saving_throw(stat_mod, dc):
    roll = random.randint(1, 20) + stat_mod
    return {"roll": roll, "modifier": stat_mod, "dc": dc, "success": roll >= dc}
