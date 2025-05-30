#!/usr/bin/env python3
"""
Mock Server for Visual DM Backend API
====================================

Flask-based mock server that serves JSON fixtures for all API endpoints
according to the extracted API contracts. Provides realistic responses,
proper HTTP status codes, CORS support, and authentication simulation.

This server allows Unity frontend development without requiring the full
backend infrastructure.

Usage:
    python mock_server.py [--port PORT] [--host HOST] [--debug]
"""

import argparse
import json
import os
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import uuid4
import re

from flask import Flask, request, jsonify, Response
from flask_cors import CORS


class MockServer:
    """Mock server for Visual DM backend API."""
    
    def __init__(self, fixtures_dir: str = "."):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for Unity integration
        
        self.fixtures_dir = fixtures_dir
        self.fixtures_cache = {}
        self.load_fixtures()
        self.setup_routes()
        self.setup_middleware()
        
        # Authentication simulation
        self.valid_tokens = {
            "dev_token_123": {
                "user_id": "test-user-1",
                "username": "developer",
                "permissions": ["read", "write", "admin"]
            },
            "player_token_456": {
                "user_id": "test-user-2", 
                "username": "player",
                "permissions": ["read", "write"]
            }
        }
    
    def load_fixtures(self):
        """Load all fixtures into memory for fast access."""
        print("🔄 Loading fixtures into cache...")
        
        for system_dir in os.listdir(self.fixtures_dir):
            system_path = os.path.join(self.fixtures_dir, system_dir)
            if os.path.isdir(system_path) and system_dir != "__pycache__":
                self.fixtures_cache[system_dir] = {}
                
                for fixture_file in os.listdir(system_path):
                    if fixture_file.endswith('.json'):
                        fixture_path = os.path.join(system_path, fixture_file)
                        try:
                            with open(fixture_path, 'r') as f:
                                fixture_name = fixture_file.replace('.json', '')
                                self.fixtures_cache[system_dir][fixture_name] = json.load(f)
                        except Exception as e:
                            print(f"⚠️  Failed to load fixture {fixture_path}: {e}")
        
        print(f"✅ Loaded fixtures for {len(self.fixtures_cache)} systems")
    
    def setup_middleware(self):
        """Setup middleware for logging and timing."""
        
        @self.app.before_request
        def log_request():
            print(f"📥 {request.method} {request.path} - {datetime.now().strftime('%H:%M:%S')}")
        
        @self.app.after_request
        def add_headers(response):
            # Add realistic response headers
            response.headers['X-API-Version'] = '1.0.0'
            response.headers['X-Response-Time'] = f"{random.randint(50, 300)}ms"
            response.headers['X-Request-ID'] = str(uuid4())
            
            # Simulate realistic response timing
            time.sleep(random.uniform(0.1, 0.5))
            
            return response
    
    def authenticate_request(self) -> Optional[Dict[str, Any]]:
        """Simulate authentication based on Authorization header."""
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            # For development, allow some endpoints without auth
            if request.endpoint in ['health', 'docs']:
                return {"user_id": "anonymous", "permissions": ["read"]}
            return None
        
        # Extract token from "Bearer TOKEN" format
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        return self.valid_tokens.get(token)
    
    def get_fixture(self, system: str, fixture_name: str, default=None) -> Any:
        """Get a fixture from the cache."""
        return self.fixtures_cache.get(system, {}).get(fixture_name, default)
    
    def generate_id(self, id_format: str = "uuid") -> str:
        """Generate an ID based on format."""
        if id_format == "int":
            return str(random.randint(1, 100000))
        return str(uuid4())
    
    def create_error_response(self, code: int, message: str = None) -> Response:
        """Create standardized error response."""
        error_messages = {
            400: "Bad Request - Invalid input parameters",
            401: "Unauthorized - Authentication required", 
            403: "Forbidden - Insufficient permissions",
            404: "Not Found - Resource does not exist",
            422: "Unprocessable Entity - Validation error",
            500: "Internal Server Error - An unexpected error occurred"
        }
        
        if not message:
            message = error_messages.get(code, "Unknown error")
        
        return jsonify({
            "detail": message,
            "code": f"HTTP_{code}",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), code
    
    def create_success_response(self, data: Any = None, message: str = "Success") -> Response:
        """Create standardized success response."""
        if data is None:
            return jsonify({
                "status": "success",
                "message": message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        return jsonify(data)
    
    def setup_routes(self):
        """Setup all API routes based on the backend systems."""
        
        # Health check endpoint
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": "1.0.0",
                "systems": list(self.fixtures_cache.keys())
            })
        
        # Character system endpoints
        self.setup_character_routes()
        
        # NPC system endpoints
        self.setup_npc_routes()
        
        # Quest system endpoints
        self.setup_quest_routes()
        
        # Arc system endpoints
        self.setup_arc_routes()
        
        # Magic system endpoints
        self.setup_magic_routes()
        
        # Equipment system endpoints
        self.setup_equipment_routes()
        
        # Economy system endpoints
        self.setup_economy_routes()
        
        # Combat system endpoints
        self.setup_combat_routes()
        
        # Faction system endpoints
        self.setup_faction_routes()
        
        # Region system endpoints
        self.setup_region_routes()
        
        # Generic system endpoints
        self.setup_generic_routes()
    
    def setup_character_routes(self):
        """Setup character system routes."""
        
        @self.app.route('/characters', methods=['GET'])
        def get_characters():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            characters = self.get_fixture('character', 'characters_list', [])
            return self.create_success_response(characters)
        
        @self.app.route('/characters', methods=['POST'])
        def create_character():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            if not request.is_json:
                return self.create_error_response(400, "Content-Type must be application/json")
            
            character_data = request.get_json()
            template = self.get_fixture('character', 'character', {})
            
            # Create new character from template
            new_character = template.copy()
            new_character.update({
                'id': self.generate_id("uuid"),
                'created_at': datetime.utcnow().isoformat() + "Z",
                'updated_at': datetime.utcnow().isoformat() + "Z",
                **character_data
            })
            
            return self.create_success_response(new_character), 201
        
        @self.app.route('/characters/<character_id>', methods=['GET'])
        def get_character(character_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            character = self.get_fixture('character', 'character')
            if not character:
                return self.create_error_response(404, "Character not found")
            
            # Update character ID to match request
            character = character.copy()
            character['id'] = character_id
            
            return self.create_success_response(character)
        
        @self.app.route('/characters/<character_id>', methods=['PUT'])
        def update_character(character_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            if not request.is_json:
                return self.create_error_response(400, "Content-Type must be application/json")
            
            update_data = request.get_json()
            character = self.get_fixture('character', 'character', {}).copy()
            character.update({
                'id': character_id,
                'updated_at': datetime.utcnow().isoformat() + "Z",
                **update_data
            })
            
            return self.create_success_response(character)
        
        @self.app.route('/characters/<character_id>', methods=['DELETE'])
        def delete_character(character_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            return self.create_success_response(message=f"Character {character_id} deleted")
    
    def setup_npc_routes(self):
        """Setup NPC system routes."""
        
        @self.app.route('/npcs', methods=['GET'])
        def get_npcs():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            # Filter by region if specified
            region_id = request.args.get('region_id')
            npcs = self.get_fixture('npc', 'npcs_list', [])
            
            if region_id:
                npcs = [npc for npc in npcs if npc.get('location', {}).get('region_id') == region_id]
            
            return self.create_success_response(npcs)
        
        @self.app.route('/npcs/<npc_id>', methods=['GET'])
        def get_npc(npc_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            npc = self.get_fixture('npc', 'npc')
            if not npc:
                return self.create_error_response(404, "NPC not found")
            
            npc = npc.copy()
            npc['id'] = npc_id
            
            return self.create_success_response(npc)
        
        @self.app.route('/npcs/generate', methods=['POST'])
        def generate_npcs():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            if not request.is_json:
                return self.create_error_response(400, "Content-Type must be application/json")
            
            generation_request = request.get_json()
            count = generation_request.get('count', 5)
            
            # Generate NPCs based on template
            npc_template = self.get_fixture('npc', 'npc', {})
            generated_npcs = []
            
            for _ in range(min(count, 20)):  # Limit to 20 NPCs
                npc = npc_template.copy()
                npc['id'] = self.generate_id("uuid")
                npc['created_at'] = datetime.utcnow().isoformat() + "Z"
                generated_npcs.append(npc)
            
            return self.create_success_response(generated_npcs), 201
    
    def setup_quest_routes(self):
        """Setup quest system routes."""
        
        @self.app.route('/quests', methods=['GET'])
        def get_quests():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            quests = self.get_fixture('quest', 'quests_list', [])
            
            # Filter by status if specified
            status = request.args.get('status')
            if status:
                quests = [q for q in quests if q.get('quest_status') == status.upper()]
            
            return self.create_success_response(quests)
        
        @self.app.route('/quests/<quest_id>', methods=['GET'])
        def get_quest(quest_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            quest = self.get_fixture('quest', 'quest')
            if not quest:
                return self.create_error_response(404, "Quest not found")
            
            quest = quest.copy()
            quest['id'] = quest_id
            
            return self.create_success_response(quest)
        
        @self.app.route('/quests/opportunities', methods=['GET'])
        def get_quest_opportunities():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            opportunities = self.get_fixture('quest', 'quest_opportunities', [])
            return self.create_success_response(opportunities)
    
    def setup_arc_routes(self):
        """Setup arc system routes."""
        
        @self.app.route('/arcs', methods=['GET'])
        def get_arcs():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            arcs = self.get_fixture('arc', 'arcs_list', [])
            return self.create_success_response(arcs)
        
        @self.app.route('/arcs/<arc_id>', methods=['GET'])
        def get_arc(arc_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            arc = self.get_fixture('arc', 'arc')
            if not arc:
                return self.create_error_response(404, "Arc not found")
            
            arc = arc.copy()
            arc['id'] = arc_id
            
            return self.create_success_response(arc)
        
        @self.app.route('/arcs/generate', methods=['POST'])
        def generate_arc():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            if not request.is_json:
                return self.create_error_response(400, "Content-Type must be application/json")
            
            arc_template = self.get_fixture('arc', 'arc', {})
            new_arc = arc_template.copy()
            new_arc.update({
                'id': self.generate_id("uuid"),
                'created_at': datetime.utcnow().isoformat() + "Z",
                'updated_at': datetime.utcnow().isoformat() + "Z"
            })
            
            return self.create_success_response(new_arc), 201
        
        @self.app.route('/arcs/analytics', methods=['GET'])
        def get_arc_analytics():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            analytics = self.get_fixture('arc', 'arc_analytics', {})
            return self.create_success_response(analytics)
    
    def setup_magic_routes(self):
        """Setup magic system routes."""
        
        @self.app.route('/spells', methods=['GET'])
        def get_spells():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            spells = self.get_fixture('magic', 'spells_list', [])
            
            # Filter by school if specified
            school = request.args.get('school')
            if school:
                spells = [s for s in spells if s.get('school') == school.upper()]
            
            return self.create_success_response(spells)
        
        @self.app.route('/spells/<int:spell_id>', methods=['GET'])
        def get_spell(spell_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            spell = self.get_fixture('magic', 'spell')
            if not spell:
                return self.create_error_response(404, "Spell not found")
            
            spell = spell.copy()
            spell['id'] = spell_id
            
            return self.create_success_response(spell)
        
        @self.app.route('/spellbooks/<spellbook_id>', methods=['GET'])
        def get_spellbook(spellbook_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            spellbook = self.get_fixture('magic', 'spellbook')
            if not spellbook:
                return self.create_error_response(404, "Spellbook not found")
            
            spellbook = spellbook.copy()
            spellbook['id'] = spellbook_id
            
            return self.create_success_response(spellbook)
    
    def setup_equipment_routes(self):
        """Setup equipment system routes."""
        
        @self.app.route('/equipment', methods=['GET'])
        def get_equipment_list():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            equipment = self.get_fixture('equipment', 'equipment_list', [])
            
            # Filter by type if specified
            equipment_type = request.args.get('type')
            if equipment_type:
                equipment = [e for e in equipment if e.get('equipment_type') == equipment_type.upper()]
            
            return self.create_success_response(equipment)
        
        @self.app.route('/equipment/<equipment_id>', methods=['GET'])
        def get_equipment(equipment_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            equipment = self.get_fixture('equipment', 'equipment')
            if not equipment:
                return self.create_error_response(404, "Equipment not found")
            
            equipment = equipment.copy()
            equipment['id'] = equipment_id
            
            return self.create_success_response(equipment)
        
        @self.app.route('/equipment/sets/<set_id>', methods=['GET'])
        def get_equipment_set(set_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            equipment_set = self.get_fixture('equipment', 'equipment_set')
            if not equipment_set:
                return self.create_error_response(404, "Equipment set not found")
            
            equipment_set = equipment_set.copy()
            equipment_set['id'] = set_id
            
            return self.create_success_response(equipment_set)
    
    def setup_economy_routes(self):
        """Setup economy system routes."""
        
        @self.app.route('/shops/<int:shop_id>/inventory', methods=['GET'])
        def get_shop_inventory(shop_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            # Generate shop inventory from equipment
            inventory = self.get_fixture('equipment', 'equipment_list', [])[:10]  # Limit to 10 items
            
            return self.create_success_response({
                "shop_id": shop_id,
                "inventory": inventory,
                "last_restock": datetime.utcnow().isoformat() + "Z"
            })
        
        @self.app.route('/shops/<int:shop_id>/buy', methods=['POST'])
        def buy_from_shop(shop_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            if not request.is_json:
                return self.create_error_response(400, "Content-Type must be application/json")
            
            purchase_data = request.get_json()
            item_id = purchase_data.get('item_id')
            quantity = purchase_data.get('quantity', 1)
            
            if not item_id:
                return self.create_error_response(400, "item_id is required")
            
            return self.create_success_response({
                "transaction_id": self.generate_id("uuid"),
                "shop_id": shop_id,
                "item_id": item_id,
                "quantity": quantity,
                "total_cost": random.randint(10, 1000),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        
        @self.app.route('/shops/<int:shop_id>/sell', methods=['POST'])
        def sell_to_shop(shop_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            if not request.is_json:
                return self.create_error_response(400, "Content-Type must be application/json")
            
            sale_data = request.get_json()
            item_id = sale_data.get('item_id')
            quantity = sale_data.get('quantity', 1)
            
            if not item_id:
                return self.create_error_response(400, "item_id is required")
            
            return self.create_success_response({
                "transaction_id": self.generate_id("uuid"),
                "shop_id": shop_id,
                "item_id": item_id,
                "quantity": quantity,
                "total_value": random.randint(5, 500),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
    
    def setup_combat_routes(self):
        """Setup combat system routes."""
        
        @self.app.route('/combat/encounters', methods=['POST'])
        def create_combat_encounter():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            if not request.is_json:
                return self.create_error_response(400, "Content-Type must be application/json")
            
            encounter_data = request.get_json()
            
            return self.create_success_response({
                "encounter_id": self.generate_id("uuid"),
                "status": "ACTIVE",
                "participants": encounter_data.get('participants', []),
                "current_turn": 1,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }), 201
        
        @self.app.route('/combat/encounters/<encounter_id>/actions', methods=['POST'])
        def submit_combat_action(encounter_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            if not request.is_json:
                return self.create_error_response(400, "Content-Type must be application/json")
            
            action_data = request.get_json()
            
            return self.create_success_response({
                "action_id": self.generate_id("uuid"),
                "encounter_id": encounter_id,
                "action_type": action_data.get('action_type', 'ATTACK'),
                "success": random.choice([True, False]),
                "damage": random.randint(1, 20) if random.choice([True, False]) else 0,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
    
    def setup_faction_routes(self):
        """Setup faction system routes."""
        
        @self.app.route('/factions', methods=['GET'])
        def get_factions():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            # Generate faction list from available fixtures
            factions = []
            for i in range(5):  # Generate 5 factions
                faction = {
                    "id": self.generate_id("uuid"),
                    "name": f"Faction {i+1}",
                    "faction_type": random.choice(["GUILD", "KINGDOM", "CULT", "MERCENARY"]),
                    "power": random.randint(1, 100),
                    "reputation": random.randint(-50, 50),
                    "wealth": random.randint(1000, 100000),
                    "created_at": datetime.utcnow().isoformat() + "Z"
                }
                factions.append(faction)
            
            return self.create_success_response(factions)
        
        @self.app.route('/factions/<faction_id>/relationships', methods=['GET'])
        def get_faction_relationships(faction_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            relationships = []
            for i in range(3):  # Generate 3 relationships
                relationship = {
                    "target_faction_id": self.generate_id("uuid"),
                    "relationship_type": random.choice(["ALLY", "ENEMY", "NEUTRAL", "TRADE_PARTNER"]),
                    "strength": random.randint(-100, 100),
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                }
                relationships.append(relationship)
            
            return self.create_success_response(relationships)
    
    def setup_region_routes(self):
        """Setup region system routes."""
        
        @self.app.route('/regions', methods=['GET'])
        def get_regions():
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            # Generate region list
            regions = []
            for i in range(8):  # Generate 8 regions
                region = {
                    "id": self.generate_id("uuid"),
                    "name": f"Region {i+1}",
                    "region_type": random.choice(["PLAINS", "FOREST", "MOUNTAIN", "DESERT", "SWAMP"]),
                    "climate": random.choice(["TEMPERATE", "TROPICAL", "ARCTIC", "ARID"]),
                    "population": random.randint(100, 50000),
                    "coordinates": {
                        "center_q": random.randint(-20, 20),
                        "center_r": random.randint(-20, 20),
                        "size": random.randint(3, 10)
                    },
                    "created_at": datetime.utcnow().isoformat() + "Z"
                }
                regions.append(region)
            
            return self.create_success_response(regions)
        
        @self.app.route('/regions/<region_id>', methods=['GET'])
        def get_region(region_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            region = {
                "id": region_id,
                "name": f"Region {region_id[:8]}",
                "region_type": random.choice(["PLAINS", "FOREST", "MOUNTAIN", "DESERT", "SWAMP"]),
                "climate": random.choice(["TEMPERATE", "TROPICAL", "ARCTIC", "ARID"]),
                "population": random.randint(100, 50000),
                "description": "A detailed description of this region...",
                "features": [
                    {"name": "Mountain Range", "type": "NATURAL"},
                    {"name": "Ancient Ruins", "type": "CULTURAL"}
                ],
                "coordinates": {
                    "center_q": random.randint(-20, 20),
                    "center_r": random.randint(-20, 20),
                    "size": random.randint(3, 10)
                },
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            
            return self.create_success_response(region)
    
    def setup_generic_routes(self):
        """Setup generic routes for remaining systems."""
        
        @self.app.route('/<system>/<resource>', methods=['GET'])
        def get_generic_list(system, resource):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            # Check if we have fixtures for this system
            if system in self.fixtures_cache:
                # Try to find a list fixture
                list_fixture = self.get_fixture(system, f"{resource}_list")
                if list_fixture:
                    return self.create_success_response(list_fixture)
                
                # Try to find a single item fixture
                single_fixture = self.get_fixture(system, resource)
                if single_fixture:
                    return self.create_success_response([single_fixture])
            
            # Return empty list if no fixtures found
            return self.create_success_response([])
        
        @self.app.route('/<system>/<resource>/<resource_id>', methods=['GET'])
        def get_generic_item(system, resource, resource_id):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            # Check if we have fixtures for this system
            if system in self.fixtures_cache:
                # Try to find the resource fixture
                fixture = self.get_fixture(system, resource)
                if fixture:
                    item = fixture.copy()
                    item['id'] = resource_id
                    return self.create_success_response(item)
            
            return self.create_error_response(404, f"{resource.title()} not found")
        
        @self.app.route('/<system>/<resource>', methods=['POST'])
        def create_generic_item(system, resource):
            user = self.authenticate_request()
            if not user:
                return self.create_error_response(401)
            
            if not request.is_json:
                return self.create_error_response(400, "Content-Type must be application/json")
            
            request_data = request.get_json()
            
            # Get template from fixtures
            template = self.get_fixture(system, resource, {})
            new_item = template.copy()
            new_item.update({
                'id': self.generate_id("uuid"),
                'created_at': datetime.utcnow().isoformat() + "Z",
                'updated_at': datetime.utcnow().isoformat() + "Z",
                **request_data
            })
            
            return self.create_success_response(new_item), 201
    
    def run(self, host: str = "localhost", port: int = 3001, debug: bool = False):
        """Run the mock server."""
        print(f"🚀 Starting Visual DM Mock Server...")
        print(f"📍 Server URL: http://{host}:{port}")
        print(f"🏥 Health check: http://{host}:{port}/health")
        print(f"🔑 Valid tokens: {list(self.valid_tokens.keys())}")
        print(f"📚 Systems available: {len(self.fixtures_cache)}")
        print()
        print("Example requests:")
        print(f"  curl -H 'Authorization: Bearer dev_token_123' http://{host}:{port}/characters")
        print(f"  curl -H 'Authorization: Bearer dev_token_123' http://{host}:{port}/health")
        print()
        
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Visual DM Mock Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=3001, help='Port to bind to (default: 3001)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--fixtures-dir', default='.', help='Directory containing fixtures (default: current)')
    
    args = parser.parse_args()
    
    # Create and run server
    server = MockServer(fixtures_dir=args.fixtures_dir)
    server.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main() 