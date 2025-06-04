"""
Dialogue System Cache Service

This module provides Redis-based caching for the dialogue system including
conversation caching, context caching, and performance optimization.
"""

import logging
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
import redis.asyncio as redis
from dataclasses import asdict

logger = logging.getLogger(__name__)


class CacheConfig:
    """Configuration for dialogue caching"""
    
    def __init__(self):
        # Redis connection settings
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.redis_db = 0
        self.redis_password = None
        self.redis_ssl = False
        
        # Cache TTL settings (in seconds)
        self.conversation_ttl = 3600  # 1 hour
        self.context_window_ttl = 1800  # 30 minutes
        self.npc_personality_ttl = 86400  # 24 hours
        self.ai_response_cache_ttl = 300  # 5 minutes
        self.connection_info_ttl = 900  # 15 minutes
        
        # Cache key prefixes
        self.conversation_prefix = "dialogue:conversation"
        self.context_prefix = "dialogue:context"
        self.personality_prefix = "dialogue:personality"
        self.response_cache_prefix = "dialogue:response_cache"
        self.connection_prefix = "dialogue:connection"
        self.metrics_prefix = "dialogue:metrics"
        
        # Performance settings
        self.max_context_size = 1000  # Max characters in cached context
        self.max_response_cache_entries = 1000
        self.cache_compression_threshold = 500  # Bytes


class ConversationCache:
    """Handles conversation-specific caching operations"""
    
    def __init__(self, redis_client: redis.Redis, config: CacheConfig):
        self.redis = redis_client
        self.config = config
    
    async def cache_conversation(self, conversation_id: str, conversation_data: Dict[str, Any]):
        """
        Cache conversation data
        
        Args:
            conversation_id: Conversation identifier
            conversation_data: Conversation data to cache
        """
        try:
            cache_key = f"{self.config.conversation_prefix}:{conversation_id}"
            serialized_data = json.dumps(conversation_data, default=str)
            
            await self.redis.setex(
                cache_key,
                self.config.conversation_ttl,
                serialized_data
            )
            
            logger.debug(f"Cached conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to cache conversation {conversation_id}: {str(e)}")
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached conversation data
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Optional[Dict[str, Any]]: Cached conversation data or None
        """
        try:
            cache_key = f"{self.config.conversation_prefix}:{conversation_id}"
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation {conversation_id}: {str(e)}")
            return None
    
    async def update_conversation_activity(self, conversation_id: str):
        """
        Update conversation last activity timestamp
        
        Args:
            conversation_id: Conversation identifier
        """
        try:
            cache_key = f"{self.config.conversation_prefix}:{conversation_id}"
            
            # Check if conversation exists in cache
            conversation_data = await self.get_conversation(conversation_id)
            if conversation_data:
                conversation_data['last_activity'] = datetime.utcnow().isoformat()
                await self.cache_conversation(conversation_id, conversation_data)
                
        except Exception as e:
            logger.error(f"Failed to update conversation activity {conversation_id}: {str(e)}")
    
    async def remove_conversation(self, conversation_id: str):
        """
        Remove conversation from cache
        
        Args:
            conversation_id: Conversation identifier
        """
        try:
            cache_key = f"{self.config.conversation_prefix}:{conversation_id}"
            await self.redis.delete(cache_key)
            
            logger.debug(f"Removed conversation {conversation_id} from cache")
            
        except Exception as e:
            logger.error(f"Failed to remove conversation {conversation_id}: {str(e)}")


class ContextCache:
    """Handles conversation context caching"""
    
    def __init__(self, redis_client: redis.Redis, config: CacheConfig):
        self.redis = redis_client
        self.config = config
    
    async def cache_context_window(
        self, 
        conversation_id: str, 
        context_data: List[Dict[str, Any]]
    ):
        """
        Cache conversation context window
        
        Args:
            conversation_id: Conversation identifier
            context_data: Context window data
        """
        try:
            cache_key = f"{self.config.context_prefix}:{conversation_id}"
            
            # Limit context size for performance
            serialized_data = json.dumps(context_data, default=str)
            if len(serialized_data) > self.config.max_context_size:
                # Truncate to most recent messages
                truncated_context = context_data[-5:]  # Keep last 5 messages
                serialized_data = json.dumps(truncated_context, default=str)
            
            await self.redis.setex(
                cache_key,
                self.config.context_window_ttl,
                serialized_data
            )
            
            logger.debug(f"Cached context for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to cache context for {conversation_id}: {str(e)}")
    
    async def get_context_window(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve cached context window
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Optional[List[Dict[str, Any]]]: Cached context data or None
        """
        try:
            cache_key = f"{self.config.context_prefix}:{conversation_id}"
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve context for {conversation_id}: {str(e)}")
            return None
    
    async def append_message_to_context(
        self, 
        conversation_id: str, 
        message: Dict[str, Any]
    ):
        """
        Append a message to cached context
        
        Args:
            conversation_id: Conversation identifier
            message: Message to append
        """
        try:
            context = await self.get_context_window(conversation_id) or []
            context.append(message)
            
            # Limit context window size
            max_messages = 10
            if len(context) > max_messages:
                context = context[-max_messages:]
            
            await self.cache_context_window(conversation_id, context)
            
        except Exception as e:
            logger.error(f"Failed to append message to context {conversation_id}: {str(e)}")


