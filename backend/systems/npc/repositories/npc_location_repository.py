"""
NPC Location Repository

Specialized repository for NPC location and movement operations.
Handles location updates, movement history, and travel pattern analysis.
"""

from typing import List, Dict, Any, Tuple, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import logging

# Use canonical imports instead of dynamic loading
from backend.systems.npc.models import NpcEntity, NpcLocationHistory
from backend.infrastructure.shared.exceptions import NpcNotFoundError

logger = logging.getLogger(__name__)


class NPCLocationRepository:
    """Specialized repository for NPC location and movement operations"""
    
    def __init__(self, db_session: Session):
        """Initialize with database session"""
        self.db = db_session
    
    def update_npc_location(self, npc_id: UUID, new_region: str, new_location: str, 
                           travel_motive: str = "wander", activity: str = None) -> bool:
        """Update NPC location and record movement history"""
        try:
            # Get the NPC
            npc = self.db.query(NpcEntity).filter(
                NpcEntity.id == npc_id,
                NpcEntity.is_active == True
            ).first()
            
            if not npc:
                raise NpcNotFoundError(f"NPC {npc_id} not found")
            
            # Record the previous location if different
            if npc.location != new_location or npc.region_id != new_region:
                # Close previous location history entry if exists
                if npc.location:
                    previous_entry = self.db.query(NpcLocationHistory).filter(
                        NpcLocationHistory.npc_id == npc_id,
                        NpcLocationHistory.departure_time.is_(None)
                    ).first()
                    
                    if previous_entry:
                        previous_entry.departure_time = datetime.utcnow()
                
                # Create new location history entry
                location_entry = NpcLocationHistory(
                    npc_id=npc_id,
                    region_id=new_region,
                    location=new_location,
                    arrival_time=datetime.utcnow(),
                    travel_motive=travel_motive,
                    activity=activity
                )
                self.db.add(location_entry)
                
                # Update NPC current location
                npc.region_id = new_region
                npc.location = new_location
                
                self.db.commit()
                logger.info(f"Updated NPC {npc_id} location to {new_location} in region {new_region}")
                return True
            
            return False  # No change in location
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating location for NPC {npc_id}: {str(e)}")
            raise
    
    def get_npc_location_history(self, npc_id: UUID, days: int = 30) -> List[NpcLocationHistory]:
        """Get NPC location history for the last N days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return self.db.query(NpcLocationHistory).filter(
                NpcLocationHistory.npc_id == npc_id,
                NpcLocationHistory.arrival_time >= cutoff_date
            ).order_by(desc(NpcLocationHistory.arrival_time)).all()
        except Exception as e:
            logger.error(f"Error getting location history for NPC {npc_id}: {str(e)}")
            raise
    
    def get_npcs_in_region(self, region_id: str, include_inactive: bool = False) -> List[NpcEntity]:
        """Get all NPCs currently in a specific region"""
        try:
            query = self.db.query(NpcEntity).filter(
                NpcEntity.region_id == region_id
            )
            
            if not include_inactive:
                query = query.filter(NpcEntity.is_active == True)
            
            return query.all()
        except Exception as e:
            logger.error(f"Error getting NPCs in region {region_id}: {str(e)}")
            raise
    
    def get_npcs_at_location(self, region_id: str, location: str, include_inactive: bool = False) -> List[NpcEntity]:
        """Get all NPCs at a specific location"""
        try:
            query = self.db.query(NpcEntity).filter(
                NpcEntity.region_id == region_id,
                NpcEntity.location == location
            )
            
            if not include_inactive:
                query = query.filter(NpcEntity.is_active == True)
            
            return query.all()
        except Exception as e:
            logger.error(f"Error getting NPCs at location {location}: {str(e)}")
            raise
    
    def get_npcs_with_travel_motive(self, motive: str, region_id: str = None) -> List[Tuple[NpcEntity, NpcLocationHistory]]:
        """Get NPCs who have traveled with a specific motive"""
        try:
            query = self.db.query(NpcEntity, NpcLocationHistory).join(
                NpcLocationHistory, NpcEntity.id == NpcLocationHistory.npc_id
            ).filter(
                NpcLocationHistory.travel_motive == motive,
                NpcEntity.is_active == True
            )
            
            if region_id:
                query = query.filter(NpcLocationHistory.region_id == region_id)
            
            return query.order_by(desc(NpcLocationHistory.arrival_time)).all()
        except Exception as e:
            logger.error(f"Error getting NPCs with motive {motive}: {str(e)}")
            raise
    
    def get_location_popularity_stats(self, region_id: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get statistics on location popularity (where NPCs visit most)"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = self.db.query(
                NpcLocationHistory.location,
                NpcLocationHistory.region_id,
                func.count(NpcLocationHistory.id).label('visit_count'),
                func.count(func.distinct(NpcLocationHistory.npc_id)).label('unique_npcs')
            ).filter(
                NpcLocationHistory.arrival_time >= cutoff_date
            )
            
            if region_id:
                query = query.filter(NpcLocationHistory.region_id == region_id)
            
            results = query.group_by(
                NpcLocationHistory.location,
                NpcLocationHistory.region_id
            ).order_by(desc('visit_count')).all()
            
            return [
                {
                    "location": result.location,
                    "region_id": result.region_id,
                    "visit_count": result.visit_count,
                    "unique_npcs": result.unique_npcs
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error getting location popularity stats: {str(e)}")
            raise
    
    def get_npc_travel_patterns(self, npc_id: UUID) -> Dict[str, Any]:
        """Analyze an NPC's travel patterns"""
        try:
            # Get all location history
            history = self.db.query(NpcLocationHistory).filter(
                NpcLocationHistory.npc_id == npc_id
            ).order_by(NpcLocationHistory.arrival_time).all()
            
            if not history:
                return {"error": "No travel history found"}
            
            # Calculate stats
            total_moves = len(history)
            regions_visited = len(set(entry.region_id for entry in history))
            locations_visited = len(set(f"{entry.region_id}_{entry.location}" for entry in history))
            
            # Most frequent motive
            motives = [entry.travel_motive for entry in history if entry.travel_motive]
            most_common_motive = max(set(motives), key=motives.count) if motives else None
            
            # Average stay duration (for completed stays)
            completed_stays = [
                entry for entry in history 
                if entry.departure_time is not None
            ]
            
            if completed_stays:
                durations = [
                    (entry.departure_time - entry.arrival_time).total_seconds() / 3600  # hours
                    for entry in completed_stays
                ]
                avg_stay_hours = sum(durations) / len(durations)
            else:
                avg_stay_hours = 0
            
            # Current location info
            current_entry = max(history, key=lambda x: x.arrival_time)
            current_stay_hours = (datetime.utcnow() - current_entry.arrival_time).total_seconds() / 3600
            
            return {
                "total_moves": total_moves,
                "regions_visited": regions_visited,
                "locations_visited": locations_visited,
                "most_common_motive": most_common_motive,
                "average_stay_hours": round(avg_stay_hours, 2),
                "current_location": f"{current_entry.region_id}_{current_entry.location}",
                "current_stay_hours": round(current_stay_hours, 2),
                "current_activity": current_entry.activity,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing travel patterns for NPC {npc_id}: {str(e)}")
            raise
    
    def find_npcs_near_location(self, region_id: str, target_location: str, radius: int = 1) -> List[Tuple[NpcEntity, float]]:
        """Find NPCs within a certain radius of a target location"""
        try:
            # Parse target coordinates
            try:
                target_x, target_y = map(int, target_location.split('_'))
            except ValueError:
                raise ValueError(f"Invalid location format: {target_location}")
            
            # Get all NPCs in the region
            npcs = self.db.query(NpcEntity).filter(
                NpcEntity.region_id == region_id,
                NpcEntity.is_active == True,
                NpcEntity.location.isnot(None)
            ).all()
            
            nearby_npcs = []
            
            for npc in npcs:
                try:
                    npc_x, npc_y = map(int, npc.location.split('_'))
                    distance = ((npc_x - target_x) ** 2 + (npc_y - target_y) ** 2) ** 0.5
                    
                    if distance <= radius:
                        nearby_npcs.append((npc, distance))
                except (ValueError, AttributeError):
                    # Skip NPCs with invalid location format
                    continue
            
            # Sort by distance
            nearby_npcs.sort(key=lambda x: x[1])
            return nearby_npcs
            
        except Exception as e:
            logger.error(f"Error finding NPCs near {target_location}: {str(e)}")
            raise
    
    def get_movement_summary_by_region(self, days: int = 7) -> Dict[str, Dict[str, int]]:
        """Get a summary of NPC movements by region for the last N days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get movement data
            movements = self.db.query(
                NpcLocationHistory.region_id,
                NpcLocationHistory.travel_motive,
                func.count(NpcLocationHistory.id).label('count')
            ).filter(
                NpcLocationHistory.arrival_time >= cutoff_date
            ).group_by(
                NpcLocationHistory.region_id,
                NpcLocationHistory.travel_motive
            ).all()
            
            # Organize by region
            summary = {}
            for movement in movements:
                region = movement.region_id
                motive = movement.travel_motive or "unknown"
                count = movement.count
                
                if region not in summary:
                    summary[region] = {}
                
                summary[region][motive] = count
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting movement summary: {str(e)}")
            raise
    
    def schedule_npc_migration(self, source_region: str, target_region: str, 
                              npc_ids: List[UUID] = None, migration_reason: str = None) -> Dict[str, Any]:
        """Schedule migration of NPCs between regions"""
        try:
            # If no specific NPCs provided, get some candidates
            if not npc_ids:
                candidates = self.db.query(NpcEntity).filter(
                    NpcEntity.region_id == source_region,
                    NpcEntity.is_active == True
                ).limit(5).all()  # Migrate up to 5 NPCs
                npc_ids = [npc.id for npc in candidates]
            
            migration_results = []
            
            for npc_id in npc_ids:
                try:
                    # Update location with migration reason
                    success = self.update_npc_location(
                        npc_id=npc_id,
                        new_region=target_region,
                        new_location="0_0",  # Default central location in new region
                        travel_motive="migration",
                        activity=f"Migrated from {source_region}: {migration_reason or 'Unknown reason'}"
                    )
                    
                    migration_results.append({
                        "npc_id": str(npc_id),
                        "success": success,
                        "new_location": f"{target_region}_0_0"
                    })
                    
                except Exception as e:
                    logger.error(f"Error migrating NPC {npc_id}: {str(e)}")
                    migration_results.append({
                        "npc_id": str(npc_id),
                        "success": False,
                        "error": str(e)
                    })
            
            successful_migrations = sum(1 for result in migration_results if result["success"])
            
            return {
                "source_region": source_region,
                "target_region": target_region,
                "migration_reason": migration_reason,
                "total_npcs": len(npc_ids),
                "successful_migrations": successful_migrations,
                "migration_results": migration_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scheduling migration from {source_region} to {target_region}: {str(e)}")
            raise 