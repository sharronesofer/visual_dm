"""
Service layer for the rumor system handling business logic and operations.
"""
from typing import List, Optional, Dict, Any, Union, Callable
import logging
import random
import asyncio # For singleton lock
from datetime import datetime

from backend.systems.rumor.models.rumor import (
    Rumor, RumorVariant, RumorSpread, RumorCategory, RumorSeverity, RumorEvent,
    JsonRumorRepository # Import the renamed class
)
from backend.systems.events.models.event_dispatcher import EventDispatcher
# Assuming a RumorRepository interface/class exists and is importable
# from backend.systems.rumor.repositories.rumor_repository import RumorRepository # Example path

# Placeholder for RumorRepository if not defined elsewhere
class MockRumorRepository: # This can be removed if JsonRumorRepository is always used.
    async def save_rumor(self, rumor: Rumor):
        logging.info(f"[MockRumorRepo] SAVE: Rumor ID {rumor.id}")
    async def get_rumor(self, rumor_id: str) -> Optional[Rumor]:
        logging.info(f"[MockRumorRepo] GET: Rumor ID {rumor_id}")
        # Return a mock rumor or None for testing purposes
        # For robust default, this mock should try to return a valid Rumor object if one is expected
        return Rumor(id=rumor_id, originator_id="mock_user", original_content="Mock rumor content") 

logger = logging.getLogger(__name__)

