
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from visual_client.menus.main_menu import main_menu
import visual_client.start_game as start_game

if __name__ == "__main__":
    print("Launching Visual Client...")

    while True:
        result = main_menu()

        if isinstance(result, dict):
            next_action = result.get("next")

            if next_action == "start_game":
                character = result.get("character")
                if character:
                    start_game.launch_start_game(character)
                else:
                    print("⚠️ Missing character data in result.")

            elif next_action == "map_view":
                print(f"✅ Map view completed for player ID: {result.get('character_id')}")

            elif next_action == "quit":
                print("✅ User quit the main menu.")
                break

            else:
                print("❓ Unknown 'next' value returned from main menu:", next_action)
        else:
            print("⚠️ main_menu did not return a result dict. Exiting.")
            break
