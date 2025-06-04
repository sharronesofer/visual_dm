"""
Rumor system for tracking rumor creation, spread, and mutation.

This module implements the rumor system for the game, allowing for rumor
creation, mutation, propagation, and tracking.

Moved from backend/systems/rumor/services/rumor_system.py during refactoring.
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

# Import models from the models directory
from backend.infrastructure.systems.rumor.models.rumor import (
    Rumor, RumorCategory, RumorSeverity, RumorVariant, RumorSpread
)
from backend.infrastructure.systems.rumor.repositories.rumor_repository import RumorRepository
from backend.infrastructure.events.core.event_base import EventBase
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='RumorBase')

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
                repository: Optional[RumorRepository] = None,
                event_dispatcher: Optional[EventDispatcher] = None,
                default_decay_rate: float = 0.05,
                gpt_mutation_handler: Optional[Callable] = None):
        """
        Initialize the rumor system.
        Args:
            repository: Repository for rumor persistence (creates default if None)
            event_dispatcher: Event dispatcher instance (uses canonical singleton if None)
            default_decay_rate: Default rate at which rumors decay (per update)
            gpt_mutation_handler: Optional function to handle GPT-based mutations
        """
        self.repository = repository or RumorRepository()
        self.event_dispatcher = event_dispatcher or EventDispatcher.get_instance()
        self.default_decay_rate = default_decay_rate
        self.gpt_mutation_handler = gpt_mutation_handler
        self._rumor_cache = {}  # id -> Rumor
        
        logger.info(f"RumorSystem initialized with repository")
    
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
        await self.repository.save_rumor(rumor)
        
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
                rumor_id, 
                to_entity_id, 
                parent_variant_id=spread_variant_id
            )
            if new_variant:
                final_variant = new_variant
                final_variant_id = new_variant.id
                mutation_occurred = True
        
        # Calculate final believability
        base_believability = rumor.get_believability_for_entity(from_entity_id)
        final_believability = max(0.0, min(1.0, base_believability + believability_modifier))
        
        # Add spread record
        rumor.spread.append(RumorSpread(
            entity_id=to_entity_id,
            variant_id=final_variant_id,
            believability=final_believability,
            source_entity_id=from_entity_id
        ))
        
        # Update cache and storage
        self._rumor_cache[rumor.id] = rumor
        await self.repository.save_rumor(rumor)
        
        # Emit spread event
        await self.event_dispatcher.publish(RumorEvent(
            event_type="rumor.spread",
            rumor_id=rumor_id,
            operation="spread",
            entity_id=to_entity_id,
            additional_data={
                "from_entity": from_entity_id,
                "variant_id": final_variant_id,
                "believability": final_believability,
                "mutation_occurred": mutation_occurred
            }
        ))
        
        logger.debug(f"Spread rumor {rumor_id} from {from_entity_id} to {to_entity_id}")
        return True

    async def get_rumor(self, rumor_id: str) -> Optional[Rumor]:
        """
        Get a rumor by ID.
        
        Args:
            rumor_id: ID of the rumor to retrieve
            
        Returns:
            Rumor object if found, None otherwise
        """
        # Check cache first
        if rumor_id in self._rumor_cache:
            return self._rumor_cache[rumor_id]
        
        # Load from repository
        rumor = await self.repository.get_rumor(rumor_id)
        if rumor:
            self._rumor_cache[rumor_id] = rumor
        
        return rumor

    async def mutate_rumor(self, 
                         rumor_id: str, 
                         entity_id: str,
                         parent_variant_id: Optional[str] = None,
                         new_content: Optional[str] = None,
                         mutation_metadata: Dict[str, Any] = None) -> Optional[RumorVariant]:
        """
        Create a mutation of a rumor.
        
        Args:
            rumor_id: ID of the rumor to mutate
            entity_id: ID of the entity creating the mutation
            parent_variant_id: ID of the variant being mutated (if None, uses latest)
            new_content: Specific content for the mutation (if None, generates automatically)
            mutation_metadata: Additional metadata about the mutation
            
        Returns:
            New RumorVariant if successful, None otherwise
        """
        rumor = await self.get_rumor(rumor_id)
        if not rumor:
            logger.warning(f"Cannot mutate rumor {rumor_id}: not found")
            return None
        
        # Determine parent variant
        if parent_variant_id:
            parent_variant = rumor.get_variant_by_id(parent_variant_id)
        else:
            # Use the latest variant known by the entity
            parent_variant_id = rumor.get_latest_variant_id_for_entity(entity_id)
            parent_variant = rumor.get_variant_by_id(parent_variant_id) if parent_variant_id else None
        
        if not parent_variant:
            logger.warning(f"No parent variant found for mutation")
            return None
        
        # Generate mutation content
        if new_content is None:
            if self.gpt_mutation_handler:
                # Use GPT for sophisticated mutation
                try:
                    new_content = await self.gpt_mutation_handler(
                        original_content=parent_variant.content,
                        rumor_context={
                            "severity": rumor.severity.value,
                            "categories": [cat.value for cat in rumor.categories],
                            "truth_value": rumor.truth_value
                        },
                        entity_id=entity_id,
                        metadata=mutation_metadata or {}
                    )
                except Exception as e:
                    logger.error(f"GPT mutation failed: {e}")
                    new_content = self._generate_basic_mutation(parent_variant.content)
            else:
                # Use basic mutation
                new_content = self._generate_basic_mutation(parent_variant.content)
        
        # Create new variant
        new_variant = RumorVariant(
            content=new_content,
            entity_id=entity_id,
            parent_variant_id=parent_variant.id,
            mutation_metadata=mutation_metadata or {}
        )
        
        # Add to rumor
        rumor.variants.append(new_variant)
        
        # Update cache and storage
        self._rumor_cache[rumor.id] = rumor
        await self.repository.save_rumor(rumor)
        
        # Emit mutation event
        await self.event_dispatcher.publish(RumorEvent(
            event_type="rumor.mutated",
            rumor_id=rumor_id,
            operation="mutated",
            entity_id=entity_id,
            additional_data={
                "variant_id": new_variant.id,
                "parent_variant_id": parent_variant.id,
                "original_content": parent_variant.content,
                "mutated_content": new_content
            }
        ))
        
        logger.debug(f"Created mutation {new_variant.id} for rumor {rumor_id}")
        return new_variant

    def _generate_basic_mutation(self, original_content: str) -> str:
        """
        Generate a basic mutation of rumor content using simple text transformations.
        
        Args:
            original_content: Original rumor content
            
        Returns:
            Mutated content
        """
        mutations = [
            # Certainty modifiers
            ("is", "might be"),
            ("was", "supposedly was"),
            ("will", "could"),
            ("definitely", "probably"),
            ("certainly", "possibly"),
            ("always", "often"),
            ("never", "rarely"),
            
            # Location vagueness
            ("at the", "somewhere near the"),
            ("in the", "around the"),
            ("near", "somewhere close to"),
            
            # Time vagueness
            ("yesterday", "recently"),
            ("today", "lately"),
            ("tomorrow", "soon"),
            ("last week", "not long ago"),
            
            # Source uncertainty
            ("I saw", "someone saw"),
            ("I heard", "word is that"),
            ("he said", "they say"),
            ("she told me", "I heard that"),
            
            # Quantity exaggeration/reduction
            ("a few", "several"),
            ("many", "quite a few"),
            ("some", "a number of"),
            ("all", "most"),
            
            # Emotional amplification/reduction
            ("angry", "quite upset"),
            ("happy", "pleased"),
            ("sad", "rather down"),
            ("excited", "enthusiastic"),
        ]
        
        # Apply 1-3 random mutations
        mutated_content = original_content
        num_mutations = random.randint(1, min(3, len(mutations)))
        
        applied_mutations = random.sample(mutations, num_mutations)
        for old_phrase, new_phrase in applied_mutations:
            if old_phrase in mutated_content.lower():
                # Case-sensitive replacement
                mutated_content = mutated_content.replace(old_phrase, new_phrase)
        
        # Add uncertainty markers occasionally
        if random.random() < 0.3:
            uncertainty_markers = [
                " (or so I heard)",
                " (though I'm not certain)",
                " (if the rumors are true)",
                " (according to some)",
                " (allegedly)"
            ]
            mutated_content += random.choice(uncertainty_markers)
        
        return mutated_content

    async def get_rumors_for_entity(self, 
                                 entity_id: str,
                                 categories: Optional[List[Union[RumorCategory, str]]] = None,
                                 min_believability: float = 0.0,
                                 max_rumors: int = 50) -> List[Dict[str, Any]]:
        """
        Get all rumors known by a specific entity.
        
        Args:
            entity_id: ID of the entity
            categories: Filter by categories (if None, includes all)
            min_believability: Minimum believability threshold
            max_rumors: Maximum number of rumors to return
            
        Returns:
            List of rumor dictionaries with entity-specific information
        """
        # Ensure rumors are loaded
        await self._preload_rumors()
        
        entity_rumors = []
        
        for rumor in self._rumor_cache.values():
            # Check if entity knows this rumor
            if not rumor.entity_knows_rumor(entity_id):
                continue
            
            # Get entity-specific information
            believability = rumor.get_believability_for_entity(entity_id)
            if believability < min_believability:
                continue
            
            # Filter by categories if specified
            if categories:
                normalized_categories = []
                for cat in categories:
                    if isinstance(cat, str):
                        try:
                            normalized_categories.append(RumorCategory(cat))
                        except ValueError:
                            continue
                    else:
                        normalized_categories.append(cat)
                
                if not any(cat in rumor.categories for cat in normalized_categories):
                    continue
            
            # Get the variant known by this entity
            variant_id = rumor.get_latest_variant_id_for_entity(entity_id)
            variant = rumor.get_variant_by_id(variant_id) if variant_id else None
            
            entity_rumors.append({
                "rumor_id": rumor.id,
                "content": variant.content if variant else rumor.original_content,
                "variant_id": variant_id,
                "believability": believability,
                "categories": [cat.value for cat in rumor.categories],
                "severity": rumor.severity.value,
                "truth_value": rumor.truth_value,
                "created_at": rumor.created_at.isoformat(),
                "spread_count": len(rumor.spread)
            })
        
        # Sort by believability (descending) and limit results
        entity_rumors.sort(key=lambda x: x["believability"], reverse=True)
        return entity_rumors[:max_rumors]

    async def _preload_rumors(self) -> None:
        """
        Preload rumors from repository into cache.
        """
        if not self._rumor_cache:
            try:
                all_rumors = await self.repository.get_all_rumors()
                for rumor in all_rumors:
                    self._rumor_cache[rumor.id] = rumor
                logger.debug(f"Preloaded {len(all_rumors)} rumors into cache")
            except Exception as e:
                logger.error(f"Failed to preload rumors: {e}")

    async def update_believability(self, 
                               rumor_id: str, 
                               entity_id: str, 
                               adjustment: float) -> bool:
        """
        Update the believability of a rumor for a specific entity.
        
        Args:
            rumor_id: ID of the rumor
            entity_id: ID of the entity
            adjustment: Believability adjustment (-1.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        rumor = await self.get_rumor(rumor_id)
        if not rumor:
            return False
        
        # Find the entity's spread record
        entity_spread = None
        for spread in rumor.spread:
            if spread.entity_id == entity_id:
                entity_spread = spread
                break
        
        if not entity_spread:
            logger.warning(f"Entity {entity_id} doesn't know rumor {rumor_id}")
            return False
        
        # Update believability
        old_believability = entity_spread.believability
        entity_spread.believability = max(0.0, min(1.0, old_believability + adjustment))
        
        # Update cache and storage
        self._rumor_cache[rumor.id] = rumor
        await self.repository.save_rumor(rumor)
        
        logger.debug(f"Updated believability for rumor {rumor_id}, entity {entity_id}: {old_believability} -> {entity_spread.believability}")
        return True

    async def decay_rumors(self, 
                        decay_rate: Optional[float] = None,
                        entity_ids: Optional[List[str]] = None) -> int:
        """
        Apply decay to rumor believability over time.
        
        Args:
            decay_rate: Rate of decay (if None, uses default)
            entity_ids: Specific entities to apply decay to (if None, applies to all)
            
        Returns:
            Number of rumors affected by decay
        """
        if decay_rate is None:
            decay_rate = self.default_decay_rate
        
        await self._preload_rumors()
        
        affected_count = 0
        
        for rumor in self._rumor_cache.values():
            rumor_affected = False
            
            for spread in rumor.spread:
                # Skip if filtering by specific entities
                if entity_ids and spread.entity_id not in entity_ids:
                    continue
                
                # Apply decay
                old_believability = spread.believability
                spread.believability = max(0.0, spread.believability - decay_rate)
                
                if spread.believability != old_believability:
                    rumor_affected = True
            
            if rumor_affected:
                # Update storage
                await self.repository.save_rumor(rumor)
                affected_count += 1
        
        logger.debug(f"Applied decay to {affected_count} rumors")
        return affected_count

    async def delete_rumor(self, rumor_id: str) -> bool:
        """
        Delete a rumor completely.
        
        Args:
            rumor_id: ID of the rumor to delete
            
        Returns:
            True if successful, False otherwise
        """
        rumor = await self.get_rumor(rumor_id)
        if not rumor:
            return False
        
        # Remove from cache
        if rumor_id in self._rumor_cache:
            del self._rumor_cache[rumor_id]
        
        # Remove from storage
        success = await self.repository.delete_rumor(rumor_id)
        
        if success:
            # Emit deletion event
            await self.event_dispatcher.publish(RumorEvent(
                event_type="rumor.deleted",
                rumor_id=rumor_id,
                operation="deleted"
            ))
            
            logger.debug(f"Deleted rumor {rumor_id}")
        
        return success

    async def query_rumors(self, 
                       search_text: Optional[str] = None,
                       categories: Optional[List[Union[RumorCategory, str]]] = None,
                       severity: Optional[Union[RumorSeverity, str]] = None,
                       min_truth: float = 0.0,
                       entity_knows: Optional[str] = None,
                       limit: int = 50) -> List[Dict[str, Any]]:
        """
        Query rumors with various filters.
        
        Args:
            search_text: Text to search for in rumor content
            categories: Filter by categories
            severity: Filter by minimum severity
            min_truth: Minimum truth value
            entity_knows: Filter to rumors known by specific entity
            limit: Maximum number of results
            
        Returns:
            List of matching rumors
        """
        await self._preload_rumors()
        
        results = []
        
        # Normalize severity filter
        min_severity = None
        if severity:
            if isinstance(severity, str):
                try:
                    min_severity = RumorSeverity(severity)
                except ValueError:
                    logger.warning(f"Unknown severity filter: {severity}")
            else:
                min_severity = severity
        
        # Normalize category filters
        category_filter = None
        if categories:
            category_filter = []
            for cat in categories:
                if isinstance(cat, str):
                    try:
                        category_filter.append(RumorCategory(cat))
                    except ValueError:
                        logger.warning(f"Unknown category filter: {cat}")
                else:
                    category_filter.append(cat)
        
        for rumor in self._rumor_cache.values():
            # Apply filters
            if min_truth > 0 and rumor.truth_value < min_truth:
                continue
            
            if min_severity and not self._severity_is_at_least(rumor.severity, min_severity):
                continue
            
            if category_filter and not any(cat in rumor.categories for cat in category_filter):
                continue
            
            if entity_knows and not rumor.entity_knows_rumor(entity_knows):
                continue
            
            # Get content for search (use original content for search)
            search_content = rumor.original_content
            if search_text and search_text.lower() not in search_content.lower():
                continue
            
            # Build result
            result = {
                "rumor_id": rumor.id,
                "original_content": rumor.original_content,
                "categories": [cat.value for cat in rumor.categories],
                "severity": rumor.severity.value,
                "truth_value": rumor.truth_value,
                "created_at": rumor.created_at.isoformat(),
                "originator_id": rumor.originator_id,
                "variant_count": len(rumor.variants),
                "spread_count": len(rumor.spread)
            }
            
            # Add entity-specific information if requested
            if entity_knows:
                believability = rumor.get_believability_for_entity(entity_knows)
                variant_id = rumor.get_latest_variant_id_for_entity(entity_knows)
                variant = rumor.get_variant_by_id(variant_id) if variant_id else None
                
                result.update({
                    "entity_believability": believability,
                    "entity_variant_id": variant_id,
                    "entity_content": variant.content if variant else rumor.original_content
                })
            
            results.append(result)
        
        # Sort by creation date (newest first) and limit
        results.sort(key=lambda x: x["created_at"], reverse=True)
        return results[:limit]

    def _severity_is_at_least(self, severity: RumorSeverity, min_severity: RumorSeverity) -> bool:
        """
        Check if a severity level meets the minimum threshold.
        """
        severity_order = [
            RumorSeverity.TRIVIAL,
            RumorSeverity.MINOR,
            RumorSeverity.MODERATE,
            RumorSeverity.MAJOR,
            RumorSeverity.CRITICAL
        ]
        
        try:
            return severity_order.index(severity) >= severity_order.index(min_severity)
        except ValueError:
            return False

    async def decay_rumors(self, decay_rate: Optional[float] = None) -> int:
        """
        Apply decay to all rumors based on time and other factors.
        
        Args:
            decay_rate: Custom decay rate (uses default if None)
            
        Returns:
            Number of rumors that were decayed
        """
        if decay_rate is None:
            decay_rate = self.default_decay_rate
        
        await self._preload_rumors()
        
        decayed_count = 0
        current_time = datetime.utcnow()
        
        for rumor in self._rumor_cache.values():
            rumor_decayed = False
            
            # Calculate time-based decay factor
            age_days = (current_time - rumor.created_at).days
            time_factor = 1.0 + (age_days * 0.1)  # Older rumors decay faster
            
            # Apply severity-based decay modifiers
            severity_modifiers = {
                RumorSeverity.TRIVIAL: 1.5,    # Decay faster
                RumorSeverity.MINOR: 1.2,
                RumorSeverity.MODERATE: 1.0,
                RumorSeverity.MAJOR: 0.8,
                RumorSeverity.CRITICAL: 0.6    # Decay slower
            }
            
            severity_factor = severity_modifiers.get(rumor.severity, 1.0)
            final_decay_rate = decay_rate * time_factor * severity_factor
            
            # Apply decay to all spread records
            for spread in rumor.spread:
                old_believability = spread.believability
                spread.believability = max(0.0, spread.believability - final_decay_rate)
                
                if spread.believability != old_believability:
                    rumor_decayed = True
            
            if rumor_decayed:
                # Update storage
                await self.repository.save_rumor(rumor)
                decayed_count += 1
        
        logger.info(f"Applied decay to {decayed_count} rumors")
        return decayed_count

    async def get_rumor_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the rumor system.
        
        Returns:
            Dictionary with various statistics
        """
        await self._preload_rumors()
        
        total_rumors = len(self._rumor_cache)
        total_variants = sum(len(rumor.variants) for rumor in self._rumor_cache.values())
        total_spreads = sum(len(rumor.spread) for rumor in self._rumor_cache.values())
        
        # Category distribution
        category_counts = {}
        for rumor in self._rumor_cache.values():
            for category in rumor.categories:
                category_counts[category.value] = category_counts.get(category.value, 0) + 1
        
        # Severity distribution
        severity_counts = {}
        for rumor in self._rumor_cache.values():
            severity = rumor.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Average metrics
        avg_truth_value = sum(rumor.truth_value for rumor in self._rumor_cache.values()) / max(1, total_rumors)
        avg_variants_per_rumor = total_variants / max(1, total_rumors)
        avg_spreads_per_rumor = total_spreads / max(1, total_rumors)
        
        return {
            "total_rumors": total_rumors,
            "total_variants": total_variants,
            "total_spreads": total_spreads,
            "category_distribution": category_counts,
            "severity_distribution": severity_counts,
            "average_truth_value": round(avg_truth_value, 3),
            "average_variants_per_rumor": round(avg_variants_per_rumor, 2),
            "average_spreads_per_rumor": round(avg_spreads_per_rumor, 2),
            "cache_size": len(self._rumor_cache)
        }


# Factory function for dependency injection
def create_rumor_system(
    repository: Optional[RumorRepository] = None,
    event_dispatcher: Optional[EventDispatcher] = None,
    default_decay_rate: float = 0.05,
    gpt_mutation_handler: Optional[Callable] = None
) -> RumorSystem:
    """Create a rumor system instance with dependency injection."""
    return RumorSystem(repository, event_dispatcher, default_decay_rate, gpt_mutation_handler) 