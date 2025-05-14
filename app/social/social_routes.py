"""
Social interaction and relationship management routes.
"""

from flask import Blueprint, jsonify, request, url_for
from typing import Dict, Any, List, Optional
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from app.core.database import db
from app.core.models.character import Character
from app.core.models.user import User
from app.core.models.party import Party
from app.core.models.region import Region
from app.core.models.quest import Quest
from app.core.models.spell import Spell
from app.core.models.inventory import InventoryItem
from app.core.models.combat import CombatStats
from app.core.models.save import SaveGame
from app.core.models.social import SocialInteraction, CharacterRelationship
from app.core.utils.error_utils import ValidationError, DatabaseError, NotFoundError
from app.core.utils.pagination import Paginator
from app.social.social_utils import (
    process_social_interaction,
    update_relationship,
    get_relationship_status
)
from datetime import datetime, timedelta
import random
from flask import current_app
from app.core.utils.cache import cached
from app.core.utils.http_cache import cache_control, etag, last_modified

social_bp = Blueprint('social', __name__)

# Cache timeouts
LIST_CACHE_TIMEOUT = timedelta(minutes=5)
DETAIL_CACHE_TIMEOUT = timedelta(minutes=10)

@social_bp.route('/interact', methods=['POST'])
def interact():
    """Process a social interaction between characters."""
    try:
        data = request.get_json()
        interaction = SocialInteraction(**data)
        result = process_social_interaction(interaction)
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/relationships', methods=['GET'])
@cached(timeout=LIST_CACHE_TIMEOUT, key_prefix='relationships')
@cache_control(max_age=300)  # 5 minutes
@etag
def get_relationships():
    """Get paginated list of character relationships."""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        
        # Create query with eager loading
        query = CharacterRelationship.query.options(
            joinedload(CharacterRelationship.character),
            joinedload(CharacterRelationship.related_character)
        )
        
        # Apply filters if provided
        if 'character_id' in request.args:
            query = query.filter(CharacterRelationship.character_id == request.args.get('character_id', type=int))
        if 'type' in request.args:
            query = query.filter(CharacterRelationship.type == request.args.get('type'))
        
        # Create paginator and return response
        paginator = Paginator(query, page, per_page)
        return jsonify(paginator.get_response())
        
    except Exception as e:
        raise DatabaseError(f"Error fetching relationships: {str(e)}")

@social_bp.route('/relationships/<int:relationship_id>', methods=['GET'])
@cached(timeout=DETAIL_CACHE_TIMEOUT, key_prefix='relationship_detail')
@cache_control(max_age=600)  # 10 minutes
@etag
@last_modified
def get_relationship(relationship_id: int):
    """Get detailed relationship information."""
    try:
        relationship = CharacterRelationship.query.options(
            joinedload(CharacterRelationship.character),
            joinedload(CharacterRelationship.related_character),
            joinedload(CharacterRelationship.interactions)
        ).get(relationship_id)
        
        if not relationship:
            raise NotFoundError(f"Relationship {relationship_id} not found")
            
        return jsonify(relationship.to_dict())
        
    except NotFoundError as e:
        raise e
    except Exception as e:
        raise DatabaseError(f"Error fetching relationship {relationship_id}: {str(e)}")

@social_bp.route('/interactions', methods=['GET'])
@cached(timeout=LIST_CACHE_TIMEOUT, key_prefix='interactions')
@cache_control(max_age=300)  # 5 minutes
@etag
def get_interactions():
    """Get paginated list of social interactions."""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        
        # Create query with eager loading
        query = SocialInteraction.query.options(
            joinedload(SocialInteraction.relationship),
            joinedload(SocialInteraction.initiator),
            joinedload(SocialInteraction.target)
        )
        
        # Apply filters if provided
        if 'character_id' in request.args:
            char_id = request.args.get('character_id', type=int)
            query = query.filter(
                (SocialInteraction.initiator_id == char_id) |
                (SocialInteraction.target_id == char_id)
            )
        if 'type' in request.args:
            query = query.filter(SocialInteraction.type == request.args.get('type'))
        
        # Create paginator and return response
        paginator = Paginator(query, page, per_page)
        return jsonify(paginator.get_response())
        
    except Exception as e:
        raise DatabaseError(f"Error fetching interactions: {str(e)}")

@social_bp.route('/interactions/<int:interaction_id>', methods=['GET'])
@cached(timeout=DETAIL_CACHE_TIMEOUT, key_prefix='interaction_detail')
@cache_control(max_age=600)  # 10 minutes
@etag
@last_modified
def get_interaction(interaction_id: int):
    """Get detailed interaction information."""
    try:
        interaction = SocialInteraction.query.options(
            joinedload(SocialInteraction.relationship),
            joinedload(SocialInteraction.initiator),
            joinedload(SocialInteraction.target)
        ).get(interaction_id)
        
        if not interaction:
            raise NotFoundError(f"Interaction {interaction_id} not found")
            
        return jsonify(interaction.to_dict())
        
    except NotFoundError as e:
        raise e
    except Exception as e:
        raise DatabaseError(f"Error fetching interaction {interaction_id}: {str(e)}")

