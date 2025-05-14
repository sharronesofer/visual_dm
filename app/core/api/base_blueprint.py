"""
Base blueprint class for API endpoints with common functionality.
"""

from typing import Any, Dict, Optional, Type, Union
from flask import Blueprint, request, current_app
from functools import wraps
from ..utils.api_response import (
    APIResponse,
    APIStatus,
    ErrorCode,
    create_validation_error,
    create_unauthorized_error,
    create_forbidden_error,
    create_internal_error
)
from ..auth.jwt_manager import verify_jwt_token, JWTError

class BaseAPIBlueprint(Blueprint):
    """Base class for API blueprints with common functionality."""

    def __init__(
        self,
        name: str,
        import_name: str,
        url_prefix: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize the blueprint.

        Args:
            name: Blueprint name
            import_name: Import name for the blueprint
            url_prefix: URL prefix for all routes in this blueprint
            **kwargs: Additional arguments passed to Blueprint
        """
        if url_prefix is None:
            url_prefix = f"/api/v1/{name}"
        super().__init__(name, import_name, url_prefix=url_prefix, **kwargs)

        # Register error handlers
        self.register_error_handler(Exception, self._handle_error)

    def _handle_error(self, error: Exception) -> Any:
        """Global error handler for the blueprint."""
        current_app.logger.error(f"Error in {self.name}: {str(error)}", exc_info=error)
        return create_internal_error().to_response()

    def require_auth(self, f: Any) -> Any:
        """Decorator to require authentication for a route."""
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return create_unauthorized_error().to_response()
            
            try:
                token = auth_header.split(' ')[1]
                user_data = verify_jwt_token(token)
                return f(*args, user_data=user_data, **kwargs)
            except (IndexError, JWTError) as e:
                return create_unauthorized_error(str(e)).to_response()
            except Exception as e:
                current_app.logger.error(f"Auth error: {str(e)}", exc_info=e)
                return create_internal_error().to_response()
        
        return decorated

    def require_roles(self, roles: Union[str, list[str]]) -> Any:
        """
        Decorator to require specific roles for a route.
        Must be used after @require_auth.
        """
        if isinstance(roles, str):
            roles = [roles]

        def decorator(f: Any) -> Any:
            @wraps(f)
            def decorated(*args: Any, **kwargs: Any) -> Any:
                user_data = kwargs.get('user_data', {})
                user_roles = user_data.get('roles', [])
                
                if not any(role in user_roles for role in roles):
                    return create_forbidden_error().to_response()
                
                return f(*args, **kwargs)
            return decorated
        return decorator

    def validate_json(self, schema: Type[Any]) -> Any:
        """Decorator to validate request JSON against a Pydantic model."""
        def decorator(f: Any) -> Any:
            @wraps(f)
            def decorated(*args: Any, **kwargs: Any) -> Any:
                if not request.is_json:
                    return create_validation_error(
                        "Content-Type must be application/json"
                    ).to_response()
                
                try:
                    data = request.get_json()
                    validated_data = schema(**data)
                    return f(*args, data=validated_data, **kwargs)
                except Exception as e:
                    return create_validation_error(
                        str(e),
                        details={"errors": str(e)}
                    ).to_response()
            return decorated
        return decorator

    def paginate(self, f: Any) -> Any:
        """Decorator to add pagination to a route."""
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            page = request.args.get('page', 1, type=int)
            limit = min(
                request.args.get('limit', 10, type=int),
                100  # Maximum items per page
            )
            
            result = f(*args, page=page, limit=limit, **kwargs)
            
            if not isinstance(result, tuple):
                data, total = result, None
            else:
                data, total = result
            
            response_data = {
                "items": data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total
                } if total is not None else None
            }
            
            return APIResponse.success(
                data=response_data,
                metadata={"has_more": total > page * limit if total else None}
            ).to_response()
        
        return decorated

    def filter_fields(self, f: Any) -> Any:
        """Decorator to filter response fields based on 'fields' query parameter."""
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            fields = request.args.get('fields')
            result = f(*args, **kwargs)
            
            if not fields:
                return result
            
            if isinstance(result, tuple):
                response, status_code = result
            else:
                response, status_code = result, 200
            
            if not isinstance(response, dict):
                return result
            
            field_list = fields.split(',')
            filtered_response = {
                k: v for k, v in response.items()
                if k in field_list
            }
            
            return filtered_response, status_code
        
        return decorated 