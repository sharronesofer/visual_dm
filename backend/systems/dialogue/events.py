"""
Dialogue system event integration.

This module defines the events emitted by the dialogue system and provides
an event emitter class for emitting these events through the event dispatcher.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from backend.systems.events.event import Event
from backend.systems.events.event_dispatcher import EventDispatcher


@dataclass
class DialogueEvent(Event):
    """Base class for dialogue-related events."""
    conversation_id: str
    timestamp: datetime = datetime.utcnow()


class DialogueStartedEvent(Event):
    """Event emitted when a new dialogue conversation starts."""
    
    event_type = "dialogue.started"
    
    def __init__(self, conversation_id: str, participants: Dict[str, str],
                 location_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a DialogueStartedEvent.
        
        Args:
            conversation_id: Unique identifier for the conversation
            participants: Dictionary mapping participant IDs to their roles
            location_id: Optional ID of the location where conversation is taking place
            metadata: Optional additional metadata
        """
        self.conversation_id = conversation_id
        self.participants = participants
        self.location_id = location_id
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
        
        # Prepare event data
        super().__init__({
            "conversation_id": conversation_id,
            "participants": participants,
            "location_id": location_id,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        })


class DialogueMessageEvent(Event):
    """Event emitted when a message is sent in a dialogue conversation."""
    
    event_type = "dialogue.message"
    
    def __init__(self, conversation_id: str, speaker_id: str, message: str,
                 message_type: str = "text", metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a DialogueMessageEvent.
        
        Args:
            conversation_id: Unique identifier for the conversation
            speaker_id: ID of the participant sending the message
            message: Content of the message
            message_type: Type of message (e.g., 'text', 'direct', 'emote')
            metadata: Optional additional metadata
        """
        self.conversation_id = conversation_id
        self.speaker_id = speaker_id
        self.message = message
        self.message_type = message_type
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
        
        # Prepare event data
        super().__init__({
            "conversation_id": conversation_id,
            "speaker_id": speaker_id,
            "message": message,
            "message_type": message_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        })


class DialogueEndedEvent(Event):
    """Event emitted when a dialogue conversation ends."""
    
    event_type = "dialogue.ended"
    
    def __init__(self, conversation_id: str, duration_seconds: float = 0,
                 message_count: int = 0, outcome: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a DialogueEndedEvent.
        
        Args:
            conversation_id: Unique identifier for the conversation
            duration_seconds: Duration of the conversation in seconds
            message_count: Number of messages in the conversation
            outcome: Reason or outcome of the conversation ending
            metadata: Optional additional metadata
        """
        self.conversation_id = conversation_id
        self.duration_seconds = duration_seconds
        self.message_count = message_count
        self.outcome = outcome
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
        
        # Prepare event data
        super().__init__({
            "conversation_id": conversation_id,
            "duration_seconds": duration_seconds,
            "message_count": message_count,
            "outcome": outcome,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        })


@dataclass
class DialogueInfoExtractedEvent(DialogueEvent):
    """Event emitted when information is extracted from dialogue."""
    info_type: str  # quest, location, item, etc.
    value: Any
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


class DialogueEventEmitter:
    """Helper class to emit dialogue events through the event dispatcher."""
    
    def __init__(self, event_dispatcher=None):
        """
        Initialize a DialogueEventEmitter.
        
        Args:
            event_dispatcher: Optional event dispatcher instance
        """
        self.event_dispatcher = event_dispatcher or EventDispatcher.get_instance()
    
    def emit_dialogue_started(self, conversation_id: str, participants: Dict[str, str],
                              location_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Emit a DialogueStartedEvent.
        
        Args:
            conversation_id: Unique identifier for the conversation
            participants: Dictionary mapping participant IDs to their roles
            location_id: Optional ID of the location where conversation is taking place
            metadata: Optional additional metadata
        """
        event = DialogueStartedEvent(
            conversation_id=conversation_id,
            participants=participants,
            location_id=location_id,
            metadata=metadata
        )
        self.event_dispatcher.emit(event)
    
    def emit_dialogue_message(self, conversation_id: str, speaker_id: str, message: str,
                              message_type: str = "text", metadata: Optional[Dict[str, Any]] = None):
        """
        Emit a DialogueMessageEvent.
        
        Args:
            conversation_id: Unique identifier for the conversation
            speaker_id: ID of the participant sending the message
            message: Content of the message
            message_type: Type of message (e.g., 'text', 'direct', 'emote')
            metadata: Optional additional metadata
        """
        event = DialogueMessageEvent(
            conversation_id=conversation_id,
            speaker_id=speaker_id,
            message=message,
            message_type=message_type,
            metadata=metadata
        )
        self.event_dispatcher.emit(event)
    
    def emit_dialogue_ended(self, conversation_id: str, duration_seconds: float = 0,
                            message_count: int = 0, outcome: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None):
        """
        Emit a DialogueEndedEvent.
        
        Args:
            conversation_id: Unique identifier for the conversation
            duration_seconds: Duration of the conversation in seconds
            message_count: Number of messages in the conversation
            outcome: Reason or outcome of the conversation ending
            metadata: Optional additional metadata
        """
        event = DialogueEndedEvent(
            conversation_id=conversation_id,
            duration_seconds=duration_seconds,
            message_count=message_count,
            outcome=outcome,
            metadata=metadata
        )
        self.event_dispatcher.emit(event)
    
    def emit_info_extracted(self, conversation_id: str, info_type: str, value: Any,
                           confidence: float = 1.0, metadata: Optional[Dict[str, Any]] = None):
        """Emit an event when information is extracted from dialogue."""
        event = DialogueInfoExtractedEvent(
            event_type="dialogue.info_extracted",
            conversation_id=conversation_id,
            info_type=info_type,
            value=value,
            confidence=confidence,
            metadata=metadata
        )
        self.event_dispatcher.publish_sync(event)
        return event 