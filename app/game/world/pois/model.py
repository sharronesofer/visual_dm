from typing import Dict, List, Optional, Tuple
import time
import math
from firebase_admin import db
from .schema import POISchema
from .types import POIType

class POI:
    """Point of Interest (POI) model class."""
    
    def __init__(self, data: Dict):
        """Initialize a POI instance."""
        self.schema = POISchema()
        validated_data = self.schema.load(data)
        
        # Required fields
        self.id = validated_data['id']
        self.name = validated_data['name']
        self.description = validated_data['description']
        self.type = validated_data['type']
        self.region_id = validated_data['region_id']
        self.x = validated_data['x']
        self.y = validated_data['y']
        self.z = validated_data['z']
        
        # Optional fields
        self.level_range = validated_data.get('level_range')
        self.faction_id = validated_data.get('faction_id')
        self.owner_id = validated_data.get('owner_id')
        
        # State flags
        self.is_discovered = validated_data.get('is_discovered', False)
        self.is_public = validated_data.get('is_public', True)
        
        # Timestamps
        self.created_at = validated_data.get('created_at', int(time.time()))
        self.updated_at = validated_data.get('updated_at', int(time.time()))
    
    @classmethod
    def create(cls, data: Dict) -> 'POI':
        """Create a new POI in the database."""
        if 'id' not in data:
            data['id'] = db.reference('pois').push().key
        data['created_at'] = int(time.time())
        data['updated_at'] = int(time.time())
        
        poi = cls(data)
        db.reference(f'pois/{poi.id}').set(poi.to_dict())
        return poi
    
    @classmethod
    def get(cls, poi_id: str) -> Optional['POI']:
        """Retrieve a POI by ID."""
        data = db.reference(f'pois/{poi_id}').get()
        return cls(data) if data else None
    
    @classmethod
    def list_all(cls) -> List['POI']:
        """List all POIs."""
        data = db.reference('pois').get() or {}
        return [cls(poi_data) for poi_data in data.values()]
    
    @classmethod
    def find_by_type(cls, poi_type: POIType) -> List['POI']:
        """Find POIs by type."""
        all_pois = cls.list_all()
        return [poi for poi in all_pois if poi.type == poi_type.value]
    
    @classmethod
    def find_in_region(cls, region_id: str) -> List['POI']:
        """Find POIs in a specific region."""
        all_pois = cls.list_all()
        return [poi for poi in all_pois if poi.region_id == region_id]
    
    def update(self, data: Dict) -> None:
        """Update POI attributes."""
        data['id'] = self.id  # Ensure ID remains unchanged
        data['updated_at'] = int(time.time())
        
        validated_data = self.schema.load(data)
        for key, value in validated_data.items():
            setattr(self, key, value)
        
        db.reference(f'pois/{self.id}').update(self.to_dict())
    
    def delete(self) -> None:
        """Delete the POI from the database."""
        db.reference(f'pois/{self.id}').delete()
    
    def calculate_distance(self, other_poi: 'POI') -> float:
        """Calculate 3D distance to another POI."""
        return math.sqrt(
            (self.x - other_poi.x) ** 2 +
            (self.y - other_poi.y) ** 2 +
            (self.z - other_poi.z) ** 2
        )
    
    def find_nearby(self, radius: float) -> List['POI']:
        """Find POIs within a specified radius."""
        all_pois = self.list_all()
        return [
            poi for poi in all_pois
            if poi.id != self.id and self.calculate_distance(poi) <= radius
        ]
    
    def get_coordinates(self) -> Tuple[float, float, float]:
        """Get POI coordinates as a tuple."""
        return (self.x, self.y, self.z)
    
    def to_dict(self) -> Dict:
        """Convert POI instance to dictionary."""
        return self.schema.dump(self)
    
    def __repr__(self) -> str:
        return f"<POI {self.name} ({self.type}) at ({self.x}, {self.y}, {self.z})>"
    
    @classmethod
    def search(cls, query: str, region_id: Optional[str] = None) -> List['POI']:
        """
        Search for POIs by name.
        
        Args:
            query: Search query string
            region_id: Optional region ID to filter results
            
        Returns:
            List[POI]: List of matching POI instances
        """
        # Note: This is a simple implementation. For production,
        # consider using a proper search index
        ref = db.reference('pois')
        if region_id:
            pois = ref.order_by_child('region_id').equal_to(region_id).get()
        else:
            pois = ref.get()
            
        if not pois:
            return []
            
        query = query.lower()
        return [
            cls(data) for data in pois.values()
            if query in data['name'].lower() or query in data.get('description', '').lower()
        ] 