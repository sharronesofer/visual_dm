"""
Authentication System Base Module

This module provides base classes and utilities for the authentication system.
Re-exports from models.base for convenience.
"""

from .models.base import AuthBaseModel, Base

__all__ = ["AuthBaseModel", "Base"] 