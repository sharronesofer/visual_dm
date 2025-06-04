"""
Memory Database Infrastructure
============================

Technical database implementations for the memory system.
This module contains database adapters and interfaces for memory persistence.
"""

from .memory_database_interface import (
    MemoryDatabaseInterface,
    SQLiteMemoryDatabase,
    PostgreSQLMemoryDatabase,
    create_memory_database,
    get_memory_database,
    set_memory_database
)

__all__ = [
    "MemoryDatabaseInterface",
    "SQLiteMemoryDatabase", 
    "PostgreSQLMemoryDatabase",
    "create_memory_database",
    "get_memory_database",
    "set_memory_database"
] 