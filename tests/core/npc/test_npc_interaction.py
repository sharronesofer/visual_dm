"""Tests for NPC interaction system with focus on outlaw status reactions."""

import pytest
from datetime import datetime, timedelta
from app.core.models.npc import NPCDisposition
from app.core.npc.system import NPCSystem
from app.core.models.character import Character
from app.core.models.consequence import Consequence
from app.core.enums import ConsequenceType
from app.utils.social import update_npc_disposition

@pytest.fixture
def npc_system(db_session):
    return NPCSystem(session=db_session)

@pytest.fixture
def outlaw_player(db_session):
    """Create a player with outlaw status."""
    player = Character(
        id=1,
        name="Test Outlaw",
        level=10
    )
    
    # Add active consequences
    consequence = Consequence(
        player_id=1,
        type=ConsequenceType.NPC_HOSTILITY,
        severity="major",
        expires_at=datetime.now() + timedelta(days=7)
    )
    
    db_session.add(player)
    db_session.add(consequence)
    db_session.commit()
    return player

@pytest.fixture
def regular_player(db_session):
    """Create a player without outlaw status."""
    player = Character(
        id=2,
        name="Test Regular",
        level=10
    )
    db_session.add(player)
    db_session.commit()
    return player

def test_npc_interaction_options_for_outlaw(npc_system, outlaw_player):
    """Test that outlaws receive limited interaction options."""
    options = npc_system.get_interaction_options(npc_id=1, player_id=outlaw_player.id)
    
    # Basic interactions should still be available
    assert any(opt['type'] == 'greet' for opt in options)
    
    # Restricted interactions should not be available
    assert not any(opt['type'] == 'ask_for_help' for opt in options)
    assert not any(opt['type'] == 'trade' for opt in options)
    
    # Verify relationship changes are more negative for outlaws
    greet_option = next(opt for opt in options if opt['type'] == 'greet')
    assert greet_option['relationship_change'] < 0

def test_npc_interaction_options_for_regular(npc_system, regular_player):
    """Test that regular players receive normal interaction options."""
    options = npc_system.get_interaction_options(npc_id=1, player_id=regular_player.id)
    
    # Should have access to all basic interactions
    assert any(opt['type'] == 'greet' for opt in options)
    assert any(opt['type'] == 'ask_about_backstory' for opt in options)
    
    # Relationship changes should be normal
    greet_option = next(opt for opt in options if opt['type'] == 'greet')
    assert greet_option['relationship_change'] > 0

def test_npc_disposition_update_for_outlaw(npc_system, outlaw_player):
    """Test that NPC disposition updates properly for outlaw interactions."""
    current_disposition = {'value': NPCDisposition.NEUTRAL.value}
    
    # Simulate interaction
    new_disposition = update_npc_disposition(
        npc_id=1,
        change=-2,  # Negative change due to outlaw status
        current_disposition=current_disposition
    )
    
    assert new_disposition['value'] < current_disposition['value']
    assert new_disposition['value'] >= NPCDisposition.HOSTILE.value

def test_npc_interaction_processing_for_outlaw(npc_system, outlaw_player):
    """Test that interaction processing handles outlaw status correctly."""
    result = npc_system.process_interaction(
        npc_id=1,
        player_id=outlaw_player.id,
        interaction_type='greet'
    )
    
    assert result['success'] is True
    assert 'hostile' in result['message'].lower()
    assert result['relationship_change'] < 0

def test_npc_interaction_processing_for_regular(npc_system, regular_player):
    """Test that interaction processing works normally for regular players."""
    result = npc_system.process_interaction(
        npc_id=1,
        player_id=regular_player.id,
        interaction_type='greet'
    )
    
    assert result['success'] is True
    assert result['relationship_change'] > 0
    assert 'hostile' not in result['message'].lower()

def test_faction_npc_reactions_to_outlaw(npc_system, outlaw_player):
    """Test that faction NPCs react appropriately to outlaw status."""
    # Test with a faction NPC
    result = npc_system.process_interaction(
        npc_id=2,  # Assuming this is a faction NPC
        player_id=outlaw_player.id,
        interaction_type='ask_about_faction'
    )
    
    assert result['success'] is False
    assert 'faction' in result['message'].lower()
    assert 'denied' in result['message'].lower()

def test_guard_npc_reactions_to_outlaw(npc_system, outlaw_player):
    """Test that guard NPCs react appropriately to outlaw status."""
    # Test with a guard NPC
    result = npc_system.process_interaction(
        npc_id=3,  # Assuming this is a guard NPC
        player_id=outlaw_player.id,
        interaction_type='greet'
    )
    
    assert result['success'] is False
    assert 'guard' in result['message'].lower()
    assert 'arrest' in result['message'].lower() or 'hostile' in result['message'].lower()

def test_merchant_npc_reactions_to_outlaw(npc_system, outlaw_player):
    """Test that merchant NPCs react appropriately to outlaw status."""
    # Test with a merchant NPC
    result = npc_system.process_interaction(
        npc_id=4,  # Assuming this is a merchant NPC
        player_id=outlaw_player.id,
        interaction_type='trade'
    )
    
    assert result['success'] is False
    assert 'merchant' in result['message'].lower()
    assert 'refuse' in result['message'].lower() 