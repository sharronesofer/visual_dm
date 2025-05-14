"""
Tests for the hex asset preview UI.
"""

import pytest
import pygame
import pygame_gui
from pathlib import Path
import json
import shutil
from unittest.mock import MagicMock, patch
from visual_client.core.tools.hex_asset_preview_ui import HexAssetPreviewUI
from visual_client.core.managers.hex_asset_manager import HexAssetManager
from visual_client.core.managers.hex_asset_metadata import HexAssetMetadataManager, AssetMetadata
from visual_client.core.managers.hex_asset_cache import HexAssetCache

@pytest.fixture
def mock_managers():
    """Create mock managers for testing."""
    asset_manager = MagicMock(spec=HexAssetManager)
    metadata_manager = MagicMock(spec=HexAssetMetadataManager)
    cache = MagicMock(spec=HexAssetCache)
    
    # Create test asset metadata
    test_assets = [
        AssetMetadata(
            asset_id=f"test_{i}",
            category="base",
            subcategory="terrain",
            name=f"Test Asset {i}",
            path=f"assets/terrain/base/test_{i}.png",
            dimensions=(64, 64),
            has_variations=bool(i % 2),
            variation_types=["snow", "autumn"] if i % 2 else [],
            color_palette=["#FF0000", "#00FF00"],
            memory_size=4096,
            tags=["test", f"tag_{i}"]
        )
        for i in range(5)
    ]
    
    # Configure mock metadata manager
    metadata_manager.search_assets.return_value = test_assets
    
    # Configure mock asset manager
    def mock_load_asset(asset_id):
        surface = pygame.Surface((64, 64))
        surface.fill((255, 0, 0))
        return surface
    
    asset_manager.load_asset.side_effect = mock_load_asset
    
    return asset_manager, metadata_manager, cache

@pytest.fixture
def preview_ui(mock_managers, tmp_path):
    """Create a test preview UI instance."""
    asset_manager, metadata_manager, cache = mock_managers
    
    # Create test preferences directory
    prefs_dir = tmp_path / "preferences"
    prefs_dir.mkdir()
    
    with patch("pathlib.Path") as mock_path:
        mock_path.return_value.parent = prefs_dir
        mock_path.return_value.exists.return_value = False
        
        ui = HexAssetPreviewUI(
            asset_manager,
            metadata_manager,
            cache,
            window_size=(800, 600)
        )
        
        return ui

def test_initialization(preview_ui, mock_managers):
    """Test preview UI initialization."""
    asset_manager, metadata_manager, cache = mock_managers
    
    assert preview_ui.window_size == (800, 600)
    assert preview_ui.asset_manager == asset_manager
    assert preview_ui.metadata_manager == metadata_manager
    assert preview_ui.cache == cache
    assert preview_ui.selected_category == "base"
    assert preview_ui.selected_asset is None
    assert preview_ui.search_text == ""
    assert len(preview_ui.favorites) == 0
    assert len(preview_ui.recent_assets) == 0
    assert preview_ui.zoom_level == 1.0
    assert preview_ui.rotation == 0

def test_ui_elements(preview_ui):
    """Test UI element creation."""
    # Check category panel
    assert preview_ui.category_panel is not None
    assert len([e for e in preview_ui.category_panel.elements 
               if isinstance(e, pygame_gui.elements.UIButton)]) == 4
    
    # Check asset list panel
    assert preview_ui.asset_list_panel is not None
    assert preview_ui.search_box is not None
    assert preview_ui.asset_list is not None
    
    # Check preview panel
    assert preview_ui.preview_panel is not None
    assert preview_ui.zoom_slider is not None
    assert preview_ui.rotation_slider is not None
    assert preview_ui.favorite_button is not None
    assert preview_ui.info_panel is not None

def test_preferences(preview_ui, tmp_path):
    """Test preferences loading and saving."""
    # Create test preferences
    prefs = {
        "favorites": ["test_1", "test_2"],
        "recent": ["test_3", "test_4"],
        "zoom": 1.5,
        "rotation": 90
    }
    
    prefs_path = tmp_path / "preferences/hex_asset_preview.json"
    prefs_path.parent.mkdir(exist_ok=True)
    
    with open(prefs_path, "w") as f:
        json.dump(prefs, f)
    
    # Test loading
    with patch("pathlib.Path") as mock_path:
        mock_path.return_value = prefs_path
        mock_path.return_value.exists.return_value = True
        preview_ui.load_preferences()
        
        assert preview_ui.favorites == set(["test_1", "test_2"])
        assert preview_ui.recent_assets == ["test_3", "test_4"]
        assert preview_ui.zoom_level == 1.5
        assert preview_ui.rotation == 90
    
    # Test saving
    preview_ui.favorites.add("test_5")
    preview_ui.recent_assets.append("test_6")
    preview_ui.zoom_level = 2.0
    preview_ui.rotation = 180
    
    with patch("pathlib.Path") as mock_path:
        mock_path.return_value = prefs_path
        preview_ui.save_preferences()
    
    with open(prefs_path, "r") as f:
        saved_prefs = json.load(f)
        assert "test_5" in saved_prefs["favorites"]
        assert "test_6" in saved_prefs["recent"]
        assert saved_prefs["zoom"] == 2.0
        assert saved_prefs["rotation"] == 180

