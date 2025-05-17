"""
Central event bus system for event-based communication between components.

This implements a publisher-subscriber pattern with thread safety 
for reliable event distribution across the application.
"""

import logging
import time
import threading
from enum import Enum
from typing import Dict, List, Set, Callable, Any, TypeVar, Generic, Optional, Union
from dataclasses import dataclass
from queue import Queue, Empty
from threading import Thread, Lock, Event
from .scene_events import SceneEvent, SceneEventType

logger = logging.getLogger(__name__)

# Define a generic type for events
T = TypeVar('T')

class EventPriority(Enum):
    """Priority levels for event processing."""
    HIGH = 0
    NORMAL = 1
    LOW = 2
    BACKGROUND = 3

@dataclass
class EventSubscription(Generic[T]):
    """Represents a subscription to an event."""
    callback: Callable[[T], None]
    priority: EventPriority = EventPriority.NORMAL
    filter_func: Optional[Callable[[T], bool]] = None
    max_frequency: Optional[float] = None  # Max frequency in events per second (None for unlimited)
    last_called: float = 0.0  # Timestamp of last call for frequency limiting
    
    def should_trigger(self, event: T) -> bool:
        """Check if the event should trigger this subscription.
        
        Args:
            event: The event to check
            
        Returns:
            bool: True if the callback should be called
        """
        # Check filter first
        if self.filter_func and not self.filter_func(event):
            return False
            
        # Check frequency limit
        if self.max_frequency is not None:
            now = time.time()
            min_interval = 1.0 / self.max_frequency
            if now - self.last_called < min_interval:
                return False
                
        return True
        
    def trigger(self, event: T) -> None:
        """Trigger the subscription with the event.
        
        Args:
            event: Event to pass to the callback
        """
        try:
            self.callback(event)
            self.last_called = time.time()
        except Exception as e:
            logger.error(f"Error in event handler: {e}", exc_info=True)


