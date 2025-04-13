# visual_client/screens/character_creation.py

import pygame
import logging
from core.character_state import initialize_character, get_initial_ui_state, steps
from core.config_general import SCREEN_WIDTH, SCREEN_HEIGHT, SERVER_URL
from core.data_loader import load_local_json, safe_get_json, load_feat_index, normalize_intrinsic_feats
import requests
from core.config_general import SERVER_URL

# Step handlers
from screens.character_steps.race_step import handle_race_step, draw_race_step
from screens.character_steps.stats_step import handle_stats_step, draw_stats_step
from screens.character_steps.skills_step import handle_skills_step, draw_skills_step
from screens.character_steps.feats_step import handle_feats_step, draw_feats_step
from screens.character_steps.name_step import handle_name_step, draw_name_step
from screens.character_steps.background_step import handle_background_step, draw_background_step
from screens.character_steps.kit_step import handle_kit_step, draw_kit_step

logging.basicConfig(level=logging.INFO)

def autosave_draft(character):
    try:
        res = requests.post(f"{SERVER_URL}/character_creator/save_draft", json=character, timeout=3)
        if res.status_code != 200:
            print("⚠️ Autosave failed:", res.status_code)
    except Exception as e:
        print("⚠️ Autosave error:", e)
        
def launch_character_creation():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Character Creation")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    character = initialize_character()
    ui_state = get_initial_ui_state()

    # Load rules data
    race_data = safe_get_json(f"{SERVER_URL}/rules/races", {"Human": {"description": "Fallback race"}})
    skill_data = safe_get_json(f"{SERVER_URL}/rules/skills", {"Stealth": {"description": "Fallback skill"}})
    feats_data = safe_get_json(f"{SERVER_URL}/rules/feats", [])
    starter_kits = safe_get_json(f"{SERVER_URL}/rules/starting_kits", {})

    feat_index = load_feat_index(feats_data)
    feat_groups = {}
    for name, feat in feat_index.items():
        category = feat.get("category", "Misc")
        feat_groups.setdefault(category, []).append(name)

    # Add view state info
    ui_state["feat_group_keys"] = sorted(feat_groups.keys())
    ui_state["feat_view_mode"] = "categories"

    running = True
    while running:
        current_step = steps[character["step"] % len(steps)]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if current_step == "Race":
                    handle_race_step(event, character, ui_state, race_data)
                elif current_step == "Stats":
                    handle_stats_step(event, character, ui_state, race_data)
                elif current_step == "Skills":
                    handle_skills_step(event, character, ui_state, skill_data)
                elif current_step == "Feats":
                    handle_feats_step(event, character, ui_state, feat_groups, feat_index)
                elif current_step == "Name":
                    handle_name_step(event, character, ui_state)
                elif current_step == "Background":
                    handle_background_step(event, character, ui_state)
                elif current_step == "Kit":
                    handle_kit_step(event, character, ui_state, starter_kits)

        screen.fill((30, 30, 60))
        if current_step == "Race":
            draw_race_step(screen, font, character, ui_state, race_data)
        elif current_step == "Stats":
            draw_stats_step(screen, font, character, ui_state, race_data)
        elif current_step == "Skills":
            draw_skills_step(screen, font, character, ui_state, skill_data)
        elif current_step == "Feats":
            draw_feats_step(screen, font, character, ui_state, feat_groups, feat_index)
        elif current_step == "Name":
            draw_name_step(screen, font, ui_state)
        elif current_step == "Background":
            draw_background_step(screen, font, ui_state)
        elif current_step == "Kit":
            draw_kit_step(screen, font, character, ui_state, starter_kits)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return {"next": "start_game", "character": character}

if __name__ == "__main__":
    res = launch_character_creation()
    print("launch_character_creation returned:", res)
