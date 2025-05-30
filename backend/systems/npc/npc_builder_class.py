#This class handles procedural creation of NPCs, including race assignment, skill/tag additions, hidden trait generation, and motif initialization. It produces a JSON-serializable character dictionary suitable for Firebase insertion.
#It supports the npc, motif, region, faction, and memory systems.

import random
from datetime import datetime
from app.rules.rules_utils import calculate_dr
from uuid import uuid4
import uuid
from firebase_admin import db

class NPCBuilder:
    def __init__(self, race_data=None, skill_list=None):
        self.race_data = race_data or {}
        self.skill_list = skill_list or []
        self.npc_id = f"npc_{uuid.uuid4().hex[:8]}"
        self.name = "Unnamed"
        self.race = "Human"
        self.attributes = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }
        self.skills = []
        self.tags = []
        self.region = "unknown_region"
        self.location = "0_0"
        self.motifs = []
        self.loyalty = {
            "score": 0,
            "goodwill": 18,
            "tags": [],
            "last_tick": datetime.utcnow().isoformat()
        }
        self.hidden_personality = self.generate_hidden_traits()
        
    def generate_hidden_traits(self):
        return {
            "hidden_ambition": random.randint(0, 6),
            "hidden_integrity": random.randint(0, 6),
            "hidden_discipline": random.randint(0, 6),
            "hidden_impulsivity": random.randint(0, 6),
            "hidden_pragmatism": random.randint(0, 6),
            "hidden_resilience": random.randint(0, 6)
        }

    def init_loyalty_from_pc(self, pc_id):
        pc_ref = db.reference(f"/pcs/{pc_id}")
        pc = pc_ref.get()

        if not pc:
            return {"error": "Missing PC"}

        loyalty_score = 0
        faction_bonus = {}

        npc_traits = self.tags + list(self.hidden_personality.keys())
        pc_traits = pc.get("features", [])

        # Goodwill boost for shared traits
        for trait in pc_traits:
            if trait in npc_traits:
                loyalty_score += 5

        # Bias by alignment match
        if self.data.get("alignment") == pc.get("alignment"):
            loyalty_score += 10

        # Bias based on shared factions
        pc_factions = pc.get("faction_affiliations", [])
        for faction in pc_factions:
            faction_bonus[faction] = faction_bonus.get(faction, 0) + 10

        # Store result
        self.loyalty = {
            "score": 0,
            "goodwill": loyalty_score,
            "faction_bias": faction_bonus,
            "last_tick": datetime.utcnow().isoformat()
        }

        return {"npc": self.npc_id, "pc": pc_id, "goodwill": loyalty_score, "faction_bias": faction_bonus}
            
    def set_id(self, npc_id=None):
        if npc_id:
            self.npc_id = npc_id
        else:
            self.npc_id = f"npc_{uuid.uuid4().hex[:8]}"
            
    def set_name(self, name): 
        self.name = name

    def set_race(self, race_name):
        if race_name not in self.race_data:
            raise ValueError(f"Unknown race: {race_name}")
        self.race = race_name
        self.apply_racial_modifiers()

    def apply_racial_modifiers(self):
        mods = self.race_data[self.race].get("ability_modifiers", {})
        for stat, bonus in mods.items():
            self.attributes[stat] += bonus

    def assign_stat(self, stat, value):
        if stat not in self.attributes:
            raise ValueError(f"Unknown stat: {stat}")
        self.attributes[stat] = value

    def add_skill(self, skill_name):
        if skill_name not in self.skill_list:
            raise ValueError(f"Unknown skill: {skill_name}")
        self.skills.append(skill_name)

    def add_tag(self, tag): 
        self.tags.append(tag)

    def set_location(self, region_id, loc_str):
        self.region = region_id
        self.location = loc_str

    def generate_motifs(self, count=3):
        self.motifs = [{
            "theme": random.randint(1, 50),
            "lifespan": (life := random.randint(2, 4)),
            "entropy_tick": 0,
            "weight": 6 - life
        } for _ in range(count)]

    def generate_backstory(self):
        # Placeholder for actual GPT call - would be implemented in production
        return f"A mysterious {self.race} named {self.name} with unknown origins."

    def finalize(self):
        return {
            "npc_id": self.npc_id,
            "name": self.name,
            "race": self.race,
            "attributes": self.attributes,
            "skills": self.skills,
            "tags": self.tags,
            "region_id": self.region,
            "location": self.location,
            "XP": 0,
            "level": 1,
            "inventory": [],
            "equipment": [],
            "gold": 0,
            "dr": 0,
            "loyalty": self.loyalty,
            "faction_affiliations": [],
            "reputation": 0,
            "cooldowns": {},
            "status_effects": [],
            "motif_history": [],
            "narrative_motif_pool": {
                "active_motifs": self.motifs,
                "motif_history": [],
                "last_rotated": datetime.utcnow().isoformat()
            },
            "rumor_index": [],
            "memory_summary": "",
            "known_languages": ["Common"],
            "backstory": self.generate_backstory(),
            "created_at": datetime.utcnow().isoformat(),
            **self.hidden_personality
        }
