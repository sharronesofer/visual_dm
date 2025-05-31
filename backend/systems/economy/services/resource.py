"""Resource management module."""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class ResourceData:
    """
    Data model for a resource.
    
    Resources represent tradeable goods and materials in the economy system.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = ""
    value: float = 0.0
    quantity: int = 0
    amount: float = 0.0  # For fractional amounts
    region_id: str = ""
    rarity: str = "common"  # common, uncommon, rare, legendary
    description: str = ""
    base_price: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def dict(self):
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "value": self.value,
            "quantity": self.quantity,
            "amount": self.amount,
            "region_id": self.region_id,
            "rarity": self.rarity,
            "description": self.description,
            "base_price": self.base_price,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "metadata": self.metadata
        }

@dataclass
class Resource:
    """Resource data model."""
    id: str
    name: str
    type: str
    value: float = 0.0
    quantity: int = 0
    amount: float = 0.0  # For compatibility with services
    region_id: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'quantity': self.quantity,
            'amount': self.amount,
            'region_id': self.region_id
        }

class ResourceManager:
    """Manages game resources."""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
    
    def add_resource(self, resource: Resource) -> None:
        """Add a resource."""
        self.resources[resource.id] = resource
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID."""
        return self.resources.get(resource_id)
    
    def list_resources(self) -> List[Resource]:
        """List all resources."""
        return list(self.resources.values())

# Export main classes
__all__ = ['Resource', 'ResourceData', 'ResourceManager']
