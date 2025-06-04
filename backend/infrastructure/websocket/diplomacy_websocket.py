"""
Diplomacy WebSocket Handler

This module provides WebSocket communication for the diplomacy system,
handling real-time diplomatic events between Unity client and backend.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Set
from uuid import UUID
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import asdict

# Business imports  
from backend.systems.diplomacy.services.core_services import DiplomacyService
from backend.systems.diplomacy.models.core_models import Treaty, Negotiation, DiplomaticEvent

# Infrastructure imports
from backend.infrastructure.events import get_event_bus
from backend.infrastructure.llm.services.diplomatic_narrative_service import create_diplomatic_narrative_service


class DiplomacyWebSocketHandler:
    """
    WebSocket handler for real-time diplomatic communication.
    
    Manages connections, message routing, and real-time updates
    for the diplomacy system between Unity client and backend.
    """
    
    def __init__(self):
        # Active WebSocket connections per faction
        self.faction_connections: Dict[UUID, Set[WebSocket]] = {}
        
        # Active connections registry
        self.active_connections: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Negotiation-specific connections
        self.negotiation_connections: Dict[UUID, Set[WebSocket]] = {}
        
        # Services with dependency injection
        self.diplomacy_service = DiplomacyService()
        self.event_bus = get_event_bus()
        self.narrative_service = create_diplomatic_narrative_service()
        
        # Subscribe to diplomatic events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to diplomatic events for real-time notifications."""
        self.event_bus.subscribe("treaty_signed", self._handle_treaty_signed)
        self.event_bus.subscribe("negotiation_started", self._handle_negotiation_started)
        self.event_bus.subscribe("alliance_formed", self._handle_alliance_formed)
        self.event_bus.subscribe("conflict_declared", self._handle_conflict_declared)
        self.event_bus.subscribe("diplomatic_incident", self._handle_diplomatic_incident)
        self.event_bus.subscribe("sanction_imposed", self._handle_sanction_imposed)
        self.event_bus.subscribe("ultimatum_issued", self._handle_ultimatum_issued)
    
    async def connect(self, websocket: WebSocket, faction_id: UUID = None, connection_type: str = "general"):
        """Handle new WebSocket connection."""
        await websocket.accept()
        
        self.active_connections[websocket] = {
            "faction_id": faction_id,
            "connection_type": connection_type,
            "connected_at": datetime.utcnow(),
            "negotiation_id": None,
            "subscribed_events": []
        }
        
        # Add to faction connections if faction_id provided
        if faction_id:
            if faction_id not in self.faction_connections:
                self.faction_connections[faction_id] = set()
            self.faction_connections[faction_id].add(websocket)
        
        # Send welcome message
        await self.send_message(websocket, {
            "type": "diplomacy_connection_established",
            "data": {
                "faction_id": str(faction_id) if faction_id else None,
                "connection_type": connection_type,
                "timestamp": datetime.utcnow().isoformat(),
                "available_commands": [
                    "start_negotiation", "join_negotiation", "make_offer", "accept_offer",
                    "reject_offer", "create_treaty", "sign_treaty", "declare_war",
                    "propose_alliance", "issue_ultimatum", "impose_sanction",
                    "get_faction_relationships", "get_active_negotiations",
                    "subscribe_to_faction_events", "get_diplomatic_status"
                ]
            }
        })
    
    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        if websocket in self.active_connections:
            connection_info = self.active_connections[websocket]
            faction_id = connection_info.get("faction_id")
            negotiation_id = connection_info.get("negotiation_id")
            
            # Remove from faction connections
            if faction_id and faction_id in self.faction_connections:
                self.faction_connections[faction_id].discard(websocket)
                if not self.faction_connections[faction_id]:
                    del self.faction_connections[faction_id]
            
            # Remove from negotiation connections
            if negotiation_id and negotiation_id in self.negotiation_connections:
                self.negotiation_connections[negotiation_id].discard(websocket)
                if not self.negotiation_connections[negotiation_id]:
                    del self.negotiation_connections[negotiation_id]
            
            # Remove from active connections
            del self.active_connections[websocket]
    
    async def handle_message(self, websocket: WebSocket, data: Dict[str, Any]):
        """Route incoming WebSocket message to appropriate handler."""
        try:
            message_type = data.get("type")
            message_data = data.get("data", {})
            request_id = data.get("request_id")
            
            if message_type == "start_negotiation":
                await self._handle_start_negotiation(websocket, message_data, request_id)
            elif message_type == "join_negotiation":
                await self._handle_join_negotiation(websocket, message_data, request_id)
            elif message_type == "make_offer":
                await self._handle_make_offer(websocket, message_data, request_id)
            elif message_type == "accept_offer":
                await self._handle_accept_offer(websocket, message_data, request_id)
            elif message_type == "reject_offer":
                await self._handle_reject_offer(websocket, message_data, request_id)
            elif message_type == "create_treaty":
                await self._handle_create_treaty(websocket, message_data, request_id)
            elif message_type == "declare_war":
                await self._handle_declare_war(websocket, message_data, request_id)
            elif message_type == "propose_alliance":
                await self._handle_propose_alliance(websocket, message_data, request_id)
            elif message_type == "issue_ultimatum":
                await self._handle_issue_ultimatum(websocket, message_data, request_id)
            elif message_type == "impose_sanction":
                await self._handle_impose_sanction(websocket, message_data, request_id)
            elif message_type == "get_faction_relationships":
                await self._handle_get_faction_relationships(websocket, message_data, request_id)
            elif message_type == "get_active_negotiations":
                await self._handle_get_active_negotiations(websocket, message_data, request_id)
            elif message_type == "subscribe_to_faction_events":
                await self._handle_subscribe_to_faction_events(websocket, message_data, request_id)
            elif message_type == "get_diplomatic_status":
                await self._handle_get_diplomatic_status(websocket, message_data, request_id)
            elif message_type == "heartbeat":
                await self._handle_heartbeat(websocket, request_id)
            else:
                await self.send_error(websocket, f"Unknown message type: {message_type}", request_id)
                
        except Exception as e:
            await self.send_error(websocket, str(e), data.get("request_id"))
    
    async def _handle_start_negotiation(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle start negotiation request."""
        try:
            parties = [UUID(id_str) for id_str in data["parties"]]
            initiator_id = UUID(data["initiator_id"])
            treaty_type = data.get("treaty_type")
            initial_offer = data.get("initial_offer")
            metadata = data.get("metadata", {})
            
            negotiation = self.diplomacy_service.start_negotiation(
                parties=parties,
                initiator_id=initiator_id,
                treaty_type=treaty_type,
                initial_offer=initial_offer,
                metadata=metadata
            )
            
            # Add to negotiation connections
            negotiation_id = negotiation.id
            if negotiation_id not in self.negotiation_connections:
                self.negotiation_connections[negotiation_id] = set()
            
            self.negotiation_connections[negotiation_id].add(websocket)
            self.active_connections[websocket]["negotiation_id"] = negotiation_id
            
            await self.send_response(websocket, "negotiation_started", {
                "negotiation": self._serialize_negotiation(negotiation)
            }, request_id)
            
            # Notify all involved factions
            for faction_id in parties:
                await self.broadcast_to_faction(faction_id, {
                    "type": "negotiation_invitation",
                    "data": {
                        "negotiation": self._serialize_negotiation(negotiation),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to start negotiation: {str(e)}", request_id)
    
    async def _handle_make_offer(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle make offer request."""
        try:
            negotiation_id = UUID(data["negotiation_id"])
            faction_id = UUID(data["faction_id"])
            terms = data["terms"]
            counter_to = UUID(data["counter_to"]) if data.get("counter_to") else None
            
            result = self.diplomacy_service.make_offer(
                negotiation_id=negotiation_id,
                faction_id=faction_id,
                terms=terms,
                counter_to=counter_to
            )
            
            if not result:
                await self.send_error(websocket, "Could not make offer", request_id)
                return
            
            negotiation, offer = result
            
            await self.send_response(websocket, "offer_made", {
                "negotiation": self._serialize_negotiation(negotiation),
                "offer": self._serialize_offer(offer)
            }, request_id)
            
            # Broadcast to all negotiation participants
            await self.broadcast_to_negotiation(negotiation_id, {
                "type": "new_offer",
                "data": {
                    "negotiation": self._serialize_negotiation(negotiation),
                    "offer": self._serialize_offer(offer),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }, exclude=websocket)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to make offer: {str(e)}", request_id)
    
    async def _handle_create_treaty(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle create treaty request."""
        try:
            name = data["name"]
            treaty_type = data["type"]
            parties = [UUID(id_str) for id_str in data["parties"]]
            terms = data["terms"]
            end_date = data.get("end_date")
            is_public = data.get("is_public", True)
            
            treaty = self.diplomacy_service.create_treaty(
                name=name,
                treaty_type=treaty_type,
                parties=parties,
                terms=terms,
                end_date=end_date,
                is_public=is_public
            )
            
            await self.send_response(websocket, "treaty_created", {
                "treaty": self._serialize_treaty(treaty)
            }, request_id)
            
            # Generate AI narrative for treaty
            faction_personalities = await self._get_faction_personalities(parties)
            narrative = await self.narrative_service.generate_treaty_announcement(
                treaty_data={
                    "id": str(treaty.id),
                    "type": treaty_type,
                    "parties": [str(p) for p in parties],
                    "terms": terms
                },
                faction_personalities=faction_personalities
            )
            
            # Broadcast treaty creation with narrative
            for faction_id in parties:
                await self.broadcast_to_faction(faction_id, {
                    "type": "treaty_created",
                    "data": {
                        "treaty": self._serialize_treaty(treaty),
                        "narrative": narrative,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to create treaty: {str(e)}", request_id)
    
    async def _handle_declare_war(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle declare war request."""
        try:
            aggressor_id = UUID(data["aggressor_id"])
            target_id = UUID(data["target_id"])
            justification = data.get("justification", "")
            
            # Update diplomatic status to war
            # This would typically call a dedicated war service
            # For now, we'll use the tension service to set status
            
            # Publish war declaration event
            self.event_bus.publish("conflict_declared", {
                "aggressor_id": str(aggressor_id),
                "target_id": str(target_id),
                "justification": justification,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await self.send_response(websocket, "war_declared", {
                "aggressor_id": str(aggressor_id),
                "target_id": str(target_id),
                "justification": justification
            }, request_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to declare war: {str(e)}", request_id)
    
    async def _handle_treaty_signed(self, event_data: Dict[str, Any]):
        """Handle treaty signed event."""
        treaty_id = UUID(event_data["treaty_id"])
        parties = [UUID(id_str) for id_str in event_data["parties"]]
        
        # Broadcast to all involved factions
        for faction_id in parties:
            await self.broadcast_to_faction(faction_id, {
                "type": "treaty_signed",
                "data": event_data
            })
    
    async def _handle_alliance_formed(self, event_data: Dict[str, Any]):
        """Handle alliance formed event."""
        members = [UUID(id_str) for id_str in event_data["members"]]
        
        # Generate AI narrative for alliance
        faction_personalities = await self._get_faction_personalities(members)
        narrative = await self.narrative_service.generate_alliance_story(
            alliance_data=event_data,
            faction_personalities=faction_personalities
        )
        
        # Broadcast to all alliance members
        for faction_id in members:
            await self.broadcast_to_faction(faction_id, {
                "type": "alliance_formed",
                "data": {
                    **event_data,
                    "narrative": narrative
                }
            })
    
    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            # Connection may be closed
            pass
    
    async def send_response(self, websocket: WebSocket, message_type: str, data: Dict[str, Any], request_id: str = None):
        """Send response message to WebSocket connection."""
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        if request_id:
            message["request_id"] = request_id
        
        await self.send_message(websocket, message)
    
    async def send_error(self, websocket: WebSocket, error_message: str, request_id: str = None):
        """Send error message to WebSocket connection."""
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
    
    async def broadcast_to_faction(self, faction_id: UUID, message: Dict[str, Any]):
        """Broadcast message to all connections for a faction."""
        if faction_id in self.faction_connections:
            connections = self.faction_connections[faction_id].copy()
            for websocket in connections:
                await self.send_message(websocket, message)
    
    async def broadcast_to_negotiation(self, negotiation_id: UUID, message: Dict[str, Any], exclude: WebSocket = None):
        """Broadcast message to all connections for a negotiation."""
        if negotiation_id in self.negotiation_connections:
            connections = self.negotiation_connections[negotiation_id].copy()
            for websocket in connections:
                if websocket != exclude:
                    await self.send_message(websocket, message)
    
    def _serialize_treaty(self, treaty: Treaty) -> Dict[str, Any]:
        """Serialize treaty for WebSocket transmission."""
        return {
            "id": str(treaty.id),
            "name": treaty.name,
            "type": treaty.type.value if hasattr(treaty.type, 'value') else str(treaty.type),
            "parties": [str(p) for p in treaty.parties],
            "terms": treaty.terms,
            "start_date": treaty.start_date.isoformat() if treaty.start_date else None,
            "end_date": treaty.end_date.isoformat() if treaty.end_date else None,
            "status": treaty.status.value if hasattr(treaty.status, 'value') else str(treaty.status),
            "is_public": treaty.is_public
        }
    
    def _serialize_negotiation(self, negotiation: Negotiation) -> Dict[str, Any]:
        """Serialize negotiation for WebSocket transmission."""
        return {
            "id": str(negotiation.id),
            "parties": [str(p) for p in negotiation.parties],
            "initiator_id": str(negotiation.initiator_id),
            "treaty_type": negotiation.treaty_type.value if hasattr(negotiation.treaty_type, 'value') else str(negotiation.treaty_type),
            "status": negotiation.status.value if hasattr(negotiation.status, 'value') else str(negotiation.status),
            "started_at": negotiation.started_at.isoformat() if negotiation.started_at else None,
            "ended_at": negotiation.ended_at.isoformat() if negotiation.ended_at else None
        }
    
    def _serialize_offer(self, offer) -> Dict[str, Any]:
        """Serialize negotiation offer for WebSocket transmission."""
        return {
            "id": str(offer.id) if hasattr(offer, 'id') else None,
            "faction_id": str(offer.faction_id) if hasattr(offer, 'faction_id') else None,
            "terms": offer.terms if hasattr(offer, 'terms') else {},
            "created_at": offer.created_at.isoformat() if hasattr(offer, 'created_at') and offer.created_at else None
        }
    
    async def _get_faction_personalities(self, faction_ids: List[UUID]) -> Dict[UUID, Dict[str, Any]]:
        """Get faction personality data for narrative generation."""
        # This would integrate with the faction system to get personality data
        # For now, return empty personalities
        return {faction_id: {} for faction_id in faction_ids}
    
    # Additional handlers for other diplomatic actions would go here...
    async def _handle_join_negotiation(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle join negotiation request."""
        # Implementation for joining existing negotiations
        pass
    
    async def _handle_accept_offer(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle accept offer request."""
        # Implementation for accepting negotiation offers
        pass
    
    async def _handle_reject_offer(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle reject offer request."""
        # Implementation for rejecting negotiation offers  
        pass
    
    async def _handle_propose_alliance(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle propose alliance request."""
        # Implementation for alliance proposals
        pass
    
    async def _handle_issue_ultimatum(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle issue ultimatum request."""
        # Implementation for ultimatum issuance
        pass
    
    async def _handle_impose_sanction(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle impose sanction request."""
        # Implementation for sanction imposition
        pass
    
    async def _handle_get_faction_relationships(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle get faction relationships request."""
        # Implementation for retrieving faction relationships
        pass
    
    async def _handle_get_active_negotiations(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle get active negotiations request."""
        # Implementation for retrieving active negotiations
        pass
    
    async def _handle_subscribe_to_faction_events(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle subscribe to faction events request."""
        # Implementation for event subscriptions
        pass
    
    async def _handle_get_diplomatic_status(self, websocket: WebSocket, data: Dict[str, Any], request_id: str):
        """Handle get diplomatic status request."""
        # Implementation for diplomatic status retrieval
        pass
    
    async def _handle_heartbeat(self, websocket: WebSocket, request_id: str):
        """Handle heartbeat request."""
        await self.send_response(websocket, "heartbeat_response", {
            "timestamp": datetime.utcnow().isoformat()
        }, request_id)
    
    async def _handle_negotiation_started(self, event_data: Dict[str, Any]):
        """Handle negotiation started event."""
        # Implementation for negotiation start notifications
        pass
    
    async def _handle_conflict_declared(self, event_data: Dict[str, Any]):
        """Handle conflict declared event."""
        # Implementation for conflict declaration notifications
        pass
    
    async def _handle_diplomatic_incident(self, event_data: Dict[str, Any]):
        """Handle diplomatic incident event."""
        # Implementation for diplomatic incident notifications
        pass
    
    async def _handle_sanction_imposed(self, event_data: Dict[str, Any]):
        """Handle sanction imposed event."""
        # Implementation for sanction imposition notifications
        pass
    
    async def _handle_ultimatum_issued(self, event_data: Dict[str, Any]):
        """Handle ultimatum issued event."""
        # Implementation for ultimatum issuance notifications
        pass


# Global WebSocket handler instance
_diplomacy_websocket_handler = None

def get_diplomacy_websocket_handler() -> DiplomacyWebSocketHandler:
    """Get or create the global diplomacy WebSocket handler instance."""
    global _diplomacy_websocket_handler
    if _diplomacy_websocket_handler is None:
        _diplomacy_websocket_handler = DiplomacyWebSocketHandler()
    return _diplomacy_websocket_handler 