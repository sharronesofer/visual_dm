# visual_client/screens/character_steps/confirmation_step.py

import pygame
from ui.character_draw import draw_text
from core.config_general import COLORS

def handle_confirmation_step(event, character):
    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
        # Final confirmation ends the creation flow
        return False  # Signal to exit loop or return to main menu
    return True  # Keep screen open

def draw_confirmation_step(screen, font, character):
    screen.fill(COLORS["background"])
    draw_text(screen, font, "Character Saved Successfully!", 100, 120, COLORS["good"])

    draw_text(screen, font, f"Name: {character.get('name', '-')}", 100, 180, COLORS["text"])
    draw_text(screen, font, f"Race: {character.get('race', '-')}", 100, 220, COLORS["text"])
    draw_text(screen, font, "Press ENTER to start the game or ESC to return to main menu.", 100, 300, COLORS["accent"])
