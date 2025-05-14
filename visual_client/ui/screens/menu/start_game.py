import pygame
from uuid import uuid4
import requests
import os
from textwrap import wrap
import uuid
from dotenv import load_dotenv
from visual_client.ui.components import Tooltip
from visual_client.ui.screens.region_map_screen import RegionMapScreen
import time

load_dotenv()  # Load environment variables early

DISABLE_PORTRAITS = True

class StartGameScreen:
    def __init__(self, screen, character_data):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.SysFont(None, 32)
        self.character_data = character_data
        self.character_id = character_data.get("character_id")
        self.tooltip = Tooltip(self.font, "")
        self.next_screen = None

        self.response_text = "Loading your character..."
        self.full_text = character_data.get("background", "")
        self.visible_text = ""
        self.status = "done"  # Start as done since we have existing data
        self.confirm_button = pygame.Rect(300, 400, 200, 50)
        self.spinner_chars = ["|", "/", "-", "\\\\"]
        self.show_confirm = False  # Initialize show_confirm attribute

        # Only generate new content if character doesn't have it
        if not self.full_text:
            self.status = "loading"
            self._generate_starting_world()
        else:
            print("✅ Using existing character background")

        # Only create new arc if character doesn't have one
        if not character_data.get("arc"):
            self._create_arc()
        else:
            print("✅ Using existing character arc")

        self._start_time = pygame.time.get_ticks()
        self._char_index = 0
        self._spinner_index = 0
        self._last_update = pygame.time.get_ticks()

    def _generate_starting_world(self):
        # Only GPT world generation now
        try:
            prompt = (
                "Describe the fantasy world for this character in 300 words or fewer. "
                "Include a capital city. Write for a player starting a quest.\n\n"
                f"Background: {self.character_data.get('background', '')}"
            )
            res = requests.post(
                "http://localhost:5050/dm_response",
                json={
                    "mode": "start_game",
                    "character_id": self.character_id,
                    "prompt": prompt
                },
                timeout=60
            )
            res.raise_for_status()
            reply = res.json()
            self.full_text = reply.get("reply", "").strip() or "[No world description generated]"
            self.status = "typing"
            print("📜 GPT response text:", self.full_text)

        except (requests.exceptions.RequestException, ValueError) as e:
            self.status = "error"
            self.full_text = f"Error during GPT call: {e}"
            print("❌ GPT request failed:", e)

        self._post_character()
        self._create_arc()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.confirm_button.collidepoint(event.pos) and self.status == "done":
                region = self.character_data.get("region_id", "dev_region")
                char_id = self.character_data.get("character_id", "test_unknown")
                self.next_screen = RegionMapScreen(self.screen, region, char_id)

    def update(self):
        now = pygame.time.get_ticks()

        if self.status == "typing":
            if now - self._last_update > 30 and self._char_index < len(self.full_text):
                self.visible_text += self.full_text[self._char_index]
                self._char_index += 1
                self._last_update = now
            elif self._char_index >= len(self.full_text):
                self.status = "done"

        elif self.status == "waiting":
            if now - self._last_update > 150:
                self._spinner_index = (self._spinner_index + 1) % len(self.spinner_chars)
                self._last_update = now

    def draw(self, surface):
        surface.fill((0, 0, 0))
        
        # Draw loading text
        text = self.font.render(self.response_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(text, text_rect)
        
        # Draw spinner animation
        spinner_char = self.spinner_chars[int(time.time() * 4) % len(self.spinner_chars)]
        spinner_text = self.font.render(spinner_char, True, (255, 255, 255))
        spinner_rect = spinner_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 40))
        surface.blit(spinner_text, spinner_rect)
        
        # Draw confirm button if needed
        if self.show_confirm:
            pygame.draw.rect(surface, (0, 255, 0), self.confirm_button)
            confirm_text = self.font.render("Begin Adventure", True, (0, 0, 0))
            text_rect = confirm_text.get_rect(center=self.confirm_button.center)
            surface.blit(confirm_text, text_rect)

    def _draw_portrait(self):
        portrait_url = self.character_data.get("portrait_url", "")
        if portrait_url and portrait_url.startswith("http"):
            try:
                import urllib.request
                import io
                from PIL import Image

                response = urllib.request.urlopen(portrait_url)
                image_file = io.BytesIO(response.read())
                img = Image.open(image_file).convert("RGB")

                portrait_surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
                portrait_surface = pygame.transform.scale(portrait_surface, (256, 256))
                self.screen.blit(portrait_surface, (720, 40))
            except Exception as e:
                self.screen.blit(self.font.render("Portrait load failed", True, (255, 0, 0)), (720, 40))
                print("❌ Portrait load error:", e)
        else:
            self.screen.blit(self.font.render("Portraits are disabled.", True, (120, 120, 120)), (720, 40))

    def _post_character(self):
        try:
            res = requests.post("http://localhost:5050/character/create", json=self.character_data, timeout=10)
            if res.status_code == 200:
                print("✅ Character saved to Firebase.")
            else:
                print(f"❌ Error saving character: {res.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error posting character:", e)

    def _create_arc(self):
        # Only create new arc if character doesn't have one
        if self.character_data.get("arc"):
            print("✅ Using existing character arc")
            return

        background = self.character_data.get("background", "")
        backstory = f"Player begins their journey. Background: '{background}'"
        try:
            res = requests.post(
                f"http://localhost:5050/arc/{self.character_id}",
                json={"event": backstory},
                timeout=10
            )
            if res.status_code == 200:
                arc = res.json()
                print("🌐 Arc created:", arc.get("summary", "[No summary]"))
            else:
                print(f"❌ Arc creation failed: {res.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Arc creation error:", e)
