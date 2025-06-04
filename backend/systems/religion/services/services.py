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
# Import repository from infrastructure
from backend.infrastructure.systems.religion.repositories import (
    ReligionRepository,
    get_religion_repository
)
from backend.systems.religion.models.exceptions import (
    ReligionNotFoundError,
    ReligionValidationError,
    ReligionConflictError
)

# Import event publisher from infrastructure
from backend.infrastructure.systems.religion.events.event_publisher import get_religion_event_publisher

# Try to import WebSocket manager from infrastructure
try:
    from backend.infrastructure.systems.religion.websocket.websocket_manager import religion_websocket_manager
    HAS_WEBSOCKET_MANAGER = True
except ImportError:
    HAS_WEBSOCKET_MANAGER = False

logger = logging.getLogger(__name__)


class ReligionService(BaseService[ReligionEntity]):
    """Service class for religion business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, ReligionEntity)
        self.db = db_session
        self.db_session = db_session  # Add this for test compatibility
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
            saved_entity = await self.repository.create(request, user_id)
            
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
            # Publish error event
            self.event_publisher.publish_religion_error(
                error_type="creation_error",
                error_message=str(e)
            )
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
            # Publish error event
            self.event_publisher.publish_religion_error(
                error_type="get_religion_error",
                error_message=str(e),
                religion_id=religion_id
            )
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
            entities, total = await self.repository.list_all(
                page=page,
                size=size,
                status=status,
                search=search
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

    async def create_membership(
        self, 
        entity_id: UUID, 
        religion_id: UUID,
        devotion_level: float = 0.5,
        role: Optional[str] = None,
        recruited_by: Optional[UUID] = None,
        conversion_reason: Optional[str] = None
    ) -> "ReligionMembershipEntity":
        """
        Create a new religion membership in database
        
        Args:
            entity_id: ID of the entity (character/NPC) joining
            religion_id: ID of the religion being joined
            devotion_level: Initial devotion level (0.0 to 1.0)
            role: Optional role in the religion
            recruited_by: Optional ID of who recruited them
            conversion_reason: Optional reason for joining
            
        Returns:
            Created membership entity
        """
        try:
            from backend.systems.religion.models.models import ReligionMembershipEntity
            
            # Check if religion exists
            religion = await self.get_religion_by_id(religion_id)
            if not religion:
                raise ReligionNotFoundError(religion_id)
            
            # Check for existing membership
            existing = self.db_session.query(ReligionMembershipEntity).filter(
                ReligionMembershipEntity.entity_id == entity_id,
                ReligionMembershipEntity.religion_id == religion_id,
                ReligionMembershipEntity.is_active == True
            ).first()
            
            if existing:
                raise ReligionConflictError(f"Entity {entity_id} is already a member of religion {religion_id}")
            
            # Create new membership
            membership = ReligionMembershipEntity(
                entity_id=entity_id,
                religion_id=religion_id,
                devotion_level=max(0.0, min(1.0, devotion_level)),  # Clamp to valid range
                role=role,
                recruited_by=recruited_by,
                conversion_reason=conversion_reason
            )
            
            self.db_session.add(membership)
            self.db_session.commit()
            self.db_session.refresh(membership)
            
            # Publish membership event
            self.event_publisher.publish_conversion(
                entity_id=entity_id,
                entity_type="character",  # Default, could be parameterized
                from_religion_id=None,
                to_religion_id=religion_id,
                conversion_reason=conversion_reason or "new_member"
            )
            
            return membership
            
        except Exception as e:
            self.db_session.rollback()
            self.event_publisher.publish_religion_error(
                error_type="membership_creation_failed",
                error_message=str(e),
                religion_id=religion_id,
                entity_id=entity_id
            )
            raise

    async def update_membership(
        self,
        membership_id: UUID,
        devotion_level: Optional[float] = None,
        role: Optional[str] = None,
        status: Optional[str] = None
    ) -> "ReligionMembershipEntity":
        """
        Update an existing religion membership
        
        Args:
            membership_id: ID of the membership to update
            devotion_level: New devotion level
            role: New role
            status: New status
            
        Returns:
            Updated membership entity
        """
        try:
            from backend.systems.religion.models.models import ReligionMembershipEntity
            
            membership = self.db_session.query(ReligionMembershipEntity).filter(
                ReligionMembershipEntity.id == membership_id,
                ReligionMembershipEntity.is_active == True
            ).first()
            
            if not membership:
                raise ReligionNotFoundError(f"Membership {membership_id} not found")
            
            # Update fields
            if devotion_level is not None:
                membership.devotion_level = max(0.0, min(1.0, devotion_level))
            if role is not None:
                membership.role = role
            if status is not None:
                membership.status = status
                if status in ["inactive", "excommunicated", "left"]:
                    membership.left_at = datetime.utcnow()
            
            membership.last_activity = datetime.utcnow()
            membership.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            self.db_session.refresh(membership)
            
            return membership
            
        except Exception as e:
            self.db_session.rollback()
            self.event_publisher.publish_religion_error(
                error_type="membership_update_failed",
                error_message=str(e),
                membership_id=membership_id
            )
            raise

    async def get_entity_memberships(self, entity_id: UUID) -> List["ReligionMembershipEntity"]:
        """
        Get all religion memberships for an entity
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            List of membership entities
        """
        try:
            from backend.systems.religion.models.models import ReligionMembershipEntity
            
            memberships = self.db_session.query(ReligionMembershipEntity).filter(
                ReligionMembershipEntity.entity_id == entity_id,
                ReligionMembershipEntity.is_active == True
            ).all()
            
            return memberships
            
        except Exception as e:
            self.event_publisher.publish_religion_error(
                error_type="membership_retrieval_failed",
                error_message=str(e),
                entity_id=entity_id
            )
            raise

    async def get_religion_members(
        self, 
        religion_id: UUID,
        status: Optional[str] = None,
        role: Optional[str] = None
    ) -> List["ReligionMembershipEntity"]:
        """
        Get all members of a religion
        
        Args:
            religion_id: ID of the religion
            status: Optional status filter
            role: Optional role filter
            
        Returns:
            List of membership entities
        """
        try:
            from backend.systems.religion.models.models import ReligionMembershipEntity
            
            query = self.db_session.query(ReligionMembershipEntity).filter(
                ReligionMembershipEntity.religion_id == religion_id,
                ReligionMembershipEntity.is_active == True
            )
            
            if status:
                query = query.filter(ReligionMembershipEntity.status == status)
            if role:
                query = query.filter(ReligionMembershipEntity.role == role)
            
            members = query.all()
            return members
            
        except Exception as e:
            self.event_publisher.publish_religion_error(
                error_type="member_retrieval_failed",
                error_message=str(e),
                religion_id=religion_id
            )
            raise

    async def calculate_regional_influence(
        self, 
        religion_id: UUID, 
        region_id: str,
        force_recalculate: bool = False
    ) -> "RegionalInfluenceEntity":
        """
        Calculate and cache regional influence for a religion
        
        Args:
            religion_id: ID of the religion
            region_id: ID of the region
            force_recalculate: Whether to force recalculation even if cache is fresh
            
        Returns:
            Regional influence entity with cached data
        """
        try:
            from backend.systems.religion.models.models import (
                RegionalInfluenceEntity, 
                ReligionMembershipEntity
            )
            
            # Check for existing cached data
            existing = self.db_session.query(RegionalInfluenceEntity).filter(
                RegionalInfluenceEntity.religion_id == religion_id,
                RegionalInfluenceEntity.region_id == region_id
            ).first()
            
            # Determine if we need to recalculate
            needs_calculation = (
                force_recalculate or 
                not existing or 
                existing.is_stale or
                (datetime.utcnow() - existing.last_calculated).total_seconds() > 3600  # 1 hour cache
            )
            
            if not needs_calculation:
                return existing
            
            # Calculate influence metrics
            # Count active members in this region (would need region data integration)
            member_count = self.db_session.query(ReligionMembershipEntity).filter(
                ReligionMembershipEntity.religion_id == religion_id,
                ReligionMembershipEntity.status == "active",
                ReligionMembershipEntity.is_active == True
            ).count()
            
            # Calculate influence factors (simplified for now)
            # In a real implementation, this would integrate with region, character, and faction systems
            base_influence = min(1.0, member_count / 1000.0)  # Scale based on member count
            
            # Political influence (would check for members in government positions)
            political_influence = base_influence * 0.3
            
            # Economic influence (would check for member wealth/business ownership)
            economic_influence = base_influence * 0.25
            
            # Cultural influence (would check for cultural events, art, etc.)
            cultural_influence = base_influence * 0.35
            
            # Military influence (would check for members in military)
            military_influence = base_influence * 0.1
            
            # Overall influence is weighted average
            overall_influence = (
                political_influence * 0.3 +
                economic_influence * 0.25 +
                cultural_influence * 0.35 +
                military_influence * 0.1
            )
            
            # Create or update cached data
            if existing:
                existing.influence_level = overall_influence
                existing.follower_count = member_count
                existing.political_influence = political_influence
                existing.economic_influence = economic_influence
                existing.cultural_influence = cultural_influence
                existing.military_influence = military_influence
                existing.last_calculated = datetime.utcnow()
                existing.is_stale = False
                existing.calculation_version += 1
                influence_entity = existing
            else:
                influence_entity = RegionalInfluenceEntity(
                    religion_id=religion_id,
                    region_id=region_id,
                    influence_level=overall_influence,
                    follower_count=member_count,
                    political_influence=political_influence,
                    economic_influence=economic_influence,
                    cultural_influence=cultural_influence,
                    military_influence=military_influence,
                    last_calculated=datetime.utcnow(),
                    is_stale=False,
                    calculation_version=1
                )
                self.db_session.add(influence_entity)
            
            self.db_session.commit()
            self.db_session.refresh(influence_entity)
            
            return influence_entity
            
        except Exception as e:
            self.db_session.rollback()
            self.event_publisher.publish_religion_error(
                error_type="influence_calculation_failed",
                error_message=str(e),
                religion_id=religion_id,
                region_id=region_id
            )
            raise

    async def get_regional_influence(
        self, 
        religion_id: UUID, 
        region_id: str
    ) -> Optional["RegionalInfluenceEntity"]:
        """
        Get cached regional influence data
        
        Args:
            religion_id: ID of the religion
            region_id: ID of the region
            
        Returns:
            Regional influence entity or None if not found
        """
        try:
            from backend.systems.religion.models.models import RegionalInfluenceEntity
            
            influence = self.db_session.query(RegionalInfluenceEntity).filter(
                RegionalInfluenceEntity.religion_id == religion_id,
                RegionalInfluenceEntity.region_id == region_id
            ).first()
            
            # If data is stale, trigger recalculation in background
            if influence and influence.is_stale:
                # In a real implementation, this would be queued for background processing
                pass
            
            return influence
            
        except Exception as e:
            self.event_publisher.publish_religion_error(
                error_type="influence_retrieval_failed",
                error_message=str(e),
                religion_id=religion_id,
                region_id=region_id
            )
            raise

    async def invalidate_regional_influence_cache(
        self, 
        religion_id: Optional[UUID] = None,
        region_id: Optional[str] = None
    ) -> int:
        """
        Mark regional influence cache as stale for recalculation
        
        Args:
            religion_id: Optional specific religion ID
            region_id: Optional specific region ID
            
        Returns:
            Number of cache entries marked as stale
        """
        try:
            from backend.systems.religion.models.models import RegionalInfluenceEntity
            
            query = self.db_session.query(RegionalInfluenceEntity)
            
            if religion_id:
                query = query.filter(RegionalInfluenceEntity.religion_id == religion_id)
            if region_id:
                query = query.filter(RegionalInfluenceEntity.region_id == region_id)
            
            count = query.update({"is_stale": True})
            self.db_session.commit()
            
            return count
            
        except Exception as e:
            self.db_session.rollback()
            self.event_publisher.publish_religion_error(
                error_type="cache_invalidation_failed",
                error_message=str(e),
                religion_id=religion_id,
                region_id=region_id
            )
            raise

    async def get_religion_influence_summary(self, religion_id: UUID) -> Dict[str, Any]:
        """
        Get a summary of religion's influence across all regions
        
        Args:
            religion_id: ID of the religion
            
        Returns:
            Dictionary with influence summary data
        """
        try:
            from backend.systems.religion.models.models import RegionalInfluenceEntity
            
            influences = self.db_session.query(RegionalInfluenceEntity).filter(
                RegionalInfluenceEntity.religion_id == religion_id
            ).all()
            
            if not influences:
                return {
                    "total_regions": 0,
                    "average_influence": 0.0,
                    "total_followers": 0,
                    "strongest_region": None,
                    "weakest_region": None,
                    "influence_breakdown": {}
                }
            
            total_followers = sum(inf.follower_count for inf in influences)
            average_influence = sum(inf.influence_level for inf in influences) / len(influences)
            
            strongest = max(influences, key=lambda x: x.influence_level)
            weakest = min(influences, key=lambda x: x.influence_level)
            
            breakdown = {
                "political": sum(inf.political_influence for inf in influences) / len(influences),
                "economic": sum(inf.economic_influence for inf in influences) / len(influences),
                "cultural": sum(inf.cultural_influence for inf in influences) / len(influences),
                "military": sum(inf.military_influence for inf in influences) / len(influences)
            }
            
            return {
                "total_regions": len(influences),
                "average_influence": average_influence,
                "total_followers": total_followers,
                "strongest_region": {
                    "region_id": strongest.region_id,
                    "influence_level": strongest.influence_level
                },
                "weakest_region": {
                    "region_id": weakest.region_id,
                    "influence_level": weakest.influence_level
                },
                "influence_breakdown": breakdown,
                "last_updated": max(inf.last_calculated for inf in influences).isoformat()
            }
            
        except Exception as e:
            self.event_publisher.publish_religion_error(
                error_type="influence_summary_failed",
                error_message=str(e),
                religion_id=religion_id
            )
            raise

    async def join_religion(self, entity_id: str, religion_id: str, 
                         entity_type: str = "character", role: Optional[str] = None,
                         initial_devotion: float = 0.5) -> Dict[str, Any]:
        """
        Allow an entity to join a religion.
        
        CROSS-FACTION SUPPORT: This method allows entities from any faction 
        to join any religion, as per Bible requirements.
        
        Args:
            entity_id: ID of the entity joining
            religion_id: ID of the religion to join
            entity_type: Type of entity (character, npc, etc.)
            role: Optional specific role in the religion
            initial_devotion: Starting devotion level (0.0-1.0)
            
        Returns:
            Dict containing the membership data
        """
        # Validate inputs
        if not (0.0 <= initial_devotion <= 1.0):
            raise ValueError("Devotion must be between 0.0 and 1.0")
        
        # Check if religion exists
        religion = await self.get_religion_by_id(religion_id)
        if not religion:
            raise ValueError(f"Religion {religion_id} not found")
        
        # Note: We deliberately DO NOT check faction restrictions here
        # as the Bible specifies cross-faction membership is required
        
        # Create membership record
        membership_id = str(uuid4())
        membership_data = {
            "id": membership_id,
            "entity_id": entity_id,
            "religion_id": religion_id,
            "entity_type": entity_type,
            "devotion": initial_devotion,  # Use float 0.0-1.0 scale
            "status": "member",           # Active membership status
            "role": role,                 # Optional specific role
            "joined_date": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "is_public": True,            # Default to public membership
            "metadata": {}
        }
        
        # Store membership
        success = await self.repository.create_membership(membership_data)
        if success:
            logger.info(f"Entity {entity_id} joined religion {religion_id}")
            return membership_data
        else:
            logger.error(f"Failed to create membership for entity {entity_id}")
            raise Exception("Failed to create membership")

    async def leave_religion(self, entity_id: str, religion_id: str) -> bool:
        """Remove an entity from a religion."""
        success = await self.repository.remove_membership(entity_id, religion_id)
        if success:
            logger.info(f"Entity {entity_id} left religion {religion_id}")
        return success

    async def update_devotion(self, entity_id: str, religion_id: str, 
                           change_amount: float, reason: Optional[str] = None) -> bool:
        """
        Update an entity's devotion to a religion.
        
        Args:
            entity_id: Entity whose devotion to update
            religion_id: Religion to update devotion for
            change_amount: Amount to change devotion by (can be negative)
            reason: Optional reason for the change
            
        Returns:
            True if successful, False otherwise
        """
        membership = await self.repository.get_membership(entity_id, religion_id)
        if not membership:
            logger.warning(f"No membership found for entity {entity_id} in religion {religion_id}")
            return False
        
        # Calculate new devotion (ensure it stays in 0.0-1.0 range)
        current_devotion = membership.get("devotion", 0.5)
        new_devotion = max(0.0, min(1.0, current_devotion + change_amount))
        
        # Update the membership
        success = await self.repository.update_membership_devotion(
            entity_id, religion_id, new_devotion, reason
        )
        
        if success:
            logger.info(f"Updated devotion for entity {entity_id} in religion {religion_id}: {current_devotion} -> {new_devotion}")
        
        return success

    async def get_entity_religions(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get all religions an entity belongs to.
        
        This supports the cross-faction membership requirement by returning
        all religions regardless of the entity's faction.
        """
        memberships = await self.repository.get_entity_memberships(entity_id)
        religions = []
        
        for membership in memberships:
            religion = await self.get_religion_by_id(UUID(membership["religion_id"]))
            if religion:
                # Combine religion and membership data
                combined_data = {
                    **religion,
                    "membership": membership
                }
                religions.append(combined_data)
        
        return religions

    async def get_religion_influence(self, religion_id: str, region_id: Optional[str] = None) -> float:
        """Calculate religion's influence in a region or globally."""
        # This would integrate with the regional influence system
        # For now, return a basic calculation
        members = await self.get_religion_members(UUID(religion_id))
        if not members:
            return 0.0
        
        # Basic influence calculation based on member count and average devotion
        total_devotion = sum(member.get("devotion", 0.5) for member in members)
        average_devotion = total_devotion / len(members)
        
        # Simple influence formula (can be enhanced)
        influence = len(members) * average_devotion * 0.1
        return min(1.0, influence)  # Cap at 1.0


# Factory function for dependency injection
def create_religion_service(db_session: Session) -> ReligionService:
    """Create religion service instance"""
    return ReligionService(db_session)


def get_religion_service(db_session: Session) -> ReligionService:
    """Get religion service instance (alias for create_religion_service)"""
    return create_religion_service(db_session)
