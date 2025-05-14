"""
UI tool for previewing and selecting hex-based assets.
"""

import pygame
import pygame_gui
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json
from ..managers.hex_asset_manager import HexAssetManager
from ..managers.hex_asset_metadata import HexAssetMetadataManager
from ..managers.hex_asset_cache import HexAssetCache
from ..managers.hex_sprite_sheet import HexSpriteSheet
from ..managers.hex_asset_renderer import HexAssetRenderer
from ..error_handler import handle_component_error, ErrorSeverity

class HexAssetPreviewUI:
    """UI tool for browsing and previewing hex-based assets."""
    
    def __init__(
        self,
        asset_manager: HexAssetManager,
        metadata_manager: HexAssetMetadataManager,
        cache: HexAssetCache,
        window_size: Tuple[int, int] = (1280, 720)
    ):
        """Initialize the preview UI.
        
        Args:
            asset_manager: Manager for hex assets
            metadata_manager: Manager for asset metadata
            cache: Asset cache system
            window_size: Window dimensions
        """
        try:
            pygame.init()
            self.window_size = window_size
            self.window_surface = pygame.display.set_mode(window_size)
            pygame.display.set_caption("Hex Asset Preview")
            
            self.asset_manager = asset_manager
            self.metadata_manager = metadata_manager
            self.cache = cache
            
            # Initialize UI manager
            self.ui_manager = pygame_gui.UIManager(window_size)
            
            # Create UI elements
            self.setup_ui()
            
            # Initialize state
            self.selected_category = "base"
            self.selected_asset = None
            self.search_text = ""
            self.favorites = set()
            self.recent_assets = []
            self.max_recent = 10
            self.zoom_level = 1.0
            self.rotation = 0
            
            # Load saved preferences
            self.load_preferences()
            
        except Exception as e:
            handle_component_error(
                e,
                "Failed to initialize hex asset preview UI",
                ErrorSeverity.ERROR,
                component="HexAssetPreviewUI"
            )
    
    def setup_ui(self):
        """Set up UI elements."""
        try:
            # Category panel
            self.category_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((0, 0), (200, self.window_size[1])),
                manager=self.ui_manager
            )
            
            # Category buttons
            categories = ["base", "features", "overlay", "effects"]
            for i, category in enumerate(categories):
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((10, 10 + i * 40), (180, 30)),
                    text=category.title(),
                    manager=self.ui_manager,
                    container=self.category_panel
                )
            
            # Asset list panel
            self.asset_list_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(
                    (200, 0),
                    (300, self.window_size[1])
                ),
                manager=self.ui_manager
            )
            
            # Search box
            self.search_box = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((10, 10), (280, 30)),
                manager=self.ui_manager,
                container=self.asset_list_panel
            )
            
            # Asset list
            self.asset_list = pygame_gui.elements.UISelectionList(
                relative_rect=pygame.Rect(
                    (10, 50),
                    (280, self.window_size[1] - 60)
                ),
                item_list=[],
                manager=self.ui_manager,
                container=self.asset_list_panel
            )
            
            # Preview panel
            self.preview_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(
                    (500, 0),
                    (self.window_size[0] - 500, self.window_size[1])
                ),
                manager=self.ui_manager
            )
            
            # Preview controls
            self.zoom_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(
                    (10, 10),
                    (200, 20)
                ),
                start_value=1.0,
                value_range=(0.5, 2.0),
                manager=self.ui_manager,
                container=self.preview_panel
            )
            
            self.rotation_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(
                    (10, 40),
                    (200, 20)
                ),
                start_value=0,
                value_range=(0, 360),
                manager=self.ui_manager,
                container=self.preview_panel
            )
            
            # Favorite button
            self.favorite_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (10, 70),
                    (30, 30)
                ),
                text="★",
                manager=self.ui_manager,
                container=self.preview_panel
            )
            
            # Asset info panel
            self.info_panel = pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect(
                    (10, self.window_size[1] - 200),
                    (self.window_size[0] - 520, 190)
                ),
                html_text="Select an asset to view details",
                manager=self.ui_manager,
                container=self.preview_panel
            )
            
        except Exception as e:
            handle_component_error(
                e,
                "Failed to set up UI elements",
                ErrorSeverity.ERROR,
                component="HexAssetPreviewUI"
            )
    
    def load_preferences(self):
        """Load saved preferences from file."""
        try:
            prefs_path = Path("preferences/hex_asset_preview.json")
            if prefs_path.exists():
                with open(prefs_path, "r") as f:
                    prefs = json.load(f)
                    self.favorites = set(prefs.get("favorites", []))
                    self.recent_assets = prefs.get("recent", [])
                    self.zoom_level = prefs.get("zoom", 1.0)
                    self.rotation = prefs.get("rotation", 0)
                    
        except Exception as e:
            handle_component_error(
                e,
                "Failed to load preferences",
                ErrorSeverity.WARNING,
                component="HexAssetPreviewUI"
            )
    
    def save_preferences(self):
        """Save preferences to file."""
        try:
            prefs_path = Path("preferences/hex_asset_preview.json")
            prefs_path.parent.mkdir(parents=True, exist_ok=True)
            
            prefs = {
                "favorites": list(self.favorites),
                "recent": self.recent_assets,
                "zoom": self.zoom_level,
                "rotation": self.rotation
            }
            
            with open(prefs_path, "w") as f:
                json.dump(prefs, f, indent=2)
                
        except Exception as e:
            handle_component_error(
                e,
                "Failed to save preferences",
                ErrorSeverity.WARNING,
                component="HexAssetPreviewUI"
            )
    
    def update_asset_list(self):
        """Update the asset list based on current category and search."""
        try:
            # Get assets for current category
            assets = self.metadata_manager.search_assets(
                category=self.selected_category,
                search_term=self.search_text
            )
            
            # Create list items
            items = []
            for asset in assets:
                name = asset.name
                if asset.asset_id in self.favorites:
                    name = "★ " + name
                items.append(name)
            
            # Update list
            self.asset_list.set_item_list(items)
            
        except Exception as e:
            handle_component_error(
                e,
                "Failed to update asset list",
                ErrorSeverity.ERROR,
                component="HexAssetPreviewUI"
            )
    
    def update_preview(self):
        """Update the preview display."""
        try:
            if not self.selected_asset:
                return
                
            # Get asset surface
            surface = self.cache.get(self.selected_asset.asset_id)
            if surface is None:
                surface = self.asset_manager.load_asset(
                    self.selected_asset.asset_id
                )
                self.cache.put(self.selected_asset.asset_id, surface)
            
            # Apply transformations
            if self.zoom_level != 1.0:
                size = surface.get_size()
                new_size = (
                    int(size[0] * self.zoom_level),
                    int(size[1] * self.zoom_level)
                )
                surface = pygame.transform.scale(surface, new_size)
            
            if self.rotation != 0:
                surface = pygame.transform.rotate(surface, self.rotation)
            
            # Calculate center position
            preview_rect = self.preview_panel.get_abs_rect()
            surface_rect = surface.get_rect()
            pos = (
                preview_rect.centerx - surface_rect.width // 2,
                preview_rect.centery - surface_rect.height // 2
            )
            
            # Draw preview
            self.window_surface.blit(surface, pos)
            
            # Update info panel
            info_text = f"""
            <b>Asset Details</b><br>
            ID: {self.selected_asset.asset_id}<br>
            Category: {self.selected_asset.category}<br>
            Subcategory: {self.selected_asset.subcategory}<br>
            Dimensions: {self.selected_asset.dimensions[0]}x{self.selected_asset.dimensions[1]}<br>
            Memory Size: {self.selected_asset.memory_size // 1024} KB<br>
            Has Variations: {"Yes" if self.selected_asset.has_variations else "No"}<br>
            Tags: {", ".join(self.selected_asset.tags)}<br>
            """
            self.info_panel.html_text = info_text
            self.info_panel.rebuild()
            
        except Exception as e:
            handle_component_error(
                e,
                "Failed to update preview",
                ErrorSeverity.ERROR,
                component="HexAssetPreviewUI"
            )
    
    def handle_event(self, event: pygame.event.Event):
        """Handle a pygame event.
        
        Args:
            event: The event to handle
        """
        try:
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    # Category selection
                    if event.ui_element in self.category_panel.elements:
                        self.selected_category = event.ui_element.text.lower()
                        self.update_asset_list()
                    
                    # Favorite toggle
                    elif event.ui_element == self.favorite_button:
                        if self.selected_asset:
                            if self.selected_asset.asset_id in self.favorites:
                                self.favorites.remove(self.selected_asset.asset_id)
                            else:
                                self.favorites.add(self.selected_asset.asset_id)
                            self.update_asset_list()
                            self.save_preferences()
                
                elif event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    if event.ui_element == self.search_box:
                        self.search_text = event.text
                        self.update_asset_list()
                
                elif event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    if event.ui_element == self.asset_list:
                        # Get selected asset metadata
                        name = event.text
                        if name.startswith("★ "):
                            name = name[2:]
                        
                        assets = self.metadata_manager.search_assets(
                            category=self.selected_category,
                            name=name
                        )
                        if assets:
                            self.selected_asset = assets[0]
                            
                            # Update recent assets
                            if self.selected_asset.asset_id in self.recent_assets:
                                self.recent_assets.remove(
                                    self.selected_asset.asset_id
                                )
                            self.recent_assets.insert(
                                0,
                                self.selected_asset.asset_id
                            )
                            if len(self.recent_assets) > self.max_recent:
                                self.recent_assets.pop()
                            
                            self.save_preferences()
                
                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == self.zoom_slider:
                        self.zoom_level = event.value
                        self.save_preferences()
                    elif event.ui_element == self.rotation_slider:
                        self.rotation = event.value
                        self.save_preferences()
            
            self.ui_manager.process_events(event)
            
        except Exception as e:
            handle_component_error(
                e,
                "Failed to handle event",
                ErrorSeverity.ERROR,
                component="HexAssetPreviewUI"
            )
    
    def run(self):
        """Run the preview UI."""
        try:
            clock = pygame.time.Clock()
            running = True
            
            while running:
                time_delta = clock.tick(60)/1000.0
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    self.handle_event(event)
                
                self.ui_manager.update(time_delta)
                
                self.window_surface.fill((40, 40, 40))
                self.update_preview()
                self.ui_manager.draw_ui(self.window_surface)
                
                pygame.display.update()
            
            pygame.quit()
            self.save_preferences()
            
        except Exception as e:
            handle_component_error(
                e,
                "Failed to run preview UI",
                ErrorSeverity.ERROR,
                component="HexAssetPreviewUI"
            ) 