"""
Skill Check API Endpoints
-------------------------
API endpoints for noncombat skill mechanics in Visual DM.
Provides comprehensive skill check functionality for frontend integration.
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field

from backend.systems.character.models.character import Character
from backend.systems.character.services.skill_check_service import (
    skill_check_service, SkillCheckDifficulty, AdvantageType, SkillCheckModifiers
)
from backend.systems.character.services.noncombat_skills import (
    noncombat_skill_service, PerceptionType, StealthContext, SocialInteractionType
)
from backend.systems.character.services.environmental_skill_mechanics import (
    environmental_skill_service, EnvironmentalContext, TerrainType, EnvironmentalCondition
)
from backend.systems.character.utils.skill_integration_utils import skill_integration_service
from backend.systems.loot.services.enhanced_identification_integration import (
    enhanced_loot_skill_service, ItemDiscoveryMethod, IdentificationSkillType
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/skill-checks", tags=["skill-checks"])

# === REQUEST MODELS ===

class SkillCheckRequest(BaseModel):
    character_id: str
    skill_name: str
    dc: Optional[int] = None
    advantage_type: str = "normal"
    description: str = ""
    environmental_conditions: List[str] = []
    modifiers: Dict[str, int] = {}

class PerceptionCheckRequest(BaseModel):
    character_id: str
    perception_type: str
    hidden_objects: List[Dict[str, Any]] = []
    environmental_conditions: List[str] = []
    dc_override: Optional[int] = None

class StealthCheckRequest(BaseModel):
    character_id: str
    stealth_context: str
    observer_ids: List[str] = []
    environmental_conditions: List[str] = []
    duration_minutes: Optional[int] = None

class SocialInteractionRequest(BaseModel):
    character_id: str
    target_npc_id: str
    interaction_type: str
    goal: str
    social_conditions: List[str] = []
    dc_override: Optional[int] = None

class ItemDiscoveryRequest(BaseModel):
    character_id: str
    discovery_method: str
    location_data: Dict[str, Any]
    available_items: List[Dict[str, Any]] = []
    environmental_conditions: List[str] = []

class ItemIdentificationRequest(BaseModel):
    character_id: str
    item: Dict[str, Any]
    identification_skill: str
    time_spent_minutes: int = 10
    use_tools: bool = False
    environmental_conditions: List[str] = []

class EnvironmentalContextRequest(BaseModel):
    terrain_type: str
    conditions: List[str]
    time_of_day: str = "day"
    season: str = "spring"
    weather_severity: int = 1
    familiarity_level: int = 0
    population_density: str = "moderate"
    magical_presence: bool = False
    threat_level: int = 0

class DialogueSkillRequest(BaseModel):
    character_id: str
    npc_data: Dict[str, Any]
    conversation_context: str

# === HELPER FUNCTIONS ===

def get_character_by_id(character_id: str) -> Character:
    """Get character by ID - implement based on your character service."""
    # This should integrate with your existing character service
    try:
        # Example implementation - replace with your actual character retrieval
        from backend.systems.character.services.character_service import character_service
        character = character_service.get_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail=f"Character {character_id} not found")
        return character
    except ImportError:
        # Fallback if character service not available
        raise HTTPException(status_code=501, detail="Character service not implemented")

def parse_advantage_type(advantage_str: str) -> AdvantageType:
    """Parse advantage type from string."""
    advantage_map = {
        "normal": AdvantageType.NORMAL,
        "advantage": AdvantageType.ADVANTAGE,
        "disadvantage": AdvantageType.DISADVANTAGE,
        "super_advantage": AdvantageType.SUPER_ADVANTAGE,
        "super_disadvantage": AdvantageType.SUPER_DISADVANTAGE
    }
    return advantage_map.get(advantage_str.lower(), AdvantageType.NORMAL)

def parse_perception_type(perception_str: str) -> PerceptionType:
    """Parse perception type from string."""
    perception_map = {
        "visual": PerceptionType.VISUAL,
        "auditory": PerceptionType.AUDITORY,
        "tactile": PerceptionType.TACTILE,
        "search": PerceptionType.SEARCH,
        "insight": PerceptionType.INSIGHT,
        "investigation": PerceptionType.INVESTIGATION
    }
    return perception_map.get(perception_str.lower(), PerceptionType.VISUAL)

def parse_stealth_context(stealth_str: str) -> StealthContext:
    """Parse stealth context from string."""
    stealth_map = {
        "hiding": StealthContext.HIDING,
        "moving_silently": StealthContext.MOVING_SILENTLY,
        "shadowing": StealthContext.SHADOWING,
        "infiltration": StealthContext.INFILTRATION,
        "pickpocketing": StealthContext.PICKPOCKETING,
        "sleight_of_hand": StealthContext.SLEIGHT_OF_HAND
    }
    return stealth_map.get(stealth_str.lower(), StealthContext.HIDING)

def parse_social_interaction_type(social_str: str) -> SocialInteractionType:
    """Parse social interaction type from string."""
    social_map = {
        "persuasion": SocialInteractionType.PERSUASION,
        "deception": SocialInteractionType.DECEPTION,
        "intimidation": SocialInteractionType.INTIMIDATION,
        "diplomacy": SocialInteractionType.DIPLOMACY,
        "gather_info": SocialInteractionType.GATHER_INFO,
        "performance": SocialInteractionType.PERFORMANCE
    }
    return social_map.get(social_str.lower(), SocialInteractionType.PERSUASION)

# === BASIC SKILL CHECK ENDPOINTS ===

@router.post("/basic")
async def make_basic_skill_check(request: SkillCheckRequest):
    """Make a basic skill check with modifiers."""
    try:
        character = get_character_by_id(request.character_id)
        
        # Create modifiers object
        modifiers = SkillCheckModifiers(
            circumstance_bonus=request.modifiers.get("circumstance_bonus", 0),
            equipment_bonus=request.modifiers.get("equipment_bonus", 0),
            condition_penalty=request.modifiers.get("condition_penalty", 0),
            environmental_modifier=request.modifiers.get("environmental_modifier", 0),
            assistance_bonus=request.modifiers.get("assistance_bonus", 0),
            time_modifier=request.modifiers.get("time_modifier", 0)
        )
        
        # Parse advantage type
        advantage_type = parse_advantage_type(request.advantage_type)
        
        # Make the skill check
        result = skill_check_service.make_skill_check(
            character=character,
            skill_name=request.skill_name,
            dc=request.dc,
            advantage_type=advantage_type,
            modifiers=modifiers,
            description=request.description
        )
        
        return {
            "success": True,
            "result": {
                "skill_name": result.skill_name,
                "total_roll": result.total_roll,
                "base_roll": result.base_roll,
                "skill_modifier": result.skill_modifier,
                "final_modifiers": result.final_modifiers,
                "dc": result.dc,
                "success": result.success,
                "degree_of_success": result.degree_of_success,
                "critical_success": result.critical_success,
                "critical_failure": result.critical_failure,
                "description": result.description
            }
        }
    
    except Exception as e:
        logger.error(f"Error in basic skill check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/passive/{character_id}/{skill_name}")
async def get_passive_skill_score(character_id: str, skill_name: str, conditions: List[str] = []):
    """Get passive skill score for a character."""
    try:
        character = get_character_by_id(character_id)
        
        modifiers = SkillCheckModifiers()
        # Apply environmental conditions if provided
        # This could be enhanced to parse conditions into proper modifiers
        
        passive_score = skill_check_service.get_passive_skill_score(
            character=character,
            skill_name=skill_name,
            modifiers=modifiers
        )
        
        return {
            "success": True,
            "passive_score": passive_score.passive_score,
            "skill_modifier": passive_score.skill_modifier,
            "ability_modifier": passive_score.ability_modifier,
            "proficiency_bonus": passive_score.proficiency_bonus
        }
    
    except Exception as e:
        logger.error(f"Error getting passive skill score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === PERCEPTION ENDPOINTS ===

@router.post("/perception")
async def make_perception_check(request: PerceptionCheckRequest):
    """Make a perception check to notice hidden objects."""
    try:
        character = get_character_by_id(request.character_id)
        perception_type = parse_perception_type(request.perception_type)
        
        result = noncombat_skill_service.make_perception_check(
            character=character,
            perception_type=perception_type,
            hidden_objects=request.hidden_objects,
            environmental_conditions=request.environmental_conditions,
            dc_override=request.dc_override
        )
        
        return {
            "success": True,
            "result": {
                "perception_type": result.perception_type.value,
                "detected_objects": result.detected_objects,
                "missed_objects": result.missed_objects,
                "additional_info": result.additional_info,
                "check_result": {
                    "total_roll": result.check_result.total_roll,
                    "success": result.check_result.success,
                    "degree_of_success": result.check_result.degree_of_success
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Error in perception check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/passive-perception/{character_id}")
async def get_passive_perception(character_id: str, conditions: List[str] = []):
    """Get character's passive perception score."""
    try:
        character = get_character_by_id(character_id)
        
        passive_perception = noncombat_skill_service.get_passive_perception(
            character=character,
            environmental_conditions=conditions
        )
        
        return {
            "success": True,
            "passive_perception": passive_perception
        }
    
    except Exception as e:
        logger.error(f"Error getting passive perception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === STEALTH ENDPOINTS ===

@router.post("/stealth")
async def make_stealth_check(request: StealthCheckRequest):
    """Make a stealth check against observers."""
    try:
        character = get_character_by_id(request.character_id)
        stealth_context = parse_stealth_context(request.stealth_context)
        
        # Get observer characters
        observers = []
        for observer_id in request.observer_ids:
            observer = get_character_by_id(observer_id)
            observers.append(observer)
        
        result = noncombat_skill_service.make_stealth_check(
            character=character,
            stealth_context=stealth_context,
            observers=observers,
            environmental_conditions=request.environmental_conditions,
            duration_minutes=request.duration_minutes
        )
        
        return {
            "success": True,
            "result": {
                "stealth_context": result.stealth_context.value,
                "detected_by": result.detected_by,
                "stealth_level": result.stealth_level,
                "duration": result.duration,
                "check_result": {
                    "total_roll": result.check_result.total_roll,
                    "success": len(result.detected_by) == 0,
                    "degree_of_success": result.check_result.degree_of_success
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Error in stealth check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === SOCIAL INTERACTION ENDPOINTS ===

@router.post("/social")
async def make_social_interaction(request: SocialInteractionRequest):
    """Make a social interaction check."""
    try:
        character = get_character_by_id(request.character_id)
        interaction_type = parse_social_interaction_type(request.interaction_type)
        
        # Create target NPC character object
        # This should integrate with your NPC system
        target_char = Character()
        target_char.name = f"NPC_{request.target_npc_id}"
        target_char.uuid = request.target_npc_id
        target_char.stats = {"wisdom": 12}  # Default stats
        
        result = noncombat_skill_service.make_social_check(
            character=character,
            target=target_char,
            interaction_type=interaction_type,
            goal=request.goal,
            social_conditions=request.social_conditions,
            dc_override=request.dc_override
        )
        
        return {
            "success": True,
            "result": {
                "interaction_type": result.interaction_type.value,
                "target_reaction": result.target_reaction,
                "attitude_change": result.attitude_change,
                "information_gained": result.information_gained,
                "consequences": result.consequences,
                "check_result": {
                    "total_roll": result.check_result.total_roll,
                    "success": result.check_result.success,
                    "degree_of_success": result.check_result.degree_of_success
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Error in social interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ITEM DISCOVERY AND IDENTIFICATION ENDPOINTS ===

@router.post("/item-discovery")
async def skill_based_item_discovery(request: ItemDiscoveryRequest):
    """Discover items using skill-based methods."""
    try:
        character = get_character_by_id(request.character_id)
        
        # Parse discovery method
        discovery_method_map = {
            "passive_perception": ItemDiscoveryMethod.PASSIVE_PERCEPTION,
            "active_search": ItemDiscoveryMethod.ACTIVE_SEARCH,
            "investigation": ItemDiscoveryMethod.INVESTIGATION,
            "survival_tracking": ItemDiscoveryMethod.SURVIVAL_TRACKING,
            "arcane_detection": ItemDiscoveryMethod.ARCANE_DETECTION,
            "merchant_appraisal": ItemDiscoveryMethod.MERCHANT_APPRAISAL
        }
        
        discovery_method = discovery_method_map.get(request.discovery_method.lower(), ItemDiscoveryMethod.ACTIVE_SEARCH)
        
        result = enhanced_loot_skill_service.skill_based_item_discovery(
            character=character,
            discovery_method=discovery_method,
            location_data=request.location_data,
            available_items=request.available_items,
            environmental_conditions=request.environmental_conditions
        )
        
        return {
            "success": True,
            "result": {
                "discovery_method": result.discovery_method.value,
                "items_found": result.items_found,
                "additional_information": result.additional_information,
                "environmental_clues": result.environmental_clues,
                "check_result": {
                    "total_roll": getattr(result.skill_check_result, 'total_roll', 0),
                    "success": getattr(result.skill_check_result, 'success', False)
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Error in item discovery: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/item-identification")
async def enhanced_item_identification(request: ItemIdentificationRequest):
    """Identify items using specific skills."""
    try:
        character = get_character_by_id(request.character_id)
        
        # Parse identification skill
        skill_map = {
            "appraise": IdentificationSkillType.APPRAISE,
            "arcana": IdentificationSkillType.ARCANA,
            "history": IdentificationSkillType.HISTORY,
            "investigation": IdentificationSkillType.INVESTIGATION,
            "nature": IdentificationSkillType.NATURE,
            "religion": IdentificationSkillType.RELIGION,
            "survival": IdentificationSkillType.SURVIVAL
        }
        
        identification_skill = skill_map.get(request.identification_skill.lower(), IdentificationSkillType.INVESTIGATION)
        
        result = enhanced_loot_skill_service.enhanced_item_identification(
            character=character,
            item=request.item,
            identification_skill=identification_skill,
            time_spent_minutes=request.time_spent_minutes,
            use_tools=request.use_tools,
            environmental_conditions=request.environmental_conditions
        )
        
        return {
            "success": True,
            "result": {
                "skill_used": result.skill_used,
                "additional_properties_revealed": result.additional_properties_revealed,
                "crafting_insights": result.crafting_insights,
                "historical_context": result.historical_context,
                "estimated_value_accuracy": result.estimated_value_accuracy,
                "confidence_level": result.confidence_level,
                "check_result": {
                    "total_roll": result.skill_check_result.total_roll,
                    "success": result.skill_check_result.success,
                    "degree_of_success": result.skill_check_result.degree_of_success
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Error in item identification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === DIALOGUE INTEGRATION ENDPOINTS ===

@router.post("/dialogue-options")
async def get_dialogue_skill_options(request: DialogueSkillRequest):
    """Get available skill-based dialogue options."""
    try:
        character = get_character_by_id(request.character_id)
        
        options = skill_integration_service.get_dialogue_skill_options(
            character=character,
            npc_data=request.npc_data,
            conversation_context=request.conversation_context
        )
        
        dialogue_options = []
        for option in options:
            dialogue_options.append({
                "skill_name": option.skill_name,
                "option_text": option.option_text,
                "dc": option.dc,
                "success_response": option.success_response,
                "failure_response": option.failure_response,
                "attitude_change_success": option.attitude_change_success,
                "attitude_change_failure": option.attitude_change_failure,
                "unlocks_information": option.unlocks_information or []
            })
        
        return {
            "success": True,
            "dialogue_options": dialogue_options
        }
    
    except Exception as e:
        logger.error(f"Error getting dialogue options: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ENVIRONMENTAL SKILL ENDPOINTS ===

@router.post("/environmental-modifiers")
async def calculate_environmental_modifiers(
    skill_name: str,
    context: EnvironmentalContextRequest,
    character_id: Optional[str] = None
):
    """Calculate environmental modifiers for a skill."""
    try:
        character = None
        if character_id:
            character = get_character_by_id(character_id)
        
        # Parse terrain type
        terrain_map = {
            "urban": TerrainType.URBAN,
            "forest": TerrainType.FOREST,
            "mountain": TerrainType.MOUNTAIN,
            "swamp": TerrainType.SWAMP,
            "desert": TerrainType.DESERT,
            "plains": TerrainType.PLAINS,
            "underground": TerrainType.UNDERGROUND,
            "water": TerrainType.WATER,
            "ruins": TerrainType.RUINS,
            "sacred_ground": TerrainType.SACRED_GROUND
        }
        
        terrain_type = terrain_map.get(context.terrain_type.lower(), TerrainType.PLAINS)
        
        # Parse environmental conditions
        condition_map = {
            "bright_light": EnvironmentalCondition.BRIGHT_LIGHT,
            "dim_light": EnvironmentalCondition.DIM_LIGHT,
            "darkness": EnvironmentalCondition.DARKNESS,
            "heavy_rain": EnvironmentalCondition.HEAVY_RAIN,
            "light_rain": EnvironmentalCondition.LIGHT_RAIN,
            "fog": EnvironmentalCondition.FOG,
            "snow": EnvironmentalCondition.SNOW,
            "wind": EnvironmentalCondition.WIND,
            "extreme_heat": EnvironmentalCondition.EXTREME_HEAT,
            "extreme_cold": EnvironmentalCondition.EXTREME_COLD,
            "loud_environment": EnvironmentalCondition.LOUD_ENVIRONMENT,
            "quiet_environment": EnvironmentalCondition.QUIET_ENVIRONMENT,
            "crowded": EnvironmentalCondition.CROWDED,
            "isolated": EnvironmentalCondition.ISOLATED,
            "familiar_terrain": EnvironmentalCondition.FAMILIAR_TERRAIN,
            "unfamiliar_terrain": EnvironmentalCondition.UNFAMILIAR_TERRAIN
        }
        
        conditions = [condition_map.get(cond.lower()) for cond in context.conditions if condition_map.get(cond.lower())]
        
        environmental_context = EnvironmentalContext(
            terrain_type=terrain_type,
            conditions=conditions,
            time_of_day=context.time_of_day,
            season=context.season,
            weather_severity=context.weather_severity,
            familiarity_level=context.familiarity_level,
            population_density=context.population_density,
            magical_presence=context.magical_presence,
            threat_level=context.threat_level
        )
        
        bonus = environmental_skill_service.calculate_environmental_modifiers(
            skill_name=skill_name,
            environmental_context=environmental_context,
            character=character
        )
        
        return {
            "success": True,
            "modifiers": {
                "terrain_bonus": bonus.terrain_bonus,
                "condition_bonus": bonus.condition_bonus,
                "time_bonus": bonus.time_bonus,
                "familiarity_bonus": bonus.familiarity_bonus,
                "total_modifier": bonus.total_modifier
            }
        }
    
    except Exception as e:
        logger.error(f"Error calculating environmental modifiers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === UTILITY ENDPOINTS ===

@router.get("/skills")
async def get_available_skills():
    """Get list of available skills for skill checks."""
    return {
        "success": True,
        "skills": [
            "perception", "stealth", "investigation", "survival", "nature",
            "arcana", "history", "religion", "insight", "persuasion",
            "deception", "intimidation", "performance", "sleight_of_hand",
            "athletics", "acrobatics", "medicine", "animal_handling",
            "gather_information", "appraise", "search", "diplomacy"
        ]
    }

@router.get("/difficulty-classes")
async def get_difficulty_classes():
    """Get standard difficulty classes."""
    return {
        "success": True,
        "difficulty_classes": {
            "trivial": SkillCheckDifficulty.TRIVIAL.value,
            "easy": SkillCheckDifficulty.EASY.value,
            "medium": SkillCheckDifficulty.MEDIUM.value,
            "hard": SkillCheckDifficulty.HARD.value,
            "very_hard": SkillCheckDifficulty.VERY_HARD.value,
            "nearly_impossible": SkillCheckDifficulty.NEARLY_IMPOSSIBLE.value
        }
    } 