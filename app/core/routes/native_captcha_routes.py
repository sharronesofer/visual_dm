"""
Native CAPTCHA routes for Unity and other game clients.

These routes provide CAPTCHA generation and validation specifically optimized
for native clients like Unity, mobile apps, and desktop games.
"""

import base64
from flask import Blueprint, jsonify, request, current_app
from app.core.services.native_captcha import native_captcha_service
from app.core.api.error_handling.exceptions import ValidationError, RateLimitError

# Create blueprint
native_captcha_bp = Blueprint('native_captcha', __name__)

@native_captcha_bp.route('/api/v1/captcha/native', methods=['GET'])
def get_native_captcha():
    """
    Generate a new CAPTCHA challenge for native clients.
    ---
    tags:
      - CAPTCHA
    summary: Get a new CAPTCHA challenge for native clients
    description: Generates a new image CAPTCHA or logic challenge for native clients
    parameters:
      - name: type
        in: query
        schema:
          type: string
          enum: [image, audio, logic]
        default: image
        description: Type of CAPTCHA to generate
      - name: difficulty
        in: query
        schema:
          type: string
          enum: [easy, medium, hard]
        default: medium
        description: Difficulty level for the CAPTCHA
      - name: client_id
        in: query
        schema:
          type: string
        description: Optional client identifier for tracking
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
                data:
                  type: object
                  description: CAPTCHA data, varies by type
      429:
        description: Rate limit exceeded
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "rate_limited"
                message:
                  type: string
                  example: "Too many requests"
                retry_after:
                  type: integer
                  example: 300
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
                  example: "An error occurred"
    """
    try:
        captcha_type = request.args.get('type', 'image')
        difficulty = request.args.get('difficulty', 'medium')
        client_id = request.args.get('client_id')
        
        # Check for rate limiting if client ID is provided
        if client_id:
            if native_captcha_service._is_rate_limited(client_id):
                retry_after = native_captcha_service._get_rate_limit_reset_time(client_id)
                return jsonify({
                    'error': 'rate_limited',
                    'message': 'Rate limit exceeded. Please try again later.',
                    'retry_after': retry_after
                }), 429
        
        if captcha_type == 'image':
            challenge_id, image_bytes, metadata = native_captcha_service.generate_image_captcha(difficulty)
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            return jsonify({
                'challenge_id': challenge_id,
                'data': {
                    'image': image_base64,
                    'metadata': metadata
                }
            })
            
        elif captcha_type == 'audio':
            challenge_id, audio_bytes, metadata = native_captcha_service.generate_audio_captcha()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return jsonify({
                'challenge_id': challenge_id,
                'data': {
                    'audio': audio_base64,
                    'metadata': metadata
                }
            })
            
        elif captcha_type == 'logic':
            challenge_id, challenge_data = native_captcha_service.generate_logic_captcha()
            
            return jsonify({
                'challenge_id': challenge_id,
                'data': challenge_data
            })
            
        else:
            return jsonify({
                'error': 'invalid_type',
                'message': f"Invalid CAPTCHA type: {captcha_type}"
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"Error generating native CAPTCHA: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'An error occurred while generating the CAPTCHA'
        }), 500

@native_captcha_bp.route('/api/v1/captcha/native/validate', methods=['POST'])
def validate_native_captcha():
    """
    Validate a CAPTCHA response from a native client.
    ---
    tags:
      - CAPTCHA
    summary: Validate a CAPTCHA response
    description: Validates a response to a CAPTCHA challenge
    requestBody:
      content:
        application/json:
          schema:
            type: object
            required:
              - challenge_id
              - response
            properties:
              challenge_id:
                type: string
                description: The CAPTCHA challenge ID
              response:
                type: string
                description: The user's response to the CAPTCHA
              client_id:
                type: string
                description: Optional client identifier for tracking
    responses:
      200:
        description: Validation result
        content:
          application/json:
            schema:
              type: object
              properties:
                valid:
                  type: boolean
                  description: Whether the CAPTCHA response is valid
                message:
                  type: string
                  description: Result message
      400:
        description: Invalid request
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "invalid_request"
                message:
                  type: string
                  example: "Missing required parameters"
      429:
        description: Rate limit exceeded
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "rate_limited"
                message:
                  type: string
                  example: "Too many attempts"
                retry_after:
                  type: integer
                  example: 300
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
                  example: "An error occurred"
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request must contain JSON data'
            }), 400
            
        challenge_id = data.get('challenge_id')
        response = data.get('response')
        client_id = data.get('client_id')
        
        if not challenge_id or response is None:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Missing required parameters: challenge_id and response'
            }), 400
            
        # Validate the CAPTCHA
        is_valid, result = native_captcha_service.validate_captcha(
            challenge_id=challenge_id,
            response=response,
            client_id=client_id
        )
        
        if is_valid:
            return jsonify({
                'valid': True,
                'message': 'CAPTCHA validation successful'
            })
        else:
            if result.get('error') == 'rate_limited':
                return jsonify({
                    'valid': False,
                    'error': 'rate_limited',
                    'message': result.get('message', 'Rate limit exceeded'),
                    'retry_after': result.get('retry_after', 300)
                }), 429
            else:
                return jsonify({
                    'valid': False,
                    'error': result.get('error', 'validation_failed'),
                    'message': result.get('message', 'CAPTCHA validation failed'),
                    'attempts_remaining': result.get('attempts_remaining')
                }), 400
            
    except Exception as e:
        current_app.logger.error(f"Error validating native CAPTCHA: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'An error occurred while validating the CAPTCHA'
        }), 500 