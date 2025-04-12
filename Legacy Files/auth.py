from flask import Blueprint, request, jsonify, current_app
from firebase_admin import auth, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    """
    Endpoint to sign up a new user.
    Expects JSON with 'username', 'email', and 'password'.
    """
    data = request.get_json(force=True)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not email or not password or not username:
        return jsonify({"error": "Email, password, and username are required"}), 400

    try:
        user = auth.create_user(email=email, password=password)
        user_ref = db.reference(f"/users/{user.uid}")
        user_ref.set({
            "username": username,
            "email": email,
            "character_data": {},
            "narrator_style": "Tolkien"  # default style
        })
        return jsonify({"message": "User created successfully", "user_id": user.uid}), 201
    except Exception as e:
        current_app.logger.error(f"Error during sign up: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint to log in a user.
    Expects JSON with 'email'. Note: Password verification is handled client-side.
    """
    data = request.get_json(force=True)
    email = data.get("email")
    # Password is not used in backend authentication due to Firebase Admin SDK limitations.
    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        user = auth.get_user_by_email(email)
        user_ref = db.reference(f"/users/{user.uid}")
        user_data = user_ref.get()
        if not user_data:
            return jsonify({"error": "User data not found in database"}), 404

        return jsonify({
            "message": "Login successful",
            "user_id": user.uid,
            "username": user_data.get("username"),
            "narrator_style": user_data.get("narrator_style", "Tolkien"),
            "character_data": user_data.get("character_data", {})
        })
    except Exception as e:
        current_app.logger.error(f"Error during login: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Endpoint for logout.
    Note: Actual logout is handled on the client-side by the Firebase client SDK.
    """
    return jsonify({"message": "User logged out (handled client-side)."})

@auth_bp.route('/chat')
def chat():
    return render_template("chat.html")