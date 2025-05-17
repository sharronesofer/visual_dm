"""
World-related API routes.
Provides endpoints for world management and interaction.
"""

from flask import Blueprint, jsonify, request, url_for, current_app
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
from app.core.models.world_state import WorldState
from app.core.models.world_event import WorldEvent
from app.core.models.npc import NPC
from app.core.models.world import Faction
from app.core.models.point_of_interest import PointOfInterest
from app.core.models.location import Location
from app.core.utils.error_utils import ValidationError, DatabaseError, NotFoundError
from app.core.utils.pagination import Paginator
from app.world.world_tick_utils import process_world_tick
from datetime import datetime, timedelta
import random
from fastapi import APIRouter, HTTPException
from visual_client.game.world import WorldState
from app.core.utils.cache import cached
from app.core.utils.http_cache import cache_control, etag, last_modified

world_bp = Blueprint('world', __name__)

# Cache timeouts
LIST_CACHE_TIMEOUT = timedelta(minutes=10)
DETAIL_CACHE_TIMEOUT = timedelta(minutes=15)

# === Region Routes ===
@world_bp.route('/regions', methods=['GET'])
@cached(timeout=LIST_CACHE_TIMEOUT, key_prefix='regions')
@cache_control(max_age=600)  # 10 minutes
@etag
def get_regions():
    """Get paginated list of regions."""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 25)), 100)
        
        query = Region.query.options(
            joinedload(Region.locations),
            joinedload(Region.characters)
        )
        
        paginator = Paginator(query, page, per_page)
        result = paginator.get_paginated_response()
        
        return jsonify(result)
    except ValueError as e:
        raise ValidationError(f"Invalid pagination parameters: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Error fetching regions: {str(e)}")

@world_bp.route('/regions', methods=['POST'])
def create_region():
    """Create a new region."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        
        region = Region(**data)
        db.session.add(region)
        db.session.commit()
        
        # Invalidate list cache
        cache = current_app.extensions.get('cache')
        if cache:
            cache.delete_pattern('regions:*')
        
        return jsonify(region.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error creating region: {str(e)}")

@world_bp.route('/regions/<int:region_id>', methods=['GET'])
@cached(timeout=DETAIL_CACHE_TIMEOUT, key_prefix='region_detail')
@cache_control(max_age=900)  # 15 minutes
@etag
@last_modified
def get_region(region_id: int):
    """Get a specific region by ID."""
    try:
        region = Region.query.options(
            joinedload(Region.locations),
            joinedload(Region.characters)
        ).filter_by(id=region_id).first()
        
        if not region:
            raise NotFoundError(f"Region {region_id} not found")
        
        return jsonify(region.to_dict())
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Error fetching region {region_id}: {str(e)}")

@world_bp.route('/regions/<int:region_id>', methods=['PUT'])
def update_region(region_id: int):
    """Update a specific region."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        
        region = Region.query.get(region_id)
        if not region:
            raise NotFoundError(f"Region {region_id} not found")
        
        for key, value in data.items():
            setattr(region, key, value)
        
        db.session.commit()
        
        # Invalidate both list and detail caches
        cache = current_app.extensions.get('cache')
        if cache:
            cache.delete_pattern('regions:*')
            cache.delete_pattern(f'region_detail:{region_id}:*')
        
        return jsonify(region.to_dict())
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error updating region {region_id}: {str(e)}")

@world_bp.route('/regions/<int:region_id>', methods=['DELETE'])
def delete_region(region_id: int):
    """Delete a specific region."""
    try:
        region = Region.query.get(region_id)
        if not region:
            raise NotFoundError(f"Region {region_id} not found")
        
        db.session.delete(region)
        db.session.commit()
        
        # Invalidate both list and detail caches
        cache = current_app.extensions.get('cache')
        if cache:
            cache.delete_pattern('regions:*')
            cache.delete_pattern(f'region_detail:{region_id}:*')
        
        return '', 204
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting region {region_id}: {str(e)}")

# === Location Routes ===
@world_bp.route('/locations', methods=['GET'])
@cached(timeout=LIST_CACHE_TIMEOUT, key_prefix='locations')
@cache_control(max_age=600)  # 10 minutes
@etag
def get_locations():
    """Get paginated list of locations."""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 25)), 100)
        
        query = Location.query.options(
            joinedload(Location.region),
            joinedload(Location.characters)
        )
        
        paginator = Paginator(query, page, per_page)
        result = paginator.get_paginated_response()
        
        return jsonify(result)
    except ValueError as e:
        raise ValidationError(f"Invalid pagination parameters: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Error fetching locations: {str(e)}")

