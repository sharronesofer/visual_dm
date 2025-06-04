"""
Combat WebSocket Handler

This module provides WebSocket communication for the combat system,
handling real-time combat events between Unity client and backend.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Set
from uuid import UUID
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import asdict

# Business imports
from backend.systems.combat.services import CombatService
from backend.systems.combat.models import CombatEncounter, Combatant, CombatAction
from backend.systems.combat.models.combat_action import ActionDefinition

# Infrastructure imports
from backend.infrastructure.repositories.combat import (
    create_combat_repository, 
    create_action_repository, 
    create_dice_service
)


class CombatWebSocketHandler:
    """
    WebSocket handler for real-time combat communication.
    
    Manages connections, message routing, and real-time updates
    for the combat system between Unity client and backend.
    """
    
    def __init__(self):
        # Active WebSocket connections per encounter
        self.encounter_connections: Dict[UUID, Set[WebSocket]] = {}
        
        # Active connections registry
        self.active_connections: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Combat service with dependency injection
        self.combat_service = self._create_combat_service()
    
    def _create_combat_service(self) -> CombatService:
        """Create combat service with injected dependencies."""
        combat_repo = create_combat_repository()
        action_repo = create_action_repository()
        dice_service = create_dice_service()
        
        return CombatService(combat_repo, action_repo, dice_service)
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Handle new WebSocket connection."""
        await websocket.accept()
        
        self.active_connections[websocket] = {
            "client_id": client_id,
            "connected_at": datetime.utcnow(),
            "encounter_id": None,
            "user_id": None
        }
        
        # Send welcome message
        await self.send_message(websocket, {
            "type": "connection_established",
            "data": {
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat(),
                "available_commands": [
                    "create_encounter", "join_encounter", "leave_encounter",
                    "add_combatant", "set_initiative", "start_combat",
                    "execute_action", "advance_turn", "end_combat",
                    "get_encounter_state", "get_available_actions"
                ]
            }
        })
    
    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        if websocket in self.active_connections:
            connection_info = self.active_connections[websocket]
            encounter_id = connection_info.get("encounter_id")
            
            # Remove from encounter connections
            if encounter_id and encounter_id in self.encounter_connections:
                self.encounter_connections[encounter_id].discard(websocket)
                if not self.encounter_connections[encounter_id]:
                    del self.encounter_connections[encounter_id]
            
            # Remove from active connections
            del self.active_connections[websocket]
    
    async def handle_message(self, websocket: WebSocket, data: Dict[str, Any]):
        """Route incoming WebSocket message to appropriate handler."""
        try:
            message_type = data.get("type")
            message_data = data.get("data", {})
            request_id = data.get("request_id")
            
            if message_type == "create_encounter":
                await self._handle_create_encounter(websocket, message_data, request_id)
            elif message_type == "join_encounter":
                await self._handle_join_encounter(websocket, message_data, request_id)
            elif message_type == "leave_encounter":
                await self._handle_leave_encounter(websocket, message_data, request_id)
            elif message_type == "add_combatant":
                await self._handle_add_combatant(websocket, message_data, request_id)
            elif message_type == "set_initiative":
                await self._handle_set_initiative(websocket, message_data, request_id)
            elif message_type == "start_combat":
                await self._handle_start_combat(websocket, message_data, request_id)
            elif message_type == "execute_action":
                await self._handle_execute_action(websocket, message_data, request_id)
            elif message_type == "advance_turn":
                await self._handle_advance_turn(websocket, message_data, request_id)
            elif message_type == "end_combat":
                await self._handle_end_combat(websocket, message_data, request_id)
            elif message_type == "get_encounter_state":
                await self._handle_get_encounter_state(websocket, message_data, request_id)
            elif message_type == "get_available_actions":
                await self._handle_get_available_actions(websocket, message_data, request_id)
            elif message_type == "heartbeat":
                await self._handle_heartbeat(websocket, request_id)
            else:
                await self.send_error(websocket, f"Unknown message type: {message_type}", request_id)
                
        except Exception as e:
            await self.send_error(websocket, str(e), data.get("request_id"))
    
    async def _handle_create_encounter(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle create encounter request."""
        try:
            name = data.get("name", "New Combat Encounter")
            description = data.get("description")
            properties = data.get("properties", {})
            
            encounter = self.combat_service.create_encounter(name, description, properties)
            
            # Add creator to encounter connections
            encounter_id = encounter.id
            if encounter_id not in self.encounter_connections:
                self.encounter_connections[encounter_id] = set()
            
            self.encounter_connections[encounter_id].add(websocket)
            self.active_connections[websocket]["encounter_id"] = encounter_id
            
            await self.send_response(websocket, "encounter_created", {
                "encounter": self._serialize_encounter(encounter)
            }, request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to create encounter: {str(e)}", request_id)
    
    async def _handle_join_encounter(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle join encounter request."""
        try:
            encounter_id = UUID(data["encounter_id"])
            
            encounter = self.combat_service.get_encounter_by_id(encounter_id)
            if not encounter:
                await self.send_error(websocket, "Encounter not found", request_id)
                return
            
            # Add to encounter connections
            if encounter_id not in self.encounter_connections:
                self.encounter_connections[encounter_id] = set()
            
            self.encounter_connections[encounter_id].add(websocket)
            self.active_connections[websocket]["encounter_id"] = encounter_id
            
            await self.send_response(websocket, "encounter_joined", {
                "encounter": self._serialize_encounter(encounter)
            }, request_id)
            
            # Notify other participants
            await self.broadcast_to_encounter(encounter_id, {
                "type": "participant_joined",
                "data": {
                    "client_id": self.active_connections[websocket].get("client_id"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }, exclude=websocket)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to join encounter: {str(e)}", request_id)
    
    async def _handle_add_combatant(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle add combatant request."""
        try:
            encounter_id = UUID(data["encounter_id"])
            combatant_data = data["combatant"]
            
            # Create combatant from data
            combatant = self._deserialize_combatant(combatant_data)
            
            encounter = self.combat_service.add_combatant_to_encounter(encounter_id, combatant)
            
            await self.send_response(websocket, "combatant_added", {
                "encounter": self._serialize_encounter(encounter),
                "combatant": self._serialize_combatant(combatant)
            }, request_id)
            
            # Broadcast to all encounter participants
            await self.broadcast_to_encounter(encounter_id, {
                "type": "combatant_added",
                "data": {
                    "combatant": self._serialize_combatant(combatant),
                    "encounter_state": self._serialize_encounter(encounter)
                }
            }, exclude=websocket)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to add combatant: {str(e)}", request_id)
    
    async def _handle_execute_action(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle execute action request."""
        try:
            encounter_id = UUID(data["encounter_id"])
            actor_id = UUID(data["actor_id"])
            action_id = data["action_id"]
            target_ids = [UUID(tid) for tid in data.get("target_ids", [])]
            additional_data = data.get("additional_data", {})
            
            encounter, action_result = self.combat_service.execute_action(
                encounter_id, actor_id, action_id, target_ids, additional_data
            )
            
            await self.send_response(websocket, "action_executed", {
                "encounter": self._serialize_encounter(encounter),
                "action_result": {
                    "success": action_result.success,
                    "message": action_result.message,
                    "damage_dealt": action_result.damage_dealt,
                    "healing_applied": action_result.healing_applied,
                    "targets_affected": [str(tid) for tid in action_result.targets_affected],
                    "status_effects_applied": action_result.status_effects_applied,
                    "additional_data": action_result.additional_data
                }
            }, request_id)
            
            # Broadcast action to all participants
            await self.broadcast_to_encounter(encounter_id, {
                "type": "action_executed", 
                "data": {
                    "actor_id": str(actor_id),
                    "action_id": action_id,
                    "action_result": {
                        "success": action_result.success,
                        "message": action_result.message,
                        "damage_dealt": action_result.damage_dealt,
                        "healing_applied": action_result.healing_applied,
                        "targets_affected": [str(tid) for tid in action_result.targets_affected],
                        "status_effects_applied": action_result.status_effects_applied
                    },
                    "encounter_state": self._serialize_encounter(encounter)
                }
            }, exclude=websocket)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to execute action: {str(e)}", request_id)
    
    async def _handle_advance_turn(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle advance turn request."""
        try:
            encounter_id = UUID(data["encounter_id"])
            
            encounter = self.combat_service.advance_turn(encounter_id)
            
            await self.send_response(websocket, "turn_advanced", {
                "encounter": self._serialize_encounter(encounter)
            }, request_id)
            
            # Broadcast to all participants
            await self.broadcast_to_encounter(encounter_id, {
                "type": "turn_advanced",
                "data": {
                    "encounter_state": self._serialize_encounter(encounter),
                    "current_turn": encounter.current_turn,
                    "round_number": encounter.round_number,
                    "current_participant": self._serialize_combatant(encounter.get_current_participant()) if encounter.get_current_participant() else None
                }
            }, exclude=websocket)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to advance turn: {str(e)}", request_id)
    
    async def _handle_get_available_actions(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle get available actions request."""
        try:
            combatant_data = data["combatant"]
            combatant = self._deserialize_combatant(combatant_data)
            
            actions = self.combat_service.get_available_actions_for_combatant(combatant)
            
            await self.send_response(websocket, "available_actions", {
                "actions": [self._serialize_action_definition(action) for action in actions]
            }, request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to get available actions: {str(e)}", request_id)
    
    async def _handle_heartbeat(self, websocket: WebSocket, request_id: str):
        """Handle heartbeat/ping request."""
        await self.send_response(websocket, "heartbeat_response", {
            "timestamp": datetime.utcnow().isoformat()
        }, request_id)
    
    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Failed to send message to WebSocket: {e}")
    
    async def send_response(self, websocket: WebSocket, message_type: str, data: Dict[str, Any], request_id: str = None):
        """Send response message."""
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        if request_id:
            message["request_id"] = request_id
        
        await self.send_message(websocket, message)
    
    async def send_error(self, websocket: WebSocket, error_message: str, request_id: str = None):
        """Send error message."""
        message = {
            "type": "error",
            "data": {
                "message": error_message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        if request_id:
            message["request_id"] = request_id
        
        await self.send_message(websocket, message)
    
    async def broadcast_to_encounter(self, encounter_id: UUID, message: Dict[str, Any], exclude: WebSocket = None):
        """Broadcast message to all connections in an encounter."""
        if encounter_id not in self.encounter_connections:
            return
        
        connections = self.encounter_connections[encounter_id].copy()
        if exclude:
            connections.discard(exclude)
        
        for websocket in connections:
            try:
                await self.send_message(websocket, message)
            except Exception as e:
                print(f"Failed to broadcast to WebSocket: {e}")
                # Remove failed connection
                self.encounter_connections[encounter_id].discard(websocket)
    
    def _serialize_encounter(self, encounter: CombatEncounter) -> Dict[str, Any]:
        """Serialize encounter for WebSocket transmission."""
        return {
            "id": str(encounter.id),
            "name": encounter.name,
            "description": encounter.description,
            "status": encounter.status,
            "round_number": encounter.round_number,
            "current_turn": encounter.current_turn,
            "participants": [self._serialize_combatant(p) for p in encounter.participants],
            "initiative_order": [str(p.id) for p in encounter.initiative_order],
            "combat_log": encounter.combat_log[-10:],  # Last 10 log entries
            "started_at": encounter.started_at.isoformat() if encounter.started_at else None,
            "ended_at": encounter.ended_at.isoformat() if encounter.ended_at else None,
            "properties": encounter.properties
        }
    
    def _serialize_combatant(self, combatant: Combatant) -> Dict[str, Any]:
        """Serialize combatant for WebSocket transmission."""
        return {
            "id": str(combatant.id),
            "name": combatant.name,
            "team": combatant.team,
            "combatant_type": combatant.combatant_type,
            "current_hp": combatant.current_hp,
            "max_hp": combatant.max_hp,
            "armor_class": combatant.armor_class,
            "initiative": combatant.initiative,
            "is_active": combatant.is_active,
            "is_conscious": combatant.is_conscious,
            "position": combatant.position,
            "status_effects": [effect.name for effect in combatant.status_effects],
            "action_economy": {
                "has_used_standard_action": combatant.has_used_standard_action,
                "has_used_bonus_action": combatant.has_used_bonus_action,
                "has_used_reaction": combatant.has_used_reaction,
                "remaining_movement": combatant.remaining_movement
            }
        }
    
    def _serialize_action_definition(self, action: ActionDefinition) -> Dict[str, Any]:
        """Serialize action definition for WebSocket transmission."""
        return {
            "id": action.id,
            "name": action.name,
            "description": action.description,
            "action_type": action.action_type.value,
            "target_type": action.target_type.value,
            "category": action.category.value,
            "range_feet": action.range_feet,
            "base_damage": action.base_damage,
            "damage_type": action.damage_type,
            "resource_cost": action.resource_cost,
            "cooldown_rounds": action.cooldown_rounds,
            "tags": list(action.tags)
        }
    
    def _deserialize_combatant(self, data: Dict[str, Any]) -> Combatant:
        """Deserialize combatant from WebSocket data."""
        return Combatant(
            id=UUID(data.get("id", str(UUID(int=0)))),
            name=data["name"],
            team=data.get("team", "neutral"),
            combatant_type=data.get("combatant_type", "character"),
            current_hp=data.get("current_hp", 20),
            max_hp=data.get("max_hp", 20),
            armor_class=data.get("armor_class", 10),
            dex_modifier=data.get("dex_modifier", 0),
            equipped_weapons=data.get("equipped_weapons", []),
            available_spells=data.get("available_spells", []),
            class_features=data.get("class_features", [])
        )
    
    # Implement other handler methods...
    async def _handle_leave_encounter(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle leave encounter request."""
        try:
            encounter_id = self.active_connections[websocket].get("encounter_id")
            
            if not encounter_id:
                await self.send_error(websocket, "Not currently in an encounter", request_id)
                return
            
            # Remove from encounter connections
            if encounter_id in self.encounter_connections:
                self.encounter_connections[encounter_id].discard(websocket)
                if not self.encounter_connections[encounter_id]:
                    del self.encounter_connections[encounter_id]
            
            # Clear encounter from connection info
            self.active_connections[websocket]["encounter_id"] = None
            
            await self.send_response(websocket, "encounter_left", {
                "encounter_id": str(encounter_id),
                "timestamp": datetime.utcnow().isoformat()
            }, request_id)
            
            # Notify other participants
            await self.broadcast_to_encounter(encounter_id, {
                "type": "participant_left",
                "data": {
                    "client_id": self.active_connections[websocket].get("client_id"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }, exclude=websocket)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to leave encounter: {str(e)}", request_id)
    
    async def _handle_set_initiative(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle set initiative request."""
        try:
            encounter_id = UUID(data["encounter_id"])
            combatant_id = UUID(data["combatant_id"])
            initiative_value = data.get("initiative_value")
            
            encounter = self.combat_service.get_encounter_by_id(encounter_id)
            if not encounter:
                await self.send_error(websocket, "Encounter not found", request_id)
                return
            
            # Find the combatant
            combatant = next((p for p in encounter.participants if p.id == combatant_id), None)
            if not combatant:
                await self.send_error(websocket, "Combatant not found", request_id)
                return
            
            # Set initiative (roll if not provided)
            if initiative_value is not None:
                combatant.initiative = initiative_value
            else:
                initiative_value = self.combat_service.roll_initiative_for_combatant(combatant)
            
            # Update encounter with new initiative order
            encounter = self.combat_service.sort_initiative_order(encounter)
            
            await self.send_response(websocket, "initiative_set", {
                "encounter": self._serialize_encounter(encounter),
                "combatant_id": str(combatant_id),
                "initiative": initiative_value
            }, request_id)
            
            # Broadcast to all participants
            await self.broadcast_to_encounter(encounter_id, {
                "type": "initiative_updated",
                "data": {
                    "combatant_id": str(combatant_id),
                    "initiative": initiative_value,
                    "encounter_state": self._serialize_encounter(encounter)
                }
            }, exclude=websocket)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to set initiative: {str(e)}", request_id)
    
    async def _handle_start_combat(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle start combat request."""
        try:
            encounter_id = UUID(data["encounter_id"])
            
            encounter = self.combat_service.start_encounter(encounter_id)
            
            await self.send_response(websocket, "combat_started", {
                "encounter": self._serialize_encounter(encounter)
            }, request_id)
            
            # Broadcast to all participants
            await self.broadcast_to_encounter(encounter_id, {
                "type": "combat_started",
                "data": {
                    "encounter_state": self._serialize_encounter(encounter),
                    "current_participant": self._serialize_combatant(encounter.get_current_participant()) if encounter.get_current_participant() else None,
                    "message": f"Combat has begun! Round {encounter.round_number}"
                }
            }, exclude=websocket)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to start combat: {str(e)}", request_id)
    
    async def _handle_end_combat(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle end combat request."""
        try:
            encounter_id = UUID(data["encounter_id"])
            reason = data.get("reason", "manually_ended")
            
            encounter = self.combat_service.end_encounter(encounter_id, reason)
            
            await self.send_response(websocket, "combat_ended", {
                "encounter": self._serialize_encounter(encounter),
                "reason": reason
            }, request_id)
            
            # Broadcast to all participants
            await self.broadcast_to_encounter(encounter_id, {
                "type": "combat_ended",
                "data": {
                    "encounter_state": self._serialize_encounter(encounter),
                    "reason": reason,
                    "message": f"Combat ended: {reason}",
                    "final_summary": self.combat_service.get_combat_summary(encounter)
                }
            }, exclude=websocket)
            
            # Clean up encounter connections after a delay
            asyncio.create_task(self._cleanup_encounter_connections(encounter_id))
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to end combat: {str(e)}", request_id)
    
    async def _handle_get_encounter_state(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle get encounter state request."""
        try:
            encounter_id = UUID(data["encounter_id"])
            
            encounter = self.combat_service.get_encounter_by_id(encounter_id)
            if not encounter:
                await self.send_error(websocket, "Encounter not found", request_id)
                return
            
            # Get additional state information
            current_participant = encounter.get_current_participant()
            combat_summary = self.combat_service.get_combat_summary(encounter)
            
            await self.send_response(websocket, "encounter_state", {
                "encounter": self._serialize_encounter(encounter),
                "current_participant": self._serialize_combatant(current_participant) if current_participant else None,
                "summary": combat_summary,
                "can_act": current_participant is not None,
                "next_actions_available": len(self.combat_service.get_available_actions_for_combatant(current_participant)) if current_participant else 0
            }, request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to get encounter state: {str(e)}", request_id)
    
    async def _cleanup_encounter_connections(self, encounter_id: UUID, delay_seconds: int = 30):
        """Clean up encounter connections after a delay."""
        await asyncio.sleep(delay_seconds)
        if encounter_id in self.encounter_connections:
            # Notify remaining connections
            await self.broadcast_to_encounter(encounter_id, {
                "type": "encounter_cleanup",
                "data": {
                    "message": "Encounter session ending, please reconnect if needed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            # Remove the encounter
            del self.encounter_connections[encounter_id]


# Global handler instance
combat_websocket_handler = CombatWebSocketHandler()


__all__ = ["CombatWebSocketHandler", "combat_websocket_handler"] 