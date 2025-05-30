"""
Rumor System for the DM module.

This module implements the spread of rumors using an Information Diffusion model with mutation,
following the design described in the Development Bible.
"""

from typing import Dict, Any, List, Optional, Set
import logging
from datetime import datetime, timedelta
import json
import math
import random
from uuid import uuid4
from firebase_admin import db
from pydantic import BaseModel, Field

from backend.systems.dm.event_integration import (
    EventDispatcher, RumorEvent
)

# ===== Rumor Type Definitions =====

RUMOR_TYPES = {
    "scandal": "Gossip about personal or political misdeeds",
    "secret": "Hidden information, often with high stakes",
    "prophecy": "Predictions about future events",
    "discovery": "News of new lands, resources, or inventions",
    "catastrophe": "Warnings of disaster, war, or plague",
    "miracle": "Reports of supernatural or miraculous events",
    "betrayal": "Accusations of treachery or broken trust",
    "romance": "Tales of love affairs or forbidden relationships",
    "treasure": "Hints of hidden wealth or valuable items",
    "monster": "Sightings or rumors of dangerous creatures",
    "political": "Shifts in power, alliances, or intrigue",
    "economic": "Market crashes, booms, or trade opportunities",
    "invention": "New technologies or magical discoveries",
    "disappearance": "Missing persons or unexplained vanishings",
    "uprising": "Rebellions, revolts, or civil unrest"
}

# ===== Rumor Models =====

