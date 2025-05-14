import pygame
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum, auto

class FocusState(Enum):
    """Enumeration of focus states for accessibility."""
    NONE = auto()
    FOCUSED = auto()
    SELECTED = auto()

@dataclass
class ActionButton:
    """Data class for action button state."""
    rect: pygame.Rect
    enabled: bool
    focus_state: FocusState
    hotkey: str
    description: str

class CombatActionMenu:
    def __init__(self, screen, actions_enabled=None):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 36)

        # Action configuration
        self.actions = ["Attack", "Cast", "Skill", "Item"]
        self.action_descriptions = {
            "Attack": "Perform a basic attack on the enemy",
            "Cast": "Cast a spell or magical ability",
            "Skill": "Use a special combat skill",
            "Item": "Use an item from your inventory"
        }
        self.action_hotkeys = {
            "Attack": "A",
            "Cast": "C",
            "Skill": "S",
            "Item": "I"
        }
        self.actions_enabled = actions_enabled or {a: True for a in self.actions}
        
        # UI state
        self.buttons: Dict[str, ActionButton] = {}
        self.selected_action = None
        self.focused_action = None
        self.last_focus_time = 0
        self.focus_duration = 1000  # ms
        
        # Accessibility settings
        self.high_contrast = False
        self.screen_reader_enabled = False
        self.keyboard_navigation = True
        
        # Initialize buttons
        self._initialize_buttons()

    def _initialize_buttons(self):
        """Initialize the action buttons with their positions and states."""
        panel_y = 620
        panel_height = 140
        button_width = 200
        button_height = 50
        spacing = 40
        x = 100

        for action in self.actions:
            rect = pygame.Rect(x, panel_y + 40, button_width, button_height)
            self.buttons[action] = ActionButton(
                rect=rect,
                enabled=self.actions_enabled.get(action, False),
                focus_state=FocusState.NONE,
                hotkey=self.action_hotkeys[action],
                description=self.action_descriptions[action]
            )
            x += button_width + spacing

    def handle_event(self, event):
        """Handle input events with accessibility support."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            return self._handle_key_press(event.key)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        return None

    def _handle_mouse_click(self, pos):
        """Handle mouse click events."""
        for action, button in self.buttons.items():
            if button.rect.collidepoint(pos) and button.enabled:
                self.selected_action = action
                button.focus_state = FocusState.SELECTED
                self._announce_action(action)
                return action
        return None

    def _handle_key_press(self, key):
        """Handle keyboard navigation and shortcuts."""
        if not self.keyboard_navigation:
            return None

        # Arrow key navigation
        if key == pygame.K_LEFT:
            self._move_focus(-1)
        elif key == pygame.K_RIGHT:
            self._move_focus(1)
        elif key == pygame.K_RETURN and self.focused_action:
            action = self.focused_action
            if self.buttons[action].enabled:
                self.selected_action = action
                self.buttons[action].focus_state = FocusState.SELECTED
                self._announce_action(action)
                return action

        # Hotkey support
        for action, button in self.buttons.items():
            if key == ord(button.hotkey.lower()) and button.enabled:
                self.selected_action = action
                button.focus_state = FocusState.SELECTED
                self._announce_action(action)
                return action

        return None

    def _handle_mouse_motion(self, pos):
        """Handle mouse motion for focus tracking."""
        for action, button in self.buttons.items():
            if button.rect.collidepoint(pos):
                if self.focused_action != action:
                    self.focused_action = action
                    button.focus_state = FocusState.FOCUSED
                    self.last_focus_time = pygame.time.get_ticks()
                    self._announce_focus(action)
            elif button.focus_state == FocusState.FOCUSED:
                button.focus_state = FocusState.NONE

    def _move_focus(self, direction):
        """Move focus between buttons in the given direction."""
        if not self.focused_action:
            # Start with first enabled button
            for action, button in self.buttons.items():
                if button.enabled:
                    self.focused_action = action
                    button.focus_state = FocusState.FOCUSED
                    self._announce_focus(action)
                    break
            return

        # Find current index and move
        actions = list(self.buttons.keys())
        current_index = actions.index(self.focused_action)
        
        # Find next enabled button
        for i in range(1, len(actions)):
            next_index = (current_index + direction * i) % len(actions)
            next_action = actions[next_index]
            if self.buttons[next_action].enabled:
                # Clear previous focus
                self.buttons[self.focused_action].focus_state = FocusState.NONE
                # Set new focus
                self.focused_action = next_action
                self.buttons[next_action].focus_state = FocusState.FOCUSED
                self._announce_focus(next_action)
                break

    def _announce_focus(self, action):
        """Announce focus change for screen readers."""
        if self.screen_reader_enabled:
            button = self.buttons[action]
            message = f"{action} button. {button.description}"
            if not button.enabled:
                message += " (Disabled)"
            print(f"Screen reader: {message}")

    def _announce_action(self, action):
        """Announce action selection for screen readers."""
        if self.screen_reader_enabled:
            print(f"Screen reader: Selected {action}")

    def set_enabled_actions(self, enabled_dict):
        """Update which actions are enabled or disabled."""
        self.actions_enabled = enabled_dict
        for action, button in self.buttons.items():
            button.enabled = enabled_dict.get(action, False)
            if not button.enabled and button.focus_state != FocusState.NONE:
                button.focus_state = FocusState.NONE
                if self.focused_action == action:
                    self.focused_action = None

    def update(self):
        """Update button states and animations."""
        current_time = pygame.time.get_ticks()
        
        # Update focus states
        for button in self.buttons.values():
            if (button.focus_state == FocusState.FOCUSED and 
                current_time - self.last_focus_time > self.focus_duration):
                button.focus_state = FocusState.NONE

    def draw(self):
        """Draw the action menu with accessibility features."""
        # Draw panel background
        panel_y = 620
        panel_height = 140
        pygame.draw.rect(self.screen, (20, 20, 20), (0, panel_y, 1024, panel_height))

        # Draw buttons with accessibility features
        for action, button in self.buttons.items():
            # Determine colors based on state and high contrast mode
            if self.high_contrast:
                bg_color = (255, 255, 255) if button.enabled else (100, 100, 100)
                text_color = (0, 0, 0) if button.enabled else (50, 50, 50)
                focus_color = (255, 0, 0)  # Red for high contrast
            else:
                bg_color = (0, 200, 100) if button.enabled else (100, 100, 100)
                text_color = (0, 0, 0)
                focus_color = (255, 255, 0)  # Yellow for normal mode

            # Draw button background
            pygame.draw.rect(self.screen, bg_color, button.rect)

            # Draw focus indicator
            if button.focus_state != FocusState.NONE:
                focus_rect = button.rect.inflate(4, 4)
                pygame.draw.rect(self.screen, focus_color, focus_rect, 2)

            # Draw button text
            text = f"{action} ({button.hotkey})"
            label = self.font.render(text, True, text_color)
            self.screen.blit(label, (button.rect.x + 20, button.rect.y + 10))

            # Draw description for focused button
            if button.focus_state == FocusState.FOCUSED:
                desc = self.font.render(button.description, True, (200, 200, 200))
                self.screen.blit(desc, (button.rect.x, button.rect.y - 30))

        pygame.display.flip()
