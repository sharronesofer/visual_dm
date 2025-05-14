"""Elasticsearch client wrapper for search functionality."""

import logging
from typing import Any, Dict, List, Optional, Union
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk
from datetime import datetime

from .models import SearchDocument, SearchResult, FacetResult, FacetValue
from .exceptions import SearchError, IndexError, QueryError, ConnectionError, ConfigurationError
from .config import INDEX_SETTINGS, ES_SETTINGS

logger = logging.getLogger(__name__)

class SearchClient:
    """Client for interacting with Elasticsearch."""

    def __init__(
        self,
        hosts: Optional[List[str]] = None,
        index_prefix: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs
    ):
        """Initialize the client.
        
        Args:
            hosts: List of Elasticsearch hosts
            index_prefix: Prefix for index names
            username: Optional username for authentication
            password: Optional password for authentication
            **kwargs: Additional arguments passed to Elasticsearch
        """
        self.hosts = hosts or ES_SETTINGS["hosts"]
        self.index_prefix = index_prefix or ES_SETTINGS["index_prefix"]
        self.client = Elasticsearch(
            self.hosts,
            basic_auth=(username, password) if username and password else None,
            **{**ES_SETTINGS, **kwargs}
        )

    def get_index_name(self, entity_type: str) -> str:
        """Get the full index name for an entity type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            Full index name with prefix
        """
        return f"{self.index_prefix}{entity_type}"

    def create_index(
        self,
        entity_type: str,
        mappings: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create an index with mappings.
        
        Args:
            entity_type: Type of entity
            mappings: Index mappings
            settings: Optional index settings
        """
        index_name = self.get_index_name(entity_type)
        try:
            if not self.client.indices.exists(index=index_name):
                # Default settings optimized for game entity search
                default_settings = {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "analysis": {
                        "analyzer": {
                            "game_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": [
                                    "lowercase",
                                    "asciifolding",
                                    "word_delimiter_graph",
                                    "stop",
                                    "snowball"
                                ]
                            }
                        }
                    },
                    "index": {
                        "max_ngram_diff": 7,
                        "highlight": {
                            "max_analyzed_offset": 1000000
                        }
                    }
                }
                
                # Merge with provided settings
                merged_settings = {
                    **(settings or ES_SETTINGS["index"]),
                    **default_settings
                }
                
                self.client.indices.create(
                    index=index_name,
                    mappings=mappings,
                    settings=merged_settings
                )
        except Exception as e:
            raise IndexError(f"Failed to create index: {str(e)}") from e

    def delete_index(self, entity_type: str) -> None:
        """Delete an index.
        
        Args:
            entity_type: Type of entity
        """
        index_name = self.get_index_name(entity_type)
        try:
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
        except Exception as e:
            raise IndexError(f"Failed to delete index: {str(e)}") from e

    def index_document(
        self,
        entity_type: str,
        doc_id: str,
        document: Dict[str, Any]
    ) -> None:
        """Index a single document.
        
        Args:
            entity_type: Type of entity
            doc_id: Document ID
            document: Document data
        """
        index_name = self.get_index_name(entity_type)
        try:
            # Add timestamp fields if not present
            if "created_at" not in document:
                document["created_at"] = datetime.now().isoformat()
            if "updated_at" not in document:
                document["updated_at"] = document["created_at"]
                
            self.client.index(
                index=index_name,
                id=doc_id,
                document=document,
                refresh=True
            )
        except Exception as e:
            raise IndexError(f"Failed to index document: {str(e)}") from e

    def bulk_index(
        self,
        entity_type: str,
        documents: List[Dict[str, Any]],
        chunk_size: int = 500
    ) -> None:
        """Bulk index multiple documents.
        
        Args:
            entity_type: Type of entity
            documents: List of documents to index
            chunk_size: Number of documents per bulk request
        """
        index_name = self.get_index_name(entity_type)
        try:
            now = datetime.now().isoformat()
            actions = []
            
            for doc in documents:
                # Add timestamp fields if not present
                if "created_at" not in doc:
                    doc["created_at"] = now
                if "updated_at" not in doc:
                    doc["updated_at"] = doc["created_at"]
                    
                actions.append({
                    "_index": index_name,
                    "_id": doc["id"],
                    "_source": doc
                })
                
            bulk(
                self.client,
                actions,
                chunk_size=chunk_size,
                refresh=True
            )
        except Exception as e:
            raise IndexError(f"Bulk indexing failed: {str(e)}") from e

    def delete_document(self, entity_type: str, doc_id: str) -> None:
        """Delete a document.
        
        Args:
            entity_type: Type of entity
            doc_id: Document ID
        """
        index_name = self.get_index_name(entity_type)
        try:
            self.client.delete(
                index=index_name,
                id=doc_id,
                refresh=True
            )
        except NotFoundError:
            pass  # Document doesn't exist, that's fine
        except Exception as e:
            raise IndexError(f"Failed to delete document: {str(e)}") from e

    async def search(
        self,
        query: str,
        index: Optional[str] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        aggs: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 10,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        highlight: bool = True,
        min_score: float = 0.1
    ) -> Dict[str, Any]:
        """Execute a search query.
        
        Args:
            query: Search query string
            index: Optional index name (defaults to all indices)
            filters: Optional list of filter clauses
            aggs: Optional aggregation queries
            page: Page number (1-based)
            page_size: Number of results per page
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            highlight: Whether to highlight matches
            min_score: Minimum score for results
            
        Returns:
            Elasticsearch response
        """
        try:
            # Build query
            search_query = {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "name^3",
                                    "description^2",
                                    "tags^2",
                                    # Entity-specific fields
                                    "dialogue^1.5",  # NPC
                                    "category^1.5",  # Item
                                    "region^1.5",    # Location
                                    "objectives^1.5", # Quest
                                    "faction_type^1.5" # Faction
                                ],
                                "type": "best_fields",
                                "tie_breaker": 0.3,
                                "minimum_should_match": "30%",
                                "fuzziness": "AUTO",
                                "prefix_length": 2
                            }
                        }
                    ],
                    "filter": filters or []
                }
            }

            # Build request body
            body = {
                "query": search_query,
                "min_score": min_score,
                "from": (page - 1) * page_size,
                "size": page_size
            }

            # Add sorting
            if sort_by:
                body["sort"] = [
                    {sort_by: {"order": sort_order}},
                    "_score"
                ]

            # Add highlighting
            if highlight:
                body["highlight"] = {
                    "pre_tags": ["<em>"],
                    "post_tags": ["</em>"],
                    "fields": {
                        "name": {"number_of_fragments": 0},
                        "description": {"number_of_fragments": 2},
                        "tags": {"number_of_fragments": 0},
                        "dialogue": {"number_of_fragments": 2},
                        "category": {"number_of_fragments": 0},
                        "region": {"number_of_fragments": 0},
                        "objectives": {"number_of_fragments": 2},
                        "faction_type": {"number_of_fragments": 0}
                    }
                }

            # Add aggregations
            if aggs:
                body["aggs"] = aggs

            # Execute search
            response = await self.client.search(
                index=index,
                body=body,
                track_total_hits=True
            )

            return response

        except Exception as e:
            raise SearchError(f"Search failed: {str(e)}") from e

    def health_check(self) -> Dict[str, Any]:
        """Check cluster health.
        
        Returns:
            Cluster health information
        """
        try:
            health = self.client.cluster.health()
            return {
                "status": health["status"],
                "cluster_name": health["cluster_name"],
                "number_of_nodes": health["number_of_nodes"],
                "active_shards": health["active_shards"]
            }
        except Exception as e:
            raise ConnectionError(f"Health check failed: {str(e)}") from e