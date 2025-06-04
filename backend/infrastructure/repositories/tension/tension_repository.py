"""
Tension Repository Implementation

Repository implementation for tension state persistence using database storage.
Follows Development Bible standards for repository pattern and data access.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import json

from backend.systems.tension.models.tension_state import TensionState, TensionModifier
from backend.systems.tension.services.tension_business_service import TensionRepository


class InMemoryTensionRepository:
    """In-memory implementation of TensionRepository for testing and fallback"""
    
    def __init__(self):
        self._states: Dict[str, TensionState] = {}
    
    def get_tension_state(self, region_id: str, poi_id: str) -> Optional[TensionState]:
        """Get current tension state for location"""
        key = f"{region_id}:{poi_id}"
        return self._states.get(key)
    
    def save_tension_state(self, region_id: str, poi_id: str, state: TensionState) -> None:
        """Save tension state for location"""
        key = f"{region_id}:{poi_id}"
        self._states[key] = state
    
    def get_all_tension_states(self) -> Dict[str, Dict[str, TensionState]]:
        """Get all tension states grouped by region"""
        result = {}
        
        for key, state in self._states.items():
            region_id, poi_id = key.split(':', 1)
            
            if region_id not in result:
                result[region_id] = {}
            
            result[region_id][poi_id] = state
        
        return result


class DatabaseTensionRepository:
    """Database implementation of TensionRepository using SQLAlchemy"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        # Import here to avoid circular imports
        from backend.infrastructure.models.tension.models import TensionStateModel
        self.TensionStateModel = TensionStateModel
    
    def get_tension_state(self, region_id: str, poi_id: str) -> Optional[TensionState]:
        """Get current tension state for location"""
        try:
            db_state = self.db_session.query(self.TensionStateModel)\
                .filter_by(region_id=region_id, poi_id=poi_id)\
                .first()
            
            if not db_state:
                return None
            
            # Convert database model to domain model
            modifiers = {}
            if db_state.modifiers_json:
                modifiers_data = json.loads(db_state.modifiers_json)
                for mod_type, mod_data in modifiers_data.items():
                    modifiers[mod_type] = TensionModifier(
                        modifier_type=mod_data['modifier_type'],
                        value=mod_data['value'],
                        expiration_time=datetime.fromisoformat(mod_data['expiration_time']),
                        source=mod_data['source']
                    )
            
            recent_events = []
            if db_state.recent_events_json:
                recent_events = json.loads(db_state.recent_events_json)
            
            return TensionState(
                current_level=db_state.current_level,
                base_level=db_state.base_level,
                last_updated=db_state.last_updated,
                recent_events=recent_events,
                modifiers=modifiers
            )
            
        except Exception:
            # Fallback to None if database access fails
            return None
    
    def save_tension_state(self, region_id: str, poi_id: str, state: TensionState) -> None:
        """Save tension state for location"""
        try:
            # Convert domain model to database format
            modifiers_data = {}
            for mod_type, modifier in state.modifiers.items():
                modifiers_data[mod_type] = {
                    'modifier_type': modifier.modifier_type,
                    'value': modifier.value,
                    'expiration_time': modifier.expiration_time.isoformat(),
                    'source': modifier.source
                }
            
            # Find existing record or create new
            db_state = self.db_session.query(self.TensionStateModel)\
                .filter_by(region_id=region_id, poi_id=poi_id)\
                .first()
            
            if not db_state:
                db_state = self.TensionStateModel(
                    region_id=region_id,
                    poi_id=poi_id
                )
                self.db_session.add(db_state)
            
            # Update fields
            db_state.current_level = state.current_level
            db_state.base_level = state.base_level
            db_state.last_updated = state.last_updated
            db_state.recent_events_json = json.dumps(state.recent_events)
            db_state.modifiers_json = json.dumps(modifiers_data) if modifiers_data else None
            
            self.db_session.commit()
            
        except Exception:
            # Rollback on error
            self.db_session.rollback()
    
    def get_all_tension_states(self) -> Dict[str, Dict[str, TensionState]]:
        """Get all tension states grouped by region"""
        try:
            all_db_states = self.db_session.query(self.TensionStateModel).all()
            
            result = {}
            for db_state in all_db_states:
                region_id = db_state.region_id
                poi_id = db_state.poi_id
                
                # Convert to domain model
                domain_state = self.get_tension_state(region_id, poi_id)
                if domain_state:
                    if region_id not in result:
                        result[region_id] = {}
                    result[region_id][poi_id] = domain_state
            
            return result
            
        except Exception:
            # Return empty dict if database access fails
            return {} 