class EventBus:
    """Central event bus for publisher-subscriber communication."""
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the EventBus.
        
        Returns:
            EventBus: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the event bus (use get_instance() instead)."""
        self.subscribers: Dict[Any, List[EventSubscription]] = {}
        self.lock = Lock()
        self.queue: Queue = Queue()
        self.worker_thread: Optional[Thread] = None
        self.running = False
        self.stop_event = Event()
        
        # Set of event types that are currently being processed
        # Used to detect cycles
        self.active_events: Set[Any] = set()
        
        # Event counters for monitoring
        self.event_counts: Dict[Any, int] = {}
        self.handler_counts: Dict[Any, int] = {}
        
        # Start worker thread
        self._start_worker()
        
    def _start_worker(self) -> None:
        """Start the worker thread for processing events."""
        if self.worker_thread is not None and self.worker_thread.is_alive():
            return
            
        self.running = True
        self.stop_event.clear()
        self.worker_thread = Thread(target=self._process_events, daemon=True)
        self.worker_thread.start()
        
    def _process_events(self) -> None:
        """Process events from the queue continuously."""
        while not self.stop_event.is_set():
            try:
                event_type, event = self.queue.get(timeout=0.1)
                
                # Skip if we detect a cycle
                if event_type in self.active_events:
                    logger.warning(f"Event cycle detected for {event_type}, skipping")
                    self.queue.task_done()
                    continue
                    
                # Mark event as being processed
                self.active_events.add(event_type)
                
                # Get subscribers for this event type
                with self.lock:
                    if event_type in self.subscribers:
                        # Sort by priority (lower value = higher priority)
                        handlers = sorted(
                            self.subscribers[event_type],
                            key=lambda s: s.priority.value
                        )
                    else:
                        handlers = []
                
                # Process all handlers
                for handler in handlers:
                    if handler.should_trigger(event):
                        handler.trigger(event)
                        
                        # Update monitoring stats
                        with self.lock:
                            if event_type in self.handler_counts:
                                self.handler_counts[event_type] += 1
                            else:
                                self.handler_counts[event_type] = 1
                
                # Remove from active set
                self.active_events.remove(event_type)
                
                # Mark as done
                self.queue.task_done()
                
            except Empty:
                # Just a timeout, continue
                pass
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)
                
    def subscribe(
        self,
        event_type: Any,
        callback: Callable[[Any], None],
        priority: EventPriority = EventPriority.NORMAL,
        filter_func: Optional[Callable[[Any], bool]] = None,
        max_frequency: Optional[float] = None
    ) -> None:
        """Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
            priority: Priority level for processing
            filter_func: Optional function to filter events
            max_frequency: Max frequency in events per second (None for unlimited)
        """
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
                
            subscription = EventSubscription(
                callback=callback,
                priority=priority,
                filter_func=filter_func,
                max_frequency=max_frequency
            )
            
            self.subscribers[event_type].append(subscription)
            logger.debug(f"Subscribed to {event_type} with priority {priority}")
            
    def unsubscribe(self, event_type: Any, callback: Callable[[Any], None]) -> bool:
        """Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            bool: True if unsubscribed, False if not found
        """
        with self.lock:
            if event_type not in self.subscribers:
                return False
                
            original_count = len(self.subscribers[event_type])
            self.subscribers[event_type] = [
                s for s in self.subscribers[event_type] 
                if s.callback != callback
            ]
            
            # If we removed something, return True
            return len(self.subscribers[event_type]) < original_count
            
    def publish(self, event_type: Any, event: Any) -> None:
        """Publish an event to all subscribers.
        
        Args:
            event_type: Type of event
            event: Event object to publish
        """
        # Update monitoring stats
        with self.lock:
            if event_type in self.event_counts:
                self.event_counts[event_type] += 1
            else:
                self.event_counts[event_type] = 1
        
        # Add to queue for processing
        self.queue.put((event_type, event))
        
    def publish_immediate(self, event_type: Any, event: Any) -> None:
        """Publish an event immediately without queuing.
        
        This is useful for events that must be processed synchronously.
        Warning: This blocks the calling thread.
        
        Args:
            event_type: Type of event
            event: Event object to publish
        """
        # Update monitoring stats
        with self.lock:
            if event_type in self.event_counts:
                self.event_counts[event_type] += 1
            else:
                self.event_counts[event_type] = 1
                
            if event_type in self.subscribers:
                handlers = sorted(
                    self.subscribers[event_type],
                    key=lambda s: s.priority.value
                )
            else:
                handlers = []
                
        # Process all handlers
        for handler in handlers:
            if handler.should_trigger(event):
                handler.trigger(event)
                
                # Update monitoring stats
                with self.lock:
                    if event_type in self.handler_counts:
                        self.handler_counts[event_type] += 1
                    else:
                        self.handler_counts[event_type] = 1
                        
    def stop(self) -> None:
        """Stop the event bus and worker thread."""
        self.stop_event.set()
        if self.worker_thread:
            self.worker_thread.join(timeout=1.0)
        self.running = False
        
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about event processing.
        
        Returns:
            Dict[str, Any]: Event bus statistics
        """
        with self.lock:
            stats = {
                "event_counts": dict(self.event_counts),
                "handler_counts": dict(self.handler_counts),
                "subscriber_counts": {
                    event_type: len(handlers)
                    for event_type, handlers in self.subscribers.items()
                },
                "queue_size": self.queue.qsize()
            }
            
        return stats
        
    def clear_stats(self) -> None:
        """Clear event statistics."""
        with self.lock:
            self.event_counts.clear()
            self.handler_counts.clear()
            
    def get_subscriber_count(self, event_type: Any) -> int:
        """Get number of subscribers for an event type.
        
        Args:
            event_type: Event type to check
            
        Returns:
            int: Number of subscribers
        """
        with self.lock:
            if event_type not in self.subscribers:
                return 0
            return len(self.subscribers[event_type])
            
    def wait_for_empty_queue(self, timeout: Optional[float] = None) -> bool:
        """Wait for the event queue to empty.
        
        Args:
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            bool: True if queue emptied, False if timed out
        """
        try:
            self.queue.join(timeout=timeout)
            return True
        except:
            return False 