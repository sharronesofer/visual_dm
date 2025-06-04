"""
Dialogue Infrastructure Module

This module contains infrastructure components for the dialogue system,
including API routes, schemas, events, and latency management.

Separated from business logic to maintain clean architecture.
"""

from .routers.websocket_routes import dialogue_websocket_router
from .latency_service import DialogueLatencyService, get_dialogue_latency_service
from .events.dialogue_events import (
    DialogueEventEmitter,
    DialogueEvent,
    DialogueLatencyEvent,
    get_dialogue_event_emitter
)

__all__ = [
    "dialogue_websocket_router",
    "DialogueLatencyService", 
    "get_dialogue_latency_service",
    "DialogueEventEmitter",
    "DialogueEvent",
    "DialogueLatencyEvent",
    "get_dialogue_event_emitter"
] 