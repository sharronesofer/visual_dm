import pygame
from textwrap import wrap
from firebase_admin import db

class BeginJourneyScreen:
    def __init__(self, screen, character_data):
        self.screen = screen
        self.character_data = character_data
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 32)
        self.message = "🌍 Welcome to your journey!"

        self.region = character_data.get("region_id", "unknown")
        self.poi = character_data.get("location", "unknown")
        self.bg_color = (10, 10, 30)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

    def update(self):
        pass

    def draw(self):
        self.screen.fill(self.bg_color)

        y = 60
        self.screen.blit(self.large_font.render("📍 Journey Begins", True, (255, 255, 0)), (60, y))
        y += 40

        self.screen.blit(self.font.render(f"Region: {self.region}", True, (200, 200, 255)), (60, y))
        y += 30
        self.screen.blit(self.font.render(f"Location: {self.poi}", True, (200, 200, 255)), (60, y))
        y += 50

        backstory = self.character_data.get("background", "No backstory provided.")
        self.screen.blit(self.font.render("📝 Background Summary:", True, (255, 255, 255)), (60, y))
        y += 30

        for line in wrap(backstory, width=80):
            self.screen.blit(self.font.render(line, True, (180, 255, 180)), (60, y))
            y += 22

        instructions = "Press ESC to quit."
        self.screen.blit(self.font.render(instructions, True, (120, 120, 120)), (60, 700))

    def start_journey(character_id):
        char_ref = db.reference(f"/players/{character_id}")
        character = char_ref.get()

        if not character:
            return {"error": "Character not found"}, 404

        region_id = character.get("region_id")
        start_pos = character.get("position", {"x": 0, "y": 0})

        # Load region tiles
        region_tiles = db.reference(f"/region_maps/{region_id}/tiles").get() or {}

        # Load starting tile info
        tile_key = f"{start_pos['x']}_{start_pos['y']}"
        starting_tile = region_tiles.get(tile_key, {})

        return {
            "character": character,
            "region_tiles": region_tiles,
            "starting_tile_info": starting_tile
        }