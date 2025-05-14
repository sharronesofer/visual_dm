"""
Faction model for game factions.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
from enum import Enum
from app.core.models.resource import Resource
from app.core.models.point_of_interest import PointOfInterest

class RelationshipType(str, Enum):
    ALLIED = "allied"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"
    WAR = "war"

class FactionRelation(BaseModel):
    """Model for tracking relationships between two factions."""
    __tablename__ = 'faction_relations'
    __table_args__ = (UniqueConstraint('faction_id', 'other_faction_id', name='uq_faction_relation'), {'extend_existing': True})

    id = Column(Integer, primary_key=True)
    faction_id = Column(Integer, ForeignKey('factions.id'), nullable=False)
    other_faction_id = Column(Integer, ForeignKey('factions.id'), nullable=False)
    relation_value = Column(Integer, default=0)  # -100 (war) to 100 (allied)
    relation_type = Column(String(20), default=RelationshipType.NEUTRAL.value)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def update_relation(self, delta: int):
        self.relation_value = max(-100, min(100, self.relation_value + delta))
        self.relation_type = self._determine_type()
        self.last_updated = datetime.utcnow()

    def _determine_type(self) -> str:
        if self.relation_value >= 75:
            return RelationshipType.ALLIED.value
        elif self.relation_value >= 25:
            return RelationshipType.FRIENDLY.value
        elif self.relation_value > -25:
            return RelationshipType.NEUTRAL.value
        elif self.relation_value > -75:
            return RelationshipType.HOSTILE.value
        else:
            return RelationshipType.WAR.value

class Faction(BaseModel):
    """
    Represents a faction in the game world
    """
    __tablename__ = 'factions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # guild, kingdom, tribe, etc.
    alignment = Column(String(50))
    influence = Column(Float, default=1.0)
    reputation = Column(Float, default=0.0)
    resources = Column(JSON, default=lambda: {
        'gold': 1000,
        'materials': {},
        'special_resources': {},
        'income_sources': [],
        'expenses': []
    })
    territory = Column(JSON, default=dict)
    relationships = Column(JSON, default=lambda: {
        'allies': [],
        'enemies': [],
        'neutral': [],
        'trade_partners': []
    })
    history = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Foreign Keys
    leader_id = Column(Integer, ForeignKey('npcs.id', use_alter=True, name='fk_faction_leader'))
    headquarters_id = Column(Integer, ForeignKey('regions.id', use_alter=True, name='fk_faction_headquarters'))
    
    # Relationships
    leader = relationship('NPC', foreign_keys=[leader_id], back_populates='led_faction')
    headquarters = relationship('Region', back_populates='based_factions', foreign_keys=[headquarters_id])
    controlled_regions = relationship('Region', back_populates='controlling_faction', foreign_keys='Region.controlling_faction_id')
    resources = relationship('Resource', back_populates='faction')
    owned_locations = relationship('PointOfInterest', back_populates='owner')
    
    # Faction Attributes
    power = Column(Float, default=1.0)  # Overall faction strength
    wealth = Column(Float, default=1000.0)  # Economic resources
    
    # Faction Data
    goals = Column(JSON, default=lambda: {
        'current': [],
        'completed': [],
        'failed': []
    })
    
    policies = Column(JSON, default=lambda: {
        'diplomatic': {
            'aggression': 0,  # -100 to 100
            'trade_focus': 0,
            'expansion': 0
        },
        'economic': {
            'tax_rate': 10,
            'trade_tariffs': 5,
            'investment_focus': []
        },
        'military': {
            'stance': 'defensive',
            'recruitment_rate': 'normal',
            'training_focus': []
        }
    })
    
    state = Column(JSON, default=lambda: {
        'active_wars': [],
        'current_projects': [],
        'recent_events': [],
        'statistics': {
            'members_count': 0,
            'territory_count': 0,
            'quest_success_rate': 0
        }
    })
    
    world_id = Column(Integer, ForeignKey('worlds.id'))
    world = relationship("World", back_populates="factions")
    
    # Relationships with other entities
    quests = relationship('app.core.models.quest.Quest', back_populates='faction')
    territories = relationship('Region', back_populates='controlling_faction', foreign_keys='Region.controlling_faction_id', overlaps='controlled_regions')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'alignment': self.alignment,
            'influence': self.influence,
            'reputation': self.reputation,
            'resources': self.resources,
            'territory': self.territory,
            'relationships': self.relationships,
            'history': self.history,
            'is_active': self.is_active,
            'leader_id': self.leader_id,
            'headquarters_id': self.headquarters_id,
            'controlled_regions': [region.to_dict() for region in self.controlled_regions],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Faction {self.name}>'

    def update_resources(self) -> Optional[Dict[str, Any]]:
        """
        Update faction resources based on income and expenses
        Returns changes if any occurred
        """
        changes = {
            'income': {},
            'expenses': {},
            'net_change': {}
        }
        
        # Process income
        for source in self.resources['income_sources']:
            resource_type = source['type']
            amount = source['amount']
            
            if resource_type not in self.resources['materials']:
                self.resources['materials'][resource_type] = 0
            
            self.resources['materials'][resource_type] += amount
            changes['income'][resource_type] = amount
        
        # Process expenses
        for expense in self.resources['expenses']:
            resource_type = expense['type']
            amount = expense['amount']
            
            if resource_type in self.resources['materials']:
                self.resources['materials'][resource_type] = max(
                    0, 
                    self.resources['materials'][resource_type] - amount
                )
                changes['expenses'][resource_type] = amount
        
        # Calculate net changes
        for resource_type in set(changes['income'].keys()) | set(changes['expenses'].keys()):
            income = changes['income'].get(resource_type, 0)
            expense = changes['expenses'].get(resource_type, 0)
            changes['net_change'][resource_type] = income - expense
        
        return changes if any(changes.values()) else None

    def process_relationships(self) -> Optional[Dict[str, Any]]:
        """
        Process and update faction relationships
        Returns changes if any occurred
        """
        changes = []
        
        # Process relationship events
        for faction_id in list(self.relationships['allies']):
            if not self._check_alliance_conditions(faction_id):
                self.relationships['allies'].remove(faction_id)
                self.relationships['neutral'].append(faction_id)
                changes.append({
                    'type': 'alliance_broken',
                    'faction_id': faction_id,
                    'reason': 'conditions_not_met'
                })
        
        for faction_id in list(self.relationships['enemies']):
            if self._check_peace_conditions(faction_id):
                self.relationships['enemies'].remove(faction_id)
                self.relationships['neutral'].append(faction_id)
                changes.append({
                    'type': 'peace_established',
                    'faction_id': faction_id,
                    'reason': 'conditions_met'
                })
        
        # Process trade relationships
        for partner_id in list(self.relationships['trade_partners']):
            if not self._check_trade_conditions(partner_id):
                self.relationships['trade_partners'].remove(partner_id)
                changes.append({
                    'type': 'trade_ended',
                    'faction_id': partner_id,
                    'reason': 'conditions_not_met'
                })
        
        return changes if changes else None

    def update_goals(self) -> Optional[Dict[str, Any]]:
        """
        Update faction goals and progress
        Returns changes if any occurred
        """
        changes = []
        
        # Process current goals
        for goal in list(self.goals['current']):
            # Check for completion
            if self._check_goal_completion(goal):
                self.goals['current'].remove(goal)
                self.goals['completed'].append(goal)
                changes.append({
                    'type': 'goal_completed',
                    'goal': goal['description']
                })
            # Check for failure
            elif self._check_goal_failure(goal):
                self.goals['current'].remove(goal)
                self.goals['failed'].append(goal)
                changes.append({
                    'type': 'goal_failed',
                    'goal': goal['description'],
                    'reason': goal.get('failure_reason', 'unknown')
                })
            # Update progress
            else:
                new_progress = self._calculate_goal_progress(goal)
                if new_progress != goal.get('progress', 0):
                    goal['progress'] = new_progress
                    changes.append({
                        'type': 'goal_progress',
                        'goal': goal['description'],
                        'progress': new_progress
                    })
        
        # Generate new goals if needed
        if len(self.goals['current']) < 3:  # Maintain at least 3 active goals
            new_goal = self._generate_new_goal()
            if new_goal:
                self.goals['current'].append(new_goal)
                changes.append({
                    'type': 'new_goal',
                    'goal': new_goal['description']
                })
        
        return changes if changes else None

    def _check_alliance_conditions(self, faction_id: int) -> bool:
        """
        Check if alliance conditions with a faction are still met
        """
        # TODO: Implement alliance condition checking
        return True

    def _check_peace_conditions(self, faction_id: int) -> bool:
        """
        Check if conditions for peace with a faction are met
        """
        # TODO: Implement peace condition checking
        return False

    def _check_trade_conditions(self, faction_id: int) -> bool:
        """
        Check if trade conditions with a faction are still met
        """
        # TODO: Implement trade condition checking
        return True

    def _check_goal_completion(self, goal: Dict[str, Any]) -> bool:
        """
        Check if a goal has been completed
        """
        if 'conditions' not in goal:
            return False
        
        for condition in goal['conditions']:
            if not self._evaluate_condition(condition):
                return False
        return True

    def _check_goal_failure(self, goal: Dict[str, Any]) -> bool:
        """
        Check if a goal has failed
        """
        if 'failure_conditions' not in goal:
            return False
        
        for condition in goal['failure_conditions']:
            if self._evaluate_condition(condition):
                return True
        return False

    def _calculate_goal_progress(self, goal: Dict[str, Any]) -> float:
        """
        Calculate progress towards a goal (0-100)
        """
        if 'progress_calculation' not in goal:
            return goal.get('progress', 0)
        
        calc = goal['progress_calculation']
        if calc['type'] == 'resource':
            current = self.resources['materials'].get(calc['resource'], 0)
            return min(100, (current / calc['target']) * 100)
        elif calc['type'] == 'territory':
            return min(100, (len(self.territories) / calc['target']) * 100)
        elif calc['type'] == 'relationship':
            if calc['faction_id'] in self.relationships[calc['desired_status']]:
                return 100
            return 0
        
        return goal.get('progress', 0)

    def _generate_new_goal(self) -> Optional[Dict[str, Any]]:
        """
        Generate a new goal based on faction state and policies
        """
        # TODO: Implement goal generation logic
        return None

    def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Evaluate a single condition
        """
        condition_type = condition['type']
        
        if condition_type == 'resource':
            resource = condition['resource']
            amount = condition['amount']
            return self.resources['materials'].get(resource, 0) >= amount
        elif condition_type == 'territory':
            return len(self.territories) >= condition['amount']
        elif condition_type == 'relationship':
            faction_id = condition['faction_id']
            status = condition['status']
            return faction_id in self.relationships[status]
        elif condition_type == 'power':
            return self.power >= condition['amount']
        
        return False

    def get_relation(self, session, other_faction_id: int) -> FactionRelation:
        return session.query(FactionRelation).filter_by(faction_id=self.id, other_faction_id=other_faction_id).first()

    def set_relation(self, session, other_faction_id: int, delta: int):
        rel = self.get_relation(session, other_faction_id)
        if not rel:
            rel = FactionRelation(faction_id=self.id, other_faction_id=other_faction_id, relation_value=0)
            session.add(rel)
        rel.update_relation(delta)
        session.commit()
        return rel

    def decay_relations(self, session, amount: int = 1):
        rels = session.query(FactionRelation).filter_by(faction_id=self.id).all()
        for rel in rels:
            if rel.relation_value > 0:
                rel.update_relation(-amount)
            elif rel.relation_value < 0:
                rel.update_relation(amount)
        session.commit()

    def trigger_event_relation_change(self, session, other_faction_id: int, event_type: str):
        # Example: event_type could be 'alliance_formed', 'war_declared', etc.
        event_deltas = {
            'alliance_formed': 50,
            'war_declared': -100,
            'trade_agreement': 20,
            'skirmish': -20,
            'diplomatic_incident': -40,
            'peace_treaty': 30,
        }
        delta = event_deltas.get(event_type, 0)
        return self.set_relation(session, other_faction_id, delta)

if __name__ == "__main__":
    def test_faction_relation():
        rel = FactionRelation(faction_id=1, other_faction_id=2, relation_value=0)
        rel.update_relation(80)
        assert rel.relation_type == RelationshipType.ALLIED.value
        rel.update_relation(-100)
        assert rel.relation_type == RelationshipType.WAR.value
        rel.update_relation(50)
        assert rel.relation_type == RelationshipType.HOSTILE.value or rel.relation_type == RelationshipType.NEUTRAL.value
        print("test_faction_relation passed")

    test_faction_relation() 