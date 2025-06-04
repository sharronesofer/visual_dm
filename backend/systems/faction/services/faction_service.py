"""
Faction system - Business Service Layer

Pure business logic for faction operations following Development Bible standards.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from backend.systems.faction.services.services import (
    FactionBusinessService,
    CreateFactionData,
    UpdateFactionData,
    FactionData
)

# Import the exception that tests expect
from backend.infrastructure.shared.exceptions import (
    FactionNotFoundError,
    FactionValidationError,
    FactionConflictError
)

# Create alias for DuplicateFactionError
DuplicateFactionError = FactionConflictError


class FactionService:
    """
    Pure business logic service for faction operations.
    
    This service contains only business rules and delegates to the business service
    for implementation details. It serves as the primary interface for faction
    operations within the system domain.
    """
    
    def __init__(self, business_service: FactionBusinessService):
        self.business_service = business_service
    
    def create_faction(
        self, 
        name: str,
        description: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        user_id: Optional[UUID] = None,
        **hidden_attributes
    ) -> FactionData:
        """
        Create a new faction with business validation.
        
        Args:
            name: Faction name (required)
            description: Optional description
            properties: Optional properties dictionary
            user_id: Optional user creating the faction
            **hidden_attributes: Hidden attribute values (1-10 range)
            
        Returns:
            FactionData: Created faction data
            
        Raises:
            FactionValidationError: If validation fails
            FactionConflictError: If faction name already exists
        """
        try:
            create_data = CreateFactionData(
                name=name,
                description=description,
                properties=properties or {},
                **hidden_attributes
            )
            
            return self.business_service.create_faction(create_data, user_id)
            
        except ValueError as e:
            if "already exists" in str(e):
                raise FactionConflictError(str(e))
            else:
                raise FactionValidationError(str(e))
    
    def get_faction_by_id(self, faction_id: UUID) -> Optional[FactionData]:
        """
        Get faction by ID.
        
        Args:
            faction_id: UUID of the faction
            
        Returns:
            FactionData or None if not found
        """
        return self.business_service.get_faction_by_id(faction_id)
    
    def get_faction_by_name(self, name: str) -> Optional[FactionData]:
        """
        Get faction by name.
        
        Args:
            name: Name of the faction
            
        Returns:
            FactionData or None if not found
        """
        # Business service doesn't have get_by_name, would need to add to repository
        # For now, delegate to business service's repository
        return self.business_service.faction_repository.get_faction_by_name(name)
    
    def update_faction(
        self, 
        faction_id: UUID, 
        **update_fields
    ) -> FactionData:
        """
        Update faction with business validation.
        
        Args:
            faction_id: UUID of faction to update
            **update_fields: Fields to update
            
        Returns:
            Updated FactionData
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
            FactionValidationError: If validation fails
        """
        try:
            update_data = UpdateFactionData(**update_fields)
            return self.business_service.update_faction(faction_id, update_data)
            
        except ValueError as e:
            if "not found" in str(e):
                raise FactionNotFoundError(str(e))
            else:
                raise FactionValidationError(str(e))
    
    def delete_faction(self, faction_id: UUID) -> bool:
        """
        Delete faction.
        
        Args:
            faction_id: UUID of faction to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        try:
            return self.business_service.delete_faction(faction_id)
        except ValueError as e:
            raise FactionNotFoundError(str(e))
    
    def list_factions(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[FactionData], int]:
        """
        List factions with pagination.
        
        Args:
            page: Page number (1-based)
            size: Page size
            status: Optional status filter
            search: Optional search term
            
        Returns:
            Tuple of (faction_list, total_count)
        """
        return self.business_service.list_factions(page, size, status, search)
    
    def calculate_power_score(self, faction_id: UUID) -> float:
        """
        Calculate faction power score.
        
        Args:
            faction_id: UUID of faction
            
        Returns:
            Power score (0.0-10.0)
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        faction = self.get_faction_by_id(faction_id)
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        return self.business_service.calculate_faction_power_score(faction)
    
    def assess_stability(self, faction_id: UUID) -> Dict[str, Any]:
        """
        Assess faction stability.
        
        Args:
            faction_id: UUID of faction
            
        Returns:
            Stability assessment data
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        faction = self.get_faction_by_id(faction_id)
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        return self.business_service.assess_faction_stability(faction)
    
    def predict_behavior_tendencies(self, faction_id: UUID) -> Dict[str, Any]:
        """
        Predict faction behavior tendencies.
        
        Args:
            faction_id: UUID of faction
            
        Returns:
            Behavior tendency predictions
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        faction = self.get_faction_by_id(faction_id)
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        return self.business_service.predict_faction_behavior_tendencies(faction)


# Legacy compatibility function for tests
def placeholder_function():
    """Placeholder function."""
    pass
