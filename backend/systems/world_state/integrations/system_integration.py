"""
World State System Integration Hub

Implements the Bible requirement for world_state to be the "Integration Hub: 
World State System (manages all system interactions)". This module provides
cross-system event propagation and state synchronization.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from uuid import uuid4

from backend.systems.world_state.services.services import WorldStateService
from backend.systems.world_state.world_types import StateCategory, WorldRegion


logger = logging.getLogger(__name__)


class SystemType(Enum):
    """Types of systems that integrate with world state"""
    FACTION = "faction"
    ECONOMY = "economy"
    COMBAT = "combat"
    DIPLOMACY = "diplomacy"
    POPULATION = "population"
    QUEST = "quest"
    REGION = "region"
    NPC = "npc"
    INVENTORY = "inventory"
    EQUIPMENT = "equipment"
    MAGIC = "magic"
    RELIGION = "religion"
    RUMOR = "rumor"
    TENSION = "tension"
    TIME = "time"
    WEATHER = "weather"
    DISEASE = "disease"
    REPAIR = "repair"
    LOOT = "loot"
    MEMORY = "memory"
    CHAOS = "chaos"
    ARC = "arc"
    MOTIF = "motif"
    CHARACTER = "character"
    DIALOGUE = "dialogue"
    POI = "poi"
    ESPIONAGE = "espionage"
    WORLD_GENERATION = "world_generation"


@dataclass
class SystemEvent:
    """Represents an event from another system that affects world state"""
    event_id: str
    source_system: SystemType
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 5  # 1-10, 10 being highest priority
    affected_regions: List[str] = None
    state_changes: List[Dict[str, Any]] = None


@dataclass
class StateChangeRequest:
    """Request to change world state from another system"""
    request_id: str
    source_system: SystemType
    key: str
    value: Any
    region_id: Optional[str] = None
    category: StateCategory = StateCategory.OTHER
    reason: str = ""
    metadata: Dict[str, Any] = None


class SystemIntegrationHub:
    """
    Central hub for managing interactions between world_state and other systems.
    Implements the Bible's requirement for world_state to be the integration hub.
    """
    
    def __init__(self, world_state_service: WorldStateService):
        self.world_state_service = world_state_service
        
        # System registry and event handlers
        self.registered_systems: Set[SystemType] = set()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.state_change_listeners: Dict[str, List[Callable]] = {}
        
        # Event processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Metrics and monitoring
        self.events_processed = 0
        self.state_changes_propagated = 0
        self.error_count = 0
        
        logger.info("SystemIntegrationHub initialized")
    
    async def start(self):
        """Start the integration hub event processing"""
        if self.is_running:
            return
        
        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_events())
        logger.info("SystemIntegrationHub started")
    
    async def stop(self):
        """Stop the integration hub"""
        self.is_running = False
        if self.processing_task:
            self.processing_task.cancel()
        logger.info("SystemIntegrationHub stopped")
    
    # === SYSTEM REGISTRATION ===
    
    def register_system(self, system_type: SystemType, event_handlers: Dict[str, Callable] = None):
        """Register a system with the integration hub"""
        self.registered_systems.add(system_type)
        
        if event_handlers:
            for event_type, handler in event_handlers.items():
                self.register_event_handler(f"{system_type.value}.{event_type}", handler)
        
        logger.info(f"Registered system: {system_type.value}")
    
    def register_event_handler(self, event_pattern: str, handler: Callable):
        """Register an event handler for specific event patterns"""
        if event_pattern not in self.event_handlers:
            self.event_handlers[event_pattern] = []
        self.event_handlers[event_pattern].append(handler)
    
    def register_state_change_listener(self, key_pattern: str, listener: Callable):
        """Register a listener for world state changes"""
        if key_pattern not in self.state_change_listeners:
            self.state_change_listeners[key_pattern] = []
        self.state_change_listeners[key_pattern].append(listener)
    
    # === EVENT PROCESSING ===
    
    async def emit_system_event(self, event: SystemEvent):
        """Emit an event from a system that may affect world state"""
        await self.event_queue.put(event)
    
    async def request_state_change(self, request: StateChangeRequest) -> bool:
        """Request a state change from another system"""
        try:
            success = await self.world_state_service.set_state_variable(
                key=request.key,
                value=request.value,
                region_id=request.region_id,
                category=request.category,
                reason=f"[{request.source_system.value}] {request.reason}",
                user_id=f"system_{request.source_system.value}"
            )
            
            if success:
                # Notify other systems of the change
                await self._propagate_state_change(request)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to process state change request from {request.source_system.value}: {e}")
            self.error_count += 1
            return False
    
    async def _process_events(self):
        """Background task to process system events"""
        while self.is_running:
            try:
                # Get event with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._handle_system_event(event)
                self.events_processed += 1
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                self.error_count += 1
    
    async def _handle_system_event(self, event: SystemEvent):
        """Handle a system event and apply world state changes"""
        try:
            # Apply automatic state changes
            if event.state_changes:
                for change in event.state_changes:
                    await self.world_state_service.set_state_variable(
                        key=change.get('key'),
                        value=change.get('value'),
                        region_id=change.get('region_id'),
                        category=StateCategory(change.get('category', 'other')),
                        reason=f"[{event.source_system.value}] {event.event_type}: {change.get('reason', '')}"
                    )
            
            # Call registered event handlers
            event_key = f"{event.source_system.value}.{event.event_type}"
            if event_key in self.event_handlers:
                for handler in self.event_handlers[event_key]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_key}: {e}")
            
            # Record the event in world state
            await self.world_state_service.record_world_event(
                event_type=f"{event.source_system.value}_{event.event_type}",
                description=f"System event from {event.source_system.value}: {event.event_type}",
                affected_regions=event.affected_regions or [],
                category=self._categorize_system_event(event.source_system),
                metadata={
                    "source_system": event.source_system.value,
                    "original_event_id": event.event_id,
                    "priority": event.priority,
                    **event.data
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to handle system event {event.event_id}: {e}")
            self.error_count += 1
    
    async def _propagate_state_change(self, request: StateChangeRequest):
        """Propagate state changes to interested systems"""
        try:
            # Find listeners for this state key
            relevant_listeners = []
            for pattern, listeners in self.state_change_listeners.items():
                if self._matches_pattern(request.key, pattern):
                    relevant_listeners.extend(listeners)
            
            # Notify listeners
            change_data = {
                "key": request.key,
                "value": request.value,
                "region_id": request.region_id,
                "category": request.category.value,
                "source_system": request.source_system.value,
                "reason": request.reason,
                "metadata": request.metadata or {}
            }
            
            for listener in relevant_listeners:
                try:
                    await listener(change_data)
                except Exception as e:
                    logger.error(f"Error in state change listener: {e}")
            
            self.state_changes_propagated += 1
            
        except Exception as e:
            logger.error(f"Failed to propagate state change: {e}")
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if a key matches a pattern (simple wildcard matching)"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return key.startswith(pattern[:-1])
        if pattern.startswith("*"):
            return key.endswith(pattern[1:])
        return key == pattern
    
    def _categorize_system_event(self, system_type: SystemType) -> StateCategory:
        """Categorize system events by their source system"""
        system_category_map = {
            SystemType.FACTION: StateCategory.POLITICAL,
            SystemType.DIPLOMACY: StateCategory.POLITICAL,
            SystemType.ECONOMY: StateCategory.ECONOMIC,
            SystemType.COMBAT: StateCategory.MILITARY,
            SystemType.TENSION: StateCategory.MILITARY,
            SystemType.POPULATION: StateCategory.SOCIAL,
            SystemType.RELIGION: StateCategory.RELIGIOUS,
            SystemType.MAGIC: StateCategory.MAGICAL,
            SystemType.WEATHER: StateCategory.ENVIRONMENTAL,
            SystemType.DISEASE: StateCategory.ENVIRONMENTAL,
            SystemType.QUEST: StateCategory.QUEST,
            SystemType.ARC: StateCategory.QUEST,
        }
        return system_category_map.get(system_type, StateCategory.OTHER)
    
    # === SPECIFIC SYSTEM INTEGRATIONS ===
    
    async def handle_faction_event(self, faction_id: str, event_type: str, data: Dict[str, Any]):
        """Handle faction system events"""
        event = SystemEvent(
            event_id=str(uuid4()),
            source_system=SystemType.FACTION,
            event_type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
            state_changes=[
                {
                    "key": f"faction.{faction_id}.last_activity",
                    "value": datetime.utcnow().isoformat(),
                    "category": "political",
                    "reason": f"Faction {event_type} event"
                }
            ]
        )
        await self.emit_system_event(event)
    
    async def handle_economy_event(self, region_id: str, event_type: str, data: Dict[str, Any]):
        """Handle economy system events"""
        event = SystemEvent(
            event_id=str(uuid4()),
            source_system=SystemType.ECONOMY,
            event_type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
            affected_regions=[region_id] if region_id else None,
            state_changes=[
                {
                    "key": f"economy.{region_id}.last_update" if region_id else "economy.global.last_update",
                    "value": datetime.utcnow().isoformat(),
                    "category": "economic",
                    "region_id": region_id,
                    "reason": f"Economy {event_type} event"
                }
            ]
        )
        await self.emit_system_event(event)
    
    async def handle_combat_event(self, participants: List[str], event_type: str, data: Dict[str, Any]):
        """Handle combat system events"""
        event = SystemEvent(
            event_id=str(uuid4()),
            source_system=SystemType.COMBAT,
            event_type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
            priority=8,  # High priority for combat events
            state_changes=[
                {
                    "key": "combat.recent_activity",
                    "value": datetime.utcnow().isoformat(),
                    "category": "military",
                    "reason": f"Combat {event_type} involving {len(participants)} participants"
                }
            ]
        )
        await self.emit_system_event(event)
    
    async def handle_quest_event(self, quest_id: str, event_type: str, data: Dict[str, Any]):
        """Handle quest system events"""
        event = SystemEvent(
            event_id=str(uuid4()),
            source_system=SystemType.QUEST,
            event_type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
            state_changes=[
                {
                    "key": f"quest.{quest_id}.status",
                    "value": data.get("status", "active"),
                    "category": "quest",
                    "reason": f"Quest {event_type} event"
                }
            ]
        )
        await self.emit_system_event(event)
    
    async def handle_time_tick(self, tick_data: Dict[str, Any]):
        """Handle time system tick events"""
        event = SystemEvent(
            event_id=str(uuid4()),
            source_system=SystemType.TIME,
            event_type="tick",
            data=tick_data,
            timestamp=datetime.utcnow(),
            priority=10,  # Highest priority for time ticks
            state_changes=[
                {
                    "key": "time.last_tick",
                    "value": datetime.utcnow().isoformat(),
                    "category": "other",
                    "reason": "Time system tick"
                },
                {
                    "key": "time.current_game_time",
                    "value": tick_data.get("game_time"),
                    "category": "other",
                    "reason": "Game time update"
                }
            ]
        )
        await self.emit_system_event(event)
    
    # === MONITORING AND METRICS ===
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get integration hub metrics"""
        return {
            "registered_systems": len(self.registered_systems),
            "system_list": [system.value for system in self.registered_systems],
            "event_handlers": len(self.event_handlers),
            "state_change_listeners": len(self.state_change_listeners),
            "events_processed": self.events_processed,
            "state_changes_propagated": self.state_changes_propagated,
            "error_count": self.error_count,
            "is_running": self.is_running,
            "queue_size": self.event_queue.qsize()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the integration hub"""
        return {
            "status": "healthy" if self.is_running and self.error_count < 10 else "unhealthy",
            "uptime": self.is_running,
            "processing_events": self.processing_task and not self.processing_task.done(),
            "recent_errors": self.error_count,
            "metrics": self.get_integration_metrics()
        }


# === CONVENIENCE FUNCTIONS ===

async def create_integration_hub(world_state_service: WorldStateService) -> SystemIntegrationHub:
    """Create and start an integration hub"""
    hub = SystemIntegrationHub(world_state_service)
    await hub.start()
    return hub


# === INTEGRATION DECORATORS ===

def world_state_integration(system_type: SystemType):
    """Decorator to automatically integrate functions with world state"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Execute the original function
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # TODO: Add automatic state change detection and propagation
            
            return result
        return wrapper
    return decorator 