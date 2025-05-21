"""
Rumor system for tracking rumor creation, spread, and mutation.

This module implements the rumor system for the game, allowing for rumor
creation, mutation, propagation, and tracking.
"""
from typing import Dict, List, Optional, Set, Any, TypeVar, Union, Callable
from enum import Enum
from datetime import datetime
import uuid
import json
import os
import random
import logging
import asyncio
from pydantic import BaseModel, Field, field_validator, ConfigDict

from backend.app.core.events.event_dispatcher import EventBase, EventDispatcher

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='RumorBase')

class RumorCategory(str, Enum):
    """Categories for rumor classification."""
    POLITICAL = "political"
    PERSONAL = "personal"
    SOCIAL = "social"
    MILITARY = "military"
    ECONOMIC = "economic"
    RELIGIOUS = "religious"
    HISTORICAL = "historical"
    GOSSIP = "gossip"
    OTHER = "other"

class RumorSeverity(str, Enum):
    """Severity levels for rumors."""
    TRIVIAL = "trivial"  # Minor gossip
    MINOR = "minor"      # Interesting but not consequential
    MODERATE = "moderate"  # Could affect reputation
    MAJOR = "major"      # Could affect relationships/alliances
    CRITICAL = "critical"  # Could trigger major events

class RumorVariant(BaseModel):
    """
    Represents a specific variant/mutation of a rumor.
    
    Rumors can mutate as they spread, with each variant potentially
    diverging from the original content.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    parent_variant_id: Optional[str] = None  # ID of variant this mutated from
    entity_id: str  # ID of entity that created this variant
    mutation_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __str__(self) -> str:
        """String representation of the variant."""
        return f"Variant({self.id[:8]}): {self.content[:50]}..."

class RumorSpread(BaseModel):
    """
    Tracks the spread of a rumor to an entity, including
    which variant they heard and how much they believe it.
    """
    entity_id: str
    variant_id: str
    heard_from_entity_id: Optional[str] = None
    believability: float = 0.5  # 0.0 (totally disbelieve) to 1.0 (fully believe)
    heard_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class Rumor(BaseModel):
    """
    Represents a rumor that can spread between entities.
    
    Rumors track their variants (mutations), spread patterns,
    and maintain a truth value separate from believability.
    
    Example:
        rumor = Rumor(
            originator_id="npc_123",
            original_content="The king has fallen ill",
            categories=[RumorCategory.POLITICAL],
            severity=RumorSeverity.MAJOR,
            truth_value=0.8
        )
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    originator_id: str
    original_content: str
    categories: List[RumorCategory] = [RumorCategory.OTHER]
    severity: RumorSeverity = RumorSeverity.MINOR
    truth_value: float = 0.5  # 0.0 (totally false) to 1.0 (totally true)
    
    # Tracking spread and mutations
    variants: List[RumorVariant] = Field(default_factory=list)
    spread: List[RumorSpread] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
        
    @field_validator('truth_value')
    @classmethod
    def validate_truth_value(cls, v):
        """Ensure truth value is between 0 and 1."""
        return max(0.0, min(1.0, v))
        
    def __str__(self) -> str:
        """String representation of the rumor."""
        short_id = self.id[:8] if self.id else "unknown"
        return f"Rumor({short_id}): {self.original_content[:50]}..."
        
    def get_latest_variant_id_for_entity(self, entity_id: str) -> Optional[str]:
        """Get the most recent variant ID heard by an entity."""
        # Filter spread records for this entity
        entity_spread = [s for s in self.spread if s.entity_id == entity_id]
        
        if not entity_spread:
            return None
            
        # Get the most recent spread
        latest_spread = max(entity_spread, key=lambda s: s.heard_at)
        return latest_spread.variant_id
        
    def get_variant_by_id(self, variant_id: str) -> Optional[RumorVariant]:
        """Get a specific variant by ID."""
        for variant in self.variants:
            if variant.id == variant_id:
                return variant
        return None
        
    def get_current_content_for_entity(self, entity_id: str) -> Optional[str]:
        """Get the content of the rumor as known to a specific entity."""
        variant_id = self.get_latest_variant_id_for_entity(entity_id)
        if not variant_id:
            return None
            
        variant = self.get_variant_by_id(variant_id)
        if not variant:
            return None
            
        return variant.content
        
    def get_believability_for_entity(self, entity_id: str) -> Optional[float]:
        """Get how strongly an entity believes this rumor."""
        # Filter spread records for this entity
        entity_spread = [s for s in self.spread if s.entity_id == entity_id]
        
        if not entity_spread:
            return None
            
        # Get the most recent spread
        latest_spread = max(entity_spread, key=lambda s: s.heard_at)
        return latest_spread.believability
    
    def entity_knows_rumor(self, entity_id: str) -> bool:
        """Check if an entity has heard this rumor."""
        return any(s.entity_id == entity_id for s in self.spread)

