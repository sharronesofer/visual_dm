#This class is responsible for character creation logic, translating input into structured JSON-compatible data ready for storage or gameplay. It supports race selection, attribute assignment, feats, skills, starter kits, and various derived attributes like HP, MP, and AC.

#All inventory and equipment logic should use the canonical Inventory/InventoryItem models and services. Legacy direct field logic has been removed.

import os
import random
from datetime import datetime
from app.rules.rules_utils import calculate_dr
from uuid import uuid4
import uuid
# # # # from app.core.database import db
from app.core.utils.json_utils import load_json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm.exc import NoResultFound
from app.core.models.character import Character
from app.core.models.user import User
from app.core.models.party import Party
from app.core.models.world import Region
from app.core.models.quest import Quest
from app.core.models.spell import Spell
from app.core.models.inventory import InventoryItem
from app.core.models.save import SaveGame

# Get the absolute paths to the JSON files
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'rules')
EQUIPMENT_DATA = load_json(os.path.join(DATA_DIR, 'equipment.json'))
FEATS_DATA = load_json(os.path.join(DATA_DIR, 'feats.json'))
RACES_DATA = load_json(os.path.join(DATA_DIR, 'races.json'))

# Extract feats from the nested structure
FEATS_LIST = {feat["name"]: feat for feat in FEATS_DATA.get("feats", [])}

