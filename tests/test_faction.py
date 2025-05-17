"""
Tests for the faction system.
"""

import pytest
from datetime import datetime
from app.core.models.world import Faction, FactionRelation, RelationshipType
from app.core.database import db

@pytest.fixture
def test_faction(app):
    """Create a test faction."""
    with app.app_context():
        faction = Faction(
            name="Test Faction",
            description="A test faction",
            type="guild",
            alignment="neutral",
            influence=1.0,
            reputation=0.0
        )
        db.session.add(faction)
        db.session.commit()
        yield faction
        db.session.delete(faction)
        db.session.commit()

@pytest.fixture
def test_factions(app):
    """Create multiple test factions."""
    with app.app_context():
        factions = [
            Faction(
                name=f"Test Faction {i}",
                description=f"Test faction {i}",
                type="guild",
                alignment="neutral",
                influence=1.0,
                reputation=0.0
            )
            for i in range(3)
        ]
        for faction in factions:
            db.session.add(faction)
        db.session.commit()
        yield factions
        for faction in factions:
            db.session.delete(faction)
        db.session.commit()

def test_faction_creation(test_faction):
    """Test basic faction creation."""
    assert test_faction.name == "Test Faction"
    assert test_faction.description == "A test faction"
    assert test_faction.type == "guild"
    assert test_faction.alignment == "neutral"
    assert test_faction.influence == 1.0
    assert test_faction.reputation == 0.0
    assert test_faction.resources == {
        'gold': 1000,
        'materials': {},
        'special_resources': {},
        'income_sources': [],
        'expenses': []
    }
    assert test_faction.goals == {
        'current': [],
        'completed': [],
        'failed': []
    }

def test_faction_to_dict(test_faction):
    """Test faction serialization."""
    faction_dict = test_faction.to_dict()
    assert faction_dict['name'] == test_faction.name
    assert faction_dict['description'] == test_faction.description
    assert faction_dict['type'] == test_faction.type
    assert faction_dict['alignment'] == test_faction.alignment
    assert faction_dict['influence'] == test_faction.influence
    assert faction_dict['reputation'] == test_faction.reputation
    assert 'created_at' in faction_dict
    assert 'updated_at' in faction_dict

def test_faction_relationships(app, test_factions):
    """Test faction relationship management."""
    with app.app_context():
        faction1, faction2, faction3 = test_factions
        
        # Test initial neutral relationship
        rel = faction1.get_relation(db.session, faction2.id)
        assert rel is None
        
        # Test setting relationship
        faction1.set_relation(db.session, faction2.id, 80)
        rel = faction1.get_relation(db.session, faction2.id)
        assert rel.relation_value == 80
        assert rel.relation_type == RelationshipType.ALLIED.value
        
        # Test relationship decay
        faction1.decay_relations(db.session, amount=10)
        rel = faction1.get_relation(db.session, faction2.id)
        assert rel.relation_value == 70
        assert rel.relation_type == RelationshipType.FRIENDLY.value
        
        # Test event-based relationship changes
        faction1.trigger_event_relation_change(db.session, faction2.id, 'war_declared')
        rel = faction1.get_relation(db.session, faction2.id)
        assert rel.relation_value == -30
        assert rel.relation_type == RelationshipType.HOSTILE.value

def test_faction_resource_management(test_faction):
    """Test faction resource management."""
    # Test initial resources
    assert test_faction.resources['gold'] == 1000
    assert test_faction.resources['materials'] == {}
    
    # Test resource update with income
    test_faction.resources['income_sources'] = [
        {'type': 'gold', 'amount': 100},
        {'type': 'wood', 'amount': 50}
    ]
    test_faction.resources['expenses'] = [
        {'type': 'gold', 'amount': 30},
        {'type': 'wood', 'amount': 20}
    ]
    
    changes = test_faction.update_resources()
    assert changes is not None
    assert changes['income']['gold'] == 100
    assert changes['income']['wood'] == 50
    assert changes['expenses']['gold'] == 30
    assert changes['expenses']['wood'] == 20
    assert test_faction.resources['materials']['wood'] == 30
    assert test_faction.resources['gold'] == 1070

def test_faction_goal_management(test_faction):
    """Test faction goal management."""
    # Add test goals
    test_faction.goals['current'].append({
        'id': 1,
        'type': 'conquest',
        'target': 'Region A',
        'conditions': [
            {'type': 'territory_control', 'target': 'Region A', 'value': True}
        ],
        'failure_conditions': [
            {'type': 'time_limit', 'deadline': (datetime.utcnow().isoformat())}
        ]
    })
    
    # Test goal updates
    changes = test_faction.update_goals()
    assert changes is not None
    assert 'completed' in changes
    assert 'failed' in changes
    assert 'new' in changes

def test_faction_policy_management(test_faction):
    """Test faction policy management."""
    # Test initial policies
    assert test_faction.policies['diplomatic']['aggression'] == 0
    assert test_faction.policies['economic']['tax_rate'] == 10
    assert test_faction.policies['military']['stance'] == 'defensive'
    
    # Test policy updates
    test_faction.policies['diplomatic']['aggression'] = 50
    test_faction.policies['economic']['tax_rate'] = 15
    test_faction.policies['military']['stance'] = 'aggressive'
    
    assert test_faction.policies['diplomatic']['aggression'] == 50
    assert test_faction.policies['economic']['tax_rate'] == 15
    assert test_faction.policies['military']['stance'] == 'aggressive'

def test_faction_state_tracking(test_faction):
    """Test faction state tracking."""
    # Test initial state
    assert test_faction.state['active_wars'] == []
    assert test_faction.state['current_projects'] == []
    assert test_faction.state['statistics']['members_count'] == 0
    
    # Test state updates
    test_faction.state['active_wars'].append({
        'faction_id': 2,
        'started_at': datetime.utcnow().isoformat(),
        'cause': 'border_dispute'
    })
    test_faction.state['statistics']['members_count'] = 10
    
    assert len(test_faction.state['active_wars']) == 1
    assert test_faction.state['statistics']['members_count'] == 10

def test_faction_relation_type_transitions():
    """Test faction relationship type transitions."""
    rel = FactionRelation(faction_id=1, other_faction_id=2, relation_value=0)
    
    # Test transition to ALLIED
    rel.update_relation(80)
    assert rel.relation_type == RelationshipType.ALLIED.value
    
    # Test transition to FRIENDLY
    rel.update_relation(-60)
    assert rel.relation_type == RelationshipType.FRIENDLY.value
    
    # Test transition to NEUTRAL
    rel.update_relation(-30)
    assert rel.relation_type == RelationshipType.NEUTRAL.value
    
    # Test transition to HOSTILE
    rel.update_relation(-50)
    assert rel.relation_type == RelationshipType.HOSTILE.value
    
    # Test transition to WAR
    rel.update_relation(-50)
    assert rel.relation_type == RelationshipType.WAR.value 