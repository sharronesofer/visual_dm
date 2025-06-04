"""
Chaos System

A hidden narrative engine that monitors system pressure across the game world 
and triggers sudden, dramatic destabilizing events when thresholds are exceeded.
This system operates completely behind the scenes to create emergent storytelling 
opportunities through systematic chaos generation.

Components:
- ChaosEngine: Main engine coordinating all chaos system operations
- PressureMonitor: Monitors pressure across all game systems  
- EventTriggerSystem: Handles chaos event triggering and cascading effects
- ChaosMath: Mathematical algorithms for chaos calculations
- ChaosEvents: Event types and classes for chaos-related events
"""

from backend.systems.chaos.core.chaos_engine import ChaosEngine
from backend.systems.chaos.core.pressure_monitor import PressureMonitor
from backend.systems.chaos.core.event_triggers import EventTriggerSystem
from backend.systems.chaos.core.config import ChaosConfig
from backend.infrastructure.systems.chaos.models.chaos_events import (
    ChaosEvent, ChaosEventType,
    PoliticalUpheavalEvent, NaturalDisasterEvent, EconomicCollapseEvent,
    WarOutbreakEvent, ResourceScarcityEvent, FactionBetrayalEvent,
    CharacterRevelationEvent
)
from backend.systems.chaos.services.chaos_service import ChaosService

__all__ = [
    # Core components
    'ChaosEngine',
    'PressureMonitor', 
    'EventTriggerSystem',
    'ChaosConfig',
    
    # Event types
    'ChaosEvent',
    'ChaosEventType',
    'PoliticalUpheavalEvent',
    'NaturalDisasterEvent', 
    'EconomicCollapseEvent',
    'WarOutbreakEvent',
    'ResourceScarcityEvent',
    'FactionBetrayalEvent',
    'CharacterRevelationEvent',
    
    # Services
    'ChaosService',
] 