class PersonalityCache:
    """Handles NPC personality caching"""
    
    def __init__(self, redis_client: redis.Redis, config: CacheConfig):
        self.redis = redis_client
        self.config = config
    
    async def cache_npc_personality(self, npc_id: str, personality_data: Dict[str, Any]):
        """
        Cache NPC personality data
        
        Args:
            npc_id: NPC identifier
            personality_data: Personality data to cache
        """
        try:
            cache_key = f"{self.config.personality_prefix}:{npc_id}"
            serialized_data = json.dumps(personality_data, default=str)
            
            await self.redis.setex(
                cache_key,
                self.config.npc_personality_ttl,
                serialized_data
            )
            
            logger.debug(f"Cached personality for NPC {npc_id}")
            
        except Exception as e:
            logger.error(f"Failed to cache personality for NPC {npc_id}: {str(e)}")
    
    async def get_npc_personality(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached NPC personality
        
        Args:
            npc_id: NPC identifier
            
        Returns:
            Optional[Dict[str, Any]]: Cached personality data or None
        """
        try:
            cache_key = f"{self.config.personality_prefix}:{npc_id}"
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve personality for NPC {npc_id}: {str(e)}")
            return None


class ResponseCache:
    """Handles AI response caching for performance optimization"""
    
    def __init__(self, redis_client: redis.Redis, config: CacheConfig):
        self.redis = redis_client
        self.config = config
    
    def _generate_response_cache_key(
        self, 
        npc_id: str, 
        player_message: str, 
        context_hash: str
    ) -> str:
        """
        Generate a cache key for AI responses
        
        Args:
            npc_id: NPC identifier
            player_message: Player's message
            context_hash: Hash of conversation context
            
        Returns:
            str: Cache key
        """
        import hashlib
        
        cache_input = f"{npc_id}:{player_message}:{context_hash}"
        hash_key = hashlib.md5(cache_input.encode()).hexdigest()
        return f"{self.config.response_cache_prefix}:{hash_key}"
    
    async def cache_ai_response(
        self,
        npc_id: str,
        player_message: str,
        context_hash: str,
        ai_response: Dict[str, Any]
    ):
        """
        Cache AI-generated response
        
        Args:
            npc_id: NPC identifier
            player_message: Player's message
            context_hash: Hash of conversation context
            ai_response: AI response to cache
        """
        try:
            cache_key = self._generate_response_cache_key(npc_id, player_message, context_hash)
            
            # Add timestamp to cached response
            cached_response = {
                **ai_response,
                'cached_at': datetime.utcnow().isoformat(),
                'cache_key': cache_key
            }
            
            serialized_data = json.dumps(cached_response, default=str)
            
            await self.redis.setex(
                cache_key,
                self.config.ai_response_cache_ttl,
                serialized_data
            )
            
            logger.debug(f"Cached AI response for NPC {npc_id}")
            
        except Exception as e:
            logger.error(f"Failed to cache AI response: {str(e)}")
    
    async def get_cached_response(
        self,
        npc_id: str,
        player_message: str,
        context_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached AI response
        
        Args:
            npc_id: NPC identifier
            player_message: Player's message
            context_hash: Hash of conversation context
            
        Returns:
            Optional[Dict[str, Any]]: Cached response or None
        """
        try:
            cache_key = self._generate_response_cache_key(npc_id, player_message, context_hash)
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                response = json.loads(cached_data)
                logger.debug(f"Cache hit for AI response: {cache_key}")
                return response
            
            logger.debug(f"Cache miss for AI response: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached response: {str(e)}")
            return None


class ConnectionCache:
    """Handles WebSocket connection caching"""
    
    def __init__(self, redis_client: redis.Redis, config: CacheConfig):
        self.redis = redis_client
        self.config = config
    
    async def cache_connection_info(
        self,
        connection_id: str,
        user_id: str,
        connection_data: Dict[str, Any]
    ):
        """
        Cache WebSocket connection information
        
        Args:
            connection_id: Connection identifier
            user_id: User identifier
            connection_data: Connection metadata
        """
        try:
            cache_key = f"{self.config.connection_prefix}:{connection_id}"
            
            connection_info = {
                'user_id': user_id,
                'connected_at': datetime.utcnow().isoformat(),
                'last_activity': datetime.utcnow().isoformat(),
                **connection_data
            }
            
            serialized_data = json.dumps(connection_info, default=str)
            
            await self.redis.setex(
                cache_key,
                self.config.connection_info_ttl,
                serialized_data
            )
            
            # Also maintain user -> connections mapping
            user_connections_key = f"{self.config.connection_prefix}:user:{user_id}"
            await self.redis.sadd(user_connections_key, connection_id)
            await self.redis.expire(user_connections_key, self.config.connection_info_ttl)
            
            logger.debug(f"Cached connection info for {connection_id}")
            
        except Exception as e:
            logger.error(f"Failed to cache connection info: {str(e)}")
    
    async def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached connection information
        
        Args:
            connection_id: Connection identifier
            
        Returns:
            Optional[Dict[str, Any]]: Connection info or None
        """
        try:
            cache_key = f"{self.config.connection_prefix}:{connection_id}"
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve connection info: {str(e)}")
            return None
    
    async def remove_connection(self, connection_id: str):
        """
        Remove connection from cache
        
        Args:
            connection_id: Connection identifier
        """
        try:
            # Get connection info first to clean up user mapping
            connection_info = await self.get_connection_info(connection_id)
            
            # Remove connection cache
            cache_key = f"{self.config.connection_prefix}:{connection_id}"
            await self.redis.delete(cache_key)
            
            # Remove from user connections set
            if connection_info and 'user_id' in connection_info:
                user_connections_key = f"{self.config.connection_prefix}:user:{connection_info['user_id']}"
                await self.redis.srem(user_connections_key, connection_id)
            
            logger.debug(f"Removed connection {connection_id} from cache")
            
        except Exception as e:
            logger.error(f"Failed to remove connection: {str(e)}")
    
    async def get_user_connections(self, user_id: str) -> List[str]:
        """
        Get all connections for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List[str]: List of connection IDs
        """
        try:
            user_connections_key = f"{self.config.connection_prefix}:user:{user_id}"
            connections = await self.redis.smembers(user_connections_key)
            return [conn.decode() if isinstance(conn, bytes) else conn for conn in connections]
            
        except Exception as e:
            logger.error(f"Failed to get user connections: {str(e)}")
            return []


class DialogueCacheService:
    """Main cache service for dialogue system"""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.redis_client: Optional[redis.Redis] = None
        self.conversation_cache: Optional[ConversationCache] = None
        self.context_cache: Optional[ContextCache] = None
        self.personality_cache: Optional[PersonalityCache] = None
        self.response_cache: Optional[ResponseCache] = None
        self.connection_cache: Optional[ConnectionCache] = None
    
    async def initialize(self):
        """Initialize Redis connection and cache services"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                ssl=self.config.redis_ssl,
                decode_responses=False
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Initialize cache services
            self.conversation_cache = ConversationCache(self.redis_client, self.config)
            self.context_cache = ContextCache(self.redis_client, self.config)
            self.personality_cache = PersonalityCache(self.redis_client, self.config)
            self.response_cache = ResponseCache(self.redis_client, self.config)
            self.connection_cache = ConnectionCache(self.redis_client, self.config)
            
            logger.info("Dialogue cache service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup Redis connections"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def health_check(self) -> bool:
        """Check if cache service is healthy"""
        try:
            if self.redis_client:
                await self.redis_client.ping()
                return True
            return False
        except Exception:
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if not self.redis_client:
                return {'status': 'not_initialized'}
            
            info = await self.redis_client.info()
            
            return {
                'status': 'healthy',
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'hit_rate': info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0)),
                'uptime': info.get('uptime_in_seconds', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {'status': 'error', 'error': str(e)}


def create_dialogue_cache_service(config: Optional[CacheConfig] = None) -> DialogueCacheService:
    """Factory function to create dialogue cache service"""
    return DialogueCacheService(config) 