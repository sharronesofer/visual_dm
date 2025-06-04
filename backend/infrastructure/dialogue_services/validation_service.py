"""
Dialogue System Validation Service

This module provides comprehensive validation services for the dialogue system
according to the Development Bible standards and business requirements.
"""

import re
import json
from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from datetime import datetime
from jsonschema import validate, ValidationError as JsonValidationError

# Custom validation exceptions
class DialogueValidationError(Exception):
    """Base exception for dialogue validation errors"""
    pass

class ConversationValidationError(DialogueValidationError):
    """Exception for conversation-specific validation errors"""
    pass

class MessageValidationError(DialogueValidationError):
    """Exception for message validation errors"""
    pass

class NPCValidationError(DialogueValidationError):
    """Exception for NPC-related validation errors"""
    pass


class DialogueValidationService:
    """Service for validating dialogue system data and operations"""
    
    def __init__(self):
        """Initialize validation service with schemas and rules"""
        self.max_message_length = 10000
        self.max_conversation_duration = 3600  # 1 hour in seconds
        self.min_response_time = 0.1  # Minimum seconds for realistic response
        self.max_response_time = 300  # Maximum seconds before timeout
        self.prohibited_content_patterns = [
            r'\b(hack|exploit|cheat)\b',
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'data:text/html'
        ]
        
    def validate_conversation_data(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate conversation creation/update data
        
        Args:
            conversation_data: Dictionary containing conversation information
            
        Returns:
            Dict[str, Any]: Validated and sanitized conversation data
            
        Raises:
            ConversationValidationError: If validation fails
        """
        try:
            validated_data = {}
            
            # Required fields validation
            if 'npc_id' not in conversation_data:
                raise ConversationValidationError("NPC ID is required")
            
            if 'player_id' not in conversation_data:
                raise ConversationValidationError("Player ID is required")
                
            # UUID validation
            validated_data['npc_id'] = self._validate_uuid(
                conversation_data['npc_id'], 'NPC ID'
            )
            validated_data['player_id'] = self._validate_uuid(
                conversation_data['player_id'], 'Player ID'
            )
            
            # Optional conversation ID
            if 'conversation_id' in conversation_data:
                validated_data['conversation_id'] = self._validate_uuid(
                    conversation_data['conversation_id'], 'Conversation ID'
                )
            
            # Interaction type validation
            valid_interaction_types = ['casual', 'quest', 'trading', 'combat', 'social']
            interaction_type = conversation_data.get('interaction_type', 'casual')
            if interaction_type not in valid_interaction_types:
                raise ConversationValidationError(
                    f"Invalid interaction type: {interaction_type}. "
                    f"Must be one of: {', '.join(valid_interaction_types)}"
                )
            validated_data['interaction_type'] = interaction_type
            
            # Context validation
            if 'context' in conversation_data:
                validated_data['context'] = self._validate_conversation_context(
                    conversation_data['context']
                )
            
            # Properties validation
            if 'properties' in conversation_data:
                validated_data['properties'] = self._validate_properties(
                    conversation_data['properties']
                )
                
            return validated_data
            
        except Exception as e:
            if isinstance(e, DialogueValidationError):
                raise
            raise ConversationValidationError(f"Conversation validation failed: {str(e)}")
    
    def validate_message_data(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate dialogue message data
        
        Args:
            message_data: Dictionary containing message information
            
        Returns:
            Dict[str, Any]: Validated and sanitized message data
            
        Raises:
            MessageValidationError: If validation fails
        """
        try:
            validated_data = {}
            
            # Required fields
            if 'content' not in message_data:
                raise MessageValidationError("Message content is required")
                
            # Content validation and sanitization
            content = str(message_data['content']).strip()
            if not content:
                raise MessageValidationError("Message content cannot be empty")
                
            if len(content) > self.max_message_length:
                raise MessageValidationError(
                    f"Message content exceeds maximum length of {self.max_message_length} characters"
                )
            
            # Check for prohibited content
            validated_data['content'] = self._sanitize_content(content)
            
            # Speaker validation
            valid_speakers = ['npc', 'player', 'system']
            speaker = message_data.get('speaker', 'npc')
            if speaker not in valid_speakers:
                raise MessageValidationError(
                    f"Invalid speaker: {speaker}. Must be one of: {', '.join(valid_speakers)}"
                )
            validated_data['speaker'] = speaker
            
            # UUID fields validation
            for field in ['conversation_id', 'npc_id', 'player_id']:
                if field in message_data:
                    validated_data[field] = self._validate_uuid(
                        message_data[field], field
                    )
            
            # Metadata validation
            if 'metadata' in message_data:
                validated_data['metadata'] = self._validate_message_metadata(
                    message_data['metadata']
                )
                
            # Timestamp validation
            if 'timestamp' in message_data:
                validated_data['timestamp'] = self._validate_timestamp(
                    message_data['timestamp']
                )
                
            return validated_data
            
        except Exception as e:
            if isinstance(e, DialogueValidationError):
                raise
            raise MessageValidationError(f"Message validation failed: {str(e)}")
    
    def validate_websocket_message(self, ws_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate WebSocket message format
        
        Args:
            ws_message: WebSocket message dictionary
            
        Returns:
            Dict[str, Any]: Validated message
            
        Raises:
            MessageValidationError: If validation fails
        """
        try:
            # Load and validate against JSON schema
            schema_path = "data/systems/dialogue/dialogue_schema.json"
            try:
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                validate(instance=ws_message, schema=schema)
            except FileNotFoundError:
                # If schema file doesn't exist, perform basic validation
                pass
            except JsonValidationError as e:
                raise MessageValidationError(f"WebSocket message schema validation failed: {str(e)}")
            
            # Basic structure validation
            required_fields = ['type', 'payload', 'timestamp']
            for field in required_fields:
                if field not in ws_message:
                    raise MessageValidationError(f"Required field '{field}' missing from WebSocket message")
            
            # Message type validation
            valid_types = [
                'dialogue_latency_connection_status',
                'dialogue_general_connection_status',
                'dialogue_conversation_connection_status',
                'dialogue_placeholder_message',
                'dialogue_response_ready',
                'dialogue_conversation_start',
                'dialogue_conversation_end',
                'dialogue_context_update',
                'dialogue_npc_interaction',
                'dialogue_bartering_start',
                'dialogue_bartering_update',
                'dialogue_error'
            ]
            
            message_type = ws_message['type']
            if message_type not in valid_types:
                raise MessageValidationError(f"Invalid message type: {message_type}")
            
            # Payload validation based on type
            payload = ws_message['payload']
            if message_type in ['dialogue_response_ready', 'dialogue_npc_interaction']:
                self._validate_dialogue_content_payload(payload)
            elif message_type == 'dialogue_conversation_start':
                self._validate_conversation_start_payload(payload)
            elif message_type in ['dialogue_bartering_start', 'dialogue_bartering_update']:
                self._validate_bartering_payload(payload)
            
            return ws_message
            
        except Exception as e:
            if isinstance(e, DialogueValidationError):
                raise
            raise MessageValidationError(f"WebSocket message validation failed: {str(e)}")
    
    def validate_npc_interaction_data(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate NPC interaction data
        
        Args:
            npc_data: Dictionary containing NPC interaction information
            
        Returns:
            Dict[str, Any]: Validated NPC data
            
        Raises:
            NPCValidationError: If validation fails
        """
        try:
            validated_data = {}
            
            # NPC ID validation
            if 'npc_id' in npc_data:
                validated_data['npc_id'] = self._validate_uuid(npc_data['npc_id'], 'NPC ID')
            
            # NPC name validation
            if 'npc_name' in npc_data:
                npc_name = str(npc_data['npc_name']).strip()
                if not npc_name:
                    raise NPCValidationError("NPC name cannot be empty")
                if len(npc_name) > 100:
                    raise NPCValidationError("NPC name exceeds maximum length of 100 characters")
                validated_data['npc_name'] = npc_name
            
            # NPC type validation
            if 'npc_type' in npc_data:
                valid_npc_types = ['peasant', 'merchant', 'noble', 'guard', 'artisan', 'scholar']
                npc_type = npc_data['npc_type']
                if npc_type not in valid_npc_types:
                    raise NPCValidationError(
                        f"Invalid NPC type: {npc_type}. "
                        f"Must be one of: {', '.join(valid_npc_types)}"
                    )
                validated_data['npc_type'] = npc_type
            
            # Relationship validation
            if 'relationship_standing' in npc_data:
                relationship = npc_data['relationship_standing']
                if not isinstance(relationship, (int, float)):
                    raise NPCValidationError("Relationship standing must be a number")
                if not (0 <= relationship <= 1):
                    raise NPCValidationError("Relationship standing must be between 0 and 1")
                validated_data['relationship_standing'] = float(relationship)
            
            # Personality traits validation
            if 'personality' in npc_data:
                personality = npc_data['personality']
                if not isinstance(personality, dict):
                    raise NPCValidationError("Personality must be a dictionary")
                
                # Validate personality trait values
                for trait, value in personality.items():
                    if not isinstance(value, (int, float)):
                        raise NPCValidationError(f"Personality trait '{trait}' must be a number")
                    if not (0 <= value <= 10):
                        raise NPCValidationError(f"Personality trait '{trait}' must be between 0 and 10")
                
                validated_data['personality'] = personality
                
            return validated_data
            
        except Exception as e:
            if isinstance(e, DialogueValidationError):
                raise
            raise NPCValidationError(f"NPC validation failed: {str(e)}")
    
    def validate_bartering_data(self, bartering_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate bartering/trading data
        
        Args:
            bartering_data: Dictionary containing bartering information
            
        Returns:
            Dict[str, Any]: Validated bartering data
            
        Raises:
            DialogueValidationError: If validation fails
        """
        try:
            validated_data = {}
            
            # Available items validation
            if 'available_items' in bartering_data:
                items = bartering_data['available_items']
                if not isinstance(items, list):
                    raise DialogueValidationError("Available items must be a list")
                
                validated_items = []
                for item in items:
                    validated_item = self._validate_bartering_item(item)
                    validated_items.append(validated_item)
                
                validated_data['available_items'] = validated_items
            
            # NPC data validation
            for field in ['npc_id', 'player_id', 'conversation_id']:
                if field in bartering_data:
                    validated_data[field] = self._validate_uuid(
                        bartering_data[field], field
                    )
            
            # NPC type validation
            if 'npc_type' in bartering_data:
                valid_types = ['peasant', 'merchant', 'noble', 'guard', 'artisan', 'scholar']
                npc_type = bartering_data['npc_type']
                if npc_type not in valid_types:
                    raise DialogueValidationError(f"Invalid NPC type for bartering: {npc_type}")
                validated_data['npc_type'] = npc_type
            
            return validated_data
            
        except Exception as e:
            if isinstance(e, DialogueValidationError):
                raise
            raise DialogueValidationError(f"Bartering validation failed: {str(e)}")
    
    # Private helper methods
    
    def _validate_uuid(self, uuid_value: Union[str, UUID], field_name: str) -> str:
        """Validate UUID format"""
        try:
            if isinstance(uuid_value, UUID):
                return str(uuid_value)
            
            # Try to parse as UUID to validate format
            UUID(str(uuid_value))
            return str(uuid_value)
        except (ValueError, TypeError):
            raise DialogueValidationError(f"Invalid UUID format for {field_name}: {uuid_value}")
    
    def _validate_timestamp(self, timestamp_value: Union[str, datetime]) -> str:
        """Validate timestamp format"""
        try:
            if isinstance(timestamp_value, datetime):
                return timestamp_value.isoformat()
            
            # Try to parse as datetime to validate format
            datetime.fromisoformat(str(timestamp_value).replace('Z', '+00:00'))
            return str(timestamp_value)
        except (ValueError, TypeError):
            raise DialogueValidationError(f"Invalid timestamp format: {timestamp_value}")
    
    def _sanitize_content(self, content: str) -> str:
        """Sanitize message content"""
        # Check for prohibited patterns
        for pattern in self.prohibited_content_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise MessageValidationError(f"Content contains prohibited pattern")
        
        # Basic HTML sanitization (remove script tags, etc.)
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'data:text/html', '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    def _validate_conversation_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate conversation context data"""
        validated_context = {}
        
        # Location validation
        if 'location' in context:
            location = str(context['location']).strip()
            if len(location) > 200:
                raise ConversationValidationError("Location exceeds maximum length")
            validated_context['location'] = location
        
        # Time validation
        if 'time_of_day' in context:
            time_of_day = str(context['time_of_day']).strip()
            validated_context['time_of_day'] = time_of_day
        
        # Previous interactions validation
        if 'previous_interactions' in context:
            prev_interactions = context['previous_interactions']
            if not isinstance(prev_interactions, int) or prev_interactions < 0:
                raise ConversationValidationError("Previous interactions must be a non-negative integer")
            validated_context['previous_interactions'] = prev_interactions
        
        # Relationship level validation
        if 'relationship_level' in context:
            rel_level = context['relationship_level']
            if not isinstance(rel_level, (int, float)) or not (-1 <= rel_level <= 1):
                raise ConversationValidationError("Relationship level must be between -1 and 1")
            validated_context['relationship_level'] = float(rel_level)
        
        return validated_context
    
    def _validate_message_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate message metadata"""
        validated_metadata = {}
        
        # Emotion validation
        if 'emotion' in metadata:
            emotion = str(metadata['emotion']).strip()
            if len(emotion) > 50:
                raise MessageValidationError("Emotion exceeds maximum length")
            validated_metadata['emotion'] = emotion
        
        # Action validation
        if 'action' in metadata:
            action = str(metadata['action']).strip()
            if len(action) > 200:
                raise MessageValidationError("Action exceeds maximum length")
            validated_metadata['action'] = action
        
        # Lists validation
        for list_field in ['items_mentioned', 'entities_mentioned']:
            if list_field in metadata:
                if not isinstance(metadata[list_field], list):
                    raise MessageValidationError(f"{list_field} must be a list")
                validated_list = [str(item).strip() for item in metadata[list_field] if str(item).strip()]
                validated_metadata[list_field] = validated_list
        
        return validated_metadata
    
    def _validate_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generic properties dictionary"""
        if not isinstance(properties, dict):
            raise DialogueValidationError("Properties must be a dictionary")
        
        # Limit property values to reasonable sizes
        validated_props = {}
        for key, value in properties.items():
            if isinstance(value, str) and len(value) > 1000:
                raise DialogueValidationError(f"Property '{key}' value exceeds maximum length")
            validated_props[str(key)] = value
        
        return validated_props
    
    def _validate_dialogue_content_payload(self, payload: Dict[str, Any]) -> None:
        """Validate dialogue content payload"""
        required_fields = ['conversation_id', 'npc_id', 'player_id', 'content', 'speaker']
        for field in required_fields:
            if field not in payload:
                raise MessageValidationError(f"Required field '{field}' missing from dialogue content payload")
    
    def _validate_conversation_start_payload(self, payload: Dict[str, Any]) -> None:
        """Validate conversation start payload"""
        required_fields = ['conversation_id', 'npc_id', 'player_id', 'npc_name', 'interaction_type']
        for field in required_fields:
            if field not in payload:
                raise MessageValidationError(f"Required field '{field}' missing from conversation start payload")
    
    def _validate_bartering_payload(self, payload: Dict[str, Any]) -> None:
        """Validate bartering payload"""
        required_fields = ['conversation_id', 'npc_id', 'player_id', 'available_items', 'npc_type']
        for field in required_fields:
            if field not in payload:
                raise MessageValidationError(f"Required field '{field}' missing from bartering payload")
    
    def _validate_bartering_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual bartering item"""
        validated_item = {}
        
        # Required fields
        required_fields = ['item_id', 'name', 'base_price', 'adjusted_price', 'availability_tier']
        for field in required_fields:
            if field not in item:
                raise DialogueValidationError(f"Required field '{field}' missing from bartering item")
        
        # Item ID validation
        validated_item['item_id'] = self._validate_uuid(item['item_id'], 'Item ID')
        
        # Name validation
        name = str(item['name']).strip()
        if not name:
            raise DialogueValidationError("Item name cannot be empty")
        if len(name) > 100:
            raise DialogueValidationError("Item name exceeds maximum length")
        validated_item['name'] = name
        
        # Price validation
        for price_field in ['base_price', 'adjusted_price']:
            price = item[price_field]
            if not isinstance(price, (int, float)) or price < 0:
                raise DialogueValidationError(f"{price_field} must be a non-negative number")
            validated_item[price_field] = float(price)
        
        # Availability tier validation
        valid_tiers = ['always_available', 'relationship_gated', 'never_available']
        tier = item['availability_tier']
        if tier not in valid_tiers:
            raise DialogueValidationError(f"Invalid availability tier: {tier}")
        validated_item['availability_tier'] = tier
        
        # Optional price modifiers
        if 'price_modifiers' in item:
            modifiers = item['price_modifiers']
            if isinstance(modifiers, dict):
                validated_modifiers = {}
                for modifier_name, value in modifiers.items():
                    if isinstance(value, (int, float)):
                        validated_modifiers[modifier_name] = float(value)
                validated_item['price_modifiers'] = validated_modifiers
        
        return validated_item


def create_dialogue_validation_service() -> DialogueValidationService:
    """Factory function to create dialogue validation service"""
    return DialogueValidationService() 