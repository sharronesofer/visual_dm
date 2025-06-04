"""
Inventory System Database Models

This module provides SQLAlchemy database models for the inventory system
according to the Development Bible infrastructure standards.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

# Import Base from the database module
from backend.infrastructure.database import Base
from backend.systems.inventory.models import InventoryType, InventoryStatus, EncumbranceLevel


class InventoryTypeEnum(enum.Enum):
    """SQLAlchemy enum for inventory types"""
    CHARACTER = "character"
    CONTAINER = "container"
    SHOP = "shop"
    BANK = "bank"
    QUEST = "quest"


class InventoryStatusEnum(enum.Enum):
    """SQLAlchemy enum for inventory status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ARCHIVED = "archived"
    CORRUPTED = "corrupted"


class InventoryEntity(Base):
    """Database entity for inventory system"""
    __tablename__ = "inventories"

    # Primary key and audit fields
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    metadata = Column(JSON, default=dict)

    # Core inventory fields
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    inventory_type = Column(SQLEnum(InventoryTypeEnum), nullable=False, default=InventoryTypeEnum.CHARACTER, index=True)
    status = Column(SQLEnum(InventoryStatusEnum), nullable=False, default=InventoryStatusEnum.ACTIVE, index=True)
    properties = Column(JSON, default=dict)

    # Ownership relationships
    owner_id = Column(PG_UUID(as_uuid=True), index=True)  # Character ID
    player_id = Column(PG_UUID(as_uuid=True), index=True)  # Player ID

    # Capacity management
    max_capacity = Column(Integer, nullable=False, default=50)
    max_weight = Column(Float)
    current_item_count = Column(Integer, nullable=False, default=0)
    current_weight = Column(Float, nullable=False, default=0.0)

    # Type-specific configurations
    allows_trading = Column(Boolean, default=True)
    allows_sorting = Column(Boolean, default=True)
    allows_filtering = Column(Boolean, default=True)
    default_sort = Column(String(50), default="name")
    available_filters = Column(JSON, default=list)

    # Database constraints and indexes
    __table_args__ = (
        # Unique constraint: one inventory name per owner
        # Note: This would be better as a partial index in PostgreSQL
        # INDEX (owner_id, name) WHERE owner_id IS NOT NULL
    )

    def to_business_model(self):
        """Convert database entity to business model"""
        from backend.systems.inventory.models import InventoryModel
        
        return InventoryModel(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            is_active=self.is_active,
            metadata=self.metadata or {},
            name=self.name,
            description=self.description,
            inventory_type=InventoryType(self.inventory_type.value),
            status=InventoryStatus(self.status.value),
            properties=self.properties or {},
            owner_id=self.owner_id,
            player_id=self.player_id,
            max_capacity=self.max_capacity,
            max_weight=self.max_weight,
            current_item_count=self.current_item_count,
            current_weight=self.current_weight,
            allows_trading=self.allows_trading,
            allows_sorting=self.allows_sorting,
            allows_filtering=self.allows_filtering,
            default_sort=self.default_sort,
            available_filters=self.available_filters or []
        )

    @classmethod
    def from_business_model(cls, model):
        """Create database entity from business model"""
        return cls(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active,
            metadata=model.metadata,
            name=model.name,
            description=model.description,
            inventory_type=InventoryTypeEnum(model.inventory_type.value),
            status=InventoryStatusEnum(model.status.value),
            properties=model.properties,
            owner_id=model.owner_id,
            player_id=model.player_id,
            max_capacity=model.max_capacity,
            max_weight=model.max_weight,
            current_item_count=model.current_item_count,
            current_weight=model.current_weight,
            allows_trading=model.allows_trading,
            allows_sorting=model.allows_sorting,
            allows_filtering=model.allows_filtering,
            default_sort=model.default_sort,
            available_filters=model.available_filters
        )

    def __repr__(self):
        return f"<InventoryEntity(id={self.id}, name='{self.name}', type={self.inventory_type.value})>"


class InventoryItemEntity(Base):
    """Database entity for items within inventories (for future item system integration)"""
    __tablename__ = "inventory_items"

    # Composite primary key: inventory_id + item_id + slot_position
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    inventory_id = Column(PG_UUID(as_uuid=True), ForeignKey("inventories.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)  # Reference to item system
    
    # Item placement
    slot_position = Column(Integer)  # Position in inventory (for ordered inventories)
    quantity = Column(Integer, nullable=False, default=1)
    
    # Cached item properties (for performance)
    item_weight = Column(Float, nullable=False, default=0.0)
    item_stack_size = Column(Integer, default=1)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Properties for item-specific data in this inventory context
    properties = Column(JSON, default=dict)

    # Relationship to inventory
    inventory = relationship("InventoryEntity", backref="items")

    __table_args__ = (
        # Ensure unique item placement in inventory
        # UNIQUE (inventory_id, item_id) for non-stackable items
        # UNIQUE (inventory_id, slot_position) for positioned inventories
    )

    def __repr__(self):
        return f"<InventoryItemEntity(inventory_id={self.inventory_id}, item_id={self.item_id}, quantity={self.quantity})>"


class InventoryAuditLogEntity(Base):
    """Database entity for inventory audit trail"""
    __tablename__ = "inventory_audit_logs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    inventory_id = Column(PG_UUID(as_uuid=True), ForeignKey("inventories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Audit information
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, ITEM_ADD, ITEM_REMOVE, etc.
    actor_id = Column(PG_UUID(as_uuid=True), index=True)  # Player/Character who performed action
    actor_type = Column(String(20), default="player")  # player, character, system, admin
    
    # Change details
    old_values = Column(JSON)
    new_values = Column(JSON)
    changes_summary = Column(Text)
    
    # Context
    session_id = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship to inventory
    inventory = relationship("InventoryEntity", backref="audit_logs")

    def __repr__(self):
        return f"<InventoryAuditLogEntity(action={self.action}, inventory_id={self.inventory_id}, timestamp={self.timestamp})>" 