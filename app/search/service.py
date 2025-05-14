"""Service layer for search functionality."""

from typing import Dict, List, Optional, Any, Type, TypeVar, Generic
from datetime import datetime
from elasticsearch import NotFoundError

from .client import SearchClient
from .models import (
    EntityType, FacetType, FacetConfig, EntityMapping, 
    FacetValue, FacetResult, SearchResult, ENTITY_MAPPINGS
)
from .exceptions import SearchError, IndexError, CircuitBreakerError
from .cache import SearchCache, CacheKey
from .circuit_breaker import search_breaker
from .pagination import PaginationParams, PaginatedResponse, CursorPaginationParams, OffsetPaginationParams
from .filters import FilterExpression, FilterParser, parse_filter_expression, apply_filters
from .entities import Entity

T = TypeVar('T')

class SearchableEntity(Generic[T]):
    """Base class for entities that can be searched."""
    
    def __init__(
        self,
        entity_type: EntityType,
        mapping: EntityMapping,
        model_cls: Type[T]
    ):
        self.entity_type = entity_type
        self.mapping = mapping
        self.model_cls = model_cls

    def to_doc(self, instance: T) -> Dict[str, Any]:
        """Convert entity instance to search document."""
        raise NotImplementedError
    
    def from_doc(self, doc: Dict[str, Any]) -> T:
        """Create entity instance from search document."""
        raise NotImplementedError

    def paginate_results(
        self,
        items: List[T],
        total: int,
        params: PaginationParams
    ) -> PaginatedResponse[T]:
        """Create a paginated response from search results.
        
        Args:
            items: List of items for the current page
            total: Total number of items across all pages
            params: Pagination parameters
            
        Returns:
            A PaginatedResponse containing the items and pagination metadata
        """
        return PaginatedResponse.create(
            items=items,
            total=total,
            params=params
        )

