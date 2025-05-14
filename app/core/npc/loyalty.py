"""
NPC loyalty and faction relationship management.
"""

from datetime import datetime
from typing import Dict, Optional
import random
from sqlalchemy.orm import Session
from app.core.database import db
from app.core.models.npc import NPC
from app.core.models.faction import Faction

class NPCLoyalty:
    """Handles NPC loyalty and faction relationships."""
    
    def __init__(self, session: Session):
        self.session = session
        
    def calculate_loyalty(self, npc_id: int, faction_id: int) -> Optional[float]:
        """Calculate an NPC's loyalty to a faction."""
        npc = self.session.query(NPC).get(npc_id)
        faction = self.session.query(Faction).get(faction_id)
        
        if not npc or not faction:
            return None
            
        # Base loyalty calculation
        base_loyalty = 0.5  # Neutral (0.0 to 1.0 scale)
        
        # Adjust based on faction relationships
        if npc.faction_id == faction_id:
            base_loyalty += 0.3  # Strong loyalty to own faction
            
        # Add random variation
        loyalty = base_loyalty + (random.random() * 0.2 - 0.1)
        
        return max(0.0, min(1.0, loyalty))
        
    def get_faction_opinion(self, npc_id: int, faction_id: int) -> Optional[float]:
        """Get an NPC's opinion of a specific faction."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc or not npc.faction_opinions:
            return None
        return npc.faction_opinions.get(str(faction_id), {}).get('loyalty')
        
    def initialize_faction_opinions(self, npc_id: int) -> None:
        """Initialize an NPC's opinions of all factions."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc:
            return
            
        factions = self.session.query(Faction).all()
        npc.faction_opinions = {}
        
        for faction in factions:
            npc.faction_opinions[str(faction.id)] = {
                'loyalty': self.calculate_loyalty(npc_id, faction.id),
                'last_updated': datetime.utcnow().isoformat()
            }
            
    def update_faction_opinion(self, npc_id: int, faction_id: int,
                             change: float, reason: str) -> None:
        """Update an NPC's opinion of a faction."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc:
            return
            
        if not npc.faction_opinions:
            npc.faction_opinions = {}
            
        current_loyalty = npc.faction_opinions.get(str(faction_id), {}).get('loyalty', 0.5)
        new_loyalty = max(0.0, min(1.0, current_loyalty + change))
        
        npc.faction_opinions[str(faction_id)] = {
            'loyalty': new_loyalty,
            'last_change': {
                'amount': change,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            },
            'last_updated': datetime.utcnow().isoformat()
        }
        
    def run_daily_tick(self) -> None:
        """Run daily loyalty updates."""
        npcs = self.session.query(NPC).all()
        for npc in npcs:
            if not npc.faction_opinions:
                continue
                
            for faction_id, opinion in npc.faction_opinions.items():
                # Slight decay of loyalty over time
                current_loyalty = opinion.get('loyalty', 0.5)
                new_loyalty = max(0.0, min(1.0, current_loyalty - 0.01))
                
                opinion['loyalty'] = new_loyalty
                opinion['last_updated'] = datetime.utcnow().isoformat()
                
            self.session.commit() 