"""
Error handlers.
"""

from flask import render_template, request, jsonify
from app.errors import bp

def wants_json_response():
    """Check if the request wants a JSON response."""
    return request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html

@bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error has occurred'
        }), 500
    return render_template('errors/500.html'), 500

@bp.app_errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    return render_template('errors/403.html'), 403

@bp.app_errorhandler(401)
def unauthorized_error(error):
    """Handle 401 errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource'
        }), 401
    return render_template('errors/401.html'), 401

@bp.app_errorhandler(400)
def bad_request_error(error):
    """Handle 400 errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Bad request',
            'message': 'The server could not understand the request'
        }), 400
    return render_template('errors/400.html'), 400

@bp.app_errorhandler(405)
def method_not_allowed_error(error):
    """Handle 405 errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Method not allowed',
            'message': 'The method is not allowed for the requested URL'
        }), 405
    return render_template('errors/405.html'), 405

@bp.app_errorhandler(429)
def too_many_requests_error(error):
    """Handle 429 errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Too many requests',
            'message': 'You have exceeded the rate limit'
        }), 429
    return render_template('errors/429.html'), 429 