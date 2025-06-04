"""
Enhanced combat router combining state management with action handling.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Body, WebSocket, WebSocketDisconnect
from datetime import datetime

from backend.infrastructure.schemas.combat.combat import CombatStateSchema
from backend.infrastructure.services.combat.combat_service import combat_service
from backend.infrastructure.utils.combat.combat_class import Combat
from backend.infrastructure.utils.combat.combat_handler_class import CombatActionHandler, CombatEngine
# from backend.systems.combat.utils import (
#     initiate_combat, resolve_combat_action, 
#     apply_fumble, apply_critical_hit_effect, apply_area_effect,
#     generate_scaled_encounter, generate_location_appropriate_encounter
# )

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/combat",
    tags=["Combat"],
)

# Store active combats for enhanced functionality
active_combats: Dict[str, Combat] = {}

# WebSocket connection manager for real-time combat updates
class CombatWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, combat_id: str):
        await websocket.accept()
        if combat_id not in self.active_connections:
            self.active_connections[combat_id] = []
        self.active_connections[combat_id].append(websocket)
        logger.info(f"WebSocket connected to combat {combat_id}")
    
    def disconnect(self, websocket: WebSocket, combat_id: str):
        if combat_id in self.active_connections:
            if websocket in self.active_connections[combat_id]:
                self.active_connections[combat_id].remove(websocket)
            if not self.active_connections[combat_id]:
                del self.active_connections[combat_id]
        logger.info(f"WebSocket disconnected from combat {combat_id}")
    
    async def broadcast_to_combat(self, combat_id: str, message: dict):
        if combat_id in self.active_connections:
            connections = self.active_connections[combat_id].copy()
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send WebSocket message to combat {combat_id}: {e}")
                    self.active_connections[combat_id].remove(connection)

# Global WebSocket manager instance
websocket_manager = CombatWebSocketManager()

# =============================================================================
# WEBSOCKET REAL-TIME ENDPOINTS
# =============================================================================

@router.websocket("/ws/{combat_id}")
async def websocket_endpoint(websocket: WebSocket, combat_id: str):
    """
    WebSocket endpoint for real-time combat updates.
    Provides live updates for combat events, turn advancement, and status changes.
    """
    await websocket_manager.connect(websocket, combat_id)
    
    try:
        # Send initial combat state
        combat_state = combat_service.get_combat_state(combat_id)
        if combat_state:
            await websocket.send_json({
                "type": "combat_update",
                "combat_id": combat_id,
                "data": combat_state.dict()
            })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for now - could handle combat commands here
            await websocket.send_json({
                "type": "echo",
                "message": f"Received: {data}"
            })
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, combat_id)
        logger.info(f"WebSocket disconnected from combat {combat_id}")
    except Exception as e:
        logger.error(f"WebSocket error for combat {combat_id}: {e}")
        websocket_manager.disconnect(websocket, combat_id)

async def broadcast_combat_event(combat_id: str, event_type: str, data: dict):
    """Helper function to broadcast combat events to all connected clients."""
    message = {
        "type": event_type,
        "combat_id": combat_id,
        "timestamp": str(datetime.utcnow()),
        "data": data
    }
    await websocket_manager.broadcast_to_combat(combat_id, message)

# =============================================================================
# CORE COMBAT STATE MANAGEMENT
# =============================================================================

@router.post("/state", response_model=CombatStateSchema, status_code=status.HTTP_201_CREATED)
def create_combat_state_endpoint(initial_state_data: Optional[Dict] = Body(None)):
    """
    Creates a new combat state. 
    Optionally accepts initial data for the combat setup.
    If no data is provided, a minimal combat state with a new combat_id is created.
    The `Development_Bible.md` mentions `POST /combat/state` to set current combat state. 
    This endpoint serves to initialize/create a new combat instance.
    """
    try:
        combat_state = combat_service.create_new_combat_instance(initial_combat_data=initial_state_data)
        return combat_state
    except Exception as e:
        logger.error(f"Error creating combat state: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/state/{combat_id}", response_model=CombatStateSchema)
def get_combat_state_endpoint(combat_id: str):
    """
    Retrieves the current state of a specific combat instance by its ID.
    This aligns with `GET /combat/state` from `Development_Bible.md`, but is made specific by ID.
    """
    combat_state = combat_service.get_combat_state(combat_id)
    if not combat_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combat instance not found")
    return combat_state

@router.put("/state/{combat_id}", response_model=CombatStateSchema)
def update_combat_state_endpoint(combat_id: str, combat_state_update: CombatStateSchema):
    """
    Updates an existing combat state by its ID.
    The `Development_Bible.md` mentions `POST /combat/state` to set current combat state. 
    A PUT to a specific combat_id is more RESTful for updates.
    """
    updated_state = combat_service.update_combat_state(combat_id, combat_state_update)
    if not updated_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combat instance not found to update")
    return updated_state

@router.delete("/state/{combat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_combat_state_endpoint(combat_id: str):
    """
    Deletes a combat instance by its ID (e.g., when combat ends).
    """
    success = combat_service.end_combat_instance(combat_id)
    
    # Also remove from active combats if present
    if combat_id in active_combats:
        del active_combats[combat_id]
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combat instance not found to delete")

@router.get("/states", response_model=List[CombatStateSchema])
def list_all_combat_states_endpoint():
    """
    Lists all active combat instances. Useful for debugging or an overview.
    """
    return combat_service.list_all_combat_instances()

# =============================================================================
# ENHANCED COMBAT MANAGEMENT
# =============================================================================

@router.post("/create")
async def create_combat(characters: Dict[str, Any] = Body(...)):
    """
    Create a new enhanced combat instance with the provided characters.
    
    Args:
        characters: Dictionary of characters to include in combat
        
    Returns:
        Combat creation result
    """
    try:
        combat = Combat(character_dict=characters)
        combat_id = combat.combat_id
        active_combats[combat_id] = combat
        
        logger.info(f"Created enhanced combat {combat_id}")
        
        return {"combat_id": combat_id, "message": "Combat created successfully"}
    except Exception as e:
        logger.error(f"Error creating enhanced combat: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/start/{combat_id}")
async def start_combat(combat_id: str):
    """
    Start a combat instance.
    
    Args:
        combat_id: ID of the combat to start
        
    Returns:
        Initial combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    try:
        combat = active_combats[combat_id]
        state = combat.start_combat()
        
        # Broadcast combat start event
        await broadcast_combat_event(combat_id, "combat_started", {
            "message": "Combat has begun",
            "state": state
        })
        
        logger.info(f"Started combat {combat_id}")
        
        return {"state": state, "message": "Combat started"}
    except Exception as e:
        logger.error(f"Error starting combat {combat_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/enhanced_state/{combat_id}")
