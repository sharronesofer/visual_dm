#This route exposes a test endpoint for generating loot bundles, combining monster level, equipment pools, item effects, and GPT-based naming/flavor. It integrates several structured rule files and generative functions.
#It directly supports asset, combat, and gpt systems.

from fastapi import APIRouter, Request
import json
from backend.systems.loot.utils.loot_utils_core import (
    group_equipment_by_type,
    generate_loot_bundle,
    gpt_name_and_flavor,
    generate_location_specific_loot,
    get_dynamic_item_price,
    get_item_description_for_player,
    attempt_identify_item,
    identify_item_completely,
    enhance_item,
    add_enchantment_to_item,
    generate_random_item,
    generate_shop_inventory,
    update_shop_prices
)
from fastapi import APIRouter, HTTPException, Path, Query, Body
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

router = APIRouter(
    prefix="/loot",
    tags=["loot"],
    responses={404: {"description": "Not found"}},
)

# Request models
class LootBundleRequest(BaseModel):
    monster_levels: List[int]
    location_id: Optional[int] = None
    region_id: Optional[int] = None
    biome_type: Optional[str] = None
    faction_id: Optional[int] = None
    faction_type: Optional[str] = None
    motif: Optional[str] = None
    source_type: str = "combat"
    quest_related: bool = False

class IdentifyItemRequest(BaseModel):
    item: Dict[str, Any]
    character_id: int
    skill_level: int = 0
    use_magic: bool = False
    spellcraft_bonus: int = 0

class EnhanceItemRequest(BaseModel):
    item: Dict[str, Any]
    character_id: int
    craft_skill_used: str
    character_craft_skill: int = 0
    tool_quality: int = 0
    material_quality: int = 0
    special_ingredients: Optional[List[str]] = None
    force_success: bool = False

# Load your JSON data once at startup
try:
    with open("data/builders/content/equipment/equipment.json") as f:
        EQUIPMENT_LIST = json.load(f)
except FileNotFoundError:
    EQUIPMENT_LIST = []

try:
    with open("data/builders/content/equipment/item_effects.json") as f:
        ITEM_EFFECTS = json.load(f)
except FileNotFoundError:
    ITEM_EFFECTS = []

try:
    with open("data/builders/content/abilities/monster_only_feats.json") as f:
        MONSTER_ABILITIES = json.load(f)
except FileNotFoundError:
    MONSTER_ABILITIES = []

EQUIPMENT_POOL = group_equipment_by_type(EQUIPMENT_LIST)

@router.post("/generate", response_model=Dict[str, Any])
async def generate_loot(request: LootBundleRequest):
    """
    Generate a bundle of loot based on monster levels and optional location data.
    """
    try:
        # If location data is provided, use location-specific loot generation
        if request.location_id or request.region_id or request.biome_type or request.faction_id or request.motif:
            loot_bundle = generate_location_specific_loot(
                location_id=request.location_id,
                location_type=request.source_type,
                biome_type=request.biome_type,
                faction_id=request.faction_id,
                faction_type=request.faction_type,
                motif=request.motif,
                monster_levels=request.monster_levels,
                region_id=request.region_id
            )
        else:
            # Otherwise use standard loot generation
            loot_bundle = generate_loot_bundle(
                monster_levels=request.monster_levels,
                quest_item=request.quest_related,
                source_type=request.source_type,
                location_id=request.location_id,
                region_id=request.region_id
            )
        
        return loot_bundle
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating loot: {str(e)}")