def test_asset_list_update(preview_ui, mock_managers):
    """Test asset list updating."""
    asset_manager, metadata_manager, cache = mock_managers
    
    # Test initial update
    preview_ui.update_asset_list()
    assert len(preview_ui.asset_list.item_list) == 5
    
    # Test with search
    preview_ui.search_text = "3"
    metadata_manager.search_assets.return_value = [
        AssetMetadata(
            asset_id="test_3",
            category="base",
            subcategory="terrain",
            name="Test Asset 3",
            path="assets/terrain/base/test_3.png",
            dimensions=(64, 64),
            has_variations=True,
            variation_types=["snow", "autumn"],
            color_palette=["#FF0000"],
            memory_size=4096,
            tags=["test"]
        )
    ]
    preview_ui.update_asset_list()
    assert len(preview_ui.asset_list.item_list) == 1
    assert "Test Asset 3" in preview_ui.asset_list.item_list[0]

def test_preview_update(preview_ui, mock_managers):
    """Test preview updating."""
    asset_manager, metadata_manager, cache = mock_managers
    
    # Set up test asset
    test_asset = AssetMetadata(
        asset_id="test_1",
        category="base",
        subcategory="terrain",
        name="Test Asset 1",
        path="assets/terrain/base/test_1.png",
        dimensions=(64, 64),
        has_variations=True,
        variation_types=["snow", "autumn"],
        color_palette=["#FF0000"],
        memory_size=4096,
        tags=["test"]
    )
    preview_ui.selected_asset = test_asset
    
    # Test basic preview
    preview_ui.update_preview()
    assert cache.get.called
    assert asset_manager.load_asset.called
    
    # Test with zoom
    preview_ui.zoom_level = 2.0
    preview_ui.update_preview()
    
    # Test with rotation
    preview_ui.rotation = 90
    preview_ui.update_preview()

def test_event_handling(preview_ui, mock_managers):
    """Test event handling."""
    asset_manager, metadata_manager, cache = mock_managers
    
    # Test category selection
    event = pygame.event.Event(
        pygame.USEREVENT,
        {
            "user_type": pygame_gui.UI_BUTTON_PRESSED,
            "ui_element": list(preview_ui.category_panel.elements)[0]
        }
    )
    preview_ui.handle_event(event)
    assert preview_ui.selected_category == "base"
    
    # Test search
    event = pygame.event.Event(
        pygame.USEREVENT,
        {
            "user_type": pygame_gui.UI_TEXT_ENTRY_CHANGED,
            "ui_element": preview_ui.search_box,
            "text": "test"
        }
    )
    preview_ui.handle_event(event)
    assert preview_ui.search_text == "test"
    
    # Test asset selection
    event = pygame.event.Event(
        pygame.USEREVENT,
        {
            "user_type": pygame_gui.UI_SELECTION_LIST_NEW_SELECTION,
            "ui_element": preview_ui.asset_list,
            "text": "Test Asset 1"
        }
    )
    preview_ui.handle_event(event)
    assert preview_ui.selected_asset is not None
    
    # Test favorite toggle
    event = pygame.event.Event(
        pygame.USEREVENT,
        {
            "user_type": pygame_gui.UI_BUTTON_PRESSED,
            "ui_element": preview_ui.favorite_button
        }
    )
    preview_ui.handle_event(event)
    assert len(preview_ui.favorites) == 1
    
    # Test zoom
    event = pygame.event.Event(
        pygame.USEREVENT,
        {
            "user_type": pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
            "ui_element": preview_ui.zoom_slider,
            "value": 1.5
        }
    )
    preview_ui.handle_event(event)
    assert preview_ui.zoom_level == 1.5
    
    # Test rotation
    event = pygame.event.Event(
        pygame.USEREVENT,
        {
            "user_type": pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
            "ui_element": preview_ui.rotation_slider,
            "value": 90
        }
    )
    preview_ui.handle_event(event)
    assert preview_ui.rotation == 90 