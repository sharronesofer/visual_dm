"""
CAPTCHA generation routes for authentication forms.
"""

from flask import Blueprint, jsonify, current_app, request, session, redirect, url_for
from app.core.validation.captcha import captcha_manager

# Create blueprint
captcha_bp = Blueprint('captcha', __name__)

@captcha_bp.route('/api/captcha', methods=['GET'])
def get_api_captcha():
    """
    Generate a new CAPTCHA challenge for API clients.
    ---
    tags:
      - CAPTCHA
    summary: Get a new CAPTCHA challenge
    description: Generates a new image CAPTCHA challenge for client-side authentication forms
    responses:
      200:
        description: CAPTCHA generated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                challenge_id:
                  type: string
                  description: Unique identifier for this CAPTCHA challenge
                  example: "abcd1234"
                image:
                  type: string
                  description: Base64-encoded PNG image
                  example: "data:image/png;base64,iVBORw0KGg..."
      500:
        description: Server error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "internal_error"
                message:
                  type: string
                  example: "An error occurred while generating the CAPTCHA"
    """
    try:
        # Generate new CAPTCHA
        challenge_id, image_bytes = captcha_manager.generate_image_captcha()
        
        # Convert image to base64
        import base64
        captcha_image = base64.b64encode(image_bytes).decode('utf-8')
        
        return jsonify({
            'challenge_id': challenge_id,
            'image': captcha_image
        })
    except Exception as e:
        current_app.logger.error(f"Error generating CAPTCHA: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'An error occurred while generating the CAPTCHA'
        }), 500

@captcha_bp.route('/api/captcha/text', methods=['GET'])
def get_text_captcha():
    """
    Generate a new text-based CAPTCHA challenge.
    ---
    tags:
      - CAPTCHA
    summary: Get a new text CAPTCHA challenge
    description: Generates a new text-based logic CAPTCHA challenge (e.g., math problem)
    responses:
      200:
        description: Text CAPTCHA generated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                challenge_id:
                  type: string
                  description: Unique identifier for this CAPTCHA challenge
                  example: "efgh5678"
                question:
                  type: string
                  description: The text question to display to the user
                  example: "What is 5 plus 3?"
      500:
        description: Server error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "internal_error"
                message:
                  type: string
                  example: "An error occurred while generating the CAPTCHA"
    """
    try:
        # Generate new text CAPTCHA
        challenge_id, challenge_data = captcha_manager.generate_text_captcha()
        
        return jsonify({
            'challenge_id': challenge_id,
            'question': challenge_data['question']
        })
    except Exception as e:
        current_app.logger.error(f"Error generating text CAPTCHA: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'An error occurred while generating the CAPTCHA'
        }), 500

@captcha_bp.route('/captcha/update-session', methods=['POST'])
def update_session_captcha():
    """Update the CAPTCHA challenge ID in the session."""
    try:
        challenge_id = request.form.get('challenge_id')
        if challenge_id:
            # Verify this is a valid challenge ID
            if challenge_id in captcha_manager.challenges:
                session['captcha_challenge_id'] = challenge_id
                
        # Redirect back to the referring page
        referrer = request.referrer or url_for('main.index')
        return redirect(referrer)
        
    except Exception as e:
        current_app.logger.error(f"Error updating session CAPTCHA: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'An error occurred while updating the CAPTCHA session'
        }), 500 