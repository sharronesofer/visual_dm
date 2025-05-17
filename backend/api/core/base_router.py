"""
Base Router Module

This module provides base router classes and factory functions for creating
consistent RESTful API endpoints across the application.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from typing import List, Dict, Any, Optional, Type, Generic, TypeVar, Callable, Union
from pydantic import BaseModel
import logging
from functools import wraps
from enum import Enum
from ..models.base import BaseEntity, PaginatedList, APIResponse, ErrorDetail, SuccessResponse

# Type variables for generic models
T = TypeVar('T', bound=BaseEntity)  # Entity type
C = TypeVar('C', bound=BaseModel)   # Create model type
U = TypeVar('U', bound=BaseModel)   # Update model type
R = TypeVar('R', bound=BaseModel)   # Response model type

# Configure logger
logger = logging.getLogger(__name__)

class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"

class PaginationParams:
    """Standard pagination parameters"""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
        cursor: Optional[str] = Query(None, description="Cursor for cursor-based pagination")
    ):
        self.page = page
        self.page_size = page_size
        self.cursor = cursor
        self.offset = (page - 1) * page_size

class FilterParams:
    """Standard filter parameters"""
    def __init__(
        self,
        q: Optional[str] = Query(None, description="General search query"),
        sort: Optional[str] = Query(None, description="Sort field (prefix with - for descending)"),
        fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
        expand: Optional[str] = Query(None, description="Comma-separated list of relations to expand"),
    ):
        self.q = q
        
        # Parse sort field and direction
        self.sort_field = None
        self.sort_order = SortOrder.ASC
        if sort:
            if sort.startswith('-'):
                self.sort_field = sort[1:]
                self.sort_order = SortOrder.DESC
            else:
                self.sort_field = sort
        
        # Parse fields to include
        self.fields = fields.split(',') if fields else None
        
        # Parse relations to expand
        self.expand = expand.split(',') if expand else None


def create_api_router(
    prefix: str,
    tags: List[str],
    responses: Dict[int, Dict[str, Any]] = None
) -> APIRouter:
    """Create a new API router with standard configurations"""
    if responses is None:
        responses = {
            400: {"model": ErrorDetail, "description": "Bad Request"},
            401: {"model": ErrorDetail, "description": "Unauthorized"},
            403: {"model": ErrorDetail, "description": "Forbidden"},
            404: {"model": ErrorDetail, "description": "Not Found"},
            500: {"model": ErrorDetail, "description": "Internal Server Error"}
        }
    
    return APIRouter(
        prefix=prefix,
        tags=tags,
        responses=responses
    )


class BaseResourceRouter(Generic[T, C, U, R]):
    """Base class for resource routers, implementing standard CRUD operations"""
    
    def __init__(
        self,
        router: APIRouter,
        prefix: str,
        resource_name: str,
        service: Any,  # Should be a service class for the resource
        response_model: Type[R],
        create_model: Type[C],
        update_model: Type[U],
        paginated_response_model: Type[PaginatedList[R]] = None,
        get_all_responses: Dict[int, Dict[str, Any]] = None,
        get_one_responses: Dict[int, Dict[str, Any]] = None,
        create_responses: Dict[int, Dict[str, Any]] = None,
        update_responses: Dict[int, Dict[str, Any]] = None,
        delete_responses: Dict[int, Dict[str, Any]] = None,
    ):
        """
        Initialize the base resource router with resource-specific parameters.
        
        Args:
            router: The FastAPI router to add endpoints to
            prefix: The URL prefix for this resource (e.g., /api/v1/users)
            resource_name: The name of the resource (e.g., "user")
            service: The service class providing data access methods
            response_model: The Pydantic model for resource responses
            create_model: The Pydantic model for creating resources
            update_model: The Pydantic model for updating resources
            paginated_response_model: The model for paginated list responses
            get_all_responses: Response documentation for get_all endpoint
            get_one_responses: Response documentation for get_one endpoint
            create_responses: Response documentation for create endpoint
            update_responses: Response documentation for update endpoint
            delete_responses: Response documentation for delete endpoint
        """
        self.router = router
        self.prefix = prefix
        self.resource_name = resource_name
        self.service = service
        self.response_model = response_model
        self.create_model = create_model
        self.update_model = update_model
        
        # Use default paginated response model if not provided
        if paginated_response_model is None:
            self.paginated_response_model = PaginatedList[response_model]
        else:
            self.paginated_response_model = paginated_response_model
            
        # Set up standard responses
        self.get_all_responses = get_all_responses or {}
        self.get_one_responses = get_one_responses or {404: {"description": f"{resource_name.title()} not found"}}
        self.create_responses = create_responses or {201: {"description": f"{resource_name.title()} created"}}
        self.update_responses = update_responses or {
            404: {"description": f"{resource_name.title()} not found"},
            422: {"description": "Validation error"}
        }
        self.delete_responses = delete_responses or {
            404: {"description": f"{resource_name.title()} not found"},
            204: {"description": f"{resource_name.title()} deleted"}
        }
    
    def add_get_all_endpoint(
        self,
        path: str = "",
        response_model_wrapper: Type = APIResponse,
        dependencies: List[Depends] = None,
        custom_params: List[Any] = None,
        operation_id: str = None
    ):
        """Add GET endpoint to retrieve all resources with pagination and filtering"""
        
        if operation_id is None:
            operation_id = f"get_all_{self.resource_name}s"
            
        @self.router.get(
            path,
            response_model=response_model_wrapper[self.paginated_response_model],
            responses=self.get_all_responses,
            dependencies=dependencies,
            operation_id=operation_id
        )
        async def get_all(
            pagination: PaginationParams = Depends(),
            filters: FilterParams = Depends(),
            *args: Any,
            **kwargs: Any
        ):
            """Get all resources with pagination and filtering"""
            try:
                # Custom params are passed to the handler
                if custom_params:
                    for param in custom_params:
                        kwargs.update({param.__name__: param})
                
                # Call the service to get paginated resources
                result = await self.service.get_all(
                    offset=pagination.offset,
                    limit=pagination.page_size,
                    cursor=pagination.cursor,
                    search_query=filters.q,
                    sort_field=filters.sort_field,
                    sort_order=filters.sort_order,
                    fields=filters.fields,
                    expand=filters.expand,
                    **kwargs
                )
                
                # Calculate pagination metadata
                next_page = None
                prev_page = None
                if pagination.page * pagination.page_size < result.get("total", 0):
                    next_page = f"{self.prefix}?page={pagination.page + 1}&page_size={pagination.page_size}"
                if pagination.page > 1:
                    prev_page = f"{self.prefix}?page={pagination.page - 1}&page_size={pagination.page_size}"
                
                # Construct response
                pagination_data = {
                    "items": result.get("items", []),
                    "total": result.get("total", 0),
                    "page": pagination.page,
                    "page_size": pagination.page_size,
                    "next_page": next_page,
                    "prev_page": prev_page
                }
                
                return {"data": pagination_data, "meta": {}}
                
            except Exception as e:
                logger.exception(f"Error getting all {self.resource_name}s: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def add_get_one_endpoint(
        self,
        path: str = "/{id}",
        response_model_wrapper: Type = APIResponse,
        dependencies: List[Depends] = None,
        operation_id: str = None
    ):
        """Add GET endpoint to retrieve a specific resource by ID"""
        
        if operation_id is None:
            operation_id = f"get_{self.resource_name}"
            
        @self.router.get(
            path,
            response_model=response_model_wrapper[self.response_model],
            responses=self.get_one_responses,
            dependencies=dependencies,
            operation_id=operation_id
        )
        async def get_one(
            id: str = Path(..., description=f"The ID of the {self.resource_name}"),
            filters: FilterParams = Depends(),
            *args: Any,
            **kwargs: Any
        ):
            """Get a specific resource by ID"""
            try:
                result = await self.service.get_by_id(
                    id=id,
                    fields=filters.fields,
                    expand=filters.expand,
                    **kwargs
                )
                
                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail=f"{self.resource_name.title()} with ID {id} not found"
                    )
                
                return {"data": result, "meta": {}}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.exception(f"Error getting {self.resource_name} {id}: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def add_create_endpoint(
        self,
        path: str = "",
        response_model_wrapper: Type = APIResponse,
        dependencies: List[Depends] = None,
        operation_id: str = None
    ):
        """Add POST endpoint to create a new resource"""
        
        if operation_id is None:
            operation_id = f"create_{self.resource_name}"
            
        @self.router.post(
            path,
            response_model=response_model_wrapper[self.response_model],
            status_code=201,
            responses=self.create_responses,
            dependencies=dependencies,
            operation_id=operation_id
        )
        async def create(
            data: self.create_model = Body(..., description=f"The {self.resource_name} to create"),
            *args: Any,
            **kwargs: Any
        ):
            """Create a new resource"""
            try:
                result = await self.service.create(data, **kwargs)
                return {"data": result, "meta": {}}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.exception(f"Error creating {self.resource_name}: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def add_update_endpoint(
        self,
        path: str = "/{id}",
        response_model_wrapper: Type = APIResponse,
        dependencies: List[Depends] = None,
        operation_id: str = None
    ):
        """Add PUT endpoint to update a resource"""
        
        if operation_id is None:
            operation_id = f"update_{self.resource_name}"
            
        @self.router.put(
            path,
            response_model=response_model_wrapper[self.response_model],
            responses=self.update_responses,
            dependencies=dependencies,
            operation_id=operation_id
        )
        async def update(
            id: str = Path(..., description=f"The ID of the {self.resource_name}"),
            data: self.update_model = Body(..., description=f"Updated {self.resource_name} data"),
            *args: Any,
            **kwargs: Any
        ):
            """Update a resource"""
            try:
                result = await self.service.update(id, data, **kwargs)
                
                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail=f"{self.resource_name.title()} with ID {id} not found"
                    )
                
                return {"data": result, "meta": {}}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.exception(f"Error updating {self.resource_name} {id}: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def add_patch_endpoint(
        self,
        path: str = "/{id}",
        response_model_wrapper: Type = APIResponse,
        dependencies: List[Depends] = None,
        operation_id: str = None
    ):
        """Add PATCH endpoint to partially update a resource"""
        
        if operation_id is None:
            operation_id = f"patch_{self.resource_name}"
            
        @self.router.patch(
            path,
            response_model=response_model_wrapper[self.response_model],
            responses=self.update_responses,
            dependencies=dependencies,
            operation_id=operation_id
        )
        async def patch(
            id: str = Path(..., description=f"The ID of the {self.resource_name}"),
            data: Dict[str, Any] = Body(..., description=f"Partial {self.resource_name} data to update"),
            *args: Any,
            **kwargs: Any
        ):
            """Partially update a resource"""
            try:
                result = await self.service.patch(id, data, **kwargs)
                
                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail=f"{self.resource_name.title()} with ID {id} not found"
                    )
                
                return {"data": result, "meta": {}}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.exception(f"Error patching {self.resource_name} {id}: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def add_delete_endpoint(
        self,
        path: str = "/{id}",
        response_model: Type = SuccessResponse,
        dependencies: List[Depends] = None,
        operation_id: str = None
    ):
        """Add DELETE endpoint to remove a resource"""
        
        if operation_id is None:
            operation_id = f"delete_{self.resource_name}"
            
        @self.router.delete(
            path,
            response_model=response_model,
            responses=self.delete_responses,
            dependencies=dependencies,
            operation_id=operation_id
        )
        async def delete(
            id: str = Path(..., description=f"The ID of the {self.resource_name}"),
            *args: Any,
            **kwargs: Any
        ):
            """Delete a resource"""
            try:
                result = await self.service.delete(id, **kwargs)
                
                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail=f"{self.resource_name.title()} with ID {id} not found"
                    )
                
                return {"success": True, "message": f"{self.resource_name.title()} deleted successfully"}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.exception(f"Error deleting {self.resource_name} {id}: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def add_standard_endpoints(
        self,
        response_model_wrapper: Type = APIResponse,
        dependencies: List[Depends] = None
    ):
        """Add all standard CRUD endpoints for the resource"""
        self.add_get_all_endpoint(response_model_wrapper=response_model_wrapper, dependencies=dependencies)
        self.add_get_one_endpoint(response_model_wrapper=response_model_wrapper, dependencies=dependencies)
        self.add_create_endpoint(response_model_wrapper=response_model_wrapper, dependencies=dependencies)
        self.add_update_endpoint(response_model_wrapper=response_model_wrapper, dependencies=dependencies)
        self.add_patch_endpoint(response_model_wrapper=response_model_wrapper, dependencies=dependencies)
        self.add_delete_endpoint(dependencies=dependencies)


def create_resource_router(
    router: APIRouter,
    prefix: str,
    resource_name: str,
    service: Any,
    response_model: Type[BaseModel],
    create_model: Type[BaseModel],
    update_model: Type[BaseModel],
    paginated_response_model: Type[PaginatedList] = None
) -> BaseResourceRouter:
    """
    Factory function to create a resource router with standard CRUD endpoints
    
    Args:
        router: The FastAPI router to add endpoints to
        prefix: URL prefix for this resource
        resource_name: Name of the resource (singular)
        service: Service class for the resource
        response_model: Model for resource responses
        create_model: Model for creating resources
        update_model: Model for updating resources
        paginated_response_model: Model for paginated list responses
        
    Returns:
        A configured BaseResourceRouter instance
    """
    resource_router = BaseResourceRouter(
        router=router,
        prefix=prefix,
        resource_name=resource_name,
        service=service,
        response_model=response_model,
        create_model=create_model,
        update_model=update_model,
        paginated_response_model=paginated_response_model
    )
    
    # Add all standard CRUD endpoints
    resource_router.add_standard_endpoints()
    
    return resource_router 