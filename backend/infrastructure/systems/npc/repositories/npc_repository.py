"""
NPC Repository

Main repository for NPC database operations.
Handles CRUD operations, memory management, faction relationships, rumors, and motifs.
"""

from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_, or_
from sqlalchemy.exc import IntegrityError
import logging

# Use local infrastructure imports
from backend.infrastructure.systems.npc.models.models import (
    NpcEntity, NpcMemory, NpcFactionAffiliation, NpcRumor, 
    NpcLocationHistory, NpcMotif, CreateNpcRequest, 
    UpdateNpcRequest, NpcResponse
)
from backend.infrastructure.shared.exceptions import (
    NpcNotFoundError,
    NpcValidationError,
    NpcConflictError
)

logger = logging.getLogger(__name__)


class NPCRepository:
    """Repository for NPC database operations"""
    
    def __init__(self, db_session: Session):
        """
        Initialize repository with database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    # =========================================================================
    # Core CRUD Operations
    # =========================================================================
    
    def create_npc(self, request: CreateNpcRequest) -> NpcEntity:
        """
        Create a new NPC
        
        Args:
            request: NPC creation request
            
        Returns:
            Created NPC entity
            
        Raises:
            NpcConflictError: If NPC with same name already exists
            NpcValidationError: If validation fails
        """
        try:
            # Check if NPC with same name exists
            existing = self.db.query(NpcEntity).filter(
                NpcEntity.name == request.name,
                NpcEntity.is_active == True
            ).first()
            
            if existing:
                raise NpcConflictError(f"NPC with name '{request.name}' already exists")
            
            # Create new NPC entity
            npc = NpcEntity(
                name=request.name,
                description=request.description,
                race=request.race or "Human",
                properties=request.properties or {}
            )
            
            # If full NPC data provided (from NPCBuilder), use it
            if request.npc_data:
                npc.update_from_npc_builder(request.npc_data)
            
            self.db.add(npc)
            self.db.commit()
            self.db.refresh(npc)
            
            logger.info(f"Created NPC: {npc.name} (ID: {npc.id})")
            return npc
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error creating NPC: {str(e)}")
            raise NpcConflictError(f"Failed to create NPC due to data conflict")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating NPC: {str(e)}")
            raise
    
    def get_npc(self, npc_id: UUID, include_relationships: bool = False) -> Optional[NpcEntity]:
        """
        Get NPC by ID
        
        Args:
            npc_id: NPC UUID
            include_relationships: Whether to load related data
            
        Returns:
            NPC entity or None if not found
        """
        try:
            query = self.db.query(NpcEntity).filter(
                NpcEntity.id == npc_id,
                NpcEntity.is_active == True
            )
            
            if include_relationships:
                query = query.options(
                    joinedload(NpcEntity.memories),
                    joinedload(NpcEntity.faction_relationships),
                    joinedload(NpcEntity.rumors),
                    joinedload(NpcEntity.location_history),
                    joinedload(NpcEntity.motifs)
                )
            
            return query.first()
            
        except Exception as e:
            logger.error(f"Error getting NPC {npc_id}: {str(e)}")
            raise
    
    def update_npc(self, npc_id: UUID, request: UpdateNpcRequest) -> NpcEntity:
        """
        Update NPC by ID
        
        Args:
            npc_id: NPC UUID
            request: Update request
            
        Returns:
            Updated NPC entity
            
        Raises:
            NpcNotFoundError: If NPC not found
        """
        try:
            npc = self.get_npc(npc_id)
            if not npc:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            # Update fields if provided
            if request.name is not None:
                npc.name = request.name
            if request.description is not None:
                npc.description = request.description
            if request.status is not None:
                npc.status = request.status
            if request.properties is not None:
                npc.properties = request.properties
            
            self.db.commit()
            self.db.refresh(npc)
            
            logger.info(f"Updated NPC: {npc.name} (ID: {npc.id})")
            return npc
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating NPC {npc_id}: {str(e)}")
            raise
    
    def delete_npc(self, npc_id: UUID, soft_delete: bool = True) -> bool:
        """
        Delete NPC (soft delete by default)
        
        Args:
            npc_id: NPC UUID
            soft_delete: Whether to soft delete (set is_active=False) or hard delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            NpcNotFoundError: If NPC not found
        """
        try:
            npc = self.get_npc(npc_id)
            if not npc:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            if soft_delete:
                npc.is_active = False
                self.db.commit()
                logger.info(f"Soft deleted NPC: {npc.name} (ID: {npc.id})")
            else:
                self.db.delete(npc)
                self.db.commit()
                logger.info(f"Hard deleted NPC: {npc.name} (ID: {npc.id})")
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting NPC {npc_id}: {str(e)}")
            raise
    
    def list_npcs(
        self, 
        page: int = 1, 
        size: int = 50, 
        status: Optional[str] = None,
        search: Optional[str] = None,
        region_id: Optional[str] = None
    ) -> Tuple[List[NpcEntity], int]:
        """
        List NPCs with pagination and filtering
        
        Args:
            page: Page number (1-based)
            size: Page size
            status: Filter by status
            search: Search term for name/description
            region_id: Filter by region
            
        Returns:
            Tuple of (NPCs list, total count)
        """
        try:
            query = self.db.query(NpcEntity).filter(NpcEntity.is_active == True)
            
            # Apply filters
            if status:
                query = query.filter(NpcEntity.status == status)
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        NpcEntity.name.ilike(search_term),
                        NpcEntity.description.ilike(search_term)
                    )
                )
            
            if region_id:
                query = query.filter(NpcEntity.region_id == region_id)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            npcs = query.order_by(NpcEntity.name).offset(offset).limit(size).all()
            
            return npcs, total
            
        except Exception as e:
            logger.error(f"Error listing NPCs: {str(e)}")
            raise
    
    # =========================================================================
    # Memory Management
    # =========================================================================
    
    def get_npc_memories(self, npc_id: UUID) -> List[NpcMemory]:
        """Get all memories for an NPC"""
        try:
            return self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id
            ).order_by(desc(NpcMemory.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting memories for NPC {npc_id}: {str(e)}")
            raise
    
    def add_memory(self, npc_id: UUID, memory_data: Dict[str, Any]) -> NpcMemory:
        """Add a memory to an NPC"""
        try:
            # Verify NPC exists
            npc = self.get_npc(npc_id)
            if not npc:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            memory = NpcMemory(
                npc_id=npc_id,
                memory_id=memory_data.get('memory_id', f"mem_{datetime.utcnow().timestamp()}"),
                content=memory_data['content'],
                memory_type=memory_data.get('memory_type', 'experience'),
                importance=memory_data.get('importance', 1.0),
                emotion=memory_data.get('emotion'),
                location=memory_data.get('location'),
                participants=memory_data.get('participants', []),
                tags=memory_data.get('tags', [])
            )
            
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            
            logger.info(f"Added memory to NPC {npc_id}: {memory.memory_id}")
            return memory
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding memory to NPC {npc_id}: {str(e)}")
            raise
    
    def remove_memory(self, npc_id: UUID, memory_id: str) -> bool:
        """Remove a memory from an NPC"""
        try:
            memory = self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.memory_id == memory_id
            ).first()
            
            if not memory:
                return False
            
            self.db.delete(memory)
            self.db.commit()
            
            logger.info(f"Removed memory {memory_id} from NPC {npc_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing memory {memory_id} from NPC {npc_id}: {str(e)}")
            raise
    
    # =========================================================================
    # Faction Management
    # =========================================================================
    
    def get_npc_factions(self, npc_id: UUID) -> List[NpcFactionAffiliation]:
        """Get all faction affiliations for an NPC"""
        try:
            return self.db.query(NpcFactionAffiliation).filter(
                NpcFactionAffiliation.npc_id == npc_id,
                NpcFactionAffiliation.status == 'active'
            ).all()
        except Exception as e:
            logger.error(f"Error getting factions for NPC {npc_id}: {str(e)}")
            raise
    
    def add_faction_affiliation(self, npc_id: UUID, faction_id: UUID, role: str = "member") -> NpcFactionAffiliation:
        """Add faction affiliation to an NPC"""
        try:
            # Verify NPC exists
            npc = self.get_npc(npc_id)
            if not npc:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            # Check if affiliation already exists
            existing = self.db.query(NpcFactionAffiliation).filter(
                NpcFactionAffiliation.npc_id == npc_id,
                NpcFactionAffiliation.faction_id == faction_id
            ).first()
            
            if existing:
                # Reactivate if inactive
                if existing.status != 'active':
                    existing.status = 'active'
                    existing.role = role
                    self.db.commit()
                    return existing
                else:
                    raise NpcConflictError(f"NPC {npc_id} already affiliated with faction {faction_id}")
            
            affiliation = NpcFactionAffiliation(
                npc_id=npc_id,
                faction_id=faction_id,
                role=role,
                joined_date=datetime.utcnow()
            )
            
            self.db.add(affiliation)
            self.db.commit()
            self.db.refresh(affiliation)
            
            logger.info(f"Added faction {faction_id} affiliation to NPC {npc_id}")
            return affiliation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding faction affiliation to NPC {npc_id}: {str(e)}")
            raise
    
    def remove_faction_affiliation(self, npc_id: UUID, faction_id: UUID) -> bool:
        """Remove faction affiliation from an NPC"""
        try:
            affiliation = self.db.query(NpcFactionAffiliation).filter(
                NpcFactionAffiliation.npc_id == npc_id,
                NpcFactionAffiliation.faction_id == faction_id
            ).first()
            
            if not affiliation:
                return False
            
            # Soft delete by setting status to inactive
            affiliation.status = 'inactive'
            self.db.commit()
            
            logger.info(f"Removed faction {faction_id} affiliation from NPC {npc_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing faction affiliation from NPC {npc_id}: {str(e)}")
            raise
    
    # =========================================================================
    # Rumor Management
    # =========================================================================
    
    def get_npc_rumors(self, npc_id: UUID) -> List[NpcRumor]:
        """Get all rumors known by an NPC"""
        try:
            return self.db.query(NpcRumor).filter(
                NpcRumor.npc_id == npc_id
            ).order_by(desc(NpcRumor.learned_date)).all()
        except Exception as e:
            logger.error(f"Error getting rumors for NPC {npc_id}: {str(e)}")
            raise
    
    def add_rumor(self, npc_id: UUID, rumor_data: Dict[str, Any]) -> NpcRumor:
        """Add a rumor to an NPC's knowledge"""
        try:
            # Verify NPC exists
            npc = self.get_npc(npc_id)
            if not npc:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            rumor = NpcRumor(
                npc_id=npc_id,
                rumor_id=rumor_data.get('rumor_id', f"rumor_{datetime.utcnow().timestamp()}"),
                content=rumor_data['content'],
                source=rumor_data.get('source'),
                credibility=rumor_data.get('credibility', 5.0),
                spread_chance=rumor_data.get('spread_chance', 0.5),
                learned_date=datetime.utcnow()
            )
            
            self.db.add(rumor)
            self.db.commit()
            self.db.refresh(rumor)
            
            logger.info(f"Added rumor to NPC {npc_id}: {rumor.rumor_id}")
            return rumor
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding rumor to NPC {npc_id}: {str(e)}")
            raise
    
    def remove_rumor(self, npc_id: UUID, rumor_id: str) -> bool:
        """Remove a rumor from an NPC's knowledge"""
        try:
            rumor = self.db.query(NpcRumor).filter(
                NpcRumor.npc_id == npc_id,
                NpcRumor.rumor_id == rumor_id
            ).first()
            
            if not rumor:
                return False
            
            self.db.delete(rumor)
            self.db.commit()
            
            logger.info(f"Removed rumor {rumor_id} from NPC {npc_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing rumor {rumor_id} from NPC {npc_id}: {str(e)}")
            raise
    
    # =========================================================================
    # Motif Management
    # =========================================================================
    
    def get_npc_motifs(self, npc_id: UUID) -> List[NpcMotif]:
        """Get all motifs for an NPC"""
        try:
            return self.db.query(NpcMotif).filter(
                NpcMotif.npc_id == npc_id,
                NpcMotif.status == 'active'
            ).all()
        except Exception as e:
            logger.error(f"Error getting motifs for NPC {npc_id}: {str(e)}")
            raise
    
    def add_motif(self, npc_id: UUID, motif_data: Dict[str, Any]) -> NpcMotif:
        """Add a motif to an NPC"""
        try:
            # Verify NPC exists
            npc = self.get_npc(npc_id)
            if not npc:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            motif = NpcMotif(
                npc_id=npc_id,
                motif_id=motif_data.get('motif_id', f"motif_{datetime.utcnow().timestamp()}"),
                motif_type=motif_data['motif_type'],
                theme=motif_data.get('theme'),
                strength=motif_data.get('strength', 1.0),
                lifespan=motif_data.get('lifespan', 3),
                description=motif_data.get('description'),
                triggers=motif_data.get('triggers', [])
            )
            
            self.db.add(motif)
            self.db.commit()
            self.db.refresh(motif)
            
            logger.info(f"Added motif to NPC {npc_id}: {motif.motif_type}")
            return motif
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding motif to NPC {npc_id}: {str(e)}")
            raise
    
    def remove_motif(self, npc_id: UUID, motif_id: str) -> bool:
        """Remove a motif from an NPC"""
        try:
            motif = self.db.query(NpcMotif).filter(
                NpcMotif.npc_id == npc_id,
                NpcMotif.motif_id == motif_id
            ).first()
            
            if not motif:
                return False
            
            motif.status = 'abandoned'
            self.db.commit()
            
            logger.info(f"Removed motif {motif_id} from NPC {npc_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing motif {motif_id} from NPC {npc_id}: {str(e)}")
            raise
    
    # =========================================================================
    # Statistics and Helpers
    # =========================================================================
    
    def get_npc_statistics(self) -> Dict[str, Any]:
        """Get NPC system statistics"""
        try:
            total_npcs = self.db.query(func.count(NpcEntity.id)).filter(
                NpcEntity.is_active == True
            ).scalar()
            
            active_npcs = self.db.query(func.count(NpcEntity.id)).filter(
                NpcEntity.is_active == True,
                NpcEntity.status == 'active'
            ).scalar()
            
            total_memories = self.db.query(func.count(NpcMemory.id)).scalar()
            total_factions = self.db.query(func.count(NpcFactionAffiliation.id)).filter(
                NpcFactionAffiliation.status == 'active'
            ).scalar()
            total_rumors = self.db.query(func.count(NpcRumor.id)).scalar()
            
            return {
                "total_npcs": total_npcs,
                "active_npcs": active_npcs,
                "total_memories": total_memories,
                "total_faction_affiliations": total_factions,
                "total_rumors": total_rumors,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting NPC statistics: {str(e)}")
            raise 