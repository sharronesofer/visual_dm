"""
Health and system status routes.
"""

from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/')
def root():
    return jsonify({
        "status": "ok",
        "message": "Visual DM API is running",
        "version": "1.0.0"
    })

@health_bp.route('/health')
def health_check():
    return jsonify({"status": "ok"}) 