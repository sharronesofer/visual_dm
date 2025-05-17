from pydantic import BaseModel
from typing import List, Any, Optional, Dict

class SearchResponse(BaseModel):
    """
    Schema for search API responses, including optional facets for aggregations.
    """
    results: List[Any]
    total: int
    page: int
    pageSize: int
    facets: Optional[Dict[str, Any]] = None 