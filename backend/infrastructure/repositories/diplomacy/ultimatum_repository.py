"""
Ultimatum Repository for Diplomacy System
"""

from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.systems.diplomacy.models.core_models import Ultimatum, UltimatumStatus
from .base_repository import BaseDiplomacyRepository

class UltimatumRepository(BaseDiplomacyRepository[Ultimatum]):
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(db_session)
    
    def create(self, ultimatum_data: Dict) -> Ultimatum:
        return self.infrastructure_repo.create_ultimatum(ultimatum_data)
    
    def get_by_id(self, ultimatum_id: UUID) -> Optional[Ultimatum]:
        return self.infrastructure_repo.get_ultimatum(ultimatum_id)
    
    def update(self, ultimatum_id: UUID, updates: Dict) -> Optional[Ultimatum]:
        return self.infrastructure_repo.update_ultimatum(ultimatum_id, updates)
    
    def delete(self, ultimatum_id: UUID) -> bool:
        return False  # Ultimatums typically aren't deleted
    
    def list_all(self, **filters) -> List[Ultimatum]:
        return self.infrastructure_repo.list_ultimatums(**filters) 