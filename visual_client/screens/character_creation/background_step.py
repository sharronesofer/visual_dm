# visual_client/screens/character_steps/background_step.py

import pygame
from textwrap import wrap
from ui.character_draw import draw_text
from core.config_general import COLORS

def handle_background_step(event, character, ui_state):
    bg = ui_state["background_input"]
    if event.key == pygame.K_RETURN:
        character["background"] = bg
        character["step"] += 1
    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
        if event.key == pygame.K_RETURN:
            character["name"] = name
            character["step"] += 1
            autosave_draft(character)
        else:
            character["step"] = max(0, character["step"] - 1)
    elif event.unicode.isprintable():
        ui_state["background_input"] += event.unicode

def draw_background_step(screen, font, ui_state):
    y = 100
    draw_text(screen, font, "Enter character background:", 100, y, COLORS["text"])
    y += 40
    for line in wrap(ui_state["background_input"], 80):
        draw_text(screen, font, line, 100, y, COLORS["highlight"])
        y += 25
