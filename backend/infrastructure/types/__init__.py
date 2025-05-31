"""
Type definitions and data structures.
"""

try:
    from .grid import Grid
    from .buildings import *
except ImportError:
    Grid = None

__all__ = [
    'Grid'
]
