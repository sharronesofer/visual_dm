"""
Faction system for managing faction dynamics and allegiances.
"""

from flask import current_app
from firebase_admin import firestore
from datetime import datetime
from typing import Dict, List, Optional
import random

class FactionSystem:
    def __init__(self, app):
        self.app = app
        self.db = firestore.client()
        self.faction_collection = self.db.collection('factions')
        self.membership_collection = self.db.collection('faction_memberships')
        self.relationship_collection = self.db.collection('faction_relationships')
        
    def create_faction(self, name: str, description: str, 
                      goals: List[str], values: Dict, alignment: str) -> str:
        """Create a new faction with goals and values."""
        faction = {
            'name': name,
            'description': description,
            'goals': goals,
            'values': values,
            'alignment': alignment,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'resources': {
                'gold': 1000,
                'influence': 50,
                'manpower': 10,
                'territory': 1
            },
            'relationships': {},
            'territory': [],
            'active_quests': [],
            'completed_quests': [],
            'members': [],
            'policies': {}
        }
        
        faction_doc = self.faction_collection.add(faction)
        return faction_doc[1].id
        
    def get_faction(self, faction_id: str) -> Optional[Dict]:
        """Get a faction by ID with complete data."""
        faction_doc = self.faction_collection.document(faction_id).get()
        if not faction_doc.exists:
            return None
            
        faction = faction_doc.to_dict()
        faction['id'] = faction_doc.id
        
        # Get members
        members = self.membership_collection.where(
            'faction_id', '==', faction_id
        ).get()
        
        faction['members'] = [
            {
                'npc_id': member.to_dict()['npc_id'],
                'role': member.to_dict()['role'],
                'joined_at': member.to_dict()['joined_at']
            }
            for member in members
        ]
        
        # Get relationships with other factions
        relationships = self.relationship_collection.where(
            'faction_id', '==', faction_id
        ).get()
        
        faction['relationships'] = {
            rel.to_dict()['target_faction_id']: rel.to_dict()['value']
            for rel in relationships
        }
        
        return faction
        
    def add_member(self, faction_id: str, npc_id: str, role: str) -> None:
        """Add an NPC to a faction with a specific role."""
        # Check if already a member
        existing = self.membership_collection.where(
            'faction_id', '==', faction_id
        ).where(
            'npc_id', '==', npc_id
        ).get()
        
        if existing:
            return
            
        # Add membership
        self.membership_collection.add({
            'faction_id': faction_id,
            'npc_id': npc_id,
            'role': role,
            'joined_at': datetime.utcnow().isoformat(),
            'contribution': 0
        })
        
        # Update NPC's faction
        npc = current_app.npc_system.get_npc(npc_id)
        if npc:
            npc_ref = current_app.npc_system.npc_collection.document(npc_id)
            npc_ref.update({
                'faction_id': faction_id,
                'faction_role': role
            })
            
        # Update faction's member list
        faction_ref = self.faction_collection.document(faction_id)
        faction = faction_ref.get().to_dict()
        if 'members' not in faction:
            faction['members'] = []
        faction['members'].append({
            'npc_id': npc_id,
            'role': role,
            'joined_at': datetime.utcnow().isoformat()
        })
        faction_ref.update({'members': faction['members']})
            
    def remove_member(self, faction_id: str, npc_id: str) -> None:
        """Remove an NPC from a faction."""
        # Remove membership
        membership = self.membership_collection.where(
            'faction_id', '==', faction_id
        ).where(
            'npc_id', '==', npc_id
        ).get()
        
        if membership:
            membership[0].reference.delete()
            
        # Update NPC's faction
        npc = current_app.npc_system.get_npc(npc_id)
        if npc:
            npc_ref = current_app.npc_system.npc_collection.document(npc_id)
            npc_ref.update({
                'faction_id': None,
                'faction_role': None
            })
            
        # Update faction's member list
        faction_ref = self.faction_collection.document(faction_id)
        faction = faction_ref.get().to_dict()
        if 'members' in faction:
            faction['members'] = [m for m in faction['members'] if m['npc_id'] != npc_id]
            faction_ref.update({'members': faction['members']})
            
    def update_faction_relationship(self, faction_id: str, target_faction_id: str, change: float) -> None:
        """Update relationship value between two factions."""
        # Get or create relationship document
        relationship_query = self.relationship_collection.where(
            'faction_id', '==', faction_id
        ).where(
            'target_faction_id', '==', target_faction_id
        ).get()
        
        if relationship_query:
            relationship = relationship_query[0]
            current_value = relationship.to_dict()['value']
            new_value = max(-1.0, min(1.0, current_value + change))
            
            relationship.reference.update({
                'value': new_value,
                'updated_at': datetime.utcnow().isoformat()
            })
        else:
            # Create new relationship
            self.relationship_collection.add({
                'faction_id': faction_id,
                'target_faction_id': target_faction_id,
                'value': max(-1.0, min(1.0, change)),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
    def update_member_contribution(self, faction_id: str, npc_id: str, amount: int) -> None:
        """Update a member's contribution to their faction."""
        membership = self.membership_collection.where(
            'faction_id', '==', faction_id
        ).where(
            'npc_id', '==', npc_id
        ).get()
        
        if membership:
            current = membership[0].to_dict()['contribution']
            membership[0].reference.update({
                'contribution': current + amount
            })
            
    def get_faction_quests(self, faction_id: str) -> List[Dict]:
        """Get available quests for a faction."""
        faction = self.get_faction(faction_id)
        if not faction:
            return []
            
        quest_templates = current_app.quest_system.get_available_templates()
        available_quests = []
        
        for template in quest_templates:
            if self._should_offer_quest(faction, template):
                quest = self._customize_quest(template, faction)
                available_quests.append(quest)
                
        return available_quests
        
    def _should_offer_quest(self, faction: Dict, quest_template: Dict) -> bool:
        """Determine if a quest template should be offered to a faction."""
        # Check alignment compatibility
        if 'required_alignment' in quest_template:
            if faction['alignment'] != quest_template['required_alignment']:
                return False
                
        # Check resource requirements
        if 'required_resources' in quest_template:
            for resource, amount in quest_template['required_resources'].items():
                if faction['resources'].get(resource, 0) < amount:
                    return False
                    
        return True
        
    def _customize_quest(self, template: Dict, faction: Dict) -> Dict:
        """Customize a quest template for a specific faction."""
        quest = template.copy()
        quest['faction_id'] = faction['id']
        quest['faction_name'] = faction['name']
        
        # Scale rewards based on faction's influence
        influence = faction['resources'].get('influence', 0)
        quest['rewards'] = {
            k: int(v * (1 + influence / 100))
            for k, v in quest['rewards'].items()
        }
        
        return quest

# Global faction system instance
faction_system = None

def init_faction_system(app) -> None:
    """Initialize the faction system."""
    global faction_system
    faction_system = FactionSystem(app) 