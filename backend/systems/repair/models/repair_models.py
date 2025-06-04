"""
Repair System Domain Models

Business domain models for the repair system.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RepairStatus(Enum):
    """Status of a repair request"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RepairSkill(Enum):
    """Repair skill levels"""
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class RepairRequirement:
    """Represents a repair requirement (material or tool)"""
    item_type: str  # "material" or "tool"
    item_id: str    # ID of the required item
    quantity: int   # Quantity needed
    required: bool  # Whether this is mandatory


class RepairRequest(Base):
    """Domain model for repair requests"""
    __tablename__ = "repair_requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    equipment_id = Column(String, nullable=False, index=True)
    character_id = Column(String, nullable=False, index=True)
    target_durability = Column(Float, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    estimated_time_hours = Column(Float, nullable=False)
    priority = Column(String, default="normal")
    status = Column(String, default=RepairStatus.PENDING.value)
    repairer_id = Column(String)
    requirements = Column(JSON, default=list)  # List of RepairRequirement dicts
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    actual_cost = Column(Float)
    
    def __init__(
        self,
        equipment_id: str,
        character_id: str,
        target_durability: float,
        estimated_cost: float,
        estimated_time_hours: float,
        priority: str = "normal",
        status: RepairStatus = RepairStatus.PENDING,
        repairer_id: Optional[str] = None,
        requirements: Optional[List[RepairRequirement]] = None,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        actual_cost: Optional[float] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.equipment_id = equipment_id
        self.character_id = character_id
        self.target_durability = target_durability
        self.estimated_cost = estimated_cost
        self.estimated_time_hours = estimated_time_hours
        self.priority = priority
        self.status = status.value if isinstance(status, RepairStatus) else status
        self.repairer_id = repairer_id
        self.requirements = [
            {
                "item_type": req.item_type,
                "item_id": req.item_id,
                "quantity": req.quantity,
                "required": req.required
            } for req in (requirements or [])
        ]
        self.created_at = created_at or datetime.utcnow()
        self.completed_at = completed_at
        self.actual_cost = actual_cost
    
    @property
    def status_enum(self) -> RepairStatus:
        """Get status as enum"""
        return RepairStatus(self.status)
    
    @status_enum.setter 
    def status_enum(self, value: RepairStatus):
        """Set status from enum"""
        self.status = value.value
    
    def __repr__(self):
        return f"<RepairRequest(id='{self.id}', equipment='{self.equipment_id}', status='{self.status}')>" 