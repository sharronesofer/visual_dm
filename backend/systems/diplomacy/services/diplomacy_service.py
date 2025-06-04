"""
Diplomacy service implementation.

This module now acts as a facade for the UnifiedDiplomacyService,
maintaining backward compatibility with existing code while delegating
to the consolidated service implementation.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

# Import the unified service
from backend.systems.diplomacy.services.unified_diplomacy_service import UnifiedDiplomacyService
from backend.systems.diplomacy.models.diplomacy_model import DiplomacyModel

class DiplomacyService:
    """
    Service class for diplomacy operations.
    
    This class now serves as a facade for UnifiedDiplomacyService,
    providing backward compatibility for existing CRUD operations.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        # Initialize the unified service
        self._unified_service = UnifiedDiplomacyService(db_session=db_session)
    
    def get_diplomacy(self, diplomacy_id: int) -> Optional[DiplomacyModel]:
        """Get diplomacy by ID."""
        return self._unified_service.get_diplomacy(diplomacy_id)
    
    def get_all_diplomacys(self) -> List[DiplomacyModel]:
        """Get all diplomacy entities."""
        return self._unified_service.get_all_diplomacys()
    
    def create_diplomacy(self, diplomacy_data: Dict[str, Any]) -> DiplomacyModel:
        """Create new diplomacy entity."""
        return self._unified_service.create_diplomacy(diplomacy_data)
    
    def update_diplomacy(self, diplomacy_id: int, updates: Dict[str, Any]) -> Optional[DiplomacyModel]:
        """Update diplomacy entity."""
        return self._unified_service.update_diplomacy(diplomacy_id, updates)
    
    def delete_diplomacy(self, diplomacy_id: int) -> bool:
        """Delete diplomacy entity."""
        return self._unified_service.delete_diplomacy(diplomacy_id)
