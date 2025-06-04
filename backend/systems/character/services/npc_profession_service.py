"""
NPC Profession Service

Implements the profession-first procedural generation system for NPCs.
Handles mechanical generation (profession, wealth, equipment, housing) 
and prepares data for GPT personality/backstory generation.
"""

import os
import random
import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from dataclasses import dataclass, field
import json

# Infrastructure imports
from backend.infrastructure.utils.json_utils import load_json

# Enhanced personality utilities
from backend.systems.character.utils.personality_interpreter import (
    generate_complete_personality_deterministic,
    get_personality_backstory_elements,
    format_personality_for_display
)

# Optional LLM service integration
try:
    from backend.infrastructure.llm.services.llm_service import LLMService, GenerationContext
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    LLMService = None
    GenerationContext = None

logger = logging.getLogger(__name__)


@dataclass
class NPCProfessionData:
    """Generated profession data for an NPC"""
    profession: str
    category: str
    social_tier: str
    wealth_amount: int
    housing_type: str
    housing_size: str
    equipment: List[str]
    employees: Optional[int]
    property: List[str]
    spawn_locations: List[str]
    skill_focuses: List[str]
    authority_level: str
    personality_profile: Dict[str, Any] = field(default_factory=dict)
    backstory_elements: Dict[str, str] = field(default_factory=dict)
    llm_enhancements: Dict[str, Any] = field(default_factory=dict)
    base_stats: Optional['NPCBaseStats'] = None


@dataclass
class NPCBaseStats:
    """Base mechanical stats for NPC generation"""
    race: str
    age: int
    attributes: Dict[str, int]
    hidden_personality: Dict[str, int]
    name: str


