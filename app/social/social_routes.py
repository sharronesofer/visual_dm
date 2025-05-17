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
from app.core.models.world import Region
from app.core.models.quest import Quest
from app.core.models.spell import Spell
from app.core.models.inventory import InventoryItem
from app.core.models.combat import CombatStats
from app.core.models.save import SaveGame
from app.core.utils.error_utils import ValidationError, DatabaseError, NotFoundError
from app.core.utils.pagination import Paginator
from datetime import datetime, timedelta
import random
from flask import current_app
from app.core.utils.cache import cached
from app.core.utils.http_cache import cache_control, etag, last_modified
from app.core.services.faction_service import FactionRelationshipService

social_bp = Blueprint('social', __name__)

# Cache timeouts
LIST_CACHE_TIMEOUT = timedelta(minutes=5)
DETAIL_CACHE_TIMEOUT = timedelta(minutes=10)

@social_bp.route('/interact', methods=['POST'])
def interact():
    """Process a social interaction between characters."""
    try:
        data = request.get_json()
        interaction = Interaction(**data)
        result = process_social_interaction(interaction)
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/relationships', methods=['GET'])
def get_relationships():
    """Get paginated list of relationships between any two entities."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        entity_id = request.args.get('entity_id', type=int)
        entity_type = request.args.get('entity_type', type=str)
        include_incoming = request.args.get('include_incoming', 'false').lower() == 'true'
        relationship_type = request.args.get('relationship_type')
        min_value = request.args.get('min_value', type=int)
        query = FactionRelationshipService.get_entity_relationships(
            entity_id=entity_id,
            entity_type=entity_type,
            relationship_type=relationship_type,
            min_value=min_value,
            include_incoming=include_incoming
        )
        # Paginate manually
        total = len(query)
        start = (page - 1) * per_page
        end = start + per_page
        results = [rel.to_dict() for rel in query[start:end]]
        return jsonify({
            'results': results,
            'total': total,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
def get_interactions():
    """Get paginated list of interactions between any two entities."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        entity1_id = request.args.get('entity1_id', type=int)
        entity1_type = request.args.get('entity1_type', type=str)
        entity2_id = request.args.get('entity2_id', type=int)
        entity2_type = request.args.get('entity2_type', type=str)
        from app.social.models.social import Interaction
        query = Interaction.query
        if entity1_id and entity1_type:
            query = query.filter_by(entity1_id=entity1_id, entity1_type=entity1_type)
        if entity2_id and entity2_type:
            query = query.filter_by(entity2_id=entity2_id, entity2_type=entity2_type)
        total = query.count()
        results = [i.to_dict() for i in query.offset((page-1)*per_page).limit(per_page)]
        return jsonify({
            'results': results,
            'total': total,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/interactions/<int:interaction_id>', methods=['GET'])
@cached(timeout=DETAIL_CACHE_TIMEOUT, key_prefix='interaction_detail')
@cache_control(max_age=600)  # 10 minutes
@etag
@last_modified
def get_interaction(interaction_id: int):
    """Get detailed interaction information."""
    try:
        interaction = Interaction.query.options(
            joinedload(Interaction.relationship),
            joinedload(Interaction.initiator),
            joinedload(Interaction.target)
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
    """Create a new relationship between any two entities."""
    try:
        data = request.get_json()
        required_fields = ['entity1_id', 'entity1_type', 'entity2_id', 'entity2_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        rel = FactionRelationshipService.set_relationship(
            entity1_id=data['entity1_id'],
            entity1_type=data['entity1_type'],
            entity2_id=data['entity2_id'],
            entity2_type=data['entity2_type'],
            relationship_type=data.get('relationship_type'),
            relationship_value=data.get('relationship_value', 0),
            metadata=data.get('metadata', {})
        )
        return jsonify(rel.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/interactions', methods=['POST'])
def create_interaction():
    """Create a new interaction between any two entities."""
    try:
        data = request.get_json()
        required_fields = ['entity1_id', 'entity1_type', 'entity2_id', 'entity2_type', 'interaction_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        from app.social.models.social import Interaction, EntityType
        interaction = Interaction(
            entity1_id=data['entity1_id'],
            entity1_type=EntityType(data['entity1_type']),
            entity2_id=data['entity2_id'],
            entity2_type=EntityType(data['entity2_type']),
            interaction_type=data['interaction_type'],
            outcome=data.get('outcome'),
            impact=data.get('impact')
        )
        db.session.add(interaction)
        db.session.commit()
        return jsonify(interaction.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/relationships/<int:relationship_id>', methods=['PUT'])
def update_relationship(relationship_id: int):
    """Update relationship information by ID."""
    try:
        relationship = CharacterRelationship.query.get(relationship_id)
        if not relationship:
            raise NotFoundError(f"Relationship {relationship_id} not found")
            
        data = request.get_json()
        
        # Update fields
        for field in ['relationship_type', 'relationship_value', 'metadata']:
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
    """Update interaction information by ID."""
    try:
        interaction = Interaction.query.get(interaction_id)
        if not interaction:
            raise NotFoundError(f"Interaction {interaction_id} not found")
            
        data = request.get_json()
        
        # Update fields
        for field in ['interaction_type', 'outcome', 'impact']:
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
    """Delete a relationship by ID."""
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
    """Delete an interaction by ID."""
    try:
        interaction = Interaction.query.get(interaction_id)
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