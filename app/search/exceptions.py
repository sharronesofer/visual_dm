"""Search-related exceptions."""

class SearchError(Exception):
    """Base class for search-related errors."""
    pass

class ConfigurationError(SearchError):
    """Error in search configuration."""
    pass

class ConnectionError(SearchError):
    """Error connecting to search backend."""
    pass

class IndexError(SearchError):
    """Error during indexing operations."""
    pass

class QueryError(SearchError):
    """Error in search query."""
    pass

class CircuitBreakerError(SearchError):
    """Error when circuit breaker is open."""
    pass 