"""
UI components for the game interface.
"""

import pygame
from typing import Dict, Optional, List, Tuple, Callable
from dataclasses import dataclass, field

@dataclass
class UITheme:
    """Theme settings for UI components."""
    background_color: Tuple[int, int, int] = (50, 50, 50)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    border_color: Tuple[int, int, int] = (100, 100, 100)
    highlight_color: Tuple[int, int, int] = (70, 70, 70)
    font_name: str = "Arial"
    font_size: int = 16
    padding: int = 5
    border_width: int = 1

class UIComponent:
    """Base class for UI components."""
    
    def __init__(self, x: int, y: int, width: int, height: int, theme: Optional[UITheme] = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.theme = theme or UITheme()
        self.visible = True
        self.enabled = True
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the component on the surface."""
        if not self.visible:
            return
        pygame.draw.rect(surface, self.theme.background_color, self.rect)
        if self.theme.border_width > 0:
            pygame.draw.rect(surface, self.theme.border_color, self.rect, self.theme.border_width)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        return False
        
    def update(self) -> None:
        """Update component state."""
        pass

class Button(UIComponent):
    """Clickable button component."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Optional[Callable] = None, theme: Optional[UITheme] = None):
        super().__init__(x, y, width, height, theme)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.font = pygame.font.SysFont(self.theme.font_name, self.theme.font_size)
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button."""
        if not self.visible:
            return
            
        color = self.theme.highlight_color if self.hovered else self.theme.background_color
        pygame.draw.rect(surface, color, self.rect)
        if self.theme.border_width > 0:
            pygame.draw.rect(surface, self.theme.border_color, self.rect, self.theme.border_width)
        
        text_surface = self.font.render(self.text, True, self.theme.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle button events."""
        if not self.enabled or not self.visible:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return self.hovered
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
                
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                if self.callback:
                    self.callback()
                return True
            self.pressed = False
            
        return False

class Label(UIComponent):
    """Text label component."""
    
    def __init__(self, x: int, y: int, text: str, font_size: int = 24, 
                 color: Tuple[int, int, int] = (0, 0, 0)):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.font_size = font_size
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self._update_size()
        
    def _update_size(self) -> None:
        """Update component size based on text."""
        text_surface = self.font.render(self.text, True, self.color)
        self.rect.width = text_surface.get_width()
        self.rect.height = text_surface.get_height()
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the label."""
        if not self.visible:
            return
            
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, self.rect.topleft)
        
    def set_text(self, text: str) -> None:
        """Update label text."""
        self.text = text
        self._update_size()

class Panel(UIComponent):
    """Container component for other UI elements."""
    
    def __init__(self, x: int, y: int, width: int, height: int, theme: Optional[UITheme] = None):
        super().__init__(x, y, width, height, theme)
        self.children: List[UIComponent] = []
        self.draggable = False
        self.dragging = False
        self.drag_offset = (0, 0)
        
    def add_child(self, child: UIComponent) -> None:
        """Add a child component."""
        self.children.append(child)
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the panel and its children."""
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(surface, self.theme.background_color, self.rect)
        pygame.draw.rect(surface, self.theme.border_color, self.rect, self.theme.border_width)
        
        # Draw children
        for child in self.children:
            if child.visible:
                child.draw(surface)
                
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for the panel and its children."""
        if not self.enabled or not self.visible:
            return False
            
        if self.draggable:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_offset = (event.pos[0] - self.x, event.pos[1] - self.y)
                    return True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.x = event.pos[0] - self.drag_offset[0]
                self.y = event.pos[1] - self.drag_offset[1]
                self.rect.x = self.x
                self.rect.y = self.y
                return True

        for child in reversed(self.children):
            if child.handle_event(event):
                return True
                
        return False
        
    def update(self) -> None:
        """Update panel and children."""
        for child in self.children:
            child.update()

class TextInput:
    """Text input component for user interaction."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 placeholder: str = "", theme: Optional[UITheme] = None):
        """Initialize text input component."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.focused = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = pygame.font.SysFont(theme.font_name, theme.font_size)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.focused = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_RETURN:
                self.focused = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable():
                self.text += event.unicode
            return True
        return False
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the text input component."""
        # Draw background
        pygame.draw.rect(surface, self.theme.background_color, self.rect)
        if self.theme.border_width > 0:
            pygame.draw.rect(surface, self.theme.border_color, self.rect, self.theme.border_width)
            
        # Draw text
        if self.text:
            text_surface = self.font.render(self.text, True, self.theme.text_color)
        elif not self.focused:
            text_surface = self.font.render(self.placeholder, True, (128, 128, 128))
        else:
            text_surface = self.font.render("", True, self.theme.text_color)
            
        # Position text
        text_rect = text_surface.get_rect()
        text_rect.left = self.rect.left + self.theme.padding
        text_rect.centery = self.rect.centery
        surface.blit(text_surface, text_rect)

        if self.focused and self.cursor_visible:
            cursor_x = text_rect.right + 2
            pygame.draw.line(surface, self.theme.text_color,
                           (cursor_x, self.rect.top + 4),
                           (cursor_x, self.rect.bottom - 4))

class Dropdown:
    """Dropdown menu component."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 options: List[str], font_size: int = 16,
                 on_select: Optional[Callable[[str], None]] = None):
        """
        Initialize dropdown component.
        
        Args:
            x: X position
            y: Y position
            width: Width of dropdown
            height: Height of each option
            options: List of options to display
            font_size: Font size for options
            on_select: Callback function when option is selected
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = 0
        self.on_select = on_select
        self.expanded = False
        self.font = pygame.font.SysFont('Arial', font_size)
        self.option_height = height
        self.hover_index = -1
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check if main button was clicked
            if self.rect.collidepoint(mouse_pos):
                self.expanded = not self.expanded
                return
                
            # Check if an option was clicked
            if self.expanded:
                for i, option_rect in enumerate(self._get_option_rects()):
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        if self.on_select:
                            self.on_select(self.options[i])
                        self.expanded = False
                        return
                        
        elif event.type == pygame.MOUSEMOTION and self.expanded:
            mouse_pos = event.pos
            self.hover_index = -1
            for i, option_rect in enumerate(self._get_option_rects()):
                if option_rect.collidepoint(mouse_pos):
                    self.hover_index = i
                    break
                    
    def _get_option_rects(self) -> List[pygame.Rect]:
        """Get rectangles for all options when expanded."""
        rects = []
        for i in range(len(self.options)):
            rects.append(pygame.Rect(
                self.rect.x,
                self.rect.y + (i + 1) * self.option_height,
                self.rect.width,
                self.option_height
            ))
        return rects
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the dropdown component."""
        # Draw main button
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)
        
        # Draw selected option
        if self.options:
            text = self.options[self.selected_index]
            text_surface = self.font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                midleft=(self.rect.left + 10, self.rect.centery)
            )
            surface.blit(text_surface, text_rect)
            
        # Draw arrow
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 4),
            (self.rect.right - 10, self.rect.centery + 4),
            (self.rect.right - 30, self.rect.centery + 4),
        ]
        pygame.draw.polygon(surface, (200, 200, 200), arrow_points)
        
        # Draw options if expanded
        if self.expanded:
            option_rects = self._get_option_rects()
            for i, (option, rect) in enumerate(zip(self.options, option_rects)):
                # Draw background
                color = (70, 70, 70) if i == self.hover_index else (40, 40, 40)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (100, 100, 100), rect, 2)
                
                # Draw text
                text_surface = self.font.render(option, True, (255, 255, 255))
                text_rect = text_surface.get_rect(
                    midleft=(rect.left + 10, rect.centery)
                )
                surface.blit(text_surface, text_rect)

class MessageLog:
    """Message log component for displaying game messages."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 font_size: int = 14, max_messages: int = 100):
        """
        Initialize message log component.
        
        Args:
            x: X position
            y: Y position
            width: Width of log
            height: Height of log
            font_size: Font size for messages
            max_messages: Maximum number of messages to store
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.messages = []
        self.max_messages = max_messages
        self.font = pygame.font.SysFont('Arial', font_size)
        self.line_height = font_size + 4
        self.scroll_offset = 0
        self.visible_lines = height // self.line_height
        
    def add_message(self, text: str, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """
        Add a message to the log.
        
        Args:
            text: Message text
            color: RGB color tuple for the message
        """
        self.messages.append((text, color))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
            
        # Auto-scroll to bottom
        self.scroll_offset = max(0, len(self.messages) - self.visible_lines)
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:  # Mouse wheel down
                max_offset = max(0, len(self.messages) - self.visible_lines)
                self.scroll_offset = min(max_offset, self.scroll_offset + 1)
                
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the message log component."""
        # Draw background
        pygame.draw.rect(surface, (30, 30, 30), self.rect)
        pygame.draw.rect(surface, (60, 60, 60), self.rect, 2)
        
        # Create a surface for the messages
        visible_rect = pygame.Rect(0, 0, self.rect.width - 4, self.rect.height - 4)
        message_surface = pygame.Surface(visible_rect.size, pygame.SRCALPHA)
        
        # Draw messages
        y = 0
        start_idx = max(0, len(self.messages) - self.visible_lines - self.scroll_offset)
        visible_messages = self.messages[start_idx:start_idx + self.visible_lines]
        
        for text, color in visible_messages:
            text_surface = self.font.render(text, True, color)
            message_surface.blit(text_surface, (5, y))
            y += self.line_height
            
        # Draw message surface to main surface
        surface.blit(message_surface, (self.rect.x + 2, self.rect.y + 2))
        
        # Draw scroll indicators if needed
        if len(self.messages) > self.visible_lines:
            if self.scroll_offset > 0:
                self._draw_scroll_indicator(surface, True)
            if self.scroll_offset < len(self.messages) - self.visible_lines:
                self._draw_scroll_indicator(surface, False)
                
    def _draw_scroll_indicator(self, surface: pygame.Surface, is_up: bool) -> None:
        """Draw scroll indicator arrow."""
        if is_up:
            points = [
                (self.rect.right - 15, self.rect.top + 15),
                (self.rect.right - 10, self.rect.top + 5),
                (self.rect.right - 20, self.rect.top + 5),
            ]
        else:
            points = [
                (self.rect.right - 15, self.rect.bottom - 15),
                (self.rect.right - 10, self.rect.bottom - 5),
                (self.rect.right - 20, self.rect.bottom - 5),
            ]
        pygame.draw.polygon(surface, (200, 200, 200), points) 