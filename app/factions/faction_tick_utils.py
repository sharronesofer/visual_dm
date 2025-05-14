"""Utility functions for handling faction updates during world ticks."""

import random
from datetime import datetime
from typing import Dict, List, Optional
from app.models.faction import Faction
from app.core.database import db

def update_faction_resources(faction_id: int) -> bool:
    """Update faction resources during a world tick."""
    try:
        faction = Faction.query.get(faction_id)
        if not faction:
            return False
            
        # Update basic resources
        for resource, amount in faction.resources.items():
            production = faction.resource_production.get(resource, 0)
            consumption = faction.resource_consumption.get(resource, 0)
            
            new_amount = amount + production - consumption
            faction.resources[resource] = max(0, new_amount)
            
        faction.last_resource_update = datetime.utcnow()
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating faction resources: {str(e)}")
        return False

def update_faction_relations(faction_id: int) -> bool:
    """Update faction relationships during a world tick."""
    try:
        faction = Faction.query.get(faction_id)
        if not faction:
            return False
            
        # Natural decay of relations
        for other_id, relation in faction.relations.items():
            if relation > 0:
                faction.relations[other_id] = max(0, relation - 1)
            elif relation < 0:
                faction.relations[other_id] = min(0, relation + 1)
                
        faction.last_relations_update = datetime.utcnow()
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating faction relations: {str(e)}")
        return False

def process_faction_events(faction_id: int) -> bool:
    """Process pending faction events during a world tick."""
    try:
        faction = Faction.query.get(faction_id)
        if not faction:
            return False
            
        current_time = datetime.utcnow()
        processed_events = []
        
        for event in faction.pending_events:
            if event['trigger_time'] <= current_time:
                if handle_faction_event(faction, event):
                    processed_events.append(event)
                    
        # Remove processed events
        faction.pending_events = [e for e in faction.pending_events 
                                if e not in processed_events]
                                
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error processing faction events: {str(e)}")
        return False

def handle_faction_event(faction: Faction, event: Dict) -> bool:
    """Handle a specific faction event."""
    try:
        event_type = event.get('type')
        
        if event_type == 'resource_change':
            resource = event['resource']
            amount = event['amount']
            faction.resources[resource] = max(0, 
                faction.resources.get(resource, 0) + amount)
                
        elif event_type == 'relation_change':
            other_faction = event['target_faction']
            change = event['change']
            current = faction.relations.get(other_faction, 0)
            faction.relations[other_faction] = max(-100, min(100, current + change))
            
        elif event_type == 'territory_change':
            territory = event['territory']
            if event['action'] == 'add':
                faction.territories.append(territory)
            elif event['action'] == 'remove':
                faction.territories.remove(territory)
                
        return True
        
    except Exception as e:
        print(f"Error handling faction event: {str(e)}")
        return False

def check_faction_goals(faction_id: int) -> List[Dict]:
    """Check faction goals during a world tick."""
    try:
        faction = Faction.query.get(faction_id)
        if not faction:
            return []
            
        completed_goals = []
        
        for goal in faction.active_goals:
            if check_goal_completion(faction, goal):
                completed_goals.append(goal)
                
                # Generate new goal to replace completed one
                new_goal = generate_faction_goal(faction)
                if new_goal:
                    faction.active_goals.append(new_goal)
                    
        # Remove completed goals
        faction.active_goals = [g for g in faction.active_goals 
                              if g not in completed_goals]
                              
        db.session.commit()
        return completed_goals
        
    except Exception as e:
        db.session.rollback()
        print(f"Error checking faction goals: {str(e)}")
        return []

def check_goal_completion(faction: Faction, goal: Dict) -> bool:
    """Check if a specific faction goal has been completed."""
    goal_type = goal.get('type')
    
    if goal_type == 'resource_threshold':
        resource = goal['resource']
        threshold = goal['threshold']
        return faction.resources.get(resource, 0) >= threshold
        
    elif goal_type == 'relation_threshold':
        target_faction = goal['target_faction']
        threshold = goal['threshold']
        return faction.relations.get(target_faction, 0) >= threshold
        
    elif goal_type == 'territory_count':
        threshold = goal['threshold']
        return len(faction.territories) >= threshold
        
    return False

def generate_faction_goal(faction: Faction) -> Optional[Dict]:
    """Generate a new goal for a faction."""
    goal_types = ['resource_threshold', 'relation_threshold', 'territory_count']
    goal_type = random.choice(goal_types)
    
    if goal_type == 'resource_threshold':
        resource = random.choice(list(faction.resources.keys()))
        current = faction.resources.get(resource, 0)
        return {
            'type': 'resource_threshold',
            'resource': resource,
            'threshold': current + random.randint(100, 500)
        }
        
    elif goal_type == 'relation_threshold':
        other_factions = [f for f in Faction.query.all() if f.id != faction.id]
        if not other_factions:
            return None
            
        target = random.choice(other_factions)
        current = faction.relations.get(str(target.id), 0)
        return {
            'type': 'relation_threshold',
            'target_faction': str(target.id),
            'threshold': min(100, current + random.randint(10, 30))
        }
        
    elif goal_type == 'territory_count':
        current = len(faction.territories)
        return {
            'type': 'territory_count',
            'threshold': current + random.randint(1, 3)
        }
        
    return None 