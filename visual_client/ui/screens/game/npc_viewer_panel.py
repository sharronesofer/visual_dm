import pygame
import requests

class NPCViewerPanel:
    def __init__(self, screen, region_id, poi_id):
        self.screen = screen
        self.region_id = region_id
        self.poi_id = poi_id
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 32)
        self.npcs = []
        self.selected_npc = 0
        self.load_npcs()

    def load_npcs(self):
        try:
            res = requests.get(f"http://localhost:5050/poi_state/{self.region_id}/{self.poi_id}")
            if res.status_code == 200:
                poi_data = res.json()
                npc_list = poi_data.get("npcs_present", [])
                self.npcs = npc_list
                print(f"✅ Loaded {len(self.npcs)} NPCs in POI.")
            else:
                print("❌ Failed to load NPC list")
        except Exception as e:
            print("❌ Error loading NPCs:", e)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_npc = (self.selected_npc + 1) % len(self.npcs)
            elif event.key == pygame.K_UP:
                self.selected_npc = (self.selected_npc - 1) % len(self.npcs)

    def fetch_npc_details(self, npc_id):
        try:
            res = requests.get(f"http://localhost:5050/npc/{npc_id}")
            if res.status_code == 200:
                return res.json()
            else:
                return {}
        except Exception as e:
            print("❌ Error fetching NPC details:", e)
            return {}

    def update(self):
        pass

    def draw(self):
        panel_x = 760
        panel_width = 260
        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x, 0, panel_width, 760))

        title = self.large_font.render("NPCs Nearby", True, (255, 255, 255))
        self.screen.blit(title, (panel_x + 20, 20))

        y = 80
        if not self.npcs:
            self.screen.blit(self.font.render("No NPCs found.", True, (200, 200, 200)), (panel_x + 20, y))
            return

        for i, npc_id in enumerate(self.npcs):
            color = (255, 255, 255) if i != self.selected_npc else (0, 255, 100)
            name_surface = self.font.render(npc_id, True, color)
            self.screen.blit(name_surface, (panel_x + 20, y))
            y += 30

        if self.npcs:
            # Draw selected NPC info
            npc_id = self.npcs[self.selected_npc]
            npc_data = self.fetch_npc_details(npc_id)
            if npc_data:
                info_y = 300
                self.screen.blit(self.font.render(f"Name: {npc_data.get('name', '?')}", True, (180, 220, 255)), (panel_x + 20, info_y))
                info_y += 30
                self.screen.blit(self.font.render(f"Faction: {npc_data.get('faction', 'None')}", True, (180, 220, 255)), (panel_x + 20, info_y))
                info_y += 30
                goodwill = npc_data.get("goodwill", 0)
                goodwill_bar_width = 200
                goodwill_fill = int((goodwill + 100) / 200 * goodwill_bar_width)

                # Goodwill Slider
                pygame.draw.rect(self.screen, (80, 80, 80), (panel_x + 20, info_y, goodwill_bar_width, 20))
                pygame.draw.rect(self.screen, (0, 255, 0), (panel_x + 20, info_y, goodwill_fill, 20))
                self.screen.blit(self.font.render("Goodwill", True, (255, 255, 255)), (panel_x + 20, info_y + 25))

        pygame.display.flip()
