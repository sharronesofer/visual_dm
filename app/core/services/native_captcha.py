"""
Native CAPTCHA service for game clients.

This module provides CAPTCHA functionality specifically designed for Unity and other
native game clients, with an emphasis on user experience and cross-platform compatibility.
"""

import random
import string
import time
import secrets
import base64
import hashlib
import json
from io import BytesIO
from typing import Dict, Tuple, Any, Optional, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from flask import current_app, request

class NativeCaptchaService:
    """CAPTCHA service for native game clients."""
    
    def __init__(self):
        """Initialize the CAPTCHA service."""
        self.challenges = {}
        self.solution_expiry_seconds = 300  # 5 minutes
        self.rate_limits = {}  # IP-based rate limiting
        self.max_attempts = 5  # Maximum number of attempts per IP in a time window
        self.rate_limit_window = 60 * 15  # 15 minutes
    
    def generate_image_captcha(self, difficulty: str = 'medium') -> Tuple[str, bytes, Dict[str, Any]]:
        """
        Generate an image-based CAPTCHA suitable for native clients.
        
        Args:
            difficulty: Difficulty level ('easy', 'medium', 'hard')
            
        Returns:
            Tuple of (challenge_id, image_bytes, metadata)
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
        width, height = 250, 100
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Try to get a font, with fallbacks
        try:
            font = ImageFont.truetype("arial.ttf", 45)
        except IOError:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 45)
            except IOError:
                font = ImageFont.load_default()
        
        # Draw text
        try:
            left, top, right, bottom = draw.textbbox((0, 0), solution, font=font)
            text_width = right - left
            text_height = bottom - top
            x = (width - text_width) / 2
            y = (height - text_height) / 2
        except AttributeError:
            # Fallback for older Pillow versions
            text_width, text_height = draw.textsize(solution, font=font)
            x = (width - text_width) / 2
            y = (height - text_height) / 2
            
        draw.text((x, y), solution, font=font, fill=(0, 0, 0))
        
        # Add noise and distortion based on difficulty
        if difficulty != 'easy':
            # Add random lines
            for _ in range(10):
                start = (random.randint(0, width), random.randint(0, height))
                end = (random.randint(0, width), random.randint(0, height))
                draw.line([start, end], fill=(100, 100, 100), width=1)
            
            # Add random dots
            for _ in range(500):
                x = random.randint(0, width)
                y = random.randint(0, height)
                draw.point((x, y), fill=(0, 0, 0))
        
        if difficulty == 'hard':
            # Apply distortion for hard mode
            image = image.filter(ImageFilter.GaussianBlur(radius=0.8))
            # Add more complex noise
            for _ in range(15):
                size = random.randint(5, 15)
                x = random.randint(0, width - size)
                y = random.randint(0, height - size)
                shape_color = (random.randint(150, 230), random.randint(150, 230), random.randint(150, 230))
                draw.rectangle([x, y, x + size, y + size], outline=shape_color)
        
        # Convert image to bytes
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        
        # Store solution with timestamp
        challenge_id = self._generate_challenge_id()
        self.challenges[challenge_id] = {
            'solution': solution,
            'timestamp': time.time(),
            'type': 'image',
            'attempts': 0,
            'max_attempts': 3
        }
        
        # Create metadata for client
        metadata = {
            'type': 'image',
            'format': 'png',
            'width': width,
            'height': height,
            'difficulty': difficulty
        }
        
        return challenge_id, image_bytes, metadata
    
    def generate_audio_captcha(self) -> Tuple[str, bytes, Dict[str, Any]]:
        """
        Generate an audio-based CAPTCHA for accessibility.
        
        Returns:
            Tuple of (challenge_id, audio_bytes, metadata)
        """
        # Generate a simple numeric code for audio
        length = 5
        solution = ''.join(random.choice(string.digits) for _ in range(length))
        
        # In a real implementation, we would generate actual audio here
        # For this example, we'll just create a placeholder
        audio_bytes = b'AUDIO_PLACEHOLDER'  # This would be real audio in production
        
        # Store solution with timestamp
        challenge_id = self._generate_challenge_id()
        self.challenges[challenge_id] = {
            'solution': solution,
            'timestamp': time.time(),
            'type': 'audio',
            'attempts': 0,
            'max_attempts': 3
        }
        
        # Create metadata for client
        metadata = {
            'type': 'audio',
            'format': 'mp3',
            'duration': 5,  # seconds
            'digits': length
        }
        
        return challenge_id, audio_bytes, metadata
    
    def generate_logic_captcha(self) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a logic-based CAPTCHA suitable for native clients.
        
        Returns:
            Tuple of (challenge_id, challenge_data)
        """
        # Generate a simple math or logic problem
        challenge_type = random.choice(['math', 'order', 'count'])
        
        if challenge_type == 'math':
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
                
            challenge_data = {
                'type': 'math',
                'question': question,
                'input_type': 'numeric'
            }
            
        elif challenge_type == 'order':
            # Create a sequence ordering challenge
            sequence_length = 5
            items = random.sample(string.ascii_uppercase, sequence_length)
            question = f"Order these letters alphabetically: {' '.join(items)}"
            solution = ''.join(sorted(items))
            
            challenge_data = {
                'type': 'order',
                'question': question,
                'items': items,
                'input_type': 'text'
            }
            
        else:  # 'count'
            # Create a counting challenge
            shapes = ['circle', 'square', 'triangle', 'star']
            counts = {shape: random.randint(1, 5) for shape in shapes}
            target_shape = random.choice(shapes)
            question = f"How many {target_shape}s are there in the image?"
            solution = str(counts[target_shape])
            
            challenge_data = {
                'type': 'count',
                'question': question,
                'shapes': counts,
                'target_shape': target_shape,
                'input_type': 'numeric'
            }
        
        # Store solution with timestamp
        challenge_id = self._generate_challenge_id()
        self.challenges[challenge_id] = {
            'solution': solution,
            'timestamp': time.time(),
            'type': 'logic',
            'attempts': 0,
            'max_attempts': 3
        }
        
        challenge_data['challenge_id'] = challenge_id
        return challenge_id, challenge_data
    
    def validate_captcha(self, challenge_id: str, response: str, client_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a CAPTCHA response.
        
        Args:
            challenge_id: Unique identifier for the CAPTCHA challenge
            response: User's response to the CAPTCHA
            client_id: Optional client identifier for rate limiting
            
        Returns:
            Tuple of (is_valid, result_data)
        """
        # Apply rate limiting if client ID is provided
        if client_id:
            if self._is_rate_limited(client_id):
                return False, {
                    'error': 'rate_limited',
                    'message': 'Too many attempts. Please try again later.',
                    'retry_after': self._get_rate_limit_reset_time(client_id)
                }
        
        # Check if challenge exists
        if challenge_id not in self.challenges:
            return False, {
                'error': 'invalid_challenge',
                'message': 'Challenge not found or expired'
            }
        
        challenge = self.challenges[challenge_id]
        
        # Check if challenge has expired
        current_time = time.time()
        if current_time - challenge['timestamp'] > self.solution_expiry_seconds:
            del self.challenges[challenge_id]
            return False, {
                'error': 'expired',
                'message': 'CAPTCHA challenge has expired'
            }
        
        # Check attempt limit
        challenge['attempts'] += 1
        if challenge['attempts'] > challenge['max_attempts']:
            del self.challenges[challenge_id]
            return False, {
                'error': 'max_attempts',
                'message': 'Maximum attempt limit reached'
            }
        
        # Normalize and validate response
        normalized_response = self._normalize_response(response, challenge['type'])
        is_valid = challenge['solution'] == normalized_response
        
        # Record the attempt in rate limiting if client ID is provided
        if client_id and not is_valid:
            self._record_attempt(client_id)
        
        # Remove challenge after successful validation
        if is_valid:
            del self.challenges[challenge_id]
            return True, {
                'success': True,
                'message': 'CAPTCHA validated successfully'
            }
        else:
            return False, {
                'error': 'invalid_response',
                'message': 'Incorrect CAPTCHA response',
                'attempts_remaining': challenge['max_attempts'] - challenge['attempts']
            }
    
    def _normalize_response(self, response: str, challenge_type: str) -> str:
        """Normalize user response based on challenge type."""
        if not response:
            return ""
            
        if challenge_type == 'image':
            # Case-insensitive for image CAPTCHAs
            return response.strip().lower()
        elif challenge_type == 'audio':
            # Numbers only for audio CAPTCHAs
            return ''.join([c for c in response if c.isdigit()])
        elif challenge_type == 'logic':
            # Depends on the specific logic challenge
            return response.strip()
        
        return response.strip()
    
    def _generate_challenge_id(self) -> str:
        """
        Generate a unique identifier for a CAPTCHA challenge.
        
        Returns:
            Unique challenge ID
        """
        return secrets.token_urlsafe(32)
    
    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if a client is rate limited."""
        if client_id not in self.rate_limits:
            return False
            
        current_time = time.time()
        client_data = self.rate_limits[client_id]
        
        # Check if rate limit window has reset
        if current_time - client_data['start_time'] > self.rate_limit_window:
            # Reset rate limit data
            self.rate_limits[client_id] = {
                'attempts': 0,
                'start_time': current_time
            }
            return False
            
        # Check if maximum attempts have been reached
        return client_data['attempts'] >= self.max_attempts
    
    def _record_attempt(self, client_id: str) -> None:
        """Record a failed attempt for rate limiting."""
        current_time = time.time()
        
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = {
                'attempts': 1,
                'start_time': current_time
            }
        else:
            # Check if rate limit window has reset
            if current_time - self.rate_limits[client_id]['start_time'] > self.rate_limit_window:
                # Reset rate limit data
                self.rate_limits[client_id] = {
                    'attempts': 1,
                    'start_time': current_time
                }
            else:
                # Increment attempt count
                self.rate_limits[client_id]['attempts'] += 1
    
    def _get_rate_limit_reset_time(self, client_id: str) -> int:
        """Get the number of seconds until rate limit resets."""
        if client_id not in self.rate_limits:
            return 0
            
        current_time = time.time()
        client_data = self.rate_limits[client_id]
        
        time_elapsed = current_time - client_data['start_time']
        time_remaining = max(0, self.rate_limit_window - time_elapsed)
        
        return int(time_remaining)
    
    def cleanup_expired_challenges(self) -> None:
        """Clean up expired CAPTCHA challenges."""
        current_time = time.time()
        expired_challenges = []
        
        for challenge_id, challenge in self.challenges.items():
            if current_time - challenge['timestamp'] > self.solution_expiry_seconds:
                expired_challenges.append(challenge_id)
        
        for challenge_id in expired_challenges:
            del self.challenges[challenge_id]

# Global instance
native_captcha_service = NativeCaptchaService() 