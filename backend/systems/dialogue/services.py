"""
Dialogue System Services

This module provides comprehensive dialogue system services for managing
conversations, NPC interactions, and real-time WebSocket communication
according to the Development Bible architecture.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

# Updated imports to use the new database models
from backend.infrastructure.database.models.dialogue_models import (
    DialogueConversation,
    DialogueMessage,
    DialogueAnalytics,
    DialogueKnowledgeBase,
    DialogueSession
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    DialogueNotFoundError,
    DialogueValidationError,
    DialogueConflictError
)
from backend.infrastructure.dialogue_services.validation_service import (
    create_dialogue_validation_service,
    ConversationValidationError,
    MessageValidationError,
    NPCValidationError
)

logger = logging.getLogger(__name__)


class DialogueService(BaseService[DialogueConversation]):
    """Core dialogue system service for managing conversations and NPC interactions"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, DialogueConversation)
        self.db = db_session
        self.validation_service = create_dialogue_validation_service()
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        self.conversation_cache: Dict[str, Any] = {}

    async def create_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new conversation between a player and NPC
        
        Args:
            conversation_data: Dictionary containing conversation details
            
        Returns:
            Dict: Created conversation data with enhanced context
            
        Raises:
            ConversationValidationError: If validation fails
        """
        try:
            # Validate input data
            validated_data = self.validation_service.validate_conversation_data(conversation_data)
            logger.info(f"Creating conversation between player {validated_data['player_id']} and NPC {validated_data['npc_id']}")
            
            # Generate conversation ID if not provided
            conversation_id = validated_data.get('conversation_id', uuid4())
            
            # Create conversation entity using new database model
            conversation = DialogueConversation(
                conversation_id=conversation_id,
                npc_id=validated_data['npc_id'],
                player_id=validated_data['player_id'],
                interaction_type=validated_data.get('interaction_type', 'casual'),
                status='active',
                context=validated_data.get('context', {}),
                properties=validated_data.get('properties', {}),
                location_id=validated_data.get('location_id'),
                dialogue_context=validated_data.get('dialogue_context', 'general'),
                npc_type=validated_data.get('npc_type'),
                relationship_level=validated_data.get('relationship_level', 0.5),
                rag_enabled=validated_data.get('rag_enabled', True),
                ai_processing_metadata=validated_data.get('ai_processing_metadata', {})
            )
            
            # Persist to database
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            
            # Store active conversation
            self.active_conversations[str(conversation_id)] = {
                'conversation': self._conversation_to_dict(conversation),
                'messages': [],
                'started_at': conversation.started_at,
                'last_activity': conversation.last_activity
            }
            
            # Create analytics record
            analytics = DialogueAnalytics(
                conversation_id=conversation_id,
                event_type='conversation_started',
                event_data={
                    'interaction_type': conversation.interaction_type,
                    'dialogue_context': conversation.dialogue_context,
                    'rag_enabled': conversation.rag_enabled
                },
                player_id=conversation.player_id,
                npc_id=conversation.npc_id
            )
            self.db.add(analytics)
            self.db.commit()
            
            # Create response
            response = {
                'success': True,
                'data': {
                    'conversation': self._conversation_to_dict(conversation),
                    'message': 'Conversation created successfully'
                },
                'message': 'Conversation created successfully'
            }
            
            logger.info(f"Successfully created conversation {conversation_id}")
            return response
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating conversation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Conversation creation failed: {str(e)}"
            }
    
    async def send_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message in an existing conversation with enhanced features
        
        Args:
            message_data: Dictionary containing message details with extended types
            
        Returns:
            Dict: Message processing result with RAG enhancement data
        """
        try:
            # Validate message data
            validated_data = self.validation_service.validate_message_data(message_data)
            logger.info(f"Processing message for conversation {validated_data.get('conversation_id')}")
            
            conversation_id = validated_data.get('conversation_id')
            if not conversation_id:
                raise MessageValidationError("Conversation ID is required for sending messages")
            
            # Retrieve conversation from database
            conversation = self.db.query(DialogueConversation).filter(
                DialogueConversation.conversation_id == conversation_id
            ).first()
            
            if not conversation:
                raise MessageValidationError(f"Conversation {conversation_id} not found")
            
            # Create enhanced message with new features
            message = DialogueMessage(
                conversation_id=conversation_id,
                content=validated_data['content'],
                speaker=validated_data['speaker'],
                message_type=validated_data.get('message_type', 'dialogue'),
                emotion=validated_data.get('emotion'),
                metadata=validated_data.get('metadata', {}),
                is_placeholder=validated_data.get('is_placeholder', False),
                placeholder_category=validated_data.get('placeholder_category'),
                processing_time=validated_data.get('processing_time'),
                rag_enhanced=validated_data.get('rag_enhanced', False),
                context_sources=validated_data.get('context_sources', []),
                confidence_score=validated_data.get('confidence_score')
            )
            
            # Persist message
            self.db.add(message)
            
            # Update conversation last activity
            conversation.last_activity = datetime.utcnow()
            
            # Update analytics
            analytics = DialogueAnalytics(
                conversation_id=conversation_id,
                event_type='message_sent',
                event_data={
                    'speaker': validated_data['speaker'],
                    'message_type': validated_data.get('message_type', 'dialogue'),
                    'rag_enhanced': validated_data.get('rag_enhanced', False),
                    'processing_time': validated_data.get('processing_time')
                },
                player_id=conversation.player_id,
                npc_id=conversation.npc_id,
                message_count=self.db.query(DialogueMessage).filter(
                    DialogueMessage.conversation_id == conversation_id
                ).count() + 1
            )
            self.db.add(analytics)
            
            self.db.commit()
            
            # Update active conversation cache
            if str(conversation_id) in self.active_conversations:
                self.active_conversations[str(conversation_id)]['messages'].append(
                    self._message_to_dict(message)
                )
                self.active_conversations[str(conversation_id)]['last_activity'] = conversation.last_activity
            
            # Create response
            response = {
                'success': True,
                'data': {
                    'message': self._message_to_dict(message),
                    'conversation_id': str(conversation_id)
                },
                'message': 'Message sent successfully'
            }
            
            logger.info(f"Successfully processed message in conversation {conversation_id}")
            return response
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error sending message: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Message sending failed: {str(e)}"
            }
    
    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve conversation details and message history
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Dict: Conversation data with enhanced context and message history
        """
        try:
            # Validate conversation ID format
            try:
                conversation_uuid = UUID(conversation_id)
            except ValueError:
                return {
                    'success': False,
                    'error': 'Invalid conversation ID format',
                    'message': 'Conversation ID must be a valid UUID'
                }
            
            # Retrieve conversation from database
            conversation = self.db.query(DialogueConversation).filter(
                DialogueConversation.conversation_id == conversation_uuid
            ).first()
            
            if not conversation:
                return {
                    'success': False,
                    'error': 'Conversation not found',
                    'message': f'Conversation {conversation_id} not found'
                }
            
            # Retrieve messages
            messages = self.db.query(DialogueMessage).filter(
                DialogueMessage.conversation_id == conversation_uuid
            ).order_by(DialogueMessage.timestamp).all()
            
            # Retrieve analytics
            analytics = self.db.query(DialogueAnalytics).filter(
                DialogueAnalytics.conversation_id == conversation_uuid
            ).order_by(DialogueAnalytics.timestamp.desc()).limit(10).all()
            
            response = {
                'success': True,
                'data': {
                    'conversation': self._conversation_to_dict(conversation),
                    'messages': [self._message_to_dict(msg) for msg in messages],
                    'analytics': [self._analytics_to_dict(anal) for anal in analytics],
                    'message_count': len(messages),
                    'rag_queries': sum(1 for msg in messages if msg.rag_enhanced)
                },
                'message': 'Conversation retrieved successfully'
            }
            
            logger.info(f"Retrieved conversation {conversation_id} with {len(messages)} messages")
            return response
            
        except Exception as e:
            logger.error(f"Error retrieving conversation {conversation_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to retrieve conversation: {str(e)}"
            }

    def _conversation_to_dict(self, conversation: DialogueConversation) -> Dict[str, Any]:
        """Convert conversation entity to dictionary"""
        return {
            'id': str(conversation.id),
            'conversation_id': str(conversation.conversation_id),
            'npc_id': str(conversation.npc_id),
            'player_id': str(conversation.player_id),
            'interaction_type': conversation.interaction_type,
            'status': conversation.status,
            'context': conversation.context,
            'properties': conversation.properties,
            'started_at': conversation.started_at.isoformat() if conversation.started_at else None,
            'ended_at': conversation.ended_at.isoformat() if conversation.ended_at else None,
            'last_activity': conversation.last_activity.isoformat() if conversation.last_activity else None,
            'location_id': str(conversation.location_id) if conversation.location_id else None,
            'dialogue_context': conversation.dialogue_context,
            'npc_type': conversation.npc_type,
            'relationship_level': float(conversation.relationship_level) if conversation.relationship_level else None,
            'rag_enabled': conversation.rag_enabled,
            'ai_processing_metadata': conversation.ai_processing_metadata,
            'total_ai_latency': float(conversation.total_ai_latency) if conversation.total_ai_latency else None,
            'created_at': conversation.created_at.isoformat() if conversation.created_at else None,
            'updated_at': conversation.updated_at.isoformat() if conversation.updated_at else None
        }

    def _message_to_dict(self, message: DialogueMessage) -> Dict[str, Any]:
        """Convert message entity to dictionary"""
        return {
            'id': str(message.id),
            'conversation_id': str(message.conversation_id),
            'content': message.content,
            'speaker': message.speaker,
            'message_type': message.message_type,
            'emotion': message.emotion,
            'metadata': message.metadata,
            'timestamp': message.timestamp.isoformat() if message.timestamp else None,
            'is_placeholder': message.is_placeholder,
            'placeholder_category': message.placeholder_category,
            'replaced_by_message_id': str(message.replaced_by_message_id) if message.replaced_by_message_id else None,
            'processing_time': float(message.processing_time) if message.processing_time else None,
            'rag_enhanced': message.rag_enhanced,
            'context_sources': message.context_sources,
            'confidence_score': float(message.confidence_score) if message.confidence_score else None,
            'created_at': message.created_at.isoformat() if message.created_at else None
        }

    def _analytics_to_dict(self, analytics: DialogueAnalytics) -> Dict[str, Any]:
        """Convert analytics entity to dictionary"""
        return {
            'id': str(analytics.id),
            'conversation_id': str(analytics.conversation_id),
            'event_type': analytics.event_type,
            'event_data': analytics.event_data,
            'player_id': str(analytics.player_id),
            'npc_id': str(analytics.npc_id),
            'session_id': str(analytics.session_id) if analytics.session_id else None,
            'timestamp': analytics.timestamp.isoformat() if analytics.timestamp else None,
            'message_count': analytics.message_count,
            'total_duration': float(analytics.total_duration) if analytics.total_duration else None,
            'ai_requests': analytics.ai_requests,
            'average_response_time': float(analytics.average_response_time) if analytics.average_response_time else None,
            'placeholder_count': analytics.placeholder_count,
            'timeout_occurrences': analytics.timeout_occurrences,
            'rag_queries': analytics.rag_queries,
            'context_transitions': analytics.context_transitions
        }

    async def end_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        End an active conversation and cleanup resources
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Dict: Conversation ending result
        """
        try:
            # Validate conversation ID format
            validated_id = self.validation_service._validate_uuid(conversation_id, 'Conversation ID')
            
            # Check if conversation exists
            if validated_id not in self.active_conversations:
                return {
                    'success': False,
                    'error': "Conversation not found",
                    'message': f"Conversation {conversation_id} does not exist or already ended"
                }
            
            # Archive conversation data
            conversation_data = self.active_conversations[validated_id]
            conversation_data['ended_at'] = datetime.utcnow()
            conversation_data['status'] = 'ended'
            
            # Move to cache and remove from active conversations
            self.conversation_cache[validated_id] = conversation_data
            del self.active_conversations[validated_id]
            
            response = {
                'success': True,
                'data': {
                    'conversation_id': validated_id,
                    'ended_at': conversation_data['ended_at'].isoformat(),
                    'total_messages': len(conversation_data['messages']),
                    'duration_minutes': (conversation_data['ended_at'] - conversation_data['started_at']).total_seconds() / 60
                },
                'message': 'Conversation ended successfully'
            }
            
            logger.info(f"Successfully ended conversation {conversation_id}")
            return response
            
        except DialogueValidationError as e:
            logger.error(f"Validation error ending conversation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to end conversation: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error ending conversation: {str(e)}")
            return {
                'success': False,
                'error': "Internal server error",
                'message': "Failed to end conversation due to internal error"
            }
    
    async def validate_npc_interaction(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate NPC interaction data for dialogue system integration
        
        Args:
            npc_data: Dictionary containing NPC interaction details
            
        Returns:
            Dict: Validation result
        """
        try:
            # Validate NPC data
            validated_data = self.validation_service.validate_npc_interaction_data(npc_data)
            logger.info(f"Validated NPC interaction data for NPC {validated_data.get('npc_id')}")
            
            response = {
                'success': True,
                'data': {
                    'validated_npc_data': validated_data,
                    'interaction_options': self._get_interaction_options(validated_data)
                },
                'message': 'NPC interaction data validated successfully'
            }
            
            return response
            
        except NPCValidationError as e:
            logger.error(f"NPC validation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"NPC interaction validation failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error validating NPC interaction: {str(e)}")
            return {
                'success': False,
                'error': "Internal server error",
                'message': "Failed to validate NPC interaction due to internal error"
            }
    
    async def process_bartering_interaction(self, bartering_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process bartering/trading interactions with NPCs
        
        Args:
            bartering_data: Dictionary containing bartering details
            
        Returns:
            Dict: Bartering processing result
        """
        try:
            # Validate bartering data
            validated_data = self.validation_service.validate_bartering_data(bartering_data)
            logger.info(f"Processing bartering interaction for conversation {validated_data.get('conversation_id')}")
            
            # Calculate price adjustments based on relationship and faction standing
            processed_items = self._process_bartering_items(validated_data)
            
            response = {
                'success': True,
                'data': {
                    'bartering_session': validated_data,
                    'processed_items': processed_items,
                    'total_available_items': len(processed_items),
                    'price_summary': self._calculate_price_summary(processed_items)
                },
                'message': 'Bartering interaction processed successfully'
            }
            
            return response
            
        except DialogueValidationError as e:
            logger.error(f"Bartering validation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Bartering interaction failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error processing bartering: {str(e)}")
            return {
                'success': False,
                'error': "Internal server error",
                'message': "Failed to process bartering due to internal error"
            }
    
    async def get_active_conversations(self, player_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get list of active conversations, optionally filtered by player
        
        Args:
            player_id: Optional player ID to filter conversations
            
        Returns:
            Dict: List of active conversations
        """
        try:
            conversations = []
            
            for conv_id, conv_data in self.active_conversations.items():
                # Filter by player if specified
                if player_id and conv_data['conversation']['player_id'] != player_id:
                    continue
                
                conversations.append({
                    'conversation_id': conv_id,
                    'npc_id': conv_data['conversation']['npc_id'],
                    'player_id': conv_data['conversation']['player_id'],
                    'interaction_type': conv_data['conversation']['interaction_type'],
                    'started_at': conv_data['started_at'].isoformat(),
                    'last_activity': conv_data['last_activity'].isoformat(),
                    'message_count': len(conv_data['messages'])
                })
            
            response = {
                'success': True,
                'data': {
                    'conversations': conversations,
                    'total_active': len(conversations),
                    'filter_applied': player_id is not None
                },
                'message': f'Retrieved {len(conversations)} active conversations'
            }
            
            logger.info(f"Retrieved {len(conversations)} active conversations")
            return response
            
        except Exception as e:
            logger.error(f"Unexpected error retrieving active conversations: {str(e)}")
            return {
                'success': False,
                'error': "Internal server error",
                'message': "Failed to retrieve active conversations due to internal error"
            }
    
    # Private helper methods
    
    def _get_interaction_options(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate available interaction options for an NPC"""
        options = {
            'talk': True,  # Always available
            'barter': True,  # Universal bartering framework
            'ask_about': True,  # Context-specific inquiries
            'give_gift': True,  # Relationship building
            'challenge': False  # Depends on NPC type and context
        }
        
        # Enable challenge option for certain NPC types
        npc_type = npc_data.get('npc_type', '')
        if npc_type in ['guard', 'noble', 'artisan']:
            options['challenge'] = True
        
        # Disable some options based on relationship
        relationship = npc_data.get('relationship_standing', 0.5)
        if relationship < 0.2:
            options['ask_about'] = False  # Limited information sharing
        
        return options
    
    def _process_bartering_items(self, bartering_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and adjust item prices based on NPC type and relationship"""
        processed_items = []
        
        npc_type = bartering_data.get('npc_type', 'peasant')
        relationship = bartering_data.get('relationship_standing', 0.5)
        
        for item in bartering_data.get('available_items', []):
            processed_item = item.copy()
            
            # Apply NPC type pricing modifiers
            base_price = item['base_price']
            adjusted_price = base_price
            
            # NPC type modifiers
            if npc_type == 'merchant':
                adjusted_price *= 0.95  # 5% discount for fair pricing
            elif npc_type == 'noble':
                adjusted_price *= 1.5   # 50% markup for luxury
            elif npc_type == 'peasant':
                adjusted_price *= 1.25  # 25% markup for desperation
            elif npc_type == 'guard':
                adjusted_price *= 1.1   # 10% markup for practical items
            
            # Relationship modifiers
            relationship_modifier = 1.0 - (relationship * 0.3)  # Up to 30% discount
            adjusted_price *= relationship_modifier
            
            processed_item['final_price'] = round(adjusted_price, 2)
            processed_item['price_modifiers'] = {
                'npc_type_modifier': npc_type,
                'relationship_discount': round((1.0 - relationship_modifier) * 100, 1),
                'final_price': processed_item['final_price']
            }
            
            processed_items.append(processed_item)
        
        return processed_items
    
    def _calculate_price_summary(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for bartering session"""
        if not items:
            return {
                'total_items': 0,
                'average_price': 0,
                'price_range': {'min': 0, 'max': 0},
                'total_value': 0
            }
        
        prices = [item['final_price'] for item in items]
        
        return {
            'total_items': len(items),
            'average_price': round(sum(prices) / len(prices), 2),
            'price_range': {
                'min': min(prices),
                'max': max(prices)
            },
            'total_value': round(sum(prices), 2)
        }


class DialogueWebSocketService:
    """Service for handling real-time WebSocket communication for dialogue system"""
    
    def __init__(self, dialogue_service: DialogueService):
        """Initialize WebSocket service with dialogue service dependency"""
        self.dialogue_service = dialogue_service
        self.validation_service = create_dialogue_validation_service()
        self.active_connections: Dict[str, Any] = {}
        
    async def handle_websocket_message(self, message: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """
        Handle incoming WebSocket message
        
        Args:
            message: WebSocket message dictionary
            connection_id: Unique connection identifier
            
        Returns:
            Dict[str, Any]: Response message
        """
        try:
            # Validate WebSocket message format
            validated_message = self.validation_service.validate_websocket_message(message)
            logger.info(f"Processing WebSocket message type: {validated_message['type']}")
            
            message_type = validated_message['type']
            payload = validated_message['payload']
            
            # Route message based on type
            if message_type == 'dialogue_conversation_start':
                return await self._handle_conversation_start(payload, connection_id)
            elif message_type == 'dialogue_npc_interaction':
                return await self._handle_npc_interaction(payload, connection_id)
            elif message_type in ['dialogue_bartering_start', 'dialogue_bartering_update']:
                return await self._handle_bartering_interaction(payload, connection_id)
            elif message_type == 'dialogue_response_ready':
                return await self._handle_response_ready(payload, connection_id)
            else:
                return self._create_error_response(f"Unhandled message type: {message_type}")
                
        except DialogueValidationError as e:
            logger.error(f"WebSocket message validation error: {str(e)}")
            return self._create_error_response(str(e))
        except Exception as e:
            logger.error(f"Unexpected error handling WebSocket message: {str(e)}")
            return self._create_error_response("Internal server error")
    
    async def _handle_conversation_start(self, payload: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle conversation start WebSocket message"""
        try:
            # Create conversation through dialogue service
            conversation_result = await self.dialogue_service.create_conversation(payload)
            
            if conversation_result['success']:
                # Store connection mapping
                conversation_id = payload['conversation_id']
                self.active_connections[connection_id] = {
                    'conversation_id': conversation_id,
                    'type': 'dialogue_conversation',
                    'connected_at': datetime.utcnow()
                }
                
                return {
                    'type': 'dialogue_conversation_connection_status',
                    'payload': {
                        'message': 'Connected to conversation successfully',
                        'subscribed_channels': [f'conversation_{conversation_id}'],
                        'conversation_id': conversation_id
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return self._create_error_response(conversation_result['error'])
                
        except Exception as e:
            logger.error(f"Error handling conversation start: {str(e)}")
            return self._create_error_response("Failed to start conversation")
    
    async def _handle_npc_interaction(self, payload: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle NPC interaction WebSocket message"""
        try:
            # Process message through dialogue service
            message_result = await self.dialogue_service.send_message(payload)
            
            if message_result['success']:
                return {
                    'type': 'dialogue_response_ready',
                    'payload': {
                        'conversation_id': payload.get('conversation_id'),
                        'npc_id': payload.get('npc_id'),
                        'player_id': payload.get('player_id'),
                        'content': message_result['data']['message']['content'],
                        'speaker': message_result['data']['message']['speaker'],
                        'metadata': message_result['data']['message'].get('metadata', {})
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return self._create_error_response(message_result['error'])
                
        except Exception as e:
            logger.error(f"Error handling NPC interaction: {str(e)}")
            return self._create_error_response("Failed to process NPC interaction")
    
    async def _handle_bartering_interaction(self, payload: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle bartering interaction WebSocket message"""
        try:
            # Process bartering through dialogue service
            bartering_result = await self.dialogue_service.process_bartering_interaction(payload)
            
            if bartering_result['success']:
                return {
                    'type': 'dialogue_bartering_update',
                    'payload': {
                        'conversation_id': payload.get('conversation_id'),
                        'npc_id': payload.get('npc_id'),
                        'player_id': payload.get('player_id'),
                        'available_items': bartering_result['data']['processed_items'],
                        'npc_type': payload.get('npc_type'),
                        'relationship_standing': payload.get('relationship_standing'),
                        'price_summary': bartering_result['data']['price_summary']
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return self._create_error_response(bartering_result['error'])
                
        except Exception as e:
            logger.error(f"Error handling bartering interaction: {str(e)}")
            return self._create_error_response("Failed to process bartering interaction")
    
    async def _handle_response_ready(self, payload: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle response ready WebSocket message"""
        # This could be used for confirming receipt of AI-generated responses
        return {
            'type': 'dialogue_response_acknowledged',
            'payload': {
                'conversation_id': payload.get('conversation_id'),
                'acknowledged_at': datetime.utcnow().isoformat()
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'type': 'dialogue_error',
            'payload': {
                'error': error_message,
                'timestamp': datetime.utcnow().isoformat()
            },
            'timestamp': datetime.utcnow().isoformat()
        }


# Factory functions for service creation
def create_dialogue_service(db_session: Session) -> DialogueService:
    """Factory function to create dialogue service instance"""
    return DialogueService(db_session)


def create_dialogue_websocket_service(dialogue_service: Optional[DialogueService] = None) -> DialogueWebSocketService:
    """Factory function to create dialogue WebSocket service instance"""
    if dialogue_service is None:
        dialogue_service = create_dialogue_service()
    return DialogueWebSocketService(dialogue_service)
