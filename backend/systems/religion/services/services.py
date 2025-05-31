"""
Religion Services Module

This module provides business logic services for the religion system.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from backend.infrastructure.shared.services import BaseService
from backend.systems.religion.models import (
    ReligionEntity,
    CreateReligionRequest,
    UpdateReligionRequest,
    ReligionResponse
)
from backend.systems.religion.repositories import (
    ReligionRepository,
    get_religion_repository
)
from backend.infrastructure.shared.exceptions import (
    ReligionNotFoundError,
    ReligionValidationError,
    ReligionConflictError
)

# Import event publisher
from backend.systems.religion.events.event_publisher import get_religion_event_publisher

# Try to import WebSocket manager for integration
try:
from backend.systems.religion.services.websocket_manager import religion_websocket_manager
    HAS_WEBSOCKET_MANAGER = True
except ImportError:
    HAS_WEBSOCKET_MANAGER = False

logger = logging.getLogger(__name__)


class ReligionService(BaseService[ReligionEntity]):
    """Service class for religion business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, ReligionEntity)
        self.db = db_session
        self.repository = get_religion_repository(db_session)
        self.event_publisher = get_religion_event_publisher()
        
        # Set up WebSocket integration if available
        if HAS_WEBSOCKET_MANAGER:
            try:
                religion_websocket_manager.religion_service = self
                logger.info("Religion service connected to WebSocket manager")
            except Exception as e:
                logger.warning(f"Could not connect to WebSocket manager: {e}")

    async def create_religion(
        self, 
        request: CreateReligionRequest,
        user_id: Optional[UUID] = None
    ) -> ReligionResponse:
        """Create a new religion with Unity field compatibility"""
        
        try:
            # Build properties dict with Unity frontend fields
            properties = request.properties or {}
            
            # Map Unity frontend fields to properties for storage
            unity_fields = {
                "type": request.type,
                "origin_story": request.origin_story,
                "core_beliefs": request.core_beliefs or [],
                "tenets": request.tenets or [],
                "practices": request.practices or [],
                "holy_places": request.holy_places or [],
                "sacred_texts": request.sacred_texts or [],
                "clergy_structure": request.clergy_structure,
                "followers_count": 0,
                "influence_regions": [],
                "deities": []
            }
            
            # Merge Unity fields with any existing properties
            properties.update({k: v for k, v in unity_fields.items() if v is not None})
            
            # Create the entity
            entity = ReligionEntity(
                name=request.name,
                description=request.description,
                properties=properties,
                status="active",
                is_active=True
            )
            
            # Save to database
            saved_entity = await self.repository.create(entity)
            
            # Create Unity-compatible response
            response = ReligionResponse.from_entity(saved_entity)
            
            # Publish creation event
            self.event_publisher.publish_religion_created(
                religion_id=saved_entity.id,
                name=saved_entity.name,
                religion_type=properties.get("type", "Monotheistic"),
                creator_id=user_id,
                metadata={"properties": properties}
            )
            
            logger.info(f"Created religion: {saved_entity.id} ({saved_entity.name})")
            return response
            
        except Exception as e:
            logger.error(f"Error creating religion: {e}")
            raise

    async def get_religion_by_id(self, religion_id: UUID) -> Optional[ReligionResponse]:
        """Get religion by ID with Unity field compatibility"""
        
        try:
            entity = await self.repository.get_by_id(religion_id)
            if not entity:
                return None
            
            # Create Unity-compatible response
            return ReligionResponse.from_entity(entity)
            
        except Exception as e:
            logger.error(f"Error getting religion {religion_id}: {e}")
            raise

    async def update_religion(
        self, 
        religion_id: UUID, 
        request: UpdateReligionRequest
    ) -> ReligionResponse:
        """Update an existing religion with Unity field compatibility"""
        
        try:
            # Get existing entity
            entity = await self.repository.get_by_id(religion_id)
            if not entity:
                raise ReligionNotFoundError(religion_id)
            
            # Track changes for event publishing
            old_values = {
                "name": entity.name,
                "description": entity.description,
                "status": entity.status,
                "properties": entity.properties.copy() if entity.properties else {}
            }
            
            # Update basic fields
            if request.name is not None:
                entity.name = request.name
            if request.description is not None:
                entity.description = request.description
            if request.status is not None:
                entity.status = request.status
            
            # Update Unity frontend fields in properties
            properties = entity.properties or {}
            
            unity_field_updates = {
                "type": request.type,
                "origin_story": request.origin_story,
                "core_beliefs": request.core_beliefs,
                "tenets": request.tenets,
                "practices": request.practices,
                "holy_places": request.holy_places,
                "sacred_texts": request.sacred_texts,
                "clergy_structure": request.clergy_structure
            }
            
            # Update only provided fields
            for field, value in unity_field_updates.items():
                if value is not None:
                    properties[field] = value
            
            # Merge with any additional properties from request
            if request.properties:
                properties.update(request.properties)
            
            entity.properties = properties
            
            # Save changes
            updated_entity = await self.repository.update(entity)
            
            # Create Unity-compatible response
            response = ReligionResponse.from_entity(updated_entity)
            
            # Publish update event
            changes = {}
            if request.name and request.name != old_values["name"]:
                changes["name"] = request.name
            if request.description and request.description != old_values["description"]:
                changes["description"] = request.description
            if request.status and request.status != old_values["status"]:
                changes["status"] = request.status
            
            # Add Unity field changes
            for field, value in unity_field_updates.items():
                if value is not None and value != old_values["properties"].get(field):
                    changes[field] = value
            
            if changes:
                self.event_publisher.publish_religion_updated(
                    religion_id=updated_entity.id,
                    changes=changes,
                    old_values=old_values
                )
            
            logger.info(f"Updated religion: {updated_entity.id} ({updated_entity.name})")
            return response
            
        except ReligionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating religion {religion_id}: {e}")
            raise

    async def delete_religion(self, religion_id: UUID) -> bool:
        """Soft delete religion"""
        try:
            # Get religion info before deletion for event
            entity = await self.repository.get_by_id(religion_id)
            if not entity:
                raise ReligionNotFoundError(f"Religion {religion_id} not found")
            
            religion_name = entity.name
            result = await self.repository.delete(religion_id)
            
            if result:
                # Publish religion deleted event
                self.event_publisher.publish_religion_deleted(
                    religion_id=religion_id,
                    name=religion_name,
                    reason="user_requested"
                )
                logger.info(f"Deleted religion {religion_id} successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error deleting religion {religion_id}: {str(e)}")
            # Publish error event
            self.event_publisher.publish_religion_error(
                error_type="deletion_error",
                error_message=str(e),
                religion_id=religion_id
            )
            raise

    async def list_religions(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[ReligionResponse], int]:
        """List religions with Unity field compatibility"""
        
        try:
            entities, total = await self.repository.list_paginated(
                page=page,
                size=size,
                filters={"status": status} if status else None,
                search_term=search
            )
            
            # Convert to Unity-compatible responses
            responses = [ReligionResponse.from_entity(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing religions: {e}")
            raise

    async def search_religions(self, query: str, limit: int = 20) -> List[ReligionResponse]:
        """Search religions with Unity field compatibility"""
        
        try:
            entities = await self.repository.search(query, limit)
            
            # Convert to Unity-compatible responses
            return [ReligionResponse.from_entity(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error searching religions with query '{query}': {e}")
            raise

    async def get_religion_by_name(self, name: str) -> Optional[ReligionResponse]:
        """Get religion by name with Unity field compatibility"""
        
        try:
            entity = await self._get_by_name(name)
            if not entity:
                return None
            
            # Create Unity-compatible response
            return ReligionResponse.from_entity(entity)
            
        except Exception as e:
            logger.error(f"Error getting religion by name '{name}': {e}")
            raise

    async def bulk_create_religions(self, requests: List[CreateReligionRequest]) -> List[ReligionResponse]:
        """Bulk create religions with Unity field compatibility"""
        
        try:
            entities = []
            responses = []
            
            for request in requests:
                # Build properties with Unity fields
                properties = request.properties or {}
                
                unity_fields = {
                    "type": request.type,
                    "origin_story": request.origin_story,
                    "core_beliefs": request.core_beliefs or [],
                    "tenets": request.tenets or [],
                    "practices": request.practices or [],
                    "holy_places": request.holy_places or [],
                    "sacred_texts": request.sacred_texts or [],
                    "clergy_structure": request.clergy_structure,
                    "followers_count": 0,
                    "influence_regions": [],
                    "deities": []
                }
                
                properties.update({k: v for k, v in unity_fields.items() if v is not None})
                
                entity = ReligionEntity(
                    name=request.name,
                    description=request.description,
                    properties=properties,
                    status="active",
                    is_active=True
                )
                entities.append(entity)
            
            # Bulk save
            saved_entities = await self.repository.bulk_create(entities)
            
            # Convert to Unity-compatible responses
            for entity in saved_entities:
                response = ReligionResponse.from_entity(entity)
                responses.append(response)
                
                # Publish creation events
                properties = entity.properties or {}
                self.event_publisher.publish_religion_created(
                    religion_id=entity.id,
                    name=entity.name,
                    religion_type=properties.get("type", "Monotheistic"),
                    metadata={"properties": properties}
                )
            
            logger.info(f"Bulk created {len(responses)} religions")
            return responses
            
        except Exception as e:
            logger.error(f"Error bulk creating religions: {e}")
            raise

    async def get_religion_statistics(self) -> Dict[str, Any]:
        """Get religion system statistics"""
        try:
            stats = await self.repository.get_statistics()
            stats["last_updated"] = datetime.utcnow().isoformat()
            
            # Publish system status event
            self.event_publisher.publish_religion_system_status(
                status="healthy",
                metrics=stats,
                message="Religion statistics retrieved successfully"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting religion statistics: {str(e)}")
            # Publish error event
            self.event_publisher.publish_religion_error(
                error_type="statistics_error",
                error_message=str(e)
            )
            raise

    # Event-driven functionality methods
    async def handle_conversion(
        self,
        entity_id: UUID,
        entity_type: str,
        from_religion_id: Optional[UUID],
        to_religion_id: UUID,
        conversion_reason: Optional[str] = None
    ) -> bool:
        """Handle religious conversion with event publishing"""
        try:
            # Publish conversion event
            self.event_publisher.publish_conversion(
                entity_id=entity_id,
                entity_type=entity_type,
                from_religion_id=from_religion_id,
                to_religion_id=to_religion_id,
                conversion_reason=conversion_reason,
                conversion_strength=1.0
            )
            
            logger.info(f"Processed conversion for {entity_type} {entity_id} to religion {to_religion_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling conversion: {str(e)}")
            # Publish error event
            self.event_publisher.publish_religion_error(
                error_type="conversion_error",
                error_message=str(e),
                context={"entity_id": entity_id, "entity_type": entity_type, "from_religion_id": from_religion_id, "to_religion_id": to_religion_id}
            )
            raise

    async def handle_religious_ritual(
        self,
        religion_id: UUID,
        entity_id: UUID,
        ritual_type: str,
        ritual_name: str,
        location: Optional[str] = None,
        participants: Optional[List[UUID]] = None
    ) -> UUID:
        """Handle religious ritual with event publishing"""
        try:
            ritual_id = uuid4()
            
            # Publish ritual event
            self.event_publisher.publish_religious_ritual(
                ritual_id=ritual_id,
                religion_id=religion_id,
                entity_id=entity_id,
                ritual_type=ritual_type,
                ritual_name=ritual_name,
                location=location,
                participants=participants,
                devotion_effect=0.1  # Default small devotion boost
            )
            
            logger.info(f"Processed ritual {ritual_name} for religion {religion_id}")
            return ritual_id
            
        except Exception as e:
            logger.error(f"Error handling religious ritual: {str(e)}")
            # Publish error event
            self.event_publisher.publish_religion_error(
                error_type="ritual_error",
                error_message=str(e),
                religion_id=religion_id,
                context={"ritual_type": ritual_type, "ritual_name": ritual_name}
            )
            raise

    async def handle_religious_narrative(
        self,
        religion_id: UUID,
        narrative_type: str,
        title: str,
        content: str,
        entities_involved: Optional[List[UUID]] = None,
        location: Optional[str] = None,
        impact_level: str = "minor"
    ) -> UUID:
        """Handle religious narrative event publishing"""
        try:
            narrative_id = uuid4()
            
            # Publish narrative event
            self.event_publisher.publish_religious_narrative(
                narrative_id=narrative_id,
                religion_id=religion_id,
                narrative_type=narrative_type,
                title=title,
                content=content,
                entities_involved=entities_involved,
                location=location,
                impact_level=impact_level
            )
            
            logger.info(f"Processed religious narrative for religion {religion_id}: {title}")
            return narrative_id
            
        except Exception as e:
            logger.error(f"Error handling religious narrative: {str(e)}")
            # Publish error event
            self.event_publisher.publish_religion_error(
                error_type="narrative_error",
                error_message=str(e),
                religion_id=religion_id,
                context={"narrative_type": narrative_type, "title": title}
            )
            raise

    # Legacy methods for backward compatibility
    async def _get_by_name(self, name: str) -> Optional[ReligionEntity]:
        """Get entity by name (legacy method)"""
        return await self.repository.get_by_name(name)

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[ReligionEntity]:
        """Get entity by ID (legacy method)"""
        return await self.repository.get_by_id(entity_id)


# Factory function for dependency injection
def create_religion_service(db_session: Session) -> ReligionService:
    """Create religion service instance"""
    return ReligionService(db_session)


def get_religion_service(db_session: Session) -> ReligionService:
    """Get religion service instance (alias for create_religion_service)"""
    return create_religion_service(db_session)
