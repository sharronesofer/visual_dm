from flask import Blueprint, request, jsonify
from firebase_admin import auth, db  # Firebase is already initialized in main.py

# Define a Blueprint for authentication-related routes
auth_bp = Blueprint('auth', __name__)

# Sign-Up Route
@auth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not email or not password or not username:
        return jsonify({"error": "Email, password, and username are required"}), 400

    try:
        # Use Firebase Auth to create a new user
        user = auth.create_user(email=email, password=password)

        # Store additional user information in Firebase Realtime Database
        user_ref = db.reference(f"/users/{user.uid}")
        user_ref.set({
            "username": username,
            "email": email,
            "character_data": {}  # Initially set empty character_data object
        })

        return jsonify({"message": "User created successfully", "user_id": user.uid}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")  # Note: Firebase Admin SDK does not verify passwords directly

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Firebase Admin SDK cannot verify passwords directly, so you typically validate them on the client-side
        # Here, we just confirm the user exists in Firebase Auth
        user = auth.get_user_by_email(email)

        # Fetch user data from the Realtime Database
        user_ref = db.reference(f"/users/{user.uid}")
        user_data = user_ref.get()

        if not user_data:
            return jsonify({"error": "User data not found in database"}), 404

        return jsonify({
            "message": "Login successful",
            "user_id": user.uid,
            "username": user_data.get("username"),
            "character_data": user_data.get("character_data")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Logout Route
@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Firebase Auth does not maintain server-side sessions, logout can be handled by client-side tokens.
    return jsonify({"message": "User logged out successfully"})