class NPCProfessionService:
    """
    Service for profession-first NPC generation with enhanced personality capabilities.
    
    Generation Flow:
    1. Roll profession (mechanical/deterministic)
    2. Apply profession effects (wealth, equipment, housing)
    3. Generate base stats (race, age, attributes, hidden personality)
    4. Generate personality using deterministic methods OR LLM (configurable)
    5. Generate backstory elements deterministically OR via LLM
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None, use_llm_for_personality: bool = False):
        """
        Initialize the NPC profession service.
        
        Args:
            llm_service: Optional LLM service for enhanced generation
            use_llm_for_personality: Whether to use LLM for personality generation (vs deterministic)
        """
        self.profession_config = self._load_profession_config()
        self.llm_service = llm_service
        self.use_llm_for_personality = use_llm_for_personality and LLM_AVAILABLE and llm_service is not None
        
    def _load_profession_config(self) -> Dict[str, Any]:
        """Load the profession system configuration"""
        try:
            return load_json("data/systems/character/professions.json")
        except Exception as e:
            logger.error(f"Failed to load profession config: {e}")
            return {"professions": {}, "generation_weights": {}}
    
    def generate_random_profession(self, 
                                 rarity_preference: str = "balanced",
                                 include_criminals: bool = True) -> str:
        """
        Generate a random profession based on rarity weights
        
        Args:
            rarity_preference: "common", "uncommon", "rare", "balanced", or "any"
            include_criminals: Whether to include criminal professions
            
        Returns:
            Profession name
        """
        weights = self.profession_config.get("generation_weights", {})
        
        # Build profession pool based on preferences
        profession_pool = []
        
        if rarity_preference == "balanced":
            # Balanced distribution
            profession_pool.extend(weights.get("common", []) * 50)      # 50% chance each
            profession_pool.extend(weights.get("uncommon", []) * 25)    # 25% chance each
            profession_pool.extend(weights.get("rare", []) * 10)        # 10% chance each
            profession_pool.extend(weights.get("very_rare", []) * 3)    # 3% chance each
            profession_pool.extend(weights.get("unique", []) * 1)       # 1% chance each
        elif rarity_preference == "common":
            profession_pool.extend(weights.get("common", []))
            profession_pool.extend(weights.get("uncommon", []))
        elif rarity_preference == "uncommon":
            profession_pool.extend(weights.get("uncommon", []))
            profession_pool.extend(weights.get("rare", []))
        elif rarity_preference == "rare":
            profession_pool.extend(weights.get("rare", []))
            profession_pool.extend(weights.get("very_rare", []))
            profession_pool.extend(weights.get("unique", []))
        elif rarity_preference == "any":
            # Equal chance for all professions
            profession_pool.extend(weights.get("common", []))
            profession_pool.extend(weights.get("uncommon", []))
            profession_pool.extend(weights.get("rare", []))
            profession_pool.extend(weights.get("very_rare", []))
            profession_pool.extend(weights.get("unique", []))
        
        # Add criminal professions if requested
        if include_criminals:
            if rarity_preference in ["balanced", "common", "any"]:
                profession_pool.extend(weights.get("criminal_common", []) * 10)
            if rarity_preference in ["balanced", "uncommon", "any"]:
                profession_pool.extend(weights.get("criminal_uncommon", []) * 5)
            if rarity_preference in ["balanced", "rare", "any"]:
                profession_pool.extend(weights.get("criminal_rare", []) * 2)
        
        if not profession_pool:
            # Fallback to all common professions
            profession_pool = weights.get("common", ["guard", "shopkeeper"])
        
        return random.choice(profession_pool)
    
    def apply_profession_effects(self, profession_name: str) -> NPCProfessionData:
        """
        Apply profession effects to generate material circumstances
        
        Args:
            profession_name: Name of the profession to apply
            
        Returns:
            Complete profession data with generated values
        """
        profession = self.profession_config.get("professions", {}).get(profession_name)
        if not profession:
            raise ValueError(f"Unknown profession: {profession_name}")
        
        # Generate wealth within range
        wealth_range = profession.get("wealth_range", [10, 100])
        wealth = random.randint(wealth_range[0], wealth_range[1])
        
        # Generate employees if applicable
        employees = None
        if "employees" in profession:
            emp_range = profession["employees"]
            if emp_range[1] > 0:  # Only if max employees > 0
                employees = random.randint(emp_range[0], emp_range[1])
        
        return NPCProfessionData(
            profession=profession_name,
            category=profession.get("category", "common"),
            social_tier=profession.get("social_tier", "lower"),
            wealth_amount=wealth,
            housing_type=profession.get("housing_type", "basic"),
            housing_size=profession.get("housing_size", "small"),
            equipment=profession.get("equipment", []).copy(),
            employees=employees,
            property=profession.get("property", []).copy(),
            spawn_locations=profession.get("spawn_locations", ["common_area"]).copy(),
            skill_focuses=profession.get("skill_focuses", []).copy(),
            authority_level=profession.get("authority_level", "none")
        )
    
    def generate_base_stats(self, profession_data: NPCProfessionData) -> NPCBaseStats:
        """
        Generate base character stats influenced by profession
        
        Args:
            profession_data: Profession information
            
        Returns:
            Base character statistics
        """
        # Generate race (could be influenced by profession in the future)
        races = ["human", "elf", "dwarf", "halfling", "gnome", "half-elf", "half-orc", "tiefling"]
        race_weights = {
            "human": 40,  # Most common
            "elf": 15,
            "dwarf": 15,
            "halfling": 10,
            "gnome": 8,
            "half-elf": 7,
            "half-orc": 3,
            "tiefling": 2
        }
        
        race_pool = []
        for race, weight in race_weights.items():
            race_pool.extend([race] * weight)
        
        race = random.choice(race_pool)
        
        # Generate age based on profession and race
        age = self._generate_age(profession_data, race)
        
        # Generate attributes influenced by profession
        attributes = self._generate_attributes(profession_data)
        
        # Generate hidden personality
        hidden_personality = self._generate_hidden_personality()
        
        # Generate name based on race and gender
        name = self._generate_name(race)
        
        return NPCBaseStats(
            race=race,
            age=age,
            attributes=attributes,
            hidden_personality=hidden_personality,
            name=name
        )
    
    def _generate_age(self, profession_data: NPCProfessionData, race: str) -> int:
        """Generate appropriate age for profession and race"""
        # Base age ranges by profession category
        age_ranges = {
            "nobility": (25, 60),
            "wealthy_merchant": (30, 55),
            "skilled_crafts": (25, 50),
            "learned_professional": (28, 65),
            "military_leadership": (30, 50),
            "service_business": (25, 55),
            "essential_crafts": (20, 50),
            "law_enforcement": (20, 45),
            "military": (18, 40),
            "manual_labor": (16, 50),
            "domestic_service": (16, 60),
            "criminal": (16, 45),
            "destitute": (20, 60)
        }
        
        base_range = age_ranges.get(profession_data.category, (20, 50))
        
        # Adjust for race
        race_modifiers = {
            "elf": (50, 100),      # Elves live much longer
            "dwarf": (10, 30),     # Dwarves age slower
            "gnome": (10, 30),     # Gnomes age slower
            "halfling": (5, 15),   # Halflings age slightly slower
            "human": (0, 0),       # Baseline
            "half-elf": (10, 25),  # Between human and elf
            "half-orc": (-5, -10), # Shorter lived
            "tiefling": (0, 5)     # Slight longevity
        }
        
        race_mod = race_modifiers.get(race, (0, 0))
        
        min_age = max(16, base_range[0] + race_mod[0])
        max_age = base_range[1] + race_mod[1]
        
        return random.randint(min_age, max_age)
    
    def _generate_attributes(self, profession_data: NPCProfessionData) -> Dict[str, int]:
        """Generate attributes with profession-based tendencies"""
        # Base attributes (-3 to +5 system)
        attributes = {
            "STR": random.randint(-1, 2),
            "DEX": random.randint(-1, 2),
            "CON": random.randint(-1, 2),
            "INT": random.randint(-1, 2),
            "WIS": random.randint(-1, 2),
            "CHA": random.randint(-1, 2)
        }
        
        # Apply profession tendencies
        profession_tendencies = {
            "nobility": {"CHA": 2, "INT": 1},
            "wealthy_merchant": {"CHA": 1, "INT": 1},
            "military_nobility": {"STR": 2, "CHA": 1},
            "skilled_crafts": {"DEX": 2, "WIS": 1},
            "learned_professional": {"INT": 3, "WIS": 1},
            "military_leadership": {"STR": 1, "CHA": 2},
            "service_business": {"CHA": 1, "WIS": 1},
            "essential_crafts": {"STR": 1, "DEX": 1},
            "law_enforcement": {"STR": 1, "CON": 1},
            "military": {"STR": 2, "CON": 1},
            "manual_labor": {"STR": 2, "CON": 2},
            "criminal": {"DEX": 2, "INT": 1}
        }
        
        tendencies = profession_tendencies.get(profession_data.category, {})
        for attr, bonus in tendencies.items():
            attributes[attr] = min(5, attributes[attr] + bonus)  # Cap at +5
        
        return attributes
    
    def _generate_hidden_personality(self) -> Dict[str, int]:
        """Generate hidden personality attributes (0-6 scale)"""
        attributes = ['ambition', 'integrity', 'discipline', 'impulsivity', 'pragmatism', 'resilience']
        
        # Generate with slight clustering around 3 (average)
        hidden_traits = {}
        for attribute in attributes:
            # Use normal distribution centered on 3
            value = random.gauss(3, 1.2)
            value = max(0, min(6, round(value)))
            hidden_traits[attribute] = value
        
        # Ensure some variation exists
        total_variation = sum(abs(value - 3) for value in hidden_traits.values())
        if total_variation < 4:
            # Add some random variation
            attribute_to_vary = random.choice(attributes)
            adjustment = random.choice([-2, -1, 1, 2])
            new_value = hidden_traits[attribute_to_vary] + adjustment
            hidden_traits[attribute_to_vary] = max(0, min(6, new_value))
        
        return hidden_traits
    
    def _generate_name(self, race: str) -> str:
        """Generate a name based on race"""
        # Simple name generation - could be expanded with proper name lists
        name_patterns = {
            "human": ["Aldric", "Brenna", "Connor", "Diana", "Erik", "Fiona", "Gareth", "Helena"],
            "elf": ["Aelindra", "Beiro", "Caelynn", "Drannor", "Enna", "Faelar", "Galinndan", "Halimath"],
            "dwarf": ["Adrik", "Bardryn", "Darrak", "Eberk", "Fargrim", "Gardain", "Harbek", "Kildrak"],
            "halfling": ["Alton", "Beau", "Cade", "Eldon", "Finn", "Garret", "Lindal", "Merric"],
            "gnome": ["Alston", "Boddynock", "Dimble", "Eldon", "Fonkin", "Gimble", "Glim", "Jebeddo"],
            "half-elf": ["Aramil", "Berris", "Dayereth", "Enna", "Galinndan", "Heian", "Immeral", "Lamlis"],
            "half-orc": ["Dench", "Feng", "Gell", "Henk", "Holg", "Imsh", "Keth", "Krusk"],
            "tiefling": ["Akmenios", "Amnon", "Barakas", "Damakos", "Ekemon", "Iados", "Kairon", "Leucis"]
        }
        
        names = name_patterns.get(race, name_patterns["human"])
        return random.choice(names)
    
    def generate_npc_by_profession(self, profession: Optional[str] = None) -> NPCProfessionData:
        """
        Generate basic NPC data by profession (deterministic phase).
        
        Args:
            profession: Specific profession or None for random
            
        Returns:
            NPCProfessionData with basic information filled out
        """
        # Determine profession
        if profession is None:
            profession = self.generate_random_profession()
        
        # Apply profession effects
        profession_data = self.apply_profession_effects(profession)
        
        # Generate base stats 
        base_stats = self.generate_base_stats(profession_data)
        
        # Store base stats in the profession data
        profession_data.base_stats = base_stats
        
        return profession_data

    def prepare_gpt_data(self, 
                        profession_data: NPCProfessionData, 
                        base_stats: NPCBaseStats) -> Dict[str, Any]:
        """
        Prepare data for GPT personality generation
        
        Args:
            profession_data: Generated profession information
            base_stats: Generated base character stats
            
        Returns:
            Dictionary ready for GPT prompt formatting
        """
        return {
            "profession": profession_data.profession,
            "race": base_stats.race,
            "age": base_stats.age,
            "attributes": base_stats.attributes,
            "hidden_personality": base_stats.hidden_personality,
            "social_tier": profession_data.social_tier,
            "wealth_level": self._categorize_wealth(profession_data.wealth_amount),
            "authority_level": profession_data.authority_level,
            "housing_type": profession_data.housing_type
        }
    
    def _categorize_wealth(self, wealth_amount: int) -> str:
        """Categorize wealth for GPT context"""
        if wealth_amount >= 10000:
            return "very_wealthy"
        elif wealth_amount >= 2000:
            return "wealthy"
        elif wealth_amount >= 500:
            return "comfortable"
        elif wealth_amount >= 100:
            return "modest"
        elif wealth_amount >= 20:
            return "poor"
        else:
            return "destitute"
    
    def get_gpt_prompt(self, gpt_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Get formatted GPT prompts for personality generation
        
        Args:
            gpt_data: Prepared data from prepare_gpt_data()
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        template = self.profession_config.get("gpt_prompt_template", {})
        
        system_prompt = template.get("system_prompt", 
            "You are generating personality and backstory for an NPC. Focus on personality traits, motivations, speech patterns, and personal history. Do NOT include mechanical stats or wealth information - that's already determined.")
        
        user_prompt_template = template.get("user_prompt",
            "Generate personality and backstory for:\nProfession: {profession}\nRace: {race}\nAge: {age}\nAttributes: {attributes}\nHidden Personality: {hidden_personality}\n\nInclude:\n- Personality description\n- Personal motivation\n- Speech style\n- Brief backstory\n- 2-3 personality quirks\n- How they view their profession")
        
        user_prompt = user_prompt_template.format(**gpt_data)
        
        return system_prompt, user_prompt
    
    def generate_complete_npc(self, profession: Optional[str] = None) -> NPCProfessionData:
        """
        Complete NPC generation with enhanced personality and backstory options.
        
        Args:
            profession: Specific profession to generate, or None for random
            
        Returns:
            Complete NPC data with profession, stats, and personality
        """
        logger.info(f"Starting complete NPC generation for profession: {profession or 'random'}")
        
        # Phase 1: Basic generation (deterministic)
        npc_data = self.generate_npc_by_profession(profession)
        
        # Phase 2: Enhanced personality generation
        personality_profile = self._generate_enhanced_personality(npc_data)
        npc_data.personality_profile = personality_profile
        
        # Phase 3: Backstory generation  
        backstory_elements = self._generate_backstory(npc_data)
        npc_data.backstory_elements = backstory_elements
        
        # Phase 4: Optional LLM enhancement
        if self.use_llm_for_personality:
            enhanced_data = self._enhance_with_llm(npc_data)
            npc_data.llm_enhancements = enhanced_data
        
        logger.info(f"Completed NPC generation: {npc_data.profession} named {getattr(npc_data, 'name', 'Unknown')}")
        return npc_data
    
    def _generate_enhanced_personality(self, npc_data: NPCProfessionData) -> Dict[str, Any]:
        """
        Generate comprehensive personality using deterministic methods.
        
        Args:
            npc_data: NPC data with base stats
            
        Returns:
            Complete personality profile
        """
        try:
            base_stats = npc_data.base_stats
            return generate_complete_personality_deterministic(
                base_stats.hidden_personality,
                profession=npc_data.profession,
                race=base_stats.race,
                age=base_stats.age
            )
        except Exception as e:
            logger.error(f"Failed to generate enhanced personality: {e}")
            return {
                "personality_summary": "A person with typical traits.",
                "speech_style": "Speaks plainly.",
                "primary_motivations": ["basic needs"],
                "personality_quirks": ["unremarkable behavior"],
                "professional_attitude": "Views work as necessary."
            }
    
    def _generate_backstory(self, npc_data: NPCProfessionData) -> Dict[str, str]:
        """
        Generate backstory elements using deterministic methods.
        
        Args:
            npc_data: NPC data with profession and stats
            
        Returns:
            Backstory elements dictionary
        """
        try:
            base_stats = npc_data.base_stats
            return get_personality_backstory_elements(
                base_stats.hidden_personality,
                profession=npc_data.profession,
                race=base_stats.race
            )
        except Exception as e:
            logger.error(f"Failed to generate backstory: {e}")
            return {
                "childhood": "Had a typical upbringing.",
                "formative_experience": "Experienced normal life events.", 
                "professional_path": "Found their current profession through circumstance.",
                "current_situation": "Lives a stable life."
            }
    
    async def _enhance_with_llm(self, npc_data: NPCProfessionData) -> Dict[str, Any]:
        """
        Enhance the NPC with LLM-generated content for richer personality.
        
        Args:
            npc_data: Complete NPC data
            
        Returns:
            LLM-enhanced content
        """
        if not self.llm_service:
            return {"error": "LLM service not available"}
        
        try:
            # Prepare context for LLM enhancement
            personality_context = format_personality_for_display(
                npc_data.base_stats.hidden_personality,
                include_full_profile=True,
                profession=npc_data.profession,
                race=npc_data.base_stats.race,
                age=npc_data.base_stats.age
            )
            
            template_vars = {
                "profession": npc_data.profession,
                "race": npc_data.base_stats.race,
                "age": npc_data.base_stats.age,
                "personality": personality_context,
                "backstory": str(npc_data.backstory_elements),
                "wealth_level": npc_data.wealth_modifier,
                "starting_gold": npc_data.starting_gold
            }
            
            # Generate enhanced content using LLM
            response = await self.llm_service.generate_with_template(
                "npc_enhancement",
                template_vars,
                context=GenerationContext.CHARACTER_CREATION
            )
            
            return {
                "enhanced_description": response.get("content", ""),
                "generation_method": "llm",
                "template_used": "npc_enhancement",
                "metadata": response.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to enhance NPC with LLM: {e}")
            return {
                "error": str(e),
                "generation_method": "llm_failed"
            }
    
    def get_profession_summary(self, profession_name: str) -> Dict[str, Any]:
        """Get summary information about a profession"""
        profession = self.profession_config.get("professions", {}).get(profession_name)
        if not profession:
            return {}
        
        return {
            "name": profession.get("name", profession_name),
            "category": profession.get("category", "unknown"),
            "social_tier": profession.get("social_tier", "working_class"),
            "wealth_range": profession.get("wealth_range", [0, 0]),
            "housing_type": profession.get("housing_type", "unknown"),
            "authority_level": profession.get("authority_level", "none"),
            "skill_focuses": profession.get("skill_focuses", [])
        } 