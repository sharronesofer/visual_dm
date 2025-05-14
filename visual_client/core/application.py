"""
Core application management with modular architecture.
"""

import pygame
import sys
import logging
import asyncio
import json
import os
from typing import Optional, Callable, Dict, Any, List, Union
from pathlib import Path
from .error_handler import handle_component_error, ErrorSeverity
from .layout import layout_manager
from config.config import init_config
from .asset_manager import AssetManager
from .loading_manager import LoadingManager
from .animation_manager import AnimationManager
from .event_manager import EventManager
from .screen_manager import ScreenManager
from .state_manager import StateManager
from .database_manager import DatabaseManager
from .task_manager import TaskManager, TaskPriority
from .websocket_manager import WebSocketManager
from .api_manager import APIManager
from .config_manager import ConfigManager
from .resource_manager import ResourceManager
from .transaction_manager import TransactionManager
from .logging_manager import LoggingManager, LogContext
from .monitoring_manager import MonitoringManager
from .security_manager import SecurityManager
from .privacy_manager import PrivacyManager
from datetime import datetime, timedelta
from visual_client.ui.screens.game.npc_affinity_debug_panel import NPCAffinityDebugPanel
from .managers.scene_loader_manager import SceneLoaderManager

logger = logging.getLogger(__name__)

