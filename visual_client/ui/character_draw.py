# visual_client/ui/character_draw.py

import pygame
from textwrap import wrap
from core.config_general import COLORS

def draw_text(screen, font, text, x, y, color=(255, 255, 255)):
    screen.blit(font.render(text, True, color), (x, y))

def draw_wrapped_text(screen, font, text, x, y, max_width, line_spacing=25, color=(255,255,255)):
    lines = wrap(text, width=max_width)
    for line in lines:
        draw_text(screen, font, line, x, y, color)
        y += line_spacing

def draw_selection_list(screen, font, items, selected_index, start_y=100, x=100, spacing=30, max_visible=18):
    for i, item in enumerate(items[:max_visible]):
        color = COLORS["highlight"] if i == selected_index else COLORS["secondary"]
        draw_text(screen, font, item, x, start_y + i * spacing, color)
