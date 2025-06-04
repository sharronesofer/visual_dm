#This class handles procedural creation of NPCs, including race assignment, skill/tag additions, hidden trait generation, and motif initialization. It produces a JSON-serializable character dictionary suitable for database insertion.
#It supports the npc, motif, region, faction, and memory systems.

import random
from datetime import datetime
from backend.infrastructure.shared.rules.rules_utils import calculate_dr
from backend.systems.npc.config import get_npc_config
from backend.systems.population.models.language_models import Language, LanguageEngine, LanguageProficiency
from uuid import uuid4
import uuid
from typing import List

class NPCBuilder:
    def __init__(self, race_data=None, skill_list=None, language_engine=None):
        self.race_data = race_data or {}
        self.skill_list = skill_list or []
        self.language_engine = language_engine or LanguageEngine()
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
        self.settlement_id = None
        self.background = None
        self.profession = None
        self.motifs = []
        self.known_languages = []
        
        # Load loyalty configuration
        config = get_npc_config()
        loyalty_settings = config.get_loyalty_settings()
        default_goodwill = loyalty_settings.get('loyalty_ranges', {}).get('default_goodwill', 18)
        
        self.loyalty = {
            "score": 0,
            "goodwill": default_goodwill,
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

    def init_loyalty_from_pc(self, pc_data):
        """Initialize loyalty based on PC data instead of Firebase lookup"""
        if not pc_data:
            return {"error": "Missing PC data"}

        loyalty_score = 0
        faction_bonus = {}

        npc_traits = self.tags + list(self.hidden_personality.keys())
        pc_traits = pc_data.get("features", [])

        # Goodwill boost for shared traits
        for trait in pc_traits:
            if trait in npc_traits:
                loyalty_score += 5

        # Bias by alignment match
        if self.data.get("alignment") == pc_data.get("alignment"):
            loyalty_score += 10

        # Bias based on shared factions
        pc_factions = pc_data.get("faction_affiliations", [])
        for faction in pc_factions:
            faction_bonus[faction] = faction_bonus.get(faction, 0) + 10

        # Store result
        self.loyalty = {
            "score": 0,
            "goodwill": loyalty_score,
            "faction_bias": faction_bonus,
            "last_tick": datetime.utcnow().isoformat()
        }

        return {"npc": self.npc_id, "pc": pc_data.get("id"), "goodwill": loyalty_score, "faction_bias": faction_bonus}
            
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
            "known_languages": self.known_languages,
            "backstory": self.generate_backstory(),
            "created_at": datetime.utcnow().isoformat(),
            **self.hidden_personality
        }

    def set_settlement_context(self, settlement_id: str, settlement_type: str = "village"):
        """Set settlement context for language determination"""
        self.settlement_id = settlement_id
        self.settlement_type = settlement_type
        
    def set_background(self, background: str):
        """Set character background for language determination"""
        self.background = background
        
    def set_profession(self, profession: str):
        """Set character profession for language determination"""
        self.profession = profession

    def generate_npc_languages(self) -> List[str]:
        """
        Generate appropriate languages for this NPC based on context.
        
        This system ensures NPCs have realistic language sets while maintaining
        gameplay accessibility through automatic common language resolution.
        
        Returns:
            List of language strings that the NPC knows
        """
        languages = []
        
        # 1. SETTLEMENT PRIMARY LANGUAGE
        # Get the primary language of the settlement
        settlement_primary = self._get_settlement_primary_language()
        languages.append(settlement_primary)
        
        # 2. RACIAL LANGUAGE
        # Add racial language if different from settlement primary
        racial_language = self._get_racial_language()
        if racial_language and racial_language != settlement_primary:
            languages.append(racial_language)
        
        # 3. COMMON (Universal Trade Language)
        # Almost everyone knows at least basic Common
        if "common" not in [lang.lower() for lang in languages]:
            languages.append("common")
        
        # 4. PROFESSION-BASED LANGUAGES
        profession_languages = self._get_profession_languages()
        for lang in profession_languages:
            if lang not in languages:
                languages.append(lang)
        
        # 5. BACKGROUND-BASED LANGUAGES  
        background_languages = self._get_background_languages()
        for lang in background_languages:
            if lang not in languages:
                languages.append(lang)
        
        # 6. INTELLIGENCE-BASED BONUS LANGUAGES
        intelligence_bonus = max(0, (self.attributes["intelligence"] - 12) // 2)
        bonus_languages = self._get_intelligence_bonus_languages(intelligence_bonus, languages)
        languages.extend(bonus_languages)
        
        # 7. TRADE LANGUAGES FOR SETTLEMENTS
        if self.settlement_type in ["town", "city", "metropolis"]:
            if "trade_common" not in languages:
                languages.append("trade_common")
                
        # 8. COASTAL AREAS GET SEA LANGUAGES
        if self._is_coastal_settlement():
            if "sea_cant" not in languages:
                languages.append("sea_cant")
        
        # Cap at reasonable number (3-6 languages typical)
        max_languages = min(6, 3 + intelligence_bonus)
        if len(languages) > max_languages:
            # Keep most important ones: settlement, racial, common, then others
            priority_languages = languages[:3]  # settlement, racial, common
            other_languages = languages[3:]
            random.shuffle(other_languages)
            languages = priority_languages + other_languages[:max_languages-3]
        
        return languages
    
    def _get_settlement_primary_language(self) -> str:
        """Determine the primary language of the settlement"""
        # This could be enhanced to use actual settlement data
        # For now, use region-based logic
        
        region_language_mapping = {
            "elvish_region": "elvish",
            "dwarven_holds": "dwarven", 
            "human_kingdoms": "common",
            "halfling_shires": "halfling",
            "trade_cities": "trade_common",
            "frontier": "common"
        }
        
        # Simple heuristic based on region name or default to common
        for region_key, language in region_language_mapping.items():
            if region_key.lower() in self.region.lower():
                return language
                
        return "common"  # Default fallback
    
    def _get_racial_language(self) -> str:
        """Get the racial language for this NPC's race"""
        racial_language_mapping = {
            "human": "common",
            "elf": "elvish", 
            "dwarf": "dwarven",
            "halfling": "halfling",
            "gnome": "gnomish",
            "orc": "orcish",
            "goblin": "goblin",
            "draconic": "draconic"
        }
        
        race_lower = self.race.lower()
        return racial_language_mapping.get(race_lower, "common")
    
    def _get_profession_languages(self) -> List[str]:
        """Get languages based on profession"""
        if not self.profession:
            return []
            
        profession_languages = {
            "merchant": ["trade_common"],
            "sailor": ["sea_cant"],
            "scholar": ["ancient_imperial", "draconic"],
            "priest": ["celestial", "old_celestial"],
            "wizard": ["draconic", "ancient_imperial"],
            "diplomat": ["elvish", "dwarven", "common"],
            "guard": ["common"],
            "noble": ["elvish", "ancient_imperial"],
            "criminal": ["goblin", "trade_common"],
            "druid": ["druidic", "sylvan"],
            "ranger": ["sylvan", "elvish"]
        }
        
        return profession_languages.get(self.profession.lower(), [])
    
    def _get_background_languages(self) -> List[str]:
        """Get languages based on background"""
        if not self.background:
            return []
            
        background_languages = {
            "noble": ["ancient_imperial", "elvish"],
            "guild_artisan": ["trade_common"],
            "outlander": ["sylvan", "giant"],
            "hermit": ["druidic", "celestial"],
            "sailor": ["sea_cant"],
            "soldier": ["common"],
            "criminal": ["goblin"],
            "entertainer": ["halfling", "elvish"],
            "folk_hero": ["common"],
            "acolyte": ["celestial"]
        }
        
        return background_languages.get(self.background.lower(), [])
    
    def _get_intelligence_bonus_languages(self, bonus_count: int, existing_languages: List[str]) -> List[str]:
        """Get bonus languages based on intelligence"""
        if bonus_count <= 0:
            return []
            
        # Intelligent characters learn useful/prestigious languages
        intelligent_choices = [
            "ancient_imperial",  # Scholarly
            "draconic",         # Magical
            "elvish",           # Cultural
            "dwarven",          # Commercial
            "celestial",        # Religious
            "trade_common",     # Practical
            "sea_cant"          # Travel
        ]
        
        # Filter out languages they already know
        available = [lang for lang in intelligent_choices if lang not in existing_languages]
        
        # Return random selection up to bonus count
        return random.sample(available, min(bonus_count, len(available)))
    
    def _is_coastal_settlement(self) -> bool:
        """Check if this is a coastal settlement (simplified heuristic)"""
        coastal_indicators = ["port", "bay", "harbor", "coast", "sea", "ocean"]
        settlement_name = f"{self.region}_{self.location}".lower()
        return any(indicator in settlement_name for indicator in coastal_indicators)

    def apply_generated_languages(self):
        """Apply the generated languages to the NPC"""
        self.known_languages = self.generate_npc_languages()
        
        # Register with language engine for comprehension calculations
        language_objects = []
        for lang_str in self.known_languages:
            try:
                lang_enum = Language(lang_str.lower())
                # Assume native proficiency for first language, good for others
                comprehension = 1.0 if lang_str == self.known_languages[0] else 0.8
                speaking = 1.0 if lang_str == self.known_languages[0] else 0.8
                literacy = 0.8 if lang_str == "common" else 0.5
                
                proficiency = LanguageProficiency(
                    language=lang_enum,
                    comprehension_level=comprehension,
                    speaking_level=speaking,
                    literacy_level=literacy,
                    formal_training=True
                )
                language_objects.append(proficiency)
            except ValueError:
                # Unknown language, skip
                continue
                
        if language_objects:
            self.language_engine.character_proficiencies[self.npc_id] = language_objects
