"""
Treaty Violation Repository for Diplomacy System
"""

from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.systems.diplomacy.models.core_models import TreatyViolation, TreatyViolationType
from .base_repository import BaseDiplomacyRepository

class ViolationRepository(BaseDiplomacyRepository[TreatyViolation]):
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(db_session)
    
    def create(self, entity: TreatyViolation) -> TreatyViolation:
        return self.infrastructure_repo.create_violation(entity)
    
    def get_by_id(self, violation_id: UUID) -> Optional[TreatyViolation]:
        return self.infrastructure_repo.get_violation(violation_id)
    
    def update(self, violation_id: UUID, updates: Dict) -> Optional[TreatyViolation]:
        return self.infrastructure_repo.update_violation(violation_id, updates)
    
    def delete(self, violation_id: UUID) -> bool:
        return False  # Violations typically aren't deleted
    
    def list_all(self, **filters) -> List[TreatyViolation]:
        return self.infrastructure_repo.list_violations(**filters) 