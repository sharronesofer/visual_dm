# visual_client/screens/character_steps/race_step.py
import pygame
from core.config_general import COLORS
from textwrap import wrap
from ui.character_draw import draw_text

def handle_race_step(event, character, ui_state, race_data):
    race_list = list(race_data.keys())
    selected_index = ui_state["selected_index"]

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            selected_index = max(selected_index - 1, 0)
        elif event.key == pygame.K_DOWN:
            selected_index = min(selected_index + 1, len(race_list) - 1)
        elif event.key == pygame.K_RETURN:
            character["race"] = race_list[selected_index]
            character["step"] += 1
            selected_index = 0
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            character["step"] = max(0, character["step"] - 1)
            selected_index = 0

    ui_state["selected_index"] = selected_index

def draw_race_step(screen, font, character, ui_state, race_data):
    race_list = list(race_data.keys())
    y = 100
    for i, race in enumerate(race_list):
        col = COLORS["highlight"] if i == ui_state["selected_index"] else COLORS["secondary"]
        draw_text(screen, font, race, 100, y + i * 30, col)

    if race_list and ui_state["selected_index"] < len(race_list):
        sel_race = race_list[ui_state["selected_index"]]
        desc = race_data[sel_race].get("description", "No description available.")
        traits = race_data[sel_race].get("special_traits", [])
        mods = race_data[sel_race].get("ability_modifiers", {})

        dy = 100
        draw_text(screen, font, "Race Description:", 600, dy, COLORS["text"])
        dy += 30
        for line in wrap(desc, 60):
            draw_text(screen, font, line, 600, dy, COLORS["accent2"])
            dy += 25

        draw_text(screen, font, "Special Traits:", 600, dy, COLORS["text"])
        dy += 30
        if traits:
            for trait in traits:
                trait_line = trait.get("type", "Trait") + ": " + (trait.get("effect") or trait.get("detail", ""))
                draw_text(screen, font, trait_line, 600, dy, COLORS["accent2"])
                dy += 25
        else:
            draw_text(screen, font, "None", 600, dy, COLORS["accent2"])
            dy += 25

        draw_text(screen, font, "Ability Modifiers:", 600, dy, COLORS["text"])
        dy += 30
        for attr, bonus in mods.items():
            mod_line = f"{attr}: {'+' if bonus >= 0 else ''}{bonus}"
            draw_text(screen, font, mod_line, 600, dy, COLORS["accent2"])
            dy += 25
