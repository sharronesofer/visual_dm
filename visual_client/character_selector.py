import pygame
import requests

SERVER = "http://localhost:5050"

def choose_character():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Choose Your Character")
    font = pygame.font.SysFont("monospace", 24)

    # Explicitly fetch all characters from backend
    try:
        response = requests.get(f"{SERVER}/players")
        response.raise_for_status()
        characters = response.json()
    except Exception as e:
        print(f"🔴 Error fetching characters from backend: {e}")
        pygame.quit()
        return None

    if not characters:
        print("⚠️ No characters found in backend.")
        pygame.quit()
        return None

    char_ids = list(characters.keys())
    selected_index = 0
    running = True

    while running:
        screen.fill((20, 20, 40))
        title = font.render("Choose Your Character (ENTER to select)", True, (255, 255, 255))
        screen.blit(title, (40, 30))

        for i, char_id in enumerate(char_ids):
            char = characters[char_id]
            name = char.get("character_name", "Unnamed")
            race = char.get("race", "?")
            char_class = char.get("class", "?")
            label = f"{name} [{race} {char_class}]"
            color = (255, 255, 0) if i == selected_index else (200, 200, 200)
            line = font.render(label, True, color)
            screen.blit(line, (60, 100 + i * 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(char_ids)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(char_ids)
                elif event.key == pygame.K_RETURN:
                    selected_char_id = char_ids[selected_index]
                    selected_char = characters[selected_char_id]
                    name = selected_char.get("character_name", "Unnamed")
                    print(f"✅ Selected: {name} (ID: {selected_char_id})")
                    pygame.quit()
                    return selected_char_id

if __name__ == "__main__":
    selected_character_id = choose_character()
    if selected_character_id:
        print(f"🚀 Selected character ID: {selected_character_id}")
    else:
        print("❌ No character selected.")
