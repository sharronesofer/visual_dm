"""
NPC Location Service
------------------
Service for managing NPC locations, movement, and travel.
"""
import random
import math
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

class NpcLocationService:
    """Service for managing NPC locations and movement."""
    
    def __init__(self, db_session=None):
        """
        Initialize the NPC location service.
        
        Args:
            db_session: Optional database session
        """
        self.db = db_session
        
    def update_npc_location(self, npc_id: UUID) -> Dict[str, Any]:
        """
        Updates an NPC's location based on mobility parameters.
        
        Args:
            npc_id: UUID of the NPC to update
            
        Returns:
            Dictionary with update results including new location if moved
            
        Note:
            This is a stub implementation. In a real scenario, this would interact with a database.
        """
        # Get NPC data - in a real implementation, this would query from the database
        npc = self._get_npc(npc_id)
        if not npc:
            return {"error": f"NPC {npc_id} not found."}

        mobility = npc.get("mobility", {})
        home = mobility.get("home_poi")
        current = mobility.get("current_poi", home)
        radius = mobility.get("radius", 1)
        travel_chance = mobility.get("travel_chance", 0.15)

        if not current or "_" not in current:
            return {"error": f"Invalid POI format for NPC {npc_id}: {current}"}

        # Random chance to stay in place
        if random.random() > travel_chance:
            return {"npc_id": str(npc_id), "stayed": True}

        # Get available POIs - in a real implementation, this would query from the database
        valid_pois = self._get_valid_pois_in_radius(current, radius)
        
        if not valid_pois:
            return {"npc_id": str(npc_id), "stayed": True, "reason": "No POIs in radius"}

        # Choose a new location and update
        new_location = random.choice(valid_pois)
        
        # Update NPC location
        npc["mobility"]["current_poi"] = new_location
        npc["mobility"]["last_moved"] = datetime.utcnow().isoformat()
        self._update_npc(npc_id, npc)

        # Get travel motive for context
        motive = npc.get("travel_motive", "wander")
        
        # Log the movement to NPC memory
        self._log_movement_to_memory(npc_id, new_location, motive)
        
        # Check for special motives that trigger quest hooks
        if motive in ["seek_revenge", "hunt_monster", "find_relic"]:
            self._create_quest_hook(npc_id, motive, new_location)

        return {
            "npc_id": str(npc_id), 
            "moved_to": new_location, 
            "motive": motive
        }
    
    def _get_npc(self, npc_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieves NPC data from storage.
        
        Args:
            npc_id: UUID of the NPC
            
        Returns:
            NPC data dictionary or None if not found
        """
        # In a real implementation, this would query the database
        # Example:
        # return self.db.query(NPCModel).filter(NPCModel.id == npc_id).first()
        
        # Placeholder implementation
        return {
            "id": str(npc_id),
            "character_name": f"NPC-{npc_id}",
            "mobility": {
                "home_poi": "5_7",
                "current_poi": "5_7",
                "radius": 2,
                "travel_chance": 0.15
            },
            "travel_motive": "wander"
        }
    
    def _update_npc(self, npc_id: UUID, npc_data: Dict[str, Any]) -> None:
        """
        Updates NPC data in storage.
        
        Args:
            npc_id: UUID of the NPC
            npc_data: Updated NPC data
        """
        # In a real implementation, this would update the database
        # Example:
        # self.db.query(NPCModel).filter(NPCModel.id == npc_id).update(npc_data)
        # self.db.commit()
        pass
    
    def _get_valid_pois_in_radius(self, current_poi: str, radius: int) -> List[str]:
        """
        Gets valid POIs within the specified radius of the current location.
        
        Args:
            current_poi: Current POI coordinates (format: "x_y")
            radius: Maximum travel radius
            
        Returns:
            List of valid POI coordinates within radius
        """
        # In a real implementation, this would query from a locations database
        # For now, we'll generate some sample POIs
        
        try:
            cx, cy = map(int, current_poi.split("_"))
        except:
            return []
            
        valid_pois = []
        
        # Generate some sample POIs within radius
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = cx + dx, cy + dy
                dist = math.sqrt(dx**2 + dy**2)
                
                if 0 < dist <= radius:
                    valid_pois.append(f"{x}_{y}")
                    
        return valid_pois
    
    def _log_movement_to_memory(self, npc_id: UUID, new_location: str, motive: str) -> None:
        """
        Logs movement to NPC's memory.
        
        Args:
            npc_id: UUID of the NPC
            new_location: New location coordinates
            motive: Travel motive
        """
        # In a real implementation, this would interact with the memory system
        # Example:
        # memory_service.add_memory(
        #     entity_id=npc_id,
        #     text=f"Moved to {new_location} due to motive: {motive}",
        #     type="MOVEMENT",
        #     relevance=0.5
        # )
        pass
    
    def _create_quest_hook(self, npc_id: UUID, motive: str, location: str) -> None:
        """
        Creates a potential quest hook based on NPC movement.
        
        Args:
            npc_id: UUID of the NPC
            motive: Travel motive
            location: Location coordinates
        """
        # In a real implementation, this would create an entry in a quest hooks database
        # Example:
        # quest_hook_service.create_hook(
        #     npc_id=npc_id,
        #     motive=motive,
        #     location=location,
        #     expiration=datetime.utcnow() + timedelta(days=7)
        # )
        pass 