"""
Main entry point for the application.
"""

import sys
import logging
from pathlib import Path
from core.application import Application
from core.error_handler import handle_component_error, ErrorSeverity
from ui.screens.menu.main_menu import MainMenuScreen
from ui.screens.character.character_creation import CharacterCreationScreen
from ui.screens.game.game import GameScreen
from ui.screens.menu.settings import SettingsScreen
from ui.screens.template_editor import TemplateEditorScreen

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main() -> int:
    """Main entry point for the application."""
    try:
        # Initialize application
        app = Application()
        
        # Register screens
        app.register_screen("main_menu", MainMenuScreen)
        app.register_screen("character_creation", CharacterCreationScreen)
        app.register_screen("game", GameScreen)
        app.register_screen("settings", SettingsScreen)
        app.register_screen("template_editor", TemplateEditorScreen)
        
        # Set initial screen
        app.set_screen("main_menu")
        
        # Run application
        app.run()
        
        return 0
        
    except Exception as e:
        handle_component_error(
            "Main",
            "main",
            e,
            ErrorSeverity.CRITICAL
        )
        return 1

if __name__ == '__main__':
    sys.exit(main())
