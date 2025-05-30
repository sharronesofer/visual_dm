"""Tests for region management system."""

import pytest
import numpy as np
from ..region import Region, RegionProperties, RegionManager

def test_region_properties():
    """Test region properties initialization."""
    props = RegionProperties(
        name="Test Region",
        description="A test region",
        color=(255, 0, 0),
        border_color=(0, 0, 0),
        z_index=1
    )
    
    assert props.name == "Test Region"
    assert props.description == "A test region"
    assert props.color == (255, 0, 0)
    assert props.border_color == (0, 0, 0)
    assert props.z_index == 1
    assert props.is_visible is True
    assert props.is_selected is False
    assert props.is_hovered is False

def test_region_initialization():
    """Test region initialization."""
    props = RegionProperties(
        name="Test Region",
        description="A test region",
        color=(255, 0, 0),
        border_color=(0, 0, 0)
    )
    
    boundary = [(0, 0), (1, 0), (1, 1), (0, 1)]
    region = Region("test-region", boundary, props)
    
    assert region.id == "test-region"
    assert len(list(region.boundary.exterior.coords)) == len(boundary) + 1  # +1 for closing point
    assert region.properties == props
    assert region._bbox == (0, 0, 1, 1)

def test_region_contains_point():
    """Test point containment check."""
    props = RegionProperties(
        name="Test Region",
        description="A test region",
        color=(255, 0, 0),
        border_color=(0, 0, 0)
    )
    
    boundary = [(0, 0), (2, 0), (2, 2), (0, 2)]
    region = Region("test-region", boundary, props)
    
    # Test points inside
    assert region.contains_point((1, 1)) is True
    assert region.contains_point((0.5, 0.5)) is True
    
    # Test points outside
    assert region.contains_point((3, 3)) is False
    assert region.contains_point((-1, -1)) is False

def test_region_intersects_viewport():
    """Test viewport intersection check."""
    props = RegionProperties(
        name="Test Region",
        description="A test region",
        color=(255, 0, 0),
        border_color=(0, 0, 0)
    )
    
    boundary = [(0, 0), (2, 0), (2, 2), (0, 2)]
    region = Region("test-region", boundary, props)
    
    # Test intersecting viewports
    assert region.intersects_viewport((-1, -1, 1, 1)) is True  # Partial overlap
    assert region.intersects_viewport((-2, -2, 3, 3)) is True  # Full containment
    assert region.intersects_viewport((1, 1, 3, 3)) is True  # Partial overlap
    
    # Test non-intersecting viewports
    assert region.intersects_viewport((3, 3, 4, 4)) is False
    assert region.intersects_viewport((-2, -2, -1, -1)) is False

def test_region_get_render_data():
    """Test render data generation."""
    props = RegionProperties(
        name="Test Region",
        description="A test region",
        color=(255, 0, 0),
        border_color=(0, 0, 0),
        z_index=1
    )
    
    boundary = [(0, 0), (1, 0), (1, 1), (0, 1)]
    region = Region("test-region", boundary, props)
    
    render_data = region.get_render_data()
    
    assert render_data["id"] == "test-region"
    assert len(render_data["boundary"]) == len(boundary) + 1  # +1 for closing point
    assert render_data["color"] == (255, 0, 0)
    assert render_data["border_color"] == (0, 0, 0)
    assert render_data["z_index"] == 1
    assert render_data["is_visible"] is True
    assert render_data["is_selected"] is False
    assert render_data["is_hovered"] is False

def test_region_manager():
    """Test region manager functionality."""
    manager = RegionManager()
    
    # Create test regions
    props1 = RegionProperties(
        name="Region 1",
        description="First test region",
        color=(255, 0, 0),
        border_color=(0, 0, 0),
        z_index=1
    )
    
    props2 = RegionProperties(
        name="Region 2",
        description="Second test region",
        color=(0, 255, 0),
        border_color=(0, 0, 0),
        z_index=2
    )
    
    region1 = Region("region1", [(0, 0), (1, 0), (1, 1), (0, 1)], props1)
    region2 = Region("region2", [(2, 2), (3, 2), (3, 3), (2, 3)], props2)
    
    # Test adding regions
    manager.add_region(region1)
    manager.add_region(region2)
    
    assert len(manager.regions) == 2
    assert "region1" in manager.regions
    assert "region2" in manager.regions
    
    # Test getting regions in viewport
    viewport1 = (-1, -1, 2, 2)  # Contains region1
    viewport2 = (1.5, 1.5, 3.5, 3.5)  # Contains region2
    viewport3 = (0, 0, 3, 3)  # Contains both regions
    
    regions_in_vp1 = manager.get_regions_in_viewport(viewport1)
    regions_in_vp2 = manager.get_regions_in_viewport(viewport2)
    regions_in_vp3 = manager.get_regions_in_viewport(viewport3)
    
    assert len(regions_in_vp1) == 1
    assert len(regions_in_vp2) == 1
    assert len(regions_in_vp3) == 2
    
    # Test getting region at point
    region_at_point1 = manager.get_region_at_point((0.5, 0.5))
    region_at_point2 = manager.get_region_at_point((2.5, 2.5))
    region_at_point3 = manager.get_region_at_point((1.5, 1.5))
    
    assert region_at_point1 == region1
    assert region_at_point2 == region2
    assert region_at_point3 is None
    
    # Test updating region property
    manager.update_region_property("region1", "is_visible", False)
    assert manager.regions["region1"].properties.is_visible is False
    
    # Test removing region
    manager.remove_region("region1")
    assert len(manager.regions) == 1
    assert "region1" not in manager.regions
    assert "region2" in manager.regions 