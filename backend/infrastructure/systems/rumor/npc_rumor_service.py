"""
NPC Rumor Infrastructure Service
Handles database operations and technical infrastructure for NPC rumor system.
Implements the NPCDataRepository protocol from the business layer.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Database and infrastructure imports
from sqlalchemy.orm import Session
from backend.infrastructure.database.session import get_db
# Note: Rumor system works with entity IDs, doesn't need direct model dependencies

# Business layer imports
from backend.systems.rumor.utils.npc_rumor_utils import (
    NPCMemoryEntry, 
    NPCData, 
    NPCDataRepository
)

logger = logging.getLogger(__name__)

class NPCRumorDatabaseService(NPCDataRepository):
    """
    Technical infrastructure service for NPC rumor operations.
    Implements database operations and external service integrations.
    
    Note: This service works with entity IDs and doesn't require 
    direct NPC/Faction model dependencies, maintaining loose coupling.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        if db_session:
            self.db_session = db_session
        else:
            # Get database session from generator
            self.db_session = next(get_db())
        self._cache = {}  # Simple in-memory cache
    
    def get_memory_log(self, npc_id: str) -> List[NPCMemoryEntry]:
        """Get memory log for an NPC from database."""
        try:
            # TODO: Replace with actual database query
            # This is a placeholder implementation
            cache_key = f"npc_memory/{npc_id.lower()}/rag_log"
            if cache_key in self._cache:
                raw_data = self._cache[cache_key]
            else:
                # Query database for NPC memory log
                raw_data = []
                logger.debug(f"Retrieved memory log for NPC {npc_id}")
            
            # Convert raw data to NPCMemoryEntry objects
            return [
                NPCMemoryEntry(
                    interaction=entry.get("interaction", ""),
                    timestamp=entry.get("timestamp", datetime.utcnow().isoformat()),
                    credibility=entry.get("credibility")
                )
                for entry in raw_data
            ]
        except Exception as e:
            logger.error(f"Error retrieving memory log for NPC {npc_id}: {e}")
            return []
    
    def set_memory_log(self, npc_id: str, memory_log: List[NPCMemoryEntry]) -> None:
        """Set memory log for an NPC in database."""
        try:
            # Convert NPCMemoryEntry objects to raw data
            raw_data = [
                {
                    "interaction": entry.interaction,
                    "timestamp": entry.timestamp,
                    "credibility": entry.credibility
                }
                for entry in memory_log
            ]
            
            # TODO: Replace with actual database update
            cache_key = f"npc_memory/{npc_id.lower()}/rag_log"
            self._cache[cache_key] = raw_data
            
            logger.debug(f"Updated memory log for NPC {npc_id} with {len(memory_log)} entries")
        except Exception as e:
            logger.error(f"Error updating memory log for NPC {npc_id}: {e}")
    
    def get_npc_knowledge(self, npc_id: str, section: Optional[str] = None) -> Dict[str, Any]:
        """Get NPC knowledge data from database."""
        try:
            # TODO: Replace with actual database query
            cache_key = f"npc_knowledge/{npc_id}" + (f"/{section}" if section else "")
            knowledge = self._cache.get(cache_key, {})
            
            logger.debug(f"Retrieved knowledge for NPC {npc_id}, section: {section}")
            return knowledge
        except Exception as e:
            logger.error(f"Error retrieving knowledge for NPC {npc_id}: {e}")
            return {}
    
    def set_npc_knowledge(self, npc_id: str, data: Dict[str, Any], section: Optional[str] = None) -> None:
        """Set NPC knowledge data in database."""
        try:
            # TODO: Replace with actual database update
            cache_key = f"npc_knowledge/{npc_id}" + (f"/{section}" if section else "")
            self._cache[cache_key] = data
            
            logger.debug(f"Updated knowledge for NPC {npc_id}, section: {section}")
        except Exception as e:
            logger.error(f"Error updating knowledge for NPC {npc_id}: {e}")
    
    def get_npc_data(self, npc_id: Optional[str] = None) -> Dict[str, NPCData]:
        """Get NPC data from database."""
        try:
            if npc_id:
                # Get specific NPC
                # TODO: Replace with actual database query
                raw_data = self._cache.get(f"npcs/{npc_id}", {})
                if raw_data:
                    return {
                        npc_id: NPCData(
                            npc_id=npc_id,
                            region_id=raw_data.get("region_id"),
                            current_poi=raw_data.get("mobility", {}).get("current_poi"),
                            relationships=raw_data.get("relationships")
                        )
                    }
                return {}
            else:
                # Get all NPCs
                # TODO: Replace with actual database query
                all_npcs = self._cache.get("npcs", {})
                result = {}
                for npc_id, raw_data in all_npcs.items():
                    result[npc_id] = NPCData(
                        npc_id=npc_id,
                        region_id=raw_data.get("region_id"),
                        current_poi=raw_data.get("mobility", {}).get("current_poi"),
                        relationships=raw_data.get("relationships")
                    )
                return result
        except Exception as e:
            logger.error(f"Error retrieving NPC data: {e}")
            return {}
    
    def get_faction_data(self) -> Dict[str, Any]:
        """Get faction data from database."""
        try:
            # TODO: Replace with actual database query
            factions = self._cache.get("factions", {})
            logger.debug(f"Retrieved {len(factions)} factions")
            return factions
        except Exception as e:
            logger.error(f"Error retrieving faction data: {e}")
            return {}
    
    def get_opinion_matrix(self, npc_a: str, npc_b: Optional[str] = None) -> Any:
        """Get opinion matrix data from database."""
        try:
            # TODO: Replace with actual database query
            cache_key = f"npc_opinion_matrix/{npc_a}" + (f"/{npc_b}" if npc_b else "")
            result = self._cache.get(cache_key, 0 if npc_b else {})
            
            logger.debug(f"Retrieved opinion matrix for {npc_a}" + (f" -> {npc_b}" if npc_b else ""))
            return result
        except Exception as e:
            logger.error(f"Error retrieving opinion matrix: {e}")
            return 0 if npc_b else {}
    
    def set_opinion_matrix(self, npc_a: str, data: Any, npc_b: Optional[str] = None) -> None:
        """Set opinion matrix data in database."""
        try:
            # TODO: Replace with actual database update
            cache_key = f"npc_opinion_matrix/{npc_a}" + (f"/{npc_b}" if npc_b else "")
            self._cache[cache_key] = data
            
            logger.debug(f"Updated opinion matrix for {npc_a}" + (f" -> {npc_b}" if npc_b else ""))
        except Exception as e:
            logger.error(f"Error updating opinion matrix: {e}")
    
    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()
        logger.debug("Cleared NPC rumor service cache")
    
    def close(self) -> None:
        """Close database connections and cleanup resources."""
        if self.db_session:
            self.db_session.close()
        self.clear_cache()
        logger.debug("Closed NPC rumor database service")

