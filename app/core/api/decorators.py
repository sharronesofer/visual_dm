"""
Decorators for enforcing API patterns and handling common functionality.
"""

from functools import wraps
from typing import Callable, Dict, Any, Optional, Type, Union
from flask import request, jsonify, current_app, g
from pydantic import BaseModel, ValidationError

from .patterns import (
    PaginationParams,
    FilterParams,
    SortParams,
    BaseResponse,
    ErrorResponse,
    get_rate_limit,
    get_cache_timeout
)
from ..middleware.rate_limit import RateLimiter
from ..middleware.cache import APICache
from app.core.models.api_key import APIKey

def validate_request_schema(schema: Type[BaseModel]) -> Callable:
    """Validate request data against a Pydantic schema."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                # Get request data based on content type
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict()

                # Validate data against schema
                validated_data = schema(**data)
                g.validated_data = validated_data

                return f(*args, **kwargs)
            except ValidationError as e:
                return ErrorResponse(
                    error="Validation error",
                    error_code="VALIDATION_ERROR",
                    details=e.errors()
                ).dict(), 422
        return wrapped
    return decorator

def paginate_results() -> Callable:
    """Handle pagination for list endpoints."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                # Validate pagination parameters
                params = PaginationParams(
                    page=request.args.get('page', 1, type=int),
                    per_page=request.args.get('per_page', 20, type=int)
                )

                # Store pagination params in context
                g.pagination = params

                # Call the handler
                result = f(*args, **kwargs)

                # If the handler returned a tuple, extract the data and status
                if isinstance(result, tuple):
                    data, status = result
                else:
                    data, status = result, 200

                # Calculate pagination metadata
                total_items = len(data) if isinstance(data, list) else 0
                total_pages = (total_items + params.per_page - 1) // params.per_page

                # Return paginated response
                return BaseResponse(
                    data=data,
                    meta={
                        "page": params.page,
                        "per_page": params.per_page,
                        "total_pages": total_pages,
                        "total_items": total_items
                    }
                ).dict(), status

            except ValidationError as e:
                return ErrorResponse(
                    error="Invalid pagination parameters",
                    error_code="INVALID_PAGINATION",
                    details=e.errors()
                ).dict(), 400
        return wrapped
    return decorator

def apply_filters() -> Callable:
    """Handle filtering for list endpoints."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                # Validate filter parameters
                filters = FilterParams(
                    search=request.args.get('search'),
                    status=request.args.get('status'),
                    created_after=request.args.get('created_after'),
                    created_before=request.args.get('created_before'),
                    tags=request.args.getlist('tags')
                )

                # Store filters in context
                g.filters = filters

                return f(*args, **kwargs)
            except ValidationError as e:
                return ErrorResponse(
                    error="Invalid filter parameters",
                    error_code="INVALID_FILTERS",
                    details=e.errors()
                ).dict(), 400
        return wrapped
    return decorator

def apply_sorting() -> Callable:
    """Handle sorting for list endpoints."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                # Validate sorting parameters
                sort_params = SortParams(
                    sort_by=request.args.get('sort_by'),
                    order=request.args.get('order', 'asc')
                )

                # Store sort params in context
                g.sort_params = sort_params

                return f(*args, **kwargs)
            except ValidationError as e:
                return ErrorResponse(
                    error="Invalid sorting parameters",
                    error_code="INVALID_SORTING",
                    details=e.errors()
                ).dict(), 400
        return wrapped
    return decorator

def rate_limit(endpoint_type: str = 'default') -> Callable:
    """Apply rate limiting to endpoints."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get rate limit config
            limit_config = get_rate_limit(endpoint_type)
            
            # Initialize rate limiter if not exists
            if not hasattr(current_app, 'rate_limiter'):
                current_app.rate_limiter = RateLimiter(
                    current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
                )

            # Check rate limit
            is_limited, headers = current_app.rate_limiter.is_rate_limited(
                endpoint_type,
                limit_config['requests'],
                limit_config['period']
            )

            if is_limited:
                return ErrorResponse(
                    error="Rate limit exceeded",
                    error_code="RATE_LIMIT_EXCEEDED",
                    details={
                        "retry_after": headers['X-RateLimit-Reset']
                    }
                ).dict(), 429, headers

            # Call the handler
            response = f(*args, **kwargs)

            # Add rate limit headers to response
            if isinstance(response, tuple):
                body, status, *rest = response
                headers.update(rest[0] if rest else {})
                return body, status, headers
            return response, 200, headers

        return wrapped
    return decorator

def cache_response(endpoint_type: str = 'list') -> Callable:
    """Cache API responses."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Initialize cache if not exists
            if not hasattr(current_app, 'api_cache'):
                current_app.api_cache = APICache(
                    current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
                )

            # Get cache timeout
            timeout = get_cache_timeout(endpoint_type)

            # Try to get from cache
            cache_key = current_app.api_cache._generate_cache_key(
                endpoint_type,
                request.path,
                request.args,
                *args,
                **kwargs
            )
            cached = current_app.api_cache.redis.get(cache_key)

            if cached:
                return jsonify(cached), 200

            # Call the handler
            response = f(*args, **kwargs)

            # Cache the response
            if isinstance(response, tuple):
                body, status, *rest = response
                if status == 200:  # Only cache successful responses
                    current_app.api_cache.redis.setex(
                        cache_key,
                        timeout,
                        body
                    )
                return response
            
            # Cache and return the response
            current_app.api_cache.redis.setex(
                cache_key,
                timeout,
                response
            )
            return response

        return wrapped
    return decorator

