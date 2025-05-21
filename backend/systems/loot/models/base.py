"""
Dedicated declarative base for loot system models.

This module provides the SQLAlchemy declarative base used by all loot system models.
"""
from sqlalchemy.ext.declarative import declarative_base

LootBase = declarative_base() 