"""
Authentication routes.
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app.auth import bp
from app.core.models.user import User
from app.core.database import db
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt
)
from app.auth.auth_utils import AuthService

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        user.update_last_login()

        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'user')  # Optional: allow role assignment if needed

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))

        # Password strength validation
        if not User.validate_password_strength(password):
            flash('Password must be at least 8 characters long and contain both letters and numbers.', 'error')
            return redirect(url_for('auth.register'))

        try:
            user = User(username=username, email=email, password=password, role=role)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username_or_email = data.get('username') or data.get('email')
    password = data.get('password')
    if not username_or_email or not password:
        return jsonify({'msg': 'Missing username/email or password'}), 400
    user = AuthService.authenticate_user(username_or_email, password)
    if not user:
        return jsonify({'msg': 'Invalid credentials'}), 401
    access_token, refresh_token = AuthService.generate_tokens(user)
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    }), 200

@bp.route('/api/logout', methods=['POST'])
@jwt_required()
def api_logout():
    jti = get_jwt()['jti']
    AuthService.blacklist_token(jti)
    return jsonify({'msg': 'Successfully logged out'}), 200

@bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def api_refresh():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    access_token, _ = AuthService.generate_tokens(user)
    return jsonify({'access_token': access_token}), 200 