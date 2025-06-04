"""
Diplomatic Incident Repository for Diplomacy System
"""

from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.systems.diplomacy.models.core_models import DiplomaticIncident, DiplomaticIncidentType
from .base_repository import BaseDiplomacyRepository

class IncidentRepository(BaseDiplomacyRepository[DiplomaticIncident]):
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(db_session)
    
    def create(self, incident_data: Dict) -> DiplomaticIncident:
        return self.infrastructure_repo.create_diplomatic_incident(incident_data)
    
    def get_by_id(self, incident_id: UUID) -> Optional[DiplomaticIncident]:
        return self.infrastructure_repo.get_diplomatic_incident(incident_id)
    
    def update(self, incident_id: UUID, updates: Dict) -> Optional[DiplomaticIncident]:
        return self.infrastructure_repo.update_diplomatic_incident(incident_id, updates)
    
    def delete(self, incident_id: UUID) -> bool:
        return False  # Incidents typically aren't deleted
    
    def list_all(self, **filters) -> List[DiplomaticIncident]:
        return self.infrastructure_repo.list_diplomatic_incidents(**filters) 