"""
Equipment WebSocket Handler

Provides real-time WebSocket communication for the equipment system.
Handles live equipment updates, character loadout changes, and equipment operations
for Unity frontend integration. Now with authentication integration.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Set
from uuid import UUID
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import asdict

# Authentication imports
from backend.infrastructure.auth.auth_user.services.auth_service import (
    verify_token, check_user_character_access
)

# Equipment system imports
from backend.infrastructure.persistence.equipment.equipment_dependencies import (
    get_equipment_instance_repository,
    get_equipment_template_repository,
    get_equipment_business_logic_service
)


class EquipmentWebSocketHandler:
    """
    WebSocket handler for real-time equipment communication with authentication.
    
    Manages connections, message routing, and real-time updates
    for the equipment system between Unity client and backend.
    """
    
    def __init__(self):
        # Active WebSocket connections per character
        self.character_connections: Dict[UUID, Set[WebSocket]] = {}
        
        # Active connections registry with authentication info
        self.active_connections: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Global broadcast connections (for system-wide updates)
        self.global_connections: Set[WebSocket] = set()
        
        # Connection to user mapping for authentication
        self.connection_users: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, character_id: str = None, client_id: str = None, token: str = None):
        """Handle new WebSocket connection with authentication."""
        await websocket.accept()
        
        # Authenticate the connection if token provided
        user_data = None
        if token:
            user_data = await self._authenticate_connection(token)
            if not user_data:
                await self.send_error(websocket, "Invalid authentication token")
                await websocket.close()
                return
        
        connection_info = {
            "client_id": client_id,
            "character_id": UUID(character_id) if character_id else None,
            "connected_at": datetime.utcnow(),
            "subscriptions": set(),
            "authenticated": user_data is not None
        }
        
        self.active_connections[websocket] = connection_info
        
        # Store user data if authenticated
        if user_data:
            self.connection_users[websocket] = user_data
        
        # Add to character connections if character_id provided and user has access
        if character_id and user_data:
            char_uuid = UUID(character_id)
            
            # Check if user has access to this character
            has_access = await check_user_character_access(
                str(user_data["id"]), character_id, "read"
            )
            
            if has_access:
                if char_uuid not in self.character_connections:
                    self.character_connections[char_uuid] = set()
                self.character_connections[char_uuid].add(websocket)
                connection_info["character_access"] = True
            else:
                connection_info["character_access"] = False
        
        # Add to global connections for system updates
        self.global_connections.add(websocket)
        
        # Send welcome message
        await self.send_message(websocket, {
            "type": "connection_established",
            "data": {
                "client_id": client_id,
                "character_id": character_id,
                "authenticated": user_data is not None,
                "character_access": connection_info.get("character_access", False),
                "timestamp": datetime.utcnow().isoformat(),
                "available_commands": [
                    "subscribe_character", "unsubscribe_character",
                    "get_character_loadout", "get_character_equipment",
                    "create_equipment", "equip_item", "unequip_item",
                    "update_equipment", "delete_equipment", "transfer_equipment",
                    "get_templates", "get_template", "get_character_stats",
                    "heartbeat"
                ]
            }
        })
    
    async def _authenticate_connection(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate WebSocket connection using JWT token."""
        try:
            # Verify the token using the auth service
            payload = verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Return basic user data for WebSocket context
            # In a real implementation, you'd fetch full user data from database
            return {
                "id": user_id,
                "authenticated_at": datetime.utcnow().isoformat(),
                "permissions": payload.get("permissions", []),
                "roles": payload.get("roles", [])
            }
        except Exception:
            return None
    
    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        if websocket in self.active_connections:
            connection_info = self.active_connections[websocket]
            character_id = connection_info.get("character_id")
            
            # Remove from character connections
            if character_id and character_id in self.character_connections:
                self.character_connections[character_id].discard(websocket)
                if not self.character_connections[character_id]:
                    del self.character_connections[character_id]
            
            # Remove from global connections
            self.global_connections.discard(websocket)
            
            # Remove from active connections
            del self.active_connections[websocket]
            
            # Remove user data
            if websocket in self.connection_users:
                del self.connection_users[websocket]
    
    async def _check_authentication(self, websocket: WebSocket) -> bool:
        """Check if WebSocket connection is authenticated."""
        return websocket in self.connection_users
    
    async def _check_character_access(self, websocket: WebSocket, character_id: str, permission: str = "read") -> bool:
        """Check if authenticated user has access to character."""
        if not await self._check_authentication(websocket):
            return False
        
        user_data = self.connection_users[websocket]
        return await check_user_character_access(str(user_data["id"]), character_id, permission)
    
    async def handle_message(self, websocket: WebSocket, data: Dict[str, Any]):
        """Route incoming WebSocket message to appropriate handler with authentication."""
        try:
            message_type = data.get("type")
            message_data = data.get("data", {})
            request_id = data.get("request_id")
            
            # Check authentication for protected operations
            protected_operations = [
                "create_equipment", "update_equipment", "delete_equipment",
                "equip_item", "unequip_item", "transfer_equipment"
            ]
            
            if message_type in protected_operations and not await self._check_authentication(websocket):
                await self.send_error(websocket, "Authentication required for this operation", request_id)
                return
            
            if message_type == "subscribe_character":
                await self._handle_subscribe_character(websocket, message_data, request_id)
            elif message_type == "unsubscribe_character":
                await self._handle_unsubscribe_character(websocket, message_data, request_id)
            elif message_type == "get_character_loadout":
                await self._handle_get_character_loadout(websocket, message_data, request_id)
            elif message_type == "get_character_equipment":
                await self._handle_get_character_equipment(websocket, message_data, request_id)
            elif message_type == "create_equipment":
                await self._handle_create_equipment(websocket, message_data, request_id)
            elif message_type == "equip_item":
                await self._handle_equip_item(websocket, message_data, request_id)
            elif message_type == "unequip_item":
                await self._handle_unequip_item(websocket, message_data, request_id)
            elif message_type == "update_equipment":
                await self._handle_update_equipment(websocket, message_data, request_id)
            elif message_type == "delete_equipment":
                await self._handle_delete_equipment(websocket, message_data, request_id)
            elif message_type == "transfer_equipment":
                await self._handle_transfer_equipment(websocket, message_data, request_id)
            elif message_type == "get_templates":
                await self._handle_get_templates(websocket, message_data, request_id)
            elif message_type == "get_template":
                await self._handle_get_template(websocket, message_data, request_id)
            elif message_type == "get_character_stats":
                await self._handle_get_character_stats(websocket, message_data, request_id)
            elif message_type == "heartbeat":
                await self._handle_heartbeat(websocket, request_id)
            else:
                await self.send_error(websocket, f"Unknown message type: {message_type}", request_id)
                
        except Exception as e:
            await self.send_error(websocket, str(e), data.get("request_id"))
    
    async def _handle_subscribe_character(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Subscribe to character equipment updates with authentication check."""
        try:
            character_id_str = data["character_id"]
            character_id = UUID(character_id_str)
            
            # Check if user has access to this character
            if not await self._check_character_access(websocket, character_id_str, "read"):
                await self.send_error(websocket, "You don't have permission to subscribe to this character", request_id)
                return
            
            # Add to character connections
            if character_id not in self.character_connections:
                self.character_connections[character_id] = set()
            self.character_connections[character_id].add(websocket)
            
            # Update connection info
            self.active_connections[websocket]["subscriptions"].add(character_id)
            
            await self.send_response(websocket, "character_subscribed", {
                "character_id": str(character_id)
            }, request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to subscribe to character: {str(e)}", request_id)
    
    async def _handle_unsubscribe_character(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Unsubscribe from character equipment updates."""
        try:
            character_id = UUID(data["character_id"])
            
            # Remove from character connections
            if character_id in self.character_connections:
                self.character_connections[character_id].discard(websocket)
                if not self.character_connections[character_id]:
                    del self.character_connections[character_id]
            
            # Update connection info
            self.active_connections[websocket]["subscriptions"].discard(character_id)
            
            await self.send_response(websocket, "character_unsubscribed", {
                "character_id": str(character_id)
            }, request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to unsubscribe from character: {str(e)}", request_id)
    
    async def _handle_get_character_loadout(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Get character equipment loadout with authentication."""
        try:
            character_id_str = data["character_id"]
            character_id = UUID(character_id_str)
            
            # Check if user has access to this character
            if not await self._check_character_access(websocket, character_id_str, "read"):
                await self.send_error(websocket, "You don't have permission to view this character's loadout", request_id)
                return
            
            instance_repo = get_equipment_instance_repository()
            loadout = instance_repo.get_character_equipment_loadout(character_id)
            
            await self.send_response(websocket, "character_loadout", {
                "character_id": str(character_id),
                "loadout": self._serialize_loadout(loadout)
            }, request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to get character loadout: {str(e)}", request_id)
    
    async def _handle_get_character_equipment(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Get character equipment list with authentication."""
        try:
            character_id_str = data["character_id"]
            character_id = UUID(character_id_str)
            equipped_only = data.get("equipped_only", False)
            
            # Check if user has access to this character
            if not await self._check_character_access(websocket, character_id_str, "read"):
                await self.send_error(websocket, "You don't have permission to view this character's equipment", request_id)
                return
            
            instance_repo = get_equipment_instance_repository()
            equipment_list = instance_repo.get_character_equipment(character_id, equipped_only)
            
            await self.send_response(websocket, "character_equipment", {
                "character_id": str(character_id),
                "equipment": [self._serialize_equipment(eq) for eq in equipment_list],
                "equipped_only": equipped_only
            }, request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to get character equipment: {str(e)}", request_id)
    
    async def _handle_create_equipment(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Create new equipment instance with authentication."""
        try:
            character_id_str = data["character_id"]
            character_id = UUID(character_id_str)
            template_id = data["template_id"]
            quality_tier = data.get("quality_tier", "basic")
            rarity_tier = data.get("rarity_tier", "common")
            
            # Check if user has write access to this character
            if not await self._check_character_access(websocket, character_id_str, "write"):
                await self.send_error(websocket, "You don't have permission to create equipment for this character", request_id)
                return
            
            # Get services
            instance_repo = get_equipment_instance_repository()
            template_repo = get_equipment_template_repository()
            business_logic = get_equipment_business_logic_service()
            
            # Validate template exists
            template = template_repo.get_template(template_id)
            if not template:
                await self.send_error(websocket, f"Equipment template '{template_id}' not found", request_id)
                return
            
            # Validate quality and rarity tiers
            quality_tier_data = template_repo.get_quality_tier(quality_tier)
            rarity_tier_data = template_repo.get_rarity_tier(rarity_tier)
            
            if not quality_tier_data or not rarity_tier_data:
                await self.send_error(websocket, "Invalid quality or rarity tier", request_id)
                return
            
            # Create equipment using business logic
            equipment_data = business_logic.create_equipment_instance(
                character_id=character_id,
                template=template,
                quality_tier=quality_tier_data,
                rarity_tier=rarity_tier_data
            )
            
            # Save to database
            saved_equipment = instance_repo.create_equipment(equipment_data)
            
            await self.send_response(websocket, "equipment_created", {
                "equipment": self._serialize_equipment(saved_equipment)
            }, request_id)
            
            # Broadcast to character subscribers
            await self.broadcast_to_character(character_id, {
                "type": "equipment_added",
                "data": {
                    "character_id": str(character_id),
                    "equipment": self._serialize_equipment(saved_equipment)
                }
            }, exclude=websocket)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to create equipment: {str(e)}", request_id)
    
    async def _handle_equip_item(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Equip item to character slot with authentication."""
        try:
            character_id_str = data["character_id"]
            character_id = UUID(character_id_str)
            equipment_id_str = data["equipment_id"]
            equipment_id = UUID(equipment_id_str)
            slot = data["slot"]
            
            # Check if user has access to this character
            if not await self._check_character_access(websocket, character_id_str, "write"):
                await self.send_error(websocket, "You don't have permission to equip this item", request_id)
                return
            
            instance_repo = get_equipment_instance_repository()
            equipment = instance_repo.get_equipment_by_id(equipment_id)
            
            if not equipment:
                await self.send_error(websocket, "Equipment not found", request_id)
                return
            
            result = instance_repo.equip_item_to_character(character_id, equipment_id, slot)
            
            if result['success']:
                await self.send_response(websocket, "item_equipped", {
                    "character_id": str(character_id),
                    "equipment_id": str(equipment_id),
                    "slot": slot,
                    "message": result['message']
                }, request_id)
                
                # Broadcast to character subscribers
                await self.broadcast_to_character(character_id, {
                    "type": "equipment_equipped",
                    "data": {
                        "character_id": str(character_id),
                        "equipment_id": str(equipment_id),
                        "slot": slot
                    }
                }, exclude=websocket)
            else:
                await self.send_error(websocket, result['error'], request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to equip item: {str(e)}", request_id)
    
    async def _handle_unequip_item(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Unequip item from character with authentication."""
        try:
            character_id_str = data["character_id"]
            character_id = UUID(character_id_str)
            equipment_id_str = data["equipment_id"]
            equipment_id = UUID(equipment_id_str)
            
            # Check if user has access to this character
            if not await self._check_character_access(websocket, character_id_str, "write"):
                await self.send_error(websocket, "You don't have permission to unequip this item", request_id)
                return
            
            instance_repo = get_equipment_instance_repository()
            equipment = instance_repo.get_equipment_by_id(equipment_id)
            
            if not equipment:
                await self.send_error(websocket, "Equipment not found", request_id)
                return
            
            result = instance_repo.unequip_item_from_character(character_id, equipment_id)
            
            if result['success']:
                await self.send_response(websocket, "item_unequipped", {
                    "character_id": str(character_id),
                    "equipment_id": str(equipment_id),
                    "message": result['message']
                }, request_id)
                
                # Broadcast to character subscribers
                await self.broadcast_to_character(character_id, {
                    "type": "equipment_unequipped",
                    "data": {
                        "character_id": str(character_id),
                        "equipment_id": str(equipment_id)
                    }
                }, exclude=websocket)
            else:
                await self.send_error(websocket, result['error'], request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to unequip item: {str(e)}", request_id)
    
    async def _handle_update_equipment(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Update equipment instance with authentication."""
        try:
            character_id_str = data["character_id"]
            character_id = UUID(character_id_str)
            equipment_id_str = data["equipment_id"]
            equipment_id = UUID(equipment_id_str)
            
            # Check if user has access to this character
            if not await self._check_character_access(websocket, character_id_str, "write"):
                await self.send_error(websocket, "You don't have permission to update this equipment", request_id)
                return
            
            instance_repo = get_equipment_instance_repository()
            equipment = instance_repo.get_equipment_by_id(equipment_id)
            
            if not equipment:
                await self.send_error(websocket, "Equipment not found", request_id)
                return
            
            # Update fields
            if "durability" in data:
                equipment.current_durability = data["durability"]
            if "custom_name" in data:
                equipment.custom_name = data["custom_name"]
            
            success = instance_repo.update_equipment(equipment)
            
            if success:
                updated_equipment = instance_repo.get_equipment_by_id(equipment_id)
                
                await self.send_response(websocket, "equipment_updated", {
                    "equipment": self._serialize_equipment(updated_equipment)
                }, request_id)
                
                # Broadcast to character subscribers
                await self.broadcast_to_character(character_id, {
                    "type": "equipment_modified",
                    "data": {
                        "character_id": str(character_id),
                        "equipment": self._serialize_equipment(updated_equipment)
                    }
                }, exclude=websocket)
            else:
                await self.send_error(websocket, "Failed to update equipment", request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to update equipment: {str(e)}", request_id)
    
    async def _handle_delete_equipment(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Delete equipment instance with authentication."""
        try:
            character_id_str = data["character_id"]
            character_id = UUID(character_id_str)
            equipment_id_str = data["equipment_id"]
            equipment_id = UUID(equipment_id_str)
            
            # Check if user has access to this character
            if not await self._check_character_access(websocket, character_id_str, "write"):
                await self.send_error(websocket, "You don't have permission to delete this equipment", request_id)
                return
            
            instance_repo = get_equipment_instance_repository()
            equipment = instance_repo.get_equipment_by_id(equipment_id)
            
            if not equipment:
                await self.send_error(websocket, "Equipment not found", request_id)
                return
            
            success = instance_repo.remove_equipment(equipment_id)
            
            if success:
                await self.send_response(websocket, "equipment_deleted", {
                    "equipment_id": str(equipment_id),
                    "character_id": str(character_id)
                }, request_id)
                
                # Broadcast to character subscribers
                await self.broadcast_to_character(character_id, {
                    "type": "equipment_removed",
                    "data": {
                        "character_id": str(character_id),
                        "equipment_id": str(equipment_id)
                    }
                }, exclude=websocket)
            else:
                await self.send_error(websocket, "Failed to delete equipment", request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to delete equipment: {str(e)}", request_id)
    
    async def _handle_transfer_equipment(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Transfer equipment to different character with authentication."""
        try:
            character_id_str = data["character_id"]
            character_id = UUID(character_id_str)
            new_owner_id_str = data["new_owner_id"]
            new_owner_id = UUID(new_owner_id_str)
            
            # Check if user has access to this character
            if not await self._check_character_access(websocket, character_id_str, "write"):
                await self.send_error(websocket, "You don't have permission to transfer this equipment", request_id)
                return
            
            instance_repo = get_equipment_instance_repository()
            equipment = instance_repo.get_equipment_by_id(character_id)
            
            if not equipment:
                await self.send_error(websocket, "Equipment not found", request_id)
                return
            
            old_owner_id = equipment.character_id
            
            success = instance_repo.transfer_equipment(character_id, new_owner_id)
            
            if success:
                await self.send_response(websocket, "equipment_transferred", {
                    "equipment_id": str(character_id),
                    "old_owner_id": str(old_owner_id),
                    "new_owner_id": str(new_owner_id)
                }, request_id)
                
                # Broadcast to both characters' subscribers
                await self.broadcast_to_character(old_owner_id, {
                    "type": "equipment_lost",
                    "data": {
                        "character_id": str(old_owner_id),
                        "equipment_id": str(character_id),
                        "transferred_to": str(new_owner_id)
                    }
                })
                
                await self.broadcast_to_character(new_owner_id, {
                    "type": "equipment_gained",
                    "data": {
                        "character_id": str(new_owner_id),
                        "equipment_id": str(character_id),
                        "transferred_from": str(old_owner_id)
                    }
                })
            else:
                await self.send_error(websocket, "Failed to transfer equipment", request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to transfer equipment: {str(e)}", request_id)
    
    async def _handle_get_templates(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Get equipment templates with authentication."""
        try:
            item_type = data.get("item_type")
            quality_tier = data.get("quality_tier")
            
            # Check if user has access to this operation
            if not await self._check_authentication(websocket):
                await self.send_error(websocket, "Authentication required to access templates", request_id)
                return
            
            template_repo = get_equipment_template_repository()
            templates = template_repo.list_templates(item_type, quality_tier)
            
            await self.send_response(websocket, "equipment_templates", {
                "templates": [self._serialize_template(template) for template in templates],
                "filters": {"item_type": item_type, "quality_tier": quality_tier}
            }, request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to get templates: {str(e)}", request_id)
    
    async def _handle_get_template(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Get specific equipment template with authentication."""
        try:
            template_id = data["template_id"]
            
            # Check if user has access to this operation
            if not await self._check_authentication(websocket):
                await self.send_error(websocket, "Authentication required to access this template", request_id)
                return
            
            template_repo = get_equipment_template_repository()
            template = template_repo.get_template(template_id)
            
            if template:
                await self.send_response(websocket, "equipment_template", {
                    "template": self._serialize_template(template)
                }, request_id)
            else:
                await self.send_error(websocket, "Template not found", request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to get template: {str(e)}", request_id)
    
    async def _handle_get_character_stats(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Get character combat stats from equipment with authentication."""
        try:
            character_id_str = data["character_id"]
            character_id = UUID(character_id_str)
            
            # Check if user has access to this operation
            if not await self._check_authentication(websocket):
                await self.send_error(websocket, "Authentication required to access character stats", request_id)
                return
            
            instance_repo = get_equipment_instance_repository()
            character_equipment_service = get_equipment_business_logic_service()
            
            stats = character_equipment_service.get_character_combat_stats(character_id)
            
            await self.send_response(websocket, "character_stats", {
                "character_id": str(character_id),
                "combat_stats": stats
            }, request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to get character stats: {str(e)}", request_id)
    
    async def _handle_heartbeat(self, websocket: WebSocket, request_id: str):
        """Handle heartbeat message with authentication."""
        await self.send_response(websocket, "heartbeat", {
            "timestamp": datetime.utcnow().isoformat()
        }, request_id)
    
    # Real-time notification methods
    async def notify_equipment_created(self, character_id: UUID, equipment_data: Dict[str, Any]):
        """Notify all character subscribers about new equipment."""
        await self.broadcast_to_character(character_id, {
            "type": "equipment_created",
            "data": {
                "character_id": str(character_id),
                "equipment": equipment_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    async def notify_equipment_updated(self, character_id: UUID, equipment_data: Dict[str, Any]):
        """Notify all character subscribers about equipment updates."""
        await self.broadcast_to_character(character_id, {
            "type": "equipment_updated",
            "data": {
                "character_id": str(character_id),
                "equipment": equipment_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    async def notify_equipment_equipped(self, character_id: UUID, equipment_id: UUID, slot: str):
        """Notify all character subscribers about equipment being equipped."""
        await self.broadcast_to_character(character_id, {
            "type": "equipment_equipped",
            "data": {
                "character_id": str(character_id),
                "equipment_id": str(equipment_id),
                "slot": slot,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    async def notify_equipment_unequipped(self, character_id: UUID, equipment_id: UUID, slot: str):
        """Notify all character subscribers about equipment being unequipped."""
        await self.broadcast_to_character(character_id, {
            "type": "equipment_unequipped",
            "data": {
                "character_id": str(character_id),
                "equipment_id": str(equipment_id),
                "slot": slot,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    async def notify_equipment_deleted(self, character_id: UUID, equipment_id: UUID):
        """Notify all character subscribers about equipment deletion."""
        await self.broadcast_to_character(character_id, {
            "type": "equipment_deleted",
            "data": {
                "character_id": str(character_id),
                "equipment_id": str(equipment_id),
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    async def notify_durability_changed(self, character_id: UUID, equipment_id: UUID, old_durability: int, new_durability: int):
        """Notify all character subscribers about durability changes."""
        await self.broadcast_to_character(character_id, {
            "type": "durability_changed",
            "data": {
                "character_id": str(character_id),
                "equipment_id": str(equipment_id),
                "old_durability": old_durability,
                "new_durability": new_durability,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    # Serialization helpers
    def _serialize_equipment(self, equipment) -> Dict[str, Any]:
        """Serialize equipment instance for JSON response."""
        return {
            "id": str(equipment.id),
            "character_id": str(equipment.character_id),
            "template_id": equipment.template_id,
            "slot": equipment.slot.value if hasattr(equipment.slot, 'value') else str(equipment.slot),
            "current_durability": equipment.current_durability,
            "max_durability": equipment.max_durability,
            "usage_count": equipment.usage_count,
            "quality_tier": equipment.quality_tier,
            "rarity_tier": equipment.rarity_tier,
            "is_equipped": equipment.is_equipped,
            "equipment_set": equipment.equipment_set,
            "enchantments": [
                {
                    "type": ench.enchantment_type,
                    "magnitude": ench.magnitude,
                    "target_attribute": ench.target_attribute,
                    "is_active": ench.is_active
                } for ench in equipment.enchantments
            ],
            "effective_stats": equipment.effective_stats,
            "created_at": equipment.created_at.isoformat(),
            "updated_at": equipment.updated_at.isoformat()
        }
    
    def _serialize_template(self, template) -> Dict[str, Any]:
        """Serialize equipment template for JSON response."""
        return {
            "id": template.id,
            "name": template.name,
            "item_type": template.item_type,
            "base_stats": template.base_stats,
            "equipment_slots": template.equipment_slots,
            "base_value": template.base_value
        }
    
    def _serialize_loadout(self, loadout) -> Dict[str, Any]:
        """Serialize character equipment loadout for JSON response."""
        return {
            "character_id": str(loadout.character_id),
            "equipped_items": [self._serialize_equipment(eq) for eq in loadout.equipped_items],
            "inventory_items": [self._serialize_equipment(eq) for eq in loadout.inventory_items],
            "equipment_slots": {slot: str(item_id) if item_id else None 
                              for slot, slot_info in loadout.equipment_slots.items() 
                              for item_id in [slot_info.equipped_item_id]},
            "total_stat_bonuses": loadout.total_stat_bonuses,
            "equipped_count": loadout.get_equipped_count(),
            "total_items": loadout.get_total_items()
        }
    
    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to WebSocket."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Failed to send message: {e}")
    
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
                "error": error_message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        if request_id:
            message["request_id"] = request_id
        
        await self.send_message(websocket, message)
    
    async def broadcast_to_character(self, character_id: UUID, message: Dict[str, Any], exclude: WebSocket = None):
        """Broadcast message to all connections subscribed to a character."""
        if character_id not in self.character_connections:
            return
        
        connections = self.character_connections[character_id].copy()
        if exclude:
            connections.discard(exclude)
        
        for websocket in connections:
            try:
                await self.send_message(websocket, message)
            except Exception as e:
                print(f"Failed to broadcast to character {character_id}: {e}")
                # Remove failed connection
                self.character_connections[character_id].discard(websocket)
    
    async def broadcast_global(self, message: Dict[str, Any], exclude: WebSocket = None):
        """Broadcast message to all connected clients."""
        connections = self.global_connections.copy()
        if exclude:
            connections.discard(exclude)
        
        for websocket in connections:
            try:
                await self.send_message(websocket, message)
            except Exception as e:
                print(f"Failed to global broadcast: {e}")
                # Remove failed connection
                self.global_connections.discard(websocket)


# Global handler instance
equipment_websocket_handler = EquipmentWebSocketHandler()


# Integration functions for calling from routers
async def notify_equipment_change(character_id: UUID, change_type: str, equipment_data: Dict[str, Any], **kwargs):
    """Notify WebSocket subscribers about equipment changes."""
    if change_type == "created":
        await equipment_websocket_handler.notify_equipment_created(character_id, equipment_data)
    elif change_type == "updated":
        await equipment_websocket_handler.notify_equipment_updated(character_id, equipment_data)
    elif change_type == "equipped":
        await equipment_websocket_handler.notify_equipment_equipped(
            character_id, kwargs.get("equipment_id"), kwargs.get("slot")
        )
    elif change_type == "unequipped":
        await equipment_websocket_handler.notify_equipment_unequipped(
            character_id, kwargs.get("equipment_id"), kwargs.get("slot")
        )
    elif change_type == "deleted":
        await equipment_websocket_handler.notify_equipment_deleted(
            character_id, kwargs.get("equipment_id")
        )
    elif change_type == "durability_changed":
        await equipment_websocket_handler.notify_durability_changed(
            character_id, kwargs.get("equipment_id"), 
            kwargs.get("old_durability"), kwargs.get("new_durability")
        ) 