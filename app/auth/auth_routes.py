from flask import Blueprint, request, jsonify
from app.auth.auth_utils import (
    create_user,
    get_user_by_username,
    verify_user_password,
    log_auth_event
)


# Define blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json(force=True)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400

    existing_user_id, _ = get_user_by_username(username)
    if existing_user_id:
        return jsonify({"error": "Username already taken."}), 409

    user_id = create_user(username, email, password)
    log_auth_event(user_id, event_type="signup")

    return jsonify({"message": "User created successfully.", "user_id": user_id}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user_id, user_data = get_user_by_username(username)
    if not user_data:
        return jsonify({"error": "User not found."}), 404

    if verify_user_password(user_data, password):
        log_auth_event(user_id, event_type="login")
        return jsonify({"message": "Login successful.", "user_id": user_id}), 200
    else:
        return jsonify({"error": "Invalid password."}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    data = request.get_json(force=True)
    user_id = data.get("user_id")

    if user_id:
        log_auth_event(user_id, event_type="logout")

    return jsonify({"message": "User logged out successfully."}), 200