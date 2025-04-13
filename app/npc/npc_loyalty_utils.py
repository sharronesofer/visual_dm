import os
import json
from firebase_admin import db
from app.npc.npc_builder_class import NPCBuilder

RULES_PATH = os.path.join(os.path.dirname(__file__), "../../rules_json")

def load_json(file):
    with open(os.path.join(RULES_PATH, file), "r", encoding="utf-8") as f:
        return json.load(f)

def load_race_data():
    return load_json("races.json")

def load_skill_list():
    return load_json("skills.json").get("skills", [])

def build_npc_from_input(data):
    race_data = load_race_data()
    skills = load_skill_list()

    builder = NPCBuilder(race_data, skills)

    builder.set_id(data.get("npc_id"))
    builder.set_name(data.get("name", "Unnamed NPC"))
    builder.set_race(data.get("race", "Human"))

    for stat, value in data.get("stats", {}).items():
        builder.assign_stat(stat, value)

    for skill in data.get("skills", []):
        builder.add_skill(skill)

    for tag in data.get("tags", []):
        builder.add_tag(tag)

    loc = data.get("location", "0_0")
    region = data.get("region_id", "unknown_region")
    builder.set_location(region, loc)

    builder.generate_motifs()

    # NEW: Set loyalty based on player character personality vector (optional)
    pc_personality = data.get("pc_personality")  # Expecting [int, int, ..., int] of length 6
    if pc_personality:
        builder.init_loyalty_from_pc(pc_personality)

    return builder.finalize()

def save_npc_to_firebase(npc_id: str, npc_data: dict):
    db.reference(f"/npcs/{npc_id}").set(npc_data)

def load_npc_from_firebase(npc_id: str):
    return db.reference(f"/npcs/{npc_id}").get()

def should_abandon(npc_id: str) -> bool:
    ref = db.reference(f"/npcs/{npc_id}/loyalty")
    loyalty_data = ref.get() or {}

    loyalty = loyalty_data.get("loyalty", 0)
    goodwill = loyalty_data.get("goodwill", 0)

    # Abandonment threshold logic: 0 goodwill and loyalty ≤ -5
    return goodwill <= 0 and loyalty <= -5

def abandon_party(npc_id: str) -> dict:
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc = npc_ref.get()

    if not npc or "party_id" not in npc:
        return {"error": "NPC not in a party."}

    party_id = npc["party_id"]
    party_ref = db.reference(f"/parties/{party_id}/members")
    members = party_ref.get() or []

    updated_members = [m for m in members if m != npc_id]
    party_ref.set(updated_members)

    # Clear NPC's party association
    npc_ref.update({"party_id": None})

    return {"message": f"{npc_id} has left party {party_id}.", "remaining_members": updated_members}
