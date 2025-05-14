"""
Region management routes.
"""

import uuid
from flask import Blueprint, jsonify

regions_bp = Blueprint('regions', __name__)

@regions_bp.route('/create_starting_region', methods=['POST'])
def create_starting_region():
    """Create a basic starting region."""
    region_id = f"region_{uuid.uuid4().hex[:8]}"
    region = {
        "region_id": region_id,
        "name": "Starting Region",
        "description": "A peaceful starting area for new adventurers.",
        "type": "starting_area",
        "level_range": [1, 5],
        "points_of_interest": []
    }
    return jsonify({"region": region}) 