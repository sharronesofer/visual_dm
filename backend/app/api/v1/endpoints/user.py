from flask import Blueprint, request, jsonify, g
from backend.app.models.user import User
from backend.app.schemas.user import UserSchema
from backend.app.db import db_session
from backend.app.middleware.auth import jwt_required
from backend.app.utils.audit_log import log_event

bp = Blueprint('user', __name__, url_prefix='/api/v1/user')

@bp.route('/profile', methods=['GET'])
@jwt_required
def get_profile():
    user = g.current_user
    return jsonify({'user': UserSchema().dump(user)})

@bp.route('/profile', methods=['PUT'])
@jwt_required
def update_profile():
    user = g.current_user
    data = request.get_json()
    # Only allow updating certain fields
    allowed_fields = {'email'}
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    db_session.commit()
    log_event('profile_update', user.id, request.remote_addr, None)
    return jsonify({'user': UserSchema().dump(user)})

@bp.route('/deactivate', methods=['POST'])
@jwt_required
def deactivate_account():
    user = g.current_user
    user.is_active = False
    db_session.commit()
    log_event('account_deactivate', user.id, request.remote_addr, None)
    return jsonify({'message': 'Account deactivated'}) 