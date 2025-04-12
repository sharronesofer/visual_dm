from flask import Flask
from basic import basic_bp
from gpt_endpoints import gpt_bp
from rules_endpoints import rules_bp  # ← New rules system
from auth import auth_bp  # Import the authentication blueprint
import firebase_admin
from firebase_admin import credentials
import json
import openai
from flask import send_from_directory

# Load OpenAI API key
try:
    with open("openai_api_key.json") as key_file:
        key_data = json.load(key_file)
    openai.api_key = key_data.get("api_key")
    if not openai.api_key:
        raise ValueError("No API key found in openai_api_key.json")
    print("OpenAI API key loaded successfully.")
except Exception as e:
    print("Failed to load OpenAI API key:", e)

# Initialize Firebase Admin SDK (Only once in main.py)
try:
    cred = credentials.Certificate('./firebase_credentials.json')  # Ensure this path is correct
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://visual-dm-default-rtdb.firebaseio.com/'  # Ensure this is your Firebase Realtime Database URL
    })
    print("Firebase initialized successfully.")
except Exception as e:
    print("Firebase initialization failed:", e)

# Initialize the Flask app
app = Flask(__name__)

# Register the blueprints
app.register_blueprint(basic_bp)
app.register_blueprint(gpt_bp)
app.register_blueprint(rules_bp)  # Register rules endpoints
app.register_blueprint(auth_bp, url_prefix='/auth')  # Register authentication endpoints with `/auth` prefix

@app.route('/chat/')
def serve_index():
    return send_from_directory('.', 'chat.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)

def update_player_arc(player_id, arc_name, arc_choices, arc_progress, npc_reactions):
    # Update the player's arc data
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    if not player_data:
        return {"error": "Player not found"}

    # Update the player's arc data
    player_ref.update({
        "current_arc": arc_name,
        "arc_choices": arc_choices,
        "arc_progress": arc_progress,
        "npc_reactions": npc_reactions
    })

    return {"status": "Player arc updated", "player_id": player_id}

