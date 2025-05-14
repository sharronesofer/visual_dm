"""
Quest model with optimized indexing and caching.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from app.core.database import db
from app.core.utils.cache_utils import CacheManager
from app.core.utils.error_utils import DatabaseError

@dataclass
class Quest:
    """Quest model with optimized indexing and caching."""
    
    # Core fields
    id: str
    title: str
    description: str
    level: int
    type: str
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Optional fields with default values
    rewards: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    current_step: Optional[int] = None
    player_id: Optional[str] = None
    npc_id: Optional[str] = None
    region_id: Optional[str] = None
    
    # Cache manager instance
    _cache: CacheManager = field(default_factory=CacheManager)
    
    # Indexed fields for frequent queries
    _indexed_fields = {
        'status': True,
        'level': True,
        'type': True,
        'player_id': True,
        'npc_id': True,
        'region_id': True
    }
    
    @classmethod
    def create_indexes(cls) -> None:
        """Create indexes for frequently queried fields."""
        try:
            collection = db.collection('quests')
            
            # Create compound indexes for common query patterns
            collection.create_index([
                ('status', 1),
                ('level', 1)
            ])
            
            collection.create_index([
                ('type', 1),
                ('status', 1)
            ])
            
            collection.create_index([
                ('player_id', 1),
                ('status', 1)
            ])
            
            collection.create_index([
                ('npc_id', 1),
                ('status', 1)
            ])
            
            collection.create_index([
                ('region_id', 1),
                ('status', 1)
            ])
            
        except Exception as e:
            raise DatabaseError(f"Failed to create indexes: {str(e)}")
            
    @classmethod
    def get_by_id(cls, quest_id: str) -> Optional['Quest']:
        """Get a quest by ID with caching."""
        try:
            # Try to get from cache first
            cached_quest = cls._cache.get(f"quest:{quest_id}")
            if cached_quest:
                return cls(**cached_quest)
                
            # If not in cache, get from database
            quest_doc = db.collection('quests').document(quest_id).get()
            if not quest_doc.exists:
                return None
                
            quest_data = quest_doc.to_dict()
            quest = cls(**quest_data)
            
            # Cache the result
            cls._cache.set(f"quest:{quest_id}", quest_data, ttl=300)  # 5 minutes TTL
            
            return quest
            
        except Exception as e:
            raise DatabaseError(f"Failed to get quest: {str(e)}")
            
    @classmethod
    def get_by_player(cls, player_id: str, status: Optional[str] = None) -> List['Quest']:
        """Get quests by player ID with caching."""
        try:
            cache_key = f"player_quests:{player_id}:{status or 'all'}"
            
            # Try to get from cache first
            cached_quests = cls._cache.get(cache_key)
            if cached_quests:
                return [cls(**quest_data) for quest_data in cached_quests]
                
            # Build query
            query = db.collection('quests').where('player_id', '==', player_id)
            if status:
                query = query.where('status', '==', status)
                
            # Execute query
            quests = []
            for quest_doc in query.get():
                quest_data = quest_doc.to_dict()
                quests.append(cls(**quest_data))
                
            # Cache the results
            cls._cache.set(cache_key, [quest.__dict__ for quest in quests], ttl=300)
            
            return quests
            
        except Exception as e:
            raise DatabaseError(f"Failed to get player quests: {str(e)}")
            
    @classmethod
    def get_by_npc(cls, npc_id: str, status: Optional[str] = None) -> List['Quest']:
        """Get quests by NPC ID with caching."""
        try:
            cache_key = f"npc_quests:{npc_id}:{status or 'all'}"
            
            # Try to get from cache first
            cached_quests = cls._cache.get(cache_key)
            if cached_quests:
                return [cls(**quest_data) for quest_data in cached_quests]
                
            # Build query
            query = db.collection('quests').where('npc_id', '==', npc_id)
            if status:
                query = query.where('status', '==', status)
                
            # Execute query
            quests = []
            for quest_doc in query.get():
                quest_data = quest_doc.to_dict()
                quests.append(cls(**quest_data))
                
            # Cache the results
            cls._cache.set(cache_key, [quest.__dict__ for quest in quests], ttl=300)
            
            return quests
            
        except Exception as e:
            raise DatabaseError(f"Failed to get NPC quests: {str(e)}")
            
    @classmethod
    def get_by_region(cls, region_id: str, status: Optional[str] = None) -> List['Quest']:
        """Get quests by region ID with caching."""
        try:
            cache_key = f"region_quests:{region_id}:{status or 'all'}"
            
            # Try to get from cache first
            cached_quests = cls._cache.get(cache_key)
            if cached_quests:
                return [cls(**quest_data) for quest_data in cached_quests]
                
            # Build query
            query = db.collection('quests').where('region_id', '==', region_id)
            if status:
                query = query.where('status', '==', status)
                
            # Execute query
            quests = []
            for quest_doc in query.get():
                quest_data = quest_doc.to_dict()
                quests.append(cls(**quest_data))
                
            # Cache the results
            cls._cache.set(cache_key, [quest.__dict__ for quest in quests], ttl=300)
            
            return quests
            
        except Exception as e:
            raise DatabaseError(f"Failed to get region quests: {str(e)}")
            
    def save(self) -> None:
        """Save the quest to the database and update cache."""
        try:
            # Prepare data
            data = self.__dict__.copy()
            data.pop('_cache', None)  # Remove cache manager from data
            
            # Save to database
            db.collection('quests').document(self.id).set(data)
            
            # Update cache
            self._cache.set(f"quest:{self.id}", data, ttl=300)
            
            # Invalidate related caches
            if self.player_id:
                self._cache.delete(f"player_quests:{self.player_id}:all")
                self._cache.delete(f"player_quests:{self.player_id}:{self.status}")
                
            if self.npc_id:
                self._cache.delete(f"npc_quests:{self.npc_id}:all")
                self._cache.delete(f"npc_quests:{self.npc_id}:{self.status}")
                
            if self.region_id:
                self._cache.delete(f"region_quests:{self.region_id}:all")
                self._cache.delete(f"region_quests:{self.region_id}:{self.status}")
                
        except Exception as e:
            raise DatabaseError(f"Failed to save quest: {str(e)}")
            
    def update_progress(self, step_id: int) -> None:
        """Update quest progress and handle cache invalidation."""
        try:
            if not self.is_valid_step(step_id):
                raise ValueError(f"Invalid step ID: {step_id}")
                
            self.current_step = step_id
            self.updated_at = datetime.utcnow()
            self.save()
            
        except Exception as e:
            raise DatabaseError(f"Failed to update quest progress: {str(e)}")
            
    def is_valid_step(self, step_id: int) -> bool:
        """Check if a step ID is valid for this quest."""
        return any(step['id'] == step_id for step in self.steps) 