from flask import Flask, request, jsonify, send_from_directory, Blueprint
import firebase_admin
from firebase_admin import credentials, auth, db
import json
import openai

# === Load OpenAI API key ===
try:
    with open("openai_api_key.json") as key_file:
        key_data = json.load(key_file)
    openai.api_key = key_data.get("api_key")
    if not openai.api_key:
        raise ValueError("No API key found in openai_api_key.json")
    print("OpenAI API key loaded successfully.")
except Exception as e:
    print("Failed to load OpenAI API key:", e)

# === Initialize Firebase ===
try:
    cred = credentials.Certificate('./firebase_credentials.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://visual-dm-default-rtdb.firebaseio.com/'
    })
    print("Firebase initialized successfully.")
except Exception as e:
    print("Firebase initialization failed:", e)

# === Flask App ===
app = Flask(__name__)

# === Blueprints ===
from basic import basic_bp
from gpt_endpoints import gpt_bp
from rules_endpoints import rules_bp

app.register_blueprint(basic_bp)
app.register_blueprint(gpt_bp)
app.register_blueprint(rules_bp)

# === Authentication Blueprint ===
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not email or not password or not username:
        return jsonify({"error": "Email, password, and username are required"}), 400

    try:
        user = auth.create_user(email=email, password=password)
        user_ref = db.reference(f"/users/{user.uid}")
        user_ref.set({
            "username": username,
            "email": email,
            "character_data": {}
        })
        return jsonify({"message": "User created successfully", "user_id": user.uid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")  # Not used with Admin SDK, client-side validation assumed

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        user = auth.get_user_by_email(email)
        user_ref = db.reference(f"/users/{user.uid}")
        user_data = user_ref.get()

        if not user_data:
            return jsonify({"error": "User data not found in database"}), 404

        return jsonify({
            "message": "Login successful",
            "user_id": user.uid,
            "username": user_data.get("username"),
            "character_data": user_data.get("character_data")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "User logged out successfully"})

# Register auth routes
app.register_blueprint(auth_bp, url_prefix='/auth')

# === Static Chat UI ===
@app.route('/chat/')
def serve_index():
    return send_from_directory('.', 'chat.html')

# === Arc Updater ===
def update_player_arc(player_id, arc_name, arc_choices, arc_progress, npc_reactions):
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    if not player_data:
        return {"error": "Player not found"}

    player_ref.update({
        "current_arc": arc_name,
        "arc_choices": arc_choices,
        "arc_progress": arc_progress,
        "npc_reactions": npc_reactions
    })

    return {"status": "Player arc updated", "player_id": player_id}

# === Entry Point ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
