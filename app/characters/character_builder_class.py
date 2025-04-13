import random
from datetime import datetime
from app.rules.rules_utils import calculate_dr

class CharacterBuilder:
    def __init__(self, race_data, feat_data, skill_list):
        self.race_data = race_data
        self.feat_data = feat_data
        self.skill_list = skill_list

        self.selected_race = None
        self.stats = {key: 8 for key in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]}
        self.selected_feats = []
        self.selected_skills = []
        self.skill_points = 0
        self.starter_kit = {}
        self.level = 1
        self.gold = 0
        self.hidden_personality = self.generate_hidden_traits()

    def load_from_input(self, input_data):
        self.set_race(input_data["race"])

        for stat, value in input_data.get("stats", {}).items():
            self.assign_stat(stat, value)

        for feat in input_data.get("feats", []):
            self.add_feat(feat)

        for skill in input_data.get("skills", []):
            self.assign_skill(skill)

        if "starter_kit" in input_data:
            starter_kits = input_data.get("starter_kits", {})  # must be passed in
            self.apply_starter_kit(input_data["starter_kit"], starter_kits)

    def set_race(self, race_name):
        if race_name not in self.race_data:
            raise ValueError(f"Unknown race: {race_name}")
        self.selected_race = race_name
        self.apply_racial_modifiers()

    def apply_racial_modifiers(self):
        mods = self.race_data[self.selected_race].get("ability_modifiers", {})
        for stat, bonus in mods.items():
            self.stats[stat] += bonus

    def assign_stat(self, stat, value):
        if stat not in self.stats:
            raise ValueError(f"Unknown stat: {stat}")
        self.stats[stat] = value

    def add_feat(self, feat_name):
        if feat_name not in self.feat_data:
            raise ValueError(f"Unknown feat: {feat_name}")
        self.selected_feats.append(feat_name)

    def assign_skill(self, skill_name):
        if skill_name not in self.skill_list:
            raise ValueError(f"Unknown skill: {skill_name}")
        self.selected_skills.append(skill_name)

    def apply_starter_kit(self, kit_name, starter_kits):
        kit = starter_kits.get(kit_name)
        if not kit:
            raise ValueError(f"Unknown starter kit: {kit_name}")
        self.starter_kit = kit
        self.gold = kit.get("gold", 0)

    def is_valid(self):
        # Add real validation logic here
        return (
            self.selected_race is not None and
            len(self.selected_feats) <= 7 and
            len(self.selected_skills) <= 10  # replace with real skill cap logic
        )

    def finalize(self):
        INT = self.stats["INT"]
        CON = self.stats["CON"]
        DEX = self.stats["DEX"]
        level = self.level

        char = {
            "race": self.selected_race,
            "stats": self.stats,
            "feats": self.selected_feats,
            "skills": self.selected_skills,
            "HP": level * (12 + CON),
            "MP": (level * 8) + (INT * level),
            "AC": 10 + DEX,
            "XP": 0,
            "level": level,
            "alignment": "Neutral",
            "languages": ["Common"],
            "created_at": datetime.utcnow().isoformat(),
            "inventory": self.starter_kit.get("inventory", []),
            "equipment": self.starter_kit.get("equipment", []),
            "gold": self.gold,
            "dr": calculate_dr(self.starter_kit.get("equipment", [])),
            "features": [],
            "proficiencies": [],
            "faction_affiliations": [],
            "reputation": 0,
            "cooldowns": {},
            "status_effects": [],
            "notable_possessions": [],
            "spells": [],
            "known_languages": ["Common"],
            "rumor_index": [],
            "beliefs": {},
            "narrative_motif_pool": {
                "active_motifs": [],
                "motif_history": [],
                "last_rotated": datetime.utcnow().isoformat()
            },
            "narrator_style": "Cormac McCarthy meets Lovecraft"
        }

        return char

    def to_dict(self):
        return self.finalize()

def generate_hidden_traits(self):
    return {
        "hidden_ambition": random.randint(0, 6),
        "hidden_integrity": random.randint(0, 6),
        "hidden_discipline": random.randint(0, 6),
        "hidden_impulsivity": random.randint(0, 6),
        "hidden_pragmatism": random.randint(0, 6),
        "hidden_resilience": random.randint(0, 6)
    }
