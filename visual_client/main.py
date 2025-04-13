# visual_client/main.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from screens.main_menu import main_menu
from screens.start_game import launch_start_game
from screens.ascii_map_viewer import main as launch_map

def run():
    print("🎮 Launching Visual Client...")

    while True:
        result = main_menu()

        if not isinstance(result, dict):
            print("⚠️ main_menu() did not return a dict. Exiting.")
            break

        next_action = result.get("next")

        if next_action == "start_game":
            character = result.get("character")
            if character:
                launch_start_game(character)
            else:
                print("⚠️ No character provided for start_game.")

        elif next_action == "map_view":
            character_id = result.get("character_id")
            if character_id:
                launch_map(character_id=character_id)
            else:
                print("⚠️ No character_id provided for map_view.")

        elif next_action == "quit":
            print("👋 Exiting game.")
            break

        else:
            print(f"❓ Unknown next action: {next_action}")
            break

if __name__ == "__main__":
    run()
