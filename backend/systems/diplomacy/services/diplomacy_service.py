"""
Diplomacy service implementation.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from backend.systems.diplomacymodels.diplomacy_model import DiplomacyModel

class DiplomacyService:
    """Service class for diplomacy operations."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
    
    def get_diplomacy(self, diplomacy_id: int) -> Optional[DiplomacyModel]:
        """Get diplomacy by ID."""
        if not self.db_session:
            # Mock implementation for testing
            return DiplomacyModel(
                id=diplomacy_id,
                name=f"Diplomacy {diplomacy_id}",
                description=f"Mock diplomacy entity"
            )
        
        return self.db_session.query(DiplomacyModel).filter(
            DiplomacyModel.id == diplomacy_id
        ).first()
    
    def get_all_diplomacys(self) -> List[DiplomacyModel]:
        """Get all diplomacy entities."""
        if not self.db_session:
            # Mock implementation
            return [
                DiplomacyModel(id=1, name=f"Mock Diplomacy 1"),
                DiplomacyModel(id=2, name=f"Mock Diplomacy 2")
            ]
        
        return self.db_session.query(DiplomacyModel).all()
    
    def create_diplomacy(self, diplomacy_data: Dict[str, Any]) -> DiplomacyModel:
        """Create new diplomacy entity."""
        diplomacy_obj = DiplomacyModel.from_dict(diplomacy_data)
        
        if self.db_session:
            self.db_session.add(diplomacy_obj)
            self.db_session.commit()
            self.db_session.refresh(diplomacy_obj)
        
        return diplomacy_obj
    
    def update_diplomacy(self, diplomacy_id: int, updates: Dict[str, Any]) -> Optional[DiplomacyModel]:
        """Update diplomacy entity."""
        diplomacy_obj = self.get_diplomacy(diplomacy_id)
        
        if diplomacy_obj:
            for key, value in updates.items():
                if hasattr(diplomacy_obj, key):
                    setattr(diplomacy_obj, key, value)
            
            if self.db_session:
                self.db_session.commit()
                self.db_session.refresh(diplomacy_obj)
        
        return diplomacy_obj
    
    def delete_diplomacy(self, diplomacy_id: int) -> bool:
        """Diplomacy delete diplomacy entity."""
        diplomacy_obj = self.get_diplomacy(diplomacy_id)
        
        if diplomacy_obj and self.db_session:
            self.db_session.delete(diplomacy_obj)
            self.db_session.commit()
            return True
        
        return False
