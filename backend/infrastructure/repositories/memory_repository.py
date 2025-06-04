"""
Memory Repository Implementation
-------------------------------

Real database persistence for the memory system following repository patterns.
Implements both relational storage for metadata and vector storage for embeddings.
"""

from typing import Dict, List, Optional, Any, Tuple, Protocol
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import json
import logging
from abc import ABC, abstractmethod

from sqlalchemy import Column, String, Text, Float, DateTime, Integer, JSON, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, update, delete, func, and_, or_

from backend.infrastructure.repositories.base_repository import BaseRepository
from backend.systems.memory.memory_categories import MemoryCategory

logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()


class MemoryEntity(Base):
    """SQLAlchemy model for memory storage."""
    
    __tablename__ = "memories"
    
    # Primary fields
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(String(255), nullable=False, index=True)  # Entity that owns this memory
    content = Column(Text, nullable=False)
    memory_type = Column(String(50), default="regular")  # regular, core, summary
    
    # Importance and categorization
    importance = Column(Float, default=0.5)
    saliency = Column(Float, default=0.5)
    categories = Column(JSON, default=list)  # List of category strings
    
    # Temporal information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    
    # Memory lifecycle
    is_active = Column(Boolean, default=True)
    is_summarized = Column(Boolean, default=False)
    summary_parent_id = Column(PGUUID(as_uuid=True), nullable=True)  # If this is a summary of other memories
    
    # Additional data
    metadata = Column(JSON, default=dict)
    embedding_vector = Column(JSON, nullable=True)  # Store as JSON array for simplicity
    
    # Relationships
    associations = relationship("MemoryAssociation", foreign_keys="MemoryAssociation.memory_a_id", back_populates="memory_a")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_memories_npc_created', 'npc_id', 'created_at'),
        Index('ix_memories_importance', 'importance'),
        Index('ix_memories_active', 'is_active'),
        Index('ix_memories_type_category', 'memory_type', 'categories'),
    )


class MemoryAssociation(Base):
    """SQLAlchemy model for memory associations."""
    
    __tablename__ = "memory_associations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    memory_a_id = Column(PGUUID(as_uuid=True), ForeignKey('memories.id'), nullable=False)
    memory_b_id = Column(PGUUID(as_uuid=True), ForeignKey('memories.id'), nullable=False)
    
    association_type = Column(String(50), nullable=False)  # semantic, temporal, causal, etc.
    strength = Column(Float, default=0.5)  # 0.0 to 1.0
    
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default=dict)
    
    # Relationships
    memory_a = relationship("MemoryEntity", foreign_keys=[memory_a_id])
    memory_b = relationship("MemoryEntity", foreign_keys=[memory_b_id])
    
    __table_args__ = (
        Index('ix_associations_memories', 'memory_a_id', 'memory_b_id'),
        Index('ix_associations_type', 'association_type'),
    )


