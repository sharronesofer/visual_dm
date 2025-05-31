"""
Comprehensive NPC Service

Main service class for NPC operations including CRUD, memory management,
faction relationships, rumors, motifs, and location tracking.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
import logging

# Use canonical imports instead of dynamic loading
from backend.systems.npc.models import (
    NpcEntity, CreateNpcRequest, UpdateNpcRequest, NpcResponse
)

from backend.infrastructure.shared.exceptions import (
    NpcNotFoundError,
    NpcValidationError,
    NpcConflictError
)
from backend.infrastructure.database import get_db

# Import the new repositories
from backend.systems.npc.repositories.npc_repository import NPCRepository
from backend.systems.npc.repositories.npc_memory_repository import NPCMemoryRepository
from backend.systems.npc.repositories.npc_location_repository import NPCLocationRepository

# Import event publisher
from backend.systems.npc.events.event_publisher import get_npc_event_publisher

logger = logging.getLogger(__name__)


class NPCService:
    """
    Comprehensive NPC Service class that manages all NPC operations using repository pattern.
    This is the main service class that all tests expect to find.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the NPCService with database session and repositories."""
        self.db = db_session if db_session else next(get_db())
        self._is_external_session = db_session is not None
        
        # Initialize repositories
        self.npc_repository = NPCRepository(self.db)
        self.memory_repository = NPCMemoryRepository(self.db)
        self.location_repository = NPCLocationRepository(self.db)
        
        # Initialize event publisher
        self.event_publisher = get_npc_event_publisher()

    def __del__(self):
        """Clean up database session if we created it."""
        if not self._is_external_session and hasattr(self, 'db'):
            try:
                self.db.close()
            except:
                pass

    # =========================================================================
    # Core CRUD Operations
    # =========================================================================
    
    async def create_npc(
        self, 
        request: CreateNpcRequest,
        user_id: Optional[UUID] = None
    ) -> NpcResponse:
        """Create a new NPC using repository"""
        try:
            logger.info(f"Creating NPC: {request.name}")
            
            # Use repository to create NPC
            entity = self.npc_repository.create_npc(request)
            
            # Publish NPC created event
            self.event_publisher.publish_npc_created(
                npc_id=entity.id,
                name=entity.name,
                race=entity.race,
                region_id=entity.region_id,
                location=entity.location,
                npc_data=request.npc_data if hasattr(request, 'npc_data') else None
            )
            
            logger.info(f"Created NPC {entity.id} successfully")
            return NpcResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating NPC: {str(e)}")
            self.event_publisher.publish_npc_error(
                error_type="creation_failed",
                error_message=str(e),
                operation="create_npc"
            )
            raise

    async def get_npc(self, npc_id: UUID) -> Optional[NpcResponse]:
        """Get NPC by ID using repository"""
        try:
            entity = self.npc_repository.get_npc(npc_id, include_relationships=True)
            
            if not entity:
                return None
                
            return NpcResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting NPC {npc_id}: {str(e)}")
            raise

    async def update_npc(
        self, 
        npc_id: UUID, 
        request: UpdateNpcRequest
    ) -> NpcResponse:
        """Update existing NPC using repository"""
        try:
            # Get old entity for change tracking
            old_entity = self.npc_repository.get_npc(npc_id)
            if not old_entity:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            # Track changes for event
            old_values = {
                "name": old_entity.name,
                "status": old_entity.status,
                "description": old_entity.description,
                "properties": old_entity.properties
            }
            
            entity = self.npc_repository.update_npc(npc_id, request)
            
            # Build changes dict
            changes = {}
            if hasattr(request, 'name') and request.name and request.name != old_entity.name:
                changes["name"] = request.name
            if hasattr(request, 'status') and request.status and request.status != old_entity.status:
                changes["status"] = request.status
            if hasattr(request, 'description') and request.description != old_entity.description:
                changes["description"] = request.description
            if hasattr(request, 'properties') and request.properties != old_entity.properties:
                changes["properties"] = request.properties
            
            # Publish status change event if status changed
            if "status" in changes:
                self.event_publisher.publish_npc_status_changed(
                    npc_id=entity.id,
                    old_status=old_entity.status,
                    new_status=entity.status,
                    reason="manual_update"
                )
            
            # Publish general update event
            if changes:
                self.event_publisher.publish_npc_updated(
                    npc_id=entity.id,
                    changes=changes,
                    old_values=old_values
                )
            
            logger.info(f"Updated NPC {entity.id} successfully")
            return NpcResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="update_failed",
                error_message=str(e),
                operation="update_npc"
            )
            raise

    async def delete_npc(self, npc_id: UUID) -> bool:
        """Soft delete NPC using repository"""
        try:
            # Get entity for event data
            entity = self.npc_repository.get_npc(npc_id)
            if not entity:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            result = self.npc_repository.delete_npc(npc_id, soft_delete=True)
            
            # Publish NPC deleted event
            self.event_publisher.publish_npc_deleted(
                npc_id=npc_id,
                name=entity.name,
                soft_delete=True
            )
            
            logger.info(f"Deleted NPC {npc_id} successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error deleting NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="deletion_failed",
                error_message=str(e),
                operation="delete_npc"
            )
            raise

    async def list_npcs(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None,
        region_id: Optional[str] = None
    ) -> Tuple[List[NpcResponse], int]:
        """List NPCs with pagination and filters using repository"""
        try:
            entities, total = self.npc_repository.list_npcs(
                page=page,
                size=size,
                status=status,
                search=search,
                region_id=region_id
            )
            
            # Convert to response models
            responses = [NpcResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing NPCs: {str(e)}")
            raise

    # =========================================================================
    # Memory Management
    # =========================================================================
    
    async def get_npc_memories(self, npc_id: UUID) -> List[Dict[str, Any]]:
        """Get all memories for an NPC using repository"""
        try:
            memories = self.npc_repository.get_npc_memories(npc_id)
            return [
                {
                    "id": str(memory.id),
                    "memory_id": memory.memory_id,
                    "content": memory.content,
                    "memory_type": memory.memory_type,
                    "importance": memory.importance,
                    "emotion": memory.emotion,
                    "location": memory.location,
                    "participants": memory.participants or [],
                    "tags": memory.tags or [],
                    "recalled_count": memory.recalled_count,
                    "created_at": memory.created_at.isoformat() if memory.created_at else None,
                    "last_recalled": memory.last_recalled.isoformat() if memory.last_recalled else None
                }
                for memory in memories
            ]
            
        except Exception as e:
            logger.error(f"Error getting memories for NPC {npc_id}: {str(e)}")
            raise

    async def add_memory_to_npc(self, npc_id: UUID, memory: Dict[str, Any]) -> bool:
        """Add memory to NPC using repository"""
        try:
            # Validate required fields
            if "content" not in memory:
                raise NpcValidationError("Memory content is required")
            
            # Use repository to add memory
            memory_entity = self.npc_repository.add_memory(npc_id, memory)
            
            # Publish memory created event
            self.event_publisher.publish_npc_memory_created(
                npc_id=npc_id,
                memory_id=memory_entity.memory_id,
                content=memory_entity.content,
                memory_type=memory_entity.memory_type,
                importance=memory_entity.importance,
                emotion=memory_entity.emotion,
                location=memory_entity.location,
                participants=memory_entity.participants or []
            )
            
            logger.info(f"Added memory {memory_entity.memory_id} to NPC {npc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding memory to NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="memory_creation_failed",
                error_message=str(e),
                operation="add_memory_to_npc"
            )
            raise

    async def forget_memory(self, npc_id: UUID, memory_id: str) -> bool:
        """Remove memory from NPC using repository"""
        try:
            result = self.npc_repository.remove_memory(npc_id, memory_id)
            
            if result:
                # Publish memory forgotten event
                self.event_publisher.publish_npc_memory_forgotten(
                    npc_id=npc_id,
                    memory_id=memory_id,
                    reason="manual_removal"
                )
                logger.info(f"Removed memory {memory_id} from NPC {npc_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error removing memory from NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="memory_removal_failed",
                error_message=str(e),
                operation="forget_memory"
            )
            raise

    async def get_memory_summary(self, npc_id: UUID) -> Dict[str, Any]:
        """Get memory summary statistics using repository"""
        try:
            return self.memory_repository.get_memory_summary_stats(npc_id)
        except Exception as e:
            logger.error(f"Error getting memory summary for NPC {npc_id}: {str(e)}")
            raise

    # =========================================================================
    # Faction Management
    # =========================================================================
    
    async def add_faction_to_npc(self, npc_id: UUID, faction_id: UUID, role: str = "member") -> bool:
        """Add faction affiliation to NPC using repository"""
        try:
            affiliation = self.npc_repository.add_faction_affiliation(npc_id, faction_id, role)
            
            # Publish faction joined event
            self.event_publisher.publish_npc_faction_joined(
                npc_id=npc_id,
                faction_id=faction_id,
                role=role,
                loyalty=affiliation.loyalty
            )
            
            logger.info(f"Added faction {faction_id} to NPC {npc_id} with role {role}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding faction to NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="faction_join_failed",
                error_message=str(e),
                operation="add_faction_to_npc"
            )
            raise

    async def remove_faction_from_npc(self, npc_id: UUID, faction_id: UUID) -> bool:
        """Remove faction affiliation from NPC using repository"""
        try:
            # Get affiliation data before removal for event
            affiliations = self.npc_repository.get_npc_factions(npc_id)
            target_affiliation = None
            for aff in affiliations:
                if aff.faction_id == faction_id:
                    target_affiliation = aff
                    break
            
            result = self.npc_repository.remove_faction_affiliation(npc_id, faction_id)
            
            if result and target_affiliation:
                # Publish faction left event
                self.event_publisher.publish_npc_faction_left(
                    npc_id=npc_id,
                    faction_id=faction_id,
                    role=target_affiliation.role,
                    final_loyalty=target_affiliation.loyalty,
                    reason="manual_removal"
                )
                logger.info(f"Removed faction {faction_id} from NPC {npc_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error removing faction from NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="faction_leave_failed",
                error_message=str(e),
                operation="remove_faction_from_npc"
            )
            raise

    async def get_npc_factions(self, npc_id: UUID) -> List[Dict[str, Any]]:
        """Get all faction affiliations for an NPC using repository"""
        try:
            affiliations = self.npc_repository.get_npc_factions(npc_id)
            return [
                {
                    "id": str(affiliation.id),
                    "faction_id": str(affiliation.faction_id),
                    "role": affiliation.role,
                    "loyalty": affiliation.loyalty,
                    "status": affiliation.status,
                    "rank": affiliation.rank,
                    "joined_date": affiliation.joined_date.isoformat() if affiliation.joined_date else None,
                    "contributions": affiliation.contributions or []
                }
                for affiliation in affiliations
            ]
            
        except Exception as e:
            logger.error(f"Error getting factions for NPC {npc_id}: {str(e)}")
            raise

    # =========================================================================
    # Rumor Management
    # =========================================================================
    
    async def add_rumor_to_npc(self, npc_id: UUID, rumor: Dict[str, Any]) -> bool:
        """Add rumor to NPC using repository"""
        try:
            # Validate required fields
            if "content" not in rumor:
                raise NpcValidationError("Rumor content is required")
            
            # Use repository to add rumor
            rumor_entity = self.npc_repository.add_rumor(npc_id, rumor)
            
            # Publish rumor learned event
            self.event_publisher.publish_npc_rumor_learned(
                npc_id=npc_id,
                rumor_id=rumor_entity.rumor_id,
                content=rumor_entity.content,
                credibility=rumor_entity.credibility,
                source=rumor_entity.source
            )
            
            logger.info(f"Added rumor {rumor_entity.rumor_id} to NPC {npc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding rumor to NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="rumor_learn_failed",
                error_message=str(e),
                operation="add_rumor_to_npc"
            )
            raise

    async def forget_rumor(self, npc_id: UUID, rumor_id: str) -> bool:
        """Remove rumor from NPC using repository"""
        try:
            result = self.npc_repository.remove_rumor(npc_id, rumor_id)
            
            if result:
                # Publish rumor forgotten event
                self.event_publisher.publish_npc_rumor_forgotten(
                    npc_id=npc_id,
                    rumor_id=rumor_id,
                    reason="manual_removal"
                )
                logger.info(f"Removed rumor {rumor_id} from NPC {npc_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error removing rumor from NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="rumor_forget_failed",
                error_message=str(e),
                operation="forget_rumor"
            )
            raise

    async def get_npc_rumors(self, npc_id: UUID) -> List[Dict[str, Any]]:
        """Get all rumors for an NPC using repository"""
        try:
            rumors = self.npc_repository.get_npc_rumors(npc_id)
            return [
                {
                    "id": str(rumor.id),
                    "rumor_id": rumor.rumor_id,
                    "content": rumor.content,
                    "source": rumor.source,
                    "credibility": rumor.credibility,
                    "spread_chance": rumor.spread_chance,
                    "times_shared": rumor.times_shared,
                    "learned_date": rumor.learned_date.isoformat() if rumor.learned_date else None,
                    "last_shared": rumor.last_shared.isoformat() if rumor.last_shared else None
                }
                for rumor in rumors
            ]
            
        except Exception as e:
            logger.error(f"Error getting rumors for NPC {npc_id}: {str(e)}")
            raise

    # =========================================================================
    # Motif Management
    # =========================================================================
    
    async def apply_motif(self, npc_id: UUID, motif: Dict[str, Any]) -> bool:
        """Apply motif to NPC using repository"""
        try:
            # Validate required fields
            if "motif_type" not in motif:
                raise NpcValidationError("Motif type is required")
            
            # Use repository to add motif
            motif_entity = self.npc_repository.add_motif(npc_id, motif)
            
            # Publish motif applied event
            self.event_publisher.publish_npc_motif_applied(
                npc_id=npc_id,
                motif_id=motif_entity.motif_id,
                motif_type=motif_entity.motif_type,
                strength=motif_entity.strength,
                description=motif_entity.description
            )
            
            logger.info(f"Applied motif {motif_entity.motif_id} to NPC {npc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying motif to NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="motif_apply_failed",
                error_message=str(e),
                operation="apply_motif"
            )
            raise

    async def remove_motif(self, npc_id: UUID, motif_id: str) -> bool:
        """Remove motif from NPC using repository"""
        try:
            # Get motif data before removal for event
            motifs = self.npc_repository.get_npc_motifs(npc_id)
            target_motif = None
            for motif in motifs:
                if motif.motif_id == motif_id:
                    target_motif = motif
                    break
            
            result = self.npc_repository.remove_motif(npc_id, motif_id)
            
            if result and target_motif:
                # Publish motif completed event
                self.event_publisher.publish_npc_motif_completed(
                    npc_id=npc_id,
                    motif_id=motif_id,
                    motif_type=target_motif.motif_type,
                    final_strength=target_motif.strength,
                    outcome="removed"
                )
                logger.info(f"Removed motif {motif_id} from NPC {npc_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error removing motif from NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="motif_remove_failed",
                error_message=str(e),
                operation="remove_motif"
            )
            raise

    async def get_npc_motifs(self, npc_id: UUID) -> List[Dict[str, Any]]:
        """Get all motifs for an NPC using repository"""
        try:
            motifs = self.npc_repository.get_npc_motifs(npc_id)
            return [
                {
                    "id": str(motif.id),
                    "motif_id": motif.motif_id,
                    "motif_type": motif.motif_type,
                    "theme": motif.theme,
                    "strength": motif.strength,
                    "lifespan": motif.lifespan,
                    "entropy_tick": motif.entropy_tick,
                    "weight": motif.weight,
                    "description": motif.description,
                    "triggers": motif.triggers or [],
                    "status": motif.status
                }
                for motif in motifs
            ]
            
        except Exception as e:
            logger.error(f"Error getting motifs for NPC {npc_id}: {str(e)}")
            raise

    # =========================================================================
    # Location Management
    # =========================================================================
    
    async def update_npc_location(self, npc_id: UUID, region_id: str, location: str, 
                                 travel_motive: str = "wander") -> Dict[str, Any]:
        """Update NPC location using location repository"""
        try:
            # Get old location for event
            old_npc = self.npc_repository.get_npc(npc_id)
            if not old_npc:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            # Update location using location repository
            success = self.location_repository.update_npc_location(
                npc_id, region_id, location, travel_motive
            )
            
            if success:
                # Publish movement event
                self.event_publisher.publish_npc_moved(
                    npc_id=npc_id,
                    old_region_id=old_npc.region_id,
                    new_region_id=region_id,
                    old_location=old_npc.location,
                    new_location=location,
                    travel_motive=travel_motive
                )
                
                logger.info(f"Updated location for NPC {npc_id} to {region_id}:{location}")
            
            return {
                "success": success,
                "npc_id": str(npc_id),
                "new_region": region_id,
                "new_location": location,
                "travel_motive": travel_motive
            }
            
        except Exception as e:
            logger.error(f"Error updating location for NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="location_update_failed",
                error_message=str(e),
                operation="update_npc_location"
            )
            raise

    async def get_regional_npcs(self, region_id: str, page: int = 1, size: int = 50) -> List[NpcResponse]:
        """Get NPCs in a specific region using repository"""
        try:
            npcs = self.location_repository.get_npcs_in_region(region_id)
            
            # Apply pagination
            start = (page - 1) * size
            end = start + size
            paginated_npcs = npcs[start:end]
            
            return [NpcResponse.from_orm(npc) for npc in paginated_npcs]
            
        except Exception as e:
            logger.error(f"Error getting regional NPCs: {str(e)}")
            raise

    async def handle_population_migration(self, source_region: str, target_region: str,
                                        npc_ids: Optional[List[UUID]] = None,
                                        migration_reason: str = None) -> Dict[str, Any]:
        """Handle NPC population migration between regions using location repository"""
        try:
            # Use location repository for migration
            result = self.location_repository.schedule_npc_migration(
                source_region, target_region, npc_ids, migration_reason
            )
            
            # Publish migration scheduled event
            self.event_publisher.publish_npc_migration_scheduled(
                npc_ids=result.get('affected_npcs', []),
                source_region=source_region,
                target_region=target_region,
                migration_reason=migration_reason
            )
            
            logger.info(f"Scheduled migration from {source_region} to {target_region}: {result['affected_count']} NPCs")
            return result
            
        except Exception as e:
            logger.error(f"Error handling population migration: {str(e)}")
            self.event_publisher.publish_npc_error(
                error_type="migration_failed",
                error_message=str(e),
                operation="handle_population_migration"
            )
            raise

    # =========================================================================
    # Advanced Features
    # =========================================================================
    
    async def schedule_npc_task(self, npc_id: UUID, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a task for an NPC"""
        try:
            # Validate required fields
            if "task_type" not in task_data:
                raise NpcValidationError("Task type is required")
            
            # Generate task scheduling data
            scheduled_time = datetime.utcnow()
            task_id = f"task_{npc_id}_{int(scheduled_time.timestamp())}"
            
            # Publish task scheduled event
            self.event_publisher.publish_npc_task_scheduled(
                npc_id=npc_id,
                task_id=task_id,
                task_type=task_data["task_type"],
                scheduled_time=scheduled_time,
                estimated_duration=task_data.get("estimated_duration"),
                task_data=task_data
            )
            
            logger.info(f"Scheduled task {task_id} for NPC {npc_id}")
            
            return {
                "task_id": task_id,
                "npc_id": str(npc_id),
                "task_type": task_data["task_type"],
                "scheduled_time": scheduled_time.isoformat(),
                "status": "scheduled"
            }
            
        except Exception as e:
            logger.error(f"Error scheduling task for NPC {npc_id}: {str(e)}")
            self.event_publisher.publish_npc_error(
                npc_id=npc_id,
                error_type="task_schedule_failed",
                error_message=str(e),
                operation="schedule_npc_task"
            )
            raise

    async def get_npc_loyalty(self, npc_id: UUID, character_id: Optional[str] = None) -> Dict[str, Any]:
        """Get NPC loyalty information"""
        try:
            npc = self.npc_repository.get_npc(npc_id)
            if not npc:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            return {
                "npc_id": str(npc_id),
                "character_id": character_id,
                "loyalty_score": npc.loyalty_score,
                "goodwill": npc.goodwill,
                "loyalty_tags": npc.loyalty_tags or [],
                "last_interaction": npc.loyalty_last_tick.isoformat() if npc.loyalty_last_tick else None,
                "status": "active" if npc.is_active else "inactive"
            }
            
        except Exception as e:
            logger.error(f"Error getting loyalty for NPC {npc_id}: {str(e)}")
            raise

    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    async def _get_by_name(self, name: str) -> Optional[NpcEntity]:
        """Get NPC entity by name"""
        return self.db.query(NpcEntity).filter(
            NpcEntity.name == name,
            NpcEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[NpcEntity]:
        """Get NPC entity by ID"""
        return self.npc_repository.get_npc(entity_id)

    async def get_npc_statistics(self) -> Dict[str, Any]:
        """Get comprehensive NPC system statistics using repository"""
        try:
            return self.npc_repository.get_npc_statistics()
        except Exception as e:
            logger.error(f"Error getting NPC statistics: {str(e)}")
            raise


# ============================================================================
# Service Factory Functions
# ============================================================================

def get_npc_service() -> NPCService:
    """Factory function to create NPCService instance for FastAPI dependency injection"""
    return NPCService()


def get_npc_service_with_session(db_session: Session) -> NPCService:
    """Factory function to create NPCService instance with explicit session"""
    return NPCService(db_session)


_singleton_service = None

def get_singleton_npc_service() -> NPCService:
    """Get singleton NPCService instance"""
    global _singleton_service
    if _singleton_service is None:
        _singleton_service = NPCService()
    return _singleton_service 