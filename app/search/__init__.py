"""
Search package for Visual DM.

This package provides full-text and faceted search capabilities for game entities
using Elasticsearch as the backend search engine.
"""

from .client import SearchClient
from .models import SearchDocument, SearchResult, FacetResult
from .exceptions import SearchError, IndexError
from .init import init_search
from .entities import NPC, Item, Location, Quest
from .service import SearchService, SearchableEntity

__all__ = [
    'SearchClient',
    'SearchDocument',
    'SearchResult',
    'FacetResult',
    'SearchError',
    'IndexError',
    'init_search',
    'NPC',
    'Item',
    'Location',
    'Quest',
    'SearchService',
    'SearchableEntity',
] 