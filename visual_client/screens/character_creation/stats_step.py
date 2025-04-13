# visual_client/screens/character_steps/stats_step.py
import pygame
from core.config_general import COLORS, ATTRIBUTES
from ui.character_draw import draw_text

def handle_stats_step(event, character, ui_state):
    attr_idx = ui_state["selected_attribute_index"]
    stats = ui_state["assigned_stats"]
    pool = character.get("points_pool", 16)

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            attr_idx = (attr_idx - 1) % len(ATTRIBUTES)
        elif event.key == pygame.K_DOWN:
            attr_idx = (attr_idx + 1) % len(ATTRIBUTES)
        elif event.key == pygame.K_LEFT:
            attr = ATTRIBUTES[attr_idx]
            if stats[attr] > -2 and pool < 99:
                stats[attr] -= 1
                pool += 1
        elif event.key == pygame.K_RIGHT:
            attr = ATTRIBUTES[attr_idx]
            if stats[attr] < 5 and pool > 0:
                stats[attr] += 1
                pool -= 1
        elif event.key == pygame.K_RETURN:
            character["base_stats"] = stats.copy()
            character["stats"] = stats.copy()
            INT_val = stats.get("INT", 0)
            skill_pts = 14 + INT_val
            character["skill_points_total"] = skill_pts
            character["remaining_skill_points"] = skill_pts
            character["points_pool"] = pool
            character["step"] += 1
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            character["step"] = max(0, character["step"] - 1)

    ui_state["selected_attribute_index"] = attr_idx
    ui_state["assigned_stats"] = stats
    character["points_pool"] = pool

def draw_stats_step(screen, font, character, ui_state, race_data):
    y = 100
    race = character.get("race")
    race_mods = race_data.get(race, {}).get("ability_modifiers", {}) if race else {}
    stats = ui_state["assigned_stats"]
    attr_idx = ui_state["selected_attribute_index"]

    draw_text(screen, font, "POINT BUY MODE", 100, y - 30, COLORS["text"])

    for i, attr in enumerate(ATTRIBUTES):
        base = stats.get(attr, 0)
        bonus = race_mods.get(attr, 0)
        total = base + bonus
        color = COLORS["highlight"] if i == attr_idx else COLORS["secondary"]
        line = f"{attr}: {base}  {'+' if bonus >= 0 else ''}{bonus}  => {total}"
        draw_text(screen, font, line, 100, y + i * 40, color)

    draw_text(screen, font, f"Points remaining: {character.get('points_pool', 0)}", 100, y + len(ATTRIBUTES) * 40, COLORS["warning"])
    draw_text(screen, font, "Use LEFT/RIGHT to adjust stats, ENTER to confirm, BACKSPACE to go back", 100, y + len(ATTRIBUTES) * 40 + 40, COLORS["accent"])
