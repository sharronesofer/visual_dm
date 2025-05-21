"""
World State Event Handlers

This module contains handlers for world state events, allowing the system to react to 
changes in the world state and propagate them to other systems.
"""
import logging
from typing import Dict, Any, Optional, List

from backend.systems.events.models.event_dispatcher import EventHandler
from backend.systems.world_state.core.events import (
    WorldStateEvent, WorldStateCreatedEvent, WorldStateUpdatedEvent, 
    WorldStateDeletedEvent, WorldStateCalculatedEvent
)
from backend.systems.world_state.utils.world_event_utils import create_world_event
from backend.systems.world_state.core.types import StateCategory, WorldRegion

logger = logging.getLogger(__name__)

class WorldStateEventHandler(EventHandler):
    """Base handler for all world state events."""
    
    def __init__(self):
        super().__init__()
        self.handled_event_types = [
            WorldStateEvent,
            WorldStateCreatedEvent,
            WorldStateUpdatedEvent,
            WorldStateDeletedEvent,
            WorldStateCalculatedEvent
        ]
    
    async def handle_event(self, event: WorldStateEvent) -> None:
        """
        General handler for world state events.
        
        Args:
            event: The world state event to handle
        """
        logger.info(f"Handling world state event: {event.state_key} ({event.change_type.name})")
        
        # Log the event for analytics
        self._log_to_analytics(event)
        
        # Delegate to specific handlers based on event type
        if isinstance(event, WorldStateCreatedEvent):
            await self._handle_created_event(event)
        elif isinstance(event, WorldStateUpdatedEvent):
            await self._handle_updated_event(event)
        elif isinstance(event, WorldStateDeletedEvent):
            await self._handle_deleted_event(event)
        elif isinstance(event, WorldStateCalculatedEvent):
            await self._handle_calculated_event(event)
        
        # Additional handling based on state category
        await self._handle_category_specific(event)
    
    async def _handle_created_event(self, event: WorldStateCreatedEvent) -> None:
        """
        Handle state created events.
        
        Args:
            event: The created event to handle
        """
        logger.debug(f"State created: {event.state_key} = {event.new_value}")
        
        # Create a world event for significant state creations
        if self._is_significant_state(event.state_key, event.category):
            await self._create_world_event(
                event_type="state_created",
                description=f"New state created: {event.state_key}",
                category=event.category,
                region=event.region,
                entity_id=event.entity_id,
                metadata={
                    "value": event.new_value,
                    "state_key": event.state_key
                }
            )
    
    async def _handle_updated_event(self, event: WorldStateUpdatedEvent) -> None:
        """
        Handle state updated events.
        
        Args:
            event: The updated event to handle
        """
        logger.debug(f"State updated: {event.state_key} = {event.new_value} (was {event.old_value})")
        
        # Check for significant changes based on threshold or rules
        if await self._is_significant_change(event):
            await self._create_world_event(
                event_type="state_changed",
                description=f"State changed: {event.state_key}",
                category=event.category,
                region=event.region,
                entity_id=event.entity_id,
                metadata={
                    "old_value": event.old_value,
                    "new_value": event.new_value,
                    "state_key": event.state_key
                }
            )
    
    async def _handle_deleted_event(self, event: WorldStateDeletedEvent) -> None:
        """
        Handle state deleted events.
        
        Args:
            event: The deleted event to handle
        """
        logger.debug(f"State deleted: {event.state_key} (was {event.old_value})")
        
        # Only create events for significant state deletions
        if self._is_significant_state(event.state_key, event.category):
            await self._create_world_event(
                event_type="state_deleted",
                description=f"State removed: {event.state_key}",
                category=event.category,
                region=event.region,
                entity_id=event.entity_id,
                metadata={
                    "old_value": event.old_value,
                    "state_key": event.state_key
                }
            )
    
    async def _handle_calculated_event(self, event: WorldStateCalculatedEvent) -> None:
        """
        Handle state calculated events (derived values).
        
        Args:
            event: The calculated event to handle
        """
        logger.debug(f"State calculated: {event.state_key} = {event.new_value}")
        
        # Only create events for significant calculations
        threshold = self._get_significance_threshold(event.state_key, event.category)
        
        # For calculated values, we might be interested in the calculation method
        if hasattr(event, "calculation_method") and event.calculation_method:
            metadata = {
                "value": event.new_value,
                "state_key": event.state_key,
                "calculation_method": event.calculation_method
            }
        else:
            metadata = {
                "value": event.new_value,
                "state_key": event.state_key
            }
        
        await self._create_world_event(
            event_type="state_calculated",
            description=f"Calculated state: {event.state_key}",
            category=event.category,
            region=event.region,
            entity_id=event.entity_id,
            metadata=metadata
        )
    
    async def _handle_category_specific(self, event: WorldStateEvent) -> None:
        """
        Handle category-specific processing.
        
        Args:
            event: The event to handle based on category
        """
        if not event.category:
            return
            
        # Handle specific categories
        if event.category == StateCategory.FACTION:
            await self._handle_faction_event(event)
        elif event.category == StateCategory.POPULATION:
            await self._handle_population_event(event)
        elif event.category == StateCategory.DIPLOMACY:
            await self._handle_diplomacy_event(event)
        elif event.category == StateCategory.ECONOMY:
            await self._handle_economy_event(event)
        elif event.category == StateCategory.MILITARY:
            await self._handle_military_event(event)
        elif event.category == StateCategory.RELIGION:
            await self._handle_religion_event(event)
    
    async def _handle_faction_event(self, event: WorldStateEvent) -> None:
        """
        Handle faction-related state changes.
        
        Args:
            event: The faction event to handle
        """
        # Example: Track faction power changes
        if "power" in event.state_key:
            logger.info(f"Faction power change detected: {event.state_key}")
            
            # Additional faction-specific processing could go here
    
    async def _handle_population_event(self, event: WorldStateEvent) -> None:
        """
        Handle population-related state changes.
        
        Args:
            event: The population event to handle
        """
        # Example: Track significant population changes
        if "population" in event.state_key:
            logger.info(f"Population change detected: {event.state_key}")
            
            # Alert on significant population decreases
            if (isinstance(event, WorldStateUpdatedEvent) and 
                isinstance(event.old_value, (int, float)) and 
                isinstance(event.new_value, (int, float)) and
                event.new_value < event.old_value * 0.8):
                
                await self._create_world_event(
                    event_type="population_crisis",
                    description=f"Major population decrease in {event.state_key}",
                    category=event.category,
                    region=event.region,
                    entity_id=event.entity_id,
                    metadata={
                        "old_population": event.old_value,
                        "new_population": event.new_value,
                        "state_key": event.state_key
                    }
                )
    
    async def _handle_diplomacy_event(self, event: WorldStateEvent) -> None:
        """
        Handle diplomacy-related state changes.
        
        Args:
            event: The diplomacy event to handle
        """
        # Example: Track diplomatic relations
        if "relation" in event.state_key:
            logger.info(f"Diplomatic relation change detected: {event.state_key}")
            
            # Track faction relationships and alliance shifts
            if isinstance(event, WorldStateUpdatedEvent):
                # Check for alliance formations or breaks
                old_relation = event.old_value
                new_relation = event.new_value
                
                # Detect alliance formation
                if isinstance(old_relation, (int, float)) and isinstance(new_relation, (int, float)):
                    if old_relation < 75 and new_relation >= 75:
                        await self._create_world_event(
                            event_type="alliance_formed",
                            description=f"New alliance formed in {event.state_key}",
                            category=event.category,
                            region=event.region,
                            entity_id=event.entity_id,
                            metadata={
                                "old_relation": old_relation,
                                "new_relation": new_relation,
                                "state_key": event.state_key
                            }
                        )
                    # Detect alliance breaking
                    elif old_relation >= 75 and new_relation < 75:
                        await self._create_world_event(
                            event_type="alliance_broken",
                            description=f"Alliance broken in {event.state_key}",
                            category=event.category,
                            region=event.region,
                            entity_id=event.entity_id,
                            metadata={
                                "old_relation": old_relation,
                                "new_relation": new_relation,
                                "state_key": event.state_key
                            }
                        )
    
    async def _handle_economy_event(self, event: WorldStateEvent) -> None:
        """
        Handle economy-related state changes.
        
        Args:
            event: The economy event to handle
        """
        # Implementation for economy-specific handling
        pass
    
    async def _handle_military_event(self, event: WorldStateEvent) -> None:
        """
        Handle military-related state changes.
        
        Args:
            event: The military event to handle
        """
        # Implementation for military-specific handling
        pass
    
    async def _handle_religion_event(self, event: WorldStateEvent) -> None:
        """
        Handle religion-related state changes.
        
        Args:
            event: The religion event to handle
        """
        # Implementation for religion-specific handling
        pass
    
    def _log_to_analytics(self, event: WorldStateEvent) -> None:
        """
        Log event to analytics system.
        
        Args:
            event: The event to log
        """
        # Example analytics integration
        try:
            # Here would be code to send to an analytics system
            # For now, just log to the console
            logger.debug(f"Analytics: {event.state_key} ({event.change_type.name})")
        except Exception as e:
            logger.error(f"Failed to log to analytics: {str(e)}")
    
    def _is_significant_state(self, state_key: str, category: Optional[StateCategory]) -> bool:
        """
        Determine if a state is significant enough to create events for.
        
        Args:
            state_key: The state key to check
            category: The state category
            
        Returns:
            True if significant, False otherwise
        """
        # Check for general important state keys
        if any(key in state_key for key in [
            "war", "relation", "capital", "leader", "ruler", "population", 
            "rebellion", "crisis", "disaster", "plague"
        ]):
            return True
        
        # Check category-specific significance
        if category:
            if category == StateCategory.FACTION and any(key in state_key for key in [
                "power", "control", "influence"
            ]):
                return True
                
            if category == StateCategory.ECONOMY and any(key in state_key for key in [
                "gold", "wealth", "treasury", "trade", "resource"
            ]):
                return True
        
        # Default to not significant
        return False
    
    async def _is_significant_change(self, event: WorldStateUpdatedEvent) -> bool:
        """
        Determine if a state change is significant enough to create an event for.
        
        Args:
            event: The event to check
            
        Returns:
            True if significant, False otherwise
        """
        # First check if the state itself is significant
        if not self._is_significant_state(event.state_key, event.category):
            return False
        
        # For numeric values, check threshold
        if isinstance(event.old_value, (int, float)) and isinstance(event.new_value, (int, float)):
            threshold = self._get_significance_threshold(event.state_key, event.category)
            
            # Calculate change percentage
            if event.old_value == 0:
                # Can't divide by zero, but any change from zero is significant
                return True
                
            change_pct = abs((event.new_value - event.old_value) / event.old_value)
            return change_pct >= threshold
        
        # For status changes, always significant
        if "status" in event.state_key:
            return True
            
        # For boolean changes, always significant
        if isinstance(event.old_value, bool) and isinstance(event.new_value, bool) and event.old_value != event.new_value:
            return True
        
        # For other types, use default significance
        return True
    
    def _get_significance_threshold(self, state_key: str, category: Optional[StateCategory]) -> float:
        """
        Get the significance threshold for a state key and category.
        
        Args:
            state_key: The state key
            category: The state category
            
        Returns:
            The threshold value (0.0 to 1.0)
        """
        # Critical states have lower thresholds
        if any(key in state_key for key in ["war", "crisis", "rebellion"]):
            return 0.05  # 5% change is significant
        
        # Different thresholds by category
        if category:
            if category == StateCategory.POPULATION:
                return 0.1  # 10% change in population is significant
                
            if category == StateCategory.ECONOMY:
                return 0.2  # 20% change in economy is significant
                
            if category == StateCategory.MILITARY:
                return 0.15  # 15% change in military is significant
                
            if category == StateCategory.DIPLOMACY:
                return 0.25  # 25% change in diplomacy is significant
        
        # Default threshold
        return 0.3  # 30% change is significant by default
    
    async def _create_world_event(self, 
                                 event_type: str, 
                                 description: str, 
                                 category: Optional[StateCategory] = None,
                                 region: Optional[WorldRegion] = None,
                                 entity_id: Optional[str] = None,
                                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a world event.
        
        Args:
            event_type: Type of event
            description: Event description
            category: Optional state category
            region: Optional world region
            entity_id: Optional entity ID
            metadata: Optional metadata
            
        Returns:
            The created event
        """
        try:
            return create_world_event(
                event_type=event_type,
                description=description,
                category=category,
                region=region,
                entity_id=entity_id,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Failed to create world event: {str(e)}")
            return {} 