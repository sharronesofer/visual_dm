"""Tests for the NPC viewer panel with focus on outlaw status display."""

import pytest
import pygame
from unittest.mock import Mock, patch
from visual_client.ui.screens.game.npc_viewer_panel import NPCViewerPanel

@pytest.fixture
def mock_screen():
    return Mock(spec=pygame.Surface)

@pytest.fixture
def mock_fonts():
    with patch('pygame.font.Font') as mock_font:
        mock_font.return_value.render.return_value = Mock(spec=pygame.Surface)
        yield mock_font

@pytest.fixture
def npc_viewer(mock_screen, mock_fonts):
    panel = NPCViewerPanel(mock_screen, "region_1", "poi_1")
    # Mock the fonts to avoid pygame initialization
    panel.font = mock_fonts()
    panel.large_font = mock_fonts()
    return panel

@pytest.fixture
def mock_npc_data():
    return {
        "regular_npc": {
            "name": "Friendly Merchant",
            "faction": "Traders Guild",
            "goodwill": 50,  # Neutral-positive goodwill
        },
        "hostile_to_outlaw": {
            "name": "Guard Captain",
            "faction": "City Watch",
            "goodwill": -80,  # Very negative goodwill for outlaws
        }
    }

def test_panel_initialization(npc_viewer):
    """Test that the panel initializes correctly."""
    assert npc_viewer.screen is not None
    assert npc_viewer.region_id == "region_1"
    assert npc_viewer.poi_id == "poi_1"

def test_draw_no_npcs(npc_viewer):
    """Test panel display when no NPCs are present."""
    npc_viewer.npcs = []
    npc_viewer.draw()
    
    # Should display "No NPCs found" message
    npc_viewer.font.render.assert_any_call("No NPCs found.", True, (200, 200, 200))

@patch('visual_client.ui.screens.game.npc_viewer_panel.NPCViewerPanel.fetch_npc_details')
def test_draw_npc_list(mock_fetch, npc_viewer, mock_npc_data):
    """Test that NPCs are listed correctly."""
    npc_viewer.npcs = ["regular_npc", "hostile_to_outlaw"]
    mock_fetch.side_effect = lambda npc_id: mock_npc_data[npc_id]
    
    npc_viewer.draw()
    
    # Should render NPC names
    npc_viewer.font.render.assert_any_call("regular_npc", True, (255, 255, 255))
    npc_viewer.font.render.assert_any_call("hostile_to_outlaw", True, (255, 255, 255))

@patch('visual_client.ui.screens.game.npc_viewer_panel.NPCViewerPanel.fetch_npc_details')
def test_draw_selected_npc_details(mock_fetch, npc_viewer, mock_npc_data):
    """Test that selected NPC details are displayed correctly."""
    npc_viewer.npcs = ["regular_npc"]
    npc_viewer.selected_npc = 0
    mock_fetch.return_value = mock_npc_data["regular_npc"]
    
    npc_viewer.draw()
    
    # Should display NPC details
    npc_viewer.font.render.assert_any_call("Name: Friendly Merchant", True, (180, 220, 255))
    npc_viewer.font.render.assert_any_call("Faction: Traders Guild", True, (180, 220, 255))
    npc_viewer.font.render.assert_any_call("Goodwill", True, (255, 255, 255))

@patch('visual_client.ui.screens.game.npc_viewer_panel.NPCViewerPanel.fetch_npc_details')
def test_draw_hostile_npc_to_outlaw(mock_fetch, npc_viewer, mock_npc_data):
    """Test that hostile NPC reactions to outlaws are displayed correctly."""
    npc_viewer.npcs = ["hostile_to_outlaw"]
    npc_viewer.selected_npc = 0
    mock_fetch.return_value = mock_npc_data["hostile_to_outlaw"]
    
    npc_viewer.draw()
    
    # Should show very negative goodwill
    # Verify the goodwill bar is rendered with appropriate size and color
    pygame.draw.rect.assert_any_call(
        npc_viewer.screen,
        (80, 80, 80),  # Background color
        pytest.approx((780, mock.ANY, 200, 20))  # Position and size
    )
    
    # The fill should be small due to negative goodwill
    pygame.draw.rect.assert_any_call(
        npc_viewer.screen,
        (0, 255, 0),  # Fill color
        pytest.approx((780, mock.ANY, 20, 20))  # Position and small width
    )

@patch('visual_client.ui.screens.game.npc_viewer_panel.NPCViewerPanel.fetch_npc_details')
def test_draw_regular_npc_goodwill(mock_fetch, npc_viewer, mock_npc_data):
    """Test that regular NPC goodwill is displayed correctly."""
    npc_viewer.npcs = ["regular_npc"]
    npc_viewer.selected_npc = 0
    mock_fetch.return_value = mock_npc_data["regular_npc"]
    
    npc_viewer.draw()
    
    # Should show neutral-positive goodwill
    # Verify the goodwill bar is rendered with appropriate size
    pygame.draw.rect.assert_any_call(
        npc_viewer.screen,
        (80, 80, 80),  # Background color
        pytest.approx((780, mock.ANY, 200, 20))  # Position and size
    )
    
    # The fill should be about half due to neutral-positive goodwill
    pygame.draw.rect.assert_any_call(
        npc_viewer.screen,
        (0, 255, 0),  # Fill color
        pytest.approx((780, mock.ANY, 150, 20))  # Position and medium width
    )

def test_npc_selection(npc_viewer):
    """Test that NPC selection works correctly."""
    npc_viewer.npcs = ["npc1", "npc2", "npc3"]
    
    # Test selection
    npc_viewer.selected_npc = 1
    npc_viewer.draw()
    
    # Selected NPC should be highlighted
    npc_viewer.font.render.assert_any_call("npc2", True, (0, 255, 100))
    # Other NPCs should be normal color
    npc_viewer.font.render.assert_any_call("npc1", True, (255, 255, 255))
    npc_viewer.font.render.assert_any_call("npc3", True, (255, 255, 255)) 