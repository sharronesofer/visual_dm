# visual_client/screens/character_steps/summary_step.py

import pygame
import json
import requests
from ui.character_draw import draw_text
from core.config_general import COLORS, SERVER_URL, ATTRIBUTES

def handle_summary_step(event, character, ui_state):
    if event.key == pygame.K_RETURN:
        try:
            payload = {
                "character_name": character.get("name"),
                "race": character.get("race"),
                "location": "0_0",
                "known_tiles": ["0_0"],
                "level": character.get("level", 1),
                "base_stats": character.get("base_stats", {}),
                "racial_modifiers": character.get("racial_modifiers", {}),
                "stats": character.get("stats", {}),
                "racial_traits": character.get("racial_traits", {}),
                "racial_description": character.get("racial_description", ""),
                "skills": character.get("skills", {}),
                "feats": character.get("feats", []),
                "starting_kit": character.get("starting_kit"),
                "background": character.get("background", ""),
                "dr": character.get("dr", 0)
            }
            requests.post(f"{SERVER_URL}/character_creator/save", json=payload, timeout=3)
            character["step"] += 1  # Move to next (e.g. start_game)
        except Exception as e:
            print(f"🔴 Error saving character: {e}")
    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
        character["step"] = max(0, character["step"] - 1)

def draw_summary_step(screen, font, character):
    y = 100
    draw_text(screen, font, f"Name: {character.get('name', '-')}", 100, y, COLORS["text"])
    y += 30
    draw_text(screen, font, f"Race: {character.get('race', '-')}", 100, y, COLORS["text"])
    y += 30
    base = ", ".join(f"{a}: {character['base_stats'].get(a, '-')}`" for a in ATTRIBUTES)
    mods = ", ".join(f"{a}: {character['racial_modifiers'].get(a, 0)}" for a in ATTRIBUTES)
    final = ", ".join(f"{a}: {character['stats'].get(a, '-')}`" for a in ATTRIBUTES)
    for label, val in [("Base Stats", base), ("Racial Bonus", mods), ("Final Stats", final)]:
        y += 30
        draw_text(screen, font, f"{label}: {val}", 100, y, COLORS["secondary"])

    y += 30
    draw_text(screen, font, f"Skills: {json.dumps(character.get('skills', {}))}", 100, y, COLORS["secondary"])
    y += 30
    draw_text(screen, font, f"Feats: {', '.join(character.get('feats', []))}", 100, y, COLORS["secondary"])
    y += 30
    draw_text(screen, font, f"Starting Kit: {character.get('starting_kit', '-')}", 100, y, COLORS["secondary"])
    y += 30
    draw_text(screen, font, f"Background: {character.get('background', '')[:100]}...", 100, y, COLORS["secondary"])
    y += 30
    draw_text(screen, font, f"DR: {character.get('dr', 0)}", 100, y, COLORS["secondary"])
    y += 40
    draw_text(screen, font, "Press ENTER to save and begin. BACKSPACE to revise.", 100, y, COLORS["good"])