class CharacterBuilder:
    pass

    def __init__(self, race_data, feat_data, skill_list):
        self.race_data = race_data
        self.feat_data = FEATS_LIST  # Use the extracted feats list
        self.skill_list = skill_list

        self.character_name = None
        self.selected_race = None
        self.attributes = {key: 8 for key in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]}
        self.selected_feats = []
        self.selected_skills = []
        self.skill_points = 0
        self.starter_kit = {}
        self.level = 1
        self.gold = 0
        self.hidden_personality = self.generate_hidden_traits()

    def load_from_input(self, input_data):
        self.character_name = input_data.get("character_name") or input_data.get("name")
        self.set_race(input_data["race"])

        for attribute, value in input_data.get("attributes", {}).items():
            self.assign_attribute(attribute, value)

        for feat in input_data.get("feats", []):
            self.add_feat(feat)

        # Handle skills - can be either a list or a dict
        skills = input_data.get("skills", [])
        if isinstance(skills, list):
            for skill in skills:
                self.assign_skill(skill)
        elif isinstance(skills, dict):
            for skill, rank in skills.items():
                self.assign_skill(skill)

        if "starter_kit" in input_data:
            starter_kits = input_data.get("starter_kits", {})  # must be passed in externally
            self.apply_starter_kit(input_data["starter_kit"], starter_kits)

    def set_race(self, race_name):
        if race_name not in self.race_data:
            raise ValueError(f"Unknown race: {race_name}")
        self.selected_race = race_name
        self.apply_racial_modifiers()

    def apply_racial_modifiers(self):
        mods = self.race_data[self.selected_race].get("ability_modifiers", {})
        for attribute, bonus in mods.items():
            if attribute in self.attributes:
                self.attributes[attribute] += bonus

    def assign_attribute(self, attribute, value):
        if attribute not in self.attributes:
            raise ValueError(f"Unknown attribute: {attribute}")
        self.attributes[attribute] = value

    def add_feat(self, feat_name):
        if feat_name not in self.feat_data:
            raise ValueError(f"Unknown feat: {feat_name}")
        # Check prerequisites
        feat = self.feat_data[feat_name]
        for prereq in feat.get("prerequisites", []):
            # TODO: Add prerequisite checking logic here
            pass
        self.selected_feats.append(feat_name)

    def assign_skill(self, skill_name):
        skill_map = {s.lower(): s for s in self.skill_list}
        skill_key = skill_name.lower()
        if skill_key not in skill_map:
            raise ValueError(f"Unknown skill: {skill_name}")
        self.selected_skills.append(skill_map[skill_key])

    def assign_skills(self, skills_dict):
        for skill_name, rank in skills_dict.items():
            if skill_name.lower() in [s.lower() for s in self.skill_list]:
                self.selected_skills.append(skill_name)
                
    def get_available_starter_kits(self) -> List[Dict[str, Any]]:
        """Get all available starter kits."""
        try:
            starter_kits_data = load_json(os.path.join(DATA_DIR, 'starter_kits.json'))
            return starter_kits_data.get('starter_kits', [])
        except Exception as e:
            print(f"Error loading starter kits: {e}")
            return []

    def apply_starter_kit(self, kit_name: str) -> None:
        """Apply a starter kit to the character."""
        starter_kits = self.get_available_starter_kits()
        kit = next((k for k in starter_kits if k['name'] == kit_name), None)
        
        if not kit:
            raise ValueError(f"Unknown starter kit: {kit_name}")
            
        self.starter_kit = {
            'equipment': kit.get('equipment', []),
            'gold': kit.get('gold', 0)
        }
        self.gold = kit.get('gold', 0)

    def is_valid(self):
        valid = True
        if self.selected_race is None:
            print("❌ Validation: No race selected.")
            valid = False
        if len(self.selected_feats) > 7:
            print(f"❌ Validation: Too many feats ({len(self.selected_feats)} > 7)")
            valid = False
        if len(self.selected_skills) > 18:
            print(f"❌ Validation: Too many skills ({len(self.selected_skills)} > 10)")
            valid = False
        return valid

    def finalize(self):
        import uuid  # 🛠 Fix: Make sure UUID is loaded properly here

        INT = self.attributes.get("INT", 0)
        CON = self.attributes.get("CON", 0)
        DEX = self.attributes.get("DEX", 0)
        level = self.level

        character_id = (
            self.character_name.lower().replace(" ", "_") + "_" + uuid.uuid4().hex[:4]
            if self.character_name else "unnamed_character_" + uuid.uuid4().hex[:4]
        )

        char = {
            "character_name": self.character_name,
            "character_id": character_id,
            "race": self.selected_race,
            "attributes": self.attributes,
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
            # Inventory and equipment are now managed by Inventory/InventoryItem models/services
            # "inventory": self.starter_kit.get("inventory", []),
            # "equipment": self.starter_kit.get("equipment", []),
            "gold": self.gold,
            # "dr": calculate_dr(self.starter_kit.get("equipment", [])),
            "features": [],
            "proficiencies": [],
            "faction_affiliations": [],
            "reputation": 0,
            "cooldowns": {},
            "attributeus_effects": [],
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

        # Inventory/InventoryItem creation should be handled here using canonical services
        # Example (pseudo-code):
        # inventory_service = InventoryService(db)
        # inventory = inventory_service.get_or_create_inventory(character_id, 'character')
        # for item in self.starter_kit.get('equipment', []):
        #     inventory_service.add_item(inventory.id, item_id=item['id'], quantity=1)
        # for item in self.starter_kit.get('inventory', []):
        #     inventory_service.add_item(inventory.id, item_id=item['id'], quantity=item.get('quantity', 1))

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

def finalize_character(character_data):
    """Finalize character creation and create initial arc"""
    try:
        # Create the character
        character = Character(
            name=character_data['name'],
            race=character_data['race'],
            character_class=character_data['class'],
            level=1,
            attributes=character_data['attributes'],
            skills=character_data.get('skills', []),
            inventory=character_data.get('inventory', []),
            equipment=character_data.get('equipment', []),
            gold=random.randint(10, 50),  # Starting gold
            background=character_data.get('background', ''),
            created_at=datetime.utcnow()
        )
        db.session.add(character)
        db.session.commit()

        # Get or create starting region
        region = Region.query.filter_by(name="Starting Region").first()
        if not region:
            # Create starting region if it doesn't exist
            region = Region(
                name="Starting Region",
                description="A peaceful starting area for new adventurers",
                region_type="plains",
                properties={
                    "tiles": generate_basic_tiles(),
                    "weather": "clear",
                    "resources": {
                        "food": 100,
                        "water": 100,
                        "wood": 100
                    }
                }
            )
            db.session.add(region)
            db.session.commit()

        # Create initial arc
        arc = Arc(
            character_id=character.id,
            title="The Beginning",
            description="Your journey begins in the starting region",
            status="active",
            current_stage=1,
            total_stages=5,
            created_at=datetime.utcnow()
        )
        db.session.add(arc)
        db.session.commit()

        return {
            "character": character.to_dict(),
            "region": region.to_dict(),
            "arc": arc.to_dict()
        }
    except Exception as e:
        db.session.rollback()
        raise e

def generate_basic_tiles():
    """Generate basic tile data for a region"""
    tiles = []
    for x in range(10):
        for y in range(10):
            tile = {
                "x": x,
                "y": y,
                "terrain": "grassland",
                "elevation": 0,
                "features": []
            }
            tiles.append(tile)
    return tiles