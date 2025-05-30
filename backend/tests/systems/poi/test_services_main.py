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
Tests for backend.systems.poi.services

This module contains tests for the main POI services module that centralizes
all service exports.
"""

import pytest
from backend.systems.poi import services


class TestMainServicesModule: pass
    """Tests for the main POI services module."""

    def test_module_imports_successfully(self): pass
        """Test that the services module imports successfully."""
        assert services is not None

    def test_module_has_docstring(self): pass
        """Test that the module has a proper docstring."""
        assert services.__doc__ is not None
        assert "Service modules for the POI system" in services.__doc__

    def test_all_services_exported(self): pass
        """Test that all expected services are exported in __all__."""
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
        
        assert hasattr(services, '__all__')
        assert services.__all__ == expected_services

    def test_poi_service_import(self): pass
        """Test that POIService can be imported."""
        assert hasattr(services, 'POIService')
        assert services.POIService is not None

    def test_poi_state_service_import(self): pass
        """Test that POIStateService can be imported."""
        assert hasattr(services, 'POIStateService')
        assert services.POIStateService is not None

    def test_metropolitan_spread_service_import(self): pass
        """Test that MetropolitanSpreadService can be imported."""
        assert hasattr(services, 'MetropolitanSpreadService')
        assert services.MetropolitanSpreadService is not None

    def test_faction_influence_service_import(self): pass
        """Test that FactionInfluenceService can be imported."""
        assert hasattr(services, 'FactionInfluenceService')
        assert services.FactionInfluenceService is not None

    def test_landmark_service_import(self): pass
        """Test that LandmarkService can be imported."""
        assert hasattr(services, 'LandmarkService')
        assert services.LandmarkService is not None

    def test_lifecycle_events_service_import(self): pass
        """Test that POILifecycleEventsService can be imported."""
        assert hasattr(services, 'POILifecycleEventsService')
        assert services.POILifecycleEventsService is not None

    def test_migration_service_import(self): pass
        """Test that POIMigrationService can be imported."""
        assert hasattr(services, 'POIMigrationService')
        assert services.POIMigrationService is not None

    def test_resource_management_service_import(self): pass
        """Test that ResourceManagementService can be imported."""
        assert hasattr(services, 'ResourceManagementService')
        assert services.ResourceManagementService is not None

    def test_services_are_classes(self): pass
        """Test that all exported services are classes."""
        for service_name in services.__all__: pass
            service_class = getattr(services, service_name)
            assert isinstance(service_class, type), f"{service_name} should be a class"

    def test_all_exports_match_imports(self): pass
        """Test that all items in __all__ are actually available."""
        for service_name in services.__all__: pass
            assert hasattr(services, service_name), f"{service_name} not found in module"

    def test_no_extra_exports(self): pass
        """Test that no extra services are exported beyond __all__."""
        # Get all public attributes that are classes (not modules or other imports)
        public_classes = []
        for attr_name in dir(services): pass
            if not attr_name.startswith('_'): pass
                attr = getattr(services, attr_name)
                # Only include classes, not modules or other imports
                if isinstance(attr, type): pass
                    public_classes.append(attr_name)
                    
        # All public classes should be in __all__
        for attr in public_classes: pass
            assert attr in services.__all__, f"Unexpected class export: {attr}"


class TestServiceImportPaths: pass
    """Tests for service import paths and structure."""

    def test_import_paths_are_correct(self): pass
        """Test that services can be imported from their expected paths."""
        # Test direct imports work
        from backend.systems.poi.services.poi_service import POIService
        from backend.systems.poi.services.poi_state_service import POIStateService
        from backend.systems.poi.services.metropolitan_spread_service import MetropolitanSpreadService
        from backend.systems.poi.services.faction_influence_service import FactionInfluenceService
        from backend.systems.poi.services.landmark_service import LandmarkService
        from backend.systems.poi.services.lifecycle_events_service import POILifecycleEventsService
        from backend.systems.poi.services.migration_service import POIMigrationService
        from backend.systems.poi.services.resource_management_service import ResourceManagementService
        
        # All imports should succeed without error
        assert POIService is not None
        assert POIStateService is not None
        assert MetropolitanSpreadService is not None
        assert FactionInfluenceService is not None
        assert LandmarkService is not None
        assert POILifecycleEventsService is not None
        assert POIMigrationService is not None
        assert ResourceManagementService is not None

    def test_imported_services_match_source_classes(self): pass
        """Test that imported services match their source classes."""
        from backend.systems.poi.services.poi_service import POIService as SourcePOIService
        from backend.systems.poi.services.poi_state_service import POIStateService as SourcePOIStateService
        
        # Test that the imported classes are the same as the source classes
        assert services.POIService is SourcePOIService
        assert services.POIStateService is SourcePOIStateService


class TestServiceIntegration: pass
    """Tests for service integration and functionality."""

    def test_services_can_be_instantiated_from_main_module(self): pass
        """Test that services can be instantiated from the main module."""
        # Test that we can access class methods (static methods don't require instantiation)
        assert hasattr(services.POIService, 'create_poi')
        assert hasattr(services.POIStateService, 'transition_state')
        assert hasattr(services.FactionInfluenceService, 'calculate_regional_influence')
        assert hasattr(services.LandmarkService, 'add_landmark')
        assert hasattr(services.POILifecycleEventsService, 'add_event')
        assert hasattr(services.POIMigrationService, 'calculate_migration_factors')
        assert hasattr(services.ResourceManagementService, 'calculate_production')

    def test_import_isolation(self): pass
        """Test that importing from main module doesn't cause circular imports."""
        # This test passes if no ImportError is raised
        from backend.systems.poi.services import POIService, POIStateService
        from backend.systems.poi.services import MetropolitanSpreadService, FactionInfluenceService
        from backend.systems.poi.services import LandmarkService, POILifecycleEventsService
        from backend.systems.poi.services import POIMigrationService, ResourceManagementService
        
        # All imports should work without circular import issues
        assert POIService is not None
        assert POIStateService is not None
        assert MetropolitanSpreadService is not None
        assert FactionInfluenceService is not None
        assert LandmarkService is not None
        assert POILifecycleEventsService is not None
        assert POIMigrationService is not None
        assert ResourceManagementService is not None 