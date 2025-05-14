from typing import Any, Dict, List, Optional, Type, Union
from flask import Blueprint, request, current_app
from flask.views import MethodView
from pydantic import BaseModel, ValidationError

from .response import APIResponse
from ..auth.decorators import require_auth, require_role, require_permission

class BaseBlueprint(Blueprint):
    """Base blueprint class with common functionality for all API endpoints."""
    
    def __init__(self, name: str, import_name: str, *args, **kwargs):
        """Initialize the blueprint with standard prefix and error handlers."""
        super().__init__(name, import_name, url_prefix=f"/api/v1/{name}", *args, **kwargs)
        self.register_error_handlers()
        
    def register_error_handlers(self):
        """Register common error handlers for the blueprint."""
        
        @self.errorhandler(ValidationError)
        def handle_validation_error(error):
            return APIResponse.bad_request(
                message="Validation error",
                details={"errors": error.errors()}
            ).to_dict(), 400
            
        @self.errorhandler(404)
        def handle_not_found(error):
            return APIResponse.not_found().to_dict(), 404
            
        @self.errorhandler(Exception)
        def handle_generic_error(error):
            current_app.logger.exception("Unhandled error occurred")
            return APIResponse.server_error().to_dict(), 500

    def register_view(self, view: Type[MethodView], 
                     urls: List[str], 
                     endpoint: Optional[str] = None,
                     decorators: Optional[List[callable]] = None):
        """Register a MethodView with the blueprint."""
        if decorators:
            for decorator in decorators:
                view.decorators = view.decorators + [decorator] if hasattr(view, 'decorators') else [decorator]
                
        view_func = view.as_view(endpoint or view.__name__.lower())
        for url in urls:
            self.add_url_rule(url, view_func=view_func)
            
    def paginate(self, query_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract and validate pagination parameters."""
        params = query_params or request.args
        try:
            page = max(1, int(params.get('page', 1)))
            limit = min(100, max(1, int(params.get('limit', 20))))
            offset = (page - 1) * limit
            
            return {
                'page': page,
                'limit': limit,
                'offset': offset
            }
        except ValueError:
            return {
                'page': 1,
                'limit': 20,
                'offset': 0
            }
            
    def get_filter_params(self, allowed_filters: List[str]) -> Dict[str, Any]:
        """Extract and validate filter parameters."""
        filters = {}
        for key in allowed_filters:
            if key in request.args:
                filters[key] = request.args[key]
        return filters
        
    def get_sort_params(self, allowed_fields: List[str]) -> List[tuple]:
        """Extract and validate sort parameters."""
        sort_params = []
        sort_str = request.args.get('sort', '')
        
        if not sort_str:
            return sort_params
            
        for field in sort_str.split(','):
            if field.startswith('-'):
                direction = 'desc'
                field = field[1:]
            else:
                direction = 'asc'
                
            if field in allowed_fields:
                sort_params.append((field, direction))
                
        return sort_params
        
    def validate_request_body(self, model: Type[BaseModel]) -> BaseModel:
        """Validate request body against a Pydantic model."""
        try:
            return model.parse_obj(request.get_json())
        except ValidationError as e:
            raise ValidationError(e.raw_errors)
            
    def get_fields_to_return(self, allowed_fields: List[str]) -> List[str]:
        """Extract and validate fields to return."""
        fields = request.args.get('fields', '').split(',')
        return [f for f in fields if f and f in allowed_fields] or allowed_fields 