async def get_enhanced_combat_state(combat_id: str):
    """
    Get the current state of an enhanced combat instance.
    
    Args:
        combat_id: ID of the combat
        
    Returns:
        Current combat state with enhanced details
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    state = combat.get_combat_state()
    
    return {"state": state}

@router.post("/next_turn/{combat_id}")
async def next_turn(combat_id: str):
    """
    Advance to the next turn in combat.
    
    Args:
        combat_id: ID of the combat
        
    Returns:
        Updated combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    try:
        combat = active_combats[combat_id]
        state = combat.next_turn()
        
        # Broadcast turn advancement event
        await broadcast_combat_event(combat_id, "turn_advance", {
            "message": "Turn advanced",
            "new_state": state,
            "current_turn": getattr(state, 'current_turn', 0),
            "current_round": getattr(state, 'round_number', 1)
        })
        
        logger.info(f"Advanced to next turn in combat {combat_id}")
        
        return {"state": state, "message": "Advanced to next turn"}
    except Exception as e:
        logger.error(f"Error advancing turn in combat {combat_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# =============================================================================
# COMBAT ACTIONS
# =============================================================================

@router.post("/take_action/{combat_id}")
async def take_action(
    combat_id: str,
    character_id: str = Body(...),
    action_id: str = Body(...),
    target_id: Optional[str] = Body(None)
):
    """
    Have a character take an action in combat.
    
    Args:
        combat_id: ID of the combat
        character_id: ID of the character taking the action
        action_id: ID of the action to take
        target_id: Optional ID of the target
        
    Returns:
        Action result and updated combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    try:
        combat = active_combats[combat_id]
        result = combat.take_action(character_id, action_id, target_id)
        
        # Broadcast action execution event
        await broadcast_combat_event(combat_id, "action_executed", {
            "actor_id": character_id,
            "action_id": action_id,
            "target_id": target_id,
            "result": result,
            "message": f"Action {action_id} executed by {character_id}"
        })
        
        logger.info(f"Character {character_id} took action {action_id} in combat {combat_id}")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing action in combat {combat_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/resolve_action")
async def resolve_action(
    attacker: Dict[str, Any] = Body(...),
    action_data: Dict[str, Any] = Body(...),
    battlefield_context: Dict[str, Any] = Body(...)
):
    """
    Resolve a combat action using the utility functions.
    
    Args:
        attacker: The attacking character data
        action_data: Action information
        battlefield_context: Battlefield context
        
    Returns:
        Action resolution result
    """
    try:
        result = resolve_combat_action(attacker, action_data, battlefield_context)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error resolving combat action: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# =============================================================================
# EFFECTS AND STATUS
# =============================================================================

@router.post("/apply_fumble")
async def apply_fumble_effect(
    attacker_id: str = Body(...),
    battle_id: Optional[str] = Body(None)
):
    """
    Apply a fumble effect to an attacker.
    
    Args:
        attacker_id: ID of the attacker who fumbled
        battle_id: Optional battle ID
        
    Returns:
        Fumble effect result
    """
    try:
        result = apply_fumble(attacker_id, battle_id)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error applying fumble effect: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/apply_critical_effect")
async def apply_critical_effect(
    target_id: str = Body(...),
    damage_type: str = Body(...),
    battle_id: Optional[str] = Body(None)
):
    """
    Apply a critical hit effect based on damage type.
    
    Args:
        target_id: ID of the target
        damage_type: Type of damage dealt
        battle_id: Optional battle ID
        
    Returns:
        Critical effect result
    """
    try:
        result = apply_critical_hit_effect(target_id, damage_type, battle_id)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error applying critical effect: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/apply_area_effect")
async def apply_area_effect_endpoint(
    battle_id: str = Body(...),
    effect_data: Dict[str, Any] = Body(...),
    source_id: Optional[str] = Body(None)
):
    """
    Apply an area effect to multiple targets.
    
    Args:
        battle_id: ID of the battle
        effect_data: Effect configuration
        source_id: Optional source ID
        
    Returns:
        Area effect result
    """
    try:
        result = apply_area_effect(battle_id, effect_data, source_id)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error applying area effect: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# =============================================================================
# ENCOUNTER GENERATION
# =============================================================================

@router.post("/generate_encounter")
async def generate_encounter(
    character_id: str = Body(...),
    location: str = Body(...),
    danger_level: int = Body(...)
):
    """
    Generate a scaled encounter for a character at a location.
    
    Args:
        character_id: ID of the character
        location: Location string (format: "x_y")
        danger_level: Danger level (1-10)
        
    Returns:
        Generated encounter data
    """
    try:
        result = generate_scaled_encounter(character_id, location, danger_level)
        return {"encounter": result}
    except Exception as e:
        logger.error(f"Error generating encounter: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/generate_location_encounter")
async def generate_location_encounter(
    region_id: str = Body(...),
    poi_id: str = Body(...),
    party_level: int = Body(...)
):
    """
    Generate an encounter appropriate for a specific location.
    
    Args:
        region_id: ID of the region
        poi_id: ID of the POI
        party_level: Average party level
        
    Returns:
        Generated encounter data
    """
    try:
        result = generate_location_appropriate_encounter(region_id, poi_id, party_level)
        return {"encounter": result}
    except Exception as e:
        logger.error(f"Error generating location encounter: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.post("/initiate")
async def initiate_combat_endpoint(
    player_party: List[Dict] = Body(...),
    enemy_party: List[Dict] = Body(...),
    battle_name: str = Body("Combat"),
    use_ram: bool = Body(True)
):
    """
    Initialize a new combat using utility functions.
    
    Args:
        player_party: List of player character data
        enemy_party: List of enemy character data
        battle_name: Name for the combat
        use_ram: Whether to store in RAM
        
    Returns:
        Combat initialization result
    """
    try:
        result = initiate_combat(player_party, enemy_party, battle_name, use_ram)
        return {"combat": result}
    except Exception as e:
        logger.error(f"Error initiating combat: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 