@world_bp.route('/locations', methods=['POST'])
def create_location():
    """Create a new location."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        
        location = Location(**data)
        db.session.add(location)
        db.session.commit()
        
        # Invalidate list cache
        cache = current_app.extensions.get('cache')
        if cache:
            cache.delete_pattern('locations:*')
        
        return jsonify(location.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error creating location: {str(e)}")

@world_bp.route('/locations/<int:location_id>', methods=['GET'])
@cached(timeout=DETAIL_CACHE_TIMEOUT, key_prefix='location_detail')
@cache_control(max_age=900)  # 15 minutes
@etag
@last_modified
def get_location(location_id: int):
    """Get a specific location by ID."""
    try:
        location = Location.query.options(
            joinedload(Location.region),
            joinedload(Location.characters)
        ).filter_by(id=location_id).first()
        
        if not location:
            raise NotFoundError(f"Location {location_id} not found")
        
        return jsonify(location.to_dict())
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Error fetching location {location_id}: {str(e)}")

@world_bp.route('/locations/<int:location_id>', methods=['PUT'])
def update_location(location_id: int):
    """Update a specific location."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        
        location = Location.query.get(location_id)
        if not location:
            raise NotFoundError(f"Location {location_id} not found")
        
        for key, value in data.items():
            setattr(location, key, value)
        
        db.session.commit()
        
        # Invalidate both list and detail caches
        cache = current_app.extensions.get('cache')
        if cache:
            cache.delete_pattern('locations:*')
            cache.delete_pattern(f'location_detail:{location_id}:*')
        
        return jsonify(location.to_dict())
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error updating location {location_id}: {str(e)}")

@world_bp.route('/locations/<int:location_id>', methods=['DELETE'])
def delete_location(location_id: int):
    """Delete a specific location."""
    try:
        location = Location.query.get(location_id)
        if not location:
            raise NotFoundError(f"Location {location_id} not found")
        
        db.session.delete(location)
        db.session.commit()
        
        # Invalidate both list and detail caches
        cache = current_app.extensions.get('cache')
        if cache:
            cache.delete_pattern('locations:*')
            cache.delete_pattern(f'location_detail:{location_id}:*')
        
        return '', 204
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting location {location_id}: {str(e)}")

# === Point of Interest Routes ===
@world_bp.route('/pois', methods=['GET'])
def get_pois():
    """Get all points of interest."""
    query = db.session.query(PointOfInterest)\
        .options(
            joinedload(PointOfInterest.region),
            joinedload(PointOfInterest.location)
        )
    
    # Apply filters if provided
    if request.args.get('region_id'):
        query = query.filter(PointOfInterest.region_id == request.args.get('region_id'))
    if request.args.get('location_id'):
        query = query.filter(PointOfInterest.location_id == request.args.get('location_id'))
    if request.args.get('type'):
        query = query.filter(PointOfInterest.type == request.args.get('type'))
    
    # Get paginated response
    paginated_response = Paginator.paginate(
        query=query,
        endpoint='world.get_pois'
    )
    
    # Convert items to dict format
    paginated_response.items = [poi.to_dict() for poi in paginated_response.items]
    
    return jsonify(paginated_response.to_dict()), 200

@world_bp.route('/pois', methods=['POST'])
def create_poi():
    """Create a new point of interest."""
    data = request.get_json()
    poi = PointOfInterest(
        name=data['name'],
        description=data.get('description'),
        type=data.get('type'),
        coordinates=data.get('coordinates'),
        region_id=data.get('region_id'),
        location_id=data.get('location_id')
    )
    db.session.add(poi)
    db.session.commit()
    return jsonify(poi.to_dict()), 201

@world_bp.route('/pois/<int:poi_id>', methods=['GET'])
def get_poi(poi_id):
    """Get a specific point of interest."""
    poi = db.session.query(PointOfInterest).get_or_404(poi_id)
    return jsonify(poi.to_dict()), 200

@world_bp.route('/pois/<int:poi_id>', methods=['PUT'])
def update_poi(poi_id):
    """Update a point of interest."""
    poi = db.session.query(PointOfInterest).get_or_404(poi_id)
    data = request.get_json()
    
    for key, value in data.items():
        if hasattr(poi, key):
            setattr(poi, key, value)
    
    db.session.commit()
    return jsonify(poi.to_dict()), 200

@world_bp.route('/pois/<int:poi_id>', methods=['DELETE'])
def delete_poi(poi_id):
    """Delete a point of interest."""
    poi = db.session.query(PointOfInterest).get_or_404(poi_id)
    db.session.delete(poi)
    db.session.commit()
    return '', 204

@world_bp.route('/regions/<int:region_id>/locations', methods=['GET'])
def get_region_locations(region_id):
    """Get all locations in a region."""
    locations = Location.query.filter_by(region_id=region_id).all()
    return jsonify([location.to_dict() for location in locations]) 