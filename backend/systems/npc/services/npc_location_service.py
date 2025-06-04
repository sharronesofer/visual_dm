"""
NPC Location Service
------------------
Service for managing NPC locations, movement, and travel.
"""
import random
import math
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.infrastructure.systems.npc.models.models import NpcEntity
from backend.infrastructure.database import get_db
from backend.systems.npc.config import get_npc_config

class NpcLocationService:
    """Service for managing NPC locations and movement."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the NPC location service.
        
        Args:
            db_session: Optional database session
        """
        self.db = db_session if db_session else next(get_db())
        self._is_external_session = db_session is not None
        self.config = get_npc_config()
        
    def __del__(self):
        """Clean up database session if we created it"""
        if not self._is_external_session and hasattr(self, 'db'):
            try:
                self.db.close()
            except:
                pass
        
    def update_npc_location(self, npc_id: UUID) -> Dict[str, Any]:
        """
        Updates an NPC's location based on mobility parameters.
        
        Args:
            npc_id: UUID of the NPC to update
            
        Returns:
            Dictionary with update results including new location if moved
        """
        try:
            # Get NPC data from database
            npc = self._get_npc(npc_id)
            if not npc:
                return {"error": f"NPC {npc_id} not found."}

            # Parse NPC properties for location data
            properties = npc.properties or {}
            mobility = properties.get("mobility", {})
            home = mobility.get("home_poi")
            current = mobility.get("current_poi", home)
            radius = mobility.get("radius", 1)
            
            # Use travel configuration to determine travel chance
            travel_config = self.config.get_travel_behaviors_config()
            wanderlust = properties.get("wanderlust", 0)
            wanderlust_behavior = travel_config.get("wanderlust_behaviors", {}).get(str(wanderlust), {})
            travel_chance = wanderlust_behavior.get("travel_chance", 0.15)

            if not current or "_" not in current:
                return {"error": f"Invalid POI format for NPC {npc_id}: {current}"}

            # Random chance to stay in place
            if random.random() > travel_chance:
                return {"npc_id": str(npc_id), "stayed": True}

            # Get available POIs
            valid_pois = self._get_valid_pois_in_radius(current, radius)
            
            if not valid_pois:
                return {"npc_id": str(npc_id), "stayed": True, "reason": "No POIs in radius"}

            # Choose a new location and update
            new_location = random.choice(valid_pois)
            
            # Update NPC location in database
            mobility["current_poi"] = new_location
            mobility["last_moved"] = datetime.utcnow().isoformat()
            properties["mobility"] = mobility
            
            npc.properties = properties
            npc.updated_at = datetime.utcnow()
            self.db.commit()

            # Get travel motive for context
            motive = properties.get("travel_motive", "wander")
            
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
            
        except Exception as e:
            self.db.rollback()
            return {"error": f"Error updating NPC location: {str(e)}"}
    
    def _get_npc(self, npc_id: UUID) -> Optional[NpcEntity]:
        """
        Retrieves NPC data from the database.
        
        Args:
            npc_id: UUID of the NPC
            
        Returns:
            NPC entity or None if not found
        """
        try:
            return self.db.query(NpcEntity).filter(
                and_(
                    NpcEntity.id == npc_id,
                    NpcEntity.is_active == True
                )
            ).first()
        except Exception as e:
            return None
    
    def _get_valid_pois_in_radius(self, current_poi: str, radius: int) -> List[str]:
        """
        Gets valid POIs within the specified radius of the current location.
        
        Args:
            current_poi: Current POI coordinates (format: "x_y")
            radius: Maximum travel radius
            
        Returns:
            List of valid POI coordinates within radius
        """
        # In a full implementation, this would query from a locations/POI database
        # For now, we'll generate some sample POIs based on the coordinate system
        
        try:
            cx, cy = map(int, current_poi.split("_"))
        except:
            return []
            
        valid_pois = []
        
        # Generate POIs within radius - this would be replaced with actual POI data
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = cx + dx, cy + dy
                dist = math.sqrt(dx**2 + dy**2)
                
                if 0 < dist <= radius:
                    # In a real system, we'd check if this coordinate has an actual POI
                    valid_pois.append(f"{x}_{y}")
                    
        return valid_pois
    
    def _log_movement_to_memory(self, npc_id: UUID, new_location: str, motive: str) -> None:
        """
        Logs movement to NPC's memory system.
        
        Args:
            npc_id: UUID of the NPC
            new_location: New location coordinates
            motive: Travel motive
        """
        try:
            # Update NPC memory with movement record
            npc = self._get_npc(npc_id)
            if npc:
                properties = npc.properties or {}
                memory_summary = properties.get("memory_summary", "")
                
                # Add movement to memory
                movement_entry = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Moved to {new_location} (motive: {motive})"
                
                if memory_summary:
                    memory_summary += f"\n{movement_entry}"
                else:
                    memory_summary = movement_entry
                
                # Keep memory summary reasonable length (last 10 entries)
                memory_lines = memory_summary.split('\n')
                if len(memory_lines) > 10:
                    memory_summary = '\n'.join(memory_lines[-10:])
                
                properties["memory_summary"] = memory_summary
                npc.properties = properties
                npc.updated_at = datetime.utcnow()
                self.db.commit()
                
        except Exception as e:
            # Don't fail the whole operation if memory logging fails
            pass

    def _create_quest_hook(self, npc_id: UUID, motive: str, location: str) -> None:
        """
        Creates a potential quest hook based on NPC movement.
        
        Args:
            npc_id: UUID of the NPC
            motive: Travel motive
            location: Location coordinates
        """
        try:
            # Store quest hook information in NPC properties
            npc = self._get_npc(npc_id)
            if npc:
                properties = npc.properties or {}
                quest_hooks = properties.get("quest_hooks", [])
                
                # Create new quest hook
                quest_hook = {
                    "id": f"hook_{len(quest_hooks) + 1}",
                    "motive": motive,
                    "location": location,
                    "created_at": datetime.utcnow().isoformat(),
                    "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                    "active": True
                }
                
                quest_hooks.append(quest_hook)
                
                # Keep only active, non-expired hooks
                now = datetime.utcnow()
                quest_hooks = [
                    hook for hook in quest_hooks 
                    if hook.get("active", True) and 
                    datetime.fromisoformat(hook.get("expires_at", now.isoformat())) > now
                ]
                
                properties["quest_hooks"] = quest_hooks
                npc.properties = properties
                npc.updated_at = datetime.utcnow()
                self.db.commit()
                
        except Exception as e:
            # Don't fail the whole operation if quest hook creation fails
            pass

    def get_npcs_in_location(self, location: str) -> List[Dict[str, Any]]:
        """
        Get all NPCs currently at a specific location.
        
        Args:
            location: Location coordinates (format: "x_y")
            
        Returns:
            List of NPC data dictionaries
        """
        try:
            npcs = self.db.query(NpcEntity).filter(NpcEntity.is_active == True).all()
            
            npcs_at_location = []
            for npc in npcs:
                properties = npc.properties or {}
                mobility = properties.get("mobility", {})
                current_poi = mobility.get("current_poi")
                
                if current_poi == location:
                    npcs_at_location.append({
                        "id": str(npc.id),
                        "name": npc.name,
                        "description": npc.description,
                        "location": location,
                        "properties": properties
                    })
                    
            return npcs_at_location
            
        except Exception as e:
            return []

    def set_npc_home_location(self, npc_id: UUID, location: str) -> bool:
        """
        Set an NPC's home location.
        
        Args:
            npc_id: UUID of the NPC
            location: Home location coordinates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            npc = self._get_npc(npc_id)
            if not npc:
                return False
                
            properties = npc.properties or {}
            mobility = properties.get("mobility", {})
            mobility["home_poi"] = location
            
            # If NPC doesn't have a current location, set it to home
            if not mobility.get("current_poi"):
                mobility["current_poi"] = location
                
            properties["mobility"] = mobility
            npc.properties = properties
            npc.updated_at = datetime.utcnow()
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            return False
