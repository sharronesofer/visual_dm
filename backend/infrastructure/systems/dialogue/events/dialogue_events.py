"""
Dialogue Events - Event definitions for the dialogue system.

This module provides event classes and emitters for dialogue system integration,
including latency management events, dialogue lifecycle events, and WebSocket
communication events.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

# Infrastructure imports
from backend.infrastructure.events import EventBus, get_event_bus

# Configure logger
logger = logging.getLogger(__name__)

class DialogueEventType(Enum):
    """Types of dialogue events."""
    DIALOGUE_STARTED = "dialogue_started"
    DIALOGUE_MESSAGE = "dialogue_message"
    DIALOGUE_ENDED = "dialogue_ended"
    AI_REQUEST_STARTED = "ai_request_started"
    AI_RESPONSE_RECEIVED = "ai_response_received"
    AI_REQUEST_TIMEOUT = "ai_request_timeout"
    LATENCY_UPDATE = "latency_update"
    LATENCY_COMPLETED = "latency_completed"
    LATENCY_TIMEOUT = "latency_timeout"
    CONTEXT_UPDATED = "context_updated"

@dataclass
class DialogueEvent:
    """Base class for dialogue events."""
    event_type: DialogueEventType
    conversation_id: str
    timestamp: datetime
    data: Dict[str, Any]
    
    def __post_init__(self):
        if isinstance(self.event_type, str):
            self.event_type = DialogueEventType(self.event_type)

@dataclass
class DialogueStartedEvent(DialogueEvent):
    """Event fired when a dialogue session starts."""
    npc_id: str
    participant_ids: List[str]
    location_id: Optional[str] = None
    
    def __init__(
        self,
        conversation_id: str,
        npc_id: str,
        participant_ids: List[str],
        location_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type=DialogueEventType.DIALOGUE_STARTED,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            data=data or {}
        )
        self.npc_id = npc_id
        self.participant_ids = participant_ids
        self.location_id = location_id

@dataclass
class DialogueMessageEvent(DialogueEvent):
    """Event fired when a message is sent in dialogue."""
    sender_id: str
    content: str
    message_type: str
    
    def __init__(
        self,
        conversation_id: str,
        sender_id: str,
        content: str,
        message_type: str = "dialogue",
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type=DialogueEventType.DIALOGUE_MESSAGE,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            data=data or {}
        )
        self.sender_id = sender_id
        self.content = content
        self.message_type = message_type

@dataclass
class DialogueEndedEvent(DialogueEvent):
    """Event fired when a dialogue session ends."""
    duration: float
    message_count: int
    
    def __init__(
        self,
        conversation_id: str,
        duration: float,
        message_count: int,
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type=DialogueEventType.DIALOGUE_ENDED,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            data=data or {}
        )
        self.duration = duration
        self.message_count = message_count

@dataclass
class AIRequestStartedEvent(DialogueEvent):
    """Event fired when an AI request starts."""
    request_id: str
    npc_id: str
    request_context: Dict[str, Any]
    
    def __init__(
        self,
        conversation_id: str,
        request_id: str,
        npc_id: str,
        request_context: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type=DialogueEventType.AI_REQUEST_STARTED,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            data=data or {}
        )
        self.request_id = request_id
        self.npc_id = npc_id
        self.request_context = request_context

@dataclass
class AIResponseReceivedEvent(DialogueEvent):
    """Event fired when an AI response is received."""
    request_id: str
    response: str
    latency: float
    
    def __init__(
        self,
        conversation_id: str,
        request_id: str,
        response: str,
        latency: float,
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type=DialogueEventType.AI_RESPONSE_RECEIVED,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            data=data or {}
        )
        self.request_id = request_id
        self.response = response
        self.latency = latency

@dataclass
class DialogueLatencyEvent(DialogueEvent):
    """Event fired for latency management updates."""
    def __init__(
        self,
        event_type: str,
        data: Dict[str, Any],
        conversation_id: Optional[str] = None
    ):
        super().__init__(
            event_type=DialogueEventType(event_type),
            conversation_id=conversation_id or data.get("conversation_id", "unknown"),
            timestamp=datetime.utcnow(),
            data=data
        )

class DialogueEventEmitter:
    """
    Event emitter for dialogue system events.
    
    Provides centralized event emission for dialogue events with proper
    integration to the global event bus and local event handlers.
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize the dialogue event emitter.
        
        Args:
            event_bus: Global event bus for cross-system communication
        """
        self.event_bus = event_bus or get_event_bus()
        self.local_handlers: Dict[DialogueEventType, List[Callable]] = {}
        
        logger.info("DialogueEventEmitter initialized")
    
    async def emit(self, event: DialogueEvent) -> None:
        """
        Emit a dialogue event to both local handlers and the global event bus.
        
        Args:
            event: The dialogue event to emit
        """
        try:
            # Emit to global event bus with system prefix
            await self.event_bus.publish(f"dialogue.{event.event_type.value}", event.data)
            
            # Call local handlers
            handlers = self.local_handlers.get(event.event_type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in dialogue event handler: {e}")
            
            logger.debug(f"Emitted dialogue event: {event.event_type.value}")
        
        except Exception as e:
            logger.error(f"Failed to emit dialogue event {event.event_type.value}: {e}")
    
    def subscribe(self, event_type: DialogueEventType, handler: Callable) -> None:
        """
        Subscribe to a specific dialogue event type.
        
        Args:
            event_type: Type of dialogue event to subscribe to
            handler: Function to call when event is emitted
        """
        if event_type not in self.local_handlers:
            self.local_handlers[event_type] = []
        
        self.local_handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to dialogue event: {event_type.value}")
    
    def unsubscribe(self, event_type: DialogueEventType, handler: Callable) -> bool:
        """
        Unsubscribe from a specific dialogue event type.
        
        Args:
            event_type: Type of dialogue event to unsubscribe from
            handler: Function to remove from handlers
            
        Returns:
            True if handler was found and removed, False otherwise
        """
        if event_type in self.local_handlers:
            try:
                self.local_handlers[event_type].remove(handler)
                logger.info(f"Unsubscribed handler from dialogue event: {event_type.value}")
                return True
            except ValueError:
                pass
        
        return False
    
    async def emit_dialogue_started(
        self,
        conversation_id: str,
        npc_id: str,
        participant_ids: List[str],
        location_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Emit a dialogue started event."""
        event = DialogueStartedEvent(
            conversation_id=conversation_id,
            npc_id=npc_id,
            participant_ids=participant_ids,
            location_id=location_id,
            data=data
        )
        await self.emit(event)
    
    async def emit_dialogue_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str,
        message_type: str = "dialogue",
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Emit a dialogue message event."""
        event = DialogueMessageEvent(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            data=data
        )
        await self.emit(event)
    
    async def emit_dialogue_ended(
        self,
        conversation_id: str,
        duration: float,
        message_count: int,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Emit a dialogue ended event."""
        event = DialogueEndedEvent(
            conversation_id=conversation_id,
            duration=duration,
            message_count=message_count,
            data=data
        )
        await self.emit(event)
    
    async def emit_ai_request_started(
        self,
        conversation_id: str,
        request_id: str,
        npc_id: str,
        request_context: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Emit an AI request started event."""
        event = AIRequestStartedEvent(
            conversation_id=conversation_id,
            request_id=request_id,
            npc_id=npc_id,
            request_context=request_context,
            data=data
        )
        await self.emit(event)
    
    async def emit_ai_response_received(
        self,
        conversation_id: str,
        request_id: str,
        response: str,
        latency: float,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Emit an AI response received event."""
        event = AIResponseReceivedEvent(
            conversation_id=conversation_id,
            request_id=request_id,
            response=response,
            latency=latency,
            data=data
        )
        await self.emit(event)

# Global event emitter instance
_dialogue_event_emitter: Optional[DialogueEventEmitter] = None

def get_dialogue_event_emitter() -> DialogueEventEmitter:
    """Get or create the global dialogue event emitter."""
    global _dialogue_event_emitter
    if _dialogue_event_emitter is None:
        _dialogue_event_emitter = DialogueEventEmitter()
    return _dialogue_event_emitter

# Import asyncio at the end to avoid circular imports
import asyncio 