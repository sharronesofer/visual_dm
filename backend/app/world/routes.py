from flask import Blueprint, jsonify, request
from typing import Dict, List
from .world import World, Region, Faction, Quest

world_bp = Blueprint('world', __name__)
world = World()

@world_bp.route('/regions', methods=['GET'])
def get_regions():
    return jsonify(world.get_world_data()['regions'])

@world_bp.route('/regions', methods=['POST'])
def create_region():
    data = request.get_json()
    region = world.add_region(data)
    return jsonify(vars(region)), 201

@world_bp.route('/regions/<region_id>', methods=['GET'])
def get_region(region_id: str):
    region = world.get_region(region_id)
    if region:
        return jsonify(vars(region))
    return jsonify({'error': 'Region not found'}), 404

@world_bp.route('/factions', methods=['GET'])
def get_factions():
    return jsonify(world.get_world_data()['factions'])

@world_bp.route('/factions', methods=['POST'])
def create_faction():
    data = request.get_json()
    faction = world.add_faction(data)
    return jsonify(vars(faction)), 201

@world_bp.route('/factions/<faction_id>', methods=['GET'])
def get_faction(faction_id: str):
    faction = world.get_faction(faction_id)
    if faction:
        return jsonify(vars(faction))
    return jsonify({'error': 'Faction not found'}), 404

@world_bp.route('/quests', methods=['GET'])
def get_quests():
    return jsonify(world.get_world_data()['quests'])

@world_bp.route('/quests', methods=['POST'])
def create_quest():
    data = request.get_json()
    quest = world.add_quest(data)
    return jsonify(vars(quest)), 201

@world_bp.route('/quests/<quest_id>', methods=['GET'])
def get_quest(quest_id: str):
    quest = world.get_quest(quest_id)
    if quest:
        return jsonify(vars(quest))
    return jsonify({'error': 'Quest not found'}), 404 