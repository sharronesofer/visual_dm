"""
Utilities for building and managing Points of Interest (POIs).
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import random
import uuid

from app.core.utils.firebase_utils import (
    get_firestore_client,
    get_document,
    set_document,
    update_document,
    get_collection
)
from app.core.utils.error_utils import ValidationError, NotFoundError, DatabaseError
from app.core.utils.logging_utils import logger

def build_poi(region_id: str, poi_type: str, owner_id: Optional[str] = None) -> Dict[str, Any]:
    """Build a new Point of Interest in a region."""
    try:
        poi_data = {
            'id': str(uuid.uuid4()),
            'region_id': region_id,
            'type': poi_type,
            'owner_id': owner_id,
            'state': 'new',
            'value': calculate_poi_value(poi_type),
            'resources': {},
            'last_updated': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
        
        set_document('pois', poi_data['id'], poi_data)
        logger.info(f"Built new POI {poi_data['id']} of type {poi_type} in region {region_id}")
        return poi_data
    except Exception as e:
        logger.error(f"Error building POI: {str(e)}")
        raise DatabaseError(f"Failed to build POI: {str(e)}")

def update_poi_state(poi_id: str, new_state: str, owner_id: Optional[str] = None) -> bool:
    """Update the state of a Point of Interest."""
    try:
        poi_data = get_document('pois', poi_id)
        if not poi_data:
            raise NotFoundError(f"POI {poi_id} not found")
            
        updates = {
            'state': new_state,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        if owner_id is not None:
            updates['owner_id'] = owner_id
            
        update_document('pois', poi_id, updates)
        logger.info(f"Updated POI {poi_id} state to {new_state}")
        return True
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error updating POI state: {str(e)}")
        raise DatabaseError(f"Failed to update POI state: {str(e)}")

def calculate_poi_value(poi_type: str) -> float:
    """Calculate the value of a Point of Interest based on its type."""
    try:
        base_values = {
            'mine': 100.0,
            'farm': 75.0,
            'tavern': 50.0,
            'shop': 60.0,
            'temple': 80.0,
            'guild': 90.0,
            'fortress': 120.0
        }
        
        base_value = base_values.get(poi_type, 50.0)
        variation = random.uniform(0.8, 1.2)  # +/- 20% random variation
        
        return round(base_value * variation, 2)
    except Exception as e:
        logger.error(f"Error calculating POI value: {str(e)}")
        raise DatabaseError(f"Failed to calculate POI value: {str(e)}")

def npc_reclaim_pois(npc_id: str) -> List[Dict[str, Any]]:
    """Handle NPCs reclaiming abandoned POIs."""
    try:
        npc_data = get_document('npcs', npc_id)
        if not npc_data:
            raise NotFoundError(f"NPC {npc_id} not found")
            
        # Get abandoned POIs in NPC's region
        region_id = npc_data.get('region_id')
        pois = get_collection('pois')
        abandoned_pois = [
            poi for poi in pois
            if poi.get('region_id') == region_id and
            poi.get('state') == 'abandoned'
        ]
        
        reclaimed_pois = []
        for poi in abandoned_pois:
            # NPCs have a 20% chance to reclaim each abandoned POI
            if random.random() < 0.2:
                update_poi_state(poi['id'], 'active', npc_id)
                reclaimed_pois.append(poi)
                logger.info(f"NPC {npc_id} reclaimed POI {poi['id']}")
                
        return reclaimed_pois
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error in NPC POI reclamation: {str(e)}")
        raise DatabaseError(f"Failed in NPC POI reclamation: {str(e)}")

__all__ = [
    'build_poi',
    'update_poi_state',
    'calculate_poi_value',
    'npc_reclaim_pois'
] 