@social_bp.route('/relationships', methods=['POST'])
def create_relationship():
    """Create a new character relationship."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['character_id', 'related_character_id', 'type']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Create relationship
        relationship = CharacterRelationship(
            character_id=data['character_id'],
            related_character_id=data['related_character_id'],
            type=data['type'],
            status=data.get('status', 'active')
        )
        
        db.session.add(relationship)
        db.session.commit()
        
        # Clear relationship list cache when new relationship is added
        cache = current_app.extensions.get('redis_cache')
        if cache:
            cache.clear_pattern('cache:relationships:*')
        
        return jsonify(relationship.to_dict()), 201
        
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error creating relationship: {str(e)}")

@social_bp.route('/interactions', methods=['POST'])
def create_interaction():
    """Create a new social interaction."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['initiator_id', 'target_id', 'type', 'relationship_id']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Create interaction
        interaction = SocialInteraction(
            initiator_id=data['initiator_id'],
            target_id=data['target_id'],
            type=data['type'],
            relationship_id=data['relationship_id'],
            details=data.get('details', {})
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        # Clear interaction list cache and relationship detail cache
        cache = current_app.extensions.get('redis_cache')
        if cache:
            cache.clear_pattern('cache:interactions:*')
            cache.clear_pattern(f'cache:relationship_detail:*{interaction.relationship_id}*')
        
        return jsonify(interaction.to_dict()), 201
        
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error creating interaction: {str(e)}")

@social_bp.route('/relationships/<int:relationship_id>', methods=['PUT'])
def update_relationship(relationship_id: int):
    """Update relationship information."""
    try:
        relationship = CharacterRelationship.query.get(relationship_id)
        if not relationship:
            raise NotFoundError(f"Relationship {relationship_id} not found")
            
        data = request.get_json()
        
        # Update fields
        for field in ['type', 'status']:
            if field in data:
                setattr(relationship, field, data[field])
        
        db.session.commit()
        
        # Clear both list and detail cache for this relationship
        cache = current_app.extensions.get('redis_cache')
        if cache:
            cache.clear_pattern('cache:relationships:*')
            cache.clear_pattern(f'cache:relationship_detail:*{relationship_id}*')
        
        return jsonify(relationship.to_dict())
        
    except NotFoundError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error updating relationship {relationship_id}: {str(e)}")

@social_bp.route('/interactions/<int:interaction_id>', methods=['PUT'])
def update_interaction(interaction_id: int):
    """Update interaction information."""
    try:
        interaction = SocialInteraction.query.get(interaction_id)
        if not interaction:
            raise NotFoundError(f"Interaction {interaction_id} not found")
            
        data = request.get_json()
        
        # Update fields
        for field in ['type', 'details']:
            if field in data:
                setattr(interaction, field, data[field])
        
        db.session.commit()
        
        # Clear both list and detail cache for this interaction
        cache = current_app.extensions.get('redis_cache')
        if cache:
            cache.clear_pattern('cache:interactions:*')
            cache.clear_pattern(f'cache:interaction_detail:*{interaction_id}*')
            cache.clear_pattern(f'cache:relationship_detail:*{interaction.relationship_id}*')
        
        return jsonify(interaction.to_dict())
        
    except NotFoundError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error updating interaction {interaction_id}: {str(e)}")

@social_bp.route('/relationships/<int:relationship_id>', methods=['DELETE'])
def delete_relationship(relationship_id: int):
    """Delete a relationship."""
    try:
        relationship = CharacterRelationship.query.get(relationship_id)
        if not relationship:
            raise NotFoundError(f"Relationship {relationship_id} not found")
            
        db.session.delete(relationship)
        db.session.commit()
        
        # Clear both list and detail cache for this relationship
        cache = current_app.extensions.get('redis_cache')
        if cache:
            cache.clear_pattern('cache:relationships:*')
            cache.clear_pattern(f'cache:relationship_detail:*{relationship_id}*')
            # Also clear interaction cache since related interactions are deleted
            cache.clear_pattern('cache:interactions:*')
        
        return '', 204
        
    except NotFoundError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting relationship {relationship_id}: {str(e)}")

@social_bp.route('/interactions/<int:interaction_id>', methods=['DELETE'])
def delete_interaction(interaction_id: int):
    """Delete an interaction."""
    try:
        interaction = SocialInteraction.query.get(interaction_id)
        if not interaction:
            raise NotFoundError(f"Interaction {interaction_id} not found")
            
        relationship_id = interaction.relationship_id
        db.session.delete(interaction)
        db.session.commit()
        
        # Clear relevant caches
        cache = current_app.extensions.get('redis_cache')
        if cache:
            cache.clear_pattern('cache:interactions:*')
            cache.clear_pattern(f'cache:interaction_detail:*{interaction_id}*')
            cache.clear_pattern(f'cache:relationship_detail:*{relationship_id}*')
        
        return '', 204
        
    except NotFoundError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting interaction {interaction_id}: {str(e)}") 