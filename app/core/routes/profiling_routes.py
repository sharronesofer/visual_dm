"""
Routes for accessing building generation profiling data.
"""

from flask import Blueprint, jsonify, request, render_template
from app.core.profiling.building_profiler import building_profiler
from app.core.utils.monitoring import track_performance

bp = Blueprint('profiling', __name__, url_prefix='/profiling')

@bp.route('/dashboard')
@track_performance
def dashboard():
    """Display the building generation performance dashboard."""
    return render_template('profiling/dashboard.html')

@bp.route('/building/stats', methods=['GET'])
@track_performance
def get_building_stats():
    """Get overall building generation statistics."""
    return jsonify(building_profiler.get_statistics())

@bp.route('/building/<building_id>', methods=['GET'])
@track_performance
def get_building_profile(building_id: str):
    """Get profile data for a specific building."""
    profile = building_profiler.get_profile(building_id)
    if not profile:
        return jsonify({'error': 'Building profile not found'}), 404
    return jsonify(profile)

@bp.route('/building/reset', methods=['POST'])
@track_performance
def reset_building_stats():
    """Reset all building profiling data."""
    building_profiler.reset_statistics()
    return jsonify({'message': 'Building profiling data reset successfully'})

profiling_routes = bp 