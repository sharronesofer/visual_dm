
#This module provides a single endpoint for checking Firebase connectivity and root structure. It’s used for debugging backend integration and confirming environment setup.
#It connects with the firebase, admin, and ops/devops systems.

from flask import Blueprint, jsonify
from firebase_admin import db

firebase_bp = Blueprint('firebase', __name__)

@firebase_bp.route('/debug_firebase_connection', methods=['GET'])
def debug_firebase_connection():
    try:
        root_ref = db.reference('/')
        data = root_ref.get()
        return jsonify({
            "success": True,
            "root_keys": list(data.keys()) if data else [],
            "database_url": db.reference().path
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