def handle_errors() -> Callable:
    """Handle common API errors."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ValidationError as e:
                return ErrorResponse(
                    error="Validation error",
                    error_code="VALIDATION_ERROR",
                    details=e.errors()
                ).dict(), 422
            except Exception as e:
                current_app.logger.exception("Unhandled error in API endpoint")
                return ErrorResponse(
                    error="Internal server error",
                    error_code="INTERNAL_ERROR",
                    details={"message": str(e)} if current_app.debug else None
                ).dict(), 500
        return wrapped
    return decorator

def api_endpoint(
    schema: Optional[Type[BaseModel]] = None,
    endpoint_type: str = 'list',
    paginated: bool = False,
    filterable: bool = False,
    sortable: bool = False,
    cache: bool = True,
    rate_limited: bool = True
) -> Callable:
    """Combined decorator for common API endpoint patterns."""
    def decorator(f: Callable) -> Callable:
        # Apply decorators in reverse order (innermost first)
        if schema:
            f = validate_request_schema(schema)(f)
        if paginated:
            f = paginate_results()(f)
        if filterable:
            f = apply_filters()(f)
        if sortable:
            f = apply_sorting()(f)
        if rate_limited:
            f = rate_limit(endpoint_type)(f)
        if cache:
            f = cache_response(endpoint_type)(f)
        
        # Always apply error handling as the outermost decorator
        f = handle_errors()(f)
        
        return f
    return decorator

def validate_response(
    response_model: Optional[Type[BaseModel]] = None,
    status_code: int = APIStatus.SUCCESS.value,
    description: Optional[str] = None,
    include_in_schema: bool = True
) -> Callable:
    """
    Decorator to validate and format API responses.
    
    Args:
        response_model: Expected Pydantic model for the response data
        status_code: Expected HTTP status code for successful responses
        description: Response description for OpenAPI documentation
        include_in_schema: Whether to include this response in OpenAPI schema
        
    Returns:
        Decorated function that validates and formats responses
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Union[Response, JSONResponse]:
            try:
                # Call the original function
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                # Handle direct Response objects
                if isinstance(result, Response):
                    return result
                
                # Handle tuple returns (data, status_code)
                response_data = result
                response_status = status_code
                if isinstance(result, tuple) and len(result) == 2:
                    response_data, response_status = result
                
                # If response is already an APIResponse, just validate and return
                if isinstance(response_data, APIResponse):
                    return JSONResponse(
                        content=response_data.dict(),
                        status_code=response_data.status
                    )
                
                # Validate response data if model provided
                if response_model is not None:
                    try:
                        validated_data = response_model.parse_obj(response_data)
                        response_data = validated_data
                    except ValidationError as e:
                        logger.error(f"Response validation failed: {e.errors()}")
                        error_response = APIResponse.server_error(
                            message="Response validation failed",
                            details={"validation_errors": e.errors()}
                        )
                        return JSONResponse(
                            content=error_response.dict(),
                            status_code=APIStatus.INTERNAL_ERROR.value
                        )
                
                # Create success response
                api_response = APIResponse.success(
                    data=response_data,
                    status_code=response_status
                )
                
                return JSONResponse(
                    content=api_response.dict(),
                    status_code=response_status
                )
                
            except Exception as e:
                logger.exception("Unhandled error in API endpoint")
                error_response = APIResponse.server_error(
                    message=str(e),
                    details={"type": type(e).__name__}
                )
                return JSONResponse(
                    content=error_response.dict(),
                    status_code=APIStatus.INTERNAL_ERROR.value
                )
        
        # Update FastAPI endpoint metadata
        wrapper.__name__ = func.__name__
        if hasattr(func, "__doc__"):
            wrapper.__doc__ = func.__doc__
        if description:
            wrapper.__doc__ = description
            
        # Add response model info for OpenAPI schema
        if include_in_schema:
            wrapper.response_model = APIResponse[response_model] if response_model else APIResponse
            wrapper.response_model_exclude_none = True
            wrapper.status_code = status_code
            
        return wrapper
    return decorator

def require_api_key() -> Callable:
    """Decorator to require a valid API key in the request headers."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return ErrorResponse(
                    error="API key required",
                    error_code="API_KEY_REQUIRED"
                ).dict(), 401
            key_obj = APIKey.query.filter_by(key=api_key, is_active=True).first()
            if not key_obj:
                return ErrorResponse(
                    error="Invalid or inactive API key",
                    error_code="INVALID_API_KEY"
                ).dict(), 403
            g.current_api_key = key_obj
            return f(*args, **kwargs)
        return wrapped
    return decorator 