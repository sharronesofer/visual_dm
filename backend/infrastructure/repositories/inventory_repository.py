"""
Inventory System Repository Implementation

This module provides SQLAlchemy repository implementation for the inventory system
according to the Development Bible infrastructure standards.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.exc import IntegrityError

from backend.infrastructure.models.inventory.models import InventoryEntity, InventoryAuditLogEntity
from backend.systems.inventory.models import InventoryModel
from backend.systems.inventory.services import InventoryRepositoryInterface


class SQLAlchemyInventoryRepository:
    """SQLAlchemy implementation of inventory repository"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def create(self, data: Dict[str, Any]) -> InventoryModel:
        """Create a new inventory"""
        try:
            # Create business model first for validation
            business_model = InventoryModel(**data)
            
            # Convert to database entity
            entity = InventoryEntity.from_business_model(business_model)
            
            # Save to database
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            # Log the creation
            await self._log_action(entity.id, "CREATE", data.get("actor_id"), new_values=data)
            
            # Return business model
            return entity.to_business_model()
            
        except IntegrityError as e:
            self.db.rollback()
            if "unique" in str(e).lower():
                raise ValueError("Inventory with this name already exists for this owner")
            raise
        except Exception as e:
            self.db.rollback()
            raise
    
    async def get_by_id(self, inventory_id: UUID) -> Optional[InventoryModel]:
        """Get inventory by ID"""
        entity = self.db.query(InventoryEntity).filter(
            InventoryEntity.id == inventory_id,
            InventoryEntity.is_active == True
        ).first()
        
        if not entity:
            return None
        
        return entity.to_business_model()
    
    async def get_by_name(self, name: str) -> Optional[InventoryModel]:
        """Get inventory by name"""
        entity = self.db.query(InventoryEntity).filter(
            InventoryEntity.name == name,
            InventoryEntity.is_active == True
        ).first()
        
        if not entity:
            return None
        
        return entity.to_business_model()
    
    async def update(self, inventory_id: UUID, data: Dict[str, Any]) -> Optional[InventoryModel]:
        """Update existing inventory"""
        try:
            # Get existing entity
            entity = self.db.query(InventoryEntity).filter(
                InventoryEntity.id == inventory_id,
                InventoryEntity.is_active == True
            ).first()
            
            if not entity:
                return None
            
            # Store old values for audit
            old_values = {
                "name": entity.name,
                "description": entity.description,
                "status": entity.status.value if entity.status else None,
                "properties": entity.properties,
                "max_capacity": entity.max_capacity,
                "max_weight": entity.max_weight
            }
            
            # Update fields
            for key, value in data.items():
                if key == "status":
                    # Handle enum conversion
                    from backend.infrastructure.models.inventory.models import InventoryStatusEnum
                    if isinstance(value, str):
                        value = InventoryStatusEnum(value)
                
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            # Update timestamp
            entity.updated_at = datetime.utcnow()
            
            # Commit changes
            self.db.commit()
            self.db.refresh(entity)
            
            # Log the update
            await self._log_action(
                inventory_id, 
                "UPDATE", 
                data.get("actor_id"),
                old_values=old_values,
                new_values=data
            )
            
            return entity.to_business_model()
            
        except IntegrityError as e:
            self.db.rollback()
            if "unique" in str(e).lower():
                raise ValueError("Inventory with this name already exists for this owner")
            raise
        except Exception as e:
            self.db.rollback()
            raise
    
    async def delete(self, inventory_id: UUID) -> bool:
        """Delete inventory (soft delete)"""
        try:
            entity = self.db.query(InventoryEntity).filter(
                InventoryEntity.id == inventory_id,
                InventoryEntity.is_active == True
            ).first()
            
            if not entity:
                return False
            
            # Soft delete
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Log the deletion
            await self._log_action(inventory_id, "DELETE", None)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise
    
    async def list(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[InventoryModel], int]:
        """List inventories with pagination and filtering"""
        try:
            # Base query
            query = self.db.query(InventoryEntity).filter(
                InventoryEntity.is_active == True
            )
            
            # Apply filters
            if status:
                from backend.infrastructure.models.inventory.models import InventoryStatusEnum
                query = query.filter(InventoryEntity.status == InventoryStatusEnum(status))
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        InventoryEntity.name.ilike(search_term),
                        InventoryEntity.description.ilike(search_term)
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(
                InventoryEntity.created_at.desc()
            ).offset(offset).limit(size).all()
            
            # Convert to business models
            business_models = [entity.to_business_model() for entity in entities]
            
            return business_models, total
            
        except Exception as e:
            raise
    
    async def list_by_owner(
        self,
        owner_id: UUID,
        page: int = 1,
        size: int = 50
    ) -> Tuple[List[InventoryModel], int]:
        """List inventories by owner"""
        try:
            # Base query for owner
            query = self.db.query(InventoryEntity).filter(
                InventoryEntity.owner_id == owner_id,
                InventoryEntity.is_active == True
            )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(
                InventoryEntity.created_at.desc()
            ).offset(offset).limit(size).all()
            
            # Convert to business models
            business_models = [entity.to_business_model() for entity in entities]
            
            return business_models, total
            
        except Exception as e:
            raise
    
    async def list_by_player(
        self,
        player_id: UUID,
        page: int = 1,
        size: int = 50
    ) -> Tuple[List[InventoryModel], int]:
        """List inventories by player"""
        try:
            # Base query for player
            query = self.db.query(InventoryEntity).filter(
                InventoryEntity.player_id == player_id,
                InventoryEntity.is_active == True
            )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(
                InventoryEntity.created_at.desc()
            ).offset(offset).limit(size).all()
            
            # Convert to business models
            business_models = [entity.to_business_model() for entity in entities]
            
            return business_models, total
            
        except Exception as e:
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get inventory statistics"""
        try:
            # Total inventories
            total = self.db.query(InventoryEntity).filter(
                InventoryEntity.is_active == True
            ).count()
            
            # Count by type
            type_stats = self.db.query(
                InventoryEntity.inventory_type,
                func.count(InventoryEntity.id)
            ).filter(
                InventoryEntity.is_active == True
            ).group_by(InventoryEntity.inventory_type).all()
            
            by_type = {type_enum.value: count for type_enum, count in type_stats}
            
            # Count by status
            status_stats = self.db.query(
                InventoryEntity.status,
                func.count(InventoryEntity.id)
            ).filter(
                InventoryEntity.is_active == True
            ).group_by(InventoryEntity.status).all()
            
            by_status = {status_enum.value: count for status_enum, count in status_stats}
            
            # Capacity and weight statistics
            capacity_stats = self.db.query(
                func.avg(InventoryEntity.current_item_count * 100.0 / InventoryEntity.max_capacity),
                func.avg(func.coalesce(
                    InventoryEntity.current_weight * 100.0 / func.nullif(InventoryEntity.max_weight, 0),
                    0
                )),
                func.sum(InventoryEntity.current_item_count),
                func.sum(InventoryEntity.current_weight)
            ).filter(
                InventoryEntity.is_active == True
            ).first()
            
            avg_capacity_usage = float(capacity_stats[0] or 0.0)
            avg_weight_usage = float(capacity_stats[1] or 0.0)
            total_items = int(capacity_stats[2] or 0)
            total_weight = float(capacity_stats[3] or 0.0)
            
            # Player statistics
            total_players = self.db.query(InventoryEntity.player_id).filter(
                InventoryEntity.player_id.isnot(None),
                InventoryEntity.is_active == True
            ).distinct().count()
            
            avg_inventories_per_player = total / total_players if total_players > 0 else 0.0
            
            # Encumbrance statistics (calculated from current data)
            encumbrance_stats = self._calculate_encumbrance_statistics()
            
            return {
                "total": total,
                "by_type": by_type,
                "by_status": by_status,
                "by_encumbrance": encumbrance_stats,
                "avg_capacity_usage": avg_capacity_usage,
                "avg_weight_usage": avg_weight_usage,
                "total_items": total_items,
                "total_weight": total_weight,
                "total_players": total_players,
                "avg_inventories_per_player": avg_inventories_per_player
            }
            
        except Exception as e:
            raise
    
    def _calculate_encumbrance_statistics(self) -> Dict[str, int]:
        """Calculate encumbrance level statistics"""
        # Get all inventories with weight data
        inventories = self.db.query(InventoryEntity).filter(
            InventoryEntity.is_active == True,
            InventoryEntity.max_weight.isnot(None),
            InventoryEntity.max_weight > 0
        ).all()
        
        encumbrance_counts = {
            "normal": 0,
            "heavy": 0,
            "encumbered": 0,
            "overloaded": 0
        }
        
        for inventory in inventories:
            ratio = inventory.current_weight / inventory.max_weight
            if ratio <= 0.75:
                encumbrance_counts["normal"] += 1
            elif ratio <= 1.0:
                encumbrance_counts["heavy"] += 1
            elif ratio <= 1.25:
                encumbrance_counts["encumbered"] += 1
            else:
                encumbrance_counts["overloaded"] += 1
        
        return encumbrance_counts
    
    async def _log_action(
        self,
        inventory_id: UUID,
        action: str,
        actor_id: Optional[UUID] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log inventory action for audit trail"""
        try:
            # Create audit log entry
            log_entry = InventoryAuditLogEntity(
                inventory_id=inventory_id,
                action=action,
                actor_id=actor_id,
                actor_type="player" if actor_id else "system",
                old_values=old_values,
                new_values=new_values,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow()
            )
            
            # Generate changes summary
            if old_values and new_values:
                changes = []
                for key, new_val in new_values.items():
                    old_val = old_values.get(key)
                    if old_val != new_val:
                        changes.append(f"{key}: {old_val} -> {new_val}")
                log_entry.changes_summary = "; ".join(changes)
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            # Don't fail the main operation if audit logging fails
            self.db.rollback()
            # In production, this should be logged to a monitoring system
            print(f"Failed to log inventory action: {e}")
    
    async def get_by_name_and_owner(self, name: str, owner_id: UUID) -> Optional[InventoryModel]:
        """Get inventory by name and owner (for duplicate checking)"""
        entity = self.db.query(InventoryEntity).filter(
            InventoryEntity.name == name,
            InventoryEntity.owner_id == owner_id,
            InventoryEntity.is_active == True
        ).first()
        
        if not entity:
            return None
        
        return entity.to_business_model()
    
    async def update_capacity_counters(
        self,
        inventory_id: UUID,
        item_count_delta: int = 0,
        weight_delta: float = 0.0
    ) -> bool:
        """Update inventory capacity counters (for item operations)"""
        try:
            entity = self.db.query(InventoryEntity).filter(
                InventoryEntity.id == inventory_id,
                InventoryEntity.is_active == True
            ).first()
            
            if not entity:
                return False
            
            # Update counters
            entity.current_item_count = max(0, entity.current_item_count + item_count_delta)
            entity.current_weight = max(0.0, entity.current_weight + weight_delta)
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Log the capacity update
            await self._log_action(
                inventory_id,
                "CAPACITY_UPDATE",
                new_values={
                    "item_count_delta": item_count_delta,
                    "weight_delta": weight_delta,
                    "new_item_count": entity.current_item_count,
                    "new_weight": entity.current_weight
                }
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise 