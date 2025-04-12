import sys
import os
import pygame
from visual_client.menus.character_creation import launch_character_creation
from visual_client.start_game import launch_start_game
from visual_client.menus.character_selector import choose_character
from visual_client.menus.ascii_map_viewer import main as launch_test_map

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Virtual DM - Main Menu")
    font = pygame.font.SysFont(None, 48)

    menu_options = ["Create Character", "Load Game", "Quit"]
    selected_index = 0
    running = True

    while running:
        screen.fill((30, 30, 60))
        title_surf = font.render("🎲 Virtual DM", True, (255, 255, 255))
        screen.blit(title_surf, (300, 100))

        for i, option in enumerate(menu_options):
            color = (255, 255, 0) if i == selected_index else (180, 180, 180)
            text_surf = font.render(option, True, color)
            screen.blit(text_surf, (320, 200 + i * 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_options)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    chosen = menu_options[selected_index]
                    if chosen == "Quit":
                        running = False
                    elif chosen == "Create Character":
                        creation_result = launch_character_creation()
                        if creation_result and creation_result.get("next") == "start_game":
                            launch_start_game(creation_result["character"])
                    elif chosen == "Load Game":
                        selected_id = choose_character()
                        if selected_id:
                            launch_test_map(character_id=selected_id)
                            return {"next": "map_view", "character_id": selected_id}

        pygame.display.flip()

    pygame.quit()
    return {"next": "quit"}

if __name__ == "__main__":
    main_menu()
