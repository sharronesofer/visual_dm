"""
Event Batching Utilities
------------------------
Provides utilities for batching events and processing them efficiently.

This module implements the event batching functionality described in the 
Development Bible, allowing for more efficient processing of high-volume events.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Callable, Generic

from ..base import EventBase
from ..dispatcher import EventDispatcher

T = TypeVar('T', bound=EventBase)

logger = logging.getLogger(__name__)

class EventBatch(Generic[T]):
    """
    A batch of events of the same type for efficient processing.
    
    This class collects events of the same type for batch processing,
    reducing overhead for high-volume events that can be processed together.
    """
    
    def __init__(self, 
                event_type: Type[T],
                max_size: int = 100,
                max_wait_time: float = 0.5,
                processor: Optional[Callable[[List[T]], Any]] = None):
        """
        Initialize a new event batch.
        
        Args:
            event_type: The type of events this batch will collect
            max_size: Maximum number of events before auto-processing
            max_wait_time: Maximum time (seconds) to wait before processing
            processor: Optional custom batch processor function
        """
        self.event_type = event_type
        self.max_size = max_size
        self.max_wait_time = max_wait_time
        self.processor = processor
        
        self.events: List[T] = []
        self.last_processed: float = time.time()
        self._lock = asyncio.Lock()
        self._dispatcher = EventDispatcher.get_instance()
    
    async def add(self, event: T) -> bool:
        """
        Add an event to the batch.
        
        If the batch reaches max_size or max_wait_time, it will be automatically processed.
        
        Args:
            event: The event to add
            
        Returns:
            True if batch was processed, False otherwise
        """
        if not isinstance(event, self.event_type):
            raise TypeError(f"Expected event of type {self.event_type.__name__}, got {type(event).__name__}")
        
        processed = False
        async with self._lock:
            self.events.append(event)
            
            # Process if we've reached the max size
            if len(self.events) >= self.max_size:
                await self.process()
                processed = True
            
            # Process if we've waited too long
            elapsed = time.time() - self.last_processed
            if elapsed >= self.max_wait_time and self.events:
                await self.process()
                processed = True
                
        return processed
    
    async def process(self) -> None:
        """
        Process all events in the batch.
        
        If a custom processor is provided, it will be used.
        Otherwise, events will be dispatched individually.
        """
        async with self._lock:
            if not self.events:
                return
                
            events_to_process = self.events.copy()
            self.events.clear()
            self.last_processed = time.time()
        
        try:
            # Use custom processor if provided
            if self.processor:
                await asyncio.create_task(self.processor(events_to_process))
            else:
                # Default: dispatch events individually
                for event in events_to_process:
                    await self._dispatcher.dispatch(event)
                    
            logger.debug(f"Processed batch of {len(events_to_process)} {self.event_type.__name__} events")
        except Exception as e:
            logger.exception(f"Error processing event batch: {e}")


class EventBatcher:
    """
    Manages multiple event batches for different event types.
    
    This singleton provides a central point for batching events
    of different types, with custom configuration for each type.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'EventBatcher':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the event batcher."""
        if EventBatcher._instance is not None:
            raise RuntimeError("EventBatcher is a singleton. Use get_instance() instead.")
            
        self._batches: Dict[Type[EventBase], EventBatch] = {}
        self._lock = asyncio.Lock()
        self._dispatcher = EventDispatcher.get_instance()
        
        # Task that periodically processes batches that have reached their wait time
        self._processing_task = None
    
    async def start(self) -> None:
        """Start the background processing task."""
        if self._processing_task is None:
            self._processing_task = asyncio.create_task(self._processing_loop())
    
    async def stop(self) -> None:
        """Stop the background processing task and process all remaining events."""
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            self._processing_task = None
            
        # Process all remaining batches
        await self.process_all()
    
    async def _processing_loop(self) -> None:
        """Background task that processes batches periodically."""
        try:
            while True:
                await self.process_ready_batches()
                await asyncio.sleep(0.1)  # Check every 100ms
        except asyncio.CancelledError:
            # Task was cancelled, clean up
            logger.debug("Event batcher processing loop cancelled")
            raise
    
    def register_batch(self, 
                      event_type: Type[T], 
                      max_size: int = 100,
                      max_wait_time: float = 0.5,
                      processor: Optional[Callable[[List[T]], Any]] = None) -> None:
        """
        Register a new batch configuration for an event type.
        
        Args:
            event_type: The type of events to batch
            max_size: Maximum batch size before processing
            max_wait_time: Maximum wait time in seconds
            processor: Optional custom processor function
        """
        batch = EventBatch(event_type, max_size, max_wait_time, processor)
        self._batches[event_type] = batch
    
    def unregister_batch(self, event_type: Type[EventBase]) -> None:
        """
        Remove batch configuration for an event type.
        
        Args:
            event_type: The event type to unregister
        """
        if event_type in self._batches:
            del self._batches[event_type]
    
    async def add_event(self, event: EventBase) -> bool:
        """
        Add an event to its corresponding batch.
        
        If the event type isn't registered for batching,
        it will be dispatched immediately.
        
        Args:
            event: The event to add
            
        Returns:
            True if dispatched or batch was processed, False if batched
        """
        event_type = type(event)
        
        # If we don't have a batch for this type, dispatch immediately
        if event_type not in self._batches:
            await self._dispatcher.dispatch(event)
            return True
        
        # Add to the appropriate batch
        batch = self._batches[event_type]
        return await batch.add(event)
    
    async def process_batch(self, event_type: Type[EventBase]) -> None:
        """
        Process a specific batch immediately.
        
        Args:
            event_type: The type of batch to process
        """
        if event_type in self._batches:
            await self._batches[event_type].process()
    
    async def process_ready_batches(self) -> None:
        """Process all batches that have reached their wait time."""
        current_time = time.time()
        
        for event_type, batch in list(self._batches.items()):
            elapsed = current_time - batch.last_processed
            if elapsed >= batch.max_wait_time and batch.events:
                await batch.process()
    
    async def process_all(self) -> None:
        """Process all batches immediately."""
        for event_type, batch in list(self._batches.items()):
            await batch.process()
    
    def get_batch_sizes(self) -> Dict[str, int]:
        """
        Get the current size of all batches.
        
        Returns:
            Dictionary mapping event type names to current batch sizes
        """
        return {
            event_type.__name__: len(batch.events)
            for event_type, batch in self._batches.items()
        }


# Convenience functions to work with the singleton

async def register_batch(event_type: Type[T], 
                        max_size: int = 100,
                        max_wait_time: float = 0.5,
                        processor: Optional[Callable[[List[T]], Any]] = None) -> None:
    """
    Register a new batch configuration for an event type.
    
    Args:
        event_type: The type of events to batch
        max_size: Maximum batch size before processing
        max_wait_time: Maximum wait time in seconds
        processor: Optional custom processor function
    """
    batcher = EventBatcher.get_instance()
    batcher.register_batch(event_type, max_size, max_wait_time, processor)

async def add_event(event: EventBase) -> bool:
    """
    Add an event to its corresponding batch or dispatch it.
    
    Args:
        event: The event to add
        
    Returns:
        True if dispatched or batch was processed, False if batched
    """
    batcher = EventBatcher.get_instance()
    return await batcher.add_event(event)

async def start_batching() -> None:
    """Start the background processing task."""
    batcher = EventBatcher.get_instance()
    await batcher.start()

async def stop_batching() -> None:
    """Stop the background processing and process all remaining events."""
    batcher = EventBatcher.get_instance()
    await batcher.stop() 