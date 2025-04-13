from app.utils.gpt_utils import GPTRequest
import json

with open("app/rules_json/feats.json") as f:
    ALL_FEATS = {feat["name"]: feat for feat in json.load(f)}

def lookup_actions_for_combatant(feat_names: list[str], combatant: dict, battlefield_context: dict):
    available = []
    mp = combatant.get("MP", 0)
    equipped = combatant.get("equipment", [])

    for name in feat_names:
        feat = ALL_FEATS.get(name)
        if not feat:
            continue

        # Skip passive or irrelevant
        if not feat.get("action_type") or feat.get("combat_irrelevant", False):
            continue

        # MP check
        if feat.get("mp_cost", 0) > mp:
            continue

        # Requires weapon?
        if feat.get("requires_weapon") and not any("weapon" in i for i in equipped):
            continue

        # Required enemy target?
        if feat.get("target", {}).get("type") == "enemy" and not battlefield_context.get("visible_enemies"):
            continue

        available.append(feat)

    return available


def choose_action_gpt(combatant: dict, battlefield_context: dict):
    """
    Returns a JSON action object GPT should respond with.
    """
    feats = combatant.get("feats", [])
    known_actions = lookup_actions_for_combatant(feats, combatant, battlefield_context)

    prompt = {
        "character": combatant,
        "context": battlefield_context,
        "available_actions": known_actions
    }

    system_prompt = (
        "You are a tactical combat AI. Choose the BEST legal combat action for this character "
        "based on their stats, MP, known feats, and the current battlefield. "
        "Only return a single JSON block describing the chosen action."
    )

    gpt = GPTRequest(model="gpt-4", temperature=0.2)
    response = gpt.call(system_prompt, str(prompt))

    try:
        return eval(response) if isinstance(response, str) else response
    except Exception:
        return {"name": "basic_attack", "base_damage": 10, "mp_cost": 0}