class RumorService:
    """
    Service for managing rumors in the game world.
    This service handles the business logic for creating, spreading, and managing rumors.
    Implements a singleton pattern.
    """
    _instance = None
    _lock = asyncio.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        # No change needed in __new__ for this step, singleton logic is in get_instance*
        return super(RumorService, cls).__new__(cls)

    def __init__(self,
                rumor_repository: JsonRumorRepository,
                event_dispatcher: Optional[EventDispatcher] = None,
                default_decay_rate: float = 0.05,
                gpt_mutation_handler = None):
        # Check moved to classmethod constructors to avoid re-init issues with singleton
        # if RumorService._initialized:
        # return

        self.repository = rumor_repository
        self.event_dispatcher = event_dispatcher or EventDispatcher.get_instance()
        self.default_decay_rate = default_decay_rate
        self.gpt_mutation_handler = gpt_mutation_handler
        
        # Mark as initialized if this specific instance's __init__ is completed.
        # The class-level _initialized guards against re-running __init__ on the SAME instance.
        # However, the primary guard against multiple instances is in get_instance* methods.
        # RumorService._initialized = True # This should be set after successful init of the instance
        logger.info("RumorService instance configured.")

    @classmethod
    async def get_instance_async(cls, 
                                 rumor_repository: Optional[JsonRumorRepository] = None, 
                                 event_dispatcher: Optional[EventDispatcher] = None,
                                 gpt_mutation_handler: Optional[Callable] = None) -> 'RumorService':
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    final_repo = rumor_repository
                    if final_repo is None:
                        # Pass the gpt_mutation_handler to the default repository
                        final_repo = JsonRumorRepository(gpt_mutation_handler=gpt_mutation_handler)
                        logger.info("RumorService created default JsonRumorRepository for async instance, passing gpt_mutation_handler.")
                    
                    # Create the new instance, potentially re-calling __init__ if not careful
                    # cls._instance = super(RumorService, cls).__new__(cls) # Create instance
                    # cls._instance.__init__(final_repo, event_dispatcher, gpt_mutation_handler=gpt_mutation_handler) # Explicitly call init once
                    
                    # More Pythonic singleton init:
                    # Create the instance and let its __init__ run once.
                    # The _initialized flag on the *instance* (if we add one) or careful __init__ would prevent re-init.
                    # For now, direct instantiation with all params:
                    cls._instance = cls(
                        rumor_repository=final_repo, 
                        event_dispatcher=event_dispatcher, 
                        gpt_mutation_handler=gpt_mutation_handler
                    )
                    cls._initialized = True # Mark class as having its singleton initialized
                    logger.info("RumorService async singleton instance created.")
        return cls._instance

    @classmethod
    def get_instance(cls, 
                     rumor_repository: Optional[JsonRumorRepository] = None, 
                     event_dispatcher: Optional[EventDispatcher] = None,
                     gpt_mutation_handler: Optional[Callable] = None) -> 'RumorService':
        # This is a simplified synchronous singleton acquisition.
        # For multi-threaded apps, a threading.Lock would be appropriate here.
        # Using the same async lock for simplicity in this context, though not ideal for pure sync.
        if cls._instance is None: # First check (no lock)
            # Assuming this lock is an asyncio.Lock, this sync method can't use it directly.
            # For true thread-safety in a sync context, import threading.Lock.
            # For this exercise, we'll assume single-threaded or careful usage for this sync getter.
            # with cls._lock: # This would block if it's an asyncio.Lock and no event loop
            if cls._instance is None: # Double-check idiom
                final_repo = rumor_repository
                if final_repo is None:
                    final_repo = JsonRumorRepository(gpt_mutation_handler=gpt_mutation_handler)
                    logger.info("RumorService created default JsonRumorRepository for sync instance, passing gpt_mutation_handler.")

                # cls._instance = super(RumorService, cls).__new__(cls)
                # cls._instance.__init__(final_repo, event_dispatcher, gpt_mutation_handler=gpt_mutation_handler)
                cls._instance = cls(
                    rumor_repository=final_repo, 
                    event_dispatcher=event_dispatcher, 
                    gpt_mutation_handler=gpt_mutation_handler
                )
                cls._initialized = True # Mark class as having its singleton initialized
                logger.info("RumorService sync singleton instance created.")
        return cls._instance
    
    async def create_rumor(self, 
                         originator_id: str,
                         content: str,
                         categories: List[Union[RumorCategory, str]] = [RumorCategory.OTHER],
                         severity: Union[RumorSeverity, str] = RumorSeverity.MINOR,
                         truth_value: float = 0.5) -> str:
        """
        Create a new rumor and store it.
        """
        # Normalize categories to enum instances
        normalized_categories = []
        for category in categories:
            if isinstance(category, str):
                try:
                    category = RumorCategory[category.upper()] # Assuming enum keys are upper
                except KeyError:
                    logger.warning(f"Invalid rumor category string: {category}. Defaulting to OTHER.")
                    category = RumorCategory.OTHER
            elif not isinstance(category, RumorCategory):
                 logger.warning(f"Invalid rumor category type: {type(category)}. Defaulting to OTHER.")
                 category = RumorCategory.OTHER
            normalized_categories.append(category)
        
        # Normalize severity
        if isinstance(severity, str):
            try:
                severity = RumorSeverity[severity.upper()] # Assuming enum keys are upper
            except KeyError:
                logger.warning(f"Invalid rumor severity string: {severity}. Defaulting to MINOR.")
                severity = RumorSeverity.MINOR
        elif not isinstance(severity, RumorSeverity):
            logger.warning(f"Invalid rumor severity type: {type(severity)}. Defaulting to MINOR.")
            severity = RumorSeverity.MINOR
        
        rumor = Rumor(
            originator_id=originator_id,
            original_content=content,
            categories=normalized_categories,
            severity=severity,
            truth_value=truth_value
        )
        
        initial_variant = RumorVariant(
            content=content,
            entity_id=originator_id # The originator is the first one to "know" this variant
        )
        rumor.variants.append(initial_variant)
        
        spread_record = RumorSpread(
            entity_id=originator_id,
            variant_id=initial_variant.id,
            believability=1.0
        )
        rumor.spread.append(spread_record)
        
        await self.repository.save_rumor(rumor)
        
        if self.event_dispatcher:
            event = RumorEvent(
                event_type="rumor.created", # Ensure event_type is set for EventBase
                rumor_id=rumor.id,
                operation="created",
                entity_id=originator_id,
                additional_data={ "content": content[:50] }
            )
            # Use publish for async, publish_sync for sync contexts
            await self.event_dispatcher.publish(event) 
        
        logger.info(f"Created rumor {rumor.id} from {originator_id}: {content[:50]}...")
        return rumor.id
    
    async def spread_rumor(self,
                        rumor_id: str,
                        from_entity_id: str,
                        to_entity_id: str,
                        variant_id: Optional[str] = None,
                        mutate: bool = False,
                        mutation_probability: float = 0.2,
                        relationship_factor: Optional[float] = None,
                        receiver_bias_factor: Optional[float] = None
                        ) -> bool:
        """
        Spread a rumor from one entity to another, potentially with mutation.
        Believability is influenced by rumor's truth, relationships, and receiver's bias.
        """
        rumor = await self.repository.get_rumor(rumor_id)
        if not rumor:
            logger.warning(f"Failed to spread rumor {rumor_id}: rumor not found")
            return False
        
        source_knows = any(s.entity_id == from_entity_id for s in rumor.spread)
        if not source_knows:
            logger.warning(f"Failed to spread rumor {rumor_id}: source entity {from_entity_id} doesn't know it")
            return False
        
        # Determine relationship_factor and receiver_bias_factor
        final_relationship_factor = 0.0
        if relationship_factor is not None:
            final_relationship_factor = relationship_factor
        else:
            # Placeholder: In a full integration, query a CharacterRelationshipService here
            # Example: final_relationship_factor = await CharacterRelationshipService.get_influence(from_entity_id, to_entity_id)
            logger.debug(f"spread_rumor: relationship_factor not provided for {from_entity_id} -> {to_entity_id}. Using default 0.0. Placeholder for CharacterRelationshipService call.")
            pass # Defaults to 0.0

        final_receiver_bias_factor = 0.0
        if receiver_bias_factor is not None:
            final_receiver_bias_factor = receiver_bias_factor
        else:
            # Placeholder: In a full integration, query an EntityPropertiesService or similar for receiver's bias
            # Example: final_receiver_bias_factor = await EntityPropertiesService.get_bias(to_entity_id, bias_type='gullibility')
            logger.debug(f"spread_rumor: receiver_bias_factor not provided for {to_entity_id}. Using default 0.0. Placeholder for EntityPropertiesService call.")
            pass # Defaults to 0.0

        if variant_id is None:
            # Find the latest variant known to the source entity
            source_spread_records = [s for s in rumor.spread if s.entity_id == from_entity_id]
            if not source_spread_records:
                 logger.warning(f"Failed to spread rumor {rumor_id}: source entity {from_entity_id} has no spread record.")
                 return False
            # Assuming spread records are ordered by time or we take the one with highest believability / latest timestamp
            # For simplicity, let's find the variant from the first spread record found for the source
            # A more robust system would track timestamp of hearing.
            variant_id = source_spread_records[0].variant_id 
            # To be more precise, one might need to sort spread records by timestamp if they exist.

        variant_to_spread = rumor.get_variant_by_id(variant_id)
        if not variant_to_spread:
            logger.warning(f"Failed to spread rumor {rumor_id}: variant {variant_id} not found")
            return False
        
        current_content_to_spread = variant_to_spread.content
        final_variant_id_for_receiver = variant_id
        mutated_this_spread = False

        if mutate and (mutation_probability >= 1.0 or random.random() < mutation_probability):
            # Delegate mutation to the repository, which uses its configured handler
            # The repository.mutate_rumor method will handle None new_content by using its gpt_handler or basic mutation
            new_mutated_variant_obj = await self.repository.mutate_rumor(
                rumor_id=rumor.id, 
                entity_id=to_entity_id, # The receiver is the one "perceiving" or creating the mutation
                parent_variant_id=variant_id,
                # new_content=None, # Let repository handle generation
                # mutation_metadata= {} # Let repository handle default
            )
            
            if new_mutated_variant_obj:
                # No need to append to rumor.variants here, repository.mutate_rumor should do that
                # and save the rumor.
                final_variant_id_for_receiver = new_mutated_variant_obj.id
                mutated_this_spread = True
                logger.debug(f"Rumor {rumor.id} mutated via repository during spread to {to_entity_id}. New variant: {new_mutated_variant_obj.id}")
        
        # Enhanced Believability Calculation for a new spread or base for reinforcement:
        base_believability_for_new_spread = 0.3 + (rumor.truth_value * 0.4) 
        believability_from_source = base_believability_for_new_spread + final_relationship_factor + final_receiver_bias_factor
        believability_from_source = max(0.0, min(1.0, believability_from_source))

        # Check if the receiver already knows this rumor
        existing_spread_record: Optional[RumorSpread] = None
        for i, s_record in enumerate(rumor.spread):
            if s_record.entity_id == to_entity_id:
                existing_spread_record = rumor.spread.pop(i) # Remove to replace/update
                break
        
        current_time = datetime.utcnow()
        reinforcement_amount = 0.2 # Example fixed reinforcement amount

        if existing_spread_record:
            # Entity already knows the rumor - reinforce it
            existing_spread_record.believability = min(1.0, existing_spread_record.believability + reinforcement_amount + (believability_from_source * 0.1)) # Add a fraction of new source's strength
            existing_spread_record.variant_id = final_variant_id_for_receiver # Update to the (potentially new) variant
            existing_spread_record.heard_from_entity_id = from_entity_id # Update who they last heard it from
            existing_spread_record.heard_at = current_time # Update when they last heard it
            existing_spread_record.last_reinforced_at = current_time
            rumor.spread.append(existing_spread_record)
            final_believability = existing_spread_record.believability
            logger.info(f"Rumor {rumor.id} reinforced for entity {to_entity_id}.")
        else:
            # Entity is hearing this rumor for the first time from this source
            new_spread_record = RumorSpread(
                entity_id=to_entity_id,
                variant_id=final_variant_id_for_receiver,
                heard_from_entity_id=from_entity_id,
                believability=believability_from_source,
                heard_at=current_time,
                last_reinforced_at=current_time 
            )
            rumor.spread.append(new_spread_record)
            final_believability = new_spread_record.believability
        
        await self.repository.save_rumor(rumor)
        
        if self.event_dispatcher:
            event = RumorEvent(
                event_type="rumor.spread", # Ensure event_type is set
                rumor_id=rumor.id,
                operation="spread" if not existing_spread_record else "reinforced", # operation type
                entity_id=to_entity_id,
                additional_data={
                    "from_entity_id": from_entity_id,
                    "variant_id": final_variant_id_for_receiver,
                    "believability": final_believability,
                    "mutated": mutated_this_spread
                }
            )
            await self.event_dispatcher.publish(event)
        
        logger.info(f"Rumor {rumor.id} (variant {final_variant_id_for_receiver}) spread from {from_entity_id} to {to_entity_id} with final believability {final_believability:.2f}")
        return True

    async def mutate_rumor(self, 
                           rumor_id: str, 
                           entity_id: str, 
                           parent_variant_id: str,
                           mutation_context: Optional[Dict[str, Any]] = None
                           ) -> Optional[RumorVariant]:
        """
        Mutate a rumor variant, creating a new variant by delegating to the repository.
        The repository will use its configured gpt_mutation_handler or a basic fallback.

        Args:
            rumor_id: The ID of the rumor.
            entity_id: The entity for whom this mutation is occurring (influences context).
            parent_variant_id: The ID of the variant this mutation is based on.
            mutation_context: Additional context for mutation (e.g., entity traits for GPT handler).

        Returns:
            The new RumorVariant if mutation occurred, else None.
        """
        # Directly call the repository's mutate_rumor method.
        # It will handle fetching the rumor, the parent variant, generating content,
        # creating the new variant, adding it to the rumor, saving, and emitting events.
        new_variant = await self.repository.mutate_rumor(
            rumor_id=rumor_id,
            entity_id=entity_id,
            parent_variant_id=parent_variant_id,
            # new_content is None, so repository will use its internal logic (GPT or basic)
            mutation_metadata=mutation_context or {} # Pass context as metadata
        )

        if new_variant:
            logger.info(f"RumorService successfully requested mutation for rumor {rumor_id} by {entity_id}. New variant {new_variant.id}")
        else:
            logger.warning(f"RumorService: Mutation failed or did not result in a new variant for rumor {rumor_id} by {entity_id}.")
            
        return new_variant

    async def decay_all_rumors(self):
        """
        Apply decay to all rumors based on their individual or the default decay_rate.
        This would typically be called periodically (e.g., daily game tick).
        Note: Actual removal of very old/irrelevant rumors might be a separate process.
        """
        # This requires fetching all rumors or iterating through them if the repository supports it.
        # For simplicity, this is a conceptual placeholder. A real implementation needs
        # to consider performance with many rumors.
        # all_rumors = await self.repository.get_all_rumors() # Hypothetical method
        # for rumor in all_rumors:
        #     for spread_info in rumor.spread:
        #         spread_info.believability = max(0, spread_info.believability - (rumor.decay_rate or self.default_decay_rate))
        #     await self.repository.save_rumor(rumor)
        logger.info("Conceptual: decay_all_rumors called. Implementation depends on repository capabilities.")
        pass # Placeholder

    async def get_rumor_context(self,
                                entity_id: Optional[str] = None,
                                location_id: Optional[str] = None, # Placeholder for future use
                                num_rumors: int = 5,
                                min_believability: float = 0.5,
                                min_severity: Optional[RumorSeverity] = RumorSeverity.MODERATE,
                                categories: Optional[List[RumorCategory]] = None
                                ) -> List[Dict[str, Any]]:
        """
        Retrieves a list of active/relevant rumors for a given context.
        This is intended to provide narrative context for GPT or event generation.
        Args:
            entity_id: Optional ID of the entity to get rumor context for.
            location_id: Optional ID of the location to get rumors about.
            num_rumors: Maximum number of rumors to return.
            min_believability: Minimum believability for an entity-specific rumor.
            min_severity: Minimum severity for a rumor.
            categories: Optional list of categories to filter by.
        Returns:
            A list of dictionaries, each representing a rumor.
        """
        logger.debug(
            f"Fetching rumor context: entity_id={entity_id}, location_id={location_id}, "
            f"num_rumors={num_rumors}, min_believability={min_believability}, "
            f"min_severity={min_severity}, categories={categories}"
        )

        query_args: Dict[str, Any] = {
            "limit": num_rumors * 2 # Fetch more to filter later if entity_id is present
        }
        if categories:
            query_args["categories"] = categories
        if min_severity:
            # The repository.query_rumors expects 'severity' to be the minimum.
            query_args["severity"] = min_severity
        if entity_id:
            # If entity_id is provided, the repository can filter for rumors known by this entity.
            query_args["entity_knows"] = entity_id
        
        # If not filtering by entity_id, we might want to apply a general truth filter.
        # The Development Bible doesn't specify this explicitly for GetRumorContext,
        # but the repository query supports min_truth. For now, let's not add it
        # unless entity_id is None, to keep it simple.
        # if not entity_id:
        #     query_args["min_truth"] = 0.3 # Example general truth threshold

        potential_rumors_data: List[Dict[str, Any]] = []
        try:
            # repository.query_rumors is defined in JsonRumorRepository (models/rumor.py)
            potential_rumors_data = await self.repository.query_rumors(**query_args)
            logger.debug(f"Repository query returned {len(potential_rumors_data)} potential rumors.")
        except Exception as e:
            logger.error(f"Error querying rumors from repository: {e}", exc_info=True)
            return [] # Return empty list on error

        contextual_rumors: List[Dict[str, Any]] = []

        for rumor_summary_data in potential_rumors_data:
            if len(contextual_rumors) >= num_rumors:
                logger.debug(f"Reached num_rumors limit ({num_rumors}). Stopping further processing.")
                break # Stop if we have collected enough rumors

            rumor_id = rumor_summary_data.get("id")
            if not rumor_id:
                logger.warning("Rumor data from query missing ID. Skipping.")
                continue

            try:
                rumor_obj = await self.repository.get_rumor(rumor_id)
                if not rumor_obj:
                    logger.warning(f"Could not retrieve full rumor object for ID: {rumor_id}. Skipping.")
                    continue

                if entity_id:
                    # For entity-specific context, check their believability
                    believability = rumor_obj.get_believability_for_entity(entity_id)
                    if believability is not None and believability >= min_believability:
                        content = rumor_obj.get_current_content_for_entity(entity_id) or rumor_obj.original_content
                        contextual_rumors.append({
                            "id": rumor_obj.id,
                            "content": content,
                            "believability": believability,
                            "severity": rumor_obj.severity.value,
                            "categories": [cat.value for cat in rumor_obj.categories]
                        })
                        logger.debug(f"Added rumor {rumor_obj.id} for entity {entity_id} context. Believability: {believability:.2f}")
                    else:
                        logger.debug(f"Skipping rumor {rumor_obj.id} for entity {entity_id}: believability ({believability}) < min_believability ({min_believability})")
                else:
                    # For general context, use the original/primary content
                    # Ensure there is at least one variant to get content from
                    main_variant_content = rumor_obj.variants[0].content if rumor_obj.variants else rumor_obj.original_content
                    contextual_rumors.append({
                        "id": rumor_obj.id,
                        "content": main_variant_content,
                        "severity": rumor_obj.severity.value,
                        "truth_value": rumor_obj.truth_value, # General context might include truth value
                        "categories": [cat.value for cat in rumor_obj.categories]
                    })
                    logger.debug(f"Added rumor {rumor_obj.id} for general context.")
            except Exception as e:
                logger.error(f"Error processing rumor {rumor_id} for context: {e}", exc_info=True)
                continue # Skip this rumor on error and proceed with others
        
        logger.info(f"Returning {len(contextual_rumors)} rumors for context.")
        # Placeholder for further processing:
        processed_rumors: List[Dict[str, Any]] = []

        # This is where the logic to iterate potential_rumors_data,
        # fetch full rumor objects if needed (especially for entity_id specific context),
        # apply min_believability, and format the output will go.

        # As a first step, let's just return what the repository gave,
        # limited by num_rumors, to ensure the call works.
        # This is NOT the final logic.
        if potential_rumors_data:
            logger.info(f"Returning up to {num_rumors} of {len(potential_rumors_data)} raw results from repo query for now.")
            return potential_rumors_data[:num_rumors] 
        
        return processed_rumors

    # Other methods like get_rumor_details, get_rumors_known_by_entity, etc.
    async def get_rumor_details(self, rumor_id: str) -> Optional[Rumor]:
        return await self.repository.get_rumor(rumor_id) 