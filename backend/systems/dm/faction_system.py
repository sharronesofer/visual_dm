"""
Faction System for the DM module.

This module implements factions, their relationships, and influence on the game world,
following the design described in the Development Bible.
"""

from typing import Dict, Any, List, Optional, Set, Tuple, Union
import logging
from datetime import datetime, timedelta
import json
import math
import random
from uuid import uuid4
from firebase_admin import db
from pydantic import BaseModel, Field

from backend.systems.dm.event_integration import (
    EventDispatcher, FactionEvent
)

# ===== Faction Models =====

class FactionRelationship(BaseModel):
    """
    Represents a relationship between two factions.
    """
    faction_id: str
    target_faction_id: str
    reputation: float = 0.0  # -1.0 (hostile) to 1.0 (allied)
    influence: float = 0.0  # How much influence this faction has over the target
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = True  # Whether this relationship is known publicly
    
    class Config:
        arbitrary_types_allowed = True


class FactionGoal(BaseModel):
    """
    Represents a goal or objective for a faction.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    faction_id: str
    title: str
    description: str
    importance: int = 5  # 1 (minor) to 10 (vital)
    progress: float = 0.0  # 0.0 to 1.0 (completion level)
    active: bool = True
    opposing_factions: List[str] = []  # Factions that oppose this goal
    supporting_factions: List[str] = []  # Factions that support this goal
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True


class FactionResource(BaseModel):
    """
    Represents a resource controlled by a faction.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    faction_id: str
    name: str
    resource_type: str  # military, economic, political, information, magical
    amount: int = 1
    quality: int = 5  # 1 (poor) to 10 (exceptional)
    location_id: Optional[str] = None
    is_public: bool = True  # Whether this resource is publicly known
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True