@router.post("/identify", response_model=Dict[str, Any])
async def identify_item(request: IdentifyItemRequest):
    """
    Attempt to identify an item using a character's skills.
    """
    try:
        updated_item, success = attempt_identify_item(
            item=request.item,
            character_id=request.character_id,
            skill_level=request.skill_level,
            use_magic=request.use_magic,
            spellcraft_bonus=request.spellcraft_bonus
        )
        
        return {
            "item": updated_item,
            "success": success,
            "description": get_item_description_for_player(updated_item, 
                                                          3 if request.use_magic else request.skill_level // 5)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error identifying item: {str(e)}")

@router.post("/identify/complete", response_model=Dict[str, Any])
async def complete_identification(
    item: Dict[str, Any] = Body(...),
    character_id: int = Body(...),
    method: str = Body("magic")
):
    """
    Completely identify an item using powerful magic.
    """
    try:
        identified_item = identify_item_completely(
            item=item,
            character_id=character_id,
            method=method
        )
        
        return {
            "item": identified_item,
            "description": get_item_description_for_player(identified_item, 3)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error identifying item: {str(e)}")

@router.post("/enhance", response_model=Dict[str, Any])
async def enhance_item_endpoint(request: EnhanceItemRequest):
    """
    Attempt to enhance an item to the next rarity level.
    """
    try:
        enhanced_item, success = enhance_item(
            item=request.item,
            character_id=request.character_id,
            craft_skill_used=request.craft_skill_used,
            character_craft_skill=request.character_craft_skill,
            tool_quality=request.tool_quality,
            material_quality=request.material_quality,
            special_ingredients=request.special_ingredients,
            force_success=request.force_success
        )
        
        return {
            "item": enhanced_item,
            "success": success,
            "description": get_item_description_for_player(enhanced_item, 3)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enhancing item: {str(e)}")

@router.post("/shop/generate-inventory", response_model=List[Dict[str, Any]])
async def generate_shop_inventory_endpoint(
    shop_id: int = Body(...),
    shop_type: str = Body(...),
    shop_tier: int = Body(1),
    shop_specialty: Optional[str] = Body(None),
    region_id: Optional[int] = Body(None),
    location_id: Optional[int] = Body(None),
    faction_id: Optional[int] = Body(None),
    motif: Optional[str] = Body(None),
    include_magical: bool = Body(True),
    inventory_size: Optional[int] = Body(None)
):
    """
    Generate a complete inventory for a shop.
    """
    try:
        inventory = generate_shop_inventory(
            shop_id=shop_id,
            shop_type=shop_type,
            shop_tier=shop_tier,
            shop_specialty=shop_specialty,
            region_id=region_id,
            location_id=location_id,
            faction_id=faction_id,
            motif=motif,
            include_magical=include_magical,
            inventory_size=inventory_size
        )
        
        return inventory
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating shop inventory: {str(e)}")

@router.post("/generate/random-item", response_model=Dict[str, Any])
async def generate_random_item_endpoint(
    category: str = Body(...),
    rarity: str = Body("common"),
    magical: bool = Body(False),
    min_level: int = Body(1),
    max_level: int = Body(10),
    faction_id: Optional[int] = Body(None),
    motif: Optional[str] = Body(None)
):
    """
    Generate a random item of the specified category.
    """
    try:
        item = generate_random_item(
            category=category,
            rarity=rarity,
            magical=magical,
            min_level=min_level,
            max_level=max_level,
            faction_id=faction_id,
            motif=motif
        )
        
        return {
            "item": item,
            "description": get_item_description_for_player(item, 3)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating random item: {str(e)}")

@router.get("/item/description", response_model=Dict[str, str])
async def get_item_description(
    item_data: str = Query(...),
    knowledge_level: int = Query(0)
):
    """
    Get a description of an item based on the player's knowledge.
    """
    import json
    try:
        item = json.loads(item_data)
        description = get_item_description_for_player(item, knowledge_level)
        return {"description": description}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting item description: {str(e)}")

@router.post("/update-prices", response_model=List[Dict[str, Any]])
async def update_prices_endpoint(
    inventory: List[Dict[str, Any]] = Body(...),
    region_id: int = Body(...),
    motif: Optional[str] = Body(None),
    world_events: Optional[List[str]] = Body(None)
):
    """
    Update prices for all items in a shop's inventory.
    """
    try:
        updated_inventory = update_shop_prices(
            inventory=inventory,
            region_id=region_id,
            motif=motif,
            world_events=world_events
        )
        
        return updated_inventory
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating prices: {str(e)}")

@router.get("/price", response_model=Dict[str, float])
async def get_item_price(
    item_data: str = Query(...),
    region_id: int = Query(...),
    motif: Optional[str] = Query(None),
    world_events: Optional[str] = Query(None)
):
    """
    Get the dynamic price for an item based on region and other factors.
    """
    import json
    try:
        item = json.loads(item_data)
        world_events_list = world_events.split(",") if world_events else None
        
        price = get_dynamic_item_price(
            item=item,
            region_id=region_id,
            motif=motif,
            world_events=world_events_list
        )
        
        return {"price": price}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting item price: {str(e)}")
