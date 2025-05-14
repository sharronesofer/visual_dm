import pygame
import requests
from visual_client.ui.components.panel import Panel, PanelConfig
from visual_client.ui.components.grid_layout import GridLayout, GridLayoutConfig
from visual_client.ui.components.tooltip import Tooltip

class NPCAffinityDebugPanel:
    def __init__(self, screen, region_id=None, poi_id=None):
        self.screen = screen
        self.region_id = region_id
        self.poi_id = poi_id
        self.font = pygame.font.SysFont(None, 20)
        self.large_font = pygame.font.SysFont(None, 28)
        self.npcs = []
        self.affinities = {}
        self.selected_npc = None
        self.selected_pair = None
        self.tooltip = Tooltip(self.font)
        self._load_npcs_and_affinities()
        self._setup_layout()

    def _load_npcs_and_affinities(self):
        # Fetch NPCs in region/POI
        try:
            if self.region_id and self.poi_id:
                res = requests.get(f"http://localhost:5050/poi_state/{self.region_id}/{self.poi_id}")
                if res.status_code == 200:
                    poi_data = res.json()
                    self.npcs = poi_data.get("npcs_present", [])
            else:
                res = requests.get("http://localhost:5050/npcs")
                if res.status_code == 200:
                    self.npcs = res.json().get("npcs", [])
        except Exception as e:
            print("❌ Error loading NPCs:", e)
            self.npcs = []
        # Fetch all pairwise affinities
        self.affinities = {}
        for i, npc1 in enumerate(self.npcs):
            for j, npc2 in enumerate(self.npcs):
                if i == j:
                    continue
                try:
                    res = requests.get(f"http://localhost:5050/npc_affinity/{npc1}/{npc2}")
                    if res.status_code == 200:
                        self.affinities[(npc1, npc2)] = res.json()
                except Exception as e:
                    continue

    def _setup_layout(self):
        # Main panel
        self.panel = Panel(
            self.screen,
            PanelConfig(
                position=(40, 40),
                width=900,
                height=700,
                background_color=(36, 40, 50),
                border_color=(120, 120, 120),
                border_width=2,
                title="NPC Affinity Debug & Visualization"
            )
        )
        # Grid for affinity heatmap
        n = len(self.npcs)
        self.grid = GridLayout(
            self.screen,
            GridLayoutConfig(
                position=(60, 100),
                width=520,
                height=520,
                rows=n,
                cols=n,
                background_color=(44, 48, 60),
                border_color=(80, 80, 80),
                border_width=1,
                padding=4,
                cell_padding=2
            )
        )
        # Inspector panel
        self.inspector_panel = Panel(
            self.screen,
            PanelConfig(
                position=(600, 100),
                width=320,
                height=520,
                background_color=(30, 34, 44),
                border_color=(100, 100, 100),
                border_width=1,
                title="Inspector"
            )
        )

    def handle_event(self, event):
        # Grid cell hover/select
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for row in range(len(self.npcs)):
                for col in range(len(self.npcs)):
                    cell_rect = self.grid.get_cell_rect(row, col)
                    if cell_rect and cell_rect.collidepoint(mx, my):
                        npc1, npc2 = self.npcs[row], self.npcs[col]
                        if npc1 != npc2:
                            aff = self.affinities.get((npc1, npc2))
                            if aff:
                                self.tooltip.set_text(f"{npc1} ↔ {npc2}\nScore: {aff.get('score', '?')}\nType: {aff.get('relationship', '?')}")
                                self.tooltip.show((mx+10, my+10))
                                self.selected_pair = (npc1, npc2)
                                return
            self.tooltip.hide()
            self.selected_pair = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for row in range(len(self.npcs)):
                for col in range(len(self.npcs)):
                    cell_rect = self.grid.get_cell_rect(row, col)
                    if cell_rect and cell_rect.collidepoint(mx, my):
                        npc1, npc2 = self.npcs[row], self.npcs[col]
                        if npc1 != npc2:
                            self.selected_npc = npc1
                            return

    def update(self):
        pass  # Could poll for live updates if needed

    def draw(self):
        self.panel.draw()
        # Draw grid labels
        n = len(self.npcs)
        for i, npc in enumerate(self.npcs):
            label = self.font.render(npc, True, (200, 220, 255))
            self.screen.blit(label, (60 + i * (self.grid.cell_width + self.grid.config.cell_padding), 80))
            self.screen.blit(label, (30, 100 + i * (self.grid.cell_height + self.grid.config.cell_padding)))
        # Draw grid cells (heatmap)
        for row in range(n):
            for col in range(n):
                cell_rect = self.grid.get_cell_rect(row, col)
                if not cell_rect:
                    continue
                npc1, npc2 = self.npcs[row], self.npcs[col]
                color = (60, 60, 60) if npc1 == npc2 else self._affinity_color(self.affinities.get((npc1, npc2)))
                pygame.draw.rect(self.screen, color, cell_rect)
                if npc1 != npc2:
                    aff = self.affinities.get((npc1, npc2))
                    if aff:
                        score = aff.get('score', '?')
                        txt = self.font.render(str(score), True, (255,255,255))
                        self.screen.blit(txt, (cell_rect.x+6, cell_rect.y+4))
        self.grid.draw()
        # Draw inspector
        self.inspector_panel.draw()
        if self.selected_npc:
            y = 140
            npc = self.selected_npc
            self.screen.blit(self.large_font.render(f"NPC: {npc}", True, (220,220,255)), (610, y))
            y += 40
            for other in self.npcs:
                if other == npc:
                    continue
                aff = self.affinities.get((npc, other))
                if aff:
                    rel = aff.get('relationship', '?')
                    score = aff.get('score', '?')
                    self.screen.blit(self.font.render(f"{other}: {rel} ({score})", True, (200,255,200)), (620, y))
                    y += 28
        # Draw tooltip
        self.tooltip.draw(self.screen)

    def _affinity_color(self, aff):
        if not aff:
            return (80, 80, 80)
        score = aff.get('score', 0)
        # Blue for negative, red for positive, green for neutral
        if score >= 80:
            return (255, 80, 80)
        elif score >= 50:
            return (255, 140, 100)
        elif score >= 20:
            return (255, 220, 120)
        elif score <= -60:
            return (80, 80, 255)
        elif score <= -30:
            return (120, 120, 255)
        elif score < 0:
            return (180, 180, 255)
        else:
            return (120, 255, 120) 