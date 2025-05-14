"""
Hex asset preview tool with a simple UI.
"""

import pygame
import pygame_gui
import json
from typing import Dict, Any, Optional, List, Tuple, Set
from pathlib import Path
from ..managers.hex_asset_manager import HexAssetManager
from ..error_handler import handle_component_error, ErrorSeverity

class HexAssetPreview:
    """Preview tool for hex-based assets with advanced features."""
    
    def __init__(
        self,
        screen_size: Tuple[int, int] = (1024, 768),
        asset_dir: str = "assets"
    ):
        """Initialize the preview tool.
        
        Args:
            screen_size: Window dimensions
            asset_dir: Directory containing game assets
        """
        try:
            pygame.init()
            self.screen = pygame.display.set_mode(screen_size)
            pygame.display.set_caption("Hex Asset Preview")
            
            self.manager = pygame_gui.UIManager(screen_size)
            self.asset_manager = HexAssetManager(asset_dir)
            
            # Load preferences
            self.preferences = self._load_preferences()
            
            # UI elements - Left Panel
            self.left_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((0, 0), (250, screen_size[1])),
                manager=self.manager
            )
            
            # Search bar
            self.search_bar = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((10, 10), (230, 30)),
                manager=self.manager,
                container=self.left_panel
            )
            
            # Category dropdown
            self.category_dropdown = pygame_gui.elements.UIDropDownMenu(
                options_list=["base", "features", "overlay", "variations"],
                starting_option=self.preferences.get("last_category", "base"),
                relative_rect=pygame.Rect((10, 50), (230, 30)),
                manager=self.manager,
                container=self.left_panel
            )
            
            # Asset list
            self.asset_list = pygame_gui.elements.UISelectionList(
                relative_rect=pygame.Rect((10, 90), (230, screen_size[1] - 200)),
                item_list=[],
                manager=self.manager,
                container=self.left_panel
            )
            
            # Favorites button
            self.favorites_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((10, screen_size[1] - 100), (110, 30)),
                text="★ Favorites",
                manager=self.manager,
                container=self.left_panel
            )
            
            # Recent button
            self.recent_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((130, screen_size[1] - 100), (110, 30)),
                text="Recent",
                manager=self.manager,
                container=self.left_panel
            )
            
            # Preview Panel
            preview_width = screen_size[0] - 250
            self.preview_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((250, 0), (preview_width, screen_size[1])),
                manager=self.manager
            )
            
            # Preview controls
            self.zoom_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect((10, 10), (preview_width - 20, 20)),
                start_value=1.0,
                value_range=(0.5, 2.0),
                manager=self.manager,
                container=self.preview_panel
            )
            
            self.rotation_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect((10, 40), (preview_width - 20, 20)),
                start_value=0.0,
                value_range=(0.0, 360.0),
                manager=self.manager,
                container=self.preview_panel
            )
            
            # Preview area
            self.preview_rect = pygame.Rect(
                (10, 70),
                (preview_width - 20, screen_size[1] - 170)
            )
            
            # Info panel
            self.info_panel = pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect(
                    (10, screen_size[1] - 90),
                    (preview_width - 20, 80)
                ),
                html_text="",
                manager=self.manager,
                container=self.preview_panel
            )
            
            # State
            self.selected_asset: Optional[str] = None
            self.selected_surface: Optional[pygame.Surface] = None
            self.selected_metadata: Optional[Dict[str, Any]] = None
            self.zoom_level: float = 1.0
            self.rotation_angle: float = 0.0
            self.favorites: Set[str] = set(self.preferences.get("favorites", []))
            self.recent_assets: List[str] = self.preferences.get("recent_assets", [])
            self.showing_favorites: bool = False
            self.showing_recent: bool = False
            self.search_query: str = ""
            
            # Load initial assets
            self._load_category_assets(self.preferences.get("last_category", "base"))
            
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "__init__",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def _load_preferences(self) -> Dict[str, Any]:
        """Load user preferences from file."""
        try:
            prefs_path = Path("user_preferences.json")
            if prefs_path.exists():
                with open(prefs_path, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "_load_preferences",
                e,
                ErrorSeverity.LOW
            )
            return {}
            
    def _save_preferences(self) -> None:
        """Save user preferences to file."""
        try:
            prefs = {
                "last_category": self.category_dropdown.selected_option,
                "favorites": list(self.favorites),
                "recent_assets": self.recent_assets[:20],  # Keep last 20
                "zoom_level": self.zoom_level,
                "rotation_angle": self.rotation_angle
            }
            with open("user_preferences.json", "w") as f:
                json.dump(prefs, f)
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "_save_preferences",
                e,
                ErrorSeverity.LOW
            )
            
    def _load_category_assets(self, category: str) -> None:
        """Load assets for a specific category.
        
        Args:
            category: Asset category to load
        """
        try:
            path = Path(self.asset_manager.asset_dir) / "terrain" / category
            assets = list(path.glob("*.png"))
            
            # Filter by search query if any
            if self.search_query:
                query = self.search_query.lower()
                assets = [a for a in assets if query in a.name.lower()]
            
            # Add favorite indicator
            items = []
            for asset in assets:
                prefix = "★ " if asset.name in self.favorites else ""
                items.append(f"{prefix}{asset.name}")
            
            self.asset_list.set_item_list(items)
            
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "_load_category_assets",
                e,
                ErrorSeverity.ERROR,
                {"category": category}
            )
            
    def _load_asset(self, path: str, category: str) -> None:
        """Load a specific asset for preview.
        
        Args:
            path: Asset path
            category: Asset category
        """
        try:
            self.selected_asset = path
            self.selected_surface = self.asset_manager.load_hex_image(
                path,
                category,
                lazy=False
            )
            self.selected_metadata = self.asset_manager.get_hex_metadata(path)
            
            # Update recent assets
            if path in self.recent_assets:
                self.recent_assets.remove(path)
            self.recent_assets.insert(0, path)
            if len(self.recent_assets) > 20:
                self.recent_assets.pop()
            
            # Update info panel
            if self.selected_metadata:
                info_text = f"<b>{path}</b><br>"
                info_text += f"Category: {category}<br>"
                info_text += f"Size: {self.selected_surface.get_width()}x{self.selected_surface.get_height()}<br>"
                info_text += f"Memory: {self.selected_metadata['memory'] / 1024:.1f} KB"
                self.info_panel.html_text = info_text
                self.info_panel.rebuild()
            
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "_load_asset",
                e,
                ErrorSeverity.ERROR,
                {"path": path, "category": category}
            )
            
    def _toggle_favorite(self, path: str) -> None:
        """Toggle favorite status of an asset.
        
        Args:
            path: Asset path
        """
        try:
            if path in self.favorites:
                self.favorites.remove(path)
            else:
                self.favorites.add(path)
            
            # Reload current view
            if self.showing_favorites:
                self._show_favorites()
            else:
                self._load_category_assets(self.category_dropdown.selected_option)
                
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "_toggle_favorite",
                e,
                ErrorSeverity.LOW
            )
            
    def _show_favorites(self) -> None:
        """Show only favorite assets."""
        try:
            self.showing_favorites = True
            self.showing_recent = False
            
            # Collect favorites from all categories
            items = []
            for category in ["base", "features", "overlay", "variations"]:
                path = Path(self.asset_manager.asset_dir) / "terrain" / category
                assets = [a for a in path.glob("*.png") if a.name in self.favorites]
                items.extend([f"★ {a.name}" for a in assets])
            
            self.asset_list.set_item_list(items)
            
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "_show_favorites",
                e,
                ErrorSeverity.LOW
            )
            
    def _show_recent(self) -> None:
        """Show recently used assets."""
        try:
            self.showing_recent = True
            self.showing_favorites = False
            
            items = []
            for path in self.recent_assets:
                prefix = "★ " if path in self.favorites else ""
                items.append(f"{prefix}{Path(path).name}")
            
            self.asset_list.set_item_list(items)
            
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "_show_recent",
                e,
                ErrorSeverity.LOW
            )
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle a pygame event.
        
        Args:
            event: The event to handle
            
        Returns:
            bool: True if event was handled
        """
        try:
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.category_dropdown:
                        self.showing_favorites = False
                        self.showing_recent = False
                        self._load_category_assets(event.text)
                        return True
                        
                elif event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    if event.ui_element == self.search_bar:
                        self.search_query = event.text
                        if not self.showing_favorites and not self.showing_recent:
                            self._load_category_assets(self.category_dropdown.selected_option)
                        return True
                        
                elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.favorites_button:
                        if not self.showing_favorites:
                            self._show_favorites()
                        else:
                            self.showing_favorites = False
                            self._load_category_assets(self.category_dropdown.selected_option)
                        return True
                        
                    elif event.ui_element == self.recent_button:
                        if not self.showing_recent:
                            self._show_recent()
                        else:
                            self.showing_recent = False
                            self._load_category_assets(self.category_dropdown.selected_option)
                        return True
                        
                elif event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    if event.ui_element == self.asset_list:
                        # Strip favorite indicator if present
                        asset_name = event.text[2:] if event.text.startswith("★ ") else event.text
                        category = self.category_dropdown.selected_option
                        self._load_asset(asset_name, category)
                        return True
                        
                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == self.zoom_slider:
                        self.zoom_level = event.value
                        return True
                    elif event.ui_element == self.rotation_slider:
                        self.rotation_angle = event.value
                        return True
                        
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and event.mod & pygame.KMOD_CTRL:
                    # Ctrl+F to focus search
                    self.search_bar.focus()
                    return True
                elif event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                    # Ctrl+S to toggle favorite for selected asset
                    if self.selected_asset:
                        self._toggle_favorite(self.selected_asset)
                        return True
                        
            return self.manager.process_events(event)
            
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "handle_event",
                e,
                ErrorSeverity.MEDIUM
            )
            return False
            
    def update(self, time_delta: float) -> None:
        """Update the preview tool.
        
        Args:
            time_delta: Time since last update in seconds
        """
        try:
            self.manager.update(time_delta)
            
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "update",
                e,
                ErrorSeverity.LOW
            )
            
    def draw(self) -> None:
        """Draw the preview tool."""
        try:
            self.screen.fill((40, 40, 40))
            
            # Draw preview
            if self.selected_surface:
                # Create a copy for transformation
                preview = self.selected_surface.copy()
                
                # Apply zoom
                if self.zoom_level != 1.0:
                    new_size = (
                        int(preview.get_width() * self.zoom_level),
                        int(preview.get_height() * self.zoom_level)
                    )
                    preview = pygame.transform.scale(preview, new_size)
                
                # Apply rotation
                if self.rotation_angle != 0.0:
                    preview = pygame.transform.rotate(preview, self.rotation_angle)
                
                # Center in preview area
                preview_x = self.preview_rect.centerx - preview.get_width() // 2
                preview_y = self.preview_rect.centery - preview.get_height() // 2
                self.screen.blit(preview, (preview_x, preview_y))
            
            self.manager.draw_ui(self.screen)
            pygame.display.update()
            
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "draw",
                e,
                ErrorSeverity.LOW
            )
            
    def run(self) -> None:
        """Run the preview tool."""
        try:
            clock = pygame.time.Clock()
            running = True
            
            while running:
                time_delta = clock.tick(60)/1000.0
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                        
                    self.handle_event(event)
                    
                self.update(time_delta)
                self.draw()
            
            # Save preferences before exit
            self._save_preferences()
            pygame.quit()
            
        except Exception as e:
            handle_component_error(
                "HexAssetPreview",
                "run",
                e,
                ErrorSeverity.ERROR
            )
            pygame.quit()
            
if __name__ == "__main__":
    preview = HexAssetPreview()
    preview.run() 