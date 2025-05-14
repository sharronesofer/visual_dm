"""
Event management utilities.
Inherits from BaseManager for common functionality.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from app.core.utils.base_manager import BaseManager
from app.utils.config_utils import get_config
from app.utils.game_utils import GameCalculator
from app.utils.constants import (
    DIFFICULTY_MULTIPLIERS,
    QUEST_TIME_LIMITS,
    EVENT_DURATIONS,
    SIZE_MULTIPLIERS
)

logger = logging.getLogger(__name__)

class EventManager(BaseManager):
    """Manager for game events and quests"""
    
    def __init__(self) -> None:
        """Initialize the event manager."""
        super().__init__('events')
        self.config = get_config()
        self.calculator = GameCalculator()
    
    def generate_quest(
        self,
        level: int,
        quest_type: str,
        difficulty: str = 'normal'
    ) -> Dict[str, Any]:
        """Generate a quest"""
        try:
            # Quest type characteristics
            quest_data = {
                'hunt': {
                    'target': ['monster', 'bandit', 'beast'],
                    'location': ['forest', 'cave', 'ruins']
                },
                'gather': {
                    'target': ['herbs', 'ore', 'artifacts'],
                    'location': ['mountain', 'swamp', 'desert']
                },
                'escort': {
                    'target': ['merchant', 'noble', 'scholar'],
                    'location': ['road', 'wilderness', 'city']
                },
                'investigate': {
                    'target': ['mystery', 'crime', 'rumor'],
                    'location': ['village', 'tavern', 'temple']
                }
            }
            
            # Get quest type data
            quest_info = quest_data.get(quest_type, quest_data['hunt'])
            
            # Get difficulty multiplier
            multiplier = DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
            
            # Generate quest details
            quest = {
                'type': quest_type,
                'level': level,
                'difficulty': difficulty,
                'target': random.choice(quest_info['target']),
                'location': random.choice(quest_info['location']),
                'duration': QUEST_TIME_LIMITS.get(quest_type, 24),
                'requirements': self._generate_requirements(
                    level,
                    multiplier,
                    ['level', 'party_size']
                ),
                'description': self._generate_description(
                    'quest',
                    quest_info['target'][0],
                    difficulty
                ),
                'start_time': datetime.utcnow(),
                'end_time': datetime.utcnow() + timedelta(
                    hours=QUEST_TIME_LIMITS.get(quest_type, 24)
                ),
                'reward': self._calculate_value(level, multiplier)
            }
            
            logger.debug(f"Generated quest: {quest}")
            return quest
            
        except Exception as e:
            self._log_error('quest generation', e)
            return {}
    
    def generate_world_event(
        self,
        level: int,
        event_type: str,
        region: str
    ) -> Dict[str, Any]:
        """Generate a world event"""
        try:
            # Event type characteristics
            event_data = {
                'natural': {
                    'types': ['storm', 'earthquake', 'drought'],
                    'effects': ['damage', 'resource loss', 'migration']
                },
                'social': {
                    'types': ['festival', 'riot', 'plague'],
                    'effects': ['population change', 'mood change', 'trade change']
                },
                'military': {
                    'types': ['invasion', 'rebellion', 'siege'],
                    'effects': ['combat', 'defense', 'alliance']
                },
                'mystical': {
                    'types': ['portal', 'curse', 'blessing'],
                    'effects': ['magic', 'transformation', 'prophecy']
                }
            }
            
            # Get event type data
            event_info = event_data.get(event_type, event_data['natural'])
            
            # Generate event details
            event = {
                'type': event_type,
                'level': level,
                'region': region,
                'subtype': random.choice(event_info['types']),
                'duration': EVENT_DURATIONS.get(event_type, 24),
                'effects': random.sample(event_info['effects'], 2),
                'severity': random.randint(1, 5),
                'description': self._generate_description(
                    'event',
                    event_info['types'][0],
                    'world'
                ),
                'start_time': datetime.utcnow(),
                'end_time': datetime.utcnow() + timedelta(
                    hours=EVENT_DURATIONS.get(event_type, 24)
                )
            }
            
            logger.debug(f"Generated world event: {event}")
            return event
            
        except Exception as e:
            self._log_error('world event generation', e)
            return {}
    
    def _generate_requirements(
        self,
        level: int,
        difficulty_multiplier: float,
        required_fields: List[str]
    ) -> Dict[str, Any]:
        """Generate quest requirements"""
        try:
            requirements = {
                'min_level': max(1, int(level * difficulty_multiplier)),
                'max_level': int(level * difficulty_multiplier),
                'min_party_size': 1,
                'max_party_size': 4,
                'special_requirements': random.sample([
                    'stealth',
                    'magic',
                    'combat',
                    'diplomacy',
                    'exploration'
                ], 2)
            }
            
            return {field: requirements[field] for field in required_fields}
            
        except Exception as e:
            self._log_error('requirements generation', e)
            return {}
    
    def _generate_description(
        self,
        quest_type: str,
        target_type: str,
        difficulty: str
    ) -> str:
        """Generate quest description"""
        try:
            if quest_type == 'quest':
                target = target_type
                location = random.choice(['forest', 'cave', 'ruins', 'mountain', 'swamp', 'desert', 'road', 'wilderness', 'city', 'village', 'tavern', 'temple'])
                description = f"Hunt down and eliminate the {target} in the {location}."
            elif quest_type == 'event':
                subtype = target_type
                region = random.choice(['forest', 'cave', 'ruins', 'mountain', 'swamp', 'desert', 'road', 'wilderness', 'city', 'village', 'tavern', 'temple'])
                description = f"A {subtype} has struck the {region} region."
            else:
                description = "Unknown quest type"
            
            return description
            
        except Exception as e:
            self._log_error('description generation', e)
            return "Failed to generate quest description"
    
    def _calculate_value(self, level: int, multiplier: float) -> float:
        """Calculate the value of a quest"""
        try:
            return self.calculator.calculate_quest_reward(level, 'normal', level) * multiplier
            
        except Exception as e:
            self._log_error('value calculation', e)
            return 0.0
    
    def _generate_event_description(
        self,
        event_type: str,
        event_types: List[str],
        region: str
    ) -> str:
        """Generate world event description"""
        try:
            subtype = random.choice(event_types)
            
            descriptions = {
                'natural': f"A {subtype} has struck the {region} region.",
                'social': f"A {subtype} is taking place in the {region} region.",
                'military': f"A {subtype} has begun in the {region} region.",
                'mystical': f"A {subtype} has appeared in the {region} region."
            }
            
            return descriptions.get(event_type, "Unknown event type")
            
        except Exception as e:
            logger.error(f"Failed to generate event description: {str(e)}")
            return "Failed to generate event description"

"""
Event handling utilities.
Provides common functionality for handling mouse and keyboard events.
"""

from typing import Optional, Callable, Tuple, Dict, Any
import pygame
from app.core.components.base import BaseComponent

class EventUtils:
    """Utility class for event handling."""
    
    @staticmethod
    def handle_mouse_motion(
        component: BaseComponent,
        event: pygame.event.Event,
        on_hover: Optional[Callable] = None,
        on_hover_enter: Optional[Callable] = None,
        on_hover_leave: Optional[Callable] = None
    ) -> bool:
        """Handle mouse motion events for a component.
        
        Args:
            component: The component to handle events for
            event: The pygame event
            on_hover: Callback for when mouse is hovering
            on_hover_enter: Callback for when mouse enters
            on_hover_leave: Callback for when mouse leaves
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        if not component.enabled or not component.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            is_hovered = component.rect.collidepoint(event.pos)
            
            if is_hovered:
                if on_hover:
                    on_hover(event.pos)
                if on_hover_enter and not getattr(component, '_was_hovered', False):
                    on_hover_enter(event.pos)
            elif on_hover_leave and getattr(component, '_was_hovered', False):
                on_hover_leave(event.pos)
                
            component._was_hovered = is_hovered
            return is_hovered
            
        return False

    @staticmethod
    def handle_mouse_button(
        component: BaseComponent,
        event: pygame.event.Event,
        on_click: Optional[Callable] = None,
        on_press: Optional[Callable] = None,
        on_release: Optional[Callable] = None
    ) -> bool:
        """Handle mouse button events for a component.
        
        Args:
            component: The component to handle events for
            event: The pygame event
            on_click: Callback for when component is clicked
            on_press: Callback for when mouse button is pressed
            on_release: Callback for when mouse button is released
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        if not component.enabled or not component.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if component.rect.collidepoint(event.pos):
                if on_press:
                    on_press(event.pos)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if component.rect.collidepoint(event.pos):
                if on_click:
                    on_click(event.pos)
                if on_release:
                    on_release(event.pos)
                return True

        return False

    @staticmethod
    def handle_keyboard(
        component: BaseComponent,
        event: pygame.event.Event,
        on_key_down: Optional[Callable] = None,
        on_key_up: Optional[Callable] = None,
        key_map: Optional[Dict[int, Callable]] = None
    ) -> bool:
        """Handle keyboard events for a component.
        
        Args:
            component: The component to handle events for
            event: The pygame event
            on_key_down: Callback for when any key is pressed
            on_key_up: Callback for when any key is released
            key_map: Dictionary mapping key codes to callbacks
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        if not component.enabled or not component.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if on_key_down:
                on_key_down(event.key)
            if key_map and event.key in key_map:
                key_map[event.key]()
            return True

        elif event.type == pygame.KEYUP:
            if on_key_up:
                on_key_up(event.key)
            return True

        return False

    @staticmethod
    def handle_scroll(
        component: BaseComponent,
        event: pygame.event.Event,
        on_scroll_up: Optional[Callable] = None,
        on_scroll_down: Optional[Callable] = None
    ) -> bool:
        """Handle mouse scroll events for a component.
        
        Args:
            component: The component to handle events for
            event: The pygame event
            on_scroll_up: Callback for when scrolling up
            on_scroll_down: Callback for when scrolling down
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        if not component.enabled or not component.visible:
            return False

        if event.type == pygame.MOUSEWHEEL:
            if component.rect.collidepoint(pygame.mouse.get_pos()):
                if event.y > 0 and on_scroll_up:
                    on_scroll_up(event.y)
                elif event.y < 0 and on_scroll_down:
                    on_scroll_down(event.y)
                return True

        return False 