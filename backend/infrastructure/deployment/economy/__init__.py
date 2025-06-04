"""
Economy Deployment Infrastructure

This module contains deployment infrastructure for the economy system,
separated from business logic per architectural guidelines.
"""

from .economy_deployment import EconomyService

__all__ = ["EconomyService"]