# Repository Protocols
class MemoryRepositoryProtocol(Protocol):
    """Protocol defining memory repository interface."""
    
    async def create_memory(self, memory_data: Dict[str, Any]) -> MemoryEntity:
        """Create a new memory."""
        ...
    
    async def get_memory_by_id(self, memory_id: UUID) -> Optional[MemoryEntity]:
        """Get memory by ID."""
        ...
    
    async def update_memory(self, memory_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update memory fields."""
        ...
    
    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete memory (soft delete)."""
        ...
    
    async def get_memories_by_entity(self, npc_id: str, limit: int = 100, offset: int = 0) -> List[MemoryEntity]:
        """Get memories for an entity."""
        ...
    
    async def search_memories(self, npc_id: str, query: str, limit: int = 10) -> List[MemoryEntity]:
        """Search memories by content."""
        ...
    
    async def get_memories_by_category(self, npc_id: str, category: MemoryCategory, limit: int = 50) -> List[MemoryEntity]:
        """Get memories by category."""
        ...
    
    async def get_recent_memories(self, npc_id: str, days: int = 7, limit: int = 50) -> List[MemoryEntity]:
        """Get recent memories."""
        ...


class SQLAlchemyMemoryRepository(BaseRepository, MemoryRepositoryProtocol):
    """SQLAlchemy implementation of memory repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.session = session
    
    async def create_memory(self, memory_data: Dict[str, Any]) -> MemoryEntity:
        """Create a new memory in the database."""
        try:
            # Ensure categories is a list
            if 'categories' in memory_data and not isinstance(memory_data['categories'], list):
                if isinstance(memory_data['categories'], str):
                    memory_data['categories'] = [memory_data['categories']]
                else:
                    memory_data['categories'] = []
            
            # Create memory entity
            memory = MemoryEntity(**memory_data)
            
            self.session.add(memory)
            await self.session.commit()
            await self.session.refresh(memory)
            
            logger.info(f"Created memory {memory.id} for entity {memory.npc_id}")
            return memory
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create memory: {e}")
            raise
    
    async def get_memory_by_id(self, memory_id: UUID) -> Optional[MemoryEntity]:
        """Get memory by ID."""
        try:
            result = await self.session.execute(
                select(MemoryEntity).where(
                    and_(MemoryEntity.id == memory_id, MemoryEntity.is_active == True)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            return None
    
    async def update_memory(self, memory_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update memory fields."""
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.utcnow()
            
            result = await self.session.execute(
                update(MemoryEntity)
                .where(MemoryEntity.id == memory_id)
                .values(**updates)
            )
            
            await self.session.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return False
    
    async def delete_memory(self, memory_id: UUID) -> bool:
        """Soft delete memory."""
        return await self.update_memory(memory_id, {'is_active': False})
    
    async def get_memories_by_entity(self, npc_id: str, limit: int = 100, offset: int = 0) -> List[MemoryEntity]:
        """Get memories for an entity with pagination."""
        try:
            result = await self.session.execute(
                select(MemoryEntity)
                .where(and_(MemoryEntity.npc_id == npc_id, MemoryEntity.is_active == True))
                .order_by(MemoryEntity.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get memories for entity {npc_id}: {e}")
            return []
    
    async def search_memories(self, npc_id: str, query: str, limit: int = 10) -> List[MemoryEntity]:
        """Search memories by content using full-text search."""
        try:
            # Simple ILIKE search - in production would use PostgreSQL full-text search
            result = await self.session.execute(
                select(MemoryEntity)
                .where(and_(
                    MemoryEntity.npc_id == npc_id,
                    MemoryEntity.is_active == True,
                    MemoryEntity.content.ilike(f'%{query}%')
                ))
                .order_by(MemoryEntity.importance.desc(), MemoryEntity.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to search memories for {npc_id} with query '{query}': {e}")
            return []
    
    async def get_memories_by_category(self, npc_id: str, category: MemoryCategory, limit: int = 50) -> List[MemoryEntity]:
        """Get memories by category."""
        try:
            # Use JSON search for categories array
            result = await self.session.execute(
                select(MemoryEntity)
                .where(and_(
                    MemoryEntity.npc_id == npc_id,
                    MemoryEntity.is_active == True,
                    MemoryEntity.categories.contains([category.value])
                ))
                .order_by(MemoryEntity.importance.desc(), MemoryEntity.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get memories by category {category.value} for {npc_id}: {e}")
            return []
    
    async def get_recent_memories(self, npc_id: str, days: int = 7, limit: int = 50) -> List[MemoryEntity]:
        """Get recent memories within specified days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await self.session.execute(
                select(MemoryEntity)
                .where(and_(
                    MemoryEntity.npc_id == npc_id,
                    MemoryEntity.is_active == True,
                    MemoryEntity.created_at >= cutoff_date
                ))
                .order_by(MemoryEntity.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get recent memories for {npc_id}: {e}")
            return []
    
    async def get_memories_involving_entity(self, npc_id: str, entity_id: str, limit: int = 50) -> List[MemoryEntity]:
        """Get memories that mention a specific entity."""
        try:
            result = await self.session.execute(
                select(MemoryEntity)
                .where(and_(
                    MemoryEntity.npc_id == npc_id,
                    MemoryEntity.is_active == True,
                    or_(
                        MemoryEntity.content.ilike(f'%{entity_id}%'),
                        MemoryEntity.metadata.contains({"entities": [entity_id]})
                    )
                ))
                .order_by(MemoryEntity.importance.desc(), MemoryEntity.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get memories involving entity {entity_id} for {npc_id}: {e}")
            return []
    
    async def update_memory_access(self, memory_id: UUID) -> bool:
        """Update memory access statistics."""
        try:
            await self.session.execute(
                update(MemoryEntity)
                .where(MemoryEntity.id == memory_id)
                .values(
                    access_count=MemoryEntity.access_count + 1,
                    last_accessed=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            )
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update memory access for {memory_id}: {e}")
            return False
    
    async def get_memory_statistics(self, npc_id: str) -> Dict[str, Any]:
        """Get memory statistics for an entity."""
        try:
            # Total memories
            total_result = await self.session.execute(
                select(func.count(MemoryEntity.id))
                .where(and_(MemoryEntity.npc_id == npc_id, MemoryEntity.is_active == True))
            )
            total_memories = total_result.scalar() or 0
            
            # Memories by type
            type_result = await self.session.execute(
                select(MemoryEntity.memory_type, func.count(MemoryEntity.id))
                .where(and_(MemoryEntity.npc_id == npc_id, MemoryEntity.is_active == True))
                .group_by(MemoryEntity.memory_type)
            )
            memories_by_type = dict(type_result.all())
            
            # Average importance
            importance_result = await self.session.execute(
                select(func.avg(MemoryEntity.importance))
                .where(and_(MemoryEntity.npc_id == npc_id, MemoryEntity.is_active == True))
            )
            avg_importance = importance_result.scalar() or 0.0
            
            return {
                'entity_id': npc_id,
                'total_memories': total_memories,
                'memories_by_type': memories_by_type,
                'average_importance': float(avg_importance),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory statistics for {npc_id}: {e}")
            return {
                'entity_id': npc_id,
                'total_memories': 0,
                'memories_by_type': {},
                'average_importance': 0.0,
                'last_updated': datetime.utcnow().isoformat()
            }


# Association Repository
class MemoryAssociationRepository(BaseRepository):
    """Repository for memory associations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.session = session
    
    async def create_association(self, memory_a_id: UUID, memory_b_id: UUID, 
                               association_type: str, strength: float = 0.5,
                               metadata: Optional[Dict] = None) -> MemoryAssociation:
        """Create a memory association."""
        try:
            association = MemoryAssociation(
                memory_a_id=memory_a_id,
                memory_b_id=memory_b_id,
                association_type=association_type,
                strength=strength,
                metadata=metadata or {}
            )
            
            self.session.add(association)
            await self.session.commit()
            await self.session.refresh(association)
            
            return association
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create association: {e}")
            raise
    
    async def get_associations_for_memory(self, memory_id: UUID, limit: int = 20) -> List[MemoryAssociation]:
        """Get all associations for a memory."""
        try:
            result = await self.session.execute(
                select(MemoryAssociation)
                .where(or_(
                    MemoryAssociation.memory_a_id == memory_id,
                    MemoryAssociation.memory_b_id == memory_id
                ))
                .order_by(MemoryAssociation.strength.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get associations for memory {memory_id}: {e}")
            return []


def create_memory_repository(session: AsyncSession) -> SQLAlchemyMemoryRepository:
    """Factory function for creating memory repository."""
    return SQLAlchemyMemoryRepository(session)


def create_association_repository(session: AsyncSession) -> MemoryAssociationRepository:
    """Factory function for creating association repository."""
    return MemoryAssociationRepository(session) 