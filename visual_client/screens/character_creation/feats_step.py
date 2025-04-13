# visual_client/screens/character_steps/feats_step.py

import pygame
from textwrap import wrap
from ui.character_draw import draw_text
from core.config_creation import MAX_FEATS
from core.config_general import COLORS
from core.character_validators import is_feat_valid

def handle_feats_step(event, character, ui_state, feat_groups, feat_index):
    feat_view_mode = ui_state.get("feat_view_mode", "categories")
    selected_index = ui_state["selected_index"]
    scroll_offset = ui_state["scroll_offset"]
    category_keys = ui_state.get("feat_group_keys", sorted(feat_groups.keys()))
    current_category = ui_state.get("current_category", category_keys[0])

    valid_feats = [f for f in feat_groups.get(current_category, []) if is_feat_valid(f, feat_index, character)]

    if feat_view_mode == "categories":
        if event.key == pygame.K_LEFT:
            selected_index = (selected_index - 1) % len(category_keys)
        elif event.key == pygame.K_RIGHT:
            selected_index = (selected_index + 1) % len(category_keys)
        if event.key == pygame.K_RETURN:
            character["name"] = name
            character["step"] += 1
            autosave_draft(character)
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            character["step"] = max(0, character["step"] - 1)

    else:
        if event.key == pygame.K_LEFT:
            feat_view_mode = "categories"
            selected_index = category_keys.index(current_category)
        elif event.key == pygame.K_UP:
            selected_index = max(selected_index - 1, 0)
        elif event.key == pygame.K_DOWN:
            selected_index = min(selected_index + 1, len(valid_feats) - 1)
        elif event.key == pygame.K_SPACE:
            feat = valid_feats[selected_index]
            if feat in character["feats"]:
                character["feats"].remove(feat)
            elif len(character["feats"]) < MAX_FEATS:
                character["feats"].append(feat)
        elif event.key == pygame.K_RETURN:
            character["step"] += 1
            feat_view_mode = "categories"
            selected_index = 0
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            feat_view_mode = "categories"
            selected_index = category_keys.index(current_category)

    ui_state["selected_index"] = selected_index
    ui_state["feat_view_mode"] = feat_view_mode
    ui_state["feat_group_keys"] = category_keys
    ui_state["current_category"] = current_category
    ui_state["scroll_offset"] = scroll_offset

def draw_feats_step(screen, font, character, ui_state, feat_groups, feat_index):
    feat_view_mode = ui_state.get("feat_view_mode", "categories")
    selected_index = ui_state["selected_index"]
    current_category = ui_state.get("current_category", "")
    category_keys = ui_state.get("feat_group_keys", sorted(feat_groups.keys()))

    y = 100
    if feat_view_mode == "categories":
        draw_text(screen, font, "Select a Feat Category:", 100, 60, COLORS["accent"])
        for i, cat in enumerate(category_keys):
            col = COLORS["highlight"] if i == selected_index else COLORS["secondary"]
            draw_text(screen, font, cat, 100, y + i * 30, col)
    else:
        valid_feats = [f for f in feat_groups.get(current_category, []) if is_feat_valid(f, feat_index, character)]
        visible_feats = valid_feats[:18]
        for i, featname in enumerate(visible_feats):
            col = COLORS["highlight"] if i == selected_index else COLORS["secondary"]
            prefix = "[✓]" if featname in character["feats"] else "[ ]"
            draw_text(screen, font, f"{prefix} {featname}", 100, y + i * 30, col)

        # Description
        if valid_feats:
            sel_feat = valid_feats[selected_index]
            fdata = feat_index.get(sel_feat, {})
            desc = fdata.get("description", "")
            mech = fdata.get("mechanical_description", "")
            dy = 100
            for line in (desc + "\n" + mech).split("\n"):
                draw_text(screen, font, line, 600, dy, COLORS["accent2"])
                dy += 25
