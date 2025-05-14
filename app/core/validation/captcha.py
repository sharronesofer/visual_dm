"""
CAPTCHA validation for preventing automated attacks.

This module provides functionality for generating and validating various types of CAPTCHA
challenges to protect authentication forms and other sensitive operations from automated attacks.
"""

import random
import string
import time
from functools import wraps
from typing import Callable, Dict, Optional, Tuple, Any
import secrets
import base64
import hmac
import hashlib
from io import BytesIO
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from flask import request, jsonify, current_app, g, session
from app.core.api.error_handling.exceptions import ValidationError

class CaptchaManager:
    """Manager for generating and validating CAPTCHA challenges."""
    
    def __init__(self):
        """Initialize CAPTCHA manager."""
        self.challenges = {}
        self.solution_expiry_seconds = 300  # 5 minutes
    
    def generate_image_captcha(self, difficulty: str = 'medium') -> Tuple[str, bytes]:
        """Generate an image-based CAPTCHA.
        
        Args:
            difficulty: Difficulty level ('easy', 'medium', 'hard')
            
        Returns:
            Tuple of (solution, image_bytes)
        """
        # Generate random text for CAPTCHA
        if difficulty == 'easy':
            length = 4
            chars = string.ascii_uppercase + string.digits
        elif difficulty == 'medium':
            length = 5
            chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        else:  # hard
            length = 6
            chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        
        solution = ''.join(random.choice(chars) for _ in range(length))
        
        # Create image with text
        width, height = 200, 80
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Try to get a font, with fallbacks
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 40)
            except IOError:
                font = ImageFont.load_default()
        
        # Draw text
        left, top, right, bottom = draw.textbbox((0, 0), solution, font=font)
        text_width = right - left
        text_height = bottom - top
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        draw.text((x, y), solution, font=font, fill=(0, 0, 0))
        
        # Add noise and distortion
        if difficulty != 'easy':
            # Add random lines
            for _ in range(8):
                start = (random.randint(0, width), random.randint(0, height))
                end = (random.randint(0, width), random.randint(0, height))
                draw.line([start, end], fill=(0, 0, 0), width=2)
            
            # Add random points
            for _ in range(1000):
                x = random.randint(0, width)
                y = random.randint(0, height)
                draw.point((x, y), fill=(0, 0, 0))
            
            # Apply filters
            image = image.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Convert image to bytes
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        
        # Store solution with timestamp
        challenge_id = self._generate_challenge_id()
        self.challenges[challenge_id] = {
            'solution': solution,
            'timestamp': time.time(),
            'type': 'image'
        }
        
        return challenge_id, image_bytes
    
    def generate_text_captcha(self) -> Tuple[str, Dict[str, Any]]:
        """Generate a text-based logic CAPTCHA.
        
        Returns:
            Tuple of (challenge_id, challenge_data)
        """
        # Generate a simple math problem
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        op = random.choice(['+', '-', '*'])
        
        if op == '+':
            solution = str(a + b)
            question = f"What is {a} plus {b}?"
        elif op == '-':
            # Ensure positive result
            if b > a:
                a, b = b, a
            solution = str(a - b)
            question = f"What is {a} minus {b}?"
        else:  # '*'
            solution = str(a * b)
            question = f"What is {a} multiplied by {b}?"
        
        # Store solution with timestamp
        challenge_id = self._generate_challenge_id()
        self.challenges[challenge_id] = {
            'solution': solution,
            'timestamp': time.time(),
            'type': 'text'
        }
        
        return challenge_id, {'question': question}
    
    def validate_captcha(self, challenge_id: str, response: str) -> bool:
        """Validate a CAPTCHA response.
        
        Args:
            challenge_id: Unique identifier for the CAPTCHA challenge
            response: User's response to the CAPTCHA
            
        Returns:
            True if the response is valid, False otherwise
        """
        # Check if challenge exists
        if challenge_id not in self.challenges:
            return False
        
        challenge = self.challenges[challenge_id]
        
        # Check if challenge has expired
        current_time = time.time()
        if current_time - challenge['timestamp'] > self.solution_expiry_seconds:
            del self.challenges[challenge_id]
            return False
        
        # Validate response
        is_valid = challenge['solution'].lower() == response.lower()
        
        # Remove challenge after validation
        del self.challenges[challenge_id]
        
        return is_valid
    
    def _generate_challenge_id(self) -> str:
        """Generate a unique identifier for a CAPTCHA challenge.
        
        Returns:
            Unique challenge ID
        """
        return secrets.token_urlsafe(32)
    
    def cleanup_expired_challenges(self) -> None:
        """Clean up expired CAPTCHA challenges."""
        current_time = time.time()
        expired_challenges = []
        
        for challenge_id, challenge in self.challenges.items():
            if current_time - challenge['timestamp'] > self.solution_expiry_seconds:
                expired_challenges.append(challenge_id)
        
        for challenge_id in expired_challenges:
            del self.challenges[challenge_id]

# Global CAPTCHA manager instance
captcha_manager = CaptchaManager()

