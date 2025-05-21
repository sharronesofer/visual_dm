# # # # from app import db
from app.models.npc import NPC
from app.models.region import Region
from app.models.faction import Faction
import random

def generate_npc_for_region(region_id, faction_id=None, role=None, name=None):
    """Generate an NPC for a specific region with optional parameters."""
    try:
        # Get the region
        region = Region.query.get(region_id)
        if not region:
            return None
            
        # Get faction if specified
        faction = None
        if faction_id:
            faction = Faction.query.get(faction_id)
            
        # Generate NPC attributes
        if not name:
            name = generate_npc_name()
            
        if not role:
            role = generate_npc_role()
            
        # Create the NPC
        npc = NPC(
            name=name,
            role=role,
            region_id=region_id,
            faction_id=faction_id if faction else None,
            description=generate_npc_description(name, role, region, faction)
        )
        
        # Save to database
        db.session.add(npc)
        db.session.commit()
        
        return npc.to_dict()
        
    except Exception as e:
        print(f"Error generating NPC: {str(e)}")
        return None

def generate_npc_name():
    """Generate a random NPC name."""
    first_names = ["Aiden", "Brianna", "Caleb", "Diana", "Ethan", "Fiona", 
                  "Gavin", "Hannah", "Ian", "Julia", "Kyle", "Luna", 
                  "Marcus", "Nora", "Owen", "Paige", "Quinn", "Riley"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
                 "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez"]
                 
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_npc_role():
    """Generate a random NPC role."""
    roles = ["Merchant", "Guard", "Innkeeper", "Blacksmith", "Farmer", 
            "Priest", "Scholar", "Bard", "Ranger", "Mage", "Thief", 
            "Noble", "Servant", "Craftsman", "Hunter"]
            
    return random.choice(roles)

def generate_npc_description(name, role, region, faction):
    """Generate a description for the NPC."""
    description = f"{name} is a {role.lower()} "
    
    if faction:
        description += f"aligned with the {faction.name} "
        
    description += f"in {region.name}."
    
    return description 
