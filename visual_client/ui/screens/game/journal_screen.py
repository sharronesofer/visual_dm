import pygame
import requests

class JournalScreen:
    def __init__(self, screen, character_id, region_id):
        self.screen = screen
        self.character_id = character_id
        self.region_id = region_id
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 32)

        self.tabs = ["Quests", "Rumors", "Notes"]
        self.selected_tab = 0
        self.data = {"Quests": [], "Rumors": [], "Notes": []}

        self.new_note = ""
        self.new_note_active = False
        self.branch_choices = {}  # quest_id -> list of branches
        self.selected_branch = {}  # quest_id -> selected branch index
        self.branch_feedback = {}  # quest_id -> feedback message

        self.load_data()

    def load_data(self):
        try:
            q = requests.get(f"http://localhost:5050/quests/{self.character_id}")
            if q.status_code == 200:
                self.data["Quests"] = q.json()
                # For each quest, fetch available branches
                for quest in self.data["Quests"]:
                    quest_id = quest.get("id")
                    if quest_id is not None:
                        try:
                            b = requests.get(f"http://localhost:5050/quests/{self.character_id}/{quest_id}/branches")
                            if b.status_code == 200:
                                branches = b.json()
                                self.branch_choices[quest_id] = branches
                                self.selected_branch[quest_id] = 0 if branches else None
                            else:
                                self.branch_choices[quest_id] = []
                        except Exception as e:
                            print(f"❌ Error loading branches for quest {quest_id}:", e)
                            self.branch_choices[quest_id] = []
        except Exception as e:
            print("❌ Error loading quests:", e)

        try:
            r = requests.get(f"http://localhost:5050/rumors/{self.region_id}")
            if r.status_code == 200:
                self.data["Rumors"] = r.json()
        except Exception as e:
            print("❌ Error loading rumors:", e)

        try:
            n = requests.get(f"http://localhost:5050/notes/{self.character_id}")
            if n.status_code == 200:
                self.data["Notes"] = n.json()
        except Exception as e:
            print("❌ Error loading notes:", e)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.selected_tab = (self.selected_tab + 1) % len(self.tabs)
            elif event.key == pygame.K_LEFT:
                self.selected_tab = (self.selected_tab - 1) % len(self.tabs)
            elif self.new_note_active:
                if event.key == pygame.K_RETURN:
                    self.save_new_note()
                elif event.key == pygame.K_BACKSPACE:
                    self.new_note = self.new_note[:-1]
                else:
                    self.new_note += event.unicode
            elif event.key == pygame.K_n and self.tabs[self.selected_tab] == "Notes":
                self.new_note_active = True
                self.new_note = ""
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.tabs[self.selected_tab] == "Quests":
                # Check for branch selection clicks
                mouse_x, mouse_y = event.pos
                y = 100
                for quest in self.data["Quests"]:
                    quest_id = quest.get("id")
                    branches = self.branch_choices.get(quest_id, [])
                    if branches:
                        for i, branch in enumerate(branches):
                            btn_rect = pygame.Rect(400, y + i * 32, 220, 28)
                            if btn_rect.collidepoint(mouse_x, mouse_y):
                                self.selected_branch[quest_id] = i
                                self.choose_branch(quest_id, branch)
                        y += 32 * len(branches)
                    y += 30

    def choose_branch(self, quest_id, branch):
        try:
            res = requests.post(
                f"http://localhost:5050/quests/{self.character_id}/{quest_id}/choose_branch",
                json={"branch_id": branch.get("id")}
            )
            if res.status_code == 200:
                resp = res.json()
                self.branch_feedback[quest_id] = "Branch chosen! Quest progressed."
                # Update quest in self.data["Quests"] if new state is returned
                if resp.get("quest"):
                    for i, q in enumerate(self.data["Quests"]):
                        if q.get("id") == quest_id:
                            self.data["Quests"][i] = resp["quest"]
                            break
                self.load_data()
            else:
                self.branch_feedback[quest_id] = f"Failed: {res.text}"
        except Exception as e:
            self.branch_feedback[quest_id] = f"Error: {e}"

    def save_new_note(self):
        try:
            res = requests.post(f"http://localhost:5050/notes/{self.character_id}", json={"note": self.new_note})
            if res.status_code == 200:
                print("✅ Note saved.")
                self.load_data()
            else:
                print("❌ Failed to save note")
        except Exception as e:
            print("❌ Error saving note:", e)
        self.new_note_active = False
        self.new_note = ""

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

        # Draw Current Tab Content
        tab_name = self.tabs[self.selected_tab]
        entries = self.data.get(tab_name, [])

        y = 100
        if not entries:
            self.screen.blit(self.font.render(f"No {tab_name.lower()} found.", True, (150, 150, 150)), (100, y))
        else:
            for entry in entries:
                line = entry if isinstance(entry, str) else str(entry)
                quest_id = entry.get("id") if isinstance(entry, dict) else None
                rendered = self.font.render(line, True, (180, 220, 180))
                self.screen.blit(rendered, (100, y))
                # Draw quest branches if available
                branches = self.branch_choices.get(quest_id, [])
                if branches:
                    for i, branch in enumerate(branches):
                        btn_rect = pygame.Rect(400, y + i * 32, 220, 28)
                        btn_color = (80, 180, 80) if self.selected_branch.get(quest_id) == i else (60, 60, 60)
                        pygame.draw.rect(self.screen, btn_color, btn_rect)
                        branch_label = self.font.render(branch.get("description", f"Branch {i+1}"), True, (255, 255, 255))
                        self.screen.blit(branch_label, (btn_rect.x + 8, btn_rect.y + 4))
                    # Draw feedback if any
                    feedback = self.branch_feedback.get(quest_id)
                    if feedback:
                        self.screen.blit(self.font.render(feedback, True, (255, 220, 120)), (400, y + len(branches) * 32 + 4))
                    y += 32 * len(branches)
                y += 30

        # If adding a new note
        if self.new_note_active:
            self.screen.blit(self.font.render("New Note (Enter to Save):", True, (255, 255, 0)), (100, 550))
            note_surface = self.font.render(self.new_note, True, (255, 255, 255))
            self.screen.blit(note_surface, (100, 580))

        pygame.display.flip()
