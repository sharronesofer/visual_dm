"""
Rumor Repository Implementation

This module provides the repository implementation for the rumor system,
bridging business logic with database infrastructure.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

# Infrastructure imports
from backend.infrastructure.systems.rumor.models.models import RumorEntity, RumorVariantEntity, RumorSpreadEntity

# Business domain imports
from backend.systems.rumor.services.services import RumorData, RumorVariantData, RumorSpreadData


class SQLAlchemyRumorRepository:
    """SQLAlchemy implementation of the rumor repository"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_rumor_by_id(self, rumor_id: UUID) -> Optional[RumorData]:
        """Get rumor by ID with all variants and spread records"""
        entity = self.db_session.query(RumorEntity).filter(
            RumorEntity.id == rumor_id,
            RumorEntity.is_active == True
        ).first()
        
        if not entity:
            return None
        
        return self._entity_to_business_data(entity)

    def create_rumor(self, rumor_data: RumorData) -> RumorData:
        """Create a new rumor with variants and spread records"""
        # Create main rumor entity
        rumor_entity = RumorEntity(
            id=rumor_data.id,
            original_content=rumor_data.original_content,
            originator_id=rumor_data.originator_id,
            categories=rumor_data.categories,
            severity=rumor_data.severity,
            truth_value=rumor_data.truth_value,
            properties=rumor_data.properties,
            created_at=rumor_data.created_at
        )
        
        self.db_session.add(rumor_entity)
        self.db_session.flush()  # Ensure rumor has an ID for foreign keys
        
        # Create variant entities
        for variant in rumor_data.variants:
            variant_entity = RumorVariantEntity(
                id=variant.id,
                rumor_id=rumor_data.id,
                content=variant.content,
                parent_variant_id=variant.parent_variant_id,
                entity_id=variant.entity_id,
                mutation_metadata=variant.mutation_metadata,
                created_at=variant.created_at
            )
            self.db_session.add(variant_entity)
        
        # Create spread entities
        for spread in rumor_data.spread:
            spread_entity = RumorSpreadEntity(
                rumor_id=rumor_data.id,
                entity_id=spread.entity_id,
                variant_id=spread.variant_id,
                heard_from_entity_id=spread.heard_from_entity_id,
                believability=spread.believability,
                heard_at=spread.heard_at
            )
            self.db_session.add(spread_entity)
        
        self.db_session.commit()
        
        # Return updated business data
        return self.get_rumor_by_id(rumor_data.id)

    def update_rumor(self, rumor_data: RumorData) -> RumorData:
        """Update existing rumor with variants and spread records"""
        # Get existing entity
        entity = self.db_session.query(RumorEntity).filter(
            RumorEntity.id == rumor_data.id
        ).first()
        
        if not entity:
            raise ValueError(f"Rumor {rumor_data.id} not found")
        
        # Update main rumor fields
        entity.original_content = rumor_data.original_content
        entity.originator_id = rumor_data.originator_id
        entity.categories = rumor_data.categories
        entity.severity = rumor_data.severity
        entity.truth_value = rumor_data.truth_value
        entity.properties = rumor_data.properties
        entity.updated_at = datetime.utcnow()
        
        # Handle variants - remove old ones and add new ones
        # (In a production system, you might want more sophisticated sync logic)
        self.db_session.query(RumorVariantEntity).filter(
            RumorVariantEntity.rumor_id == rumor_data.id
        ).delete()
        
        for variant in rumor_data.variants:
            variant_entity = RumorVariantEntity(
                id=variant.id,
                rumor_id=rumor_data.id,
                content=variant.content,
                parent_variant_id=variant.parent_variant_id,
                entity_id=variant.entity_id,
                mutation_metadata=variant.mutation_metadata,
                created_at=variant.created_at
            )
            self.db_session.add(variant_entity)
        
        # Handle spread records - similar approach
        self.db_session.query(RumorSpreadEntity).filter(
            RumorSpreadEntity.rumor_id == rumor_data.id
        ).delete()
        
        for spread in rumor_data.spread:
            spread_entity = RumorSpreadEntity(
                rumor_id=rumor_data.id,
                entity_id=spread.entity_id,
                variant_id=spread.variant_id,
                heard_from_entity_id=spread.heard_from_entity_id,
                believability=spread.believability,
                heard_at=spread.heard_at
            )
            self.db_session.add(spread_entity)
        
        self.db_session.commit()
        
        # Return updated business data
        return self.get_rumor_by_id(rumor_data.id)

    def delete_rumor(self, rumor_id: UUID) -> bool:
        """Soft delete rumor by setting is_active to False"""
        entity = self.db_session.query(RumorEntity).filter(
            RumorEntity.id == rumor_id
        ).first()
        
        if not entity:
            return False
        
        entity.is_active = False
        entity.updated_at = datetime.utcnow()
        self.db_session.commit()
        
        return True

    def list_rumors(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[RumorData], int]:
        """List rumors with pagination and filtering"""
        query = self.db_session.query(RumorEntity).filter(
            RumorEntity.is_active == True
        )
        
        # Apply filters
        if status:
            # For backwards compatibility, map status to other filters if needed
            if status == "active":
                query = query.filter(RumorEntity.is_active == True)
            elif status == "inactive":
                query = query.filter(RumorEntity.is_active == False)
        
        if search:
            query = query.filter(
                or_(
                    RumorEntity.original_content.ilike(f"%{search}%"),
                    RumorEntity.originator_id.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        entities = query.order_by(desc(RumorEntity.created_at)).offset(
            (page - 1) * size
        ).limit(size).all()
        
        # Convert to business data
        rumors = [self._entity_to_business_data(entity) for entity in entities]
        
        return rumors, total

    def get_rumor_statistics(self) -> Dict[str, Any]:
        """Get rumor statistics"""
        total_rumors = self.db_session.query(RumorEntity).filter(
            RumorEntity.is_active == True
        ).count()
        
        active_rumors = total_rumors  # All are active due to filter
        
        # Calculate average spread count
        avg_spread_subquery = self.db_session.query(
            func.count(RumorSpreadEntity.id).label('spread_count')
        ).filter(
            RumorSpreadEntity.rumor_id == RumorEntity.id
        ).subquery()
        
        avg_spread = self.db_session.query(
            func.avg(avg_spread_subquery.c.spread_count)
        ).scalar() or 0.0
        
        # Severity distribution
        severity_stats = {}
        for severity in ['trivial', 'minor', 'moderate', 'major', 'critical']:
            count = self.db_session.query(RumorEntity).filter(
                RumorEntity.is_active == True,
                RumorEntity.severity == severity
            ).count()
            severity_stats[f"{severity}_rumors"] = count
        
        return {
            "total_rumors": total_rumors,
            "active_rumors": active_rumors,
            "inactive_rumors": 0,  # We filter these out
            "average_spread_count": round(avg_spread, 2),
            **severity_stats
        }

    def _entity_to_business_data(self, entity: RumorEntity) -> RumorData:
        """Convert database entity to business data object"""
        # Convert variants
        variants = []
        for variant_entity in entity.variants:
            variant = RumorVariantData(
                id=variant_entity.id,
                content=variant_entity.content,
                created_at=variant_entity.created_at,
                parent_variant_id=variant_entity.parent_variant_id,
                entity_id=variant_entity.entity_id,
                mutation_metadata=variant_entity.mutation_metadata or {}
            )
            variants.append(variant)
        
        # Convert spread records
        spread_records = []
        for spread_entity in entity.spread_records:
            spread = RumorSpreadData(
                entity_id=spread_entity.entity_id,
                variant_id=spread_entity.variant_id,
                heard_from_entity_id=spread_entity.heard_from_entity_id,
                believability=spread_entity.believability,
                heard_at=spread_entity.heard_at
            )
            spread_records.append(spread)
        
        # Create business data object
        return RumorData(
            id=entity.id,
            originator_id=entity.originator_id,
            original_content=entity.original_content,
            categories=entity.categories or [],
            severity=entity.severity,
            truth_value=entity.truth_value,
            variants=variants,
            spread=spread_records,
            properties=entity.properties or {},
            created_at=entity.created_at
        ) 