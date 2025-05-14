"""
Main NPC system for managing non-player characters and their interactions.
"""

from datetime import datetime
from typing import Dict, List, Optional
import random
from sqlalchemy.orm import Session
from flask import current_app
from app.core.database import db
from app.core.models.npc import NPC
from app.core.models.faction import Faction
from app.core.models.region import Region
from app.core.npc.relationships import NPCRelationships
from app.core.npc.loyalty import NPCLoyalty
from app.core.npc.travel import NPCTravel
from app.core.npc.rumors import NPCRumors
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class NPCSystem:
    """Main system for managing NPCs and their interactions."""
    
    def __init__(self, session: Session = None):
        self.session = session or db.session
        self.relationships = NPCRelationships(self.session)
        self.loyalty = NPCLoyalty(self.session)
        self.travel = NPCTravel(self.session)
        self.rumors = NPCRumors(self.session)
        self.scheduler = BackgroundScheduler()
        self._setup_daily_tasks()
        
    def _setup_daily_tasks(self):
        """Set up scheduled daily tasks."""
        # Run all daily updates at once
        self.scheduler.add_job(
            self.run_daily_updates,
            trigger=IntervalTrigger(days=1),
            id='npc_daily_updates',
            replace_existing=True
        )
        self.scheduler.start()
        
    def run_daily_updates(self):
        """Run all daily updates for NPCs."""
        with self.session.begin():
            # Run relationship updates
            self.relationships.run_daily_tick()
            
            # Run loyalty updates
            self.loyalty.run_daily_tick()
            
            # Run travel updates
            self.travel.run_daily_tick()
            
            # Run rumor updates
            self.rumors.run_daily_tick()
            
    def cleanup(self):
        """Clean up resources when shutting down."""
        self.scheduler.shutdown()
        
    def create_npc(self, name: str, race: str, class_: str, 
                  backstory: str, personality: Dict,
                  region_id: Optional[int] = None,
                  faction_id: Optional[int] = None) -> NPC:
        """Create a new NPC with backstory and personality."""
        npc = NPC(
            name=name,
            race=race,
            class_=class_,
            backstory=backstory,
            personality=personality,
            region_id=region_id,
            faction_id=faction_id,
            stats=self._generate_npc_stats(race, class_),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.session.add(npc)
        self.session.commit()
        
        # Initialize relationships and faction opinions
        self.relationships.initialize_relationships(npc.id)
        self.loyalty.initialize_faction_opinions(npc.id)
        
        return npc
        
    def get_npc(self, npc_id: int) -> Optional[NPC]:
        """Get an NPC by ID with complete data."""
        return self.session.query(NPC).get(npc_id)
        
    def update_relationship(self, npc_id: int, target_id: int, 
                          change: float, reason: str) -> None:
        """Update relationship between two NPCs."""
        self.relationships.update_relationship(npc_id, target_id, change, reason)
        
    def get_interaction_options(self, npc_id: int, 
                              player_id: int) -> List[Dict]:
        """Get available interaction options for an NPC."""
        npc = self.get_npc(npc_id)
        if not npc:
            return []
            
        options = []
        
        # Basic interactions
        options.append({
            'type': 'greet',
            'description': 'Greet the NPC',
            'relationship_change': 0.1
        })
        
        options.append({
            'type': 'ask_about_backstory',
            'description': 'Ask about their backstory',
            'relationship_change': 0.2
        })
        
        # Faction-based interactions
        if npc.faction_id:
            faction = self.session.query(Faction).get(npc.faction_id)
            if faction:
                options.append({
                    'type': 'ask_about_faction',
                    'description': f'Ask about the {faction.name}',
                    'relationship_change': 0.15
                })
                
        # Quest-related interactions
        if npc.quests_given:
            options.append({
                'type': 'ask_about_quests',
                'description': 'Ask about available quests',
                'relationship_change': 0.1
            })
            
        # Relationship-based interactions
        relationship = self.relationships.get_relationship(npc_id, player_id)
        if relationship and relationship > 0.5:
            options.append({
                'type': 'ask_for_help',
                'description': 'Ask for their help',
                'relationship_change': -0.1
            })
            
        return options
        
    def process_interaction(self, npc_id: int, player_id: int,
                          interaction_type: str) -> Dict:
        """Process an interaction between an NPC and player."""
        npc = self.get_npc(npc_id)
        if not npc:
            return {'success': False, 'message': 'NPC not found'}
            
        # Find the interaction option
        options = self.get_interaction_options(npc_id, player_id)
        option = next((opt for opt in options if opt['type'] == interaction_type), None)
        
        if not option:
            return {'success': False, 'message': 'Invalid interaction type'}
            
        # Update relationship
        self.update_relationship(
            npc_id, player_id,
            option['relationship_change'],
            f'{interaction_type} interaction'
        )
        
        # Generate response based on personality and relationship
        response = self._generate_response(npc, interaction_type)
        
        return {
            'success': True,
            'message': response,
            'relationship_change': option['relationship_change']
        }
        
    def _generate_npc_stats(self, race: str, class_: str) -> Dict:
        """Generate stats for an NPC based on race and class."""
        base_stats = {
            'strength': random.randint(8, 15),
            'dexterity': random.randint(8, 15),
            'constitution': random.randint(8, 15),
            'intelligence': random.randint(8, 15),
            'wisdom': random.randint(8, 15),
            'charisma': random.randint(8, 15)
        }
        
        # Apply race bonuses
        race_bonuses = current_app.config.get('RACE_STAT_BONUSES', {})
        if race in race_bonuses:
            for stat, bonus in race_bonuses[race].items():
                base_stats[stat] += bonus
                
        # Apply class focus
        class_focus = current_app.config.get('CLASS_STAT_FOCUS', {})
        if class_ in class_focus:
            focus_stats = class_focus[class_]
            for stat in focus_stats:
                base_stats[stat] += random.randint(1, 3)
                
        return base_stats
        
    def _generate_response(self, npc: NPC, interaction_type: str) -> str:
        """Generate an NPC response based on personality and interaction type."""
        personality = npc.personality
        
        # Base responses for each interaction type
        responses = {
            'greet': [
                "Hello there!",
                "Greetings, traveler.",
                "Hey, what's up?",
                "Good to see you."
            ],
            'ask_about_backstory': [
                "Well, it's a long story...",
                "I don't usually talk about my past.",
                "What would you like to know?",
                "My story isn't very interesting."
            ],
            'ask_about_faction': [
                "Our faction is doing well.",
                "I'm proud to be a member.",
                "We have big plans.",
                "It's not really your business."
            ],
            'ask_about_quests': [
                "I might have something for you.",
                "Looking for work?",
                "I could use some help.",
                "Nothing right now."
            ],
            'ask_for_help': [
                "I'll do what I can.",
                "Let me think about it.",
                "I'm not sure I can help.",
                "I have my own problems."
            ]
        }
        
        # Select a response based on personality and relationship
        response_pool = responses.get(interaction_type, ["I don't know what to say."])
        return random.choice(response_pool)

def init_npc_system(app):
    """Initialize the NPC system."""
    app.npc_system = NPCSystem()
    
    # Register cleanup on app teardown
    @app.teardown_appcontext
    def cleanup_npc_system(exception=None):
        app.npc_system.cleanup() 