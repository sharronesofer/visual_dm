from typing import Dict, List, Optional, Tuple
import math
from datetime import datetime

from backend.systems.population.models import (
    POIPopulation, 
    POIType, 
    POIState, 
    PopulationConfig,
    PopulationChangedEvent as ModelPopulationChangedEvent
)
from backend.core.logging import logger
from backend.systems.population.utils import (
    calculate_growth_rate,
    calculate_next_state
)
from backend.systems.population.events import (
    PopulationChangedEventData,
    PopulationStateChangedEventData
)
from backend.core.events.event_dispatcher import EventDispatcher

class PopulationService:
    """Service for handling population control system logic"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PopulationService, cls).__new__(cls)
            cls._instance.populations = {}
            cls._instance.config = PopulationConfig()
            cls._instance.events = []  # Only stores model events for API compatibility
            cls._instance.initialized = False
            cls._instance.event_dispatcher = EventDispatcher.get_instance()
        return cls._instance
    
    async def initialize(self):
        """Initialize the population service with configuration"""
        if self.initialized:
            return
            
        # In a real implementation, load from database
        logger.info("Initializing population service")
        self.initialized = True
    
    async def get_all_populations(self) -> List[POIPopulation]:
        """Get all POI populations"""
        return list(self.populations.values())
    
    async def get_population(self, poi_id: str) -> Optional[POIPopulation]:
        """Get population data for a specific POI"""
        return self.populations.get(poi_id)
    
    async def create_population(self, population: POIPopulation) -> POIPopulation:
        """Create population data for a POI"""
        # Set base rate based on POI type if not specified
        if population.base_rate == 1.0:  # Default value
            population.base_rate = self.config.base_rates.get(population.poi_type, 1.0)
        
        # Store the population data
        self.populations[population.poi_id] = population
        logger.info(f"Created population data for POI {population.poi_id}")
        return population
    
    async def update_population(self, poi_id: str, population: POIPopulation) -> Optional[POIPopulation]:
        """Update population data for a POI"""
        if poi_id in self.populations:
            old_population = self.populations[poi_id]
            old_state = old_population.state
            self.populations[poi_id] = population
            
            # Record population change event if population changed
            if old_population.current_population != population.current_population:
                # Create model event for API compatibility
                model_event = ModelPopulationChangedEvent(
                    poi_id=poi_id,
                    old_population=old_population.current_population,
                    new_population=population.current_population,
                    old_state=old_state,
                    new_state=population.state,
                    change_type="manual",
                    timestamp=datetime.utcnow()
                )
                self.events.append(model_event)
                
                # Create and publish event to event dispatcher
                event = PopulationChangedEventData(
                    poi_id=poi_id,
                    poi_name=population.name,
                    poi_type=population.poi_type,
                    old_population=old_population.current_population,
                    new_population=population.current_population,
                    old_state=old_state,
                    new_state=population.state,
                    change_type="manual"
                )
                self.event_dispatcher.publish_sync(event)
                
                # If state also changed, publish state change event
                if old_state != population.state:
                    state_event = PopulationStateChangedEventData(
                        poi_id=poi_id,
                        poi_name=population.name,
                        poi_type=population.poi_type,
                        old_state=old_state,
                        new_state=population.state,
                        population=population.current_population,
                        reason="manual_update"
                    )
                    self.event_dispatcher.publish_sync(state_event)
            
            logger.info(f"Updated population data for POI {poi_id}")
            return population
        return None
    
    async def delete_population(self, poi_id: str) -> bool:
        """Delete population data for a POI"""
        if poi_id in self.populations:
            del self.populations[poi_id]
            logger.info(f"Deleted population data for POI {poi_id}")
            return True
        return False
    
    async def set_global_multiplier(self, value: float) -> float:
        """Set the global population multiplier"""
        # Ensure the multiplier is a non-negative value
        self.config.global_multiplier = max(0.0, value)
        logger.info(f"Set global population multiplier to {self.config.global_multiplier}")
        return self.config.global_multiplier
    
    async def set_base_rate(self, poi_type: POIType, value: float) -> Dict[POIType, float]:
        """Set the base rate for a POI type"""
        # Ensure the base rate is a non-negative value
        self.config.base_rates[poi_type] = max(0.0, value)
        logger.info(f"Set base rate for {poi_type} to {self.config.base_rates[poi_type]}")
        return self.config.base_rates
    
    async def monthly_update(self) -> List[ModelPopulationChangedEvent]:
        """Process monthly population updates for all POIs"""
        logger.info("Processing monthly population updates")
        model_events = []
        
        for poi_id, population in self.populations.items():
            old_population = population.current_population
            old_state = population.state
            
            # Skip POIs in non-growing states
            if population.state in [POIState.RUINS, POIState.DUNGEON, POIState.ABANDONED]:
                continue
                
            # Calculate population growth
            if population.current_population < population.target_population:
                # Calculate growth rate using utility function
                rate = calculate_growth_rate(
                    population, 
                    self.config.global_multiplier,
                    self.config.soft_cap_threshold, 
                    self.config.soft_cap_multiplier
                )
                
                # Add new population, rounded down
                population.current_population += math.floor(rate)
                
                # Apply hard cap
                if population.current_population > population.target_population:
                    population.current_population = population.target_population
            
            # Apply minimum population threshold
            if population.current_population < population.min_population:
                population.current_population = population.min_population
            
            # Update POI state based on population ratio using utility function
            new_state = calculate_next_state(population, self.config.state_transition_thresholds)
            if new_state != population.state:
                population.state = new_state
            
            # Record event if population changed
            if old_population != population.current_population or old_state != population.state:
                change_type = "growth" if population.current_population > old_population else "decline"
                
                # Create model event for API compatibility
                model_event = ModelPopulationChangedEvent(
                    poi_id=poi_id,
                    old_population=old_population,
                    new_population=population.current_population,
                    old_state=old_state,
                    new_state=population.state,
                    change_type=change_type,
                    timestamp=datetime.utcnow()
                )
                model_events.append(model_event)
                self.events.append(model_event)
                
                # Create and publish event to event dispatcher
                event = PopulationChangedEventData(
                    poi_id=poi_id,
                    poi_name=population.name,
                    poi_type=population.poi_type,
                    old_population=old_population,
                    new_population=population.current_population,
                    old_state=old_state,
                    new_state=population.state,
                    change_type=change_type
                )
                self.event_dispatcher.publish_sync(event)
                
                # If state also changed, publish state change event
                if old_state != population.state:
                    state_event = PopulationStateChangedEventData(
                        poi_id=poi_id,
                        poi_name=population.name,
                        poi_type=population.poi_type,
                        old_state=old_state,
                        new_state=population.state,
                        population=population.current_population,
                        reason="population_change"
                    )
                    self.event_dispatcher.publish_sync(state_event)
            
            # Update last updated timestamp
            population.last_updated = datetime.utcnow()
        
        logger.info(f"Monthly update complete, {len(model_events)} populations changed")
        return model_events

# Create a singleton instance
population_service = PopulationService() 