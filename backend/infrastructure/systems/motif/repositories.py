"""
Motif system - Repository layer.
Data access layer for motif operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.exc import SQLAlchemyError

from backend.infrastructure.systems.motif.models import (
    Motif, MotifFilter, MotifScope, MotifLifecycle, MotifCategory
)
from backend.infrastructure.database.base import Base

logger = logging.getLogger(__name__)


class MotifRepository:
    """Repository for motif data operations."""

    def __init__(self, session: Optional[AsyncSession] = None):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self._sample_motifs = []  # Fallback storage for testing

    async def create_motif(self, motif: Motif) -> Motif:
        """
        Create a new motif in the database.
        
        Args:
            motif: Motif instance to create
            
        Returns:
            Created motif with populated ID
            
        Raises:
            ValueError: If motif data is invalid
            RuntimeError: If database operation fails
        """
        try:
            if not self.session:
                # Fallback for testing - use in-memory storage
                motif.id = f"motif_{len(self._sample_motifs) + 1}"
                motif.created_at = datetime.utcnow()
                motif.updated_at = datetime.utcnow()
                self._sample_motifs.append(motif)
                logger.info(f"Created motif (in-memory): {motif.id}")
                return motif
            
            # Set timestamps
            motif.created_at = datetime.utcnow()
            motif.updated_at = datetime.utcnow()
            
            # Add to session and flush to get ID
            self.session.add(motif)
            await self.session.flush()
            await self.session.commit()
            
            logger.info(f"Created motif in database: {motif.id}")
            return motif
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating motif: {e}")
            if self.session:
                await self.session.rollback()
            raise RuntimeError(f"Failed to create motif: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating motif: {e}")
            raise ValueError(f"Invalid motif data: {str(e)}")

    async def get_motif(self, motif_id: str) -> Optional[Motif]:
        """
        Get a motif by ID.
        
        Args:
            motif_id: Unique motif identifier
            
        Returns:
            Motif instance or None if not found
        """
        try:
            if not self.session:
                # Fallback for testing
                for motif in self._sample_motifs:
                    if motif.id == motif_id:
                        return motif
                return None
            
            # Database query
            stmt = select(Motif).where(Motif.id == motif_id)
            result = await self.session.execute(stmt)
            motif = result.scalar_one_or_none()
            
            if motif:
                logger.debug(f"Retrieved motif: {motif_id}")
            else:
                logger.debug(f"Motif not found: {motif_id}")
                
            return motif
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting motif {motif_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting motif {motif_id}: {e}")
            return None

    async def update_motif(self, motif_id: str, update_data: Dict[str, Any]) -> Optional[Motif]:
        """
        Update a motif with new data.
        
        Args:
            motif_id: Unique motif identifier
            update_data: Dictionary of fields to update
            
        Returns:
            Updated motif or None if not found
        """
        try:
            if not self.session:
                # Fallback for testing
                for motif in self._sample_motifs:
                    if motif.id == motif_id:
                        for key, value in update_data.items():
                            if hasattr(motif, key):
                                setattr(motif, key, value)
                        motif.updated_at = datetime.utcnow()
                        logger.info(f"Updated motif (in-memory): {motif_id}")
                        return motif
                return None
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            # Update in database
            stmt = (
                update(Motif)
                .where(Motif.id == motif_id)
                .values(**update_data)
                .returning(Motif)
            )
            
            result = await self.session.execute(stmt)
            motif = result.scalar_one_or_none()
            
            if motif:
                await self.session.commit()
                logger.info(f"Updated motif in database: {motif_id}")
            else:
                logger.warning(f"Motif not found for update: {motif_id}")
                
            return motif
            
        except SQLAlchemyError as e:
            logger.error(f"Database error updating motif {motif_id}: {e}")
            if self.session:
                await self.session.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error updating motif {motif_id}: {e}")
            return None

    async def delete_motif(self, motif_id: str) -> bool:
        """
        Delete a motif from the database.
        
        Args:
            motif_id: Unique motif identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            if not self.session:
                # Fallback for testing
                for i, motif in enumerate(self._sample_motifs):
                    if motif.id == motif_id:
                        del self._sample_motifs[i]
                        logger.info(f"Deleted motif (in-memory): {motif_id}")
                        return True
                return False
            
            # Delete from database
            stmt = delete(Motif).where(Motif.id == motif_id)
            result = await self.session.execute(stmt)
            
            if result.rowcount > 0:
                await self.session.commit()
                logger.info(f"Deleted motif from database: {motif_id}")
                return True
            else:
                logger.warning(f"Motif not found for deletion: {motif_id}")
                return False
                
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting motif {motif_id}: {e}")
            if self.session:
                await self.session.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting motif {motif_id}: {e}")
            return False

    def get_all_motifs(self) -> List[Motif]:
        """
        Get all motifs (synchronous for backward compatibility).
        
        Returns:
            List of all motifs
        """
        if not self.session:
            return self._sample_motifs.copy()
        
        # Note: This should be converted to async in real implementation
        logger.warning("get_all_motifs is synchronous - should be converted to async")
        return []

    async def list_motifs(
        self, 
        filter_params: Optional[MotifFilter] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Motif]:
        """
        List motifs with filtering, pagination, and sorting.
        
        Args:
            filter_params: Filter criteria
            limit: Maximum results to return
            offset: Number of results to skip
            
        Returns:
            List of motifs matching criteria
        """
        try:
            if not self.session:
                # Fallback for testing
                motifs = self._apply_filter_fallback(self._sample_motifs, filter_params)
                return motifs[offset:offset + limit]
            
            # Build query
            stmt = select(Motif)
            
            # Apply filters
            if filter_params:
                conditions = self._build_filter_conditions(filter_params)
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            # Apply pagination and ordering
            stmt = stmt.order_by(Motif.created_at.desc()).offset(offset).limit(limit)
            
            # Execute query
            result = await self.session.execute(stmt)
            motifs = result.scalars().all()
            
            logger.debug(f"Retrieved {len(motifs)} motifs with filters")
            return list(motifs)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing motifs: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing motifs: {e}")
            return []

    async def count_motifs(self, filter_params: Optional[MotifFilter] = None) -> int:
        """
        Count motifs matching filter criteria.
        
        Args:
            filter_params: Filter criteria
            
        Returns:
            Count of matching motifs
        """
        try:
            if not self.session:
                # Fallback for testing
                motifs = self._apply_filter_fallback(self._sample_motifs, filter_params)
                return len(motifs)
            
            # Build count query
            stmt = select(func.count(Motif.id))
            
            # Apply filters
            if filter_params:
                conditions = self._build_filter_conditions(filter_params)
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            # Execute query
            result = await self.session.execute(stmt)
            count = result.scalar()
            
            logger.debug(f"Counted {count} motifs with filters")
            return count or 0
            
        except SQLAlchemyError as e:
            logger.error(f"Database error counting motifs: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error counting motifs: {e}")
            return 0

    def filter_motifs(self, filter_params: MotifFilter) -> List[Motif]:
        """
        Filter motifs (synchronous for backward compatibility).
        
        Args:
            filter_params: Filter criteria
            
        Returns:
            List of filtered motifs
        """
        if not self.session:
            return self._apply_filter_fallback(self._sample_motifs, filter_params)
        
        # Note: This should be converted to async in real implementation
        logger.warning("filter_motifs is synchronous - should be converted to async")
        return []

    def get_global_motifs(self) -> List[Motif]:
        """
        Get all global scope motifs (synchronous for backward compatibility).
        
        Returns:
            List of global motifs
        """
        if not self.session:
            return [m for m in self._sample_motifs if m.scope == MotifScope.GLOBAL]
        
        # Note: This should be converted to async in real implementation  
        logger.warning("get_global_motifs is synchronous - should be converted to async")
        return []

    def get_regional_motifs(self, region_id: str) -> List[Motif]:
        """
        Get all motifs for a specific region (synchronous for backward compatibility).
        
        Args:
            region_id: Region identifier
            
        Returns:
            List of regional motifs
        """
        if not self.session:
            return [
                m for m in self._sample_motifs 
                if m.scope == MotifScope.REGIONAL and getattr(m, 'region_id', None) == region_id
            ]
        
        # Note: This should be converted to async in real implementation
        logger.warning("get_regional_motifs is synchronous - should be converted to async")
        return []

    async def get_motifs_at_position(
        self, 
        x: float, 
        y: float, 
        radius: float = 50.0
    ) -> List[Motif]:
        """
        Get motifs affecting a specific position.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            radius: Search radius
            
        Returns:
            List of motifs within radius
        """
        try:
            if not self.session:
                # Fallback for testing - simplified distance check
                nearby_motifs = []
                for motif in self._sample_motifs:
                    # Check if motif has position data
                    motif_x = getattr(motif, 'x', None)
                    motif_y = getattr(motif, 'y', None)
                    
                    if motif_x is not None and motif_y is not None:
                        # Simple distance calculation
                        distance = ((x - motif_x) ** 2 + (y - motif_y) ** 2) ** 0.5
                        if distance <= radius:
                            nearby_motifs.append(motif)
                    elif motif.scope == MotifScope.GLOBAL:
                        # Global motifs affect all positions
                        nearby_motifs.append(motif)
                
                return nearby_motifs
            
            # Database spatial query would go here
            # For now, return empty list
            logger.info(f"Spatial query at ({x}, {y}) with radius {radius}")
            return []
            
        except Exception as e:
            logger.error(f"Error getting motifs at position ({x}, {y}): {e}")
            return []

    def _build_filter_conditions(self, filter_params: MotifFilter) -> List:
        """
        Build SQLAlchemy filter conditions from filter parameters.
        
        Args:
            filter_params: Filter criteria
            
        Returns:
            List of SQLAlchemy condition expressions
        """
        conditions = []
        
        if filter_params.category:
            conditions.append(Motif.category == filter_params.category)
        
        if filter_params.scope:
            conditions.append(Motif.scope == filter_params.scope)
        
        if filter_params.lifecycle:
            conditions.append(Motif.lifecycle == filter_params.lifecycle)
        
        if filter_params.min_intensity:
            conditions.append(Motif.intensity >= filter_params.min_intensity)
        
        if filter_params.max_intensity:
            conditions.append(Motif.intensity <= filter_params.max_intensity)
        
        if filter_params.region_id:
            conditions.append(Motif.region_id == filter_params.region_id)
        
        if filter_params.active_only:
            # Filter for active lifecycles
            active_states = [MotifLifecycle.EMERGING, MotifLifecycle.STABLE, MotifLifecycle.WANING]
            conditions.append(Motif.lifecycle.in_(active_states))
        
        return conditions

    def _apply_filter_fallback(
        self, 
        motifs: List[Motif], 
        filter_params: Optional[MotifFilter]
    ) -> List[Motif]:
        """
        Apply filters to motif list (fallback for testing).
        
        Args:
            motifs: List of motifs to filter
            filter_params: Filter criteria
            
        Returns:
            Filtered motif list
        """
        if not filter_params:
            return motifs
        
        filtered = motifs
        
        if filter_params.category:
            filtered = [m for m in filtered if m.category == filter_params.category]
        
        if filter_params.scope:
            filtered = [m for m in filtered if m.scope == filter_params.scope]
        
        if filter_params.lifecycle:
            filtered = [m for m in filtered if m.lifecycle == filter_params.lifecycle]
        
        if filter_params.min_intensity:
            filtered = [m for m in filtered if m.intensity >= filter_params.min_intensity]
        
        if filter_params.max_intensity:
            filtered = [m for m in filtered if m.intensity <= filter_params.max_intensity]
        
        if filter_params.region_id:
            filtered = [
                m for m in filtered 
                if getattr(m, 'region_id', None) == filter_params.region_id
            ]
        
        if filter_params.active_only:
            active_states = {MotifLifecycle.EMERGING, MotifLifecycle.STABLE, MotifLifecycle.WANING}
            filtered = [m for m in filtered if m.lifecycle in active_states]
        
        return filtered 