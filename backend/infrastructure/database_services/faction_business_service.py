"""
Faction Database Service - Technical Infrastructure

This module handles all database operations for factions.
Extracted from backend/systems/faction/services/services.py
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime

from backend.infrastructure.models.faction.models import (
    FactionEntity,
    FactionModel,
    CreateFactionRequest,
    UpdateFactionRequest,
    FactionResponse
)
from backend.infrastructure.utils.faction.faction_utils import (
    generate_faction_hidden_attributes,
    validate_hidden_attributes
)
from backend.infrastructure.utils.faction.validators import (
    validate_faction_data, 
    validate_faction_name,
    validate_faction_description,
    FactionValidationError
)
from backend.infrastructure.shared.exceptions import (
    FactionNotFoundError,
    FactionConflictError,
    NotFoundError,
    ValidationError
)
from backend.infrastructure.faction_services import FactionDatabaseService


class FactionBusinessDatabaseService:
    """Database service for faction business operations - technical infrastructure"""
    
    def __init__(self, database_service: FactionDatabaseService):
        self.db_service = database_service

    async def create_faction(
        self, 
        request: CreateFactionRequest,
        user_id: Optional[UUID] = None
    ) -> FactionResponse:
        """Create a new faction with comprehensive validation"""
        try:
            # Convert Pydantic model to dict for validation
            faction_data = request.model_dump(exclude_unset=True)
            
            # Comprehensive validation and sanitization
            validated_data = validate_faction_data(faction_data)
            
            # Check for existing faction with same name
            existing_faction = await self.db_service.get_faction_by_name(validated_data['name'])
            if existing_faction:
                raise FactionConflictError(f"Faction with name '{validated_data['name']}' already exists")
            
            # Generate hidden attributes if not provided
            hidden_attrs = {}
            for attr_name in ['hidden_ambition', 'hidden_integrity', 'hidden_discipline', 
                             'hidden_impulsivity', 'hidden_pragmatism', 'hidden_resilience']:
                if attr_name in validated_data:
                    hidden_attrs[attr_name] = validated_data[attr_name]
            
            if not hidden_attrs:
                # Generate random attributes if none provided
                generated_attrs = generate_faction_hidden_attributes()
                hidden_attrs = generated_attrs
            else:
                # Validate and fill missing attributes
                hidden_attrs = validate_hidden_attributes(hidden_attrs)
            
            # Create entity with validated data
            faction_entity = FactionEntity(
                id=uuid4(),
                name=validated_data['name'],
                description=validated_data.get('description'),
                status=validated_data.get('status', 'active'),
                properties=validated_data.get('properties', {}),
                **hidden_attrs  # Unpack hidden attributes
            )
            
            # Add user tracking if provided
            if user_id:
                faction_entity.properties = faction_entity.properties or {}
                faction_entity.properties['created_by'] = str(user_id)
            
            # Save to database via database service
            saved_entity = await self.db_service.create_faction_entity(faction_entity)
            
            # Convert to response model
            return FactionResponse.model_validate(saved_entity)
            
        except FactionValidationError as e:
            raise ValidationError(f"Invalid faction data: {e}")
        except FactionConflictError:
            raise  # Re-raise conflict errors as-is
        except Exception as e:
            raise ValidationError(f"Failed to create faction: {e}")

    async def get_faction_by_id(self, faction_id: UUID) -> Optional[FactionResponse]:
        """Get faction by ID"""
        try:
            entity = await self.db_service.get_faction_by_id(faction_id)
            
            if not entity:
                return None
                
            return FactionResponse.from_orm(entity)
            
        except Exception as e:
            raise

    async def update_faction(
        self, 
        faction_id: UUID, 
        request: UpdateFactionRequest
    ) -> FactionResponse:
        """Update existing faction"""
        try:
            entity = await self.db_service.get_faction_by_id(faction_id)
            if not entity:
                raise FactionNotFoundError(f"Faction {faction_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                # Handle hidden attributes separately for validation
                hidden_attr_updates = {}
                for attr_name in ["hidden_ambition", "hidden_integrity", "hidden_discipline", 
                                "hidden_impulsivity", "hidden_pragmatism", "hidden_resilience"]:
                    if attr_name in update_data:
                        hidden_attr_updates[attr_name] = update_data.pop(attr_name)
                
                # Validate hidden attributes if any are being updated
                if hidden_attr_updates:
                    # Get current values for attributes not being updated
                    current_attrs = entity.get_hidden_attributes()
                    current_attrs.update(hidden_attr_updates)
                    validated_attrs = validate_hidden_attributes(current_attrs)
                    
                    # Apply validated hidden attributes
                    for attr_name, value in validated_attrs.items():
                        setattr(entity, attr_name, value)
                
                # Apply other updates
                for field, value in update_data.items():
                    setattr(entity, field, value)
                    
                # Update via database service
                updated_entity = await self.db_service.update_faction_entity(entity)
            
            return FactionResponse.from_orm(updated_entity)
            
        except Exception as e:
            raise

    async def delete_faction(self, faction_id: UUID) -> bool:
        """Soft delete faction"""
        try:
            entity = await self.db_service.get_faction_by_id(faction_id)
            if not entity:
                raise FactionNotFoundError(f"Faction {faction_id} not found")
            
            return await self.db_service.delete_faction_entity(entity)
            
        except Exception as e:
            raise

    async def list_factions(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[FactionResponse], int]:
        """List factions with pagination and filtering"""
        try:
            entities, total_count = await self.db_service.list_factions(page, size, status, search)
            
            # Convert to response models
            responses = [FactionResponse.from_orm(entity) for entity in entities]
            
            return responses, total_count
            
        except Exception as e:
            raise

    async def get_faction_statistics(self) -> Dict[str, Any]:
        """Get faction statistics"""
        try:
            return await self.db_service.get_faction_statistics()
            
        except Exception as e:
            raise


def create_faction_business_database_service(database_service: FactionDatabaseService) -> FactionBusinessDatabaseService:
    """Factory function to create faction business database service"""
    return FactionBusinessDatabaseService(database_service) 