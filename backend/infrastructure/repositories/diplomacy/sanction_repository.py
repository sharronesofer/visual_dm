"""
Sanction Repository for Diplomacy System
"""

from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.systems.diplomacy.models.core_models import Sanction, SanctionType, SanctionStatus
from .base_repository import BaseDiplomacyRepository

class SanctionRepository(BaseDiplomacyRepository[Sanction]):
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(db_session)
    
    def create(self, entity: Sanction) -> Sanction:
        return self.infrastructure_repo.create_sanction(entity)
    
    def get_by_id(self, sanction_id: UUID) -> Optional[Sanction]:
        return self.infrastructure_repo.get_sanction(sanction_id)
    
    def update(self, sanction_id: UUID, updates: Dict) -> Optional[Sanction]:
        return self.infrastructure_repo.update_sanction(sanction_id, updates)
    
    def delete(self, sanction_id: UUID) -> bool:
        return self.infrastructure_repo.delete_sanction(sanction_id)
    
    def list_all(self, **filters) -> List[Sanction]:
        return self.infrastructure_repo.list_sanctions(**filters) 