class RumorEvent(EventBase):
    """Event emitted when rumor operations occur."""
    rumor_id: str
    operation: str  # "created", "spread", "mutated", etc.
    entity_id: Optional[str] = None
    additional_data: Dict[str, Any] = Field(default_factory=dict)

class RumorSystem:
    """
    System for managing rumors in the game world.
    Emits RumorCreated, RumorSpread, RumorMutated events via the canonical EventDispatcher.
    """
    def __init__(self, 
                storage_path: str = "data/rumors/",
                event_dispatcher: Optional[EventDispatcher] = None,
                default_decay_rate: float = 0.05,
                gpt_mutation_handler: Optional[Callable] = None):
        """
        Initialize the rumor system.
        Args:
            storage_path: Directory for rumor storage
            event_dispatcher: Event dispatcher instance (uses canonical singleton if None)
            default_decay_rate: Default rate at which rumors decay (per update)
            gpt_mutation_handler: Optional function to handle GPT-based mutations
        """
        self.storage_path = storage_path
        self.event_dispatcher = event_dispatcher or EventDispatcher.get_instance()
        self.default_decay_rate = default_decay_rate
        self.gpt_mutation_handler = gpt_mutation_handler
        self._rumor_cache = {}  # id -> Rumor
        os.makedirs(storage_path, exist_ok=True)
        
        logger.info(f"RumorSystem initialized with storage at {storage_path}")
    
    async def create_rumor(self, 
                         originator_id: str,
                         content: str,
                         categories: List[Union[RumorCategory, str]] = [RumorCategory.OTHER],
                         severity: Union[RumorSeverity, str] = RumorSeverity.MINOR,
                         truth_value: float = 0.5) -> str:
        """
        Create a new rumor.
        
        Args:
            originator_id: ID of entity creating the rumor
            content: The content of the rumor
            categories: List of rumor categories
            severity: Severity level of the rumor
            truth_value: How true the rumor is (0.0-1.0)
            
        Returns:
            ID of the created rumor
        """
        # Normalize categories
        normalized_categories = []
        for cat in categories:
            if isinstance(cat, str):
                try:
                    normalized_categories.append(RumorCategory(cat))
                except ValueError:
                    normalized_categories.append(RumorCategory.OTHER)
                    logger.warning(f"Unknown rumor category: {cat}, using OTHER instead")
            else:
                normalized_categories.append(cat)
                
        # Normalize severity
        if isinstance(severity, str):
            try:
                normalized_severity = RumorSeverity(severity)
            except ValueError:
                normalized_severity = RumorSeverity.MINOR
                logger.warning(f"Unknown rumor severity: {severity}, using MINOR instead")
        else:
            normalized_severity = severity
            
        # Create initial variant
        initial_variant = RumorVariant(
            content=content,
            entity_id=originator_id
        )
        
        # Create rumor
        rumor = Rumor(
            originator_id=originator_id,
            original_content=content,
            categories=normalized_categories,
            severity=normalized_severity,
            truth_value=max(0.0, min(1.0, truth_value)),
            variants=[initial_variant],
            spread=[
                RumorSpread(
                    entity_id=originator_id,
                    variant_id=initial_variant.id,
                    believability=1.0  # Originator fully believes their own rumor
                )
            ]
        )
        
        # Cache the rumor
        self._rumor_cache[rumor.id] = rumor
        
        # Save to storage
        await self._save_rumor(rumor)
        
        # Emit event
        await self.event_dispatcher.publish(RumorEvent(
            event_type="rumor.created",
            rumor_id=rumor.id,
            operation="created",
            entity_id=originator_id
        ))
        
        logger.debug(f"Created rumor {rumor.id} from entity {originator_id}")
        return rumor.id 

    async def spread_rumor(self,
                        rumor_id: str,
                        from_entity_id: str,
                        to_entity_id: str,
                        variant_id: Optional[str] = None,
                        believability_modifier: float = 0.0,
                        mutate: bool = False,
                        mutation_probability: float = 0.2) -> bool:
        """
        Spread a rumor from one entity to another, potentially with mutation.
        
        Args:
            rumor_id: ID of the rumor to spread
            from_entity_id: ID of the entity spreading the rumor
            to_entity_id: ID of the entity receiving the rumor
            variant_id: Specific variant ID to spread (if None, uses latest known by from_entity)
            believability_modifier: Adjustment to believability (-1.0 to 1.0)
            mutate: Whether to allow rumor mutation during spread
            mutation_probability: Chance of mutation if mutate=True (0.0-1.0)
            
        Returns:
            bool: True if successfully spread, False otherwise
        """
        # Get the rumor
        rumor = await self.get_rumor(rumor_id)
        if not rumor:
            logger.warning(f"Cannot spread rumor {rumor_id}: not found")
            return False
            
        # Check if the source entity knows the rumor
        if not rumor.entity_knows_rumor(from_entity_id):
            logger.warning(f"Entity {from_entity_id} doesn't know rumor {rumor_id}")
            return False
            
        # Get the variant to spread
        spread_variant_id = variant_id
        
        # If no variant specified, use the latest one known by from_entity
        if not spread_variant_id:
            spread_variant_id = rumor.get_latest_variant_id_for_entity(from_entity_id)
            if not spread_variant_id:
                logger.warning(f"No variant found for entity {from_entity_id}")
                return False
        
        spread_variant = rumor.get_variant_by_id(spread_variant_id)
        if not spread_variant:
            logger.warning(f"Variant {spread_variant_id} not found in rumor {rumor_id}")
            return False
        
        # Determine if the rumor should mutate during transmission
        final_variant = spread_variant
        final_variant_id = spread_variant_id
        mutation_occurred = False
        
        if mutate and random.random() < mutation_probability:
            # Create a mutation
            new_variant = await self.mutate_rumor(
                rumor_id=rumor_id, 
                entity_id=to_entity_id,
                parent_variant_id=spread_variant_id
            )
            if new_variant:
                final_variant = new_variant
                final_variant_id = new_variant.id
                mutation_occurred = True
                logger.debug(f"Rumor {rumor_id} mutated during spread to {to_entity_id}")
        
        # Calculate believability
        # Base is either existing belief (if already heard) or average (0.5)
        base_believability = 0.5
        existing_believability = rumor.get_believability_for_entity(to_entity_id)
        if existing_believability is not None:
            base_believability = existing_believability
            
        # Apply modifier, ensuring result is between 0 and 1
        new_believability = max(0.0, min(1.0, base_believability + believability_modifier))
        
        # Add or update spread record
        new_spread = RumorSpread(
            entity_id=to_entity_id,
            variant_id=final_variant_id,
            heard_from_entity_id=from_entity_id,
            believability=new_believability
        )
        
        # Check if entity already knows this rumor
        already_knew = rumor.entity_knows_rumor(to_entity_id)
        
        # Add spread record
        rumor.spread.append(new_spread)
        
        # Update cache
        self._rumor_cache[rumor_id] = rumor
        
        # Save to storage
        await self._save_rumor(rumor)
        
        # Emit event
        event_type = "rumor.updated" if already_knew else "rumor.spread"
        await self.event_dispatcher.publish(RumorEvent(
            event_type=event_type,
            rumor_id=rumor_id,
            operation="spread",
            entity_id=to_entity_id,
            additional_data={
                "from_entity_id": from_entity_id,
                "variant_id": final_variant_id,
                "believability": new_believability,
                "mutation_occurred": mutation_occurred
            }
        ))
        
        logger.debug(f"Rumor {rumor_id} spread from {from_entity_id} to {to_entity_id}")
        return True

    async def _save_rumor(self, rumor):
        """Save a rumor to persistent storage."""
        try:
            # Ensure the directory exists
            os.makedirs(self.storage_path, exist_ok=True)
            
            # Convert to dict for serialization using model_dump()
            rumor_dict = rumor.model_dump()
            
            # Handle special serialization (sets, etc.)
            if "known_by" in rumor_dict and isinstance(rumor_dict["known_by"], set):
                rumor_dict["known_by"] = list(rumor_dict["known_by"])
                
            # Save to file
            rumor_file = os.path.join(self.storage_path, f"{rumor.id}.json")
            
            # Use asyncio file operations
            import aiofiles
            async with aiofiles.open(rumor_file, 'w') as f:
                await f.write(json.dumps(rumor_dict, default=str, indent=2))
                
            logger.debug(f"Saved rumor {rumor.id} to {rumor_file}")
        except Exception as e:
            logger.error(f"Error saving rumor {rumor.id}: {e}")
            raise
            
    async def get_rumor(self, rumor_id: str) -> Optional[Rumor]:
        """
        Get a rumor by ID, from cache or storage.
        
        Args:
            rumor_id: ID of the rumor to retrieve
            
        Returns:
            Rumor object if found, None otherwise
        """
        # Check cache first
        if rumor_id in self._rumor_cache:
            return self._rumor_cache[rumor_id]
            
        # Not in cache, try loading from storage
        try:
            rumor = await self._load_rumor(rumor_id)
            if rumor:
                # Add to cache
                self._rumor_cache[rumor_id] = rumor
                return rumor
        except Exception as e:
            logger.error(f"Error loading rumor {rumor_id}: {e}")
            
        return None
        
    async def _load_rumor(self, rumor_id: str) -> Optional[Rumor]:
        """
        Load a rumor from storage.
        
        Args:
            rumor_id: ID of the rumor to load
            
        Returns:
            Rumor object if found, None otherwise
        """
        rumor_file = os.path.join(self.storage_path, f"{rumor_id}.json")
        
        if not os.path.exists(rumor_file):
            logger.debug(f"Rumor file not found: {rumor_file}")
            return None
            
        try:
            # Use asyncio file operations
            import aiofiles
            async with aiofiles.open(rumor_file, 'r') as f:
                content = await f.read()
                rumor_dict = json.loads(content)
                
                # Handle enum types properly
                if 'categories' in rumor_dict:
                    categories = []
                    for cat in rumor_dict['categories']:
                        try:
                            categories.append(RumorCategory(cat))
                        except (ValueError, TypeError):
                            categories.append(RumorCategory.OTHER)
                    rumor_dict['categories'] = categories
                    
                if 'severity' in rumor_dict:
                    try:
                        rumor_dict['severity'] = RumorSeverity(rumor_dict['severity'])
                    except (ValueError, TypeError):
                        rumor_dict['severity'] = RumorSeverity.MINOR
                
                # Convert datetime strings to datetime objects
                for key in ['created_at']:
                    if key in rumor_dict and isinstance(rumor_dict[key], str):
                        try:
                            rumor_dict[key] = datetime.fromisoformat(rumor_dict[key].replace('Z', '+00:00'))
                        except (ValueError, TypeError):
                            rumor_dict[key] = datetime.utcnow()
                
                # Handle variants
                if 'variants' in rumor_dict:
                    variants = []
                    for variant_dict in rumor_dict['variants']:
                        if 'created_at' in variant_dict and isinstance(variant_dict['created_at'], str):
                            try:
                                variant_dict['created_at'] = datetime.fromisoformat(variant_dict['created_at'].replace('Z', '+00:00'))
                            except (ValueError, TypeError):
                                variant_dict['created_at'] = datetime.utcnow()
                        variants.append(RumorVariant(**variant_dict))
                    rumor_dict['variants'] = variants
                
                # Handle spread records
                if 'spread' in rumor_dict:
                    spread_records = []
                    for spread_dict in rumor_dict['spread']:
                        if 'heard_at' in spread_dict and isinstance(spread_dict['heard_at'], str):
                            try:
                                spread_dict['heard_at'] = datetime.fromisoformat(spread_dict['heard_at'].replace('Z', '+00:00'))
                            except (ValueError, TypeError):
                                spread_dict['heard_at'] = datetime.utcnow()
                        spread_records.append(RumorSpread(**spread_dict))
                    rumor_dict['spread'] = spread_records
                
                # Create rumor object
                rumor = Rumor(**rumor_dict)
                logger.debug(f"Loaded rumor {rumor_id} from {rumor_file}")
                return rumor
                
        except Exception as e:
            logger.error(f"Error loading rumor {rumor_id} from {rumor_file}: {e}")
            raise
        
        return None
        
    async def mutate_rumor(self, 
                         rumor_id: str, 
                         entity_id: str,
                         parent_variant_id: Optional[str] = None,
                         new_content: Optional[str] = None,
                         mutation_metadata: Dict[str, Any] = None) -> Optional[RumorVariant]:
        """
        Create a new variant (mutation) of a rumor.
        
        Args:
            rumor_id: ID of the rumor to mutate
            entity_id: ID of the entity creating the mutation
            parent_variant_id: ID of the variant to mutate from (if None, uses original)
            new_content: Content for the new variant (if None, uses AI or random mutation)
            mutation_metadata: Additional data about the mutation
            
        Returns:
            The new variant if successful, None otherwise
        """
        # Get the rumor
        rumor = await self.get_rumor(rumor_id)
        if not rumor:
            logger.warning(f"Cannot mutate rumor {rumor_id}: not found")
            return None
            
        # Get the parent variant
        parent_variant = None
        if parent_variant_id:
            parent_variant = rumor.get_variant_by_id(parent_variant_id)
            if not parent_variant:
                logger.warning(f"Parent variant {parent_variant_id} not found")
                return None
        else:
            # Use the original variant
            if len(rumor.variants) > 0:
                parent_variant = rumor.variants[0]
            else:
                logger.warning(f"Rumor {rumor_id} has no variants to mutate from")
                return None
        
        # Determine new content for the mutation
        mutated_content = new_content
        
        if mutated_content is None:
            # If no content provided, generate a mutation
            if self.gpt_mutation_handler and callable(self.gpt_mutation_handler):
                # Use GPT handler if available
                try:
                    mutated_content = await self.gpt_mutation_handler(
                        parent_variant.content,
                        rumor.categories,
                        rumor.severity
                    )
                except Exception as e:
                    logger.error(f"Error in GPT mutation handler: {e}")
                    # Fall back to basic mutation if GPT fails
                    mutated_content = self._generate_basic_mutation(parent_variant.content)
            else:
                # Basic random mutation
                mutated_content = self._generate_basic_mutation(parent_variant.content)
        
        # Create the new variant
        metadata = mutation_metadata or {}
        new_variant = RumorVariant(
            content=mutated_content,
            parent_variant_id=parent_variant.id,
            entity_id=entity_id,
            mutation_metadata=metadata
        )
        
        # Add to the rumor's variants
        rumor.variants.append(new_variant)
        
        # Update cache
        self._rumor_cache[rumor_id] = rumor
        
        # Save to storage
        await self._save_rumor(rumor)
        
        # Emit event
        await self.event_dispatcher.publish(RumorEvent(
            event_type="rumor.mutated",
            rumor_id=rumor_id,
            operation="mutated",
            entity_id=entity_id,
            additional_data={
                "variant_id": new_variant.id,
                "parent_variant_id": parent_variant.id
            }
        ))
        
        logger.debug(f"Rumor {rumor_id} mutated by entity {entity_id}")
        return new_variant
        
    def _generate_basic_mutation(self, original_content: str) -> str:
        """
        Generate a simple mutation of the original content.
        This is a fallback when no GPT handler is available.
        
        Args:
            original_content: The content to mutate
            
        Returns:
            Mutated content string
        """
        # Split into words
        words = original_content.split()
        
        if len(words) <= 3:
            # Too short to mutate effectively, just add something
            return f"{original_content} (allegedly)"
            
        # Possible mutation types
        mutation_types = [
            "exaggerate",
            "minimize",
            "confuse_details",
            "add_qualifier",
            "change_subject",
            "add_detail"
        ]
        
        mutation_type = random.choice(mutation_types)
        
        if mutation_type == "exaggerate":
            # Add intensifiers
            intensifiers = ["extremely", "definitely", "absolutely", "severely", "massively"]
            insert_pos = random.randint(1, min(5, len(words) - 1))
            words.insert(insert_pos, random.choice(intensifiers))
            
        elif mutation_type == "minimize":
            # Add reducers
            reducers = ["slightly", "somewhat", "barely", "hardly", "possibly"]
            insert_pos = random.randint(1, min(5, len(words) - 1))
            words.insert(insert_pos, random.choice(reducers))
            
        elif mutation_type == "confuse_details":
            # Change a number or name if present
            for i, word in enumerate(words):
                if word.isdigit():
                    # Modify a number
                    num = int(word)
                    words[i] = str(num + random.randint(-num//2 if num > 4 else -1, num))
                    break
                elif word[0].isupper() and i > 0:
                    # Might be a name, replace with a generic one
                    replacements = ["someone", "the person", "that individual", "they"]
                    words[i] = random.choice(replacements)
                    break
                    
        elif mutation_type == "add_qualifier":
            # Add uncertainty
            qualifiers = [
                "I think", "They say", "I heard", "Supposedly", 
                "Rumor has it", "Allegedly", "Apparently"
            ]
            words.insert(0, random.choice(qualifiers))
            
        elif mutation_type == "change_subject":
            # Change who the rumor is about
            subjects = ["he", "she", "they", "someone", "the person", "that individual"]
            for i, word in enumerate(words):
                if word.lower() in ["he", "she", "they", "him", "her"]:
                    words[i] = random.choice(subjects)
                    break
                    
        elif mutation_type == "add_detail":
            # Add a random detail
            details = [
                "last week", "in secret", "discreetly", "when no one was looking",
                "at night", "reluctantly", "eagerly", "without telling anyone"
            ]
            insert_pos = min(len(words) - 1, random.randint(len(words)//2, len(words)))
            words.insert(insert_pos, random.choice(details))
            
        # Combine back into a string
        return " ".join(words)
        
    async def get_rumors_for_entity(self, 
                                 entity_id: str,
                                 categories: Optional[List[Union[RumorCategory, str]]] = None,
                                 min_believability: float = 0.0,
                                 max_rumors: int = 50) -> List[Dict[str, Any]]:
        """
        Get all rumors known by a specific entity.
        
        Args:
            entity_id: ID of the entity
            categories: Optional filter for rumor categories (if None, returns all)
            min_believability: Minimum believability threshold (0.0-1.0)
            max_rumors: Maximum number of rumors to return
            
        Returns:
            List of rumor data dictionaries with content and metadata
        """
        result = []
        count = 0
        
        # Load all rumors from storage if cache is empty
        if not self._rumor_cache:
            await self._preload_rumors()
            
        # Normalize categories for filtering
        normalized_categories = None
        if categories:
            normalized_categories = []
            for cat in categories:
                if isinstance(cat, str):
                    try:
                        normalized_categories.append(RumorCategory(cat))
                    except ValueError:
                        normalized_categories.append(RumorCategory.OTHER)
                else:
                    normalized_categories.append(cat)
        
        # Check each rumor
        for rumor_id, rumor in self._rumor_cache.items():
            # Skip if entity doesn't know this rumor
            if not rumor.entity_knows_rumor(entity_id):
                continue
                
            # Check believability threshold
            believability = rumor.get_believability_for_entity(entity_id)
            if believability is None or believability < min_believability:
                continue
                
            # Check category filter
            if normalized_categories and not any(cat in rumor.categories for cat in normalized_categories):
                continue
                
            # Get content as known to this entity
            content = rumor.get_current_content_for_entity(entity_id)
            if not content:
                continue
                
            # Add to result
            result.append({
                "rumor_id": rumor.id,
                "content": content,
                "categories": [cat.value for cat in rumor.categories],
                "severity": rumor.severity.value,
                "believability": believability,
                "heard_at": next((s.heard_at for s in rumor.spread 
                                  if s.entity_id == entity_id), datetime.utcnow())
            })
            
            count += 1
            if count >= max_rumors:
                break
                
        # Sort by recency (most recent first)
        result.sort(key=lambda x: x["heard_at"], reverse=True)
        
        return result
        
    async def _preload_rumors(self) -> None:
        """Load all rumors from storage into the cache."""
        if not os.path.exists(self.storage_path):
            logger.debug(f"Rumor storage path does not exist: {self.storage_path}")
            return
            
        try:
            rumor_files = [f for f in os.listdir(self.storage_path) 
                          if f.endswith('.json')]
            
            logger.info(f"Found {len(rumor_files)} rumor files in {self.storage_path}")
            loaded_count = 0
            error_count = 0
            
            for rumor_file in rumor_files:
                try:
                    rumor_id = rumor_file.replace('.json', '')
                    rumor = await self._load_rumor(rumor_id)
                    if rumor:
                        self._rumor_cache[rumor_id] = rumor
                        loaded_count += 1
                    else:
                        error_count += 1
                        logger.warning(f"Failed to load rumor from {rumor_file}: Returned None")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error loading rumor {rumor_file}: {str(e)}")
            
            logger.info(f"Preloaded {loaded_count} rumors into cache. Errors: {error_count}")
        except Exception as e:
            logger.error(f"Error loading rumors from {self.storage_path}: {str(e)}")

    async def update_believability(self, 
                               rumor_id: str, 
                               entity_id: str, 
                               adjustment: float) -> bool:
        """
        Adjust how strongly an entity believes a rumor.
        
        Args:
            rumor_id: ID of the rumor
            entity_id: ID of the entity whose belief is changing
            adjustment: Amount to adjust believability (-1.0 to 1.0)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get the rumor
        rumor = await self.get_rumor(rumor_id)
        if not rumor:
            logger.warning(f"Cannot update believability: rumor {rumor_id} not found")
            return False
            
        # Check if the entity knows the rumor
        if not rumor.entity_knows_rumor(entity_id):
            logger.warning(f"Cannot update believability: entity {entity_id} doesn't know rumor {rumor_id}")
            return False
            
        # Get current believability
        current = rumor.get_believability_for_entity(entity_id)
        if current is None:
            logger.warning(f"Cannot determine current believability for entity {entity_id}")
            return False
            
        # Calculate new believability, ensuring it stays between 0 and 1
        new_believability = max(0.0, min(1.0, current + adjustment))
        
        # Find the most recent spread record for this entity
        spread_records = [s for s in rumor.spread if s.entity_id == entity_id]
        if not spread_records:
            logger.warning(f"No spread records found for entity {entity_id}")
            return False
            
        latest_spread = max(spread_records, key=lambda s: s.heard_at)
        
        # Create a new spread record with updated believability but same variant
        new_spread = RumorSpread(
            entity_id=entity_id,
            variant_id=latest_spread.variant_id,
            heard_from_entity_id=latest_spread.heard_from_entity_id,
            believability=new_believability
        )
        
        # Add the new record
        rumor.spread.append(new_spread)
        
        # Update cache
        self._rumor_cache[rumor_id] = rumor
        
        # Save to storage
        await self._save_rumor(rumor)
        
        # Emit event
        await self.event_dispatcher.publish(RumorEvent(
            event_type="rumor.believability_changed",
            rumor_id=rumor_id,
            operation="believability_changed",
            entity_id=entity_id,
            additional_data={
                "previous_believability": current,
                "new_believability": new_believability,
                "adjustment": adjustment
            }
        ))
        
        logger.debug(f"Updated believability for entity {entity_id} on rumor {rumor_id}: {current} → {new_believability}")
        return True
        
    async def delete_rumor(self, rumor_id: str) -> bool:
        """
        Permanently delete a rumor.
        
        Args:
            rumor_id: ID of the rumor to delete
            
        Returns:
            bool: True if successfully deleted, False otherwise
        """
        # Check if in cache
        if rumor_id in self._rumor_cache:
            del self._rumor_cache[rumor_id]
            
        # Delete from storage
        rumor_file = os.path.join(self.storage_path, f"{rumor_id}.json")
        if os.path.exists(rumor_file):
            try:
                os.remove(rumor_file)
                logger.debug(f"Deleted rumor file: {rumor_file}")
                
                # Emit event
                await self.event_dispatcher.publish(RumorEvent(
                    event_type="rumor.deleted",
                    rumor_id=rumor_id,
                    operation="deleted"
                ))
                
                return True
            except Exception as e:
                logger.error(f"Error deleting rumor file {rumor_file}: {e}")
                
        return False
        
    async def query_rumors(self, 
                       search_text: Optional[str] = None,
                       categories: Optional[List[Union[RumorCategory, str]]] = None,
                       severity: Optional[Union[RumorSeverity, str]] = None,
                       min_truth: float = 0.0,
                       entity_knows: Optional[str] = None,
                       limit: int = 50) -> List[Dict[str, Any]]:
        """
        Query rumors with optional filtering.
        
        Args:
            search_text: Optional text to search for in rumor content
            categories: Optional list of categories to filter by
            severity: Optional minimum severity level
            min_truth: Minimum truth value (0.0-1.0)
            entity_knows: Optional entity ID to filter for rumors known by this entity
            limit: Maximum number of results to return
            
        Returns:
            List of rumor dictionaries
        """
        if not self._rumor_cache:
            await self._preload_rumors()
            
        # Normalize categories input
        norm_categories = None
        if categories:
            norm_categories = []
            for cat in categories:
                if isinstance(cat, str):
                    try:
                        norm_categories.append(RumorCategory(cat.lower()))
                    except ValueError:
                        logger.warning(f"Invalid category: {cat}")
                else:
                    norm_categories.append(cat)
                    
        # Normalize severity input
        norm_severity = None
        if severity:
            if isinstance(severity, str):
                try:
                    norm_severity = RumorSeverity(severity.lower())
                except ValueError:
                    logger.warning(f"Invalid severity: {severity}")
            else:
                norm_severity = severity
        
        # Prepare search text for case-insensitive search
        search_lower = search_text.lower() if search_text else None
                    
        results = []
        
        for rumor in self._rumor_cache.values():
            # Filter by truth value
            if rumor.truth_value < min_truth:
                continue
                
            # Filter by severity
            if norm_severity and not self._severity_is_at_least(rumor.severity, norm_severity):
                continue
                
            # Filter by categories (must match at least one)
            if norm_categories and not any(cat in rumor.categories for cat in norm_categories):
                continue
                
            # Filter by search text (in original or any variant)
            if search_lower:
                content_matches = rumor.original_content.lower().find(search_lower) >= 0
                if not content_matches:
                    # Check variants
                    variant_matches = any(
                        variant.content.lower().find(search_lower) >= 0
                        for variant in rumor.variants
                    )
                    if not variant_matches:
                        continue
                        
            # Filter by entity knowledge
            if entity_knows and not rumor.entity_knows_rumor(entity_knows):
                continue
                
            # Add to results
            result = {
                "id": rumor.id,
                "created_at": rumor.created_at.isoformat(),
                "originator_id": rumor.originator_id,
                "original_content": rumor.original_content,
                "categories": [cat.value for cat in rumor.categories],
                "severity": rumor.severity.value,
                "truth_value": rumor.truth_value,
                "variant_count": len(rumor.variants),
                "spread_count": len(rumor.spread)
            }
            
            results.append(result)
            
            # Apply limit
            if len(results) >= limit:
                break
                
        return results
        
    def _severity_is_at_least(self, severity: RumorSeverity, min_severity: RumorSeverity) -> bool:
        """Check if a severity level is at least the minimum required level."""
        severity_order = {
            RumorSeverity.TRIVIAL: 0,
            RumorSeverity.MINOR: 1,
            RumorSeverity.MODERATE: 2,
            RumorSeverity.MAJOR: 3,
            RumorSeverity.CRITICAL: 4
        }
        
        return severity_order.get(severity, 0) >= severity_order.get(min_severity, 0)
    
    async def decay_rumors(self, decay_rate: Optional[float] = None) -> int:
        """
        Apply natural decay to believability of all rumors over time.
        
        This represents the natural tendency of people to forget or doubt rumors
        over time unless they are reinforced.
        
        Args:
            decay_rate: Rate at which believability decays (0.0-1.0).
                        If None, uses the default_decay_rate set in constructor.
        
        Returns:
            int: Number of rumor-entity relationships affected by decay
        """
        if decay_rate is None:
            decay_rate = self.default_decay_rate
            
        decay_rate = max(0.0, min(1.0, decay_rate))  # Clamp between 0 and 1
        
        affected_count = 0
        updated_rumors = []
        
        try:
            # Process each rumor in the cache
            for rumor_id, rumor in self._rumor_cache.items():
                changed = False
                
                # Apply decay to each entity's believability
                for spread_record in rumor.spread:
                    # Skip if believability is already 0
                    if spread_record.believability <= 0:
                        continue
                        
                    # Apply decay
                    original_believability = spread_record.believability
                    spread_record.believability = max(0.0, spread_record.believability - decay_rate)
                    
                    # Check if believability actually changed (beyond floating point error)
                    if abs(original_believability - spread_record.believability) > 0.001:
                        changed = True
                        affected_count += 1
                
                # If any believability values changed, save the rumor
                if changed:
                    updated_rumors.append(rumor)
                    
            # Save all updated rumors in parallel
            if updated_rumors:
                tasks = [self._save_rumor(rumor) for rumor in updated_rumors]
                await asyncio.gather(*tasks)
                
                logger.info(f"Applied decay rate {decay_rate} to {affected_count} " 
                           f"entity relationships across {len(updated_rumors)} rumors")
            else:
                logger.info(f"No rumors affected by decay rate {decay_rate}")
                
            return affected_count
        except Exception as e:
            logger.error(f"Error applying rumor decay: {str(e)}")
            return 0 
