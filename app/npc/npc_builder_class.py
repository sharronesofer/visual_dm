import random
from datetime import datetime
from app.rules.rules_utils import calculate_dr

class NPCBuilder:
    def __init__(self, race_data, skill_list):
        self.race_data = race_data
        self.skill_list = skill_list

        self.npc_id = None
        self.name = "Unnamed NPC"
        self.race = None
        self.stats = {key: 8 for key in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]}
        self.skills = []
        self.tags = []
        self.region = "unknown_region"
        self.location = "0_0"

        self.hidden_personality = self.generate_hidden_traits()
        self.loyalty = {
            "score": 0,
            "goodwill": 18,
            "tags": [],
            "auto_abandon": False,
            "last_tick": datetime.utcnow().isoformat()
        }

        self.motifs = []
        self.relationships = {}

    def generate_hidden_traits(self):
        return {
            "hidden_ambition": random.randint(0, 6),
            "hidden_integrity": random.randint(0, 6),
            "hidden_discipline": random.randint(0, 6),
            "hidden_impulsivity": random.randint(0, 6),
            "hidden_pragmatism": random.randint(0, 6),
            "hidden_resilience": random.randint(0, 6)
        }

    def init_loyalty_from_pc(self, pc_personality):
        npc_vector = list(self.hidden_personality.values())
        dist = sum(abs(a - b) for a, b in zip(npc_vector, pc_personality))
        self.loyalty["goodwill"] = 36 - dist

    def set_id(self, npc_id): self.npc_id = npc_id
    def set_name(self, name): self.name = name

    def set_race(self, race_name):
        if race_name not in self.race_data:
            raise ValueError(f"Unknown race: {race_name}")
        self.race = race_name
        self.apply_racial_modifiers()

    def apply_racial_modifiers(self):
        mods = self.race_data[self.race].get("ability_modifiers", {})
        for stat, bonus in mods.items():
            self.stats[stat] += bonus

    def assign_stat(self, stat, value):
        if stat not in self.stats:
            raise ValueError(f"Unknown stat: {stat}")
        self.stats[stat] = value

    def add_skill(self, skill_name):
        if skill_name not in self.skill_list:
            raise ValueError(f"Unknown skill: {skill_name}")
        self.skills.append(skill_name)

    def add_tag(self, tag): self.tags.append(tag)

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

    def finalize(self):
        return {
            "npc_id": self.npc_id,
            "name": self.name,
            "race": self.race,
            "stats": self.stats,
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
            "created_at": datetime.utcnow().isoformat(),
            **self.hidden_personality
        }
