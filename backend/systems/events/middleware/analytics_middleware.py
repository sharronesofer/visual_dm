"""
Analytics middleware for the event system.

This middleware captures events for analytics purposes, enabling
metrics tracking, reporting, and LLM training data collection.
"""
import logging
from typing import Any, Callable, Dict, Optional
import time
import json
import os
from pathlib import Path

from ..core.event_base import EventBase

logger = logging.getLogger('events.analytics')

class AnalyticsConfig:
    """Configuration for analytics middleware."""
    ENABLED = True
    STORAGE_PATH = os.environ.get('ANALYTICS_STORAGE_PATH', 'data/analytics')
    BATCH_SIZE = int(os.environ.get('ANALYTICS_BATCH_SIZE', '100'))
    SESSION_ID = f"session_{int(time.time())}"

class _AnalyticsCollector:
    """
    Internal class for collecting and storing analytics events.
    
    This is a singleton that manages batched writes of events to disk.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_AnalyticsCollector, cls).__new__(cls)
            cls._instance._events = []
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Set up storage directory if it doesn't exist."""
        if AnalyticsConfig.ENABLED:
            storage_path = Path(AnalyticsConfig.STORAGE_PATH)
            storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Analytics collector initialized with storage path: {storage_path}")
    
    def collect(self, event: EventBase, metadata: Optional[Dict] = None) -> None:
        """
        Collect an event for analytics.
        
        Args:
            event: The event to collect
            metadata: Additional metadata to include
        """
        if not AnalyticsConfig.ENABLED:
            return
            
        # Create event record with metadata
        record = {
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "session_id": AnalyticsConfig.SESSION_ID,
            "payload": json.loads(event.json(exclude_none=True))
        }
        
        if metadata:
            record["metadata"] = metadata
            
        self._events.append(record)
        
        # Flush to disk if batch size reached
        if len(self._events) >= AnalyticsConfig.BATCH_SIZE:
            self.flush()
    
    def flush(self) -> None:
        """Flush collected events to disk."""
        if not self._events or not AnalyticsConfig.ENABLED:
            return
            
        try:
            # Use ISO-format date as filename
            today = time.strftime("%Y-%m-%d")
            filename = f"{today}_events_{int(time.time())}.jsonl"
            filepath = Path(AnalyticsConfig.STORAGE_PATH) / filename
            
            with open(filepath, 'a') as f:
                for event in self._events:
                    f.write(json.dumps(event) + '\n')
                    
            logger.debug(f"Flushed {len(self._events)} events to {filepath}")
            self._events = []
        except Exception as e:
            logger.error(f"Error flushing analytics events: {str(e)}")

async def analytics_middleware(event: EventBase, next_middleware: Callable[[EventBase], Any]) -> Any:
    """
    Middleware that captures events for analytics purposes.
    
    Args:
        event: The event being dispatched
        next_middleware: The next middleware in the chain
        
    Returns:
        The result from the next middleware
    """
    # Collect the event in the analytics system
    collector = _AnalyticsCollector()
    collector.collect(event)
    
    # Continue processing the event
    return await next_middleware(event) 