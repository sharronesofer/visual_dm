"""
Character-related API routes.
Provides endpoints for character management and interaction.
"""

from flask import Blueprint, jsonify, request, url_for, current_app, abort
from typing import Dict, Any, List, Optional
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from app.core.database import db
from app.core.models.character import Character
from app.core.utils.error_utils import ValidationError, DatabaseError, NotFoundError
from app.core.utils.pagination import Paginator
from app.characters.character_builder_class import CharacterBuilder
from app.core.utils.json_utils import load_json
import os
from app.core.utils.cache import cached
from app.core.utils.http_cache import cache_control, etag, last_modified
from datetime import timedelta

character_bp = Blueprint('characters', __name__)

# Get the absolute paths to the JSON files
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'rules')
FEATS_DATA = load_json(os.path.join(DATA_DIR, 'feats.json'))
SKILLS_DATA = load_json(os.path.join(DATA_DIR, 'skills.json'))

# Extract skills list
SKILLS_LIST = [skill["name"] for skill in SKILLS_DATA.get("skills", [])]

# Cache timeouts
LIST_CACHE_TIMEOUT = timedelta(minutes=5)
DETAIL_CACHE_TIMEOUT = timedelta(minutes=10)

# === Character Routes ===
@character_bp.route('/', methods=['GET'])
@cached(timeout=LIST_CACHE_TIMEOUT, key_prefix='characters')
@cache_control(max_age=300)  # 5 minutes
@etag
def get_characters():
    """Get paginated list of characters."""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 25)), 100)
        
        query = Character.query.options(
            joinedload(Character.party),
            joinedload(Character.region),
            joinedload(Character.inventory_items),
            joinedload(Character.relationships)
        )
        
        paginator = Paginator(query, page, per_page)
        result = paginator.get_paginated_response()
        
        return jsonify(result)
    except ValueError as e:
        raise ValidationError(f"Invalid pagination parameters: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Error fetching characters: {str(e)}")

@character_bp.route('/', methods=['POST'])
def create_character():
    """Create a new character."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        
        character = Character(**data)
        db.session.add(character)
        db.session.commit()
        
        # Invalidate list cache
        cache = current_app.extensions.get('cache')
        if cache:
            cache.delete_pattern('characters:*')
        
        return jsonify(character.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error creating character: {str(e)}")

@character_bp.route('/<int:character_id>', methods=['GET'])
@cached(timeout=DETAIL_CACHE_TIMEOUT, key_prefix='character_detail')
@cache_control(max_age=600)  # 10 minutes
@etag
@last_modified
def get_character(character_id: int):
    """Get a specific character by ID."""
    try:
        character = Character.query.options(
            joinedload(Character.party),
            joinedload(Character.region),
            joinedload(Character.inventory_items),
            joinedload(Character.relationships)
        ).filter_by(id=character_id).first()
        
        if not character:
            raise NotFoundError(f"Character {character_id} not found")
        
        return jsonify(character.to_dict())
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Error fetching character {character_id}: {str(e)}")

@character_bp.route('/<int:character_id>', methods=['PUT'])
def update_character(character_id: int):
    """Update a specific character."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        
        character = Character.query.get(character_id)
        if not character:
            raise NotFoundError(f"Character {character_id} not found")
        
        for key, value in data.items():
            setattr(character, key, value)
        
        db.session.commit()
        
        # Invalidate both list and detail caches
        cache = current_app.extensions.get('cache')
        if cache:
            cache.delete_pattern('characters:*')
            cache.delete_pattern(f'character_detail:{character_id}:*')
        
        return jsonify(character.to_dict())
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error updating character {character_id}: {str(e)}")

@character_bp.route('/<int:character_id>', methods=['DELETE'])
def delete_character(character_id: int):
    """Delete a specific character."""
    try:
        character = Character.query.get(character_id)
        if not character:
            raise NotFoundError(f"Character {character_id} not found")
        
        db.session.delete(character)
        db.session.commit()
        
        # Invalidate both list and detail caches
        cache = current_app.extensions.get('cache')
        if cache:
            cache.delete_pattern('characters:*')
            cache.delete_pattern(f'character_detail:{character_id}:*')
        
        return '', 204
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting character {character_id}: {str(e)}")

