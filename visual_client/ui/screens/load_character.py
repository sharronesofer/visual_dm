"""
Load character screen with comprehensive user feedback.

This module provides a character loading screen that:
1. Shows clear loading states and progress
2. Provides detailed error messages with recovery options
3. Implements progress indicators for long operations
4. Offers retry mechanisms for failed operations
5. Maintains a loading history for debugging
"""

import pygame
import requests
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum, auto
from app.core.utils.error_utils import ScreenError, ResourceError
from app.core.utils.screen_utils import ScreenManager
from app.core.utils.input_utils import InputHandler
from app.core.utils.render_utils import Renderer
from app.ui.components import (
    Button,
    Panel,
    ComponentStyle,
    BaseComponent,
    ProgressBar,
    Label
)
from visual_client.screens.start_game import StartGameScreen

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadState(Enum):
    """Enumeration of possible loading states."""
    IDLE = auto()
    LOADING = auto()
    SUCCESS = auto()
    ERROR = auto()
    RETRYING = auto()

@dataclass
class LoadHistory:
    """Record of loading attempts and their outcomes."""
    timestamp: float
    character_id: str
    success: bool
    error_message: Optional[str]
    retry_count: int

class LoadCharacterScreen:
    """Load character screen with comprehensive user feedback."""
    
    def __init__(self, screen_manager: ScreenManager):
        """Initialize the load character screen.
        
        Args:
            screen_manager: Screen manager instance
        """
        self.screen_manager = screen_manager
        self.state = LoadState.IDLE
        self.loading_progress = 0.0
        self.error_message = None
        self.retry_count = 0
        self.max_retries = 3
        self.load_history: List[LoadHistory] = []
        self.selected_character: Optional[Dict[str, Any]] = None
        self.character_list: List[Dict[str, Any]] = []
        
        # Initialize UI components
        self._initialize_components()
        
    def _initialize_components(self) -> None:
        """Initialize UI components with error handling."""
        try:
            screen_rect = self.screen_manager.get_screen_rect()
            
            # Main panel
            self.main_panel = Panel(
                pygame.Rect(0, 0, screen_rect.width, screen_rect.height),
                ComponentStyle(background_color=(30, 30, 30))
            )
            
            # Status panel
            self.status_panel = Panel(
                pygame.Rect(
                    screen_rect.width // 2 - 200,
                    screen_rect.height - 100,
                    400,
                    80
                ),
                ComponentStyle(
                    background_color=(40, 40, 40),
                    border_width=1
                )
            )
            
            # Progress bar
            self.progress_bar = ProgressBar(
                pygame.Rect(
                    screen_rect.width // 2 - 150,
                    screen_rect.height - 60,
                    300,
                    20
                ),
                ComponentStyle(
                    background_color=(50, 50, 50),
                    active_color=(0, 255, 0)
                )
            )
            
            # Status label
            self.status_label = Label(
                pygame.Rect(
                    screen_rect.width // 2 - 150,
                    screen_rect.height - 90,
                    300,
                    30
                ),
                "",
                ComponentStyle(
                    font_color=(255, 255, 255),
                    font_size=16
                )
            )
            
            # Character list panel
            self.character_panel = Panel(
                pygame.Rect(
                    50,
                    50,
                    screen_rect.width - 100,
                    screen_rect.height - 200
                ),
                ComponentStyle(
                    background_color=(40, 40, 40),
                    border_width=1
                )
            )
            
            # Action buttons
            self._create_action_buttons()
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {str(e)}")
            self._create_fallback_components()
            
    def _create_action_buttons(self) -> None:
        """Create action buttons with error handling."""
        try:
            screen_rect = self.screen_manager.get_screen_rect()
            button_style = ComponentStyle(
                background_color=(70, 70, 70),
                hover_color=(100, 100, 100),
                font_size=16
            )
            
            # Load button
            self.load_button = Button(
                pygame.Rect(
                    screen_rect.width // 2 - 100,
                    screen_rect.height - 40,
                    200,
                    30
                ),
                "Load Character",
                button_style,
                self.main_panel
            )
            self.load_button.add_callback('click', self._handle_load)
            
            # Back button
            self.back_button = Button(
                pygame.Rect(
                    20,
                    screen_rect.height - 40,
                    100,
                    30
                ),
                "Back",
                button_style,
                self.main_panel
            )
            self.back_button.add_callback('click', self._handle_back)
            
            # Retry button
            self.retry_button = Button(
                pygame.Rect(
                    screen_rect.width // 2 - 50,
                    screen_rect.height - 40,
                    100,
                    30
                ),
                "Retry",
                button_style,
                self.main_panel
            )
            self.retry_button.add_callback('click', self._handle_retry)
            self.retry_button.visible = False
            
        except Exception as e:
            logger.error(f"Failed to create action buttons: {str(e)}")
            
    def _create_fallback_components(self) -> None:
        """Create minimal fallback components."""
        try:
            screen_rect = self.screen_manager.get_screen_rect()
            
            # Error panel
            self.error_panel = Panel(
                pygame.Rect(0, 0, screen_rect.width, screen_rect.height),
                ComponentStyle(background_color=(30, 0, 0))
            )
            
            # Error message
            self.error_label = Label(
                pygame.Rect(
                    screen_rect.width // 2 - 200,
                    screen_rect.height // 2 - 15,
                    400,
                    30
                ),
                "Critical Error: Please restart the game",
                ComponentStyle(
                    font_color=(255, 0, 0),
                    font_size=20
                )
            )
            
        except Exception as e:
            logger.critical(f"Failed to create fallback components: {str(e)}")
            raise ScreenError("Critical failure: Unable to create UI")
            
    def _update_loading_state(self, state: LoadState, message: str = None) -> None:
        """Update loading state and UI accordingly.
        
        Args:
            state: New loading state
            message: Optional status message
        """
        self.state = state
        if message:
            self.status_label.text = message
            
        # Update button visibility
        self.load_button.visible = state == LoadState.IDLE
        self.retry_button.visible = state == LoadState.ERROR
        self.back_button.visible = state != LoadState.LOADING
        
        # Update progress bar
        if state == LoadState.LOADING:
            self.progress_bar.visible = True
        else:
            self.progress_bar.visible = False
            self.loading_progress = 0.0
            
    def _handle_load(self, component: BaseComponent) -> None:
        """Handle load character button click."""
        if not self.selected_character:
            self._update_loading_state(
                LoadState.ERROR,
                "Please select a character first"
            )
            return
            
        self._update_loading_state(
            LoadState.LOADING,
            "Loading character data..."
        )
        
        try:
            # Simulate loading progress
            self._update_progress(0.3, "Fetching character data...")
            response = requests.get(
                f"http://localhost:5050/character/{self.selected_character['id']}"
            )
            
            if response.status_code == 200:
                self._update_progress(0.6, "Processing character data...")
                character_data = response.json()
                
                self._update_progress(0.9, "Initializing game state...")
                self.screen_manager.set_screen("game", character_data)
                
                self._update_loading_state(
                    LoadState.SUCCESS,
                    "Character loaded successfully"
                )
                
                # Record successful load
                self.load_history.append(LoadHistory(
                    timestamp=pygame.time.get_ticks() / 1000.0,
                    character_id=self.selected_character['id'],
                    success=True,
                    error_message=None,
                    retry_count=self.retry_count
                ))
                
            else:
                raise ResourceError(f"Server returned status code {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to load character: {str(e)}")
            self._update_loading_state(
                LoadState.ERROR,
                f"Failed to load character: {str(e)}"
            )
            
            # Record failed load
            self.load_history.append(LoadHistory(
                timestamp=pygame.time.get_ticks() / 1000.0,
                character_id=self.selected_character['id'],
                success=False,
                error_message=str(e),
                retry_count=self.retry_count
            ))
            
    def _update_progress(self, progress: float, message: str) -> None:
        """Update loading progress and status message.
        
        Args:
            progress: Progress value between 0 and 1
            message: Status message
        """
        self.loading_progress = progress
        self.progress_bar.set_progress(progress)
        self.status_label.text = message
        
    def _handle_retry(self, component: BaseComponent) -> None:
        """Handle retry button click."""
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self._update_loading_state(
                LoadState.RETRYING,
                f"Retrying... (Attempt {self.retry_count}/{self.max_retries})"
            )
            self._handle_load(component)
        else:
            self._update_loading_state(
                LoadState.ERROR,
                "Maximum retry attempts reached. Please try again later."
            )
            
    def _handle_back(self, component: BaseComponent) -> None:
        """Handle back button click."""
        self.screen_manager.set_screen("main_menu")
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events with error handling.
        
        Args:
            event: Event to handle
            
        Returns:
            bool: True if event was handled
        """
        try:
            if event.type == pygame.QUIT:
                return True
                
            # Handle component events
            for component in [
                self.load_button,
                self.back_button,
                self.retry_button
            ]:
                if component.visible and component.handle_event(event):
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error handling event: {str(e)}")
            self._update_loading_state(
                LoadState.ERROR,
                f"An error occurred: {str(e)}"
            )
            return True
            
    def update(self) -> None:
        """Update screen state."""
        try:
            # Update components
            for component in [
                self.main_panel,
                self.status_panel,
                self.progress_bar,
                self.status_label,
                self.character_panel,
                self.load_button,
                self.back_button,
                self.retry_button
            ]:
                component.update()
                
        except Exception as e:
            logger.error(f"Error during update: {str(e)}")
            self._update_loading_state(
                LoadState.ERROR,
                f"Update error: {str(e)}"
            )
            
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the screen with error handling.
        
        Args:
            surface: Surface to draw on
        """
        try:
            # Draw background
            surface.fill((30, 30, 30))
            
            # Draw components
            self.main_panel.draw(surface)
            self.status_panel.draw(surface)
            self.progress_bar.draw(surface)
            self.status_label.draw(surface)
            self.character_panel.draw(surface)
            
            # Draw buttons
            self.load_button.draw(surface)
            self.back_button.draw(surface)
            self.retry_button.draw(surface)
            
        except Exception as e:
            logger.error(f"Error during draw: {str(e)}")
            # Draw fallback error screen
            surface.fill((0, 0, 0))
            font = pygame.font.SysFont(None, 24)
            text = font.render(
                "Critical Error: Please restart the game",
                True,
                (255, 0, 0)
            )
            text_rect = text.get_rect(center=surface.get_rect().center)
            surface.blit(text, text_rect)