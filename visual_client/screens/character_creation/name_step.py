# visual_client/screens/character_steps/name_step.py

import pygame
from ui.character_draw import draw_text
from core.config_general import COLORS

def handle_name_step(event, character, ui_state):
    name = ui_state["name_input"]
    if event.key == pygame.K_RETURN:
        character["name"] = name
        character["step"] += 1
    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
        if name:
            ui_state["name_input"] = name[:-1]
        else:
            character["step"] = max(0, character["step"] - 1)
    elif event.unicode.isprintable():
        ui_state["name_input"] += event.unicode

def draw_name_step(screen, font, ui_state):
    draw_text(screen, font, "Enter character name:", 100, 100, COLORS["text"])
    draw_text(screen, font, ui_state["name_input"], 100, 150, COLORS["highlight"])
