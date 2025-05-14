"""
Shared database base and SQLAlchemy instance.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

# Shared SQLAlchemy instance

db = SQLAlchemy()

# Shared declarative base for non-Flask models
Base = declarative_base() 