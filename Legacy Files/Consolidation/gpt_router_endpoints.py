import openai
import json
import logging
from firebase_admin import db
from datetime import datetime
import random

# GPT Router
def gpt_router(importance_score, flags=None):
    flags = flags or {}
    return "gpt-4" if importance_score >= 7 or flags.get("force_gpt4") else "gpt-3.5-turbo"

# Logging GPT usage
def log_gpt_usage(model, usage):
    timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
    db.reference(f'/gpt_usage/{model}/{timestamp}').set(usage)

# DM Context
def build_dm_context():
    global_state = db.reference('/global_state').get() or {}
    return f"Global State: {json.dumps(global_state)}"

# NPC Context
def build_npc_context(npc_id, extra_context=""):
    npc_memory = db.reference(f'/npc_memory/{npc_id.lower()}').get() or {}
    npc_knowledge = db.reference(f'/npc_knowledge/{npc_id.lower()}').get() or {}
    context = f"NPC Memory: {json.dumps(npc_memory)}; NPC Knowledge: {json.dumps(npc_knowledge)}"
    return f"{context}; {extra_context}" if extra_context else context

# Dice Roller
def roll_expression(expr):
    expr = expr.lower().strip().replace(" ", "")
    num, die, mod = 1, 20, 0
    if 'd' in expr:
        parts = expr.split('d')
        num = int(parts[0]) if parts[0] else 1
        if '+' in parts[1]:
            die, mod = map(int, parts[1].split('+'))
        elif '-' in parts[1]:
            die, mod = parts[1].split('-')
            die, mod = int(die), -int(mod)
        else:
            die = int(parts[1])
    rolls = [random.randint(1, die) for _ in range(num)]
    return sum(rolls) + mod

# GPT-driven NPC interaction
def npc_interact(npc_id, player_id, prompt, conversation_history, importance_score=5, flags=None):
    npc_context = build_npc_context(npc_id)
    full_prompt = f"NPC Context: {npc_context}\nConversation: {conversation_history}\nPrompt: {prompt}"

    model = gpt_router(importance_score, flags)

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an NPC in a fantasy world."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=150
    )

    reply = response.choices[0].message.content.strip()
    log_gpt_usage(model, response.get("usage", {}))

    return {"npc_id": npc_id, "reply": reply, "model_used": model}

# DM response
def dm_response(prompt, importance_score=5, flags=None):
    roll_context = ""
    if any(word in prompt.lower() for word in ["attack", "hit", "strike"]):
        attack_result = roll_expression("1d20+5")
        damage_result = roll_expression("1d8+3")
        roll_context = f"Attack Roll: {attack_result}, Damage: {damage_result}"

    dm_context = build_dm_context()
    full_prompt = f"{dm_context}\n{roll_context}\nPrompt: {prompt}"

    model = gpt_router(importance_score, flags)

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are the Dungeon Master."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.8,
        max_tokens=200
    )

    reply = response.choices[0].message.content.strip()
    log_gpt_usage(model, response.get("usage", {}))

    return {"reply": reply, "model_used": model}

# Quest hook detection
def detect_and_log_quest(player_id, npc_id, reply):
    if "quest" in reply.lower():
        from memory_and_logging import append_to_existing_log
        append_to_existing_log(player_id, npc_id, reply)

# Skill Check Resolver
def resolve_skill_check(skill, ability_score, modifiers=None, dc=10):
    modifiers = modifiers or []
    roll = random.randint(1, 20)
    total = roll + ((ability_score - 10) // 2) + sum(modifiers)
    success = total >= dc
    return {"skill": skill, "roll": roll, "total": total, "success": success}