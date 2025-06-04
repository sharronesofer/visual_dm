"""
Memory Categories - Business Logic

This module defines the canonical memory categorization system for the business logic layer.
It imports from the infrastructure layer but exposes a simplified business interface.
"""

# Import from infrastructure
from backend.infrastructure.memory_utils.memory_categorization import (
    MemoryCategory,
    MemoryCategoryInfo,
    MEMORY_CATEGORY_CONFIG,
    get_category_info,
    get_all_categories,
    get_permanent_categories,
    get_decay_categories,
    categorize_memory_content
)

# Re-export for business logic layer
__all__ = [
    "MemoryCategory",
    "MemoryCategoryInfo", 
    "MEMORY_CATEGORY_CONFIG",
    "get_category_info",
    "get_all_categories",
    "get_permanent_categories",
    "get_decay_categories",
    "categorize_memory_content"
] 