"""
Repair System Database Repository

Handles all database operations for the repair system.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.systems.repair.models.repair_models import RepairRequest, RepairStatus
from backend.systems.equipment.models.equipment_models import EquipmentInstance, MaintenanceRecord


class RepairRepository:
    """Repository for repair database operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_equipment_by_id(self, equipment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get equipment data from database.
        
        Args:
            equipment_id: ID of equipment to retrieve
        
        Returns:
            Equipment data or None if not found
        """
        try:
            equipment = self.db.query(EquipmentInstance).filter(
                EquipmentInstance.id == equipment_id
            ).first()
            
            if not equipment:
                return None
            
            return {
                'id': equipment.id,
                'name': equipment.custom_name or f'Equipment {equipment.template_id}',
                'type': 'weapon',  # Would need to look up from template
                'quality': 'basic',  # Would need to look up from template  
                'current_durability': equipment.durability,
                'max_durability': 100.0,
                'base_value': equipment.current_value or 100.0,
                'owner_id': equipment.owner_id,
                'location_id': equipment.location,
                'template_id': equipment.template_id
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve equipment {equipment_id}: {e}")
    
    def update_equipment_durability(self, equipment_id: str, new_durability: float) -> bool:
        """
        Update equipment durability in database.
        
        Args:
            equipment_id: ID of equipment to update
            new_durability: New durability value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            equipment = self.db.query(EquipmentInstance).filter(
                EquipmentInstance.id == equipment_id
            ).first()
            
            if not equipment:
                return False
            
            old_durability = equipment.durability
            equipment.durability = new_durability
            
            # Create maintenance record
            maintenance_record = MaintenanceRecord(
                equipment_instance_id=equipment_id,
                action_type="repair",
                durability_before=old_durability,
                durability_after=new_durability,
                success=True,
                notes=f"Durability updated from {old_durability:.1f} to {new_durability:.1f}"
            )
            
            self.db.add(maintenance_record)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update equipment {equipment_id} durability: {e}")
    
    def create_repair_request(self, repair_request: RepairRequest) -> RepairRequest:
        """
        Save repair request to database.
        
        Args:
            repair_request: RepairRequest instance to save
            
        Returns:
            Saved repair request with ID populated
        """
        try:
            self.db.add(repair_request)
            self.db.commit()
            self.db.refresh(repair_request)
            return repair_request
            
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create repair request: {e}")
    
    def get_repair_request_by_id(self, repair_request_id: str) -> Optional[RepairRequest]:
        """
        Get repair request by ID.
        
        Args:
            repair_request_id: ID of repair request
            
        Returns:
            RepairRequest or None if not found
        """
        try:
            return self.db.query(RepairRequest).filter(
                RepairRequest.id == repair_request_id
            ).first()
            
        except Exception as e:
            raise RuntimeError(f"Failed to get repair request {repair_request_id}: {e}")
    
    def update_repair_request(self, repair_request: RepairRequest) -> RepairRequest:
        """
        Update repair request in database.
        
        Args:
            repair_request: Updated repair request
            
        Returns:
            Updated repair request
        """
        try:
            self.db.commit()
            return repair_request
            
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update repair request: {e}")
    
    def get_repair_requests(
        self,
        repairer_id: Optional[str] = None,
        character_id: Optional[str] = None,
        status_filter: Optional[RepairStatus] = None
    ) -> List[RepairRequest]:
        """
        Get repair requests with filtering.
        
        Args:
            repairer_id: Filter by specific repairer
            character_id: Filter by specific character
            status_filter: Filter by repair status
            
        Returns:
            List of repair requests
        """
        try:
            query = self.db.query(RepairRequest)
            
            if repairer_id:
                query = query.filter(RepairRequest.repairer_id == repairer_id)
            
            if character_id:
                query = query.filter(RepairRequest.character_id == character_id)
            
            if status_filter:
                query = query.filter(RepairRequest.status == status_filter)
            
            return query.order_by(RepairRequest.created_at.desc()).all()
            
        except Exception as e:
            raise RuntimeError(f"Failed to get repair requests: {e}")
    
    def get_equipment_details(self, equipment_id: str) -> Dict[str, Any]:
        """
        Get equipment details from database.
        
        Args:
            equipment_id: ID of equipment
            
        Returns:
            Equipment details dictionary
        """
        equipment = self.get_equipment_by_id(equipment_id)
        if not equipment:
            raise RuntimeError(f"Equipment {equipment_id} not found")
        
        return equipment
    
    def get_damaged_equipment(
        self, 
        character_id: Optional[str] = None,
        damage_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Get list of damaged equipment that needs repair.
        
        Args:
            character_id: Filter by character ID
            damage_threshold: Equipment below this durability level
            
        Returns:
            List of damaged equipment
        """
        try:
            query = self.db.query(EquipmentInstance).filter(
                EquipmentInstance.durability < (damage_threshold * 100.0)
            )
            
            if character_id:
                query = query.filter(EquipmentInstance.owner_id == character_id)
            
            damaged_equipment = query.all()
            
            return [
                {
                    'id': eq.id,
                    'name': eq.custom_name or f'Equipment {eq.template_id}',
                    'current_durability': eq.durability,
                    'status': eq.get_durability_status(),
                    'owner_id': eq.owner_id,
                    'template_id': eq.template_id
                }
                for eq in damaged_equipment
            ]
            
        except Exception as e:
            raise RuntimeError(f"Failed to get damaged equipment: {e}")
    
    def create_maintenance_record(
        self,
        equipment_id: str,
        action_type: str,
        durability_before: float,
        durability_after: float,
        gold_cost: int = 0,
        materials_used: List[Dict[str, Any]] = None,
        success: bool = True,
        notes: str = None,
        performed_by: str = None
    ) -> MaintenanceRecord:
        """
        Create a maintenance record for equipment.
        
        Args:
            equipment_id: ID of equipment
            action_type: Type of maintenance performed
            durability_before: Durability before maintenance
            durability_after: Durability after maintenance
            gold_cost: Cost in gold
            materials_used: List of materials and quantities used
            success: Whether the maintenance was successful
            notes: Additional notes
            performed_by: Character or NPC who performed maintenance
            
        Returns:
            Created maintenance record
        """
        try:
            record = MaintenanceRecord(
                equipment_instance_id=equipment_id,
                action_type=action_type,
                durability_before=durability_before,
                durability_after=durability_after,
                gold_cost=gold_cost,
                materials_used=materials_used or [],
                success=success,
                notes=notes,
                performed_by=performed_by
            )
            
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record
            
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create maintenance record: {e}") 