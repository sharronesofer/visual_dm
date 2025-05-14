"""
Base route class for consolidating common route patterns.
Provides standardized CRUD operations, authentication, and response handling.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from app.core.utils.base_manager import BaseManager
from app.utils.auth import require_auth
from app.utils.firebase.client import firebase_client
import logging
from app.core.utils.auth_utils import AuthManager
from app.core.utils.error_handlers import handle_error
from app.core.utils.config_utils import get_config

logger = logging.getLogger(__name__)

class BaseRoutes:
    """
    Base class for all route handlers.
    Consolidates common route patterns and functionality.
    """
    
    def __init__(self, name: str, model_class, manager: BaseManager):
        """
        Initialize the base routes.
        
        Args:
            name: Name of the route (e.g., 'character', 'npc', 'region')
            model_class: SQLAlchemy model class
            manager: BaseManager instance for the model
        """
        self.name = name
        self.model_class = model_class
        self.manager = manager
        self.bp = Blueprint(name, __name__)
        self._register_routes()
        
    def _register_routes(self) -> None:
        """Register standard CRUD routes."""
        @self.bp.route(f'/<{self.name}_id>', methods=['GET'])
        @require_auth
        def get_entity(entity_id: str) -> Dict[str, Any]:
            """Get an entity by ID."""
            return jsonify(self.manager.get_entity(entity_id))
            
        @self.bp.route(f'/<{self.name}_id>', methods=['PUT'])
        @require_auth
        def update_entity(entity_id: str) -> Dict[str, Any]:
            """Update an entity."""
            data = request.get_json()
            
            def post_update_hook(entity: Any, data: dict):
                """Hook to run after entity update."""
                # Update Firebase cache
                firebase_client.set(f'/{self.name}s/{entity_id}', entity.to_dict())
                
            return jsonify(self.manager.update_entity(
                entity_id,
                data,
                post_update_hook=post_update_hook
            ))
            
        @self.bp.route(f'/<{self.name}_id>', methods=['DELETE'])
        @require_auth
        def delete_entity(entity_id: str) -> Dict[str, Any]:
            """Delete an entity."""
            try:
                # Delete associated data first
                self._cleanup_associated_data(entity_id)
                
                # Delete the entity
                result = self.manager.delete_entity(entity_id)
                
                if result['success']:
                    # Update Firebase cache
                    firebase_client.delete(f'/{self.name}s/{entity_id}')
                    
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error deleting {self.name}: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
                
    def _cleanup_associated_data(self, entity_id: str) -> None:
        """Clean up data associated with the entity."""
        # Override in subclasses to handle specific cleanup
        pass
        
    def register_custom_route(
        self,
        rule: str,
        methods: List[str],
        handler: Callable,
        require_auth: bool = True
    ) -> None:
        """
        Register a custom route with optional authentication.
        
        Args:
            rule: URL rule
            methods: List of HTTP methods
            handler: Route handler function
            require_auth: Whether to require authentication
        """
        if require_auth:
            handler = self.require_auth(handler)
            
        self.bp.route(rule, methods=methods)(handler)
        
    @staticmethod
    def require_auth(f: Callable) -> Callable:
        """Decorator to require authentication."""
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Get token from header
                auth_header = request.headers.get('Authorization')
                if not auth_header:
                    raise ValueError("No authorization header")
                    
                # Verify token
                token = auth_header.split(" ")[1]
                auth_manager = AuthManager()
                payload = auth_manager.verify_token(token)
                
                # Add user info to request context
                request.user = payload
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Authentication failed: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 401
                
        return decorated 

base_bp = Blueprint('base', __name__)

@base_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@base_bp.route('/api/config', methods=['GET'])
def get_configuration():
    """Get application configuration"""
    config = {
        "debug": get_config('DEBUG', False),
        "environment": get_config('ENVIRONMENT', 'development'),
        "version": get_config('VERSION', '1.0.0')
    }
    return jsonify(config)

@base_bp.errorhandler(Exception)
def handle_exception(error):
    """Global error handler"""
    return handle_error(error) 