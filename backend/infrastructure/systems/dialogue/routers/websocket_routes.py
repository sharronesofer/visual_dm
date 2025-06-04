"""
Dialogue System WebSocket Routes

This module implements the WebSocket infrastructure for the dialogue system,
providing real-time communication for conversations and NPC interactions
according to the Development Bible architecture.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter
from starlette.websockets import WebSocketState

# Import business logic services (proper separation)
from backend.systems.dialogue.services import (
    create_dialogue_service,
    create_dialogue_websocket_service,
    DialogueService,
    DialogueWebSocketService
)
from backend.infrastructure.dialogue_services.validation_service import (
    create_dialogue_validation_service,
    ConversationValidationError,
    MessageValidationError,
    NPCValidationError
)
from backend.infrastructure.utils.error_handling import (
    create_error_response,
    log_error_with_context
)

# Set up logging
logger = logging.getLogger(__name__)

# Create router instance
websocket_router = APIRouter(prefix="/dialogue", tags=["dialogue-websocket"])

# Global connection manager
class DialogueConnectionManager:
    """Manages WebSocket connections for the dialogue system"""
    
    def __init__(self):
        """Initialize connection manager"""
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.conversation_subscriptions: Dict[str, List[str]] = {}  # conversation_id -> [connection_ids]
        self.dialogue_service: Optional[DialogueService] = None
        self.websocket_service: Optional[DialogueWebSocketService] = None
        
    async def initialize_services(self):
        """Initialize business logic services"""
        if self.dialogue_service is None:
            self.dialogue_service = create_dialogue_service()
            
        if self.websocket_service is None:
            self.websocket_service = create_dialogue_websocket_service(self.dialogue_service)
    
    async def connect(self, websocket: WebSocket, connection_id: str) -> bool:
        """Accept WebSocket connection and register it"""
        try:
            await websocket.accept()
            
            # Initialize services if needed
            await self.initialize_services()
            
            self.active_connections[connection_id] = {
                'websocket': websocket,
                'connected_at': datetime.utcnow(),
                'conversation_ids': [],
                'last_activity': datetime.utcnow(),
                'client_info': {}
            }
            
            logger.info(f"WebSocket connection established: {connection_id}")
            
            # Send connection status message
            await self.send_to_connection(connection_id, {
                'type': 'dialogue_general_connection_status',
                'payload': {
                    'message': 'Connected to dialogue system successfully',
                    'connection_id': connection_id,
                    'server_time': datetime.utcnow().isoformat()
                },
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error accepting WebSocket connection {connection_id}: {str(e)}")
            return False
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection and clean up subscriptions"""
        try:
            if connection_id in self.active_connections:
                connection_data = self.active_connections[connection_id]
                
                # Clean up conversation subscriptions
                for conversation_id in connection_data.get('conversation_ids', []):
                    self.unsubscribe_from_conversation(connection_id, conversation_id)
                
                # Remove connection
                del self.active_connections[connection_id]
                logger.info(f"WebSocket connection disconnected: {connection_id}")
                
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket {connection_id}: {str(e)}")
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific connection"""
        try:
            if connection_id not in self.active_connections:
                logger.warning(f"Attempted to send message to non-existent connection: {connection_id}")
                return False
            
            connection = self.active_connections[connection_id]
            websocket = connection['websocket']
            
            # Check if connection is still active
            if websocket.client_state != WebSocketState.CONNECTED:
                logger.warning(f"WebSocket connection {connection_id} is not in connected state")
                self.disconnect(connection_id)
                return False
            
            # Update last activity
            connection['last_activity'] = datetime.utcnow()
            
            # Send message
            await websocket.send_text(json.dumps(message))
            logger.debug(f"Message sent to connection {connection_id}: {message['type']}")
            return True
            
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected during send: {connection_id}")
            self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.error(f"Error sending message to connection {connection_id}: {str(e)}")
            self.disconnect(connection_id)
            return False
    
    async def send_to_conversation(self, conversation_id: str, message: Dict[str, Any], exclude_connection: Optional[str] = None):
        """Send message to all connections subscribed to a conversation"""
        if conversation_id not in self.conversation_subscriptions:
            return
        
        connection_ids = self.conversation_subscriptions[conversation_id].copy()
        for connection_id in connection_ids:
            if exclude_connection and connection_id == exclude_connection:
                continue
                
            success = await self.send_to_connection(connection_id, message)
            if not success:
                # Clean up failed connection
                self.unsubscribe_from_conversation(connection_id, conversation_id)
    
    def subscribe_to_conversation(self, connection_id: str, conversation_id: str):
        """Subscribe connection to conversation updates"""
        if conversation_id not in self.conversation_subscriptions:
            self.conversation_subscriptions[conversation_id] = []
        
        if connection_id not in self.conversation_subscriptions[conversation_id]:
            self.conversation_subscriptions[conversation_id].append(connection_id)
        
        if connection_id in self.active_connections:
            connection_data = self.active_connections[connection_id]
            if conversation_id not in connection_data['conversation_ids']:
                connection_data['conversation_ids'].append(conversation_id)
        
        logger.debug(f"Connection {connection_id} subscribed to conversation {conversation_id}")
    
    def unsubscribe_from_conversation(self, connection_id: str, conversation_id: str):
        """Unsubscribe connection from conversation updates"""
        if conversation_id in self.conversation_subscriptions:
            if connection_id in self.conversation_subscriptions[conversation_id]:
                self.conversation_subscriptions[conversation_id].remove(connection_id)
            
            # Clean up empty subscription lists
            if not self.conversation_subscriptions[conversation_id]:
                del self.conversation_subscriptions[conversation_id]
        
        if connection_id in self.active_connections:
            connection_data = self.active_connections[connection_id]
            if conversation_id in connection_data['conversation_ids']:
                connection_data['conversation_ids'].remove(conversation_id)
        
        logger.debug(f"Connection {connection_id} unsubscribed from conversation {conversation_id}")
    
    async def handle_message(self, connection_id: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming WebSocket message"""
        try:
            # Ensure services are initialized
            await self.initialize_services()
            
            # Process through business logic service
            response = await self.websocket_service.handle_websocket_message(message, connection_id)
            
            # Handle conversation subscriptions
            if message.get('type') == 'dialogue_conversation_start':
                conversation_id = message.get('payload', {}).get('conversation_id')
                if conversation_id:
                    self.subscribe_to_conversation(connection_id, conversation_id)
            
            # Send response back to originating connection
            if response:
                await self.send_to_connection(connection_id, response)
                
                # Broadcast to conversation if applicable
                if response.get('type') in ['dialogue_response_ready', 'dialogue_bartering_update']:
                    conversation_id = response.get('payload', {}).get('conversation_id')
                    if conversation_id:
                        await self.send_to_conversation(
                            conversation_id, 
                            response, 
                            exclude_connection=connection_id
                        )
            
            return response
            
        except ConversationValidationError as e:
            error_response = {
                'type': 'dialogue_error',
                'payload': {
                    'error': str(e),
                    'error_type': 'validation_error',
                    'timestamp': datetime.utcnow().isoformat()
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            await self.send_to_connection(connection_id, error_response)
            logger.warning(f"Validation error in message handling: {str(e)}")
            return error_response
            
        except Exception as e:
            error_response = {
                'type': 'dialogue_error',
                'payload': {
                    'error': 'Internal server error',
                    'error_type': 'server_error',
                    'timestamp': datetime.utcnow().isoformat()
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            await self.send_to_connection(connection_id, error_response)
            log_error_with_context(
                logger, 
                f"Unexpected error handling WebSocket message: {str(e)}", 
                {'connection_id': connection_id, 'message_type': message.get('type')}
            )
            return error_response
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections"""
        return {
            'total_connections': len(self.active_connections),
            'total_conversation_subscriptions': len(self.conversation_subscriptions),
            'active_conversations': list(self.conversation_subscriptions.keys()),
            'connections_per_conversation': {
                conv_id: len(conn_ids) 
                for conv_id, conn_ids in self.conversation_subscriptions.items()
            }
        }
    
    async def cleanup_stale_connections(self, max_idle_minutes: int = 30):
        """Clean up connections that have been idle too long"""
        cutoff_time = datetime.utcnow()
        stale_connections = []
        
        for connection_id, connection_data in self.active_connections.items():
            idle_time = (cutoff_time - connection_data['last_activity']).total_seconds() / 60
            if idle_time > max_idle_minutes:
                stale_connections.append(connection_id)
        
        for connection_id in stale_connections:
            logger.info(f"Cleaning up stale connection: {connection_id}")
            self.disconnect(connection_id)


# Global connection manager instance
connection_manager = DialogueConnectionManager()


@websocket_router.websocket("/ws/{connection_id}")
async def dialogue_websocket_endpoint(websocket: WebSocket, connection_id: str):
    """
    Main WebSocket endpoint for dialogue system communication
    
    Handles real-time conversations, NPC interactions, and bartering
    according to the Development Bible WebSocket-first architecture.
    """
    logger.info(f"WebSocket connection attempt: {connection_id}")
    
    # Accept connection
    connection_success = await connection_manager.connect(websocket, connection_id)
    if not connection_success:
        logger.error(f"Failed to establish WebSocket connection: {connection_id}")
        return
    
    try:
        # Main message handling loop
        while True:
            try:
                # Receive message from client
                raw_message = await websocket.receive_text()
                
                # Parse JSON message
                try:
                    message = json.loads(raw_message)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON received from {connection_id}: {str(e)}")
                    await connection_manager.send_to_connection(connection_id, {
                        'type': 'dialogue_error',
                        'payload': {
                            'error': 'Invalid JSON format',
                            'error_type': 'format_error',
                            'timestamp': datetime.utcnow().isoformat()
                        },
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    continue
                
                # Process message through connection manager
                logger.debug(f"Processing message from {connection_id}: {message.get('type', 'unknown')}")
                response = await connection_manager.handle_message(connection_id, message)
                
                # Log successful message processing
                if response and response.get('type') != 'dialogue_error':
                    logger.debug(f"Successfully processed message for {connection_id}")
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected: {connection_id}")
                break
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message for {connection_id}: {str(e)}")
                
                # Try to send error response
                try:
                    await connection_manager.send_to_connection(connection_id, {
                        'type': 'dialogue_error',
                        'payload': {
                            'error': 'Message processing failed',
                            'error_type': 'processing_error',
                            'timestamp': datetime.utcnow().isoformat()
                        },
                        'timestamp': datetime.utcnow().isoformat()
                    })
                except:
                    # If we can't send error response, connection is likely dead
                    logger.error(f"Failed to send error response to {connection_id}")
                    break
    
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket handler for {connection_id}: {str(e)}")
    
    finally:
        # Clean up connection
        connection_manager.disconnect(connection_id)
        logger.info(f"WebSocket connection handler finished: {connection_id}")


@websocket_router.get("/stats")
async def get_dialogue_websocket_stats():
    """
    Get current WebSocket connection statistics for monitoring
    
    Returns:
        Dict containing connection and subscription statistics
    """
    try:
        stats = connection_manager.get_connection_stats()
        stats['timestamp'] = datetime.utcnow().isoformat()
        return {
            'success': True,
            'data': stats,
            'message': 'WebSocket statistics retrieved successfully'
        }
    except Exception as e:
        logger.error(f"Error retrieving WebSocket stats: {str(e)}")
        return create_error_response(
            error="Failed to retrieve WebSocket statistics",
            message="Internal server error"
        )


@websocket_router.post("/cleanup-stale")
async def cleanup_stale_connections(max_idle_minutes: int = 30):
    """
    Manually trigger cleanup of stale WebSocket connections
    
    Args:
        max_idle_minutes: Maximum idle time before connection is considered stale
        
    Returns:
        Dict containing cleanup results
    """
    try:
        initial_count = len(connection_manager.active_connections)
        await connection_manager.cleanup_stale_connections(max_idle_minutes)
        final_count = len(connection_manager.active_connections)
        
        cleaned_up = initial_count - final_count
        
        return {
            'success': True,
            'data': {
                'initial_connections': initial_count,
                'final_connections': final_count,
                'cleaned_up': cleaned_up,
                'max_idle_minutes': max_idle_minutes
            },
            'message': f'Cleaned up {cleaned_up} stale connections'
        }
    except Exception as e:
        logger.error(f"Error during stale connection cleanup: {str(e)}")
        return create_error_response(
            error="Failed to cleanup stale connections",
            message="Internal server error"
        )


# Health check endpoint for WebSocket service
@websocket_router.get("/health")
async def dialogue_websocket_health():
    """
    Health check endpoint for dialogue WebSocket service
    
    Returns:
        Dict containing service health status
    """
    try:
        stats = connection_manager.get_connection_stats()
        
        # Determine health status
        health_status = "healthy"
        if stats['total_connections'] > 1000:  # Arbitrary threshold
            health_status = "degraded"
        
        return {
            'success': True,
            'data': {
                'status': health_status,
                'service': 'dialogue-websocket',
                'connections': stats['total_connections'],
                'conversations': stats['total_conversation_subscriptions'],
                'timestamp': datetime.utcnow().isoformat()
            },
            'message': f'Dialogue WebSocket service is {health_status}'
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return {
            'success': False,
            'data': {
                'status': 'unhealthy',
                'service': 'dialogue-websocket',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            },
            'message': 'Dialogue WebSocket service health check failed'
        }


# Export router for inclusion in main FastAPI app
__all__ = ['websocket_router', 'connection_manager'] 