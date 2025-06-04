"""
Consolidated Rumor Service - Technical Infrastructure

This service combines the best aspects of both the event-driven rumor system
and the database-backed service patterns. It uses centralized configuration
from the rules system and provides a unified interface for rumor operations.

Moved from backend/systems/rumor/services/consolidated_rumor_service.py during refactoring.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Import centralized rules configuration
try:
    from backend.systems.rules.rules import (
        get_rumor_decay_rate,
        get_rumor_mutation_chance,
        get_rumor_spread_radius,
        get_rumor_believability_threshold,
        get_npc_rumor_behavior,
        get_rumor_config
    )
    _USE_CENTRALIZED_CONFIG = True
except ImportError:
    _USE_CENTRALIZED_CONFIG = False

# Import infrastructure components
try:
    from backend.infrastructure.systems.rumor.models.rumor import (
        Rumor, RumorCategory, RumorSeverity, RumorVariant, RumorSpread
    )
    from backend.infrastructure.systems.rumor.repositories.rumor_repository import RumorRepository
    from backend.infrastructure.events.core.event_base import EventBase
    from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
    _INFRASTRUCTURE_AVAILABLE = True
except ImportError:
    _INFRASTRUCTURE_AVAILABLE = False

logger = logging.getLogger(__name__)


class RumorEvent(EventBase):
    """Event emitted when rumor operations occur."""
    rumor_id: str
    operation: str  # "created", "spread", "mutated", etc.
    entity_id: Optional[str] = None
    additional_data: Dict[str, Any] = {}


class ConsolidatedRumorService:
    """
    Unified rumor service that provides both event-driven and database-backed functionality.
    Uses centralized configuration from the rules system.
    """
    
    def __init__(self, 
                 repository: Optional['RumorRepository'] = None,
                 event_dispatcher: Optional['EventDispatcher'] = None,
                 use_events: bool = True):
        """
        Initialize the consolidated rumor service.
        
        Args:
            repository: Repository for rumor persistence
            event_dispatcher: Event dispatcher for publishing events
            use_events: Whether to emit events for operations
        """
        self.repository = repository
        self.event_dispatcher = event_dispatcher
        self.use_events = use_events
        self._rumor_cache = {}
        
        # Initialize infrastructure if available
        if _INFRASTRUCTURE_AVAILABLE and not repository:
            self.repository = RumorRepository()
        
        if _INFRASTRUCTURE_AVAILABLE and not event_dispatcher and use_events:
            self.event_dispatcher = EventDispatcher.get_instance()
        
        logger.info(f"ConsolidatedRumorService initialized with events={use_events}")
    
    async def create_rumor(self,
                          originator_id: str,
                          content: str,
                          categories: List[Union[RumorCategory, str]] = None,
                          severity: Union[RumorSeverity, str] = None,
                          truth_value: float = 0.5) -> str:
        """
        Create a new rumor with centralized configuration defaults.
        
        Args:
            originator_id: ID of entity creating the rumor
            content: The content of the rumor
            categories: List of rumor categories (defaults to OTHER)
            severity: Severity level (defaults based on content or configuration)
            truth_value: How true the rumor is (0.0-1.0)
            
        Returns:
            ID of the created rumor
        """
        # Apply defaults from configuration
        if categories is None:
            categories = [RumorCategory.OTHER] if _INFRASTRUCTURE_AVAILABLE else ["other"]
        
        if severity is None:
            # Try to determine severity from content or use moderate default
            severity = RumorSeverity.MODERATE if _INFRASTRUCTURE_AVAILABLE else "moderate"
        
        # Normalize inputs using configuration
        normalized_categories = self._normalize_categories(categories)
        normalized_severity = self._normalize_severity(severity)
        
        if _INFRASTRUCTURE_AVAILABLE and self.repository:
            # Use full infrastructure
            rumor = await self._create_infrastructure_rumor(
                originator_id, content, normalized_categories, normalized_severity, truth_value
            )
            rumor_id = rumor.id
        else:
            # Use simplified approach
            rumor_id = await self._create_simple_rumor(
                originator_id, content, normalized_categories, normalized_severity, truth_value
            )
        
        # Emit event if enabled
        if self.use_events and self.event_dispatcher:
            await self.event_dispatcher.publish(RumorEvent(
                event_type="rumor.created",
                rumor_id=rumor_id,
                operation="created",
                entity_id=originator_id
            ))
        
        logger.info(f"Created rumor {rumor_id} from entity {originator_id}")
        return rumor_id
    
    async def spread_rumor(self,
                          rumor_id: str,
                          from_entity_id: str,
                          to_entity_id: str,
                          location_type: Optional[str] = None,
                          relationship_strength: float = 0.0) -> bool:
        """
        Spread a rumor between entities using centralized mechanics.
        
        Args:
            rumor_id: ID of the rumor to spread
            from_entity_id: ID of the entity spreading the rumor
            to_entity_id: ID of the entity receiving the rumor
            location_type: Type of location for environmental modifiers
            relationship_strength: Strength of relationship (-1.0 to 1.0)
            
        Returns:
            True if successfully spread, False otherwise
        """
        # Get rumor information
        rumor_info = await self.get_rumor(rumor_id)
        if not rumor_info:
            logger.warning(f"Cannot spread rumor {rumor_id}: not found")
            return False
        
        # Calculate spread probability using centralized configuration
        severity = rumor_info.get("severity", "moderate")
        
        # Get environmental modifiers if configured
        location_modifiers = {}
        if _USE_CENTRALIZED_CONFIG and location_type:
            config = get_rumor_config("environment")
            location_modifiers = config.get("location_modifiers", {}).get(location_type.lower(), {})
        
        # Calculate believability threshold
        if _USE_CENTRALIZED_CONFIG:
            threshold = get_rumor_believability_threshold(severity, relationship_strength)
        else:
            threshold = 0.5  # Default threshold
        
        # Apply location modifiers
        spread_multiplier = location_modifiers.get("spread_multiplier", 1.0)
        mutation_modifier = location_modifiers.get("mutation_chance_modifier", 0.0)
        
        # Determine if rumor spreads
        base_spread_chance = 0.7 * spread_multiplier
        current_believability = rumor_info.get("believability", 0.5)
        
        if current_believability < threshold:
            logger.debug(f"Rumor {rumor_id} believability {current_believability} below threshold {threshold}")
            return False
        
        # Calculate mutation chance
        spread_count = rumor_info.get("spread_count", 0)
        if _USE_CENTRALIZED_CONFIG:
            mutation_chance = get_rumor_mutation_chance(severity, spread_count) + mutation_modifier
        else:
            mutation_chance = 0.2 + mutation_modifier
        
        # Perform the spread
        success = await self._perform_spread(
            rumor_id, from_entity_id, to_entity_id, 
            mutation_chance, spread_multiplier
        )
        
        # Emit event if successful
        if success and self.use_events and self.event_dispatcher:
            await self.event_dispatcher.publish(RumorEvent(
                event_type="rumor.spread",
                rumor_id=rumor_id,
                operation="spread",
                entity_id=to_entity_id,
                additional_data={
                    "from_entity": from_entity_id,
                    "location_type": location_type,
                    "relationship_strength": relationship_strength
                }
            ))
        
        return success
    
    async def decay_rumors(self, days_since_active: int = 1) -> int:
        """
        Apply decay to all active rumors based on their properties.
        
        Args:
            days_since_active: Number of days since rumors were last active
            
        Returns:
            Number of rumors that were decayed
        """
        decayed_count = 0
        
        if _INFRASTRUCTURE_AVAILABLE and self.repository:
            # Get all active rumors from repository
            all_rumors = await self.repository.get_all_active_rumors()
            
            for rumor in all_rumors:
                if _USE_CENTRALIZED_CONFIG:
                    decay_rate = get_rumor_decay_rate(rumor.severity.value, days_since_active)
                else:
                    decay_rate = 0.05 * days_since_active
                
                # Apply decay
                new_believability = max(0.0, rumor.believability - decay_rate)
                if new_believability != rumor.believability:
                    rumor.believability = new_believability
                    await self.repository.save_rumor(rumor)
                    decayed_count += 1
        else:
            # Simplified decay for cached rumors
            for rumor_id, rumor_data in self._rumor_cache.items():
                severity = rumor_data.get("severity", "moderate")
                current_believability = rumor_data.get("believability", 0.5)
                
                if _USE_CENTRALIZED_CONFIG:
                    decay_rate = get_rumor_decay_rate(severity, days_since_active)
                else:
                    decay_rate = 0.05 * days_since_active
                
                new_believability = max(0.0, current_believability - decay_rate)
                if new_believability != current_believability:
                    rumor_data["believability"] = new_believability
                    decayed_count += 1
        
        logger.info(f"Applied decay to {decayed_count} rumors")
        return decayed_count
    
    async def get_rumor(self, rumor_id: str) -> Optional[Dict[str, Any]]:
        """Get rumor information by ID."""
        if _INFRASTRUCTURE_AVAILABLE and self.repository:
            rumor = await self.repository.get_rumor_by_id(rumor_id)
            return self._rumor_to_dict(rumor) if rumor else None
        else:
            return self._rumor_cache.get(rumor_id)
    
    async def get_rumors_for_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all rumors known by a specific entity."""
        if _INFRASTRUCTURE_AVAILABLE and self.repository:
            rumors = await self.repository.get_rumors_for_entity(entity_id)
            return [self._rumor_to_dict(rumor) for rumor in rumors]
        else:
            # Simplified search in cache
            return [rumor for rumor in self._rumor_cache.values() 
                   if entity_id in rumor.get("known_by", [])]
    
    def _normalize_categories(self, categories: List[Union[str, Any]]) -> List[Any]:
        """Normalize category inputs to proper enum values."""
        if not _INFRASTRUCTURE_AVAILABLE:
            return [str(cat).lower() for cat in categories]
        
        normalized = []
        for cat in categories:
            if isinstance(cat, str):
                try:
                    normalized.append(RumorCategory(cat.upper()))
                except ValueError:
                    normalized.append(RumorCategory.OTHER)
            else:
                normalized.append(cat)
        return normalized
    
    def _normalize_severity(self, severity: Union[str, Any]) -> Any:
        """Normalize severity input to proper enum value."""
        if not _INFRASTRUCTURE_AVAILABLE:
            return str(severity).lower()
        
        if isinstance(severity, str):
            try:
                return RumorSeverity(severity.upper())
            except ValueError:
                return RumorSeverity.MODERATE
        return severity
    
    async def _create_infrastructure_rumor(self, originator_id: str, content: str, 
                                         categories: List[Any], severity: Any, 
                                         truth_value: float) -> 'Rumor':
        """Create rumor using full infrastructure."""
        from uuid import uuid4
        
        # Create initial variant
        initial_variant = RumorVariant(
            id=str(uuid4()),
            content=content,
            entity_id=originator_id
        )
        
        # Create rumor
        rumor = Rumor(
            id=str(uuid4()),
            originator_id=originator_id,
            original_content=content,
            categories=categories,
            severity=severity,
            truth_value=truth_value,
            variants=[initial_variant],
            spread=[
                RumorSpread(
                    entity_id=originator_id,
                    variant_id=initial_variant.id,
                    believability=1.0
                )
            ]
        )
        
        await self.repository.save_rumor(rumor)
        return rumor
    
    async def _create_simple_rumor(self, originator_id: str, content: str,
                                 categories: List[str], severity: str,
                                 truth_value: float) -> str:
        """Create rumor using simplified approach."""
        from uuid import uuid4
        
        rumor_id = str(uuid4())
        rumor_data = {
            "id": rumor_id,
            "originator_id": originator_id,
            "content": content,
            "categories": categories,
            "severity": severity,
            "truth_value": truth_value,
            "believability": 1.0,
            "spread_count": 0,
            "known_by": [originator_id],
            "created_at": datetime.utcnow().isoformat()
        }
        
        self._rumor_cache[rumor_id] = rumor_data
        return rumor_id
    
    async def _perform_spread(self, rumor_id: str, from_entity: str, to_entity: str,
                            mutation_chance: float, spread_multiplier: float) -> bool:
        """Perform the actual spreading operation."""
        import random
        
        # Check if mutation occurs
        mutated = random.random() < mutation_chance
        
        if _INFRASTRUCTURE_AVAILABLE and self.repository:
            # Use repository-based spreading
            rumor = await self.repository.get_rumor_by_id(rumor_id)
            if not rumor:
                return False
            
            # Add spread record
            rumor.spread.append(RumorSpread(
                entity_id=to_entity,
                variant_id=rumor.variants[-1].id,  # Use latest variant
                believability=rumor.believability * spread_multiplier
            ))
            
            if mutated:
                # Create new variant
                new_content = self._apply_simple_mutation(rumor.original_content)
                new_variant = RumorVariant(
                    id=str(uuid4()),
                    content=new_content,
                    entity_id=to_entity,
                    parent_variant_id=rumor.variants[-1].id
                )
                rumor.variants.append(new_variant)
            
            await self.repository.save_rumor(rumor)
        else:
            # Use cache-based spreading
            rumor_data = self._rumor_cache.get(rumor_id)
            if not rumor_data:
                return False
            
            known_by = rumor_data.get("known_by", [])
            if to_entity not in known_by:
                known_by.append(to_entity)
                rumor_data["known_by"] = known_by
                rumor_data["spread_count"] = rumor_data.get("spread_count", 0) + 1
            
            if mutated:
                rumor_data["content"] = self._apply_simple_mutation(rumor_data["content"])
        
        return True
    
    def _apply_simple_mutation(self, content: str) -> str:
        """Apply simple mutation to rumor content."""
        import random
        
        mutations = [
            lambda c: c.replace("was", "might have been"),
            lambda c: c.replace("definitely", "supposedly"),
            lambda c: c.replace("at", "somewhere near"),
            lambda c: c.replace("yesterday", "recently"),
            lambda c: c + " (or so I heard)"
        ]
        
        mutation = random.choice(mutations)
        return mutation(content)
    
    def _rumor_to_dict(self, rumor: Any) -> Dict[str, Any]:
        """Convert rumor object to dictionary."""
        if not rumor:
            return {}
        
        if hasattr(rumor, 'dict'):
            return rumor.dict()
        elif hasattr(rumor, '__dict__'):
            return rumor.__dict__
        else:
            return {}


def create_consolidated_rumor_service(
    repository: Optional['RumorRepository'] = None,
    event_dispatcher: Optional['EventDispatcher'] = None,
    use_events: bool = True
) -> ConsolidatedRumorService:
    """Factory function to create consolidated rumor service"""
    return ConsolidatedRumorService(repository, event_dispatcher, use_events) 