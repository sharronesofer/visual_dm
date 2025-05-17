from flask import Blueprint, request, jsonify
from app.models.user import User
from backend.app.schemas.user import UserSchema
from backend.app.utils.password import hash_password, verify_password
from backend.app.utils.jwt import create_access_token, create_refresh_token, decode_token
from backend.app.db import db_session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta, datetime
from backend.app.utils.audit_log import log_event
import secrets

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

PASSWORD_RESET_TOKEN_EXPIRY_HOURS = 1

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        log_event('register_failed', None, request.remote_addr, 'Missing email or password')
        return jsonify({'error': 'Email and password required'}), 400
    user = User(email=email, password_hash=hash_password(password))
    db_session.add(user)
    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        log_event('register_failed', None, request.remote_addr, f'Email {email} already registered')
        return jsonify({'error': 'Email already registered'}), 409
    access_token = create_access_token({'sub': user.id})
    refresh_token = create_refresh_token({'sub': user.id})
    log_event('register_success', user.id, request.remote_addr, None)
    return jsonify({
        'user': UserSchema().dump(user),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = db_session.query(User).filter_by(email=email, is_active=True).first()
    if not user or not verify_password(password, user.password_hash):
        log_event('login_failed', None, request.remote_addr, f'Email {email}')
        return jsonify({'error': 'Invalid credentials'}), 401
    access_token = create_access_token({'sub': user.id})
    refresh_token = create_refresh_token({'sub': user.id})
    log_event('login_success', user.id, request.remote_addr, None)
    return jsonify({
        'user': UserSchema().dump(user),
        'access_token': access_token,
        'refresh_token': refresh_token
    })

@bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    payload = decode_token(refresh_token)
    if not payload or 'sub' not in payload:
        log_event('refresh_failed', None, request.remote_addr, 'Invalid refresh token')
        return jsonify({'error': 'Invalid refresh token'}), 401
    user = db_session.query(User).filter_by(id=payload['sub'], is_active=True).first()
    if not user:
        log_event('refresh_failed', None, request.remote_addr, 'User not found')
        return jsonify({'error': 'User not found'}), 404
    access_token = create_access_token({'sub': user.id})
    log_event('refresh_success', user.id, request.remote_addr, None)
    return jsonify({'access_token': access_token})

@bp.route('/logout', methods=['POST'])
def logout():
    # For stateless JWT, logout is handled client-side. Optionally implement token blacklist here.
    log_event('logout', None, request.remote_addr, None)
    return jsonify({'message': 'Logged out successfully'})

@bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')
    if not email:
        log_event('password_reset_request_failed', None, request.remote_addr, 'Missing email')
        return jsonify({'error': 'Email required'}), 400
    user = db_session.query(User).filter_by(email=email, is_active=True).first()
    if not user:
        log_event('password_reset_request_failed', None, request.remote_addr, f'No user for {email}')
        return jsonify({'message': 'If the email exists, a reset link will be sent.'}), 200
    token = secrets.token_urlsafe(32)
    user.password_reset_token = token
    user.password_reset_sent_at = datetime.utcnow()
    db_session.commit()
    log_event('password_reset_requested', user.id, request.remote_addr, None)
    # TODO: Integrate with email service. For now, log the token.
    print(f"Password reset token for {email}: {token}")
    return jsonify({'message': 'If the email exists, a reset link will be sent.'}), 200

@bp.route('/confirm-password-reset', methods=['POST'])
def confirm_password_reset():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    if not token or not new_password:
        log_event('password_reset_confirm_failed', None, request.remote_addr, 'Missing token or new_password')
        return jsonify({'error': 'Token and new password required'}), 400
    user = db_session.query(User).filter_by(password_reset_token=token, is_active=True).first()
    if not user:
        log_event('password_reset_confirm_failed', None, request.remote_addr, 'Invalid token')
        return jsonify({'error': 'Invalid or expired token'}), 400
    sent_at = user.password_reset_sent_at
    if not sent_at or (datetime.utcnow() - sent_at > timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRY_HOURS)):
        log_event('password_reset_confirm_failed', user.id, request.remote_addr, 'Token expired')
        return jsonify({'error': 'Token expired'}), 400
    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_sent_at = None
    db_session.commit()
    log_event('password_reset_success', user.id, request.remote_addr, None)
    return jsonify({'message': 'Password has been reset successfully.'}), 200 