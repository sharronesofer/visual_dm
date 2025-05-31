"""
Analytics Service Module

Provides comprehensive analytics functionality for the Visual DM system,
including event tracking, data storage, and LLM training dataset generation.
"""

import asyncio
import json
import logging
import os
import threading
import warnings
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from queue import Queue
import uuid


class AnalyticsEventType(Enum):
    """Canonical analytics event types defined by Development Bible."""
    
    # Core game events
    GAME_START = "GameStart"
    GAME_END = "GameEnd"
    
    # Domain-specific events  
    MEMORY_EVENT = "MemoryEvent"
    RUMOR_EVENT = "RumorEvent"
    MOTIF_EVENT = "MotifEvent"
    POPULATION_EVENT = "PopulationEvent"
    POI_STATE_EVENT = "POIStateEvent"
    FACTION_EVENT = "FactionEvent"
    QUEST_EVENT = "QuestEvent"
    COMBAT_EVENT = "CombatEvent"
    TIME_EVENT = "TimeEvent"
    STORAGE_EVENT = "StorageEvent"
    RELATIONSHIP_EVENT = "RelationshipEvent"
    WORLD_STATE_EVENT = "WorldStateEvent"
    
    # Flexible event type
    CUSTOM_EVENT = "CustomEvent"
    
    @classmethod
    def get_all(cls) -> List[str]:
        """Return all canonical event types."""
        return [event_type.value for event_type in cls]


class AnalyticsService:
    """
    Core analytics service for Visual DM.
    
    Implements singleton pattern with comprehensive event tracking,
    async processing, and LLM training dataset generation.
    """
    
    _instance: Optional['AnalyticsService'] = None
    _instance_lock = threading.Lock()
    _async_instance: Optional['AnalyticsService'] = None
    _async_lock = asyncio.Lock() if asyncio.iscoroutinefunction(lambda: None) else None
    
    def __init__(self, storage_path: Optional[Path] = None, test_mode: bool = False):
        """Initialize analytics service."""
        self.logger = logging.getLogger(__name__)
        self.test_mode = test_mode
        self._storage_path = storage_path or Path("backend/analytics_data")
        self._event_queue: Queue = Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._async_components_initialized = False
        
        # Ensure storage directory exists
        if not self.test_mode:
            self._storage_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_instance(cls, storage_path: Optional[Path] = None, test_mode: bool = False) -> 'AnalyticsService':
        """Get singleton instance (thread-safe)."""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls(storage_path=storage_path, test_mode=test_mode)
        return cls._instance
    
    @classmethod
    async def get_instance_async(cls, storage_path: Optional[Path] = None, test_mode: bool = False) -> 'AnalyticsService':
        """Get singleton instance (async, coroutine-safe)."""
        if cls._async_instance is None:
            # Simulate async lock behavior
            if cls._async_instance is None:
                cls._async_instance = cls(storage_path=storage_path, test_mode=test_mode)
                await cls._async_instance._ensure_async_components()
        return cls._async_instance
    
    @property
    def storage_path(self) -> Path:
        """Get storage path."""
        return self._storage_path
    
    @storage_path.setter
    def storage_path(self, path: Path) -> None:
        """Set storage path."""
        self._storage_path = path
        if not self.test_mode:
            self._storage_path.mkdir(parents=True, exist_ok=True)
    
    async def _ensure_async_components(self) -> None:
        """Ensure async components are initialized."""
        if not self._async_components_initialized:
            # Start background worker if not in test mode
            if not self.test_mode and self._worker_thread is None:
                self._worker_thread = threading.Thread(
                    target=self._process_event_queue,
                    daemon=True
                )
                self._worker_thread.start()
            self._async_components_initialized = True
    
    def log_event(self, event_type: Union[str, AnalyticsEventType], entity_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log an analytics event (synchronous)."""
        # Validate event type and warn if non-canonical
        if isinstance(event_type, str) and not event_type.startswith("Custom_"):
            canonical_types = AnalyticsEventType.get_all()
            if event_type not in canonical_types:
                warnings.warn(f"Non-canonical event type: {event_type}")
        
        # Convert enum to string
        if isinstance(event_type, AnalyticsEventType):
            event_type = event_type.value
        
        # Store event
        self._store_event_sync(event_type, entity_id, metadata or {})
    
    async def log_event_async(self, event_type: Union[str, AnalyticsEventType], entity_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log an analytics event (asynchronous)."""
        await self._ensure_async_components()
        
        # Convert enum to string
        if isinstance(event_type, AnalyticsEventType):
            event_type = event_type.value
        
        await self._store_event(event_type, entity_id, metadata or {})
    
    def queue_track_event(self, event_type: Union[str, AnalyticsEventType], entity_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Queue an event for background processing."""
        if isinstance(event_type, AnalyticsEventType):
            event_type = event_type.value
        
        event_data = {
            'event_type': event_type,
            'entity_id': entity_id,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self._event_queue.put(event_data)
    
    def register_with_dispatcher(self, dispatcher) -> None:
        """Register analytics service with the event dispatcher."""
        # Create analytics middleware and register it
        middleware = self.get_analytics_middleware()
        if hasattr(dispatcher, 'add_middleware'):
            dispatcher.add_middleware(middleware)
        elif hasattr(dispatcher, 'register_middleware'):
            dispatcher.register_middleware(middleware)
    
    def get_analytics_middleware(self):
        """Create analytics middleware for event dispatcher integration."""
        try:
            from backend.infrastructure.events import EventMiddleware
        except ImportError:
            # Fallback if events system not available
            class EventMiddleware:
                async def process(self, event) -> None:
                    pass
        
        class AnalyticsEventMiddleware(EventMiddleware):
            def __init__(self, analytics_service: 'AnalyticsService'):
                self.analytics_service = analytics_service
            
            async def process_async(self, event) -> None:
                """Process events through analytics service asynchronously."""
                try:
                    event_type = self.analytics_service._map_event_to_analytics_type(event)
                    entity_id = getattr(event, 'entity_id', str(uuid.uuid4()))
                    metadata = getattr(event, 'metadata', {})
                    
                    await self.analytics_service.log_event_async(
                        event_type=event_type,
                        entity_id=entity_id,
                        metadata=metadata
                    )
                except Exception as e:
                    self.analytics_service.logger.error(f"Error in analytics middleware: {e}")
                
                return event
            
            def process_sync(self, event) -> None:
                """Process events through analytics service synchronously."""
                try:
                    event_type = self.analytics_service._map_event_to_analytics_type(event)
                    entity_id = getattr(event, 'entity_id', str(uuid.uuid4()))
                    metadata = getattr(event, 'metadata', {})
                    
                    self.analytics_service.log_event(
                        event_type=event_type,
                        entity_id=entity_id,
                        metadata=metadata
                    )
                except Exception as e:
                    self.analytics_service.logger.error(f"Error in analytics middleware: {e}")
                
                return event
            
            async def process(self, event) -> None:
                """Process events through analytics service."""
                return await self.process_async(event)
        
        return AnalyticsEventMiddleware(self)
    
    def _map_event_to_analytics_type(self, event) -> AnalyticsEventType:
        """Map events to canonical analytics types."""
        event_name = type(event).__name__
        
        # Direct name mappings
        name_mappings = {
            "GameInitialized": AnalyticsEventType.GAME_START,
            "GameEnded": AnalyticsEventType.GAME_END,
            "MemoryCreated": AnalyticsEventType.MEMORY_EVENT,
            "MemoryUpdated": AnalyticsEventType.MEMORY_EVENT,
            "MemoryDeleted": AnalyticsEventType.MEMORY_EVENT,
            "MemoryRecalled": AnalyticsEventType.MEMORY_EVENT,
            "RumorCreated": AnalyticsEventType.RUMOR_EVENT,
            "RumorSpread": AnalyticsEventType.RUMOR_EVENT,
            "RumorUpdated": AnalyticsEventType.RUMOR_EVENT,
            "NarrativeMotifIntroduced": AnalyticsEventType.MOTIF_EVENT,
            "FactionCreated": AnalyticsEventType.FACTION_EVENT,
            "FactionUpdated": AnalyticsEventType.FACTION_EVENT,
            "FactionRelationshipChanged": AnalyticsEventType.FACTION_EVENT,
            "CharacterRelationshipChanged": AnalyticsEventType.RELATIONSHIP_EVENT,
            "GameSaved": AnalyticsEventType.STORAGE_EVENT,
            "GameLoaded": AnalyticsEventType.STORAGE_EVENT,
        }
        
        if event_name in name_mappings:
            return name_mappings[event_name]
        
        # Import event types dynamically to avoid circular imports
        try:
            from backend.infrastructure.events import (
                MemoryEvent, RumorEvent, FactionEvent, CharacterEvent,
                NarrativeEvent, GameEvent, SystemEvent
            )
            
            # Check by base class
            if isinstance(event, MemoryEvent):
                return AnalyticsEventType.MEMORY_EVENT
            elif isinstance(event, RumorEvent):
                return AnalyticsEventType.RUMOR_EVENT
            elif isinstance(event, FactionEvent):
                return AnalyticsEventType.FACTION_EVENT
            elif isinstance(event, CharacterEvent):
                # Check if it's a relationship event
                if hasattr(event, 'relationship'):
                    return AnalyticsEventType.RELATIONSHIP_EVENT
                return AnalyticsEventType.CUSTOM_EVENT
            elif isinstance(event, NarrativeEvent):
                # Check for specific narrative event types
                if hasattr(event, 'is_motif_event') and event.is_motif_event:
                    return AnalyticsEventType.MOTIF_EVENT
                elif hasattr(event, 'is_quest_event') and event.is_quest_event:
                    return AnalyticsEventType.QUEST_EVENT
                return AnalyticsEventType.CUSTOM_EVENT
        except ImportError:
            pass
        
        # Default fallback
        return AnalyticsEventType.CUSTOM_EVENT
    
    def _process_event_queue(self) -> None:
        """Background worker to process queued events."""
        while not self._shutdown_event.is_set():
            try:
                if not self._event_queue.empty():
                    event_data = self._event_queue.get(timeout=1)
                    self._store_event_sync(
                        event_data['event_type'],
                        event_data['entity_id'],
                        event_data['metadata']
                    )
                    self._event_queue.task_done()
                else:
                    # Sleep briefly to avoid busy waiting
                    self._shutdown_event.wait(0.1)
            except Exception as e:
                self.logger.error(f"Error processing event queue: {e}")
    
    async def _store_event(self, event_type: str, entity_id: str, metadata: Dict[str, Any]) -> None:
        """Store event asynchronously."""
        # For async version, delegate to sync method
        self._store_event_sync(event_type, entity_id, metadata)
    
    def _store_event_sync(self, event_type: str, entity_id: str, metadata: Dict[str, Any]) -> None:
        """Store event synchronously."""
        if self.test_mode:
            # In test mode, just log the event
            self.logger.debug(f"Test mode: storing event {event_type} for entity {entity_id}")
            return
        
        try:
            # Get the file path for this event
            event_file = self._get_event_file_path(event_type)
            
            # Ensure directory exists
            event_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create event record
            event_record = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'entity_id': entity_id,
                'metadata': metadata
            }
            
            # Append to JSONL file
            with open(event_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event_record) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to store event: {e}")
    
    def _get_event_file_path(self, event_type: str) -> Path:
        """Get the file path for storing an event type."""
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        
        return self._storage_path / year / month / day / f"{event_type}.jsonl"
    
    def generate_dataset(self) -> List[Dict[str, Any]]:
        """Generate LLM training dataset from stored events (synchronous)."""
        return self._generate_dataset_sync()
    
    async def generate_dataset_async(self) -> List[Dict[str, Any]]:
        """Generate LLM training dataset from stored events (asynchronous)."""
        return self._generate_dataset_sync()
    
    def _generate_dataset_sync(self) -> List[Dict[str, Any]]:
        """Generate dataset synchronously."""
        dataset = []
        
        if self.test_mode:
            # Return mock dataset for testing
            return [{"test": "data"}]
        
        try:
            # Traverse storage directory and collect events
            for event_file in self._storage_path.rglob("*.jsonl"):
                with open(event_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())
                            dataset.append(event_data)
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            self.logger.error(f"Failed to generate dataset: {e}")
        
        return dataset
    
    def stop_worker(self) -> None:
        """Stop the background worker thread."""
        self._shutdown_event.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5)


def get_analytics_service(storage_path: Optional[Path] = None, test_mode: bool = False) -> AnalyticsService:
    """Factory function to get analytics service instance."""
    return AnalyticsService.get_instance(storage_path=storage_path, test_mode=test_mode) 