class Rumor(BaseModel):
    """
    Represents a single rumor in the system.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    rumor_type: str
    source_entity_id: str
    truth_value: float = 1.0  # 0.0 (completely false) to 1.0 (completely true)
    severity: int = 1  # 1 (minor) to 5 (major)
    region_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}
    tags: List[str] = []
    
    class Config:
        arbitrary_types_allowed = True


class RumorSpread(BaseModel):
    """
    Tracks the spreading of a rumor to an entity.
    """
    rumor_id: str
    entity_id: str
    source_entity_id: str
    believability: float = 0.5  # 0.0 (completely disbelieved) to 1.0 (completely believed)
    spread_at: datetime = Field(default_factory=datetime.utcnow)
    mutated: bool = False
    mutated_content: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ===== Rumor System =====

class RumorSystem:
    """
    Singleton manager for rumor creation, spreading, and mutation.
    
    Implements the Information Diffusion model with mutations.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the RumorSystem."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the rumor system."""
        if RumorSystem._instance is not None:
            raise Exception("This class is a singleton. Use get_instance() instead.")
        
        RumorSystem._instance = self
        self.event_dispatcher = EventDispatcher.get_instance()
        
        # Rumor spread settings
        self.mutation_chance = 0.3  # 30% chance of mutation per spread
        self.mutation_severity = 0.2  # Magnitude of mutations (0.0 to 1.0)
        
        # Decay settings
        self.decay_rate = 0.1  # 10% decay per day
        self.decay_threshold = 0.1  # Rumors below this believability decay faster
        
        # Cache settings
        self.rumor_cache = {}
        self.spread_cache = {}
        self.cache_ttl = timedelta(minutes=5)
        self.cache_timestamps = {}
    
    def create_rumor(self, content: str, rumor_type: str, source_entity_id: str,
                     truth_value: float = 1.0, severity: int = 1,
                     region_id: Optional[str] = None, tags: List[str] = None,
                     metadata: Dict[str, Any] = None) -> Rumor:
        """
        Create a new rumor.
        
        Args:
            content: The rumor content
            rumor_type: Type of rumor (from RUMOR_TYPES)
            source_entity_id: ID of the entity creating the rumor
            truth_value: How true the rumor is (0.0 to 1.0)
            severity: How severe/important the rumor is (1 to 5)
            region_id: Optional region ID
            tags: Optional tags for the rumor
            metadata: Optional metadata for the rumor
            
        Returns:
            The created Rumor object
        """
        # Validate rumor type
        if rumor_type not in RUMOR_TYPES:
            raise ValueError(f"Invalid rumor type: {rumor_type}")
        
        # Validate numeric parameters
        truth_value = max(0.0, min(1.0, truth_value))
        severity = max(1, min(5, severity))
        
        # Create rumor
        rumor = Rumor(
            content=content,
            rumor_type=rumor_type,
            source_entity_id=source_entity_id,
            truth_value=truth_value,
            severity=severity,
            region_id=region_id,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store in Firebase
        self._store_rumor(rumor)
        
        # Clear cache
        self._clear_rumor_cache(rumor.id)
        
        # Emit event
        self.event_dispatcher.publish(RumorEvent(
            event_type="rumor.created",
            rumor_id=rumor.id,
            source_entity_id=source_entity_id,
            target_entity_ids=[],  # No targets yet
            rumor_type=rumor_type,
            rumor_data=rumor.dict()
        ))
        
        return rumor
    
    def get_rumor(self, rumor_id: str) -> Optional[Rumor]:
        """
        Get a rumor by ID.
        
        Args:
            rumor_id: The ID of the rumor
            
        Returns:
            The Rumor object or None if not found
        """
        # Check cache first
        if self._is_rumor_cached(rumor_id):
            rumor_dict = self._get_rumor_from_cache(rumor_id)
            if rumor_dict:
                return self._dict_to_rumor(rumor_dict)
        
        # Fetch from Firebase
        rumor_ref = db.reference(f"/rumors/{rumor_id}")
        rumor_data = rumor_ref.get()
        
        if not rumor_data:
            return None
        
        # Cache it
        self._cache_rumor(rumor_id, rumor_data)
        
        return self._dict_to_rumor(rumor_data)
    
    def spread_rumor(self, rumor_id: str, source_entity_id: str,
                     target_entity_ids: List[str], apply_mutation: bool = True) -> Dict[str, RumorSpread]:
        """
        Spread a rumor to one or more entities.
        
        Args:
            rumor_id: The ID of the rumor
            source_entity_id: ID of the entity spreading the rumor
            target_entity_ids: IDs of the entities receiving the rumor
            apply_mutation: Whether to apply mutation
            
        Returns:
            Dict of target_entity_id -> RumorSpread
        """
        # Get rumor
        rumor = self.get_rumor(rumor_id)
        if not rumor:
            raise ValueError(f"Rumor {rumor_id} not found")
        
        # Check if the source has the rumor
        source_has_rumor = self._entity_has_rumor(source_entity_id, rumor_id)
        if not source_has_rumor and source_entity_id != rumor.source_entity_id:
            raise ValueError(f"Entity {source_entity_id} does not have rumor {rumor_id}")
        
        result = {}
        mutated_targets = []
        
        # Process each target
        for target_id in target_entity_ids:
            # Skip if target already has this rumor
            if self._entity_has_rumor(target_id, rumor_id):
                continue
            
            # Determine if mutation occurs
            mutated = False
            mutated_content = None
            
            if apply_mutation and random.random() < self.mutation_chance:
                mutated = True
                mutated_content = self._mutate_rumor_content(rumor.content)
                mutated_targets.append(target_id)
            
            # Calculate initial believability based on relationship (placeholder logic)
            believability = self._calculate_initial_believability(source_entity_id, target_id)
            
            # Create spread record
            spread = RumorSpread(
                rumor_id=rumor_id,
                entity_id=target_id,
                source_entity_id=source_entity_id,
                believability=believability,
                mutated=mutated,
                mutated_content=mutated_content
            )
            
            # Store in Firebase
            self._store_rumor_spread(spread)
            
            result[target_id] = spread
        
        # Emit event if any targets were processed
        if result:
            self.event_dispatcher.publish(RumorEvent(
                event_type="rumor.spread",
                rumor_id=rumor_id,
                source_entity_id=source_entity_id,
                target_entity_ids=list(result.keys()),
                rumor_type=rumor.rumor_type,
                rumor_data=rumor.dict(),
                mutated=bool(mutated_targets)
            ))
        
        return result
    
    def get_entity_rumors(self, entity_id: str, include_expired: bool = False) -> List[Dict[str, Any]]:
        """
        Get all rumors known to an entity.
        
        Args:
            entity_id: The ID of the entity
            include_expired: Whether to include expired rumors
            
        Returns:
            List of rumor details, including spread info
        """
        # Apply decay if needed
        self._apply_decay_if_needed(entity_id)
        
        # Get spread records
        spread_ref = db.reference(f"/rumor_spread/{entity_id}")
        spread_data = spread_ref.get() or {}
        
        result = []
        
        # Process each spread record
        for rumor_id, spread_dict in spread_data.items():
            # Skip if expired and not requested
            if not include_expired and self._is_rumor_expired(spread_dict):
                continue
            
            # Convert dates
            spread_dict["spread_at"] = datetime.fromisoformat(spread_dict["spread_at"])
            
            # Get rumor details
            rumor = self.get_rumor(rumor_id)
            if not rumor:
                continue
            
            # Add to result
            result.append({
                "rumor": rumor.dict(),
                "spread": spread_dict,
                "content": spread_dict.get("mutated_content") if spread_dict.get("mutated") else rumor.content
            })
        
        # Sort by believability (descending)
        result.sort(key=lambda r: r["spread"]["believability"], reverse=True)
        
        return result
    
    def update_believability(self, entity_id: str, rumor_id: str, adjustment: float) -> float:
        """
        Update an entity's believability of a rumor.
        
        Args:
            entity_id: The ID of the entity
            rumor_id: The ID of the rumor
            adjustment: The adjustment to believability (-1.0 to 1.0)
            
        Returns:
            The new believability value
        """
        # Get spread record
        spread_ref = db.reference(f"/rumor_spread/{entity_id}/{rumor_id}")
        spread_data = spread_ref.get()
        
        if not spread_data:
            raise ValueError(f"Entity {entity_id} does not have rumor {rumor_id}")
        
        # Calculate new believability
        current = spread_data.get("believability", 0.5)
        new_value = max(0.0, min(1.0, current + adjustment))
        
        # Update in Firebase
        spread_ref.update({"believability": new_value})
        
        # Clear cache
        self._clear_spread_cache(entity_id, rumor_id)
        
        return new_value
    
    def get_regional_rumors(self, region_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most believed rumors in a region.
        
        Args:
            region_id: The ID of the region
            limit: Maximum number of rumors to return
            
        Returns:
            List of rumor details with aggregate believability
        """
        # Get all rumors for the region
        rumors_ref = db.reference("/rumors")
        region_rumors = []
        
        all_rumors = rumors_ref.get() or {}
        for rumor_id, rumor_data in all_rumors.items():
            if rumor_data.get("region_id") == region_id:
                # Convert dates
                rumor_data["created_at"] = datetime.fromisoformat(rumor_data["created_at"])
                rumor_data["updated_at"] = datetime.fromisoformat(rumor_data["updated_at"])
                
                rumor_data["id"] = rumor_id
                region_rumors.append(self._dict_to_rumor(rumor_data))
        
        # If no rumors found, return empty list
        if not region_rumors:
            return []
        
        # Calculate aggregate believability for each rumor
        result = []
        for rumor in region_rumors:
            # Get all spread records for this rumor
            spread_ref = db.reference("/rumor_spread")
            all_spread = spread_ref.get() or {}
            
            spread_records = []
            total_believability = 0.0
            count = 0
            
            # Gather spread records
            for entity_id, entity_rumors in all_spread.items():
                if rumor.id in entity_rumors:
                    spread = entity_rumors[rumor.id]
                    spread["entity_id"] = entity_id
                    spread_records.append(spread)
                    total_believability += spread.get("believability", 0.5)
                    count += 1
            
            # Calculate average believability
            avg_believability = total_believability / count if count > 0 else 0.0
            
            # Add to result
            result.append({
                "rumor": rumor.dict(),
                "spread_count": count,
                "avg_believability": avg_believability
            })
        
        # Sort by average believability (descending)
        result.sort(key=lambda r: r["avg_believability"], reverse=True)
        
        return result[:limit]
    
    def get_rumor_context(self, entity_id: str = None, region_id: str = None,
                          max_rumors: int = 5) -> str:
        """
        Generate narrative context for rumors, either for an entity or a region.
        
        Args:
            entity_id: The ID of the entity (optional)
            region_id: The ID of the region (optional)
            max_rumors: Maximum number of rumors to include
            
        Returns:
            String of rumor context for narrative
        """
        context_lines = []
        
        if entity_id:
            # Get entity's rumors
            rumors = self.get_entity_rumors(entity_id)
            
            # Sort by believability
            rumors.sort(key=lambda r: r["spread"]["believability"], reverse=True)
            
            for i, r in enumerate(rumors[:max_rumors]):
                believability = r["spread"]["believability"]
                if believability > 0.8:
                    belief = "strongly believes"
                elif believability > 0.5:
                    belief = "believes"
                elif believability > 0.2:
                    belief = "is somewhat skeptical of"
                else:
                    belief = "doubts"
                
                context_lines.append(f"{i+1}. {entity_id} {belief} that {r['content']}")
        
        elif region_id:
            # Get regional rumors
            rumors = self.get_regional_rumors(region_id, max_rumors)
            
            for i, r in enumerate(rumors):
                spread = r["spread_count"]
                belief = r["avg_believability"]
                
                if spread > 10:
                    spread_text = "widely known"
                elif spread > 5:
                    spread_text = "somewhat known"
                else:
                    spread_text = "barely known"
                
                if belief > 0.8:
                    belief_text = "widely believed"
                elif belief > 0.5:
                    belief_text = "generally accepted"
                elif belief > 0.2:
                    belief_text = "somewhat doubted"
                else:
                    belief_text = "generally disbelieved"
                
                context_lines.append(f"{i+1}. It is {spread_text} and {belief_text} that {r['rumor']['content']}")
        
        return "\n".join(context_lines)
    
    # ===== Internal Methods =====
    
    def _store_rumor(self, rumor: Rumor):
        """
        Store a rumor in Firebase.
        
        Args:
            rumor: The Rumor object to store
        """
        rumor_dict = rumor.dict()
        
        # Convert datetime objects to ISO format for Firebase
        rumor_dict["created_at"] = rumor_dict["created_at"].isoformat()
        rumor_dict["updated_at"] = rumor_dict["updated_at"].isoformat()
        
        # Remove id field (it's the key)
        rumor_id = rumor_dict.pop("id")
        
        # Store in Firebase
        rumor_ref = db.reference(f"/rumors/{rumor_id}")
        rumor_ref.set(rumor_dict)
        
        # Update cache
        self._cache_rumor(rumor_id, rumor_dict)
    
    def _store_rumor_spread(self, spread: RumorSpread):
        """
        Store a rumor spread record in Firebase.
        
        Args:
            spread: The RumorSpread object to store
        """
        spread_dict = spread.dict()
        
        # Convert datetime objects to ISO format for Firebase
        spread_dict["spread_at"] = spread_dict["spread_at"].isoformat()
        
        # Store in Firebase
        spread_ref = db.reference(f"/rumor_spread/{spread.entity_id}/{spread.rumor_id}")
        spread_ref.set(spread_dict)
        
        # Update cache
        self._cache_rumor_spread(spread.entity_id, spread.rumor_id, spread_dict)
    
    def _entity_has_rumor(self, entity_id: str, rumor_id: str) -> bool:
        """
        Check if an entity already has a rumor.
        
        Args:
            entity_id: The ID of the entity
            rumor_id: The ID of the rumor
            
        Returns:
            True if the entity has the rumor, False otherwise
        """
        spread_ref = db.reference(f"/rumor_spread/{entity_id}/{rumor_id}")
        return spread_ref.get() is not None
    
    def _mutate_rumor_content(self, content: str) -> str:
        """
        Apply mutation to rumor content.
        
        Args:
            content: The original rumor content
            
        Returns:
            The mutated content
        """
        # TODO: Implement more sophisticated mutation logic
        # For now, just add "allegedly" or similar qualifiers
        
        qualifiers = [
            "allegedly", "reportedly", "supposedly", "apparently",
            "some say that", "it is believed that", "there are rumors that",
            "according to trusted sources", "it is said that"
        ]
        
        if random.random() < 0.5:
            return f"{random.choice(qualifiers)} {content}"
        else:
            # Replace a random word or add an adjective
            # This is a placeholder; would need more NLP for better mutations
            return f"{content} (but details are unclear)"
    
    def _calculate_initial_believability(self, source_id: str, target_id: str) -> float:
        """
        Calculate initial believability based on relationship.
        
        Args:
            source_id: The ID of the source entity
            target_id: The ID of the target entity
            
        Returns:
            Initial believability value (0.0 to 1.0)
        """
        # TODO: Implement relationship-based believability
        # For now, use a random value with bias toward middle
        
        # Check if source is NPC and target is player (more believable)
        if source_id.startswith("npc_") and target_id.startswith("player_"):
            base = 0.7
        # Check if source is player and target is NPC (less believable)
        elif source_id.startswith("player_") and target_id.startswith("npc_"):
            base = 0.4
        else:
            base = 0.5
        
        # Add some randomness
        return max(0.1, min(0.9, base + (random.random() - 0.5) * 0.4))
    
    def _apply_decay(self, entity_id: str):
        """
        Apply decay to all rumors for an entity.
        
        Args:
            entity_id: The ID of the entity
        """
        # Get last decay time
        last_decay_ref = db.reference(f"/rumor_decay/{entity_id}")
        last_decay = last_decay_ref.get()
        
        # Calculate days since last decay
        now = datetime.utcnow()
        if last_decay:
            last_decay_time = datetime.fromisoformat(last_decay)
            days_since_decay = (now - last_decay_time).days
        else:
            days_since_decay = 0
        
        # If no decay needed, update timestamp and return
        if days_since_decay < 1:
            return
        
        # Get all rumors for this entity
        spread_ref = db.reference(f"/rumor_spread/{entity_id}")
        spread_data = spread_ref.get() or {}
        
        # Apply decay to each rumor
        for rumor_id, spread in spread_data.items():
            # Calculate new believability
            current = spread.get("believability", 0.5)
            
            # Rumors below threshold decay faster
            if current < self.decay_threshold:
                decay_rate = self.decay_rate * 2
            else:
                decay_rate = self.decay_rate
            
            decay_factor = math.pow(1 - decay_rate, days_since_decay)
            new_value = current * decay_factor
            
            # Update in Firebase
            rumor_ref = spread_ref.child(rumor_id)
            rumor_ref.update({"believability": new_value})
        
        # Update last decay time
        last_decay_ref.set(now.isoformat())
        
        # Clear cache for this entity
        self._clear_entity_spread_cache(entity_id)
    
    def _apply_decay_if_needed(self, entity_id: str):
        """
        Check if decay should be applied and do so if needed.
        
        Args:
            entity_id: The ID of the entity
        """
        # Get last decay time
        last_decay_ref = db.reference(f"/rumor_decay/{entity_id}")
        last_decay = last_decay_ref.get()
        
        # If never decayed or more than a day since last decay, apply decay
        if not last_decay:
            self._apply_decay(entity_id)
            return
        
        last_decay_time = datetime.fromisoformat(last_decay)
        days_since_decay = (datetime.utcnow() - last_decay_time).days
        
        if days_since_decay >= 1:
            self._apply_decay(entity_id)
    
    def _is_rumor_expired(self, spread_dict: Dict[str, Any]) -> bool:
        """
        Check if a rumor spread record is expired.
        
        Args:
            spread_dict: The spread record
            
        Returns:
            True if expired, False otherwise
        """
        # Rumors with very low believability are considered expired
        return spread_dict.get("believability", 0.5) < 0.05
    
    def _dict_to_rumor(self, rumor_dict: Dict[str, Any]) -> Rumor:
        """
        Convert a dict to a Rumor object.
        
        Args:
            rumor_dict: The rumor dict
            
        Returns:
            Rumor object
        """
        # Convert ISO strings to datetime
        if isinstance(rumor_dict.get("created_at"), str):
            rumor_dict["created_at"] = datetime.fromisoformat(rumor_dict["created_at"])
        if isinstance(rumor_dict.get("updated_at"), str):
            rumor_dict["updated_at"] = datetime.fromisoformat(rumor_dict["updated_at"])
        
        return Rumor(**rumor_dict)
    
    # ===== Cache Methods =====
    
    def _is_rumor_cached(self, rumor_id: str) -> bool:
        """
        Check if a rumor is cached and not expired.
        
        Args:
            rumor_id: The ID of the rumor
            
        Returns:
            True if cached and not expired, False otherwise
        """
        if rumor_id not in self.cache_timestamps:
            return False
        
        cache_time = self.cache_timestamps[rumor_id]
        now = datetime.utcnow()
        
        return now - cache_time < self.cache_ttl
    
    def _cache_rumor(self, rumor_id: str, rumor_dict: Dict[str, Any]):
        """
        Cache a rumor.
        
        Args:
            rumor_id: The ID of the rumor
            rumor_dict: The rumor dict
        """
        self.rumor_cache[rumor_id] = rumor_dict
        self.cache_timestamps[rumor_id] = datetime.utcnow()
    
    def _clear_rumor_cache(self, rumor_id: str):
        """
        Clear the cache for a rumor.
        
        Args:
            rumor_id: The ID of the rumor
        """
        if rumor_id in self.rumor_cache:
            del self.rumor_cache[rumor_id]
        
        if rumor_id in self.cache_timestamps:
            del self.cache_timestamps[rumor_id]
    
    def _get_rumor_from_cache(self, rumor_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a rumor from the cache.
        
        Args:
            rumor_id: The ID of the rumor
            
        Returns:
            Rumor dict or None if not found
        """
        if not self._is_rumor_cached(rumor_id):
            return None
        
        return self.rumor_cache.get(rumor_id)
    
    def _cache_rumor_spread(self, entity_id: str, rumor_id: str, spread_dict: Dict[str, Any]):
        """
        Cache a rumor spread record.
        
        Args:
            entity_id: The ID of the entity
            rumor_id: The ID of the rumor
            spread_dict: The spread dict
        """
        if entity_id not in self.spread_cache:
            self.spread_cache[entity_id] = {}
        
        self.spread_cache[entity_id][rumor_id] = spread_dict
        
        # Set cache timestamp
        key = f"{entity_id}:{rumor_id}"
        self.cache_timestamps[key] = datetime.utcnow()
    
    def _clear_spread_cache(self, entity_id: str, rumor_id: str):
        """
        Clear the cache for a rumor spread record.
        
        Args:
            entity_id: The ID of the entity
            rumor_id: The ID of the rumor
        """
        if entity_id in self.spread_cache and rumor_id in self.spread_cache[entity_id]:
            del self.spread_cache[entity_id][rumor_id]
        
        key = f"{entity_id}:{rumor_id}"
        if key in self.cache_timestamps:
            del self.cache_timestamps[key]
    
    def _clear_entity_spread_cache(self, entity_id: str):
        """
        Clear all spread cache for an entity.
        
        Args:
            entity_id: The ID of the entity
        """
        if entity_id in self.spread_cache:
            del self.spread_cache[entity_id]
        
        # Clear all related timestamps
        to_delete = []
        for key in self.cache_timestamps:
            if key.startswith(f"{entity_id}:"):
                to_delete.append(key)
        
        for key in to_delete:
            del self.cache_timestamps[key]


# Initialize the rumor system
rumor_system = RumorSystem.get_instance() 