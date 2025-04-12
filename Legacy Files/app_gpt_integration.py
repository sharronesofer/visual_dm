import os
import json
import openai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# ---------------------------
# App Initialization & Logging
# ---------------------------
app = Flask(__name__)
CORS(app)

# Set up a rotating file handler (max 1MB per file, with 3 backups)
handler = RotatingFileHandler('gpt_app.log', maxBytes=1_000_000, backupCount=3)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# ---------------------------
# Firebase & OpenAI Setup
# ---------------------------
try:
    cred = credentials.Certificate('./firebase_credentials.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://visual-dm-default-rtdb.firebaseio.com/'
    })
    app.logger.info("Firebase initialized successfully.")
except Exception as e:
    app.logger.error("Firebase initialization failed: %s", str(e))

try:
    with open("openai_api_key.json") as key_file:
        key_data = json.load(key_file)
    openai.api_key = key_data.get("api_key")
    app.logger.info("OpenAI API key loaded successfully.")
except Exception as e:
    app.logger.error("Failed to load OpenAI API key: %s", str(e))

# ---------------------------
# Advanced GPT Integration Functions
# ---------------------------
def build_dm_context():
    """
    Builds context for the Dungeon Master GPT by retrieving the global state.
    """
    try:
        global_state = db.reference('/global_state').get() or {}
    except Exception as e:
        app.logger.error("Error fetching global state for DM context: %s", str(e))
        global_state = {}
    context = f"Global State: {json.dumps(global_state)}"
    return context

def build_npc_context(npc_id):
    """
    Builds context for an NPC by retrieving its memory and knowledge.
    """
    try:
        npc_memory = db.reference(f'/npc_memory/{npc_id.lower()}').get() or {}
        npc_knowledge = db.reference(f'/npc_knowledge/{npc_id.lower()}').get() or {}
    except Exception as e:
        app.logger.error("Error fetching NPC data for context: %s", str(e))
        npc_memory = {}
        npc_knowledge = {}
    context = f"NPC Memory: {json.dumps(npc_memory)}; NPC Knowledge: {json.dumps(npc_knowledge)}"
    return context

def gpt_router(importance_score, flags=None):
    """
    Selects the GPT model based on an importance score and optional flags.
    
    For importance scores 7 or higher (or if force_gpt4 flag is set), GPT-4 is used.
    Otherwise, a lighter model (e.g., gpt-3.5-turbo) is chosen.
    """
    if flags is None:
        flags = {}
    if importance_score >= 7 or flags.get("force_gpt4", False):
        return "gpt-4"
    else:
        return "gpt-3.5-turbo"

# ---------------------------
# Global Error Handler
# ---------------------------
@app.errorhandler(Exception)
def global_error_handler(error):
    app.logger.error("Unhandled Exception: %s", str(error))
    return jsonify({"error": "An internal error occurred.", "details": str(error)}), 500

# ---------------------------
# Basic Index Endpoint
# ---------------------------
@app.route('/')
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        app.logger.error("Error rendering index: %s", str(e))
        raise

# ---------------------------
# Updated GPT Endpoints
# ---------------------------
@app.route('/npc_interact', methods=['POST'])
def npc_interact():
    """
    Processes an NPC interaction by bundling NPC context, conversation history, and the prompt.
    The endpoint uses gpt_router to select the appropriate GPT model.
    
    Expected JSON input:
    {
      "npc_id": "npc_identifier",
      "conversation_history": "Previous dialogue or context",
      "prompt": "Situation or dialogue prompt for the NPC",
      "importance_score": 5,  # Optional (default 5)
      "flags": {}             # Optional flags (e.g., {"force_gpt4": true})
    }
    """
    try:
        data = request.json
        npc_id = data.get("npc_id", "")
        conversation_history = data.get("conversation_history", "")
        prompt = data.get("prompt", "")
        importance_score = data.get("importance_score", 5)
        flags = data.get("flags", {})

        if not npc_id or not prompt:
            return jsonify({"error": "npc_id and prompt are required"}), 400

        npc_context = build_npc_context(npc_id)
        full_prompt = (
            f"NPC Context: {npc_context}\n"
            f"Conversation History: {conversation_history}\n"
            f"Prompt: {prompt}"
        )
        model_to_use = gpt_router(importance_score, flags)
        response = openai.ChatCompletion.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"npc_id": npc_id, "reply": reply, "model_used": model_to_use})
    except Exception as e:
        app.logger.error("Error in npc_interact: %s", str(e))
        raise

@app.route('/dm_response', methods=['POST'])
def dm_response():
    """
    Generates a Dungeon Master narrative response by bundling DM context and a prompt.
    The gpt_router function determines which GPT model to use.
    
    Expected JSON input:
    {
      "prompt": "Narrative prompt for the DM",
      "importance_score": 5,  # Optional (default 5)
      "flags": {}             # Optional flags (e.g., {"force_gpt4": true})
    }
    """
    try:
        data = request.json
        prompt = data.get("prompt", "")
        importance_score = data.get("importance_score", 5)
        flags = data.get("flags", {})

        if not prompt:
            return jsonify({"error": "prompt is required"}), 400

        dm_context = build_dm_context()
        full_prompt = f"DM Context: {dm_context}\nPrompt: {prompt}"
        model_to_use = gpt_router(importance_score, flags)
        response = openai.ChatCompletion.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": "You are the Dungeon Master narrating a persistent fantasy world."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.8,
            max_tokens=200
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply, "model_used": model_to_use})
    except Exception as e:
        app.logger.error("Error in dm_response: %s", str(e))
        raise

# ---------------------------
# Run the Flask App
# ---------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
