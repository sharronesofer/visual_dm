"""
Hybrid Equipment Service for Visual DM.

Combines JSON-based templates with SQLAlchemy database instances to provide
a complete equipment management system that balances performance, flexibility,
and ease of configuration.

Hybrid Pattern Implementation:
- Templates (JSON): Static equipment definitions, quality tiers, enchantments
- Instances (Database): Individual equipment owned by characters with unique state
- Service Layer: Orchestrates between templates and instances
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4
from sqlalchemy.orm import Session

from .template_service import EquipmentTemplateService, template_service, EquipmentTemplate, EnchantmentTemplate
from backend.systems.equipment.services.enchanting_service import EnchantingService
from .equipment_quality import EquipmentQualityService
from .durability_service import DurabilityService
from backend.systems.equipment.models.equipment_models import (
    EquipmentInstance, AppliedEnchantment, MaintenanceRecord, 
    EquipmentSet, CharacterEquipmentProfile
)
from backend.infrastructure.persistence.equipment.equipment_repository import EquipmentRepository

logger = logging.getLogger(__name__)

class HybridEquipmentService:
    """
    Main service that orchestrates equipment management using the hybrid pattern.
    
    Combines static templates (JSON) with dynamic instances (database) to provide
    complete equipment lifecycle management.
    """
    
    def __init__(self, db_session: Session, equipment_repo: EquipmentRepository = None):
        """Initialize hybrid equipment service."""
        self.db = db_session
        self.templates = template_service
        
        # Initialize services with proper dependencies
        self.quality_service = EquipmentQualityService()
        self.enchanting = EnchantingService(self.quality_service)
        self.durability = DurabilityService(db_session)
        self.repo = equipment_repo or EquipmentRepository()
        
        # Ensure templates are loaded
        if not self.templates._loaded:
            self.templates.load_all_templates()
        
        logger.info("Initialized HybridEquipmentService")
    
    # Equipment Instance Management
    
    def create_equipment_instance(
        self, 
        template_id: str, 
        owner_id: str,
        quality_override: str = None,
        custom_name: str = None
    ) -> Optional[EquipmentInstance]:
        """
        Create a new equipment instance from a template.
        
        Args:
            template_id: ID of the equipment template
            owner_id: Character ID who will own this equipment
            quality_override: Override the template's quality tier
            custom_name: Custom name for this instance
            
        Returns:
            Created equipment instance or None if failed
        """
        template = self.templates.get_equipment_template(template_id)
        if not template:
            logger.error(f"Equipment template not found: {template_id}")
            return None
        
        # Determine quality tier
        quality_tier = quality_override or template.quality_tier
        quality_config = self.templates.get_quality_tier(quality_tier)
        
        if not quality_config:
            logger.error(f"Quality tier not found: {quality_tier}")
            return None
        
        # Calculate instance properties
        base_value = self.templates.calculate_template_value(template_id, quality_tier)
        instance_id = str(uuid4())
        
        # Create the database instance
        instance = EquipmentInstance(
            id=instance_id,
            template_id=template_id,
            owner_id=owner_id,
            durability=100.0,
            custom_name=custom_name,
            current_value=base_value,
            identification_level=1,  # Basic identification
            custom_metadata={
                "quality_tier": quality_tier,
                "base_template": template_id,
                "creation_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        try:
            self.db.add(instance)
            self.db.commit()
            logger.info(f"Created equipment instance {instance_id} from template {template_id}")
            return instance
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create equipment instance: {e}")
            return None
    
    def get_equipment_instance(self, instance_id: str) -> Optional[EquipmentInstance]:
        """Get equipment instance by ID."""
        return self.db.query(EquipmentInstance).filter_by(id=instance_id).first()
    
    def get_character_equipment(
        self, 
        character_id: str, 
        equipped_only: bool = False
    ) -> List[EquipmentInstance]:
        """Get all equipment for a character."""
        query = self.db.query(EquipmentInstance).filter_by(owner_id=character_id)
        
        if equipped_only:
            query = query.filter_by(is_equipped=True)
        
        return query.all()
    
    def get_equipment_details(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete equipment details combining template and instance data.
        
        Returns a comprehensive view that merges static template properties
        with dynamic instance state.
        """
        instance = self.get_equipment_instance(instance_id)
        if not instance:
            return None
        
        # Get the template data
        template = self.templates.get_equipment_template(instance.template_id)
        if not template:
            logger.warning(f"Template not found for instance {instance_id}: {instance.template_id}")
            return None
        
        # Get quality tier
        quality_tier = instance.custom_metadata.get("quality_tier", template.quality_tier)
        quality_config = self.templates.get_quality_tier(quality_tier)
        
        # Calculate current stats (affected by condition)
        condition_penalty = self._calculate_condition_penalty(instance.durability, quality_config)
        adjusted_stats = {}
        for stat, value in template.stat_modifiers.items():
            adjusted_stats[stat] = int(value * (1.0 - condition_penalty))
        
        # Get active enchantments
        active_enchantments = []
        for applied_ench in instance.applied_enchantments:
            if applied_ench.is_active():
                ench_template = self.templates.get_enchantment_template(applied_ench.enchantment_id)
                if ench_template:
                    active_enchantments.append({
                        "template": ench_template,
                        "power_level": applied_ench.power_level,
                        "stability": applied_ench.stability,
                        "mastery_level": applied_ench.mastery_level
                    })
        
        return {
            "instance": instance,
            "template": template,
            "quality_config": quality_config,
            "current_stats": adjusted_stats,
            "condition_status": instance.get_durability_status(),
            "condition_penalty": condition_penalty,
            "active_enchantments": active_enchantments,
            "maintenance_history": instance.maintenance_history,
            "estimated_repair_cost": self._calculate_repair_cost(instance, template, quality_config),
            "can_be_enchanted": len(instance.applied_enchantments) < self.quality_service.get_enchantment_slots(quality_tier) if quality_config else False
        }
    
    # Equipment Operations
    
    def equip_item(
        self, 
        instance_id: str, 
        equipment_slot: str, 
        force: bool = False
    ) -> bool:
        """
        Equip an item to a specific slot.
        
        Args:
            instance_id: Equipment instance to equip
            equipment_slot: Slot to equip to (main_hand, chest, etc.)
            force: Skip validation checks
            
        Returns:
            True if successful
        """
        instance = self.get_equipment_instance(instance_id)
        if not instance:
            return False
        
        template = self.templates.get_equipment_template(instance.template_id)
        if not template:
            return False
        
        # Validate slot compatibility
        if not force and equipment_slot not in template.equipment_slots:
            logger.error(f"Invalid slot {equipment_slot} for equipment {template.name}")
            return False
        
        # Check if item is functional
        if not force and not instance.is_functional():
            logger.error(f"Cannot equip broken equipment: {instance.id}")
            return False
        
        # Unequip any existing item in this slot
        existing = self.db.query(EquipmentInstance).filter_by(
            owner_id=instance.owner_id,
            equipment_slot=equipment_slot,
            is_equipped=True
        ).first()
        
        if existing:
            self.unequip_item(existing.id)
        
        # Equip the new item
        instance.is_equipped = True
        instance.equipment_slot = equipment_slot
        instance.location = "equipped"
        instance.last_updated = datetime.utcnow()
        
        try:
            self.db.commit()
            logger.info(f"Equipped {instance.id} to slot {equipment_slot}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to equip item: {e}")
            return False
    
    def unequip_item(self, instance_id: str) -> bool:
        """Unequip an item."""
        instance = self.get_equipment_instance(instance_id)
        if not instance:
            return False
        
        instance.is_equipped = False
        instance.equipment_slot = None
        instance.location = "inventory"
        instance.last_updated = datetime.utcnow()
        
        try:
            self.db.commit()
            logger.info(f"Unequipped item {instance.id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to unequip item: {e}")
            return False
    
    def repair_equipment(
        self, 
        instance_id: str, 
        repairer_id: str,
        materials: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Repair equipment using the quality tier requirements.
        
        Returns:
            Dictionary with repair results including success, cost, durability change
        """
        instance = self.get_equipment_instance(instance_id)
        if not instance:
            return {"success": False, "error": "Equipment not found"}
        
        template = self.templates.get_equipment_template(instance.template_id)
        quality_tier = instance.custom_metadata.get("quality_tier", template.quality_tier)
        quality_config = self.templates.get_quality_tier(quality_tier)
        
        if not quality_config:
            return {"success": False, "error": "Quality configuration not found"}
        
        # Calculate repair parameters
        repair_cost = self._calculate_repair_cost(instance, template, quality_config)
        durability_before = instance.durability
        
        # Determine repair amount (can't exceed original max)
        max_durability = 100.0 * quality_config.durability_multiplier if hasattr(quality_config, 'durability_multiplier') else 100.0
        repair_amount = min(30.0, max_durability - instance.durability)
        
        # Apply repair
        instance.durability = min(max_durability, instance.durability + repair_amount)
        instance.last_repaired = datetime.utcnow()
        instance.last_updated = datetime.utcnow()
        
        # Recalculate value based on new condition
        instance.current_value = self._calculate_current_value(instance, template, quality_config)
        
        # Create maintenance record
        maintenance = MaintenanceRecord(
            equipment_instance_id=instance.id,
            action_type="repair",
            performed_by=repairer_id,
            durability_before=durability_before,
            durability_after=instance.durability,
            gold_cost=repair_cost,
            materials_used=materials or {},
            success=True,
            notes=f"Repaired {repair_amount:.1f} durability points"
        )
        
        try:
            self.db.add(maintenance)
            self.db.commit()
            
            return {
                "success": True,
                "durability_before": durability_before,
                "durability_after": instance.durability,
                "repair_amount": repair_amount,
                "gold_cost": repair_cost,
                "new_condition": instance.get_durability_status()
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to repair equipment: {e}")
            return {"success": False, "error": str(e)}
    
    # Enchanting Integration
    
    def apply_enchantment(
        self, 
        instance_id: str, 
        enchantment_id: str, 
        enchanter_id: str
    ) -> Dict[str, Any]:
        """Apply an enchantment to equipment using the enchanting service."""
        instance = self.get_equipment_instance(instance_id)
        if not instance:
            return {"success": False, "error": "Equipment not found"}
        
        # Use the enchanting service for the application logic
        result = self.enchanting.apply_enchantment(
            instance_id, enchantment_id, enchanter_id
        )
        
        if result["success"]:
            # Update the equipment instance if needed
            instance.last_updated = datetime.utcnow()
            self.db.commit()
        
        return result
    
    def disenchant_equipment(
        self, 
        instance_id: str, 
        disenchanter_id: str
    ) -> Dict[str, Any]:
        """Disenchant equipment to learn enchantments."""
        return self.enchanting.disenchant_item(instance_id, disenchanter_id)
    
    # Equipment Degradation
    
    def process_time_degradation(self, character_id: str = None) -> Dict[str, Any]:
        """
        Process time-based equipment degradation.
        
        Args:
            character_id: Process only this character's equipment, or all if None
            
        Returns:
            Summary of degradation processed
        """
        query = self.db.query(EquipmentInstance)
        if character_id:
            query = query.filter_by(owner_id=character_id)
        
        equipment_list = query.all()
        processed = 0
        degraded = 0
        
        for instance in equipment_list:
            if self._should_process_degradation(instance):
                if self._apply_time_degradation(instance):
                    degraded += 1
                processed += 1
        
        if processed > 0:
            self.db.commit()
        
        return {
            "equipment_processed": processed,
            "equipment_degraded": degraded,
            "character_id": character_id
        }
    
    def apply_combat_damage(
        self, 
        instance_id: str, 
        damage_amount: float, 
        damage_type: str = "physical"
    ) -> bool:
        """Apply combat damage to equipment."""
        instance = self.get_equipment_instance(instance_id)
        if not instance:
            return False
        
        template = self.templates.get_equipment_template(instance.template_id)
        if not template:
            return False
        
        # Get damage multiplier from quality configuration
        quality_tier = instance.custom_metadata.get("quality_tier", template.quality_tier)
        quality_config = self.templates.get_quality_tier(quality_tier)
        
        # Calculate actual damage based on item type and quality
        base_multiplier = 0.5  # Default
        if hasattr(quality_config, 'degradation_rate'):
            base_multiplier *= quality_config.degradation_rate
        
        actual_damage = damage_amount * base_multiplier
        instance.durability = max(0.0, instance.durability - actual_damage)
        instance.last_updated = datetime.utcnow()
        
        try:
            self.db.commit()
            logger.debug(f"Applied {actual_damage:.2f} combat damage to {instance.id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to apply combat damage: {e}")
            return False
    
    # Helper Methods
    
    def _calculate_condition_penalty(self, durability: float, quality_config) -> float:
        """Calculate stat penalty based on equipment condition."""
        if durability >= 75:
            return 0.0
        elif durability >= 50:
            return 0.1
        elif durability >= 25:
            return 0.25
        elif durability > 0:
            return 0.5
        else:
            return 1.0  # Broken
    
    def _calculate_repair_cost(
        self, 
        instance: EquipmentInstance, 
        template: EquipmentTemplate, 
        quality_config
    ) -> int:
        """Calculate repair cost based on damage and quality."""
        damage_percent = (100.0 - instance.durability) / 100.0
        base_cost = quality_config.repair_cost if quality_config else 500
        return int(base_cost * damage_percent)
    
    def _calculate_current_value(
        self, 
        instance: EquipmentInstance, 
        template: EquipmentTemplate, 
        quality_config
    ) -> int:
        """Calculate current market value based on condition and enchantments."""
        base_value = self.templates.calculate_template_value(
            template.id, 
            instance.custom_metadata.get("quality_tier", template.quality_tier)
        )
        
        # Apply condition depreciation
        condition_factor = instance.durability / 100.0
        current_value = int(base_value * condition_factor)
        
        # Add enchantment value
        for enchantment in instance.applied_enchantments:
            if enchantment.is_active():
                ench_template = self.templates.get_enchantment_template(enchantment.enchantment_id)
                if ench_template:
                    enchantment_value = int(ench_template.base_cost * (enchantment.power_level / 100.0))
                    current_value += enchantment_value
        
        return current_value
    
    def _should_process_degradation(self, instance: EquipmentInstance) -> bool:
        """Check if equipment should undergo time degradation."""
        if instance.durability <= 0:
            return False
        
        # Check if enough time has passed since last update
        if instance.last_updated:
            time_since_update = datetime.utcnow() - instance.last_updated
            return time_since_update > timedelta(hours=1)
        
        return True
    
    def _apply_time_degradation(self, instance: EquipmentInstance) -> bool:
        """Apply time-based degradation to equipment."""
        template = self.templates.get_equipment_template(instance.template_id)
        if not template:
            return False
        
        quality_tier = instance.custom_metadata.get("quality_tier", template.quality_tier)
        quality_config = self.templates.get_quality_tier(quality_tier)
        
        if not quality_config:
            return False
        
        # Calculate degradation rate (slower for higher quality)
        base_degradation = 0.1  # 0.1% per hour
        degradation_rate = base_degradation * quality_config.degradation_rate
        
        # Apply degradation
        old_durability = instance.durability
        instance.durability = max(0.0, instance.durability - degradation_rate)
        instance.last_updated = datetime.utcnow()
        
        return instance.durability != old_durability
    
    # Template Integration Methods
    
    def list_available_equipment_templates(
        self, 
        item_type: str = None, 
        quality_tier: str = None,
        max_level: int = None
    ) -> List[EquipmentTemplate]:
        """List equipment templates available based on criteria."""
        templates = self.templates.list_equipment_templates()
        
        filtered = []
        for template in templates:
            # Filter by type
            if item_type and template.item_type != item_type:
                continue
            
            # Filter by quality
            if quality_tier and template.quality_tier != quality_tier:
                continue
            
            # Filter by level requirement
            if max_level and template.restrictions.get("min_level", 0) > max_level:
                continue
            
            filtered.append(template)
        
        return filtered
    
    def get_equipment_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive template information."""
        template = self.templates.get_equipment_template(template_id)
        if not template:
            return None
        
        quality_config = self.templates.get_quality_tier(template.quality_tier)
        compatible_enchantments = self.templates.get_compatible_enchantments(template_id)
        
        return {
            "template": template,
            "quality_config": quality_config,
            "calculated_value": self.templates.calculate_template_value(template_id),
            "compatible_enchantments": compatible_enchantments,
            "can_be_crafted": template.crafting_requirements is not None
        }


# Convenience function for creating service instances
def create_hybrid_equipment_service(db_session: Session) -> HybridEquipmentService:
    """Create a new hybrid equipment service instance."""
    return HybridEquipmentService(db_session) 