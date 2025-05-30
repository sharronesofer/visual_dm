"""
Service layer for the rumor system handling business logic and operations.
"""
from typing import List, Optional, Dict, Any, Union
import logging

from backend.systems.rumor.models.rumor import (
    Rumor, RumorVariant, RumorSpread, RumorCategory, RumorSeverity, RumorEvent
)
from backend.systems.events.services.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

class RumorService:
    """
    Service for managing rumors in the game world.
    This service handles the business logic for creating, spreading, and managing rumors.
    """
    
    def __init__(self, 
                rumor_repository,
                event_dispatcher: Optional[EventDispatcher] = None,
                default_decay_rate: float = 0.05,
                gpt_mutation_handler = None):
        """
        Initialize the rumor service.
        
        Args:
            rumor_repository: Repository for rumor storage and retrieval
            event_dispatcher: Event dispatcher instance for emitting events
            default_decay_rate: Default rate at which rumors decay (per update)
            gpt_mutation_handler: Optional function to handle GPT-based mutations
        """
        self.repository = rumor_repository
        self.event_dispatcher = event_dispatcher
        self.default_decay_rate = default_decay_rate
        self.gpt_mutation_handler = gpt_mutation_handler
        
        logger.info("RumorService initialized")
    
    async def create_rumor(self, 
                         originator_id: str,
                         content: str,
                         categories: List[Union[RumorCategory, str]] = [RumorCategory.OTHER],
                         severity: Union[RumorSeverity, str] = RumorSeverity.MINOR,
                         truth_value: float = 0.5) -> str:
        """
        Create a new rumor and store it.
        
        Args:
            originator_id: ID of the entity that originated the rumor
            content: The content of the rumor
            categories: Categories this rumor belongs to
            severity: How severe/important this rumor is
            truth_value: How true this rumor is (0.0 to 1.0)
            
        Returns:
            The ID of the created rumor
        """
        # Normalize categories to enum instances
        normalized_categories = []
        for category in categories:
            if isinstance(category, str):
                try:
                    category = RumorCategory(category)
                except ValueError:
                    category = RumorCategory.OTHER
            normalized_categories.append(category)
        
        # Normalize severity
        if isinstance(severity, str):
            try:
                severity = RumorSeverity(severity)
            except ValueError:
                severity = RumorSeverity.MINOR
        
        # Create new rumor
        rumor = Rumor(
            originator_id=originator_id,
            original_content=content,
            categories=normalized_categories,
            severity=severity,
            truth_value=truth_value
        )
        
        # Create initial variant
        initial_variant = RumorVariant(
            content=content,
            entity_id=originator_id
        )
        rumor.variants.append(initial_variant)
        
        # Record that the originator knows their own rumor
        spread_record = RumorSpread(
            entity_id=originator_id,
            variant_id=initial_variant.id,
            believability=1.0  # Originator fully believes their own rumor
        )
        rumor.spread.append(spread_record)
        
        # Save the rumor
        await self.repository.save_rumor(rumor)
        
        # Emit event
        if self.event_dispatcher:
            event = RumorEvent(
                rumor_id=rumor.id,
                operation="created",
                entity_id=originator_id
            )
            await self.event_dispatcher.dispatch_event(event)
        
        logger.info(f"Created rumor {rumor.id} from {originator_id}: {content[:50]}...")
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
            variant_id: Optional specific variant to spread (uses latest known to from_entity if None)
            believability_modifier: Adjustment to believability (-1.0 to 1.0)
            mutate: Whether to allow mutation during spread
            mutation_probability: Probability of mutation (0.0 to 1.0)
            
        Returns:
            True if spread successful, False otherwise
        """
        # Get the rumor
        rumor = await self.repository.get_rumor(rumor_id)
        if not rumor:
            logger.warning(f"Failed to spread rumor {rumor_id}: rumor not found")
            return False
        
        # Check if source entity knows the rumor
        if not rumor.entity_knows_rumor(from_entity_id):
            logger.warning(f"Failed to spread rumor {rumor_id}: source entity {from_entity_id} doesn't know it")
            return False
        
        # Determine which variant we're spreading
        if variant_id is None:
            variant_id = rumor.get_latest_variant_id_for_entity(from_entity_id)
            if not variant_id:
                logger.warning(f"Failed to spread rumor {rumor_id}: couldn't determine variant for source entity {from_entity_id}")
                return False
                
        variant = rumor.get_variant_by_id(variant_id)
        if not variant:
            logger.warning(f"Failed to spread rumor {rumor_id}: variant {variant_id} not found")
            return False
        
        # Determine if mutation occurs
        new_variant = None
        if mutate and (mutation_probability >= 1.0 or random.random() < mutation_probability):
            new_variant = await self.mutate_rumor(
                rumor_id=rumor_id,
                entity_id=to_entity_id,
                parent_variant_id=variant_id
            )
            if new_variant:
                variant_id = new_variant.id
        
        # Calculate believability
        # Base: Higher for true rumors, lower for false ones
        base_believability = 0.3 + (rumor.truth_value * 0.4)  
        # Modified by relationship between entities, etc.
        believability = max(0.0, min(1.0, base_believability + believability_modifier))
        
        # Create spread record
        spread_record = RumorSpread(
            entity_id=to_entity_id,
            variant_id=variant_id,
            heard_from_entity_id=from_entity_id,
            believability=believability
        )
        
        # If the entity already knows this rumor, consider it reinforcement
        # Remove old spread records for this entity
        rumor.spread = [s for s in rumor.spread if s.entity_id != to_entity_id]
        
        # Add the new spread record
        rumor.spread.append(spread_record)
        
        # Save the rumor
        await self.repository.save_rumor(rumor)
        
        # Emit event
        if self.event_dispatcher:
            event = RumorEvent(
                rumor_id=rumor.id,
                operation="spread",
                entity_id=to_entity_id,
                additional_data={
                    "from_entity_id": from_entity_id,
                    "variant_id": variant_id,
                    "mutated": new_variant is not None
                }
            )
            await self.event_dispatcher.dispatch_event(event)
        
        logger.info(f"Rumor {rumor_id} spread from {from_entity_id} to {to_entity_id}")
        return True 