# === Character Stats Routes ===
@character_bp.route('/<int:character_id>/stats', methods=['GET'])
def get_character_stats(character_id):
    """Get a character's stats."""
    character = db.session.query(Character).get_or_404(character_id)
    return jsonify(character.get_stats()), 200

@character_bp.route('/<int:character_id>/stats', methods=['PUT'])
def update_character_stats(character_id):
    """Update a character's stats."""
    character = db.session.query(Character).get_or_404(character_id)
    data = request.get_json()
    character.update_stats(data)
    db.session.commit()
    return jsonify(character.get_stats()), 200

# === Character Equipment Routes ===
@character_bp.route('/<int:character_id>/equipment', methods=['GET'])
def get_character_equipment(character_id):
    """Get a character's equipment."""
    character = db.session.query(Character).get_or_404(character_id)
    return jsonify(character.get_equipment()), 200

@character_bp.route('/<int:character_id>/equipment', methods=['PUT'])
def update_character_equipment(character_id):
    """Update a character's equipment."""
    character = db.session.query(Character).get_or_404(character_id)
    data = request.get_json()
    character.update_equipment(data)
    db.session.commit()
    return jsonify(character.get_equipment()), 200

@character_bp.route('/api/character-builder/initialize', methods=['POST'])
def initialize_character_builder():
    """Initialize a new character builder instance."""
    try:
        builder = CharacterBuilder(FEATS_DATA, SKILLS_LIST)
        return jsonify({"message": "Character builder initialized successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@character_bp.route('/api/character-builder/name', methods=['POST'])
def set_character_name():
    """Set the character's name."""
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({"error": "Name is required"}), 400

        builder = CharacterBuilder(FEATS_DATA, SKILLS_LIST)
        builder.character_name = name
        return jsonify({"message": "Character name set successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@character_bp.route('/api/character-builder/attribute', methods=['POST'])
def set_attribute():
    """Set a character attribute."""
    try:
        data = request.get_json()
        attribute = data.get('attribute')
        value = data.get('value')
        
        if not attribute or value is None:
            return jsonify({"error": "Attribute and value are required"}), 400

        builder = CharacterBuilder(FEATS_DATA, SKILLS_LIST)
        builder.assign_attribute(attribute, value)
        return jsonify({"message": "Attribute set successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@character_bp.route('/api/character-builder/skill', methods=['POST'])
def assign_skill():
    """Assign a skill to the character."""
    try:
        data = request.get_json()
        skill = data.get('skill')
        
        if not skill:
            return jsonify({"error": "Skill is required"}), 400

        builder = CharacterBuilder(FEATS_DATA, SKILLS_LIST)
        builder.assign_skill(skill)
        return jsonify({"message": "Skill assigned successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@character_bp.route('/api/character-builder/starter-kits', methods=['GET'])
def get_starter_kits():
    """Get all available starter kits."""
    try:
        query = db.session.query(StarterKit)
        
        # Get paginated response
        paginated_response = Paginator.paginate(
            query=query,
            endpoint='characters.get_starter_kits'
        )
        
        # Convert items to dict format
        paginated_response.items = [kit.to_dict() for kit in paginated_response.items]
        
        return jsonify(paginated_response.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@character_bp.route('/api/character-builder/starter-kit', methods=['POST'])
def set_starter_kit():
    """Set the character's starter kit."""
    try:
        data = request.get_json()
        kit_name = data.get('kitName')
        
        if not kit_name:
            return jsonify({"error": "Kit name is required"}), 400

        builder = CharacterBuilder(FEATS_DATA, SKILLS_LIST)
        builder.apply_starter_kit(kit_name)
        
        return jsonify({
            "message": "Starter kit applied successfully",
            "equipment": builder.starter_kit.get("equipment", []),
            "gold": builder.gold
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@character_bp.route('/api/character-builder/validate', methods=['GET'])
def validate_character():
    """Validate the character build."""
    try:
        builder = CharacterBuilder(FEATS_DATA, SKILLS_LIST)
        is_valid = builder.is_valid()
        return jsonify({"isValid": is_valid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@character_bp.route('/api/character-builder/finalize', methods=['POST'])
def finalize_character():
    """Finalize the character build."""
    try:
        builder = CharacterBuilder(FEATS_DATA, SKILLS_LIST)
        character_data = builder.finalize()
        return jsonify(character_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


