"""
Equipment Instance Repository - Database Infrastructure Layer

Provides database persistence for equipment instances according to Development Bible standards.
This is INFRASTRUCTURE code - business logic lives in /backend/systems/.

Key Features:
- SQLAlchemy database operations for equipment instances
- Handles quality tier (affects durability) and rarity tier (affects enchantments) separately
- Integration with business logic through interfaces
- Database transaction management
- Data conversion between database and business models
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
import logging

from backend.systems.equipment.services.business_logic_service import (
    EquipmentInstanceData, EquipmentSlot, EnchantmentData
)
from backend.systems.equipment.repositories import IEquipmentInstanceRepository

logger = logging.getLogger(__name__)


class EquipmentInstanceRepository(IEquipmentInstanceRepository):
    """Infrastructure implementation of equipment instance repository"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_equipment(self, equipment_data: EquipmentInstanceData) -> EquipmentInstanceData:
        """Create a new equipment instance in the database"""
        try:
            # Insert equipment instance using raw SQL for now
            insert_query = text("""
                INSERT INTO equipment_instances (
                    id, character_id, template_id, slot, current_durability, max_durability,
                    usage_count, quality_tier, rarity_tier, enchantment_seed, is_equipped,
                    equipment_set, created_at, updated_at
                ) VALUES (
                    :id, :character_id, :template_id, :slot, :current_durability, :max_durability,
                    :usage_count, :quality_tier, :rarity_tier, :enchantment_seed, :is_equipped,
                    :equipment_set, :created_at, :updated_at
                )
            """)
            
            self.db.execute(insert_query, {
                'id': str(equipment_data.id),
                'character_id': str(equipment_data.character_id),
                'template_id': equipment_data.template_id,
                'slot': equipment_data.slot.value,
                'current_durability': equipment_data.current_durability,
                'max_durability': equipment_data.max_durability,
                'usage_count': equipment_data.usage_count,
                'quality_tier': equipment_data.quality_tier,
                'rarity_tier': equipment_data.rarity_tier,
                'enchantment_seed': None,  # Optional field
                'is_equipped': equipment_data.is_equipped,
                'equipment_set': equipment_data.equipment_set,
                'created_at': equipment_data.created_at,
                'updated_at': equipment_data.updated_at
            })
            
            # Create enchantment records
            for enchantment in equipment_data.enchantments:
                enchant_query = text("""
                    INSERT INTO applied_enchantments (
                        id, equipment_id, enchantment_type, magnitude, target_attribute, is_active, applied_at
                    ) VALUES (
                        gen_random_uuid(), :equipment_id, :enchantment_type, :magnitude, :target_attribute, :is_active, :applied_at
                    )
                """)
                
                self.db.execute(enchant_query, {
                    'equipment_id': str(equipment_data.id),
                    'enchantment_type': enchantment.enchantment_type,
                    'magnitude': enchantment.magnitude,
                    'target_attribute': enchantment.target_attribute,
                    'is_active': enchantment.is_active,
                    'applied_at': datetime.now()
                })
            
            self.db.commit()
            logger.info(f"Created equipment instance {equipment_data.id}")
            
            return equipment_data
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating equipment instance: {e}")
            raise
    
    def get_equipment_by_id(self, equipment_id: UUID) -> Optional[EquipmentInstanceData]:
        """Get equipment instance by ID"""
        try:
            # Get equipment instance
            equipment_query = text("""
                SELECT id, character_id, template_id, slot, current_durability, max_durability,
                       usage_count, quality_tier, rarity_tier, is_equipped, equipment_set,
                       created_at, updated_at
                FROM equipment_instances 
                WHERE id = :equipment_id
            """)
            
            result = self.db.execute(equipment_query, {'equipment_id': str(equipment_id)}).fetchone()
            
            if not result:
                return None
            
            # Get enchantments
            enchantments_query = text("""
                SELECT enchantment_type, magnitude, target_attribute, is_active
                FROM applied_enchantments
                WHERE equipment_id = :equipment_id AND is_active = true
            """)
            
            enchantment_results = self.db.execute(enchantments_query, {'equipment_id': str(equipment_id)}).fetchall()
            
            enchantments = [
                EnchantmentData(
                    enchantment_type=row.enchantment_type,
                    magnitude=row.magnitude,
                    target_attribute=row.target_attribute,
                    is_active=row.is_active
                )
                for row in enchantment_results
            ]
            
            # Calculate effective stats (would be more complex in real implementation)
            effective_stats = {"placeholder": "stats would be calculated here"}
            
            return EquipmentInstanceData(
                id=UUID(result.id),
                character_id=UUID(result.character_id),
                template_id=result.template_id,
                slot=EquipmentSlot(result.slot),
                current_durability=result.current_durability,
                max_durability=result.max_durability,
                usage_count=result.usage_count,
                quality_tier=result.quality_tier,
                rarity_tier=result.rarity_tier,
                equipment_set=result.equipment_set,
                is_equipped=result.is_equipped,
                enchantments=enchantments,
                effective_stats=effective_stats,
                created_at=result.created_at,
                updated_at=result.updated_at
            )
            
        except Exception as e:
            logger.error(f"Error retrieving equipment {equipment_id}: {e}")
            return None
    
    def get_character_equipment(self, character_id: UUID, equipped_only: bool = False) -> List[EquipmentInstanceData]:
        """Get all equipment for a character"""
        try:
            where_clause = "WHERE character_id = :character_id"
            params = {'character_id': str(character_id)}
            
            if equipped_only:
                where_clause += " AND is_equipped = true"
            
            equipment_query = text(f"""
                SELECT id, character_id, template_id, slot, current_durability, max_durability,
                       usage_count, quality_tier, rarity_tier, is_equipped, equipment_set,
                       created_at, updated_at
                FROM equipment_instances 
                {where_clause}
                ORDER BY created_at DESC
            """)
            
            results = self.db.execute(equipment_query, params).fetchall()
            
            equipment_list = []
            for row in results:
                # Get enchantments for each piece
                enchantments_query = text("""
                    SELECT enchantment_type, magnitude, target_attribute, is_active
                    FROM applied_enchantments
                    WHERE equipment_id = :equipment_id AND is_active = true
                """)
                
                enchantment_results = self.db.execute(enchantments_query, {'equipment_id': row.id}).fetchall()
                
                enchantments = [
                    EnchantmentData(
                        enchantment_type=ench.enchantment_type,
                        magnitude=ench.magnitude,
                        target_attribute=ench.target_attribute,
                        is_active=ench.is_active
                    )
                    for ench in enchantment_results
                ]
                
                effective_stats = {"placeholder": "stats would be calculated here"}
                
                equipment_list.append(EquipmentInstanceData(
                    id=UUID(row.id),
                    character_id=UUID(row.character_id),
                    template_id=row.template_id,
                    slot=EquipmentSlot(row.slot),
                    current_durability=row.current_durability,
                    max_durability=row.max_durability,
                    usage_count=row.usage_count,
                    quality_tier=row.quality_tier,
                    rarity_tier=row.rarity_tier,
                    equipment_set=row.equipment_set,
                    is_equipped=row.is_equipped,
                    enchantments=enchantments,
                    effective_stats=effective_stats,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                ))
            
            return equipment_list
            
        except Exception as e:
            logger.error(f"Error retrieving character equipment for {character_id}: {e}")
            return []
    
    def list_equipment(self, character_id: Optional[UUID] = None, slot: Optional[EquipmentSlot] = None,
                      equipment_set: Optional[str] = None, quality_tier: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> List[EquipmentInstanceData]:
        """List equipment with optional filters"""
        try:
            where_conditions = []
            params = {'limit': limit, 'offset': offset}
            
            if character_id:
                where_conditions.append("character_id = :character_id")
                params['character_id'] = str(character_id)
            
            if slot:
                where_conditions.append("slot = :slot")
                params['slot'] = slot.value
            
            if equipment_set:
                where_conditions.append("equipment_set = :equipment_set")
                params['equipment_set'] = equipment_set
            
            if quality_tier:
                where_conditions.append("quality_tier = :quality_tier")
                params['quality_tier'] = quality_tier
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            equipment_query = text(f"""
                SELECT id, character_id, template_id, slot, current_durability, max_durability,
                       usage_count, quality_tier, rarity_tier, is_equipped, equipment_set,
                       created_at, updated_at
                FROM equipment_instances 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            
            results = self.db.execute(equipment_query, params).fetchall()
            
            # Convert to business objects (simplified for brevity)
            equipment_list = []
            for row in results:
                effective_stats = {"placeholder": "stats would be calculated here"}
                
                equipment_list.append(EquipmentInstanceData(
                    id=UUID(row.id),
                    character_id=UUID(row.character_id),
                    template_id=row.template_id,
                    slot=EquipmentSlot(row.slot),
                    current_durability=row.current_durability,
                    max_durability=row.max_durability,
                    usage_count=row.usage_count,
                    quality_tier=row.quality_tier,
                    rarity_tier=row.rarity_tier,
                    equipment_set=row.equipment_set,
                    is_equipped=row.is_equipped,
                    enchantments=[],  # Could load separately if needed
                    effective_stats=effective_stats,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                ))
            
            return equipment_list
            
        except Exception as e:
            logger.error(f"Error listing equipment: {e}")
            return []
    
    def update_equipment(self, equipment_id: UUID, updates: Dict[str, Any]) -> EquipmentInstanceData:
        """Update equipment instance"""
        try:
            # Build update query dynamically
            update_fields = []
            params = {'equipment_id': str(equipment_id), 'updated_at': datetime.now()}
            
            for field, value in updates.items():
                if field in ['current_durability', 'is_equipped', 'usage_count']:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value
            
            if not update_fields:
                # No valid updates, just return current equipment
                return self.get_equipment_by_id(equipment_id)
            
            update_query = text(f"""
                UPDATE equipment_instances 
                SET {', '.join(update_fields)}, updated_at = :updated_at
                WHERE id = :equipment_id
            """)
            
            self.db.execute(update_query, params)
            self.db.commit()
            
            logger.info(f"Updated equipment {equipment_id}")
            
            # Return updated equipment
            return self.get_equipment_by_id(equipment_id)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating equipment {equipment_id}: {e}")
            raise
    
    def delete_equipment(self, equipment_id: UUID) -> bool:
        """Delete equipment instance"""
        try:
            # Delete enchantments first (due to foreign key)
            delete_enchantments_query = text("""
                DELETE FROM applied_enchantments WHERE equipment_id = :equipment_id
            """)
            self.db.execute(delete_enchantments_query, {'equipment_id': str(equipment_id)})
            
            # Delete equipment instance
            delete_equipment_query = text("""
                DELETE FROM equipment_instances WHERE id = :equipment_id
            """)
            result = self.db.execute(delete_equipment_query, {'equipment_id': str(equipment_id)})
            
            self.db.commit()
            
            if result.rowcount > 0:
                logger.info(f"Deleted equipment {equipment_id}")
                return True
            else:
                logger.warning(f"Equipment {equipment_id} not found for deletion")
                return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting equipment {equipment_id}: {e}")
            return False 