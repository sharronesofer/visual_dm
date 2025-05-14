"""
NPC rumor generation and management.
"""

from datetime import datetime
from typing import Dict, List, Optional
import random
from sqlalchemy.orm import Session
from app.core.database import db
from app.core.models.npc import NPC
from app.core.models.region import Region

class NPCRumors:
    """Handles NPC rumor generation and management."""
    
    def __init__(self, session: Session = None):
        self.session = session or db.session
        
    def generate_rumor(self, npc_id: int, region_id: int) -> Optional[Dict]:
        """Generate a rumor for an NPC."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc:
            return None
            
        # Generate rumor based on NPC's relationships and knowledge
        rumor = {
            "source": npc_id,
            "content": f"{npc.name} has heard something interesting...",
            "credibility": random.random(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return rumor
        
    def spread_rumor(self, npc_id: int, rumor: Dict) -> List[int]:
        """Spread a rumor to nearby NPCs."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc or not npc.region_id:
            return []
            
        # Get nearby NPCs
        nearby_npcs = self.session.query(NPC).filter(
            NPC.region_id == npc.region_id,
            NPC.id != npc_id
        ).all()
        
        # Determine which NPCs receive the rumor
        recipients = []
        for target_npc in nearby_npcs:
            if random.random() < 0.7:  # 70% chance to spread
                if not target_npc.rumors:
                    target_npc.rumors = []
                    
                # Add rumor to NPC's list
                target_npc.rumors.append({
                    **rumor,
                    "received_at": datetime.utcnow().isoformat()
                })
                recipients.append(target_npc.id)
                
        self.session.commit()
        return recipients
        
    def distort_rumor(self, npc_id: int, rumor: Dict) -> Dict:
        """Distort a rumor when an NPC spreads it."""
        if random.random() < 0.2:  # 20% chance to distort
            # Modify the rumor content
            rumor["content"] = f"Rumor: {rumor['content']} (distorted)"
            rumor["credibility"] *= 0.8  # Reduce credibility
            
        return rumor
        
    def fabricate_rumor(self, npc_id: int) -> Optional[Dict]:
        """Create a new false rumor."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc:
            return None
            
        if random.random() < 0.1:  # 10% chance to fabricate
            fake_rumor = {
                "source": npc_id,
                "content": f"{npc.name} is spreading a false rumor...",
                "credibility": random.random() * 0.5,  # Lower credibility for fakes
                "timestamp": datetime.utcnow().isoformat()
            }
            return fake_rumor
            
        return None
        
    def get_npc_rumors(self, npc_id: int) -> List[Dict]:
        """Get all rumors an NPC has heard."""
        npc = self.session.query(NPC).get(npc_id)
        if not npc or not npc.rumors:
            return []
        return npc.rumors
        
    def run_daily_tick(self) -> None:
        """Run daily rumor updates."""
        npcs = self.session.query(NPC).all()
        for npc in npcs:
            if not npc.rumors:
                continue
                
            # Remove old rumors
            current_time = datetime.utcnow()
            npc.rumors = [
                rumor for rumor in npc.rumors
                if (current_time - datetime.fromisoformat(rumor["timestamp"])).days < 7
            ]
            
            # Chance to fabricate new rumors
            if random.random() < 0.05:  # 5% chance per day
                new_rumor = self.fabricate_rumor(npc.id)
                if new_rumor:
                    if not npc.rumors:
                        npc.rumors = []
                    npc.rumors.append(new_rumor)
                    
            self.session.commit() 