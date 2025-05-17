from fastapi import Query, HTTPException, Depends
from typing import Optional, List

def validate_search_query(
    q: Optional[str] = Query(None),
    filter: Optional[List[str]] = Query(None),
    sort: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100)
):
    """
    Validates search query parameters for type, allowed values, and limits.
    Raises HTTPException(400) for invalid input.
    """
    # Example: Add more validation logic as needed
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if pageSize < 1 or pageSize > 100:
        raise HTTPException(status_code=400, detail="pageSize must be between 1 and 100")
    # Add more filter/sort validation as needed
    return {
        "q": q,
        "filter": filter,
        "sort": sort,
        "page": page,
        "pageSize": pageSize
    } 