class Application:
    """
    Main application class with modular architecture.
    
    Display configuration options (from config.json):
    - display.width: Window width (default 1280)
    - display.height: Window height (default 720)
    - display.fullscreen: Fullscreen mode (default false)
    - display.background_color: Background color as [R, G, B] (default [40, 44, 52])
    - app.name: Window title (default 'Visual DM')
    """
    
    def __init__(
        self,
        config_path: str = "config.json",
        log_dir: str = "logs",
        data_dir: str = "data",
        privacy_dir: str = "privacy_data",
        scan_interval: int = 86400,  # 24 hours
        push_interval: int = 60,  # 1 minute
        retention_period: int = 604800  # 7 days
    ):
        """Initialize the application.
        
        Args:
            config_path: Path to configuration file
            log_dir: Directory for logs
            data_dir: Directory for data
            privacy_dir: Directory for privacy data
            scan_interval: Security scan interval in seconds
            push_interval: Metrics push interval in seconds
            retention_period: Data retention period in seconds
        """
        try:
            # Initialize configuration
            self.config = init_config()
            
            # Initialize Pygame
            pygame.init()
            
            # Initialize managers
            self._init_managers(config_path, log_dir, data_dir, privacy_dir, scan_interval, push_interval, retention_period)
            
            # Set up display with responsive design
            self._setup_display()
            
            # Initialize clock
            self.clock = pygame.time.Clock()
            
            # Initialize state
            self.running = False
            self.fullscreen = False
            self.screens = {}
            self.current_screen = None
            
            logger.info("Application initialized successfully")
            
        except Exception as e:
            handle_component_error(
                "Application",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def _init_managers(
        self,
        config_path: str,
        log_dir: str,
        data_dir: str,
        privacy_dir: str,
        scan_interval: int,
        push_interval: int,
        retention_period: int
    ) -> None:
        """Initialize all manager components."""
        try:
            # Initialize logging manager first
            self.logging_manager = LoggingManager(
                log_dir=log_dir,
                log_level=self.config.get("logging", {}).get("log_level", logging.INFO)
            )
            
            # Initialize monitoring manager
            self.monitoring_manager = MonitoringManager(
                push_interval=push_interval,
                retention_period=retention_period
            )
            
            # Initialize other managers
            self.config_manager = ConfigManager(config_path)
            self.config = self.config_manager.get_config()
            
            self.resource_manager = ResourceManager(data_dir)
            
            self.state_manager = StateManager()
            
            self.event_manager = EventManager()
            
            self.task_manager = TaskManager(
                max_workers=self.config.get("task_manager", {}).get("max_workers", 4)
            )
            
            self.websocket_manager = WebSocketManager(
                uri=self.config.get("websocket", {}).get("uri", "ws://localhost:8000/ws"),
                reconnect_interval=self.config.get("websocket", {}).get("reconnect_interval", 5)
            )
            
            self.api_manager = APIManager(
                base_path=self.config.get("api", {}).get("base_path", "/api")
            )
            
            self.database_manager = DatabaseManager(
                db_path=self.config.get("database", {}).get("path", "game.db")
            )
            
            self.transaction_manager = TransactionManager(
                db_path=self.config.get("storage", {}).get("db_path", "game.db")
            )
            
            self.security_manager = SecurityManager(scan_interval)
            self.privacy_manager = PrivacyManager(
                privacy_dir,
                timedelta(seconds=retention_period)
            )
            
            # Start monitoring
            self.monitoring_manager.start()
            
            # Initialize layout manager
            self.layout_manager = layout_manager
            
            # Initialize asset manager
            self.asset_manager = AssetManager(self.config.get("asset_dir", "assets"))
            
            # Initialize loading manager
            self.loading_manager = LoadingManager()
            
            # Initialize animation manager
            self.animation_manager = AnimationManager()
            
            # Initialize screen manager
            self.screen_manager = ScreenManager()
            self.screen_manager.register_screen('npc_affinity_debug', lambda: NPCAffinityDebugPanel(self.screen))
            
            # Register API versions
            self._register_api_versions()
            
            # Integrate SceneLoaderManager for async scene loading
            if hasattr(self, 'scene_manager'):
                self.scene_loader_manager = SceneLoaderManager(self.scene_manager, self.loading_manager)
                self.scene_manager.set_scene_loader_manager(self.scene_loader_manager)
            
        except Exception as e:
            handle_component_error(
                "Application",
                "_init_managers",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def _register_api_versions(self) -> None:
        """Register API versions and endpoints."""
        try:
            # Register current version
            self.api_manager.register_version(
                "1.0.0",
                "stable",
                "Initial API version"
            )
            
            # Register endpoints
            self._register_api_endpoints()
            
            # Generate and save OpenAPI documentation
            spec = self.api_manager.generate_openapi_spec("1.0.0")
            if isinstance(spec, dict):
                self.api_manager.save_openapi_spec(spec)
            
        except Exception as e:
            handle_component_error(
                "Application",
                "_register_api_versions",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def _register_api_endpoints(self) -> None:
        """Register API endpoints."""
        try:
            # Register API endpoints with proper parameters
            self.api_manager.register_endpoint(
                path="/game/state",
                method="GET",
                description="Get current game state",
                parameters=[],
                responses={
                    "200": {
                        "description": "Game state retrieved successfully",
                        "content": {"application/json": {}}
                    }
                },
                tags=["game"]
            )
            
            self.api_manager.register_endpoint(
                path="/game/state",
                method="POST",
                description="Update game state",
                parameters=[{
                    "name": "state",
                    "in": "body",
                    "required": True,
                    "schema": {"type": "object"}
                }],
                responses={
                    "200": {
                        "description": "Game state updated successfully",
                        "content": {"application/json": {}}
                    }
                },
                tags=["game"]
            )
            
            logger.info("API endpoints registered successfully")
            
        except Exception as e:
            handle_component_error(
                "Application",
                "_register_api_endpoints",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def _setup_display(self) -> None:
        """Set up the display with responsive design support."""
        try:
            # Get display info
            display_info = pygame.display.Info()
            screen_width = display_info.current_w
            screen_height = display_info.current_h
            # Set up display mode
            flags = pygame.RESIZABLE | pygame.DOUBLEBUF
            if self.config.get("display", {}).get("fullscreen", False):
                flags |= pygame.FULLSCREEN
                self.fullscreen = True
            # Load window size from config
            width = self.config.get("display", {}).get("width", 1280)
            height = self.config.get("display", {}).get("height", 720)
            self.screen = pygame.display.set_mode((width, height), flags)
            # Set window title from config
            pygame.display.set_caption(self.config.get("app", {}).get("name", "Visual DM"))
            # Set up display scaling
            self._setup_display_scaling()
        except Exception as e:
            handle_component_error(
                "Application",
                "_setup_display",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def _setup_display_scaling(self) -> None:
        """Set up display scaling for cross-browser compatibility."""
        try:
            # Get display info
            display_info = pygame.display.Info()
            screen_width = display_info.current_w
            screen_height = display_info.current_h
            
            # Calculate scaling factors
            width_scale = screen_width / self.config.get("display", {}).get("width", 1280)
            height_scale = screen_height / self.config.get("display", {}).get("height", 720)
            self.scale_factor = min(width_scale, height_scale)
            
            # Set up scaling surface
            self.scaled_surface = pygame.Surface(
                (
                    self.config.get("display", {}).get("width", 1280),
                    self.config.get("display", {}).get("height", 720)
                )
            )
            
        except Exception as e:
            handle_component_error(
                "Application",
                "_setup_display_scaling",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def handle_resize(self, event: pygame.event.Event) -> None:
        """Handle window resize events."""
        try:
            if event.type == pygame.VIDEORESIZE:
                # Update screen size
                self.screen = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.RESIZABLE | pygame.DOUBLEBUF
                )
                
                # Update layout manager
                self.layout_manager.update_screen_size(event.w, event.h)
                
                # Update current screen
                self.screen_manager.update_responsive_properties()
                
        except Exception as e:
            handle_component_error(
                "Application",
                "handle_resize",
                e,
                ErrorSeverity.ERROR,
                {"event": str(event)}
            )
            
    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        try:
            self.fullscreen = not self.fullscreen
            flags = pygame.RESIZABLE | pygame.DOUBLEBUF
            if self.fullscreen:
                flags |= pygame.FULLSCREEN
                
            self.screen = pygame.display.set_mode(
                (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT),
                flags
            )
            
            # Update layout manager
            self.layout_manager.update_screen_size(
                self.screen.get_width(),
                self.screen.get_height()
            )
            
            # Update current screen
            self.screen_manager.update_responsive_properties()
                
        except Exception as e:
            handle_component_error(
                "Application",
                "toggle_fullscreen",
                e,
                ErrorSeverity.ERROR
            )
            
    def handle_events(self) -> None:
        """Handle all pygame events with responsive design support."""
        try:
            for event in pygame.event.get():
                # Handle quit event
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                    
                # Handle resize events
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event)
                    
                # Handle fullscreen toggle
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    
                # Process event through event manager
                self.event_manager.process_event(event)
                
            # Process asset loading queue
            self.asset_manager.process_loading_queue()
            
        except Exception as e:
            handle_component_error(
                "Application",
                "handle_events",
                e,
                ErrorSeverity.ERROR
            )
            
    def update(self, dt: int) -> None:
        """Update application state."""
        try:
            # Update managers
            self.animation_manager.update()
            self.loading_manager.process_loading_queue()
            self.screen_manager.update(dt)
            self.state_manager.update(dt)
            
        except Exception as e:
            handle_component_error(
                "Application",
                "update",
                e,
                ErrorSeverity.ERROR,
                {"dt": dt}
            )
            
    def draw(self) -> None:
        """Draw the current screen with responsive design support."""
        try:
            # Get background color from config and convert to tuple
            background_color = tuple(self.config.get("display", {}).get("background_color", [40, 44, 52]))
            self.scaled_surface.fill(background_color)
            
            # Draw current screen
            self.screen_manager.draw(self.scaled_surface)
            
            # Draw loading indicators
            for id in self.loading_manager.loading_states:
                self.loading_manager.draw_loading(
                    self.scaled_surface,
                    id,
                    (50, 50)
                )
                
            # Scale and blit to screen
            scaled_size = (
                int(self.config.get("display", {}).get("width", 1280) * self.scale_factor),
                int(self.config.get("display", {}).get("height", 720) * self.scale_factor)
            )
            scaled_surface = pygame.transform.scale(self.scaled_surface, scaled_size)
            
            # Center on screen
            screen_rect = scaled_surface.get_rect(
                center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
            )
            self.screen.blit(scaled_surface, screen_rect)
            
            pygame.display.flip()
            
        except Exception as e:
            handle_component_error(
                "Application",
                "draw",
                e,
                ErrorSeverity.ERROR
            )
            
    def submit_background_task(
        self,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """Submit a background task for execution.
        
        Args:
            func: Function to execute
            args: Positional arguments
            priority: Task priority
            max_retries: Maximum number of retries
            kwargs: Keyword arguments
            
        Returns:
            Task ID
        """
        try:
            return self.task_manager.submit_task(
                func,
                *args,
                priority=priority,
                max_retries=max_retries,
                **kwargs
            )
            
        except Exception as e:
            handle_component_error(
                "Application",
                "submit_background_task",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get task status.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status if found, None otherwise
        """
        try:
            return self.task_manager.get_task_status(task_id)
            
        except Exception as e:
            handle_component_error(
                "Application",
                "get_task_status",
                e,
                ErrorSeverity.ERROR
            )
            return None
            
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get task result.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task result if completed, None otherwise
        """
        try:
            return self.task_manager.get_task_result(task_id)
            
        except Exception as e:
            handle_component_error(
                "Application",
                "get_task_result",
                e,
                ErrorSeverity.ERROR
            )
            return None
            
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if task was cancelled, False otherwise
        """
        try:
            return self.task_manager.cancel_task(task_id)
            
        except Exception as e:
            handle_component_error(
                "Application",
                "cancel_task",
                e,
                ErrorSeverity.ERROR
            )
            return False
            
    async def send_realtime_update(self, message_type: str, data: Dict[str, Any]) -> None:
        """Send a real-time update through WebSocket.
        
        Args:
            message_type: Type of update
            data: Update data
        """
        try:
            await self.websocket_manager.send_message(message_type, data)
            
        except Exception as e:
            handle_component_error(
                "Application",
                "send_realtime_update",
                e,
                ErrorSeverity.ERROR
            )
            
    def register_realtime_handler(self, message_type: str, handler: Callable) -> None:
        """Register a real-time update handler.
        
        Args:
            message_type: Type of update
            handler: Handler function
        """
        try:
            self.websocket_manager.register_handler(message_type, handler)
            
        except Exception as e:
            handle_component_error(
                "Application",
                "register_realtime_handler",
                e,
                ErrorSeverity.ERROR
            )
            
    def unregister_realtime_handler(self, message_type: str, handler: Callable) -> None:
        """Unregister a real-time update handler.
        
        Args:
            message_type: Type of update
            handler: Handler function to remove
        """
        try:
            self.websocket_manager.unregister_handler(message_type, handler)
            
        except Exception as e:
            handle_component_error(
                "Application",
                "unregister_realtime_handler",
                e,
                ErrorSeverity.ERROR
            )
            
    async def run(self) -> None:
        """Run the application main loop."""
        try:
            # Start task manager
            self.task_manager.start()
            
            # Connect WebSocket
            await self.websocket_manager.connect()
            
            # Start WebSocket listener in background
            asyncio.create_task(self.websocket_manager.listen())
            
            self.running = True
            last_time = pygame.time.get_ticks()
            
            while self.running:
                # Calculate delta time
                current_time = pygame.time.get_ticks()
                dt = current_time - last_time
                last_time = current_time
                
                # Main loop steps
                self.handle_events()
                self.update(dt)
                self.draw()
                
                # Cap frame rate
                self.clock.tick(self.config.UI_REFRESH_RATE)
                
                # Process asyncio events
                await asyncio.sleep(0)
                
        except Exception as e:
            handle_component_error(
                "Application",
                "run",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
        finally:
            await self.cleanup()
            
    async def cleanup(self) -> None:
        """Clean up application resources."""
        try:
            # Clean up managers
            self.screen_manager.cleanup()
            self.state_manager.cleanup()
            self.asset_manager.cleanup()
            self.database_manager.cleanup()
            self.task_manager.cleanup()
            await self.websocket_manager.cleanup()
            self.api_manager.cleanup()
            
            # Stop monitoring
            self.monitoring_manager.stop()
            
            pygame.quit()
            logger.info("Application cleaned up successfully")
            
        except Exception as e:
            handle_component_error(
                "Application",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            )

    def _handle_state_update(self, state: Dict[str, Any]) -> None:
        """Handle state update.
        
        Args:
            state: New state
        """
        try:
            self.state_manager.update(state)
            
            # Record metrics
            self.monitoring_manager.record_metric(
                "state_updates",
                1,
                {"state_type": "update"}
            )
            
            logger.info(f"State updated: {state}")
            
        except Exception as e:
            handle_component_error(
                "Application",
                "_handle_state_update",
                e,
                ErrorSeverity.ERROR
            )
            
    def _handle_error(self, error: Exception) -> None:
        """Handle error.
        
        Args:
            error: Error to handle
        """
        try:
            # Record error metric
            self.monitoring_manager.record_metric(
                "errors",
                1,
                {"error_type": type(error).__name__}
            )
            
            logger.error(f"Error occurred: {error}")
            
        except Exception as e:
            handle_component_error(
                "Application",
                "_handle_error",
                e,
                ErrorSeverity.ERROR
            )

    def register_screen(self, name: str, screen_class) -> None:
        """Register a screen.
        
        Args:
            name: Screen name
            screen_class: Screen class
        """
        self.screens[name] = screen_class
        
    def set_screen(self, name: str) -> None:
        """Set the current screen.
        
        Args:
            name: Screen name
        """
        if name not in self.screens:
            raise ValueError(f"Screen {name} not found")
            
        if self.current_screen:
            self.current_screen.on_exit()
            
        self.current_screen = self.screens[name](self)
        self.current_screen.on_enter()
        
    def run(self) -> None:
        """Run the application."""
        try:
            self.running = True
            
            while self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif self.current_screen:
                        self.current_screen.handle_event(event)
                
                # Update
                dt = self.clock.tick(60) / 1000.0  # Convert to seconds
                if self.current_screen:
                    self.current_screen.update(dt)
                
                # Draw
                if self.current_screen:
                    self.current_screen.draw(self.screen)
                    pygame.display.flip()
                
        except Exception as e:
            handle_component_error(
                "Application",
                "run",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def quit(self) -> None:
        """Quit the application."""
        self.running = False

    def reload_display_settings(self) -> None:
        """
        Reload display settings from the current config and apply them at runtime.
        Useful for testing different window configurations without restarting the app.
        """
        try:
            self._setup_display()
            logger.info("Display settings reloaded from config.")
        except Exception as e:
            handle_component_error(
                "Application",
                "reload_display_settings",
                e,
                ErrorSeverity.ERROR
            )
            raise 