class SearchService:
    """Service for handling search operations."""

    def __init__(self):
        self.cache = SearchCache()
        self.client = SearchClient()
        self.entities = {}
        
        # Register default entity types
        for entity_type in EntityType:
            if entity_type in ENTITY_MAPPINGS:
                self.register_entity(
                    SearchableEntity(
                        entity_type=entity_type,
                        mapping=ENTITY_MAPPINGS[entity_type],
                        model_cls=Entity
                    )
                )

    @search_breaker
    async def search(
        self,
        query: str,
        entity_type: Optional[EntityType] = None,
        filters: Optional[Dict[str, Any]] = None,
        filter_expression: Optional[FilterExpression] = None,
        pagination: Optional[PaginationParams] = None,
        sort_fields: Optional[List[Dict[str, str]]] = None,
        highlight: bool = True,
        min_score: float = 0.1,
        use_cache: bool = True,
        suggest_filters: bool = False
    ) -> PaginatedResponse[T]:
        """Search for entities with advanced filtering and faceting.
        
        Args:
            query: Search query string
            entity_type: Type of entity to search for
            filters: Filter parameters
            filter_expression: Pre-built filter expression
            pagination: Pagination parameters (offset-based or cursor-based)
            sort_fields: List of sort fields with order (e.g. [{"field": "name", "order": "asc"}])
            highlight: Whether to highlight matching text
            min_score: Minimum relevance score
            use_cache: Whether to use cache
            suggest_filters: Whether to include filter suggestions
            
        Returns:
            Paginated search results with facets, highlights, and filter suggestions
        """
        try:
            # Check cache first
            if use_cache:
                cache_key = CacheKey(
                    query=query,
                    entity_type=entity_type,
                    filters=filters,
                    pagination=pagination,
                    sort_fields=sort_fields
                )
                cached = self.cache.get(cache_key)
                if cached:
                    return cached

            # Build search query
            search_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["name^2", "description", "tags^1.5"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ],
                        "filter": []
                    }
                },
                "min_score": min_score,
                "track_total_hits": True  # Always track total hits for accurate counts
            }

            # Add entity type filter
            if entity_type:
                search_query["query"]["bool"]["filter"].append({
                    "term": {"type": entity_type.value}
                })

            # Add custom filters
            if filters:
                filter_expressions = [
                    parse_filter_expression(field, filter_data)
                    for field, filter_data in filters.items()
                ]
                for expr in filter_expressions:
                    search_query["query"]["bool"]["filter"].append(
                        FilterParser.build_es_query(expr)
                    )

            # Add highlighting if requested
            if highlight:
                search_query["highlight"] = {
                    "fields": {
                        "name": {"number_of_fragments": 0},
                        "description": {"number_of_fragments": 2},
                        "tags": {"number_of_fragments": 0}
                    },
                    "pre_tags": ["<em>"],
                    "post_tags": ["</em>"]
                }

            # Add sorting with multiple fields
            if sort_fields:
                search_query["sort"] = [
                    {field["field"]: {"order": field.get("order", "desc")}}
                    for field in sort_fields
                ]
            else:
                # Default sorting by _score and _id for consistent cursor pagination
                search_query["sort"] = [
                    {"_score": {"order": "desc"}},
                    {"_id": {"order": "asc"}}
                ]

            # Handle pagination
            search_params = {}
            
            if pagination:
                if isinstance(pagination, CursorPaginationParams):
                    # Cursor-based pagination
                    search_params["size"] = pagination.limit
                    
                    if pagination.cursor:
                        try:
                            sort_values = CursorPaginationParams.decode_cursor(pagination.cursor)
                            search_query["search_after"] = [
                                sort_values[field["field"]] 
                                for field in (sort_fields or [{"field": "_score"}, {"field": "_id"}])
                            ]
                        except ValueError as e:
                            raise SearchError(f"Invalid cursor: {str(e)}")
                            
                else:
                    # Offset-based pagination
                    search_params.update({
                        "size": pagination.limit,
                        "from_": pagination.offset
                    })
            else:
                # Default pagination
                search_params["size"] = 20

            # Add aggregations for faceted search
            search_query["aggs"] = self._build_aggregations(entity_type, filters)

            # Add filter suggestions if requested
            if suggest_filters:
                search_query["suggest"] = self._build_filter_suggestions(query, entity_type)

            # Execute search
            response = await self.client.search(
                index=str(entity_type) if entity_type else "_all",
                body=search_query,
                **search_params
            )

            # Process results
            hits = response["hits"]["hits"]
            total = response["hits"]["total"]["value"]
            
            # Convert hits to entity instances
            items = []
            for hit in hits:
                entity = self.entities[EntityType(hit["_source"]["type"])]
                item = entity.from_doc(hit["_source"])
                
                # Add highlight data if available
                if highlight and "highlight" in hit:
                    setattr(item, "highlights", hit["highlight"])
                
                items.append(item)

            # Create paginated response
            if pagination:
                if isinstance(pagination, CursorPaginationParams):
                    result = PaginatedResponse.create_cursor_based(
                        items=items,
                        total=total,
                        params=pagination,
                        sort_fields=sort_fields or [{"field": "_score"}, {"field": "_id"}],
                        prev_cursor=pagination.cursor
                    )
                else:
                    result = PaginatedResponse.create_offset_based(
                        items=items,
                        total=total,
                        params=pagination
                    )
            else:
                # Default to offset-based pagination
                result = PaginatedResponse.create_offset_based(
                    items=items,
                    total=total,
                    params=OffsetPaginationParams()
                )

            # Add facets if aggregations were requested
            if "aggregations" in response:
                result.facets = self._parse_aggregations(
                    entity_type,
                    response["aggregations"],
                    filters
                )

            # Add filter suggestions if requested
            if suggest_filters and "suggest" in response:
                result.filter_suggestions = self._parse_filter_suggestions(
                    response["suggest"]
                )

            # Cache the result
            if use_cache:
                self.cache.set(cache_key, result)

            return result

        except Exception as e:
            raise SearchError(f"Search failed: {str(e)}") from e

    def _build_aggregations(
        self,
        entity_type: Optional[EntityType],
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build aggregation queries for faceted search.
        
        Args:
            entity_type: Type of entity to get facets for
            filters: Current filter values
            
        Returns:
            Elasticsearch aggregation query
        """
        aggs = {}
        
        # Common facets for all entity types
        aggs.update({
            "tags": {
                "terms": {"field": "tags", "size": 20}
            },
            "created_at": {
                "date_histogram": {
                    "field": "created_at",
                    "calendar_interval": "month"
                }
            }
        })
        
        # Entity-specific facets
        if entity_type:
            if entity_type == EntityType.NPC:
                aggs.update({
                    "level": {
                        "range": {
                            "field": "level",
                            "ranges": [
                                {"to": 10},
                                {"from": 10, "to": 20},
                                {"from": 20, "to": 30},
                                {"from": 30}
                            ]
                        }
                    },
                    "faction": {"terms": {"field": "faction"}},
                    "location": {"terms": {"field": "location"}}
                })
            elif entity_type == EntityType.ITEM:
                aggs.update({
                    "rarity": {"terms": {"field": "rarity"}},
                    "category": {"terms": {"field": "category"}},
                    "level_requirement": {
                        "range": {
                            "field": "level_requirement",
                            "ranges": [
                                {"to": 10},
                                {"from": 10, "to": 20},
                                {"from": 20, "to": 30},
                                {"from": 30}
                            ]
                        }
                    }
                })
            elif entity_type == EntityType.LOCATION:
                aggs.update({
                    "region": {"terms": {"field": "region"}},
                    "terrain_type": {"terms": {"field": "terrain_type"}},
                    "danger_level": {
                        "range": {
                            "field": "danger_level",
                            "ranges": [
                                {"to": 2},
                                {"from": 2, "to": 4},
                                {"from": 4, "to": 6},
                                {"from": 6}
                            ]
                        }
                    }
                })
            elif entity_type == EntityType.QUEST:
                aggs.update({
                    "difficulty": {"terms": {"field": "difficulty"}},
                    "status": {"terms": {"field": "status"}}
                })
            elif entity_type == EntityType.FACTION:
                aggs.update({
                    "faction_type": {"terms": {"field": "faction_type"}},
                    "status": {"terms": {"field": "status"}},
                    "influence": {
                        "range": {
                            "field": "influence",
                            "ranges": [
                                {"to": 25},
                                {"from": 25, "to": 50},
                                {"from": 50, "to": 75},
                                {"from": 75}
                            ]
                        }
                    }
                })
        
        return aggs

    def _parse_aggregations(
        self,
        entity_type: Optional[EntityType],
        aggs: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[FacetValue]]:
        """Parse aggregation results into facet values.
        
        Args:
            entity_type: Type of entity
            aggs: Elasticsearch aggregation results
            filters: Current filter values
            
        Returns:
            Dictionary of facet field to list of facet values
        """
        facets = {}
        
        for field, agg in aggs.items():
            if "buckets" in agg:
                facets[field] = [
                    FacetValue(
                        value=bucket["key"],
                        count=bucket["doc_count"],
                        selected=filters and field in filters and str(bucket["key"]) in filters[field]
                    )
                    for bucket in agg["buckets"]
                ]
            elif "ranges" in agg:
                facets[field] = [
                    FacetValue(
                        value=f"{range.get('from', '*')}-{range.get('to', '*')}",
                        count=range["doc_count"],
                        selected=False  # Range selection status needs custom handling
                    )
                    for range in agg["buckets"]
                ]
        
        return facets

    @search_breaker
    def register_entity(self, entity: SearchableEntity) -> None:
        """Register an entity type for searching.
        
        Args:
            entity: SearchableEntity instance
        """
        self.entities[entity.entity_type] = entity
        self.client.create_index(
            str(entity.entity_type),
            entity.mapping.mappings
        )

    @search_breaker
    def index_document(self, entity_type: EntityType, document: T) -> None:
        """Index a document.
        
        Args:
            entity_type: Type of entity
            document: Document to index
            
        Raises:
            IndexError: If indexing fails
            CircuitBreakerError: If circuit breaker is open
        """
        try:
            entity = self.entities[entity_type]
            doc = entity.to_doc(document)
            self.client.index_document(
                str(entity_type),
                doc["id"],
                doc
            )
            
            # Invalidate cache for this entity type
            if self.cache:
                self.cache.invalidate(str(entity_type))
                
        except Exception as e:
            raise IndexError(f"Failed to index document: {str(e)}") from e

    @search_breaker
    def delete_document(self, entity_type: EntityType, doc_id: str) -> None:
        """Delete a document.
        
        Args:
            entity_type: Type of entity
            doc_id: Document ID
            
        Raises:
            IndexError: If deletion fails
            CircuitBreakerError: If circuit breaker is open
        """
        try:
            self.client.delete_document(
                str(entity_type),
                doc_id
            )
            
            # Invalidate cache for this entity type
            if self.cache:
                self.cache.invalidate(str(entity_type))
                
        except Exception as e:
            raise IndexError(f"Failed to delete document: {str(e)}") from e

    @search_breaker
    def health_check(self) -> Dict[str, Any]:
        """Check cluster health.
        
        Returns:
            Health status information
            
        Raises:
            CircuitBreakerError: If circuit breaker is open
        """
        return self.client.health_check()

    def _build_filter_suggestions(
        self,
        query: str,
        entity_type: Optional[EntityType] = None
    ) -> Dict[str, Any]:
        """Build filter suggestions configuration.
        
        Args:
            query: Search query string
            entity_type: Type of entity to get suggestions for
            
        Returns:
            Elasticsearch suggest configuration
        """
        fields = ["name", "tags", "description"]
        if entity_type:
            fields.extend(self.entities[entity_type].mapping.get_suggestable_fields())
            
        return {
            "field_suggestions": {
                "text": query,
                "completion": {
                    "field": "suggest",
                    "size": 5,
                    "skip_duplicates": True,
                    "contexts": {
                        "type": [entity_type.value] if entity_type else []
                    }
                }
            }
        }

    def _parse_filter_suggestions(
        self,
        suggestions: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Parse filter suggestions from response.
        
        Args:
            suggestions: Elasticsearch suggestions response
            
        Returns:
            Dictionary of field names to suggested values
        """
        result = {}
        for suggestion_type, values in suggestions.items():
            field = suggestion_type.replace("_suggestions", "")
            result[field] = [
                option["text"]
                for suggestion in values
                for option in suggestion["options"]
            ]
        return result