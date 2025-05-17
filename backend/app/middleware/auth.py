from functools import wraps
from flask import request, g, jsonify
from backend.app.utils.jwt import decode_token
from app.models.user import User, Role, Permission
from backend.app.db import db_session

# Helper to get user from JWT

def get_current_user():
    auth_header = request.headers.get('Authorization', None)
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    payload = decode_token(token)
    if not payload or 'sub' not in payload:
        return None
    user = db_session.query(User).filter_by(id=payload['sub'], is_active=True).first()
    return user

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper

def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            user_roles = {role.name for role in user.roles}
            if not any(role in user_roles for role in roles):
                return jsonify({'error': 'Insufficient role'}), 403
            g.current_user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def permissions_required(*permissions):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            user_permissions = {perm.name for role in user.roles for perm in role.permissions}
            if not all(perm in user_permissions for perm in permissions):
                return jsonify({'error': 'Insufficient permissions'}), 403
            g.current_user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator 