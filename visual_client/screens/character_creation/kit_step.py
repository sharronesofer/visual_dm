# visual_client/screens/character_steps/kit_step.py

import pygame
from ui.character_draw import draw_text
from core.config_general import COLORS

def handle_kit_step(event, character, ui_state, starter_kits):
    kits = sorted(starter_kits.keys())
    index = ui_state["selected_index"]

    if event.key == pygame.K_UP:
        index = max(index - 1, 0)
    elif event.key == pygame.K_DOWN:
        index = min(index + 1, len(kits) - 1)
    elif event.key == pygame.K_RETURN:
        if kits:
            character["starting_kit"] = kits[index]
        character["step"] += 1
    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
        character["step"] = max(0, character["step"] - 1)

    ui_state["selected_index"] = index

def draw_kit_step(screen, font, character, ui_state, starter_kits):
    kits = sorted(starter_kits.keys())
    y = 100
    for i, kit in enumerate(kits):
        col = COLORS["highlight"] if i == ui_state["selected_index"] else COLORS["secondary"]
        draw_text(screen, font, kit, 100, y + i * 30, col)

    if kits and ui_state["selected_index"] < len(kits):
        selected_kit = kits[ui_state["selected_index"]]
        items = starter_kits[selected_kit].get("items", [])
        dy = 100
        draw_text(screen, font, "Kit Contents:", 600, dy, COLORS["text"])
        dy += 30
        for item in items:
            draw_text(screen, font, item, 600, dy, COLORS["accent2"])
            dy += 25
