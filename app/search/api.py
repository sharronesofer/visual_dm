"""FastAPI router for search endpoints."""

from typing import Dict, List, Optional, Union, Any, TypeVar, Generic
from fastapi import APIRouter, Depends, HTTPException, Query, Security
from pydantic import BaseModel, Field

from .service import SearchService
from .models import (
    SearchResult, EntityType, FacetValue,
    FacetType, FacetConfig, EntityMapping
)
from .pagination import PaginationParams, PaginatedResponse
from .config import SEARCH_SETTINGS, ES_SETTINGS
from .exceptions import SearchError, ConfigurationError, IndexError, CircuitBreakerError
from .security import (
    SearchPermissions, require_search_read, require_search_write,
    require_search_admin, search_rate_limiter, suggest_rate_limiter,
    index_rate_limiter, bulk_rate_limiter
)
from .filters import (
    FilterExpression, FilterDataType, FilterOperator,
    FilterCondition, parse_filter_params
)

router = APIRouter(prefix="/api/v1/search", tags=["search"])

T = TypeVar('T')

# Response Models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    cluster_name: str
    number_of_nodes: int
    active_shards: int

class GameEntitySearchRequest(BaseModel):
    """Search request parameters for game entities.
    
    Attributes:
        query: Search query string
        entity_type: Type of game entity to search for (NPC, Item, Location, Quest, Faction)
        filters: Filter parameters for entity-specific attributes
        combine_with: How to combine filter conditions
        page: Page number (1-based)
        per_page: Number of items per page
        sort_by: Field to sort by
        sort_order: Sort order ('asc' or 'desc')
        highlight: Whether to highlight matching text in results
        min_score: Minimum relevance score for results
    """
    query: str = Field(..., description="Search query string")
    entity_type: EntityType = Field(..., description="Type of game entity to search for")
    filters: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Filter parameters")
    combine_with: str = Field("and", description="How to combine filter conditions")
    page: Optional[int] = Field(1, ge=1, description="Page number (1-based)")
    per_page: Optional[int] = Field(10, ge=1, le=100, description="Number of items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("asc", description="Sort order ('asc' or 'desc')")
    highlight: Optional[bool] = Field(True, description="Whether to highlight matching text")
    min_score: Optional[float] = Field(0.1, description="Minimum relevance score")

class GameEntitySearchResponse(BaseModel):
    """Search response for game entities.
    
    Attributes:
        items: List of matching entities
        total: Total number of matches
        facets: Faceted search results
        highlights: Text highlights for matches
        suggestions: Search suggestions based on query
    """
    items: List[Dict[str, Any]]
    total: int
    facets: Optional[Dict[str, List[Dict[str, Any]]]] = None
    highlights: Optional[Dict[str, List[str]]] = None
    suggestions: Optional[List[str]] = None

class IndexRequest(BaseModel):
    """Index document request."""
    entity_type: EntityType
    document: Dict[str, Any]

class BulkIndexRequest(BaseModel):
    """Bulk index request."""
    entity_type: EntityType
    documents: List[Dict[str, Any]]

class CircuitBreakerState(BaseModel):
    """Circuit breaker state response."""
    state: str
    failures: int
    last_failure: Optional[str]
    time_to_reset: int

# Dependency to get search service instance
def get_search_service() -> SearchService:
    """Get a configured search service instance."""
    try:
        return SearchService(**ES_SETTINGS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize search service: {e}")

# Field type mappings for each entity type
FIELD_TYPES: Dict[EntityType, Dict[str, FilterDataType]] = {
    EntityType.NPC: {
        "name": FilterDataType.STRING,
        "level": FilterDataType.NUMBER,
        "faction": FilterDataType.STRING,
        "location": FilterDataType.STRING,
        "created_at": FilterDataType.DATE,
        "updated_at": FilterDataType.DATE,
        "tags": FilterDataType.LIST
    },
    EntityType.ITEM: {
        "name": FilterDataType.STRING,
        "rarity": FilterDataType.STRING,
        "category": FilterDataType.STRING,
        "level_requirement": FilterDataType.NUMBER,
        "created_at": FilterDataType.DATE,
        "updated_at": FilterDataType.DATE,
        "tags": FilterDataType.LIST
    },
    EntityType.LOCATION: {
        "name": FilterDataType.STRING,
        "region": FilterDataType.STRING,
        "terrain_type": FilterDataType.STRING,
        "danger_level": FilterDataType.NUMBER,
        "created_at": FilterDataType.DATE,
        "updated_at": FilterDataType.DATE,
        "tags": FilterDataType.LIST
    },
    EntityType.QUEST: {
        "name": FilterDataType.STRING,
        "difficulty": FilterDataType.STRING,
        "status": FilterDataType.STRING,
        "created_at": FilterDataType.DATE,
        "updated_at": FilterDataType.DATE,
        "tags": FilterDataType.LIST
    },
    EntityType.FACTION: {
        "name": FilterDataType.STRING,
        "faction_type": FilterDataType.STRING,
        "status": FilterDataType.STRING,
        "influence": FilterDataType.NUMBER,
        "resources": FilterDataType.OBJECT,
        "territory": FilterDataType.OBJECT,
        "traits": FilterDataType.OBJECT,
        "created_at": FilterDataType.DATE,
        "updated_at": FilterDataType.DATE,
        "tags": FilterDataType.LIST
    }
}

@router.post("/game-entities", response_model=PaginatedResponse[GameEntitySearchResponse])
async def search_game_entities(
    request: GameEntitySearchRequest,
    service: SearchService = Depends(get_search_service),
    _: bool = Depends(require_search_read),
    __: bool = Depends(search_rate_limiter.check_rate_limit)
) -> PaginatedResponse[GameEntitySearchResponse]:
    """Search for game entities with advanced filtering and faceting.
    
    This endpoint provides full-text search across game entities (NPCs, Items,
    Locations, Quests, Factions) with support for:
    - Entity-specific attribute filtering
    - Faceted search results
    - Text highlighting
    - Search suggestions
    - Pagination
    - Custom sorting
    
    Args:
        request: Search request parameters
        service: Search service instance
        
    Returns:
        Paginated search results with facets and highlights
        
    Raises:
        HTTPException: If the search fails or parameters are invalid
    """
    try:
        # Validate entity type
        if request.entity_type not in [
            EntityType.NPC,
            EntityType.ITEM,
            EntityType.LOCATION,
            EntityType.QUEST,
            EntityType.FACTION
        ]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid game entity type: {request.entity_type}"
            )

        # Get field types for the entity
        field_types = FIELD_TYPES.get(request.entity_type)
        if not field_types:
            raise HTTPException(
                status_code=500,
                detail=f"Field types not configured for entity type: {request.entity_type}"
            )

        # Validate filters if present
        if request.filters:
            for field, filter_data in request.filters.items():
                # Check if field exists for entity type
                if field not in field_types:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid filter field for {request.entity_type}: {field}"
                    )

                # Validate operator
                operator = filter_data.get('operator')
                if operator and not any(operator == op.value for op in FilterOperator):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid filter operator: {operator}"
                    )

                # Validate data type
                data_type = filter_data.get('type')
                if data_type and not any(data_type == dt.value for dt in FilterDataType):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid filter data type: {data_type}"
                    )

                # Set data type from field configuration if not provided
                if not data_type:
                    filter_data['type'] = field_types[field].value

        # Create pagination parameters
        pagination = PaginationParams(
            page=request.page,
            limit=request.per_page
        )

        # Perform search with all parameters
        results = await service.search(
            query=request.query,
            entity_type=request.entity_type,
            filters=request.filters,
            filter_expression=None,  # Built by service from filters
            pagination=pagination,
            sort_by=request.sort_by,
            sort_order=request.sort_order,
            highlight=request.highlight,
            min_score=request.min_score,
            use_cache=True
        )
        
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SearchError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check(
    search_service: SearchService = Depends(get_search_service),
    _: bool = Depends(require_search_read)
) -> HealthResponse:
    """Check search cluster health.
    
    Args:
        search_service: Injected search service instance
        
    Returns:
        Health check information
        
    Raises:
        HTTPException: If health check fails or circuit breaker is open
    """
    try:
        health = search_service.health_check()
        return HealthResponse(
            status=health['status'],
            cluster_name=health['cluster_name'],
            number_of_nodes=health['number_of_nodes'],
            active_shards=health['active_primary_shards']
        )
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
            headers={"Retry-After": "60"}
        )
    except SearchError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/circuit-breaker", response_model=CircuitBreakerState)
