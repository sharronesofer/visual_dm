from flask import Flask
from flask_cors import CORS
from firebase_admin import credentials, initialize_app
import json

# === Blueprint Imports ===
from app.auth.auth_routes import auth_bp
from app.characters.character_routes import character_bp
from app.combat.combat_routes import combat_bp
from app.data.inventory_routes import inventory_bp
from app.data.menu_routes import menu_bp
from app.data.party_routes import party_bp
from app.dm_engine.dm_routes import dm_engine_bp
from app.memory.memory_routes import memory_bp
from app.motifs.motif_routes import motif_bp
from app.npc.npc_routes import npc_routes_bp
from app.quests.quest_routes import quest_bp
from app.regions.region_routes import region_management_bp
from app.regions.tension_routes import tension_bp
from app.regions.worldgen_routes import worldgen_bp
from app.rules.rules_routes import rules_bp
from app.rules.rules_validation_routes import rules_validation_bp
from app.visuals.tile_routes import tiles_bp

# === App Setup ===
app = Flask(__name__)
CORS(app)

# === Firebase Setup ===
try:
    cred = credentials.Certificate('./firebase_credentials.json')
    initialize_app(cred, {
        'databaseURL': 'https://visual-dm-default-rtdb.firebaseio.com/'
    })
    print("Firebase initialized.")
except Exception as e:
    print(f"Failed to initialize Firebase: {e}")

# === Register Blueprints ===
app.register_blueprint(auth_bp)
app.register_blueprint(character_bp)
app.register_blueprint(combat_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(party_bp)
app.register_blueprint(dm_engine_bp)
app.register_blueprint(memory_bp)
app.register_blueprint(motif_bp)
app.register_blueprint(npc_routes_bp)
app.register_blueprint(quest_bp)
app.register_blueprint(region_management_bp)
app.register_blueprint(tension_bp)
app.register_blueprint(worldgen_bp)
app.register_blueprint(rules_bp)
app.register_blueprint(rules_validation_bp)
app.register_blueprint(tiles_bp)

# === Run App ===
if __name__ == "__main__":
    app.run(debug=True, port=5050)
