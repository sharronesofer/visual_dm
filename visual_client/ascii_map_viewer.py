import pygame
import requests
import os
from requests.utils import quote
from visual_client.menus.character_selector import choose_character
from urllib.parse import quote

TILE_SIZE = 24
SERVER = "http://localhost:5050"

TILE_MAP = {
  "grassland": "~", "forest": ".", "riverlands": "^", "hills": "#",
  "wetlands": "*", "desert": "≈", "tundra": "=", "mountains": "+",
  "savanna": "%", "jungle": "&", "coastal": "@", "volcano": "$",
  "cursed_lands": "!", "toxic_swamp": "?", "necrotic_fields": "/",
  "haunted_woods": "\\", "frozen_wastes": "|", "scorched_plains": "O",
  "shattered_mountains": "x", "wasteland": ":", "ruins": ";",
  "arcane_storm": "~", "celestial_plateau": ".", "void_rift": "^",
  "floating_isles": "#", "crystal_forest": "*", "grave_valley": "≈",
  "fungal_jungle": "=", "sunken_city": "+", "clockwork_canyon": "%",
  "obsidian_sea": "&"
}

def move_player_to(new_key, character_id):
    try:
        res = requests.post(f"{SERVER}/move_player", json={
            "character_id": character_id,
            "new_location": new_key
        })
        if res.status_code != 200:
            print(f"⚠️ move_player failed: {res.status_code}")
            return False

        tiles_res = requests.get(f"{SERVER}/tiles_visible/{character_id}")
        known_tiles = tiles_res.json() if tiles_res.status_code == 200 else []
        if new_key not in known_tiles:
            known_tiles.append(new_key)

        update_res = requests.patch(
            f"{SERVER}/update_known_tiles/{character_id}",
            json={
                "location": new_key, 
                "known_tiles": known_tiles}
        )
        if update_res.status_code != 200:
            print(f"⚠️ known_tiles update failed: {update_res.status_code}")

        return res.json().get("combat_triggered", False)

    except Exception as e:
        print("⚠️ Movement error:", e)
        return False

def format_key(x, y):
    return f"{x}_{y}"

def draw_text(surface, font, text, x, y, color=(255,255,255)):
    surface.blit(font.render(text, True, color), (x, y))

def get_visible_tiles(character_id):
    try:
        res = requests.get(f"{SERVER}/tiles_visible/{character_id}")
        return res.json() if res.status_code == 200 else ["0_0"]
    except Exception as e:
        print("Tiles fetch exception:", e)
        return ["0_0"]

def get_tile_data(tile_key):
    try:
        res = requests.get(f"{SERVER}/tile_data/{tile_key}")
        return res.json() if res.status_code == 200 else {}
    except:
        return {}

def get_player_location(character_id):
    try:
        res = requests.get(f"{SERVER}/menu/character_sheet/{character_id}")
        player_data = res.json() if res.status_code == 200 else {}
        return player_data.get("location", "0_0")
    except Exception as e:
        print("⚠️ Location fetch error:", e)
        return "0_0"

def parse_key(key):
    try:
        x, y = key.split("_")
        return int(x), int(y)
    except Exception as e:
        print("🔴 Failed to parse key:", key, "| Error:", e)
        return 0, 0

def draw_ascii_map(screen, font, tile_keys, player_loc):
    coords = [parse_key(key) for key in tile_keys]
    if not coords:
        draw_text(screen, font, "⚠️ No tiles", 40, 40, (255, 0, 0))
        return

    player_x, player_y = parse_key(player_loc)

    screen_w, screen_h = screen.get_size()
    center_x = screen_w // 2
    center_y = screen_h // 2

    for key in tile_keys:
        x, y = parse_key(key)
        tile = get_tile_data(key)
        terrain = tile.get("terrain", "grassland")
        char = TILE_MAP.get(terrain, "?")
        if tile.get("POI"):
            char = "T"
        if key == player_loc:
            char = "@"

        tx = center_x + (x - player_x) * TILE_SIZE
        ty = center_y - (y - player_y) * TILE_SIZE  # vertical inversion

        draw_text(screen, font, char, tx, ty)

def main(character_id=None):
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("ASCII World Map")
    font = pygame.font.SysFont("monospace", 20)

    if character_id is None:
        character_id = choose_character()  # explicitly get character_id if not provided

    running = True

    while running:
        visible_tiles = get_visible_tiles(character_id)
        player_loc = get_player_location(character_id)

        screen.fill((0, 0, 0))
        draw_ascii_map(screen, font, visible_tiles, player_loc)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                x, y = parse_key(player_loc)
                if event.key in (pygame.K_w, pygame.K_UP): y += 1
                elif event.key in (pygame.K_s, pygame.K_DOWN): y -= 1
                elif event.key in (pygame.K_a, pygame.K_LEFT): x -= 1
                elif event.key in (pygame.K_d, pygame.K_RIGHT): x += 1
                else: continue

                new_key = format_key(x, y)
                print(f"🔄 Moving character to: {new_key}")
                moved = move_player_to(new_key, character_id)
                if moved:
                    player_loc = new_key
                    print(f"✅ New location: {player_loc}")

    pygame.quit()
    return

if __name__ == "__main__":
    main()
