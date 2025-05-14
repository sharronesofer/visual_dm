"""
WebSocket management system for real-time communication.
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, Any, Optional, Callable, List
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and real-time communication."""
    
    def __init__(
        self,
        uri: str = "ws://localhost:8000/ws",
        reconnect_interval: int = 5,
        max_retries: int = 3
    ):
        """Initialize the WebSocket manager.
        
        Args:
            uri: WebSocket server URI
            reconnect_interval: Reconnection interval in seconds
            max_retries: Maximum number of reconnection attempts
        """
        try:
            self.uri = uri
            self.reconnect_interval = reconnect_interval
            self.max_retries = max_retries
            
            self.websocket = None
            self.connected = False
            self.handlers: Dict[str, List[Callable]] = {}
            self.retry_count = 0
            
            logger.info("WebSocket manager initialized")
            
        except Exception as e:
            handle_component_error(
                "WebSocketManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    async def connect(self) -> None:
        """Connect to WebSocket server."""
        try:
            if self.connected:
                return
                
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            self.retry_count = 0
            
            logger.info("Connected to WebSocket server")
            
        except Exception as e:
            handle_component_error(
                "WebSocketManager",
                "connect",
                e,
                ErrorSeverity.ERROR
            )
            await self._handle_connection_error()
            
    async def _handle_connection_error(self) -> None:
        """Handle connection errors and attempt reconnection."""
        try:
            self.connected = False
            self.retry_count += 1
            
            if self.retry_count <= self.max_retries:
                logger.warning(
                    f"Connection failed. Retrying in {self.reconnect_interval} seconds... "
                    f"(Attempt {self.retry_count}/{self.max_retries})"
                )
                await asyncio.sleep(self.reconnect_interval)
                await self.connect()
            else:
                logger.error("Maximum reconnection attempts reached")
                
        except Exception as e:
            handle_component_error(
                "WebSocketManager",
                "_handle_connection_error",
                e,
                ErrorSeverity.ERROR
            )
            
    async def send_message(self, message_type: str, data: Dict[str, Any]) -> None:
        """Send a message through WebSocket.
        
        Args:
            message_type: Type of message
            data: Message data
        """
        try:
            if not self.connected:
                await self.connect()
                
            message = {
                "type": message_type,
                "data": data
            }
            
            await self.websocket.send(json.dumps(message))
            
            logger.debug(f"Sent message: {message_type}")
            
        except Exception as e:
            handle_component_error(
                "WebSocketManager",
                "send_message",
                e,
                ErrorSeverity.ERROR,
                {"message_type": message_type}
            )
            await self._handle_connection_error()
            
    async def listen(self) -> None:
        """Listen for incoming WebSocket messages."""
        try:
            while True:
                if not self.connected:
                    await self.connect()
                    
                try:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    
                    # Process message
                    await self._process_message(data)
                    
                except websockets.ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    await self._handle_connection_error()
                    
        except Exception as e:
            handle_component_error(
                "WebSocketManager",
                "listen",
                e,
                ErrorSeverity.ERROR
            )
            
    async def _process_message(self, message: Dict[str, Any]) -> None:
        """Process incoming WebSocket message.
        
        Args:
            message: Received message
        """
        try:
            message_type = message.get("type")
            data = message.get("data", {})
            
            if message_type in self.handlers:
                for handler in self.handlers[message_type]:
                    try:
                        await handler(data)
                    except Exception as e:
                        handle_component_error(
                            "WebSocketManager",
                            "_process_message",
                            e,
                            ErrorSeverity.ERROR,
                            {"message_type": message_type}
                        )
                        
            logger.debug(f"Processed message: {message_type}")
            
        except Exception as e:
            handle_component_error(
                "WebSocketManager",
                "_process_message",
                e,
                ErrorSeverity.ERROR
            )
            
    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Register a message handler.
        
        Args:
            message_type: Type of message to handle
            handler: Handler function
        """
        try:
            if message_type not in self.handlers:
                self.handlers[message_type] = []
                
            self.handlers[message_type].append(handler)
            
            logger.debug(f"Registered handler for: {message_type}")
            
        except Exception as e:
            handle_component_error(
                "WebSocketManager",
                "register_handler",
                e,
                ErrorSeverity.ERROR,
                {"message_type": message_type}
            )
            
    def unregister_handler(self, message_type: str, handler: Callable) -> None:
        """Unregister a message handler.
        
        Args:
            message_type: Type of message
            handler: Handler function to remove
        """
        try:
            if message_type in self.handlers:
                self.handlers[message_type].remove(handler)
                
                if not self.handlers[message_type]:
                    del self.handlers[message_type]
                    
            logger.debug(f"Unregistered handler for: {message_type}")
            
        except Exception as e:
            handle_component_error(
                "WebSocketManager",
                "unregister_handler",
                e,
                ErrorSeverity.ERROR,
                {"message_type": message_type}
            )
            
    async def cleanup(self) -> None:
        """Clean up WebSocket resources."""
        try:
            if self.websocket:
                await self.websocket.close()
                
            self.connected = False
            self.handlers.clear()
            
            logger.info("WebSocket manager cleaned up")
            
        except Exception as e:
            handle_component_error(
                "WebSocketManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 