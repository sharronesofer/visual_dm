
import pygame
import json
import os

# Correct path to visual_dm/rules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "rules"))
COMBAT_MENU_PATH = os.path.join(ROOT, "combat_menu.json")
FEATS_PATH = os.path.join(ROOT, "feats.json")

with open(COMBAT_MENU_PATH, "r") as f:
    COMBAT_MENU = json.load(f)

with open(FEATS_PATH, "r") as f:
    FEAT_LIST = json.load(f)

FEAT_INDEX = {f['name']: f for f in FEAT_LIST}

def draw_text(surface, font, text, x, y, color=(255,255,255)):
    surface.blit(font.render(text, True, color), (x, y))

def show_combat_menu(screen, font):
    selected_category_idx = 0
    selected_sub_idx = 0
    selected_action_idx = 0

    categories = list(COMBAT_MENU.keys())
    current_category = categories[selected_category_idx]
    subcategories = list(COMBAT_MENU[current_category].keys())
    current_sub = subcategories[selected_sub_idx]
    actions = COMBAT_MENU[current_category][current_sub]

    in_combat = True
    while in_combat:
        screen.fill((10, 10, 30))
        font_large = pygame.font.SysFont("monospace", 24)
        draw_text(screen, font_large, "Combat Menu (ESC to exit)", 30, 10, (255, 200, 100))

        # Draw categories
        y = 50
        draw_text(screen, font, "Category:", 40, y)
        for i, cat in enumerate(categories):
            color = (255,255,0) if i == selected_category_idx else (180,180,255)
            draw_text(screen, font, f"  {cat}", 60, y + 25 + i*25, color)

        # Draw subcategories
        y = 50
        draw_text(screen, font, "Subcategory:", 250, y)
        subcategories = list(COMBAT_MENU[current_category].keys())
        for j, sub in enumerate(subcategories):
            color = (255,255,0) if j == selected_sub_idx else (140,255,180)
            draw_text(screen, font, f"  {sub}", 270, y + 25 + j*25, color)

        # Draw actions
        y = 50
        draw_text(screen, font, "Actions:", 500, y)
        actions = COMBAT_MENU[current_category][current_sub]
        for k, act in enumerate(actions):
            color = (255,255,0) if k == selected_action_idx else (255,255,255)
            draw_text(screen, font, f"  {act}", 520, y + 25 + k*25, color)

        # Draw preview
        y = 300
        draw_text(screen, font_large, "Feat Preview", 40, y, (255, 180, 180))
        preview = FEAT_INDEX.get(actions[selected_action_idx], {})
        draw_text(screen, font, f"Name: {preview.get('name', 'N/A')}", 40, y+30)
        draw_text(screen, font, f"MP Cost: {preview.get('mp_cost', '—')}", 40, y+55)
        draw_text(screen, font, f"Action Type: {preview.get('action_type', '—')}", 40, y+80)
        draw_text(screen, font, f"Effect: {preview.get('effect', '—')}", 40, y+105)
        if preview.get('parsed_mechanics', {}).get('damage_dice'):
            draw_text(screen, font, f"Damage: {preview['parsed_mechanics']['damage_dice']}", 40, y+130)
        if preview.get('parsed_mechanics', {}).get('save_required'):
            save_type = preview['parsed_mechanics'].get('save_type', '?')
            draw_text(screen, font, f"Save: {save_type} vs DC", 40, y+155)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_combat = False
                elif event.key == pygame.K_RETURN:
                    print(f"Selected: {actions[selected_action_idx]}")
                elif event.key == pygame.K_DOWN:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        selected_sub_idx = (selected_sub_idx + 1) % len(subcategories)
                        selected_action_idx = 0
                    else:
                        selected_action_idx = (selected_action_idx + 1) % len(actions)
                elif event.key == pygame.K_UP:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        selected_sub_idx = (selected_sub_idx - 1) % len(subcategories)
                        selected_action_idx = 0
                    else:
                        selected_action_idx = (selected_action_idx - 1) % len(actions)
                elif event.key == pygame.K_RIGHT:
                    selected_category_idx = (selected_category_idx + 1) % len(categories)
                    selected_sub_idx = 0
                    selected_action_idx = 0
                elif event.key == pygame.K_LEFT:
                    selected_category_idx = (selected_category_idx - 1) % len(categories)
                    selected_sub_idx = 0
                    selected_action_idx = 0
