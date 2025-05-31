# # # # from app import db
from app.models.npc import NPC
from app.models.faction import Faction
import random
from datetime import datetime, timedelta

class NPCRelationships:
    """Handles NPC relationship management"""
    
    @staticmethod
    def get_relationships(npc_id):
        """Get all relationships for an NPC"""
        npc = NPC.query.get(npc_id)
        if not npc:
            return None
        return npc.relationships or {}

    @staticmethod
    def add_relationship(npc_id, target_npc_id, relationship_type, strength=1):
        """Add a relationship between two NPCs"""
        npc = NPC.query.get(npc_id)
        target_npc = NPC.query.get(target_npc_id)
        
        if not npc or not target_npc:
            return None
            
        if not npc.relationships:
            npc.relationships = {}
            
        npc.relationships[target_npc_id] = {
            "type": relationship_type,
            "strength": strength,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        db.session.commit()
        return npc.relationships[target_npc_id]

    @staticmethod
    def run_daily_tick():
        """Run daily relationship updates"""
        npcs = NPC.query.all()
        for npc in npcs:
            if not npc.relationships:
                continue
                
            for target_id, relationship in npc.relationships.items():
                # Decay relationship strength
                relationship["strength"] = max(0, relationship["strength"] - 0.1)
                
                # Update timestamp
                relationship["last_updated"] = datetime.utcnow().isoformat()
                
            db.session.commit()

class NPCRumors:
    """Handles NPC rumor generation and management"""
    
    @staticmethod
    def generate_rumor(npc_id, region_id):
        """Generate a rumor for an NPC"""
        npc = NPC.query.get(npc_id)
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

    @staticmethod
    def distort_rumors():
        """Distort existing rumors"""
        rumors = db.reference("/npc_rumors").get() or {}
        distorted = []
        
        for rumor_id, rumor in rumors.items():
            if random.random() < 0.2:  # 20% chance to distort
                rumor["content"] = f"Rumor: {rumor['content']} (distorted)"
                distorted.append(rumor_id)
                
        return distorted

    @staticmethod
    def fabricate_rumors():
        """Create new false rumors"""
        npcs = NPC.query.all()
        fakes = []
        
        for npc in npcs:
            if random.random() < 0.1:  # 10% chance to fabricate
                fake_rumor = {
                    "source": npc.id,
                    "content": f"{npc.name} is spreading a false rumor...",
                    "credibility": random.random() * 0.5,  # Lower credibility for fakes
                    "timestamp": datetime.utcnow().isoformat()
                }
                fakes.append(fake_rumor)
                
        return fakes

class NPCLoyalty:
    """Handles NPC loyalty and faction relationships"""
    
    @staticmethod
    def calculate_loyalty(npc_id, faction_id):
        """Calculate an NPC's loyalty to a faction"""
        npc = NPC.query.get(npc_id)
        faction = Faction.query.get(faction_id)
        
        if not npc or not faction:
            return None
            
        # Base loyalty calculation
        base_loyalty = 50  # Neutral
        
        # Adjust based on faction relationships
        if npc.faction_id == faction_id:
            base_loyalty += 30  # Strong loyalty to own faction
            
        # Add random variation
        loyalty = base_loyalty + random.randint(-10, 10)
        
        return max(0, min(100, loyalty))  # Clamp between 0 and 100

    @staticmethod
    def initialize_faction_opinions(npc_id):
        """Initialize an NPC's opinions of all factions"""
        npc = NPC.query.get(npc_id)
        if not npc:
            return
            
        factions = Faction.query.all()
        npc.faction_opinions = {}
        
        for faction in factions:
            npc.faction_opinions[faction.id] = {
                "loyalty": NPCLoyalty.calculate_loyalty(npc_id, faction.id),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        db.session.commit()

class NPCTravel:
    """Handles NPC travel and location management"""
    
    @staticmethod
    def travel_to_region(npc_id, target_region_id):
        """Move an NPC to a new region"""
        npc = NPC.query.get(npc_id)
        if not npc:
            return False
            
        # Check if NPC can travel (e.g., not in combat, not imprisoned)
        if npc.status != "active":
            return False
            
        # Update NPC's location
        npc.region_id = target_region_id
        npc.last_travel = datetime.utcnow()
        
        db.session.commit()
        return True

# Emotion pool for NPC emotional states
EMOTION_POOL = [
    "happy", "sad", "angry", "fearful", "disgusted", "surprised",
    "content", "anxious", "hopeful", "jealous", "proud", "ashamed",
    "excited", "bored", "confused", "determined", "grateful", "lonely"
] 