"""
Event management system for handling pygame events.
"""

import pygame
import logging
from typing import Dict, List, Callable, Any
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

class EventManager:
    """Manages event handling and distribution."""
    
    def __init__(self):
        """Initialize the event manager."""
        self.event_handlers: Dict[int, List[Callable]] = {}
        self.screen_handlers: List[Callable] = []
        
    def register_handler(self, event_type: int, handler: Callable) -> None:
        """Register an event handler for a specific event type.
        
        Args:
            event_type: Pygame event type
            handler: Function to handle the event
        """
        try:
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
                
            self.event_handlers[event_type].append(handler)
            logger.debug(f"Registered handler for event type: {event_type}")
            
        except Exception as e:
            handle_component_error(
                "EventManager",
                "register_handler",
                e,
                ErrorSeverity.ERROR,
                {"event_type": event_type}
            )
            
    def register_screen_handler(self, handler: Callable) -> None:
        """Register a screen-level event handler.
        
        Args:
            handler: Function to handle screen events
        """
        try:
            self.screen_handlers.append(handler)
            logger.debug("Registered screen event handler")
            
        except Exception as e:
            handle_component_error(
                "EventManager",
                "register_screen_handler",
                e,
                ErrorSeverity.ERROR
            )
            
    def unregister_handler(self, event_type: int, handler: Callable) -> None:
        """Unregister an event handler.
        
        Args:
            event_type: Pygame event type
            handler: Function to remove
        """
        try:
            if event_type in self.event_handlers:
                self.event_handlers[event_type].remove(handler)
                logger.debug(f"Unregistered handler for event type: {event_type}")
                
        except Exception as e:
            handle_component_error(
                "EventManager",
                "unregister_handler",
                e,
                ErrorSeverity.ERROR,
                {"event_type": event_type}
            )
            
    def unregister_screen_handler(self, handler: Callable) -> None:
        """Unregister a screen-level event handler.
        
        Args:
            handler: Function to remove
        """
        try:
            self.screen_handlers.remove(handler)
            logger.debug("Unregistered screen event handler")
            
        except Exception as e:
            handle_component_error(
                "EventManager",
                "unregister_screen_handler",
                e,
                ErrorSeverity.ERROR
            )
            
    def process_event(self, event: pygame.event.Event) -> None:
        """Process a pygame event.
        
        Args:
            event: Pygame event to process
        """
        try:
            # Process specific event handlers
            if event.type in self.event_handlers:
                for handler in self.event_handlers[event.type]:
                    handler(event)
                    
            # Process screen handlers
            for handler in self.screen_handlers:
                handler(event)
                
        except Exception as e:
            handle_component_error(
                "EventManager",
                "process_event",
                e,
                ErrorSeverity.ERROR,
                {"event": str(event)}
            )
            
    def clear_handlers(self) -> None:
        """Clear all registered event handlers."""
        try:
            self.event_handlers.clear()
            self.screen_handlers.clear()
            logger.debug("Cleared all event handlers")
            
        except Exception as e:
            handle_component_error(
                "EventManager",
                "clear_handlers",
                e,
                ErrorSeverity.ERROR
            ) 