class Faction(BaseModel):
    """
    Represents a faction in the game world.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    faction_type: str  # government, guild, cult, family, military, etc.
    power_level: int = 5  # 1 (minimal) to 10 (world-spanning)
    secrecy: int = 1  # 1 (public) to 10 (completely hidden)
    stability: float = 0.5  # 0.0 (collapsing) to 1.0 (rock solid)
    territory: List[str] = []  # Region IDs where faction has presence
    leadership: List[Dict[str, Any]] = []  # Key members/leaders
    colors: List[str] = []  # Symbolic colors
    symbol: Optional[str] = None  # Description of faction symbol/crest
    values: List[str] = []  # Core values/principles
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True


# ===== Faction System =====

class FactionSystem:
    """
    Singleton manager for faction creation, relationships, and influence.
    
    Implements faction dynamics, allegiances, and power struggles.
    """
    _instance = None
    
    # Faction types
    FACTION_TYPES = [
        "government",   # Official ruling bodies, councils
        "guild",        # Professional organizations, trade groups
        "cult",         # Religious or mystical organizations
        "criminal",     # Thieves' guilds, criminal organizations
        "military",     # Armies, mercenary companies
        "noble",        # Noble houses, aristocratic families
        "arcane",       # Magical orders, academies
        "merchant",     # Trading companies, merchant houses
        "tribal",       # Clans, indigenous groups
        "revolutionary", # Rebels, resistance movements
        "secret_society" # Hidden organizations with specific goals
    ]
    
    # Resource types
    RESOURCE_TYPES = [
        "military",     # Troops, weapons, fortifications
        "economic",     # Money, trade goods, property
        "political",    # Influence, connections, authority
        "information",  # Secrets, intelligence networks
        "magical",      # Artifacts, spells, magical locations
        "social",       # Reputation, social connections
        "technological" # Special tools, inventions, infrastructure
    ]
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the FactionSystem."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the faction system."""
        if FactionSystem._instance is not None:
            raise Exception("This class is a singleton. Use get_instance() instead.")
        
        FactionSystem._instance = self
        self.event_dispatcher = EventDispatcher.get_instance()
        
        # System parameters
        self.influence_decay_rate = 0.05  # Per week decay of influence
        self.relationship_inertia = 0.7   # How much relationships resist change
        self.power_projection_factor = 0.2  # How effectively power affects influence
        
        # Cache settings
        self.faction_cache = {}
        self.relationship_cache = {}
        self.cache_ttl = timedelta(minutes=15)
        self.cache_timestamps = {}
    
    def create_faction(self, name: str, description: str, faction_type: str,
                       power_level: int = 5, secrecy: int = 1, stability: float = 0.5,
                       territory: List[str] = None, leadership: List[Dict[str, Any]] = None,
                       colors: List[str] = None, symbol: Optional[str] = None,
                       values: List[str] = None, tags: List[str] = None,
                       metadata: Dict[str, Any] = None) -> Faction:
        """
        Create a new faction.
        
        Args:
            name: Unique name for the faction
            description: Description of the faction
            faction_type: Type of faction (from FACTION_TYPES)
            power_level: Power level (1 to 10)
            secrecy: How secretive the faction is (1 to 10)
            stability: How stable the faction is (0.0 to 1.0)
            territory: List of region IDs where the faction has presence
            leadership: Key leaders/members of the faction
            colors: Symbolic colors of the faction
            symbol: Description of faction symbol/crest
            values: Core values/principles of the faction
            tags: Search tags for the faction
            metadata: Additional data for the faction
            
        Returns:
            The created Faction object
        """
        # Validate faction type
        if faction_type not in self.FACTION_TYPES:
            raise ValueError(f"Invalid faction type: {faction_type}")
        
        # Validate numeric parameters
        power_level = max(1, min(10, power_level))
        secrecy = max(1, min(10, secrecy))
        stability = max(0.0, min(1.0, stability))
        
        # Create faction
        faction = Faction(
            name=name,
            description=description,
            faction_type=faction_type,
            power_level=power_level,
            secrecy=secrecy,
            stability=stability,
            territory=territory or [],
            leadership=leadership or [],
            colors=colors or [],
            symbol=symbol,
            values=values or [],
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store in Firebase
        self._store_faction(faction)
        
        # Clear cache
        self._clear_faction_cache(faction.id)
        
        # Emit event
        self.event_dispatcher.publish(FactionEvent(
            event_type="faction.created",
            faction_id=faction.id,
            faction_name=faction.name,
            faction_type=faction.type
        ))
        
        return faction
    
    def get_faction(self, faction_id: str) -> Optional[Faction]:
        """
        Get a faction by ID.
        
        Args:
            faction_id: The ID of the faction
            
        Returns:
            The Faction object or None if not found
        """
        # Check cache first
        if self._is_faction_cached(faction_id):
            faction_dict = self._get_faction_from_cache(faction_id)
            if faction_dict:
                return self._dict_to_faction(faction_dict)
        
        # Fetch from Firebase
        faction_ref = db.reference(f"/factions/{faction_id}")
        faction_data = faction_ref.get()
        
        if not faction_data:
            return None
        
        # Cache it
        self._cache_faction(faction_id, faction_data)
        
        return self._dict_to_faction(faction_data)
    
    def get_factions_by_type(self, faction_type: str) -> List[Faction]:
        """
        Get all factions of a specific type.
        
        Args:
            faction_type: The type to filter by
            
        Returns:
            List of Faction objects of the type
        """
        # Validate faction type
        if faction_type not in self.FACTION_TYPES:
            raise ValueError(f"Invalid faction type: {faction_type}")
        
        # Query Firebase
        factions_ref = db.reference("/factions")
        all_factions = factions_ref.get() or {}
        
        result = []
        for faction_id, faction_data in all_factions.items():
            if faction_data.get("faction_type") == faction_type and faction_data.get("active", True):
                faction_data["id"] = faction_id
                result.append(self._dict_to_faction(faction_data))
        
        return result
    
    def set_relationship(self, faction_id: str, target_faction_id: str,
                        reputation: float, influence: float = None,
                        is_public: bool = True) -> FactionRelationship:
        """
        Set or update the relationship between two factions.
        
        Args:
            faction_id: ID of the source faction
            target_faction_id: ID of the target faction
            reputation: How the source views the target (-1.0 to 1.0)
            influence: How much influence source has over target (0.0 to 1.0)
            is_public: Whether this relationship is publicly known
            
        Returns:
            The created/updated FactionRelationship object
        """
        # Validate factions exist
        if not self.get_faction(faction_id):
            raise ValueError(f"Faction {faction_id} not found")
        if not self.get_faction(target_faction_id):
            raise ValueError(f"Faction {target_faction_id} not found")
        
        # Validate numeric parameters
        reputation = max(-1.0, min(1.0, reputation))
        
        # Get existing relationship if any
        existing = self._get_relationship(faction_id, target_faction_id)
        
        # If influence not provided, keep existing or calculate based on power
        if influence is None:
            if existing:
                influence = existing.influence
            else:
                # Calculate default influence based on power difference
                source_faction = self.get_faction(faction_id)
                target_faction = self.get_faction(target_faction_id)
                power_diff = source_faction.power_level - target_faction.power_level
                
                # Power difference affects base influence
                base_influence = 0.5 + (power_diff * 0.05)
                influence = max(0.0, min(1.0, base_influence))
        else:
            influence = max(0.0, min(1.0, influence))
        
        # Create or update relationship
        relationship = FactionRelationship(
            faction_id=faction_id,
            target_faction_id=target_faction_id,
            reputation=reputation,
            influence=influence,
            modified_at=datetime.utcnow(),
            is_public=is_public
        )
        
        # Store in Firebase
        self._store_relationship(relationship)
        
        # Clear cache
        self._clear_relationship_cache(faction_id, target_faction_id)
        
        # Emit event
        self.event_dispatcher.publish(FactionEvent(
            event_type="faction.relationship_changed",
            faction_id=faction_id,
            target_faction_id=target_faction_id,
            reputation=reputation,
            influence=influence,
            is_public=is_public
        ))
        
        return relationship
    
    def add_faction_goal(self, faction_id: str, title: str, description: str,
                         importance: int = 5, progress: float = 0.0,
                         opposing_factions: List[str] = None,
                         supporting_factions: List[str] = None,
                         metadata: Dict[str, Any] = None) -> FactionGoal:
        """
        Add a goal for a faction.
        
        Args:
            faction_id: ID of the faction
            title: Short title for the goal
            description: Detailed description of the goal
            importance: How important this goal is (1 to 10)
            progress: Current progress toward goal (0.0 to 1.0)
            opposing_factions: Faction IDs that oppose this goal
            supporting_factions: Faction IDs that support this goal
            metadata: Additional data for the goal
            
        Returns:
            The created FactionGoal object
        """
        # Validate faction exists
        if not self.get_faction(faction_id):
            raise ValueError(f"Faction {faction_id} not found")
        
        # Validate numeric parameters
        importance = max(1, min(10, importance))
        progress = max(0.0, min(1.0, progress))
        
        # Validate opposing factions
        if opposing_factions:
            for opp_id in opposing_factions:
                if not self.get_faction(opp_id):
                    raise ValueError(f"Opposing faction {opp_id} not found")
        
        # Validate supporting factions
        if supporting_factions:
            for sup_id in supporting_factions:
                if not self.get_faction(sup_id):
                    raise ValueError(f"Supporting faction {sup_id} not found")
        
        # Create goal
        goal = FactionGoal(
            faction_id=faction_id,
            title=title,
            description=description,
            importance=importance,
            progress=progress,
            opposing_factions=opposing_factions or [],
            supporting_factions=supporting_factions or [],
            metadata=metadata or {}
        )
        
        # Store in Firebase
        self._store_goal(goal)
        
        # Emit event
        self.event_dispatcher.publish(FactionEvent(
            event_type="faction.goal_added",
            faction_id=faction_id,
            goal_id=goal.id,
            goal_title=goal.title,
            importance=importance
        ))
        
        return goal
    
    def add_faction_resource(self, faction_id: str, name: str, resource_type: str,
                            amount: int = 1, quality: int = 5,
                            location_id: Optional[str] = None,
                            is_public: bool = True) -> FactionResource:
        """
        Add a resource for a faction.
        
        Args:
            faction_id: ID of the faction
            name: Name of the resource
            resource_type: Type of resource (from RESOURCE_TYPES)
            amount: Quantity of the resource
            quality: Quality of the resource (1 to 10)
            location_id: Optional region/location ID
            is_public: Whether this resource is publicly known
            
        Returns:
            The created FactionResource object
        """
        # Validate faction exists
        if not self.get_faction(faction_id):
            raise ValueError(f"Faction {faction_id} not found")
        
        # Validate resource type
        if resource_type not in self.RESOURCE_TYPES:
            raise ValueError(f"Invalid resource type: {resource_type}")
        
        # Validate numeric parameters
        amount = max(1, amount)
        quality = max(1, min(10, quality))
        
        # Create resource
        resource = FactionResource(
            faction_id=faction_id,
            name=name,
            resource_type=resource_type,
            amount=amount,
            quality=quality,
            location_id=location_id,
            is_public=is_public
        )
        
        # Store in Firebase
        self._store_resource(resource)
        
        # Emit event
        self.event_dispatcher.publish(FactionEvent(
            event_type="faction.resource_added",
            faction_id=faction_id,
            resource_id=resource.id,
            resource_name=resource.name,
            resource_type=resource_type,
            is_public=is_public
        ))
        
        return resource
    
    # ===== Internal Methods =====
    
    def _store_faction(self, faction: Faction):
        """
        Store a faction in Firebase.
        
        Args:
            faction: The Faction object to store
        """
        faction_dict = faction.dict()
        
        # Convert datetime objects to ISO format for Firebase
        faction_dict["created_at"] = faction_dict["created_at"].isoformat()
        
        # Remove id field (it's the key)
        faction_id = faction_dict.pop("id")
        
        # Store in Firebase
        faction_ref = db.reference(f"/factions/{faction_id}")
        faction_ref.set(faction_dict)
        
        # Update cache
        self._cache_faction(faction_id, faction_dict)
    
    def _store_relationship(self, relationship: FactionRelationship):
        """
        Store a faction relationship in Firebase.
        
        Args:
            relationship: The FactionRelationship object to store
        """
        rel_dict = relationship.dict()
        
        # Convert datetime objects to ISO format for Firebase
        rel_dict["modified_at"] = rel_dict["modified_at"].isoformat()
        
        # Store in Firebase
        rel_ref = db.reference(f"/faction_relationships/{relationship.faction_id}/{relationship.target_faction_id}")
        rel_ref.set(rel_dict)
    
    def _store_goal(self, goal: FactionGoal):
        """
        Store a faction goal in Firebase.
        
        Args:
            goal: The FactionGoal object to store
        """
        goal_dict = goal.dict()
        
        # Convert datetime objects to ISO format for Firebase
        goal_dict["created_at"] = goal_dict["created_at"].isoformat()
        goal_dict["modified_at"] = goal_dict["modified_at"].isoformat()
        
        # Remove id field (it's the key)
        goal_id = goal_dict.pop("id")
        
        # Store in Firebase
        goal_ref = db.reference(f"/faction_goals/{goal_id}")
        goal_ref.set(goal_dict)
    
    def _store_resource(self, resource: FactionResource):
        """
        Store a faction resource in Firebase.
        
        Args:
            resource: The FactionResource object to store
        """
        resource_dict = resource.dict()
        
        # Convert datetime objects to ISO format for Firebase
        resource_dict["created_at"] = resource_dict["created_at"].isoformat()
        
        # Remove id field (it's the key)
        resource_id = resource_dict.pop("id")
        
        # Store in Firebase
        resource_ref = db.reference(f"/faction_resources/{resource_id}")
        resource_ref.set(resource_dict)
    
    def _get_relationship(self, faction_id: str, target_faction_id: str) -> Optional[FactionRelationship]:
        """
        Get the relationship between two factions.
        
        Args:
            faction_id: ID of the source faction
            target_faction_id: ID of the target faction
            
        Returns:
            The FactionRelationship or None if not found
        """
        # Check cache first
        cache_key = f"{faction_id}:{target_faction_id}"
        if cache_key in self.relationship_cache:
            cached = self.relationship_cache[cache_key]
            if datetime.utcnow() - self.cache_timestamps.get(cache_key, datetime.min) < self.cache_ttl:
                return FactionRelationship(**cached)
        
        # Fetch from Firebase
        rel_ref = db.reference(f"/faction_relationships/{faction_id}/{target_faction_id}")
        rel_data = rel_ref.get()
        
        if not rel_data:
            return None
        
        # Convert ISO strings to datetime
        if isinstance(rel_data.get("modified_at"), str):
            rel_data["modified_at"] = datetime.fromisoformat(rel_data["modified_at"])
        
        # Cache it
        self.relationship_cache[cache_key] = rel_data
        self.cache_timestamps[cache_key] = datetime.utcnow()
        
        return FactionRelationship(**rel_data)
    
    def _dict_to_faction(self, faction_dict: Dict[str, Any]) -> Faction:
        """
        Convert a dict to a Faction object.
        
        Args:
            faction_dict: The faction dict
            
        Returns:
            Faction object
        """
        # Convert ISO strings to datetime
        if isinstance(faction_dict.get("created_at"), str):
            faction_dict["created_at"] = datetime.fromisoformat(faction_dict["created_at"])
        
        return Faction(**faction_dict)
    
    # ===== Cache Methods =====
    
    def _is_faction_cached(self, faction_id: str) -> bool:
        """
        Check if a faction is cached and not expired.
        
        Args:
            faction_id: The ID of the faction
            
        Returns:
            True if cached and not expired, False otherwise
        """
        if faction_id not in self.cache_timestamps:
            return False
        
        cache_time = self.cache_timestamps[faction_id]
        now = datetime.utcnow()
        
        return now - cache_time < self.cache_ttl
    
    def _cache_faction(self, faction_id: str, faction_dict: Dict[str, Any]):
        """
        Cache a faction.
        
        Args:
            faction_id: The ID of the faction
            faction_dict: The faction dict
        """
        self.faction_cache[faction_id] = faction_dict
        self.cache_timestamps[faction_id] = datetime.utcnow()
    
    def _clear_faction_cache(self, faction_id: str):
        """
        Clear the cache for a faction.
        
        Args:
            faction_id: The ID of the faction
        """
        if faction_id in self.faction_cache:
            del self.faction_cache[faction_id]
        
        if faction_id in self.cache_timestamps:
            del self.cache_timestamps[faction_id]
    
    def _clear_relationship_cache(self, faction_id: str, target_faction_id: str):
        """
        Clear the cache for a faction relationship.
        
        Args:
            faction_id: The ID of the source faction
            target_faction_id: The ID of the target faction
        """
        cache_key = f"{faction_id}:{target_faction_id}"
        if cache_key in self.relationship_cache:
            del self.relationship_cache[cache_key]
        
        if cache_key in self.cache_timestamps:
            del self.cache_timestamps[cache_key]
    
    def _get_faction_from_cache(self, faction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a faction from the cache.
        
        Args:
            faction_id: The ID of the faction
            
        Returns:
            Faction dict or None if not found
        """
        if not self._is_faction_cached(faction_id):
            return None
        
        return self.faction_cache.get(faction_id)


    def get_faction_goals(self, faction_id: str, include_completed: bool = False) -> List[FactionGoal]:
        """
        Get all goals for a faction.
        
        Args:
            faction_id: ID of the faction
            include_completed: Whether to include goals with 100% progress
            
        Returns:
            List of FactionGoal objects
        """
        # Validate faction exists
        if not self.get_faction(faction_id):
            raise ValueError(f"Faction {faction_id} not found")
        
        # Query Firebase
        goals_ref = db.reference("/faction_goals")
        all_goals = goals_ref.get() or {}
        
        result = []
        for goal_id, goal_data in all_goals.items():
            if goal_data.get("faction_id") == faction_id and goal_data.get("active", True):
                # Skip completed goals if not requested
                if not include_completed and goal_data.get("progress", 0.0) >= 1.0:
                    continue
                
                # Convert dates
                if isinstance(goal_data.get("created_at"), str):
                    goal_data["created_at"] = datetime.fromisoformat(goal_data["created_at"])
                if isinstance(goal_data.get("modified_at"), str):
                    goal_data["modified_at"] = datetime.fromisoformat(goal_data["modified_at"])
                
                goal_data["id"] = goal_id
                result.append(FactionGoal(**goal_data))
        
        # Sort by importance (descending)
        result.sort(key=lambda g: g.importance, reverse=True)
        
        return result
    
    def get_faction_resources(self, faction_id: str, resource_type: Optional[str] = None) -> List[FactionResource]:
        """
        Get resources for a faction.
        
        Args:
            faction_id: ID of the faction
            resource_type: Optional filter by resource type
            
        Returns:
            List of FactionResource objects
        """
        # Validate faction exists
        if not self.get_faction(faction_id):
            raise ValueError(f"Faction {faction_id} not found")
        
        # Validate resource type if provided
        if resource_type and resource_type not in self.RESOURCE_TYPES:
            raise ValueError(f"Invalid resource type: {resource_type}")
        
        # Query Firebase
        resources_ref = db.reference("/faction_resources")
        all_resources = resources_ref.get() or {}
        
        result = []
        for resource_id, resource_data in all_resources.items():
            if resource_data.get("faction_id") == faction_id:
                # Filter by type if requested
                if resource_type and resource_data.get("resource_type") != resource_type:
                    continue
                
                # Convert dates
                if isinstance(resource_data.get("created_at"), str):
                    resource_data["created_at"] = datetime.fromisoformat(resource_data["created_at"])
                
                resource_data["id"] = resource_id
                result.append(FactionResource(**resource_data))
        
        # Sort by quality * amount (descending)
        result.sort(key=lambda r: r.quality * r.amount, reverse=True)
        
        return result
    
    def get_faction_relationships(self, faction_id: str, 
                                 min_reputation: float = -1.0,
                                 include_hidden: bool = False) -> List[Dict[str, Any]]:
        """
        Get all relationships for a faction.
        
        Args:
            faction_id: ID of the faction
            min_reputation: Minimum reputation threshold
            include_hidden: Whether to include non-public relationships
            
        Returns:
            List of relationship details with faction info
        """
        # Validate faction exists
        if not self.get_faction(faction_id):
            raise ValueError(f"Faction {faction_id} not found")
        
        # Query Firebase
        rel_ref = db.reference(f"/faction_relationships/{faction_id}")
        all_rels = rel_ref.get() or {}
        
        result = []
        for target_id, rel_data in all_rels.items():
            # Skip if below reputation threshold
            if rel_data.get("reputation", 0.0) < min_reputation:
                continue
            
            # Skip if hidden and not requested
            if not include_hidden and not rel_data.get("is_public", True):
                continue
            
            # Get target faction
            target_faction = self.get_faction(target_id)
            if target_faction:
                # Convert dates
                if isinstance(rel_data.get("modified_at"), str):
                    rel_data["modified_at"] = datetime.fromisoformat(rel_data["modified_at"])
                
                result.append({
                    "relationship": FactionRelationship(**rel_data),
                    "faction": target_faction
                })
        
        # Sort by reputation (descending)
        result.sort(key=lambda r: r["relationship"].reputation, reverse=True)
        
        return result
    
    def calculate_faction_power(self, faction_id: str) -> Dict[str, Any]:
        """
        Calculate the effective power of a faction based on resources, stability, and relationships.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            Dict with power details
        """
        # Get the faction
        faction = self.get_faction(faction_id)
        if not faction:
            raise ValueError(f"Faction {faction_id} not found")
        
        # Base power from faction's power_level
        base_power = faction.power_level
        
        # Resource contribution
        resources = self.get_faction_resources(faction_id)
        resource_power = 0
        for r in resources:
            # Quality affects power more than quantity
            resource_power += (r.quality * 0.5) + (min(10, r.amount) * 0.1)
        
        resource_factor = min(2.0, resource_power / 10)  # Cap at doubling base power
        
        # Stability factor
        stability_factor = 0.5 + (faction.stability * 0.5)  # 0.5 to 1.0
        
        # Allies contribution
        relationships = self.get_faction_relationships(faction_id, min_reputation=0.5)
        ally_power = 0
        for rel in relationships:
            ally_faction = rel["faction"]
            ally_rep = rel["relationship"].reputation
            
            # Only strong allies contribute
            if ally_rep > 0.5:
                ally_contribution = ally_faction.power_level * ((ally_rep - 0.5) * 2)  # Scale 0.5-1.0 to 0-1.0
                ally_power += ally_contribution
        
        # Enemies detraction
        enemies = self.get_faction_relationships(faction_id, min_reputation=-1.0)
        enemy_power = 0
        for rel in enemies:
            enemy_faction = rel["faction"]
            enemy_rep = rel["relationship"].reputation
            
            # Only strong enemies detract
            if enemy_rep < -0.5:
                enemy_effect = enemy_faction.power_level * ((abs(enemy_rep) - 0.5) * 2)  # Scale 0.5-1.0 to 0-1.0
                enemy_power += enemy_effect
        
        enemy_factor = max(0.5, 1.0 - (enemy_power / 20))  # Can reduce power by up to 50%
        
        # Calculate total effective power
        effective_power = base_power * resource_factor * stability_factor * enemy_factor
        
        # Add ally bonus after other calculations
        ally_bonus = min(faction.power_level * 0.5, ally_power * 0.2)  # Cap at 50% of base power
        effective_power += ally_bonus
        
        return {
            "faction": faction.name,
            "base_power": base_power,
            "effective_power": round(effective_power, 1),
            "resource_factor": round(resource_factor, 2),
            "stability_factor": round(stability_factor, 2),
            "enemy_factor": round(enemy_factor, 2),
            "ally_bonus": round(ally_bonus, 1)
        }
    
    def get_faction_conflicts(self) -> List[Dict[str, Any]]:
        """
        Identify active conflicts between factions.
        
        Returns:
            List of faction conflicts with details
        """
        # Get all factions
        factions_ref = db.reference("/factions")
        all_factions = factions_ref.get() or {}
        
        # Get all relationships
        rels_ref = db.reference("/faction_relationships")
        all_rels = rels_ref.get() or {}
        
        conflicts = []
        
        # Look for mutual negative relationships
        for faction_id, targets in all_rels.items():
            # Skip if not active
            faction_data = all_factions.get(faction_id)
            if not faction_data or not faction_data.get("active", True):
                continue
            
            for target_id, rel_data in targets.items():
                # Skip if not active
                target_data = all_factions.get(target_id)
                if not target_data or not target_data.get("active", True):
                    continue
                
                # Check if relationship is negative
                if rel_data.get("reputation", 0.0) < -0.3:
                    # Check if target also has negative relationship
                    if (target_id in all_rels and 
                        faction_id in all_rels[target_id] and
                        all_rels[target_id][faction_id].get("reputation", 0.0) < -0.3):
                        
                        # Calculate conflict severity based on reputation and power
                        faction = self._dict_to_faction({**faction_data, "id": faction_id})
                        target = self._dict_to_faction({**target_data, "id": target_id})
                        
                        faction_reputation = rel_data.get("reputation", 0.0)
                        target_reputation = all_rels[target_id][faction_id].get("reputation", 0.0)
                        
                        severity = abs(faction_reputation) * abs(target_reputation) * (faction.power_level + target.power_level) / 10
                        
                        # Check if this conflict is already in the list (other direction)
                        if not any(c["faction_id"] == target_id and c["target_id"] == faction_id for c in conflicts):
                            conflicts.append({
                                "faction_id": faction_id,
                                "faction_name": faction.name,
                                "target_id": target_id,
                                "target_name": target.name,
                                "severity": round(severity, 2),
                                "faction_reputation": faction_reputation,
                                "target_reputation": target_reputation
                            })
        
        # Sort by severity (descending)
        conflicts.sort(key=lambda c: c["severity"], reverse=True)
        
        return conflicts
    
    def get_faction_narrative_context(self, faction_id: str = None, region_id: str = None,
                                     include_hidden: bool = False,
                                     max_factions: int = 3) -> str:
        """
        Generate narrative context for factions, either for a specific faction or region.
        
        Args:
            faction_id: Optional faction ID to focus on
            region_id: Optional region ID to focus on
            include_hidden: Whether to include hidden details
            max_factions: Maximum number of factions to include
            
        Returns:
            String of faction narrative context
        """
        context_lines = []
        
        if faction_id:
            # Get faction details
            faction = self.get_faction(faction_id)
            if not faction:
                return "Unknown faction."
            
            # Description
            context_lines.append(f"{faction.name}: {faction.description}")
            
            # Power level description
            if faction.power_level >= 9:
                power_desc = "a world-spanning power"
            elif faction.power_level >= 7:
                power_desc = "a major regional power"
            elif faction.power_level >= 5:
                power_desc = "a significant local power"
            elif faction.power_level >= 3:
                power_desc = "a minor but notable organization"
            else:
                power_desc = "a small, limited organization"
            
            context_lines.append(f"They are {power_desc}.")
            
            # Add secrecy if it's significant
            if faction.secrecy >= 7:
                context_lines.append(f"They operate in extreme secrecy; few know of their existence.")
            elif faction.secrecy >= 5:
                context_lines.append(f"They maintain many secrets and hidden operations.")
            
            # Add key values
            if faction.values:
                values_str = ", ".join(faction.values[:3])
                context_lines.append(f"Core values: {values_str}")
            
            # Add key relationships
            relationships = self.get_faction_relationships(faction_id, include_hidden=include_hidden)[:3]
            if relationships:
                context_lines.append("Key relationships:")
                for rel in relationships:
                    target = rel["faction"]
                    reputation = rel["relationship"].reputation
                    
                    if reputation > 0.7:
                        rel_desc = f"strong allies with"
                    elif reputation > 0.3:
                        rel_desc = f"friendly with"
                    elif reputation > -0.3:
                        rel_desc = f"neutral toward"
                    elif reputation > -0.7:
                        rel_desc = f"hostile toward"
                    else:
                        rel_desc = f"sworn enemies of"
                    
                    context_lines.append(f"- They are {rel_desc} {target.name}")
            
            # Add current goals
            goals = self.get_faction_goals(faction_id)[:2]
            if goals:
                context_lines.append("Current objectives:")
                for goal in goals:
                    progress_text = ""
                    if goal.progress > 0.8:
                        progress_text = " (nearly achieved)"
                    elif goal.progress > 0.5:
                        progress_text = " (significant progress)"
                    elif goal.progress > 0.2:
                        progress_text = " (some progress)"
                    
                    context_lines.append(f"- {goal.title}{progress_text}")
        
        elif region_id:
            # Get factions with presence in this region
            factions_ref = db.reference("/factions")
            all_factions = factions_ref.get() or {}
            
            regional_factions = []
            for faction_id, faction_data in all_factions.items():
                territories = faction_data.get("territory", [])
                if region_id in territories and faction_data.get("active", True):
                    # Skip highly secretive factions unless requested
                    if not include_hidden and faction_data.get("secrecy", 1) > 7:
                        continue
                    
                    faction_data["id"] = faction_id
                    regional_factions.append(self._dict_to_faction(faction_data))
            
            # Sort by power level (descending)
            regional_factions.sort(key=lambda f: f.power_level, reverse=True)
            
            # Take top factions
            top_factions = regional_factions[:max_factions]
            
            if top_factions:
                context_lines.append(f"Major factions in this region:")
                
                for i, faction in enumerate(top_factions):
                    if faction.power_level >= 8:
                        influence = "dominates"
                    elif faction.power_level >= 6:
                        influence = "holds significant power in"
                    elif faction.power_level >= 4:
                        influence = "maintains a notable presence in"
                    else:
                        influence = "has a minor presence in"
                    
                    context_lines.append(f"{i+1}. {faction.name} {influence} this area.")
                    
                    # Add a bit more detail
                    if faction.secrecy <= 3:  # Only for public factions
                        if faction.values and random.random() < 0.7:
                            value = random.choice(faction.values)
                            context_lines.append(f"   They are known for their {value}.")
                        elif faction.symbol and random.random() < 0.5:
                            context_lines.append(f"   Their symbol, {faction.symbol}, is a common sight.")
            
            # Add conflicts in region if any
            conflicts = self.get_faction_conflicts()
            regional_conflicts = []
            
            for conflict in conflicts:
                faction1_id = conflict["faction_id"]
                faction2_id = conflict["target_id"]
                
                # Check if both factions have presence in this region
                faction1 = all_factions.get(faction1_id, {})
                faction2 = all_factions.get(faction2_id, {})
                
                territories1 = faction1.get("territory", [])
                territories2 = faction2.get("territory", [])
                
                if region_id in territories1 and region_id in territories2:
                    regional_conflicts.append(conflict)
            
            if regional_conflicts and len(regional_conflicts) > 0:
                top_conflict = regional_conflicts[0]
                
                severity = top_conflict["severity"]
                if severity > 15:
                    conflict_desc = "are engaged in open warfare"
                elif severity > 10:
                    conflict_desc = "are in serious conflict"
                elif severity > 5:
                    conflict_desc = "are increasingly hostile toward each other"
                else:
                    conflict_desc = "have growing tensions"
                
                context_lines.append(f"Note: {top_conflict['faction_name']} and {top_conflict['target_name']} {conflict_desc} in this region.")
        
        return "\n".join(context_lines)


# Initialize the faction system
faction_system = FactionSystem.get_instance() 