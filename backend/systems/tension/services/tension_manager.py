"""
Unified Tension Management System

Combines tension calculation, war triggers, and conflict resolution into a single
cohesive system with externalized configuration and proper event integration.

This is now a wrapper around the pure business logic service.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

from .tension_business_service import (
    TensionBusinessService,
    TensionModifier,
    TensionState,
    ConflictTrigger,
    TensionConfig,
    RevoltConfig,
    CalculationConstants,
    TensionConfigRepository,
    TensionRepository,
    FactionService,
    EventDispatcher
)
from ..models.tension_events import TensionEvent, TensionEventType


class UnifiedTensionManager:
    """
    Unified tension management system that handles:
    - Tension calculation and decay
    - War and conflict triggers
    - Event-driven tension updates
    - Cross-system integration
    
    This is now a wrapper around the pure business logic service.
    """
    
    def __init__(self, 
                 config_repository: Optional[TensionConfigRepository] = None,
                 tension_repository: Optional[TensionRepository] = None,
                 faction_service: Optional[FactionService] = None,
                 event_dispatcher: Optional[EventDispatcher] = None):
        """Initialize the unified tension manager with dependency injection."""
        
        # Use default implementations if not provided
        if config_repository is None:
            config_repository = self._create_default_config_repository()
        if tension_repository is None:
            tension_repository = self._create_default_tension_repository()
        
        # Initialize the business service
        self.business_service = TensionBusinessService(
            config_repository=config_repository,
            tension_repository=tension_repository,
            faction_service=faction_service,
            event_dispatcher=event_dispatcher
        )
        
        # Legacy compatibility - expose business service stats
        self.stats = self.business_service.stats
    
    def _create_default_config_repository(self) -> TensionConfigRepository:
        """Create a default config repository using the infrastructure adapter."""
        try:
            from backend.infrastructure.config_loaders.tension_config import TensionConfigManager
            config_manager = TensionConfigManager()
            
            # Create adapter that implements the protocol
            class ConfigRepositoryAdapter:
                def __init__(self, config_manager):
                    self.config_manager = config_manager
                
                def get_location_config(self, region_id: str, poi_id: str) -> TensionConfig:
                    config = self.config_manager.get_location_config(region_id, poi_id)
                    return TensionConfig(
                        base_tension=config.base_tension,
                        decay_rate=config.decay_rate,
                        max_tension=config.max_tension,
                        min_tension=config.min_tension,
                        player_impact=config.player_impact,
                        npc_impact=config.npc_impact,
                        environmental_impact=config.environmental_impact
                    )
                
                def get_event_impact_config(self, event_type: TensionEventType) -> Dict[str, float]:
                    return self.config_manager.get_event_impact_config(event_type)
                
                def get_revolt_config(self) -> RevoltConfig:
                    config = self.config_manager.get_revolt_config()
                    return RevoltConfig(
                        base_probability_threshold=config.base_probability_threshold,
                        faction_influence_modifier=config.faction_influence_modifier,
                        duration_range_hours=config.duration_range_hours,
                        casualty_multiplier=config.casualty_multiplier,
                        economic_impact_factor=config.economic_impact_factor
                    )
                
                def get_conflict_triggers(self) -> List[ConflictTrigger]:
                    triggers = self.config_manager.get_conflict_triggers()
                    return [
                        ConflictTrigger(
                            name=t.name,
                            tension_threshold=t.tension_threshold,
                            duration_hours=t.duration_hours,
                            faction_requirements=t.faction_requirements,
                            probability_modifier=t.probability_modifier
                        )
                        for t in triggers
                    ]
                
                def get_calculation_constants(self) -> CalculationConstants:
                    constants = self.config_manager.get_calculation_constants()
                    return CalculationConstants(
                        high_tension_threshold=constants.high_tension_threshold,
                        event_history_hours=constants.event_history_hours,
                        modifier_expiration_check_hours=constants.modifier_expiration_check_hours,
                        severity_thresholds=constants.severity_thresholds,
                        revolt_probability=constants.revolt_probability,
                        tension_limits=constants.tension_limits
                    )
            
            return ConfigRepositoryAdapter(config_manager)
        except ImportError:
            # Fallback to in-memory defaults if infrastructure not available
            return self._create_fallback_config_repository()
    
    def _create_default_tension_repository(self) -> TensionRepository:
        """Create a default in-memory tension repository."""
        class InMemoryTensionRepository:
            def __init__(self):
                self.tension_states: Dict[str, Dict[str, TensionState]] = {}
            
            def get_tension_state(self, region_id: str, poi_id: str) -> Optional[TensionState]:
                return self.tension_states.get(region_id, {}).get(poi_id)
            
            def save_tension_state(self, region_id: str, poi_id: str, state: TensionState) -> None:
                if region_id not in self.tension_states:
                    self.tension_states[region_id] = {}
                self.tension_states[region_id][poi_id] = state
            
            def get_all_tension_states(self) -> Dict[str, Dict[str, TensionState]]:
                return self.tension_states
        
        return InMemoryTensionRepository()
    
    def _create_fallback_config_repository(self) -> TensionConfigRepository:
        """Create a fallback config repository with hardcoded defaults."""
        class FallbackConfigRepository:
            def get_location_config(self, region_id: str, poi_id: str) -> TensionConfig:
                return TensionConfig(
                    base_tension=0.3,
                    decay_rate=0.04,
                    max_tension=1.0,
                    min_tension=0.1,
                    player_impact=1.0,
                    npc_impact=1.0,
                    environmental_impact=1.0
                )
            
            def get_event_impact_config(self, event_type: TensionEventType) -> Dict[str, float]:
                return {'base_impact': 0.1}
            
            def get_revolt_config(self) -> RevoltConfig:
                return RevoltConfig(
                    base_probability_threshold=0.8,
                    faction_influence_modifier=0.2,
                    duration_range_hours=(2, 12),
                    casualty_multiplier=0.1,
                    economic_impact_factor=0.3
                )
            
            def get_conflict_triggers(self) -> List[ConflictTrigger]:
                return [
                    ConflictTrigger(
                        name="high_tension",
                        tension_threshold=0.8,
                        duration_hours=24,
                        faction_requirements={},
                        probability_modifier=1.0
                    )
                ]
            
            def get_calculation_constants(self) -> CalculationConstants:
                return CalculationConstants(
                    high_tension_threshold=0.7,
                    event_history_hours=24,
                    modifier_expiration_check_hours=1,
                    severity_thresholds={"minor": 0.1, "moderate": 0.3, "major": 0.6, "extreme": 1.0},
                    revolt_probability={"low": 0.1, "medium": 0.3, "high": 0.7},
                    tension_limits={"min": 0.0, "max": 1.0}
                )
        
        return FallbackConfigRepository()
    
    # Delegate all methods to the business service
    def calculate_tension(
        self,
        region_id: str,
        poi_id: str,
        current_time: Optional[datetime] = None
    ) -> float:
        """Calculate current tension for a location with proper decay and modifiers."""
        return self.business_service.calculate_tension(region_id, poi_id, current_time)
    
    def update_tension_from_event(
        self,
        region_id: str,
        poi_id: str,
        event_type: Union[TensionEventType, str],
        event_data: Dict[str, Any],
        current_time: Optional[datetime] = None
    ) -> float:
        """
        Update tension based on a specific event.
        
        Args:
            event_type: Can be TensionEventType enum or string for external compatibility
        """
        return self.business_service.update_tension_from_event(
            region_id, poi_id, event_type, event_data, current_time
        )
    
    def check_conflict_triggers(
        self,
        region_id: str,
        current_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Check if any conflict triggers are activated for a region."""
        return self.business_service.check_conflict_triggers(region_id, current_time)
    
    def simulate_revolt(
        self,
        region_id: str,
        poi_id: str,
        factions_present: List[Dict],
        tension_level: float,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Simulate a potential revolt based on tension and faction dynamics."""
        return self.business_service.simulate_revolt(
            region_id, poi_id, factions_present, tension_level, current_time
        )
    
    def get_regions_by_tension(
        self,
        min_tension: float = 0.0,
        max_tension: float = 1.0,
        current_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get regions filtered by tension level range."""
        return self.business_service.get_regions_by_tension(min_tension, max_tension, current_time)
    
    def decay_all_tension(self, current_time: Optional[datetime] = None) -> Dict[str, int]:
        """Apply decay to all tension states globally."""
        return self.business_service.decay_all_tension(current_time)
    
    def add_tension_modifier(
        self, 
        region_id: str, 
        poi_id: str, 
        modifier_type: str, 
        value: float, 
        duration_hours: float,
        source: str = "unknown"
    ) -> None:
        """Add a temporary tension modifier."""
        self.business_service.add_tension_modifier(
            region_id, poi_id, modifier_type, value, duration_hours, source
        )
    
    # Legacy compatibility methods
    def get_factions_in_region(self, region_id: str) -> List[Dict]:
        """Get factions in a region (legacy compatibility)."""
        if self.business_service.faction_service:
            return self.business_service.faction_service.get_factions_in_region(region_id)
        return []


# Legacy compatibility - keep the old class names available
TensionManager = UnifiedTensionManager 