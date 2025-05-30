"""
Tests for dialogue system cache functionality.

This module tests the caching functionality for dialogue data including
conversation contexts, message histories, and integration data.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import threading
import time

from backend.systems.dialogue.cache import DialogueCache


@pytest.fixture
def cache(): pass
    """Create a fresh cache instance for testing."""
    # Clear singleton instance if it exists
    if hasattr(DialogueCache, '_instance'): pass
        DialogueCache._instance = None
    
    cache_instance = DialogueCache.get_instance()
    cache_instance.clear()
    return cache_instance


@pytest.fixture
def sample_context(): pass
    """Sample conversation context for testing."""
    return {
        "conversation_id": "conv_123",
        "participants": ["player", "npc_1"],
        "location": "tavern",
        "messages": [
            {"sender": "player", "content": "Hello"},
            {"sender": "npc_1", "content": "Greetings!"}
        ],
        "metadata": {"mood": "friendly"}
    }


@pytest.fixture
def sample_extraction(): pass
    """Sample extraction data for testing."""
    return {
        "entities": ["Dragon", "Quest"],
        "keywords": ["dangerous", "reward"],
        "sentiment": "neutral",
        "topics": ["adventure", "combat"]
    }


@pytest.fixture
def sample_memories(): pass
    """Sample character memories for testing."""
    return [
        {
            "id": "mem_1",
            "content": "Player helped in combat",
            "importance": 0.8,
            "timestamp": "2024-01-01T12:00:00"
        },
        {
            "id": "mem_2", 
            "content": "Player was polite",
            "importance": 0.6,
            "timestamp": "2024-01-01T12:05:00"
        }
    ]


def test_module_imports(): pass
    """Test that cache module can be imported."""
    from backend.systems.dialogue.cache import DialogueCache
    assert DialogueCache is not None


class TestDialogueCacheSingleton: pass
    """Test singleton behavior of DialogueCache."""
    
    def test_singleton_instance(self, cache): pass
        """Test that cache maintains singleton behavior."""
        cache1 = DialogueCache.get_instance()
        cache2 = DialogueCache.get_instance()
        
        assert cache1 is cache2
        assert cache1 is cache
    
    def test_new_warns_about_direct_instantiation(self, cache): pass
        """Test that direct instantiation warns about singleton usage."""
        with patch('backend.systems.dialogue.cache.logger') as mock_logger: pass
            # Create another instance directly
            cache2 = DialogueCache()
            
            # Should be same instance
            assert cache2 is cache
            
            # Should have logged a warning
            mock_logger.warning.assert_called_once()
            assert "singleton" in mock_logger.warning.call_args[0][0].lower()
    
    def test_thread_safety(self): pass
        """Test that singleton is thread-safe."""
        # Clear singleton
        if hasattr(DialogueCache, '_instance'): pass
            DialogueCache._instance = None
        
        instances = []
        
        def create_instance(): pass
            instances.append(DialogueCache.get_instance())
        
        # Create threads that all try to create instances
        threads = []
        for _ in range(10): pass
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads: pass
            thread.join()
        
        # All instances should be the same
        assert len(instances) == 10
        assert all(instance is instances[0] for instance in instances)


class TestDialogueCacheContextMethods: pass
    """Test context caching methods."""
    
    def test_cache_and_get_context(self, cache, sample_context): pass
        """Test caching and retrieving conversation context."""
        conversation_id = "conv_123"
        
        # Cache context
        cache.cache_context(conversation_id, sample_context)
        
        # Retrieve context
        cached_context = cache.get_cached_context(conversation_id)
        
        assert cached_context == sample_context
    
    def test_cache_context_with_custom_ttl(self, cache, sample_context): pass
        """Test caching context with custom TTL."""
        conversation_id = "conv_123"
        custom_ttl = 7200  # 2 hours
        
        cache.cache_context(conversation_id, sample_context, ttl=custom_ttl)
        
        # Should be cached
        cached_context = cache.get_cached_context(conversation_id)
        assert cached_context == sample_context
    
    def test_get_nonexistent_context(self, cache): pass
        """Test retrieving non-existent context returns None."""
        result = cache.get_cached_context("nonexistent")
        assert result is None
    
    def test_context_expiration(self, cache, sample_context): pass
        """Test that context expires after TTL."""
        conversation_id = "conv_123"
        short_ttl = 1  # 1 second
        
        # Cache with short TTL
        cache.cache_context(conversation_id, sample_context, ttl=short_ttl)
        
        # Should be available immediately
        cached_context = cache.get_cached_context(conversation_id)
        assert cached_context == sample_context
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired
        cached_context = cache.get_cached_context(conversation_id)
        assert cached_context is None


class TestDialogueCacheExtractionMethods: pass
    """Test extraction caching methods."""
    
    def test_cache_and_get_extraction(self, cache, sample_extraction): pass
        """Test caching and retrieving message extraction."""
        message_id = "msg_123"
        
        # Cache extraction
        cache.cache_extraction(message_id, sample_extraction)
        
        # Retrieve extraction
        cached_extraction = cache.get_cached_extraction(message_id)
        
        assert cached_extraction == sample_extraction
    
    def test_cache_extraction_with_custom_ttl(self, cache, sample_extraction): pass
        """Test caching extraction with custom TTL."""
        message_id = "msg_123"
        custom_ttl = 7200  # 2 hours
        
        cache.cache_extraction(message_id, sample_extraction, ttl=custom_ttl)
        
        # Should be cached
        cached_extraction = cache.get_cached_extraction(message_id)
        assert cached_extraction == sample_extraction
    
    def test_get_nonexistent_extraction(self, cache): pass
        """Test retrieving non-existent extraction returns None."""
        result = cache.get_cached_extraction("nonexistent")
        assert result is None
    
    def test_extraction_expiration(self, cache, sample_extraction): pass
        """Test that extraction expires after TTL."""
        message_id = "msg_123"
        short_ttl = 1  # 1 second
        
        # Cache with short TTL
        cache.cache_extraction(message_id, sample_extraction, ttl=short_ttl)
        
        # Should be available immediately
        cached_extraction = cache.get_cached_extraction(message_id)
        assert cached_extraction == sample_extraction
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired
        cached_extraction = cache.get_cached_extraction(message_id)
        assert cached_extraction is None


class TestDialogueCacheCharacterMemories: pass
    """Test character memories caching methods."""
    
    def test_cache_and_get_character_memories(self, cache, sample_memories): pass
        """Test caching and retrieving character memories."""
        character_id = "char_1"
        about_character_id = "char_2"
        
        # Cache memories
        cache.cache_character_memories(character_id, about_character_id, sample_memories)
        
        # Retrieve memories
        cached_memories = cache.get_cached_character_memories(character_id, about_character_id)
        
        assert cached_memories == sample_memories
    
    def test_cache_memories_with_custom_ttl(self, cache, sample_memories): pass
        """Test caching memories with custom TTL."""
        character_id = "char_1"
        about_character_id = "char_2"
        custom_ttl = 7200  # 2 hours
        
        cache.cache_character_memories(character_id, about_character_id, sample_memories, ttl=custom_ttl)
        
        # Should be cached
        cached_memories = cache.get_cached_character_memories(character_id, about_character_id)
        assert cached_memories == sample_memories
    
    def test_get_nonexistent_memories(self, cache): pass
        """Test retrieving non-existent memories returns None."""
        result = cache.get_cached_character_memories("nonexistent", "also_nonexistent")
        assert result is None
    
    def test_memories_expiration(self, cache, sample_memories): pass
        """Test that memories expire after TTL."""
        character_id = "char_1"
        about_character_id = "char_2"
        short_ttl = 1  # 1 second
        
        # Cache with short TTL
        cache.cache_character_memories(character_id, about_character_id, sample_memories, ttl=short_ttl)
        
        # Should be available immediately
        cached_memories = cache.get_cached_character_memories(character_id, about_character_id)
        assert cached_memories == sample_memories
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired
        cached_memories = cache.get_cached_character_memories(character_id, about_character_id)
        assert cached_memories is None
    
    def test_multiple_character_memories(self, cache, sample_memories): pass
        """Test caching memories for multiple character pairs."""
        char1 = "char_1"
        char2 = "char_2"
        char3 = "char_3"
        
        memories_1_2 = sample_memories
        memories_1_3 = [{"id": "mem_3", "content": "Different memory", "importance": 0.5}]
        
        # Cache memories for different character pairs
        cache.cache_character_memories(char1, char2, memories_1_2)
        cache.cache_character_memories(char1, char3, memories_1_3)
        
        # Should retrieve correct memories for each pair
        cached_1_2 = cache.get_cached_character_memories(char1, char2)
        cached_1_3 = cache.get_cached_character_memories(char1, char3)
        
        assert cached_1_2 == memories_1_2
        assert cached_1_3 == memories_1_3
        assert cached_1_2 != cached_1_3


class TestDialogueCacheLocationData: pass
    """Test location-based caching methods."""
    
    def test_cache_and_get_location_rumors(self, cache): pass
        """Test caching and retrieving location rumors."""
        location_id = "tavern_1"
        rumors = [
            {"id": "rumor_1", "content": "Dragon spotted nearby", "credibility": 0.7},
            {"id": "rumor_2", "content": "Treasure hidden in caves", "credibility": 0.5}
        ]
        
        # Cache rumors
        cache.set_location_rumors(location_id, rumors)
        
        # Retrieve rumors
        cached_rumors = cache.get_location_rumors(location_id)
        
        assert cached_rumors == rumors
    
    def test_cache_and_get_location_motifs(self, cache): pass
        """Test caching and retrieving location motifs."""
        location_id = "tavern_1"
        motifs = {
            "atmosphere": "cozy",
            "dominant_themes": ["hospitality", "gossip"],
            "mood": "welcoming"
        }
        
        # Cache motifs
        cache.set_location_motifs(location_id, motifs)
        
        # Retrieve motifs
        cached_motifs = cache.get_location_motifs(location_id)
        
        assert cached_motifs == motifs
    
    def test_get_nonexistent_location_data(self, cache): pass
        """Test retrieving non-existent location data returns None."""
        assert cache.get_location_rumors("nonexistent") is None
        assert cache.get_location_motifs("nonexistent") is None


class TestDialogueCacheGenericMethods: pass
    """Test generic cache methods."""
    
    def test_set_and_get_conversation(self, cache, sample_context): pass
        """Test generic conversation caching."""
        conversation_id = "conv_123"
        
        cache.set_conversation(conversation_id, sample_context)
        cached_data = cache.get_conversation(conversation_id)
        
        assert cached_data == sample_context
    
    def test_set_and_get_messages(self, cache): pass
        """Test generic message caching."""
        conversation_id = "conv_123"
        messages = [
            {"id": "msg_1", "content": "Hello", "sender": "player"},
            {"id": "msg_2", "content": "Hi there!", "sender": "npc"}
        ]
        
        cache.set_messages(conversation_id, messages)
        cached_messages = cache.get_messages(conversation_id)
        
        assert cached_messages == messages
    
    def test_set_and_get_context(self, cache, sample_context): pass
        """Test generic context caching."""
        conversation_id = "conv_123"
        
        cache.set_context(conversation_id, sample_context)
        cached_context = cache.get_context(conversation_id)
        
        assert cached_context == sample_context
    
    def test_cache_and_get_custom_context(self, cache): pass
        """Test custom context caching with arbitrary keys."""
        key = "custom_key"
        context = {"custom": "data", "number": 42}
        
        cache.cache_context(key, context)
        cached_context = cache.get_cached_context(key)
        
        assert cached_context == context
    
    def test_set_and_get_character_memories_generic(self, cache, sample_memories): pass
        """Test generic character memories caching."""
        character_id = "char_1"
        
        cache.set_character_memories(character_id, sample_memories)
        cached_memories = cache.get_character_memories(character_id)
        
        assert cached_memories == sample_memories
    
    def test_cache_and_get_extraction_generic(self, cache, sample_extraction): pass
        """Test generic extraction caching."""
        key = "extraction_key"
        
        cache.cache_extraction(key, sample_extraction)
        cached_extraction = cache.get_cached_extraction(key)
        
        assert cached_extraction == sample_extraction


class TestDialogueCacheClearMethods: pass
    """Test cache clearing methods."""
    
    def test_clear_conversation_data(self, cache, sample_context): pass
        """Test clearing conversation-specific data."""
        conversation_id = "conv_123"
        
        # Cache different types of data for the conversation
        cache.set_conversation(conversation_id, sample_context)
        cache.set_messages(conversation_id, [{"msg": "test"}])
        cache.set_context(conversation_id, sample_context)
        
        # Verify data is cached
        assert cache.get_conversation(conversation_id) is not None
        assert cache.get_messages(conversation_id) is not None
        assert cache.get_context(conversation_id) is not None
        
        # Clear conversation data
        cache.clear_conversation_data(conversation_id)
        
        # Verify data is cleared
        assert cache.get_conversation(conversation_id) is None
        assert cache.get_messages(conversation_id) is None
        assert cache.get_context(conversation_id) is None
    
    def test_clear_character_data(self, cache, sample_memories): pass
        """Test clearing character-specific data."""
        character_id = "char_1"
        
        # Cache character data using the proper generic method
        cache.set_character_memories(character_id, sample_memories)
        # Note: cache_character_memories needs two character IDs, so we skip this here
        
        # Verify data is cached
        assert cache.get_character_memories(character_id) is not None
        
        # Clear character data
        cache.clear_character_data(character_id)
        
        # Verify data is cleared
        assert cache.get_character_memories(character_id) is None
    
    def test_clear_location_data(self, cache): pass
        """Test clearing location-specific data."""
        location_id = "tavern_1"
        rumors = [{"rumor": "test"}]
        motifs = {"motif": "test"}
        
        # Cache location data
        cache.set_location_rumors(location_id, rumors)
        cache.set_location_motifs(location_id, motifs)
        
        # Verify data is cached
        assert cache.get_location_rumors(location_id) is not None
        assert cache.get_location_motifs(location_id) is not None
        
        # Clear location data
        cache.clear_location_data(location_id)
        
        # Verify data is cleared
        assert cache.get_location_rumors(location_id) is None
        assert cache.get_location_motifs(location_id) is None
    
    def test_clear_all(self, cache, sample_context, sample_memories): pass
        """Test clearing all cache data."""
        # Cache various types of data
        cache.set_conversation("conv_1", sample_context)
        cache.set_character_memories("char_1", sample_memories)
        cache.cache_context("conv_1", sample_context)
        cache.cache_extraction("msg_1", {"key": "value"})
        
        # Verify data is cached
        assert cache.get_conversation("conv_1") is not None
        assert cache.get_character_memories("char_1") is not None
        assert cache.get_cached_context("conv_1") is not None
        assert cache.get_cached_extraction("msg_1") is not None
        
        # Clear all data
        cache.clear_all()
        
        # Verify all data is cleared
        assert cache.get_conversation("conv_1") is None
        assert cache.get_character_memories("char_1") is None
        assert cache.get_cached_context("conv_1") is None
        assert cache.get_cached_extraction("msg_1") is None
    
    def test_clear_method(self, cache, sample_context): pass
        """Test the main clear method."""
        # Cache some data
        cache.cache_context("test", sample_context)
        cache.cache_extraction("test", {"data": "test"})
        
        # Verify data is cached
        assert cache.get_cached_context("test") is not None
        assert cache.get_cached_extraction("test") is not None
        
        # Clear cache
        cache.clear()
        
        # Verify data is cleared (no need to check individual gets since clear() empties everything)
        # Just verify the cache dictionaries are empty
        assert len(cache._context_cache) == 0
        assert len(cache._extraction_cache) == 0


class TestDialogueCacheExpiration: pass
    """Test cache expiration functionality."""
    
    def test_set_expiration_and_check(self, cache): pass
        """Test setting and checking expiration."""
        # Cache something with short TTL
        cache.cache_context("test", {"data": "test"}, ttl=1)
        
        # Should not be expired immediately
        assert cache.get_cached_context("test") is not None
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired now
        assert cache.get_cached_context("test") is None
    
    def test_cleanup_expired_removes_old_data(self, cache): pass
        """Test that cleanup removes expired data."""
        # Cache multiple items with different TTLs
        cache.cache_context("short", {"data": "short"}, ttl=1)
        cache.cache_context("long", {"data": "long"}, ttl=3600)
        cache.cache_extraction("short_ext", {"data": "short"}, ttl=1)
        
        # All should be available immediately
        assert cache.get_cached_context("short") is not None
        assert cache.get_cached_context("long") is not None
        assert cache.get_cached_extraction("short_ext") is not None
        
        # Wait for short items to expire
        time.sleep(2)
        
        # Accessing any item should trigger cleanup
        _ = cache.get_cached_context("long")
        
        # Short items should be gone, long item should remain
        assert cache.get_cached_context("short") is None
        assert cache.get_cached_context("long") is not None
        assert cache.get_cached_extraction("short_ext") is None
    
    def test_different_ttl_defaults(self, cache): pass
        """Test that different cache types have appropriate default TTLs."""
        # Test default TTLs are set properly
        assert cache.conversation_ttl == 3600  # 1 hour
        assert cache.message_ttl == 3600  # 1 hour
        assert cache.context_ttl == 1800  # 30 minutes
        assert cache.character_memories_ttl == 7200  # 2 hours
        assert cache.location_rumors_ttl == 7200  # 2 hours
        assert cache.location_motifs_ttl == 14400  # 4 hours
        assert cache.extraction_ttl == 3600  # 1 hour


class TestDialogueCacheLogging: pass
    """Test cache logging functionality."""
    
    def test_cache_operations_logged(self, cache, sample_context): pass
        """Test that cache operations are properly logged."""
        with patch('backend.systems.dialogue.cache.logger') as mock_logger: pass
            # Perform cache operations
            cache.cache_context("test", sample_context)
            cache.get_cached_context("test")
            cache.get_cached_context("nonexistent")
            
            # Should have logged cache operations
            assert mock_logger.debug.called
            assert mock_logger.debug.call_count >= 1
    
    def test_expiration_logged(self, cache, sample_context): pass
        """Test that cache expiration is logged."""
        with patch('backend.systems.dialogue.cache.logger') as mock_logger: pass
            # Cache with short TTL
            cache.cache_context("test", sample_context, ttl=1)
            
            # Wait for expiration
            time.sleep(2)
            
            # Try to access expired item
            cache.get_cached_context("test")
            
            # Should have logged expiration
            log_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            assert any("Expired custom context cache" in msg for msg in log_calls)


class TestDialogueCacheEdgeCases: pass
    """Test edge cases and error conditions."""
    
    def test_none_values_cached(self, cache): pass
        """Test that None values can be cached and retrieved."""
        cache.cache_context("none_test", None)
        result = cache.get_cached_context("none_test")
        assert result is None
    
    def test_empty_data_cached(self, cache): pass
        """Test that empty data structures can be cached."""
        cache.cache_context("empty_dict", {})
        cache.cache_extraction("empty_list", [])
        cache.cache_character_memories("char", "other", [])
        
        assert cache.get_cached_context("empty_dict") == {}
        assert cache.get_cached_extraction("empty_list") == []
        assert cache.get_cached_character_memories("char", "other") == []
    
    def test_large_data_cached(self, cache): pass
        """Test caching large data structures."""
        large_data = {"items": [{"id": i, "data": f"item_{i}"} for i in range(1000)]}
        
        cache.cache_context("large", large_data)
        result = cache.get_cached_context("large")
        
        assert result == large_data
        assert len(result["items"]) == 1000
    
    def test_unicode_data_cached(self, cache): pass
        """Test caching data with unicode characters."""
        unicode_data = {
            "text": "Hello 世界! 🌟",
            "names": ["José", "François", "Αλέξανδρος"],
            "emoji": "🎮🗡️🛡️"
        }
        
        cache.cache_context("unicode", unicode_data)
        result = cache.get_cached_context("unicode")
        
        assert result == unicode_data
    
    def test_zero_ttl(self, cache): pass
        """Test caching with zero TTL."""
        # Zero TTL should be treated as invalid and use default TTL
        cache.cache_context("zero_ttl", {"data": "test"}, ttl=0)
        result = cache.get_cached_context("zero_ttl")
        # Should still be cached since zero TTL uses default
        assert result is not None
        assert result == {"data": "test"}
    
    def test_negative_ttl(self, cache): pass
        """Test caching with negative TTL."""
        # Negative TTL should use default TTL (warning logged)
        cache.cache_context("negative_ttl", {"data": "test"}, ttl=-1)
        result = cache.get_cached_context("negative_ttl")
        # Should still be cached since negative TTL uses default
        assert result is not None
        assert result == {"data": "test"} 