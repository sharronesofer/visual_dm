"""
Tension Service - API Facade

Service facade for tension operations - adapts business service to API expectations
according to Development Bible standards.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime

from backend.systems.tension.services.tension_business_service import (
    TensionBusinessService,
    create_tension_business_service
)
from backend.systems.tension.models.tension_events import TensionEventType


class TensionService:
    """
    Facade service for tension operations - renamed from UnifiedTensionManager
    per user clarification to follow faction system naming pattern.
    
    This service acts as the main entry point for tension system operations,
    combining business logic with infrastructure concerns.
    """
    
    def __init__(self, db_session=None):
        """Initialize with database session or fallback to in-memory"""
        self.db_session = db_session
        self.business_service = self._create_business_service()
    
    def _create_business_service(self) -> TensionBusinessService:
        """Create business service with appropriate repositories"""
        try:
            # Try to use database repositories
            if self.db_session:
                from backend.infrastructure.repositories.tension.tension_repository import DatabaseTensionRepository
                tension_repo = DatabaseTensionRepository(self.db_session)
            else:
                from backend.infrastructure.repositories.tension.tension_repository import InMemoryTensionRepository
                tension_repo = InMemoryTensionRepository()
            
            # Load configuration repository
            try:
                from backend.infrastructure.config_loaders.tension.tension_config_repository import JSONTensionConfigRepository
                config_repo = JSONTensionConfigRepository()
            except Exception:
                from backend.infrastructure.config_loaders.tension.tension_config_repository import FallbackTensionConfigRepository
                config_repo = FallbackTensionConfigRepository()
            
            # Try to get faction service (optional)
            faction_service = None
            try:
                from backend.systems.faction.services.services import FactionService
                if self.db_session:
                    faction_service = FactionService(self.db_session)
            except Exception:
                pass  # Faction service is optional
            
            # Create business service
            return create_tension_business_service(
                config_repository=config_repo,
                tension_repository=tension_repo,
                faction_service=faction_service
            )
            
        except Exception:
            # Fallback to minimal configuration if infrastructure fails
            from backend.infrastructure.repositories.tension.tension_repository import InMemoryTensionRepository
            from backend.infrastructure.config_loaders.tension.tension_config_repository import FallbackTensionConfigRepository
            
            return create_tension_business_service(
                config_repository=FallbackTensionConfigRepository(),
                tension_repository=InMemoryTensionRepository()
            )
    
    # Public API methods - delegate to business service
    
    def calculate_tension(self, region_id: str, poi_id: str, current_time: Optional[datetime] = None) -> float:
        """Calculate current tension level for a location"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.business_service.calculate_tension(region_id, poi_id, current_time)
    
    def update_tension_from_event(self, 
                                 region_id: str, 
                                 poi_id: str, 
                                 event_type: Union[TensionEventType, str], 
                                 event_data: Dict[str, Any],
                                 current_time: Optional[datetime] = None) -> float:
        """Update tension based on an event"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.business_service.update_tension_from_event(
            region_id, poi_id, event_type, event_data, current_time
        )
    
    def check_conflict_triggers(self, region_id: str, current_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Check for triggered conflicts in a region"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.business_service.check_conflict_triggers(region_id, current_time)
    
    def add_tension_modifier(self, 
                           region_id: str, 
                           poi_id: str, 
                           modifier_type: str, 
                           value: float, 
                           duration_hours: float,
                           source: str) -> None:
        """Add a temporary tension modifier"""
        self.business_service.add_tension_modifier(
            region_id, poi_id, modifier_type, value, duration_hours, source
        )
    
    def get_regions_by_tension(self, 
                              min_tension: float, 
                              max_tension: float,
                              current_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get regions with tension levels in specified range"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.business_service.get_regions_by_tension(min_tension, max_tension, current_time)
    
    def decay_all_tension(self, current_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Apply decay to all tension in all regions"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.business_service.decay_all_tension(current_time)
    
    # Additional convenience methods for API integration
    
    def get_region_tension_summary(self, region_id: str) -> Dict[str, Any]:
        """Get comprehensive tension summary for a region"""
        current_time = datetime.utcnow()
        
        # Get all tension states for region
        all_states = self.business_service.tension_repository.get_all_tension_states()
        region_states = all_states.get(region_id, {})
        
        if not region_states:
            return {
                'region_id': region_id,
                'poi_count': 0,
                'average_tension': 0.0,
                'max_tension': 0.0,
                'min_tension': 0.0,
                'high_tension_pois': [],
                'conflict_triggers': []
            }
        
        # Calculate tensions for all POIs
        tensions = {}
        for poi_id in region_states.keys():
            tensions[poi_id] = self.calculate_tension(region_id, poi_id, current_time)
        
        tension_values = list(tensions.values())
        avg_tension = sum(tension_values) / len(tension_values)
        max_tension = max(tension_values)
        min_tension = min(tension_values)
        
        # Find high tension POIs (above 0.7)
        high_tension_pois = [
            {'poi_id': poi_id, 'tension': tension}
            for poi_id, tension in tensions.items()
            if tension >= 0.7
        ]
        
        # Check for conflicts
        conflicts = self.check_conflict_triggers(region_id, current_time)
        
        return {
            'region_id': region_id,
            'poi_count': len(region_states),
            'average_tension': round(avg_tension, 3),
            'max_tension': round(max_tension, 3),
            'min_tension': round(min_tension, 3),
            'high_tension_pois': high_tension_pois,
            'conflict_triggers': conflicts,
            'last_updated': current_time.isoformat()
        }
    
    def get_global_tension_report(self) -> Dict[str, Any]:
        """Get global tension statistics"""
        current_time = datetime.utcnow()
        
        all_states = self.business_service.tension_repository.get_all_tension_states()
        
        total_pois = 0
        total_tension = 0.0
        high_tension_regions = []
        
        for region_id, poi_states in all_states.items():
            region_tensions = []
            
            for poi_id in poi_states.keys():
                tension = self.calculate_tension(region_id, poi_id, current_time)
                region_tensions.append(tension)
                total_tension += tension
                total_pois += 1
            
            if region_tensions:
                max_regional_tension = max(region_tensions)
                if max_regional_tension >= 0.7:
                    high_tension_regions.append({
                        'region_id': region_id,
                        'max_tension': round(max_regional_tension, 3),
                        'average_tension': round(sum(region_tensions) / len(region_tensions), 3)
                    })
        
        avg_global_tension = total_tension / total_pois if total_pois > 0 else 0.0
        
        return {
            'total_regions': len(all_states),
            'total_pois': total_pois,
            'average_global_tension': round(avg_global_tension, 3),
            'high_tension_region_count': len(high_tension_regions),
            'high_tension_regions': high_tension_regions,
            'last_updated': current_time.isoformat(),
            'statistics': self.stats
        }
    
    # Expose business service statistics
    @property
    def stats(self) -> Dict[str, Any]:
        """Get tension system statistics"""
        return self.business_service.stats
    
    # Legacy compatibility methods (for backward compatibility)
    def process_player_combat(self, region_id: str, poi_id: str, combat_data: Dict[str, Any]) -> float:
        """Legacy method for player combat processing"""
        return self.update_tension_from_event(
            region_id, poi_id, TensionEventType.PLAYER_COMBAT, combat_data
        )
    
    def process_npc_death(self, region_id: str, poi_id: str, death_data: Dict[str, Any]) -> float:
        """Legacy method for NPC death processing"""
        return self.update_tension_from_event(
            region_id, poi_id, TensionEventType.NPC_DEATH, death_data
        )
    
    def apply_festival_effect(self, region_id: str, poi_id: str, festival_data: Dict[str, Any]) -> None:
        """Apply festival effects that reduce tension"""
        self.update_tension_from_event(
            region_id, poi_id, TensionEventType.FESTIVAL, festival_data
        )

    # Faction Relationship Methods (Development Bible: -100 to +100 scale)
    
    def get_faction_relationship(self, faction_a_id: str, faction_b_id: str, current_time: Optional[datetime] = None):
        """Get relationship between two factions"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.business_service.get_faction_relationship(faction_a_id, faction_b_id, current_time)
    
    def update_faction_tension(self, faction_a_id: str, faction_b_id: str, tension_change: int, source: str = "unknown", current_time: Optional[datetime] = None):
        """Update tension between two factions (Development Bible: -100 to +100 scale)"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.business_service.update_faction_tension(faction_a_id, faction_b_id, tension_change, source, current_time)
    
    def check_war_status(self, faction_a_id: str, faction_b_id: str) -> bool:
        """Check if two factions are at war (Development Bible: war at 70+ tension)"""
        return self.business_service.check_war_status(faction_a_id, faction_b_id)
    
    def get_faction_wars(self):
        """Get all faction relationships currently at war"""
        return self.business_service.get_faction_wars()
    
    def get_faction_alliances(self):
        """Get all faction relationships that are alliances (negative tension)"""
        return self.business_service.get_faction_alliances()
    
    def decay_all_faction_tension(self, current_time: Optional[datetime] = None):
        """Apply daily decay to all faction relationships towards neutral"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.business_service.decay_all_faction_tension(current_time)
    
    def get_faction_relationships_for_faction(self, faction_id: str):
        """Get all relationships involving a specific faction"""
        if not self.business_service.faction_relationship_repository:
            return []
        
        return self.business_service.faction_relationship_repository.get_faction_relationships_for_faction(faction_id)


# Legacy alias for backward compatibility 
UnifiedTensionManager = TensionService 