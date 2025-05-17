"""
NPC travel and location management.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import db
from app.core.models.npc import NPC
from app.core.models.world import Region

class NPCTravel:
    """Handles NPC travel and location management."""
    
    def __init__(self, session: Session = None):
        self.session = session or db.session
        
    def get_current_location(self, npc_id: int) -> Optional[Region]:
        """Get an NPC's current location."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc:
            return None
        return npc.region
        
    def travel_to_region(self, npc_id: int, target_region_id: int) -> bool:
        """Move an NPC to a new region."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc:
            return False
            
        # Check if NPC can travel (e.g., not in combat, not imprisoned)
        if npc.status != "active":
            return False
            
        # Update NPC's location
        npc.region_id = target_region_id
        npc.last_travel = datetime.utcnow()
        
        self.session.commit()
        return True
        
    def get_nearby_npcs(self, npc_id: int, radius: int = 1) -> list:
        """Get NPCs in nearby regions."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc or not npc.region_id:
            return []
            
        # Get current region and connected regions
        current_region = self.session.query(Region).get(npc.region_id)
        if not current_region:
            return []
            
        # Get all regions within radius
        nearby_regions = self._get_regions_within_radius(current_region, radius)
        
        # Get NPCs in these regions
        nearby_npcs = []
        for region in nearby_regions:
            region_npcs = self.session.query(NPC).filter(
                NPC.region_id == region.id,
                NPC.id != npc_id
            ).all()
            nearby_npcs.extend(region_npcs)
            
        return nearby_npcs
        
    def _get_regions_within_radius(self, region: Region, radius: int) -> list:
        """Get all regions within a certain radius of the given region."""
        if radius <= 0:
            return [region]
            
        regions = [region]
        visited = {region.id}
        
        for _ in range(radius):
            new_regions = []
            for current_region in regions:
                # Get connected regions (you'll need to implement this based on your region model)
                connected_regions = self._get_connected_regions(current_region)
                for connected in connected_regions:
                    if connected.id not in visited:
                        visited.add(connected.id)
                        new_regions.append(connected)
            regions.extend(new_regions)
            
        return regions
        
    def _get_connected_regions(self, region: Region) -> list:
        """Get regions directly connected to the given region."""
        # This is a placeholder - implement based on your region model
        # For example, if regions have a 'connections' relationship:
        return region.connections if hasattr(region, 'connections') else [] 