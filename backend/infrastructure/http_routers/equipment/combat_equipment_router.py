"""
Combat Equipment Integration Router

FastAPI router for combat-equipment integration endpoints.
Provides real-time combat calculations with equipment bonuses.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
import logging

from backend.infrastructure.database import get_db
from backend.infrastructure.services.equipment.combat_equipment_integration import CombatEquipmentIntegration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/combat/equipment", tags=["combat-equipment"])

def get_combat_equipment_service(db: Session = Depends(get_db)) -> CombatEquipmentIntegration:
    """Dependency to get combat equipment integration service."""
    return CombatEquipmentIntegration(db)

@router.get("/{character_id}/combat-stats", response_model=Dict[str, Any])
async def get_character_combat_stats(
    character_id: str = Path(..., description="Character ID"),
    service: CombatEquipmentIntegration = Depends(get_combat_equipment_service)
):
    """
    Get comprehensive combat statistics for a character including equipment bonuses.
    
    Returns detailed combat information including:
    - Armor class with equipment bonuses
    - Attack and damage bonuses from weapons
    - Equipment condition and its effect on performance
    - Weapon and armor details
    """
    try:
        combat_stats = service.get_combat_stats_for_character(character_id)
        
        if not combat_stats:
            raise HTTPException(status_code=404, detail=f"No combat stats found for character {character_id}")
        
        return {
            "character_id": character_id,
            "combat_stats": combat_stats,
            "message": "Combat stats calculated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting combat stats for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get combat stats: {str(e)}")

@router.post("/attack-roll", response_model=Dict[str, Any])
async def calculate_attack_roll(
    attack_data: Dict[str, Any] = Body(..., description="Attack calculation data"),
    service: CombatEquipmentIntegration = Depends(get_combat_equipment_service)
):
    """
    Calculate an attack roll with equipment bonuses.
    
    Request body should contain:
    - attacker_id: ID of attacking character
    - target_id: ID of target character
    - weapon_slot: Equipment slot being used (default: main_hand)
    
    Returns detailed attack calculation including hit/miss determination.
    """
    try:
        attacker_id = attack_data.get("attacker_id")
        target_id = attack_data.get("target_id")
        weapon_slot = attack_data.get("weapon_slot", "main_hand")
        
        if not attacker_id or not target_id:
            raise HTTPException(status_code=400, detail="attacker_id and target_id are required")
        
        attack_result = service.calculate_attack_roll(attacker_id, target_id, weapon_slot)
        
        if attack_result.get('error'):
            raise HTTPException(status_code=400, detail=attack_result['error'])
        
        return {
            "success": True,
            "attack_result": attack_result,
            "message": "Attack roll calculated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating attack roll: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate attack roll: {str(e)}")

@router.post("/damage-roll", response_model=Dict[str, Any])
async def calculate_damage_roll(
    damage_data: Dict[str, Any] = Body(..., description="Damage calculation data"),
    service: CombatEquipmentIntegration = Depends(get_combat_equipment_service)
):
    """
    Calculate damage based on an attack result.
    
    Request body should contain the attack_result from calculate_attack_roll.
    
    Returns damage calculation including equipment bonuses and critical hit effects.
    """
    try:
        attack_result = damage_data.get("attack_result")
        
        if not attack_result:
            raise HTTPException(status_code=400, detail="attack_result is required")
        
        damage_result = service.calculate_damage_roll(attack_result)
        
        if damage_result.get('error'):
            raise HTTPException(status_code=400, detail=damage_result['error'])
        
        return {
            "success": True,
            "damage_result": damage_result,
            "message": "Damage roll calculated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating damage roll: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate damage roll: {str(e)}")

@router.post("/combat-action", response_model=Dict[str, Any])
async def execute_combat_action(
    action_data: Dict[str, Any] = Body(..., description="Combat action data"),
    service: CombatEquipmentIntegration = Depends(get_combat_equipment_service)
):
    """
    Execute a complete combat action with equipment integration.
    
    Request body should contain:
    - attacker_id: ID of attacking character
    - target_id: ID of target character
    - action_type: Type of action (default: attack)
    - weapon_slot: Equipment slot being used (default: main_hand)
    
    Returns complete combat resolution including equipment effects and degradation.
    """
    try:
        attacker_id = action_data.get("attacker_id")
        target_id = action_data.get("target_id")
        action_type = action_data.get("action_type", "attack")
        weapon_slot = action_data.get("weapon_slot", "main_hand")
        
        if not attacker_id or not target_id:
            raise HTTPException(status_code=400, detail="attacker_id and target_id are required")
        
        result = service.apply_combat_action(attacker_id, target_id, action_type, weapon_slot)
        
        if not result.get('success'):
            error_msg = result.get('error', 'Combat action failed')
            raise HTTPException(status_code=400, detail=error_msg)
        
        return {
            "success": True,
            "combat_result": result,
            "message": result.get('message', 'Combat action executed successfully')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing combat action: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute combat action: {str(e)}")

@router.get("/{character_id}/weapon-stats", response_model=Dict[str, Any])
async def get_character_weapon_stats(
    character_id: str = Path(..., description="Character ID"),
    weapon_slot: str = Query("main_hand", description="Weapon slot to examine"),
    service: CombatEquipmentIntegration = Depends(get_combat_equipment_service)
):
    """
    Get detailed weapon statistics for a character's equipped weapon.
    
    Returns weapon damage, attack bonuses, condition, and enchantments.
    """
    try:
        combat_stats = service.get_combat_stats_for_character(character_id)
        
        if not combat_stats:
            raise HTTPException(status_code=404, detail=f"No combat stats found for character {character_id}")
        
        if weapon_slot == "main_hand":
            weapon_stats = combat_stats.get('primary_weapon')
        else:
            secondary_weapons = combat_stats.get('secondary_weapons', [])
            weapon_stats = secondary_weapons[0] if secondary_weapons else None
        
        if not weapon_stats:
            return {
                "character_id": character_id,
                "weapon_slot": weapon_slot,
                "weapon_stats": None,
                "message": f"No weapon equipped in {weapon_slot} slot"
            }
        
        return {
            "character_id": character_id,
            "weapon_slot": weapon_slot,
            "weapon_stats": weapon_stats,
            "message": "Weapon stats retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weapon stats for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get weapon stats: {str(e)}")

@router.get("/{character_id}/armor-stats", response_model=Dict[str, Any])
async def get_character_armor_stats(
    character_id: str = Path(..., description="Character ID"),
    service: CombatEquipmentIntegration = Depends(get_combat_equipment_service)
):
    """
    Get detailed armor statistics for a character's equipped armor.
    
    Returns armor class bonuses, damage reduction, condition, and coverage.
    """
    try:
        combat_stats = service.get_combat_stats_for_character(character_id)
        
        if not combat_stats:
            raise HTTPException(status_code=404, detail=f"No combat stats found for character {character_id}")
        
        armor_stats = combat_stats.get('armor')
        shield_stats = combat_stats.get('shield')
        
        return {
            "character_id": character_id,
            "armor_stats": armor_stats,
            "shield_stats": shield_stats,
            "total_armor_class": combat_stats.get('armor_class', 10),
            "message": "Armor stats retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting armor stats for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get armor stats: {str(e)}")

@router.post("/simulate-combat", response_model=Dict[str, Any])
async def simulate_combat_round(
    simulation_data: Dict[str, Any] = Body(..., description="Combat simulation data"),
    service: CombatEquipmentIntegration = Depends(get_combat_equipment_service)
):
    """
    Simulate a full combat round between two characters.
    
    Request body should contain:
    - character1_id: ID of first character
    - character2_id: ID of second character
    - rounds: Number of rounds to simulate (default: 1)
    
    Returns detailed combat simulation results.
    """
    try:
        char1_id = simulation_data.get("character1_id")
        char2_id = simulation_data.get("character2_id")
        rounds = simulation_data.get("rounds", 1)
        
        if not char1_id or not char2_id:
            raise HTTPException(status_code=400, detail="character1_id and character2_id are required")
        
        if rounds < 1 or rounds > 10:
            raise HTTPException(status_code=400, detail="rounds must be between 1 and 10")
        
        simulation_results = []
        
        for round_num in range(1, rounds + 1):
            # Character 1 attacks Character 2
            round_result = {
                'round': round_num,
                'actions': []
            }
            
            action1 = service.apply_combat_action(char1_id, char2_id, "attack")
            round_result['actions'].append({
                'attacker': char1_id,
                'target': char2_id,
                'result': action1
            })
            
            # Character 2 attacks Character 1 (if alive)
            if action1.get('success'):
                action2 = service.apply_combat_action(char2_id, char1_id, "attack")
                round_result['actions'].append({
                    'attacker': char2_id,
                    'target': char1_id,
                    'result': action2
                })
            
            simulation_results.append(round_result)
        
        return {
            "success": True,
            "simulation_results": simulation_results,
            "rounds_simulated": rounds,
            "message": f"Combat simulation completed for {rounds} round(s)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error simulating combat: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate combat: {str(e)}")

@router.get("/health", include_in_schema=False)
async def combat_equipment_health_check():
    """Health check endpoint for combat-equipment integration."""
    return {
        "status": "healthy", 
        "service": "combat_equipment_integration",
        "message": "Combat-Equipment integration service is operational"
    } 