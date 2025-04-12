import pygame
import requests
import json
from textwrap import wrap

def get_world_description(character):
    url = "http://localhost:5050/dm_response"
    payload = {
        "mode": "start_game",
        "character_id": character.get("character_id"),
        "prompt": "Please generate an exciting, embellished overview for starting the game."
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("reply", "No description received.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error calling dm_response endpoint: {e}"


def launch_start_game(character):
    """
    Displays the 'start game' overview. We do NOT re-init or re-quit pygame here.
    We assume pygame is already running and a display is open.
    """
    # 1. Obtain the world description (and quest hook) from the backend
    world_description = get_world_description(character)

    # 2. Reuse the existing display surface
    screen = pygame.display.get_surface()
    if not screen:
        # If you want to handle the edge case where no display surface exists yet:
        screen = pygame.display.set_mode((1280, 720))

    # 3. Create a font & clock (if needed)
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    # 4. Wrap text lines
    lines = []
    for paragraph in world_description.split("\n"):
        wrapped = wrap(paragraph, width=100)
        if wrapped:
            lines.extend(wrapped)
        else:
            lines.append("")  # blank line
        lines.append("")     # extra spacing between paragraphs

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # If user closes the window, break out.
                running = False

        # 5. Draw the text
        screen.fill((30, 30, 60))
        y = 20
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (20, y))
            y += 30

        pygame.display.flip()
        clock.tick(30)

    # 6. Do NOT call pygame.quit() here, so the rest of the game can continue.
    # Just return control to the caller.
    return

# If you're debugging just this file on its own, you could do:
# But in production, you'd typically pass a real character from your main flow.
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))

    # Demo placeholder
    fake_character = {
        "character_name": "Talon",
        "race": "Elf",
        "stats": {"STR": 1, "DEX": 3, "CON": 2, "INT": 4, "WIS": 3, "CHA": 2},
        "background": "Raised in a secluded woodland where ancient magic still thrives."
    }

    launch_start_game(fake_character)
    # If you want to quit after the demonstration:
