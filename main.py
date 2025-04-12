# main.py
import os
import logging
import firebase_admin
from menu import menu_bp
from rules_endpoints import rules_bp
from flask import Flask, jsonify
from firebase_admin import initialize_app, credentials, db
from inventory import inventory_bp
from world_map import visual_bp
from basic import basic_bp, relationship_bp, auth_bp, gpt_bp
from quest_engine import create_quest_log_entry, extract_quest_from_reply
from worldgen import worldgen_bp
from relationship_engine import releng_bp
from party_engine import party_bp
from rules_endpoints import rules_bp
from player_routes import player_bp  # <-- explicitly import new blueprint
from character_management import character_bp
from npc_management import npc_management_bp
from npc_relationships import npc_relationships_bp
from npc_interactions import npc_interactions_bp

def create_app():
    app = Flask(__name__)

    # Initialize Firebase Admin once
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://visual-dm-default-rtdb.firebaseio.com"  # Make sure this is correct for your Firebase project
    })

    # Register your Blueprints
    # 1) No prefix for basic_bp → so /chat is at GET /chat
    app.register_blueprint(basic_bp)
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(character_bp)

    # 2) Auth routes at /auth
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 3) Relationship routes at /relationship
    app.register_blueprint(relationship_bp, url_prefix='/relationship')

    # 4) GPT blueprint with no prefix, so /dm_response is just /dm_response
    app.register_blueprint(gpt_bp)
    app.register_blueprint(npc_management_bp)
    app.register_blueprint(npc_relationships_bp)
    app.register_blueprint(npc_interactions_bp)
    # 5) Other blueprints if you want them
    app.register_blueprint(worldgen_bp, url_prefix='/worldgen')
    app.register_blueprint(releng_bp, url_prefix='/releng')
    app.register_blueprint(party_bp, url_prefix='/party')
    app.register_blueprint(player_bp)  # <-- explicitly register new blueprint

    # Possibly also register rules_bp if you want
    # app.register_blueprint(rules_bp, url_prefix='/rules')
    app.register_blueprint(menu_bp)  # No prefix means /character_creator/start is correct
    app.register_blueprint(rules_bp, url_prefix="/rules")  # So /rules/classes will work
    app.register_blueprint(visual_bp)  # <-- Do NOT use a prefix unless your frontend matches it

    # Other configuration
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {list(rule.methods)} {rule.rule}")

    return app

if __name__ == "__main__":
    debug_mode = True
    port_num = 5050

    app = create_app()
    app.run(debug=debug_mode, port=port_num)
