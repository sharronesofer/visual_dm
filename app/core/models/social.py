"""
Social interaction models for tracking character relationships and interactions.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Float, Table, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

# Remove the character_relationships association table and CharacterRelationship model entirely from this file 