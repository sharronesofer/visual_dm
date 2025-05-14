"""
API endpoints for managing NPC versions.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from typing import Dict, Any, List

from app.core.models.npc import NPC
from app.core.models.npc_version import NPCVersion
from app.core.services.npc_version_service import NPCVersionService
from app.api.schemas.npc_version import NPCVersionSchema, NPCVersionComparisonSchema, NPCVersionHistorySchema
from app.core.database import db
from app.api.utils.error_handlers import handle_validation_error

bp = Blueprint('npc_version', __name__)
version_schema = NPCVersionSchema()
versions_schema = NPCVersionSchema(many=True)
comparison_schema = NPCVersionComparisonSchema(many=True)
history_schema = NPCVersionHistorySchema(many=True)

@bp.route('/npcs/<int:npc_id>/versions', methods=['GET'])
@jwt_required()
def get_npc_versions(npc_id: int):
    """Get version history for an NPC."""
    npc = NPC.query.get_or_404(npc_id)
    versions = NPCVersion.query.filter_by(npc_id=npc_id).order_by(NPCVersion.version_number.desc()).all()
    return jsonify(versions_schema.dump(versions))

@bp.route('/npcs/<int:npc_id>/versions/<int:version_number>', methods=['GET'])
@jwt_required()
def get_npc_version(npc_id: int, version_number: int):
    """Get a specific version of an NPC."""
    version = NPCVersion.query.filter_by(
        npc_id=npc_id, 
        version_number=version_number
    ).first_or_404()
    return jsonify(version_schema.dump(version))

@bp.route('/npcs/<int:npc_id>/versions/compare', methods=['GET'])
@jwt_required()
def compare_versions(npc_id: int):
    """Compare two versions of an NPC."""
    version1_num = request.args.get('version1', type=int)
    version2_num = request.args.get('version2', type=int)
    
    if not version1_num or not version2_num:
        return jsonify({'error': 'Both version numbers are required'}), 400
        
    version1 = NPCVersion.query.filter_by(
        npc_id=npc_id, 
        version_number=version1_num
    ).first_or_404()
    
    version2 = NPCVersion.query.filter_by(
        npc_id=npc_id, 
        version_number=version2_num
    ).first_or_404()
    
    differences = NPCVersionService.compare_versions(version1, version2)
    return jsonify(comparison_schema.dump(differences))

@bp.route('/npcs/<int:npc_id>/versions/revert', methods=['POST'])
@jwt_required()
def revert_to_version(npc_id: int):
    """Revert an NPC to a specific version."""
    version_number = request.json.get('version_number')
    if not version_number:
        return jsonify({'error': 'Version number is required'}), 400
        
    try:
        npc = NPC.query.get_or_404(npc_id)
        version = NPCVersion.query.filter_by(
            npc_id=npc_id,
            version_number=version_number
        ).first_or_404()
        
        NPCVersionService.revert_to_version(npc, version)
        db.session.commit()
        
        return jsonify({'message': f'Successfully reverted NPC {npc_id} to version {version_number}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/npcs/<int:npc_id>/versions/latest', methods=['GET'])
@jwt_required()
def get_latest_version(npc_id: int):
    """Get the latest version of an NPC."""
    version = NPCVersion.query.filter_by(npc_id=npc_id).order_by(NPCVersion.version_number.desc()).first_or_404()
    return jsonify(version_schema.dump(version))

@bp.route('/npcs/<int:npc_id>/versions/history', methods=['GET'])
@jwt_required()
def get_version_history(npc_id: int):
    """Get a summary of version history for an NPC."""
    versions = NPCVersion.query.filter_by(npc_id=npc_id).order_by(NPCVersion.version_number.desc()).all()
    history = [{
        'version_number': v.version_number,
        'change_type': v.change_type,
        'change_description': v.change_description,
        'changed_fields': v.changed_fields,
        'created_at': v.created_at,
        'code_version_id': v.code_version_id
    } for v in versions]
    return jsonify(history_schema.dump(history)) 