def require_captcha(view_name: Optional[str] = None):
    """
    Decorator for requiring CAPTCHA validation on endpoints.
    
    Args:
        view_name: Name of the view to use for CAPTCHA generation (if different from the decorated view)
            
    Returns:
        Decorated function
    
    Usage:
        @app.route('/register', methods=['POST'])
        @require_captcha()
        def register():
            # Request is guaranteed to have a valid CAPTCHA response
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                if request.method == 'GET':
                    # This is a GET request, likely showing a form
                    # Generate a new CAPTCHA for the form
                    challenge_id, image_bytes = captcha_manager.generate_image_captcha()
                    captcha_image = base64.b64encode(image_bytes).decode('utf-8')
                    
                    # Store the challenge ID in the session
                    session['captcha_challenge_id'] = challenge_id
                    g.captcha_image = captcha_image
                    
                    return f(*args, **kwargs)
                else:
                    # This is a form submission, validate the CAPTCHA
                    challenge_id = session.get('captcha_challenge_id')
                    if not challenge_id:
                        raise ValidationError(
                            message="CAPTCHA challenge not found",
                            details=[{"field": "captcha", "message": "Please refresh and try again"}]
                        )
                    
                    captcha_response = request.form.get('captcha')
                    if not captcha_response:
                        raise ValidationError(
                            message="CAPTCHA response not provided",
                            details=[{"field": "captcha", "message": "Please complete the CAPTCHA"}]
                        )
                    
                    is_valid = captcha_manager.validate_captcha(challenge_id, captcha_response)
                    if not is_valid:
                        raise ValidationError(
                            message="Invalid CAPTCHA response",
                            details=[{"field": "captcha", "message": "Incorrect CAPTCHA response"}]
                        )
                    
                    # Clear the challenge ID from the session
                    session.pop('captcha_challenge_id', None)
                    
                    return f(*args, **kwargs)
                
            except ValidationError as e:
                current_app.logger.warning(f"CAPTCHA validation error: {e.message}")
                
                # Generate a new CAPTCHA for retry
                challenge_id, image_bytes = captcha_manager.generate_image_captcha()
                captcha_image = base64.b64encode(image_bytes).decode('utf-8')
                session['captcha_challenge_id'] = challenge_id
                g.captcha_image = captcha_image
                g.validation_error = e
                
                # If using a different view for CAPTCHA, redirect to it
                if view_name and view_name != f.__name__:
                    from flask import redirect, url_for
                    return redirect(url_for(view_name))
                
                # Otherwise, re-render the current view with error
                return f(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"CAPTCHA validation error: {str(e)}")
                return jsonify({
                    "error": "internal_error",
                    "message": "An error occurred while validating the CAPTCHA"
                }), 500
        
        return decorated
    return decorator

def api_require_captcha():
    """
    Decorator for requiring CAPTCHA validation on API endpoints.
    
    Returns:
        Decorated function
    
    Usage:
        @app.route('/api/register', methods=['POST'])
        @api_require_captcha()
        def api_register():
            # Request is guaranteed to have a valid CAPTCHA response
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                data = request.get_json(force=True) if request.is_json else {}
                challenge_id = data.get('captcha_challenge_id')
                captcha_response = data.get('captcha_response')
                
                # Validate CAPTCHA inputs
                if not challenge_id:
                    return jsonify({
                        "error": "validation_error",
                        "message": "CAPTCHA challenge ID not provided",
                        "details": [{"field": "captcha_challenge_id", "message": "Required field"}]
                    }), 400
                
                if not captcha_response:
                    return jsonify({
                        "error": "validation_error",
                        "message": "CAPTCHA response not provided",
                        "details": [{"field": "captcha_response", "message": "Required field"}]
                    }), 400
                
                # Validate CAPTCHA
                is_valid = captcha_manager.validate_captcha(challenge_id, captcha_response)
                if not is_valid:
                    # Generate a new CAPTCHA for retry
                    new_challenge_id, image_bytes = captcha_manager.generate_image_captcha()
                    captcha_image = base64.b64encode(image_bytes).decode('utf-8')
                    
                    return jsonify({
                        "error": "validation_error",
                        "message": "Invalid CAPTCHA response",
                        "details": [{"field": "captcha_response", "message": "Incorrect CAPTCHA response"}],
                        "new_captcha": {
                            "challenge_id": new_challenge_id,
                            "image": captcha_image
                        }
                    }), 400
                
                return f(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"API CAPTCHA validation error: {str(e)}")
                return jsonify({
                    "error": "internal_error",
                    "message": "An error occurred while validating the CAPTCHA"
                }), 500
        
        return decorated
    return decorator

def get_captcha():
    """
    Generate a new CAPTCHA challenge.
    
    Returns:
        Dictionary with challenge_id and image data
    """
    challenge_id, image_bytes = captcha_manager.generate_image_captcha()
    captcha_image = base64.b64encode(image_bytes).decode('utf-8')
    
    return {
        'challenge_id': challenge_id,
        'image': captcha_image
    } 