async def get_circuit_breaker_state(
    search_service: SearchService = Depends(get_search_service),
    _: bool = Depends(require_search_admin)
) -> CircuitBreakerState:
    """Get current state of the circuit breaker.
    
    Args:
        search_service: Injected search service instance
        
    Returns:
        Circuit breaker state information
    """
    from .circuit_breaker import search_breaker
    if not search_breaker:
        raise HTTPException(
            status_code=404,
            detail="Circuit breaker is not enabled"
        )
    return CircuitBreakerState(**search_breaker.get_state())

@router.get("/suggest")
async def suggest(
    query: str = Query(..., description="Partial query to get suggestions for"),
    entity_type: EntityType = Query(..., description="Type of entity to get suggestions for"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of suggestions to return"),
    search_service: SearchService = Depends(get_search_service),
    _: bool = Depends(require_search_read),
    __: bool = Depends(suggest_rate_limiter.check_rate_limit)
) -> List[str]:
    """Get search suggestions based on partial input.
    
    This endpoint provides autocomplete/typeahead functionality by returning
    relevant suggestions based on partial user input.
    
    Args:
        query: Partial query string
        entity_type: Type of entity to get suggestions for
        limit: Maximum number of suggestions to return
        search_service: Injected search service instance
        
    Returns:
        List of suggestion strings
        
    Raises:
        HTTPException: If the suggestion lookup fails
    """
    try:
        # For now, we'll just do a regular search and extract the names
        result = search_service.search(
            query=query,
            entity_type=entity_type,
            pagination=PaginationParams(page=1, limit=limit),
            sort_by="_score",
            highlight=False
        )
        return [doc.name for doc in result.items]
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SearchError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index", status_code=201)
async def index_document(
    request: IndexRequest,
    search_service: SearchService = Depends(get_search_service),
    _: bool = Depends(require_search_write),
    __: bool = Depends(index_rate_limiter.check_rate_limit)
) -> Dict[str, str]:
    """Index a document.
    
    Args:
        request: Index request parameters
        search_service: Injected search service instance
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If indexing fails or circuit breaker is open
    """
    try:
        search_service.index_document(
            entity_type=request.entity_type,
            document=request.document
        )
        return {"message": "Document indexed successfully"}
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
            headers={"Retry-After": "60"}
        )
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", status_code=201)
async def bulk_index(
    request: BulkIndexRequest,
    search_service: SearchService = Depends(get_search_service),
    _: bool = Depends(require_search_write),
    __: bool = Depends(bulk_rate_limiter.check_rate_limit)
) -> Dict[str, str]:
    """Bulk index multiple documents.
    
    Args:
        request: Bulk index request parameters
        search_service: Injected search service instance
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If indexing fails or circuit breaker is open
    """
    try:
        search_service.bulk_index(
            entity_type=request.entity_type,
            documents=request.documents
        )
        return {"message": "Documents indexed successfully"}
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
            headers={"Retry-After": "60"}
        )
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{entity_type}/{doc_id}")
async def delete_document(
    entity_type: EntityType,
    doc_id: str,
    search_service: SearchService = Depends(get_search_service),
    _: bool = Depends(require_search_write)
) -> Dict[str, str]:
    """Delete a document.
    
    Args:
        entity_type: Type of entity to delete
        doc_id: ID of document to delete
        search_service: Injected search service instance
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If deletion fails or circuit breaker is open
    """
    try:
        search_service.delete_document(
            entity_type=entity_type,
            doc_id=doc_id
        )
        return {"message": "Document deleted successfully"}
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
            headers={"Retry-After": "60"}
        )
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{entity_type}")
async def clear_index(
    entity_type: EntityType,
    search_service: SearchService = Depends(get_search_service),
    _: bool = Depends(require_search_admin)
) -> Dict[str, str]:
    """Clear all documents from an index.
    
    Args:
        entity_type: Type of entity index to clear
        search_service: Injected search service instance
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If operation fails or circuit breaker is open
    """
    try:
        search_service.clear_index(entity_type=entity_type)
        return {"message": f"Index {entity_type} cleared successfully"}
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
            headers={"Retry-After": "60"}
        )
    except IndexError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 