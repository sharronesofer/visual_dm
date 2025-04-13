# visual_client/screens/character_steps/skills_step.py

import pygame
from ui.character_draw import draw_text
from core.config_general import COLORS

def handle_skills_step(event, character, ui_state, skill_data):
    skills = list(skill_data.keys())
    index = ui_state["selected_index"]
    remaining = character["remaining_skill_points"]

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            index = max(index - 1, 0)
        elif event.key == pygame.K_DOWN:
            index = min(index + 1, len(skills) - 1)
        elif event.key == pygame.K_LEFT:
            skill = skills[index]
            rank = character["skills"].get(skill, 0)
            if rank > 0:
                character["skills"][skill] = rank - 1
                character["remaining_skill_points"] += 1
        elif event.key == pygame.K_RIGHT:
            skill = skills[index]
            rank = character["skills"].get(skill, 0)
            if rank < 4 and remaining > 0:
                character["skills"][skill] = rank + 1
                character["remaining_skill_points"] -= 1
        elif event.key == pygame.K_RETURN:
            character["step"] += 1
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            character["step"] = max(0, character["step"] - 1)

    ui_state["selected_index"] = index

def draw_skills_step(screen, font, character, ui_state, skill_data):
    skill_list = list(skill_data.keys())
    y = 100
    draw_text(screen, font, f"Total Skill Points: {character['skill_points_total']}   Remaining: {character['remaining_skill_points']}", 100, 60, COLORS["warning"])
    for i, skill in enumerate(skill_list[:18]):
        rank = character["skills"].get(skill, 0)
        ability = skill_data[skill].get("ability", "STR")
        base = character["stats"].get(ability, 0)
        total = rank + base
        color = COLORS["highlight"] if i == ui_state["selected_index"] else COLORS["secondary"]
        draw_text(screen, font, f"{skill}: {rank} + {base} => {total}", 100, y + i * 30, color)