# Legacy database interface for backward compatibility
class DatabaseInterface:
    """Legacy database interface for backward compatibility."""
    
    def __init__(self):
        self._service = NPCRumorDatabaseService()
    
    def get_memory_log(self, npc_id: str) -> List[Dict[str, Any]]:
        """Get memory log for an NPC (legacy format)."""
        entries = self._service.get_memory_log(npc_id)
        return [
            {
                "interaction": entry.interaction,
                "timestamp": entry.timestamp,
                "credibility": entry.credibility
            }
            for entry in entries
        ]
    
    def set_memory_log(self, npc_id: str, memory_log: List[Dict[str, Any]]):
        """Set memory log for an NPC (legacy format)."""
        entries = [
            NPCMemoryEntry(
                interaction=entry.get("interaction", ""),
                timestamp=entry.get("timestamp", datetime.utcnow().isoformat()),
                credibility=entry.get("credibility")
            )
            for entry in memory_log
        ]
        self._service.set_memory_log(npc_id, entries)
    
    def get_npc_knowledge(self, npc_id: str, section: str = None) -> Dict[str, Any]:
        """Get NPC knowledge data (legacy format)."""
        return self._service.get_npc_knowledge(npc_id, section)
    
    def set_npc_knowledge(self, npc_id: str, data: Dict[str, Any], section: str = None):
        """Set NPC knowledge data (legacy format)."""
        self._service.set_npc_knowledge(npc_id, data, section)
    
    def get_npc_data(self, npc_id: str = None) -> Dict[str, Any]:
        """Get NPC data (legacy format)."""
        npc_data = self._service.get_npc_data(npc_id)
        if npc_id and npc_id in npc_data:
            npc = npc_data[npc_id]
            return {
                "region_id": npc.region_id,
                "mobility": {"current_poi": npc.current_poi},
                "relationships": npc.relationships or {}
            }
        elif not npc_id:
            result = {}
            for npc_id, npc in npc_data.items():
                result[npc_id] = {
                    "region_id": npc.region_id,
                    "mobility": {"current_poi": npc.current_poi},
                    "relationships": npc.relationships or {}
                }
            return result
        return {}
    
    def get_faction_data(self) -> Dict[str, Any]:
        """Get faction data (legacy format)."""
        return self._service.get_faction_data()
    
    def get_opinion_matrix(self, npc_a: str, npc_b: str = None) -> Any:
        """Get opinion matrix data (legacy format)."""
        return self._service.get_opinion_matrix(npc_a, npc_b)
    
    def set_opinion_matrix(self, npc_a: str, data: Any, npc_b: str = None):
        """Set opinion matrix data (legacy format)."""
        self._service.set_opinion_matrix(npc_a, data, npc_b) 