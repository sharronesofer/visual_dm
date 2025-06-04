"""
Dialogue System Latency Service

This module provides latency monitoring and optimization for dialogue operations,
including response time tracking, performance metrics, and optimization strategies.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import analytics for performance tracking
from backend.infrastructure.analytics.event_logger import EventLogger, EventType

# Import dialogue models for type hints
from backend.infrastructure.dialogue_models.dialogue_models import DialogueResponse, DialogueContext

logger = logging.getLogger(__name__)

from __future__ import annotations

import uuid
from enum import Enum
import json

from fastapi import WebSocket

# Business logic imports (dialogue system)
from backend.infrastructure.systems.dialogue.events import DialogueEventEmitter, DialogueLatencyEvent
from backend.systems.dialogue.models.dialogue_models import DialogueResponse, DialogueContext
from backend.infrastructure.systems.dialogue.schemas.dialogue_schemas import LatencyResponseSchema

# Infrastructure imports
from backend.infrastructure.llm.services.llm_service import LLMService
from backend.infrastructure.events import EventBus, get_event_bus
from backend.infrastructure.core.websocket_manager import WebSocketManager

class LatencyThreshold(Enum):
    """Latency threshold categories for placeholder progression."""
    INSTANT = 0.0        # 0ms - immediate acknowledgment
    SHORT = 1.5          # 1.5s - thinking indicators
    MEDIUM = 3.0         # 3s - context-aware placeholders
    LONG = 8.0           # 8s - apologetic indicators
    TIMEOUT = 30.0       # 30s - maximum timeout

class PlaceholderCategory(Enum):
    """Categories of placeholder messages based on timing and context."""
    APPROACH_ACKNOWLEDGMENT = "approach_acknowledgment"
    THINKING_INDICATOR = "thinking_indicator"
    CONTEXT_AWARE_DELAY = "context_aware_delay"
    EXTENDED_PROCESSING = "extended_processing"
    TIMEOUT_WARNING = "timeout_warning"

class DialogueLatencyService:
    """
    Core service for managing NPC dialogue latency and placeholder messages.
    
    Provides real-time updates via WebSocket, context-aware placeholder selection,
    and seamless integration with the existing dialogue system infrastructure.
    """
    
    def __init__(
        self,
        websocket_manager: Optional[WebSocketManager] = None,
        event_emitter: Optional[DialogueEventEmitter] = None,
        event_bus: Optional[EventBus] = None,
        llm_service: Optional[LLMService] = None
    ):
        """
        Initialize the dialogue latency service.
        
        Args:
            websocket_manager: WebSocket manager for real-time communication
            event_emitter: Dialogue event emitter for system integration
            event_bus: Global event bus for cross-system communication
            llm_service: LLM service for AI response generation
        """
        self.websocket_manager = websocket_manager or WebSocketManager()
        self.event_emitter = event_emitter or DialogueEventEmitter()
        self.event_bus = event_bus or get_event_bus()
        self.llm_service = llm_service
        
        # Active dialogue sessions with latency tracking
        self.active_sessions: Dict[str, DialogueLatencySession] = {}
        
        # WebSocket connections for real-time updates
        self.websocket_connections: Set[WebSocket] = set()
        
        # Placeholder message templates
        self._initialize_placeholder_templates()
        
        # Event handlers
        self._setup_event_handlers()
        
        logger.info("DialogueLatencyService initialized")
    
    def _initialize_placeholder_templates(self) -> None:
        """Initialize placeholder message templates by category and context."""
        self.placeholder_templates = {
            PlaceholderCategory.APPROACH_ACKNOWLEDGMENT: {
                DialogueContext.GENERAL: [
                    "The {npc_type} notices you approaching...",
                    "The {npc_type} looks up from their activities...",
                    "The {npc_type} turns their attention to you..."
                ],
                DialogueContext.BARTERING: [
                    "The merchant looks up from their wares...",
                    "The trader sets down their ledger and greets you...",
                    "The shopkeeper's eyes light up as they see a potential customer..."
                ],
                DialogueContext.QUEST_RELATED: [
                    "The {npc_type} recognizes you immediately...",
                    "The {npc_type} seems to have been expecting you...",
                    "The {npc_type} looks relieved to see you..."
                ],
                DialogueContext.FACTION_RELATED: [
                    "The {faction_member} acknowledges your approach with respect...",
                    "The {faction_member} gives you a knowing nod...",
                    "The {faction_member} straightens as they recognize your allegiance..."
                ],
                DialogueContext.SOCIAL: [
                    "The {npc_type} smiles warmly as you approach...",
                    "The {npc_type} pauses their conversation to greet you...",
                    "The {npc_type} waves you over with a friendly gesture..."
                ]
            },
            
            PlaceholderCategory.THINKING_INDICATOR: {
                DialogueContext.GENERAL: [
                    "...",
                    "They pause thoughtfully...",
                    "Considering your words...",
                    "Taking a moment to think..."
                ],
                DialogueContext.BARTERING: [
                    "Calculating prices...",
                    "Examining their inventory...",
                    "Considering the trade value..."
                ],
                DialogueContext.QUEST_RELATED: [
                    "Recalling the details...",
                    "Gathering their thoughts...",
                    "Remembering what they know..."
                ]
            },
            
            PlaceholderCategory.CONTEXT_AWARE_DELAY: {
                DialogueContext.BARTERING: [
                    "They examine your goods carefully...",
                    "Calculating market values...",
                    "Checking their current stock..."
                ],
                DialogueContext.QUEST_RELATED: [
                    "They recall what they know about that...",
                    "Searching their memory for details...",
                    "Gathering relevant information..."
                ],
                DialogueContext.FACTION_RELATED: [
                    "They consider their allegiances carefully...",
                    "Weighing the political implications...",
                    "Thinking about their faction's interests..."
                ],
                DialogueContext.LORE: [
                    "Reaching into their vast knowledge...",
                    "Recalling ancient stories...",
                    "Sorting through historical details..."
                ]
            },
            
            PlaceholderCategory.EXTENDED_PROCESSING: {
                DialogueContext.GENERAL: [
                    "This seems to require careful thought...",
                    "They're gathering their thoughts...",
                    "Taking time to consider your request...",
                    "This appears to be a complex matter..."
                ]
            },
            
            PlaceholderCategory.TIMEOUT_WARNING: {
                DialogueContext.GENERAL: [
                    "The conversation seems unexpectedly complex...",
                    "They appear to be deeply contemplating...",
                    "This may take a moment longer than usual..."
                ]
            }
        }
    
    def _setup_event_handlers(self) -> None:
        """Set up event handlers for dialogue system integration."""
        # Listen for dialogue start events
        self.event_bus.subscribe("dialogue.started", self._on_dialogue_started)
        self.event_bus.subscribe("dialogue.ai_request", self._on_ai_request_started)
        self.event_bus.subscribe("dialogue.ai_response", self._on_ai_response_received)
        self.event_bus.subscribe("dialogue.ended", self._on_dialogue_ended)
    
    async def start_dialogue_latency_tracking(
        self,
        conversation_id: str,
        npc_id: str,
        context: DialogueContext = DialogueContext.GENERAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DialogueLatencySession:
        """
        Start latency tracking for a new dialogue session.
        
        Args:
            conversation_id: Unique conversation identifier
            npc_id: NPC identifier for context-aware placeholders
            context: Dialogue context for appropriate placeholder selection
            metadata: Additional metadata for placeholder customization
            
        Returns:
            DialogueLatencySession object for tracking this conversation
        """
        # Create new latency session
        session = DialogueLatencySession(
            conversation_id=conversation_id,
            npc_id=npc_id,
            context=context,
            metadata=metadata or {}
        )
        
        self.active_sessions[conversation_id] = session
        
        # Send immediate acknowledgment
        await self._send_acknowledgment_placeholder(session)
        
        # Start latency monitoring task
        asyncio.create_task(self._monitor_latency(session))
        
        logger.info(f"Started latency tracking for conversation {conversation_id}")
        return session
    
    async def update_dialogue_context(
        self,
        conversation_id: str,
        new_context: DialogueContext,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update dialogue context for more appropriate placeholder selection.
        
        Args:
            conversation_id: Conversation to update
            new_context: New dialogue context
            metadata: Additional metadata updates
            
        Returns:
            True if successfully updated, False if session not found
        """
        if conversation_id not in self.active_sessions:
            logger.warning(f"Attempted to update context for non-existent session {conversation_id}")
            return False
        
        session = self.active_sessions[conversation_id]
        session.context = new_context
        
        if metadata:
            session.metadata.update(metadata)
        
        logger.info(f"Updated context for conversation {conversation_id} to {new_context}")
        return True
    
    async def handle_ai_response_start(
        self,
        conversation_id: str,
        request_id: Optional[str] = None
    ) -> bool:
        """
        Handle the start of an AI response generation.
        
        Args:
            conversation_id: Conversation identifier
            request_id: Optional request identifier for tracking
            
        Returns:
            True if session exists and was updated
        """
        if conversation_id not in self.active_sessions:
            logger.warning(f"AI response start for non-existent session {conversation_id}")
            return False
        
        session = self.active_sessions[conversation_id]
        session.ai_request_id = request_id
        session.ai_start_time = datetime.utcnow()
        session.status = "processing"
        
        # Start intensive latency monitoring
        asyncio.create_task(self._monitor_ai_latency(session))
        
        logger.info(f"Started AI response tracking for conversation {conversation_id}")
        return True
    
    async def handle_ai_response_complete(
        self,
        conversation_id: str,
        response: str,
        request_id: Optional[str] = None
    ) -> bool:
        """
        Handle completion of AI response generation.
        
        Args:
            conversation_id: Conversation identifier
            response: Generated AI response
            request_id: Optional request identifier for verification
            
        Returns:
            True if session exists and was completed
        """
        if conversation_id not in self.active_sessions:
            logger.warning(f"AI response complete for non-existent session {conversation_id}")
            return False
        
        session = self.active_sessions[conversation_id]
        
        # Verify request ID if provided
        if request_id and session.ai_request_id != request_id:
            logger.warning(f"Request ID mismatch for conversation {conversation_id}")
        
        session.ai_end_time = datetime.utcnow()
        session.final_response = response
        session.status = "completed"
        
        # Calculate total latency
        if session.ai_start_time:
            latency = (session.ai_end_time - session.ai_start_time).total_seconds()
            session.total_latency = latency
        
        # Send final response via WebSocket
        await self._send_final_response(session, response)
        
        # Emit completion event
        await self._emit_latency_completion_event(session)
        
        logger.info(f"Completed AI response for conversation {conversation_id}, latency: {session.total_latency:.2f}s")
        return True
    
    async def handle_ai_response_timeout(
        self,
        conversation_id: str,
        timeout_reason: str = "AI response timeout"
    ) -> bool:
        """
        Handle AI response timeout scenarios.
        
        Args:
            conversation_id: Conversation identifier
            timeout_reason: Reason for timeout
            
        Returns:
            True if session exists and timeout was handled
        """
        if conversation_id not in self.active_sessions:
            logger.warning(f"AI timeout for non-existent session {conversation_id}")
            return False
        
        session = self.active_sessions[conversation_id]
        session.status = "timeout"
        session.timeout_reason = timeout_reason
        
        # Send timeout message
        timeout_message = "I apologize, but I'm having trouble formulating a response right now. Please try again."
        await self._send_final_response(session, timeout_message)
        
        # Emit timeout event
        await self._emit_latency_timeout_event(session)
        
        logger.warning(f"AI response timeout for conversation {conversation_id}: {timeout_reason}")
        return True
    
    async def end_dialogue_latency_tracking(self, conversation_id: str) -> bool:
        """
        End latency tracking for a dialogue session.
        
        Args:
            conversation_id: Conversation to end tracking for
            
        Returns:
            True if session existed and was removed
        """
        if conversation_id not in self.active_sessions:
            logger.warning(f"Attempted to end tracking for non-existent session {conversation_id}")
            return False
        
        session = self.active_sessions[conversation_id]
        
        # Cancel any ongoing monitoring tasks
        if hasattr(session, '_monitoring_task') and session._monitoring_task:
            session._monitoring_task.cancel()
        
        # Remove from active sessions
        del self.active_sessions[conversation_id]
        
        logger.info(f"Ended latency tracking for conversation {conversation_id}")
        return True
    
    async def _send_acknowledgment_placeholder(self, session: 'DialogueLatencySession') -> None:
        """Send immediate acknowledgment placeholder."""
        templates = self.placeholder_templates[PlaceholderCategory.APPROACH_ACKNOWLEDGMENT]
        context_templates = templates.get(session.context, templates[DialogueContext.GENERAL])
        
        message = self._format_placeholder_message(
            context_templates[0],
            session.metadata
        )
        
        await self._send_latency_update(session, message, PlaceholderCategory.APPROACH_ACKNOWLEDGMENT)
        session.last_placeholder_time = datetime.utcnow()
    
    async def _monitor_latency(self, session: 'DialogueLatencySession') -> None:
        """Monitor latency and send appropriate placeholder updates."""
        session._monitoring_task = asyncio.current_task()
        
        try:
            while session.status in ["waiting", "processing"]:
                await asyncio.sleep(0.5)  # Check every 500ms
                
                if session.status == "completed" or session.status == "timeout":
                    break
                
                elapsed = (datetime.utcnow() - session.start_time).total_seconds()
                
                # Check if we need to send a new placeholder
                if await self._should_send_placeholder(session, elapsed):
                    await self._send_appropriate_placeholder(session, elapsed)
        
        except asyncio.CancelledError:
            logger.info(f"Latency monitoring cancelled for conversation {session.conversation_id}")
        except Exception as e:
            logger.error(f"Error in latency monitoring for {session.conversation_id}: {e}")
    
    async def _monitor_ai_latency(self, session: 'DialogueLatencySession') -> None:
        """Intensive monitoring during AI response generation."""
        try:
            while session.status == "processing":
                await asyncio.sleep(0.2)  # More frequent checks during AI processing
                
                if not session.ai_start_time:
                    continue
                
                elapsed = (datetime.utcnow() - session.ai_start_time).total_seconds()
                
                # Check for timeout
                if elapsed >= LatencyThreshold.TIMEOUT.value:
                    await self.handle_ai_response_timeout(
                        session.conversation_id,
                        f"AI response exceeded {LatencyThreshold.TIMEOUT.value}s timeout"
                    )
                    break
                
                # Send progressive placeholders
                if await self._should_send_placeholder(session, elapsed):
                    await self._send_appropriate_placeholder(session, elapsed)
        
        except asyncio.CancelledError:
            logger.info(f"AI latency monitoring cancelled for conversation {session.conversation_id}")
        except Exception as e:
            logger.error(f"Error in AI latency monitoring for {session.conversation_id}: {e}")
    
    async def _should_send_placeholder(self, session: 'DialogueLatencySession', elapsed: float) -> bool:
        """Determine if a placeholder should be sent based on elapsed time."""
        # Don't send if we recently sent one
        if session.last_placeholder_time:
            since_last = (datetime.utcnow() - session.last_placeholder_time).total_seconds()
            if since_last < 1.0:  # Minimum 1 second between placeholders
                return False
        
        # Check thresholds
        if elapsed >= LatencyThreshold.LONG.value and session.last_placeholder_category != PlaceholderCategory.EXTENDED_PROCESSING:
            return True
        elif elapsed >= LatencyThreshold.MEDIUM.value and session.last_placeholder_category not in [PlaceholderCategory.CONTEXT_AWARE_DELAY, PlaceholderCategory.EXTENDED_PROCESSING]:
            return True
        elif elapsed >= LatencyThreshold.SHORT.value and session.last_placeholder_category not in [PlaceholderCategory.THINKING_INDICATOR, PlaceholderCategory.CONTEXT_AWARE_DELAY, PlaceholderCategory.EXTENDED_PROCESSING]:
            return True
        
        return False
    
    async def _send_appropriate_placeholder(self, session: 'DialogueLatencySession', elapsed: float) -> None:
        """Send appropriate placeholder based on elapsed time and context."""
        if elapsed >= LatencyThreshold.LONG.value:
            category = PlaceholderCategory.EXTENDED_PROCESSING
        elif elapsed >= LatencyThreshold.MEDIUM.value:
            category = PlaceholderCategory.CONTEXT_AWARE_DELAY
        elif elapsed >= LatencyThreshold.SHORT.value:
            category = PlaceholderCategory.THINKING_INDICATOR
        else:
            return  # Too early for placeholders
        
        # Get appropriate template
        templates = self.placeholder_templates[category]
        context_templates = templates.get(session.context, templates[DialogueContext.GENERAL])
        
        # Select message (could be random or sequential)
        import random
        message = self._format_placeholder_message(
            random.choice(context_templates),
            session.metadata
        )
        
        await self._send_latency_update(session, message, category)
        session.last_placeholder_time = datetime.utcnow()
        session.last_placeholder_category = category
    
    def _format_placeholder_message(self, template: str, metadata: Dict[str, Any]) -> str:
        """Format placeholder message template with metadata."""
        try:
            return template.format(**metadata)
        except (KeyError, ValueError):
            # If formatting fails, return template as-is
            logger.warning(f"Failed to format placeholder template: {template}")
            return template
    
    async def _send_latency_update(
        self,
        session: 'DialogueLatencySession',
        message: str,
        category: PlaceholderCategory
    ) -> None:
        """Send latency update via WebSocket to Unity frontend."""
        update_data = {
            "type": "dialogue_latency_update",
            "conversation_id": session.conversation_id,
            "npc_id": session.npc_id,
            "message": message,
            "category": category.value,
            "context": session.context.value,
            "timestamp": datetime.utcnow().isoformat(),
            "elapsed_time": (datetime.utcnow() - session.start_time).total_seconds()
        }
        
        # Send via WebSocket manager
        await self.websocket_manager.broadcast_to_channel("dialogue", update_data)
        
        # Also emit event for system integration
        await self._emit_latency_update_event(session, message, category)
    
    async def _send_final_response(self, session: 'DialogueLatencySession', response: str) -> None:
        """Send final dialogue response via WebSocket."""
        final_data = {
            "type": "dialogue_final_response",
            "conversation_id": session.conversation_id,
            "npc_id": session.npc_id,
            "response": response,
            "total_latency": session.total_latency,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send via WebSocket manager
        await self.websocket_manager.broadcast_to_channel("dialogue", final_data)
    
    async def _emit_latency_update_event(
        self,
        session: 'DialogueLatencySession',
        message: str,
        category: PlaceholderCategory
    ) -> None:
        """Emit latency update event for system integration."""
        event_data = {
            "conversation_id": session.conversation_id,
            "npc_id": session.npc_id,
            "placeholder_message": message,
            "category": category.value,
            "context": session.context.value,
            "elapsed_time": (datetime.utcnow() - session.start_time).total_seconds()
        }
        
        await self.event_emitter.emit(DialogueLatencyEvent(
            event_type="latency_update",
            data=event_data
        ))
    
    async def _emit_latency_completion_event(self, session: 'DialogueLatencySession') -> None:
        """Emit latency completion event."""
        event_data = {
            "conversation_id": session.conversation_id,
            "npc_id": session.npc_id,
            "total_latency": session.total_latency,
            "status": session.status
        }
        
        await self.event_emitter.emit(DialogueLatencyEvent(
            event_type="latency_completed",
            data=event_data
        ))
    
    async def _emit_latency_timeout_event(self, session: 'DialogueLatencySession') -> None:
        """Emit latency timeout event."""
        event_data = {
            "conversation_id": session.conversation_id,
            "npc_id": session.npc_id,
            "timeout_reason": session.timeout_reason,
            "elapsed_time": (datetime.utcnow() - session.start_time).total_seconds()
        }
        
        await self.event_emitter.emit(DialogueLatencyEvent(
            event_type="latency_timeout",
            data=event_data
        ))
    
    # Event handlers for dialogue system integration
    async def _on_dialogue_started(self, event_data: Dict[str, Any]) -> None:
        """Handle dialogue started event."""
        conversation_id = event_data.get("conversation_id")
        if conversation_id:
            # Auto-start latency tracking for new dialogues
            await self.start_dialogue_latency_tracking(
                conversation_id=conversation_id,
                npc_id=event_data.get("npc_id", "unknown"),
                context=DialogueContext.GENERAL,
                metadata=event_data.get("metadata", {})
            )
    
    async def _on_ai_request_started(self, event_data: Dict[str, Any]) -> None:
        """Handle AI request started event."""
        conversation_id = event_data.get("conversation_id")
        request_id = event_data.get("request_id")
        
        if conversation_id:
            await self.handle_ai_response_start(conversation_id, request_id)
    
    async def _on_ai_response_received(self, event_data: Dict[str, Any]) -> None:
        """Handle AI response received event."""
        conversation_id = event_data.get("conversation_id")
        response = event_data.get("response")
        request_id = event_data.get("request_id")
        
        if conversation_id and response:
            await self.handle_ai_response_complete(conversation_id, response, request_id)
    
    async def _on_dialogue_ended(self, event_data: Dict[str, Any]) -> None:
        """Handle dialogue ended event."""
        conversation_id = event_data.get("conversation_id")
        if conversation_id:
            await self.end_dialogue_latency_tracking(conversation_id)
    
    # WebSocket connection management
    async def connect_websocket(self, websocket: WebSocket) -> None:
        """Connect a WebSocket for real-time updates."""
        await self.websocket_manager.connect(websocket, "dialogue")
        self.websocket_connections.add(websocket)
        logger.info("WebSocket connected to dialogue latency service")
    
    async def disconnect_websocket(self, websocket: WebSocket) -> None:
        """Disconnect a WebSocket."""
        await self.websocket_manager.disconnect(websocket)
        self.websocket_connections.discard(websocket)
        logger.info("WebSocket disconnected from dialogue latency service")

class DialogueLatencySession:
    """
    Represents an active dialogue session with latency tracking.
    
    Tracks timing, context, placeholder history, and current state
    for comprehensive latency management.
    """
    
    def __init__(
        self,
        conversation_id: str,
        npc_id: str,
        context: DialogueContext = DialogueContext.GENERAL,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.conversation_id = conversation_id
        self.npc_id = npc_id
        self.context = context
        self.metadata = metadata or {}
        
        # Timing tracking
        self.start_time = datetime.utcnow()
        self.ai_start_time: Optional[datetime] = None
        self.ai_end_time: Optional[datetime] = None
        self.last_placeholder_time: Optional[datetime] = None
        self.total_latency: Optional[float] = None
        
        # State tracking
        self.status = "waiting"  # waiting, processing, completed, timeout
        self.ai_request_id: Optional[str] = None
        self.final_response: Optional[str] = None
        self.timeout_reason: Optional[str] = None
        
        # Placeholder tracking
        self.last_placeholder_category: Optional[PlaceholderCategory] = None
        self.placeholder_history: List[Dict[str, Any]] = []
        
        # Task management
        self._monitoring_task: Optional[asyncio.Task] = None
    
    def add_placeholder_to_history(
        self,
        message: str,
        category: PlaceholderCategory,
        elapsed_time: float
    ) -> None:
        """Add a placeholder message to the history."""
        self.placeholder_history.append({
            "message": message,
            "category": category.value,
            "elapsed_time": elapsed_time,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the session for analytics."""
        return {
            "conversation_id": self.conversation_id,
            "npc_id": self.npc_id,
            "context": self.context.value,
            "start_time": self.start_time.isoformat(),
            "total_latency": self.total_latency,
            "status": self.status,
            "placeholder_count": len(self.placeholder_history),
            "metadata": self.metadata
        }

# Global service instance
_dialogue_latency_service: Optional[DialogueLatencyService] = None

def get_dialogue_latency_service() -> DialogueLatencyService:
    """Get or create the global dialogue latency service instance."""
    global _dialogue_latency_service
    if _dialogue_latency_service is None:
        _dialogue_latency_service = DialogueLatencyService()
    return _dialogue_latency_service 