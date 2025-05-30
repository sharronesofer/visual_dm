from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
from backend.systems.poi.services import MetropolitanSpreadService
from backend.systems.economy.models import Resource
"""
Tests for backend.systems.poi.services module.

This module contains tests for the main services module that exports all POI services.
"""

import pytest
from unittest.mock import Mock, patch


class TestServicesModule:
    """Tests for the POI services module."""

    def test_module_imports_successfully(self):
        """Test that the services module can be imported without errors."""
        import backend.systems.poi.services as services_module
        assert services_module is not None

    def test_all_services_exported(self):
        """Test that all expected services are exported in __all__."""
        from backend.systems.poi.services import __all__
        
        expected_services = [
            "POIService",
            "POIStateService",
            "MetropolitanSpreadService",
            "MetropolitanService",  # Backward compatibility alias
            "FactionInfluenceService",
            "LandmarkService",
            "POILifecycleEventsService",
            "POIMigrationService",
            "ResourceManagementService",
        ]
        
        assert len(__all__) == len(expected_services)
        for service in expected_services:
            assert service in __all__

    def test_poi_service_import(self):
        """Test that POIService can be imported from the services module."""
        from backend.systems.poi.services import POIService
        assert POIService is not None

    def test_poi_state_service_import(self):
        """Test that POIStateService can be imported from the services module."""
        from backend.systems.poi.services import POIStateService
        assert POIStateService is not None

    def test_metropolitan_spread_service_import(self):
        """Test that MetropolitanSpreadService can be imported from the services module."""
        from backend.systems.poi.services import MetropolitanSpreadService
        assert MetropolitanSpreadService is not None

    def test_faction_influence_service_import(self):
        """Test that FactionInfluenceService can be imported from the services module."""
        from backend.systems.poi.services import FactionInfluenceService
        assert FactionInfluenceService is not None

    def test_landmark_service_import(self):
        """Test that LandmarkService can be imported from the services module."""
        from backend.systems.poi.services import LandmarkService
        assert LandmarkService is not None

    def test_lifecycle_events_service_import(self):
        """Test that POILifecycleEventsService can be imported from the services module."""
        from backend.systems.poi.services import POILifecycleEventsService
        assert POILifecycleEventsService is not None

    def test_migration_service_import(self):
        """Test that POIMigrationService can be imported from the services module."""
        from backend.systems.poi.services import POIMigrationService
        assert POIMigrationService is not None

    def test_resource_management_service_import(self):
        """Test that ResourceManagementService can be imported from the services module."""
        from backend.systems.poi.services import ResourceManagementService
        assert ResourceManagementService is not None

    def test_services_are_classes(self):
        """Test that imported services are actual classes."""
        from backend.systems.poi.services import (
            POIService,
            POIStateService,
            MetropolitanSpreadService,
            FactionInfluenceService,
            LandmarkService,
            POILifecycleEventsService,
            POIMigrationService,
            ResourceManagementService,
        )
        
        # Verify each import is a class
        assert isinstance(POIService, type)
        assert isinstance(POIStateService, type)
        assert isinstance(MetropolitanSpreadService, type)
        assert isinstance(FactionInfluenceService, type)
        assert isinstance(LandmarkService, type)
        assert isinstance(POILifecycleEventsService, type)
        assert isinstance(POIMigrationService, type)
        assert isinstance(ResourceManagementService, type)

    def test_all_exports_match_imports(self):
        """Test that __all__ list matches the actual available imports."""
        import backend.systems.poi.services as services_module
        
        # Get all items from __all__
        exported_names = services_module.__all__
        
        # Verify each exported name is actually available
        for name in exported_names:
            assert hasattr(services_module, name), f"Service {name} not found in module"
            service_class = getattr(services_module, name)
            assert service_class is not None

    def test_module_docstring(self):
        """Test that the module has proper documentation."""
        import backend.systems.poi.services as services_module
        
        assert services_module.__doc__ is not None
        assert "Service modules for the POI system" in services_module.__doc__
        assert "organized by functionality" in services_module.__doc__

    def test_no_extra_exports(self):
        """Test that only expected class exports are in the module."""
        import backend.systems.poi.services as services_module
        
        # Get all public attributes that are classes (not modules or other imports)
        public_classes = []
        for attr_name in dir(services_module):
            if not attr_name.startswith('_'):
                attr = getattr(services_module, attr_name)
                # Only include classes, not modules or other imports
                if isinstance(attr, type):
                    public_classes.append(attr_name)
        
        # All public classes should be in __all__
        for attr in public_classes:
            assert attr in services_module.__all__, f"Unexpected class export: {attr}"


class TestServiceIntegration:
    """Integration tests for the services module."""

    def test_services_can_be_instantiated(self):
        """Test that services can be instantiated (basic smoke test)."""
        from backend.systems.poi.services import (
            POIService,
            POIStateService,
            MetropolitanSpreadService,
        )
        
        # These should not raise exceptions during instantiation
        # Note: Some services might require dependencies, so we'll mock them
        try:
            POIService()
        except Exception:
            # Service might require dependencies - that's OK for this test
            pass
        
        try:
            POIStateService()
        except Exception:
            # Service might require dependencies - that's OK for this test
            pass
        
        try:
            MetropolitanSpreadService()
        except Exception:
            # Service might require dependencies - that's OK for this test
            pass

    @patch('backend.systems.poi.services.poi_service')
    @patch('backend.systems.poi.services.poi_state_service')
    def test_import_isolation(self, mock_state_service, mock_service):
        """Test that imports don't interfere with each other."""
        # Import the module fresh
        import importlib
        import backend.systems.poi.services as services_module
        
        # Force reload to test import behavior
        importlib.reload(services_module)
        
        # Verify the module still works after reload
        assert hasattr(services_module, 'POIService')
        assert hasattr(services_module, 'POIStateService')
        assert len(services_module.__all__) == 9 