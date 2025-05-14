"""
NPC relationship management system.
"""

from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.core.database import db
from app.core.models.npc import NPC

class NPCRelationships:
    """Handles NPC relationship management."""
    
    def __init__(self, session: Session):
        self.session = session
        
    def get_relationships(self, npc_id: int) -> Dict:
        """Get all relationships for an NPC."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc:
            return {}
        return npc.relationships or {}
        
    def get_relationship(self, npc_id: int, target_id: int) -> Optional[float]:
        """Get relationship value between two NPCs."""
        relationships = self.get_relationships(npc_id)
        return relationships.get(str(target_id), {}).get('value')
        
    def update_relationship(self, npc_id: int, target_id: int,
                          change: float, reason: str) -> None:
        """Update relationship between two NPCs."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc:
            return
            
        if not npc.relationships:
            npc.relationships = {}
            
        current_value = npc.relationships.get(str(target_id), {}).get('value', 0.0)
        new_value = max(-1.0, min(1.0, current_value + change))
        
        npc.relationships[str(target_id)] = {
            'value': new_value,
            'last_change': {
                'amount': change,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            },
            'updated_at': datetime.utcnow().isoformat()
        }
        
    def initialize_relationships(self, npc_id: int) -> None:
        """Initialize an NPC's relationships with other NPCs."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc:
            return
            
        # Get all other NPCs in the same region
        other_npcs = self.session.query(NPC).filter(
            NPC.id != npc_id,
            NPC.region_id == npc.region_id
        ).all()
        
        npc.relationships = {}
        for other_npc in other_npcs:
            # Initialize with neutral relationship
            npc.relationships[str(other_npc.id)] = {
                'value': 0.0,
                'last_change': {
                    'amount': 0.0,
                    'reason': 'initialization',
                    'timestamp': datetime.utcnow().isoformat()
                },
                'updated_at': datetime.utcnow().isoformat()
            }
            
    def run_daily_tick(self) -> None:
        """Run daily relationship updates."""
        npcs = self.session.query(NPC).all()
        for npc in npcs:
            if not npc.relationships:
                continue
                
            for target_id, relationship in npc.relationships.items():
                # Decay relationship strength
                current_value = relationship.get('value', 0.0)
                new_value = max(-1.0, min(1.0, current_value - 0.1))
                
                relationship['value'] = new_value
                relationship['updated_at'] = datetime.utcnow().isoformat()
                
            self.session.commit() 