import pygame
import requests
import json
from textwrap import wrap

class WorldInspectorPanel:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 32)

        self.tabs = ["Global", "Regional", "POI"]
        self.selected_tab = 0
        self.data = {"Global": {}, "Regional": {}, "POI": {}}

        self.load_summary()

    def load_summary(self):
        try:
            res = requests.get("http://localhost:5050/world_summary")
            if res.status_code == 200:
                world = res.json()
                self.data["Global"] = world.get("global_state", {})
                self.data["Regional"] = world.get("regional_state", {})
                self.data["POI"] = world.get("poi_state", {})
            else:
                print("❌ Failed to load world summary.")
        except Exception as e:
            print("❌ Error loading world data:", e)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.selected_tab = (self.selected_tab + 1) % len(self.tabs)
            elif event.key == pygame.K_LEFT:
                self.selected_tab = (self.selected_tab - 1) % len(self.tabs)

    def update(self):
        pass

    def draw(self):
        self.screen.fill((0, 0, 0))

        # Draw Tabs
        x = 100
        for i, tab in enumerate(self.tabs):
            color = (255, 255, 0) if i == self.selected_tab else (200, 200, 200)
            label = self.large_font.render(tab, True, color)
            self.screen.blit(label, (x, 20))
            x += 200

        # Draw Data
        tab_name = self.tabs[self.selected_tab]
        state = self.data.get(tab_name, {})

        y = 100
        if not state:
            self.screen.blit(self.font.render(f"No {tab_name} data found.", True, (150, 150, 150)), (100, y))
        else:
            formatted = json.dumps(state, indent=2)
            lines = wrap(formatted, width=80)

            for line in lines:
                rendered = self.font.render(line, True, (180, 220, 180))
                self.screen.blit(rendered, (60, y))
                y += 25
                if y > 720:  # simple overflow cutoff
                    break

        pygame.display.flip()
