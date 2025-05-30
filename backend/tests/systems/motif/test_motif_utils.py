from typing import Any
from typing import Dict
from uuid import UUID
"""
Comprehensive tests for Motif Utils.
These tests focus on improving coverage of utility functions.
"""
from enum import Enum

import pytest
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
import hashlib
import base64
import zlib
import json

from backend.systems.motif.models import (
    Motif,
    MotifCategory, 
    MotifScope, 
    MotifLifecycle,
    LocationInfo,
    MotifEffect
)
from backend.systems.motif.utils import (
    calculate_distance, is_point_in_radius, calculate_motif_influence,
    generate_random_position, clamp_value, lerp, get_cardinal_direction,
    calculate_region_center, get_nearby_regions, validate_coordinates,
    normalize_angle, degrees_to_radians, radians_to_degrees,
    calculate_bearing, point_to_line_distance, is_point_in_polygon,
    calculate_polygon_area, generate_uuid, format_timestamp,
    parse_timestamp, calculate_age_in_days, is_expired,
    safe_divide, calculate_percentage, round_to_precision,
    get_enum_values, validate_enum_value, deep_merge_dicts,
    flatten_dict, unflatten_dict, sanitize_filename,
    truncate_string, count_words, extract_keywords,
    calculate_similarity, normalize_text, validate_json_schema,
    generate_hash, encode_base64, decode_base64,
    compress_string, decompress_string,
    roll_chaos_event,
    generate_motif_name,
    generate_motif_description,
    generate_realistic_duration,
    roll_new_motif,
    estimate_motif_compatibility,
    detect_motif_conflicts,
    get_compatible_motifs,
    motif_to_narrative_context,
    calculate_motif_spread,
    synthesize_motifs,
    get_region_motif_context,
)


class TestMotifUtils:
    """Test utility functions with comprehensive coverage."""

    # ==== Distance and Geometric Calculations ====
    
    def test_calculate_distance_basic(self):
        """Test basic distance calculations."""
        # Test horizontal distance
        assert calculate_distance(0, 0, 3, 0) == 3.0
        
        # Test vertical distance
        assert calculate_distance(0, 0, 0, 4) == 4.0
        
        # Test Pythagorean triple
        assert calculate_distance(0, 0, 3, 4) == 5.0
        
        # Test same point
        assert calculate_distance(10, 20, 10, 20) == 0.0
        
        # Test negative coordinates
        assert calculate_distance(-5, -3, -1, 0) == 5.0

    def test_calculate_distance_edge_cases(self):
        """Test distance calculation edge cases."""
        # Test very large numbers
        result = calculate_distance(0, 0, 1000000, 1000000)
        expected = math.sqrt(2) * 1000000
        assert abs(result - expected) < 0.001
        
        # Test very small numbers
        result = calculate_distance(0, 0, 0.001, 0.001)
        expected = math.sqrt(2) * 0.001
        assert abs(result - expected) < 0.000001

    def test_is_point_in_radius_basic(self):
        """Test basic radius checks."""
        # Point exactly on radius
        assert is_point_in_radius(0, 0, 5, 0, 5.0) is True
        
        # Point inside radius
        assert is_point_in_radius(0, 0, 3, 0, 5.0) is True
        
        # Point outside radius
        assert is_point_in_radius(0, 0, 6, 0, 5.0) is False
        
        # Same point (distance 0)
        assert is_point_in_radius(10, 10, 10, 10, 5.0) is True

    def test_is_point_in_radius_edge_cases(self):
        """Test radius check edge cases."""
        # Zero radius
        assert is_point_in_radius(0, 0, 0, 0, 0.0) is True
        assert is_point_in_radius(0, 0, 1, 0, 0.0) is False
        
        # Very large radius
        assert is_point_in_radius(0, 0, 100, 100, 1000000.0) is True

    def test_calculate_motif_influence(self):
        """Test motif influence calculations."""
        # Test with default falloff
        influence = calculate_motif_influence(5.0, 10.0)
        assert 0 <= influence <= 5.0
        
        # Test at center (distance 0)
        influence = calculate_motif_influence(5.0, 0.0)
        assert influence == 5.0
        
        # Test beyond max distance
        influence = calculate_motif_influence(5.0, 100.0, max_distance=50.0)
        assert influence == 0.0
        
        # Test custom falloff
        influence = calculate_motif_influence(10.0, 5.0, falloff_rate=0.5)
        assert 0 <= influence <= 10.0

    def test_generate_random_position(self):
        """Test random position generation."""
        # Test within bounds
        x, y = generate_random_position(0, 100, 0, 100)
        assert 0 <= x <= 100
        assert 0 <= y <= 100
        
        # Test negative bounds
        x, y = generate_random_position(-50, 50, -25, 75)
        assert -50 <= x <= 50
        assert -25 <= y <= 75
        
        # Test multiple generations are different (probabilistic)
        positions = [generate_random_position(0, 1000, 0, 1000) for _ in range(10)]
        unique_positions = set(positions)
        assert len(unique_positions) > 1  # Very unlikely to get all same positions

    def test_clamp_value(self):
        """Test value clamping."""
        # Test within range
        assert clamp_value(5, 0, 10) == 5
        
        # Test below minimum
        assert clamp_value(-5, 0, 10) == 0
        
        # Test above maximum
        assert clamp_value(15, 0, 10) == 10
        
        # Test at boundaries
        assert clamp_value(0, 0, 10) == 0
        assert clamp_value(10, 0, 10) == 10

    def test_lerp(self):
        """Test linear interpolation."""
        # Test basic interpolation
        assert lerp(0, 10, 0.5) == 5.0
        
        # Test at endpoints
        assert lerp(0, 10, 0.0) == 0.0
        assert lerp(0, 10, 1.0) == 10.0
        
        # Test negative values
        assert lerp(-10, 10, 0.5) == 0.0
        
        # Test beyond range (extrapolation)
        assert lerp(0, 10, 1.5) == 15.0
        assert lerp(0, 10, -0.5) == -5.0

    def test_get_cardinal_direction(self):
        """Test cardinal direction calculation."""
        # Test cardinal directions
        assert get_cardinal_direction(0, 0, 1, 0) == "East"
        assert get_cardinal_direction(0, 0, -1, 0) == "West"
        assert get_cardinal_direction(0, 0, 0, 1) == "North"
        assert get_cardinal_direction(0, 0, 0, -1) == "South"
        
        # Test diagonal directions
        assert get_cardinal_direction(0, 0, 1, 1) == "Northeast"
        assert get_cardinal_direction(0, 0, -1, 1) == "Northwest"
        assert get_cardinal_direction(0, 0, 1, -1) == "Southeast"
        assert get_cardinal_direction(0, 0, -1, -1) == "Southwest"
        
        # Test same point
        assert get_cardinal_direction(0, 0, 0, 0) == "Center"

    def test_calculate_region_center(self):
        """Test region center calculation."""
        # Test simple square region
        points = [(0, 0), (10, 0), (10, 10), (0, 10)]
        center_x, center_y = calculate_region_center(points)
        assert center_x == 5.0
        assert center_y == 5.0
        
        # Test triangle
        points = [(0, 0), (6, 0), (3, 3)]
        center_x, center_y = calculate_region_center(points)
        assert center_x == 3.0
        assert center_y == 1.0
        
        # Test single point
        points = [(5, 5)]
        center_x, center_y = calculate_region_center(points)
        assert center_x == 5.0
        assert center_y == 5.0

    def test_get_nearby_regions(self):
        """Test getting nearby regions."""
        # Mock regions data
        regions = {
            "region1": {"center_x": 0, "center_y": 0},
            "region2": {"center_x": 5, "center_y": 0}, 
            "region3": {"center_x": 15, "center_y": 0}  # Further away
        }
        nearby = get_nearby_regions(0, 0, regions, 10)
        assert "region1" in nearby
        assert "region2" in nearby
        assert "region3" not in nearby  # This region is at distance 15 > 10

    def test_validate_coordinates(self):
        """Test coordinate validation."""
        # Test valid coordinates
        assert validate_coordinates(0, 0) is True
        assert validate_coordinates(-180, -90) is True
        assert validate_coordinates(180, 90) is True
        
        # Test invalid coordinates
        assert validate_coordinates(181, 0) is False
        assert validate_coordinates(0, 91) is False
        assert validate_coordinates(-181, 0) is False
        assert validate_coordinates(0, -91) is False
        
        # Test None values
        assert validate_coordinates(None, 0) is False
        assert validate_coordinates(0, None) is False

    # ==== Angle and Trigonometric Functions ====
    
    def test_normalize_angle(self):
        """Test angle normalization."""
        # Test angles in range
        assert normalize_angle(45) == 45
        assert normalize_angle(0) == 0
        assert normalize_angle(359) == 359
        
        # Test angles outside range
        assert normalize_angle(360) == 0
        assert normalize_angle(405) == 45
        assert normalize_angle(-45) == 315
        assert normalize_angle(-360) == 0

    def test_degrees_to_radians(self):
        """Test degree to radian conversion."""
        assert abs(degrees_to_radians(0) - 0) < 0.001
        assert abs(degrees_to_radians(90) - math.pi/2) < 0.001
        assert abs(degrees_to_radians(180) - math.pi) < 0.001
        assert abs(degrees_to_radians(360) - 2*math.pi) < 0.001

    def test_radians_to_degrees(self):
        """Test radian to degree conversion."""
        assert abs(radians_to_degrees(0) - 0) < 0.001
        assert abs(radians_to_degrees(math.pi/2) - 90) < 0.001
        assert abs(radians_to_degrees(math.pi) - 180) < 0.001
        assert abs(radians_to_degrees(2*math.pi) - 360) < 0.001

    def test_calculate_bearing(self):
        """Test bearing calculation."""
        # Test cardinal directions
        assert abs(calculate_bearing(0, 0, 1, 0) - 90) < 0.001  # East
        assert abs(calculate_bearing(0, 0, 0, 1) - 0) < 0.001   # North
        assert abs(calculate_bearing(0, 0, -1, 0) - 270) < 0.001 # West
        assert abs(calculate_bearing(0, 0, 0, -1) - 180) < 0.001 # South

    def test_point_to_line_distance(self):
        """Test point to line distance calculation."""
        # Test point on line
        distance = point_to_line_distance(1, 1, 0, 0, 2, 2)
        assert abs(distance) < 0.001
        
        # Test point off line
        distance = point_to_line_distance(0, 1, 0, 0, 2, 0)
        assert abs(distance - 1) < 0.001

    def test_is_point_in_polygon(self):
        """Test point in polygon detection."""
        # Test square polygon
        polygon = [(0, 0), (10, 0), (10, 10), (0, 10)]
        
        # Point inside
        assert is_point_in_polygon(5, 5, polygon) is True
        
        # Point outside
        assert is_point_in_polygon(15, 5, polygon) is False
        
        # Point on edge (implementation dependent)
        result = is_point_in_polygon(0, 5, polygon)
        assert isinstance(result, bool)

    def test_calculate_polygon_area(self):
        """Test polygon area calculation."""
        # Test square
        polygon = [(0, 0), (10, 0), (10, 10), (0, 10)]
        area = calculate_polygon_area(polygon)
        assert abs(area - 100) < 0.001
        
        # Test triangle
        polygon = [(0, 0), (10, 0), (5, 10)]
        area = calculate_polygon_area(polygon)
        assert abs(area - 50) < 0.001

    # ==== Utility Functions ====
    
    def test_generate_uuid(self):
        """Test UUID generation."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        
        # UUIDs should be strings
        assert isinstance(uuid1, str)
        assert isinstance(uuid2, str)
        
        # UUIDs should be unique
        assert uuid1 != uuid2
        
        # UUIDs should have correct format (36 chars with hyphens)
        assert len(uuid1) == 36
        assert uuid1.count('-') == 4

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        dt = datetime(2023, 12, 25, 10, 30, 45)
        
        # Test default format
        formatted = format_timestamp(dt)
        assert isinstance(formatted, str)
        assert "2023" in formatted
        
        # Test custom format
        formatted = format_timestamp(dt, "%Y-%m-%d")
        assert formatted == "2023-12-25"

    def test_parse_timestamp(self):
        """Test timestamp parsing."""
        # Test ISO format
        dt = parse_timestamp("2023-12-25T10:30:45")
        assert dt.year == 2023
        assert dt.month == 12
        assert dt.day == 25
        
        # Test custom format
        dt = parse_timestamp("2023-12-25", "%Y-%m-%d")
        assert dt.year == 2023
        assert dt.month == 12
        assert dt.day == 25

    def test_calculate_age_in_days(self):
        """Test age calculation in days."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        assert abs(calculate_age_in_days(yesterday) - 1) < 0.1
        assert abs(calculate_age_in_days(week_ago) - 7) < 0.1
        assert calculate_age_in_days(now) < 0.1

    def test_is_expired(self):
        """Test expiration checking."""
        now = datetime.now()
        past = now - timedelta(days=1)
        future = now + timedelta(days=1)
        
        assert is_expired(past) is True
        assert is_expired(future) is False
        assert is_expired(now) is False  # Current time not expired

    def test_safe_divide(self):
        """Test safe division."""
        # Normal division
        assert safe_divide(10, 2) == 5.0
        
        # Division by zero
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=1.0) == 1.0
        
        # Division with floats
        assert abs(safe_divide(7, 3) - 2.333) < 0.001

    def test_calculate_percentage(self):
        """Test percentage calculation."""
        assert calculate_percentage(25, 100) == 25.0
        assert calculate_percentage(1, 3) == 33.33
        assert calculate_percentage(0, 100) == 0.0
        
        # Test with zero total
        assert calculate_percentage(10, 0) == 0.0

    def test_round_to_precision(self):
        """Test precision rounding."""
        assert round_to_precision(3.14159, 2) == 3.14
        assert round_to_precision(3.14159, 0) == 3.0
        assert round_to_precision(123.456, 1) == 123.5

    # ==== Enum and Validation Functions ====
    
    def test_get_enum_values(self):
        """Test getting enum values."""
        values = get_enum_values(MotifCategory)
        assert isinstance(values, list)
        assert "chaos" in values
        assert "war" in values
        assert len(values) > 0

    def test_validate_enum_value(self):
        """Test enum value validation."""
        assert validate_enum_value("chaos", MotifCategory) is True
        assert validate_enum_value("invalid", MotifCategory) is False
        assert validate_enum_value(MotifCategory.CHAOS, MotifCategory) is True

    # ==== Dictionary and Data Functions ====
    
    def test_deep_merge_dicts(self):
        """Test deep dictionary merging."""
        dict1 = {"a": 1, "b": {"c": 2}}
        dict2 = {"b": {"d": 3}, "e": 4}
        
        result = deep_merge_dicts(dict1, dict2)
        assert result["a"] == 1
        assert result["b"]["c"] == 2
        assert result["b"]["d"] == 3
        assert result["e"] == 4

    def test_flatten_dict(self):
        """Test dictionary flattening."""
        nested = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        flattened = flatten_dict(nested)
        
        assert "a" in flattened
        assert "b.c" in flattened or "b_c" in flattened
        assert flattened["a"] == 1

    def test_unflatten_dict(self):
        """Test dictionary unflattening."""
        flat = {"a": 1, "b.c": 2, "b.d.e": 3}
        nested = unflatten_dict(flat)
        
        assert nested["a"] == 1
        assert nested["b"]["c"] == 2
        assert nested["b"]["d"]["e"] == 3

    # ==== String Functions ====
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("normal.txt") == "normal.txt"
        assert "/" not in sanitize_filename("path/to/file.txt")
        assert "\\" not in sanitize_filename("path\\to\\file.txt")
        assert sanitize_filename("file<>:\"|?*.txt") != "file<>:\"|?*.txt"

    def test_truncate_string(self):
        """Test string truncation."""
        assert truncate_string("hello world", 5) == "hello"
        assert truncate_string("hello world", 5, "...") == "he..."
        assert truncate_string("short", 10) == "short"

    def test_count_words(self):
        """Test word counting."""
        assert count_words("hello world") == 2
        assert count_words("one") == 1
        assert count_words("") == 0
        assert count_words("  spaced   out  ") == 2

    def test_extract_keywords(self):
        """Test keyword extraction."""
        keywords = extract_keywords("the quick brown fox jumps")
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        # Should filter out common words like "the"
        assert "quick" in keywords or "brown" in keywords

    def test_calculate_similarity(self):
        """Test similarity calculation."""
        similarity = calculate_similarity("hello", "hello")
        assert similarity == 1.0
        
        similarity = calculate_similarity("hello", "world")
        assert 0 <= similarity <= 1
        
        similarity = calculate_similarity("abc", "abcd")
        assert 0 < similarity < 1

    def test_normalize_text(self):
        """Test text normalization."""
        text = "  Hello, WORLD!  123  "
        normalized = normalize_text(text)
        assert normalized == "hello, world! 123"

    # ==== Encoding and Hashing Functions ====
    
    def test_generate_hash(self):
        """Test hash generation."""
        hash1 = generate_hash("test")
        hash2 = generate_hash("test")
        hash3 = generate_hash("different")
        
        # Same input should produce same hash
        assert hash1 == hash2
        
        # Different input should produce different hash
        assert hash1 != hash3
        
        # Hash should be a string
        assert isinstance(hash1, str)

    def test_encode_decode_base64(self):
        """Test base64 encoding and decoding."""
        original = "hello world"
        encoded = encode_base64(original)
        decoded = decode_base64(encoded)
        
        assert isinstance(encoded, str)
        assert decoded == original

    def test_compress_decompress_string(self):
        """Test string compression and decompression."""
        original = "This is a test string for compression. " * 10  # Repeat for better compression
        compressed = compress_string(original)
        decompressed = decompress_string(compressed)
        
        assert decompressed == original
        # Compression should reduce size for repetitive strings
        assert len(compressed) < len(original.encode('utf-8'))

    def test_validate_json_schema(self):
        """Test JSON schema validation."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name"]
        }
        
        valid_data = {"name": "John", "age": 30}
        invalid_data = {"age": 30}  # Missing required name
        
        assert validate_json_schema(valid_data, schema) is True
        assert validate_json_schema(invalid_data, schema) is False

    def test_roll_chaos_event(self):
        """Test chaos event generation."""
        event = roll_chaos_event()
        assert isinstance(event, str)
        assert len(event) > 0

    def test_generate_motif_name(self):
        """Test motif name generation."""
        name = generate_motif_name(MotifCategory.CHAOS, MotifScope.REGIONAL)
        assert isinstance(name, str)
        assert len(name) > 0
        
        # Test different combinations
        global_name = generate_motif_name(MotifCategory.HOPE, MotifScope.GLOBAL)
        local_name = generate_motif_name(MotifCategory.DEATH, MotifScope.LOCAL)
        assert isinstance(global_name, str)
        assert isinstance(local_name, str)

    def test_generate_motif_description(self):
        """Test motif description generation."""
        desc = generate_motif_description(MotifCategory.CHAOS, MotifScope.REGIONAL, 5.0)
        assert isinstance(desc, str)
        assert len(desc) > 0
        assert "chaos" in desc.lower() or "disorder" in desc.lower()
        
        # Test high intensity description (7+ should be "overwhelming")
        high_desc = generate_motif_description(MotifCategory.BETRAYAL, MotifScope.GLOBAL, 7.5)
        assert "overwhelming" in high_desc.lower()
        
        # Test low intensity
        low_desc = generate_motif_description(MotifCategory.HOPE, MotifScope.LOCAL, 2.0)
        assert "subtle" in low_desc.lower()

    def test_generate_realistic_duration(self):
        """Test duration generation."""
        # Global motifs should be longer
        global_duration = generate_realistic_duration(MotifScope.GLOBAL, 5.0)
        assert global_duration >= 1
        assert global_duration > 10  # Should be around 28 days
        
        # Local motifs should be shorter
        local_duration = generate_realistic_duration(MotifScope.LOCAL, 3.0)
        assert local_duration >= 1
        assert local_duration < 20  # Should be much shorter
        
        # Regional should be in between
        regional_duration = generate_realistic_duration(MotifScope.REGIONAL, 4.0)
        assert regional_duration >= 1

    def test_roll_new_motif(self):
        """Test new motif rolling."""
        motif = roll_new_motif()
        assert isinstance(motif, dict)
        assert "theme" in motif
        assert "lifespan" in motif
        assert "entropy_tick" in motif
        assert "weight" in motif
        assert 2 <= motif["lifespan"] <= 4
        
        # Test with chaos source
        chaos_motif = roll_new_motif(chaos_source=True)
        assert chaos_motif.get("chaos_source") is True
        
        # Test with exclusions
        excluded_motif = roll_new_motif(exclude=["war", "peace"])
        assert excluded_motif["theme"] not in ["war", "peace"]

    def test_estimate_motif_compatibility(self):
        """Test motif compatibility estimation."""
        # Create proper Motif objects with all required fields
        motif1 = Motif(
            id="1", 
            name="Chaos Rising", 
            description="A chaotic force", 
            category=MotifCategory.CHAOS, 
            scope=MotifScope.REGIONAL,
            intensity=5.0,
            theme="chaos"
        )
        motif2 = Motif(
            id="2", 
            name="Hope Returns", 
            description="A hopeful force", 
            category=MotifCategory.HOPE, 
            scope=MotifScope.LOCAL,
            intensity=4.0,
            theme="hope"
        )
        
        result = estimate_motif_compatibility(motif1, motif2)
        assert isinstance(result, float)
        assert -1.0 <= result <= 1.0

    def test_detect_motif_conflicts(self):
        """Test motif conflict detection."""
        # Test with few motifs
        result = detect_motif_conflicts([
            Motif(
                id="1", 
                name="Chaos Rising", 
                description="A chaotic force",
                category=MotifCategory.CHAOS, 
                scope=MotifScope.REGIONAL,
                intensity=5.0,
                theme="chaos"
            )
        ])
        assert result["has_conflicts"] == False
        
        # Test different categories that should conflict
        result = detect_motif_conflicts([
            Motif(
                id="1", 
                name="Chaos Rising", 
                description="A chaotic force",
                category=MotifCategory.CHAOS, 
                scope=MotifScope.REGIONAL,
                intensity=5.0,
                theme="chaos"
            ),
            Motif(
                id="2", 
                name="Peace Restored", 
                description="A peaceful force",
                category=MotifCategory.PEACE, 
                scope=MotifScope.LOCAL,
                intensity=4.0,
                theme="peace"
            )
        ])
        assert result["has_conflicts"] == True

    def test_get_compatible_motifs(self):
        """Test getting compatible motifs."""
        motif = Motif(
            id="1", 
            name="Chaos Rising", 
            description="A chaotic force",
            category=MotifCategory.CHAOS, 
            scope=MotifScope.REGIONAL,
            intensity=5.0,
            theme="chaos"
        )
        available = [
            Motif(
                id="2", 
                name="War Drums", 
                description="A war motif",
                category=MotifCategory.WAR, 
                scope=MotifScope.LOCAL,
                intensity=4.0,
                theme="war"
            )
        ]
        result = get_compatible_motifs(motif, available, count=3)
        assert isinstance(result, list)

    def test_motif_to_narrative_context(self):
        """Test motif to narrative context conversion."""
        context = motif_to_narrative_context(
            Motif(
                id="1", 
                name="Chaos Rising", 
                description="A chaotic force",
                category=MotifCategory.CHAOS, 
                scope=MotifScope.REGIONAL,
                intensity=5.0,
                theme="chaos"
            )
        )
        assert isinstance(context, dict)
        assert "theme" in context

    def test_calculate_motif_spread(self):
        """Test motif spread calculation."""
        motif = Motif(
            id="1", 
            name="Chaos Rising", 
            description="A chaotic force",
            category=MotifCategory.CHAOS, 
            scope=MotifScope.REGIONAL,
            intensity=5.0,
            theme="chaos"
        )
        spread = calculate_motif_spread(motif, distance=50.0, max_distance=100.0)
        assert spread is None or isinstance(spread, dict)

    def test_synthesize_motifs(self):
        """Test motif synthesis."""
        synthesis = synthesize_motifs([
            Motif(
                id="1", 
                name="Chaos Rising", 
                description="A chaotic force",
                category=MotifCategory.CHAOS, 
                scope=MotifScope.REGIONAL,
                intensity=5.0,
                theme="chaos"
            ), 
            Motif(
                id="2", 
                name="Hope Returns", 
                description="A hopeful force",
                category=MotifCategory.HOPE, 
                scope=MotifScope.LOCAL,
                intensity=4.0,
                theme="hope"
            )
        ])
        assert isinstance(synthesis, dict)
        assert "theme" in synthesis

    def test_get_region_motif_context(self):
        """Test region motif context generation."""
        context = get_region_motif_context([
            Motif(
                id="1", 
                name="Chaos Rising", 
                description="A chaotic force",
                category=MotifCategory.CHAOS, 
                scope=MotifScope.REGIONAL,
                intensity=5.0,
                theme="chaos"
            )
        ], format_type="descriptive")
        assert isinstance(context, str)
        assert len(context) > 0

    def test_calculate_motif_influence(self):
        """Test motif influence calculation."""
        # Test at center
        influence = calculate_motif_influence(10.0, 0.0)
        assert influence == 10.0
        
        # Test at distance
        influence_dist = calculate_motif_influence(10.0, 50.0, max_distance=100.0)
        assert 0 < influence_dist < 10.0
        
        # Test beyond max distance
        influence_far = calculate_motif_influence(10.0, 150.0, max_distance=100.0)
        assert influence_far == 0.0

    def test_generate_random_position(self):
        """Test random position generation."""
        x, y = generate_random_position(-10.0, 10.0, -5.0, 5.0)
        assert -10.0 <= x <= 10.0
        assert -5.0 <= y <= 5.0

    def test_clamp_value(self):
        """Test value clamping."""
        assert clamp_value(5.0, 0.0, 10.0) == 5.0
        assert clamp_value(-5.0, 0.0, 10.0) == 0.0
        assert clamp_value(15.0, 0.0, 10.0) == 10.0

    def test_lerp(self):
        """Test linear interpolation."""
        assert lerp(0.0, 10.0, 0.0) == 0.0
        assert lerp(0.0, 10.0, 1.0) == 10.0
        assert lerp(0.0, 10.0, 0.5) == 5.0

    def test_get_cardinal_direction(self):
        """Test cardinal direction calculation."""
        assert get_cardinal_direction(0, 0, 1, 0) == "East"
        assert get_cardinal_direction(0, 0, -1, 0) == "West"
        assert get_cardinal_direction(0, 0, 0, 1) == "North"
        assert get_cardinal_direction(0, 0, 0, -1) == "South"

    def test_calculate_region_center(self):
        """Test region center calculation."""
        points = [(0, 0), (2, 0), (1, 2)]
        center_x, center_y = calculate_region_center(points)
        assert abs(center_x - 1.0) < 0.001
        assert abs(center_y - 2/3) < 0.001

    def test_get_nearby_regions(self):
        """Test nearby regions finding."""
        regions = {
            "region1": {"center_x": 0, "center_y": 0},
            "region2": {"center_x": 5, "center_y": 0},
            "region3": {"center_x": 15, "center_y": 0}
        }
        nearby = get_nearby_regions(0, 0, regions, max_distance=10)
        assert "region1" in nearby
        assert "region2" in nearby
        assert "region3" not in nearby  # This region is at distance 15 > 10

    def test_validate_coordinates(self):
        """Test coordinate validation."""
        assert validate_coordinates(0, 0) is True
        assert validate_coordinates(180, 90) is True
        assert validate_coordinates(-180, -90) is True
        assert validate_coordinates(181, 0) is False
        assert validate_coordinates(0, 91) is False

    def test_normalize_angle(self):
        """Test angle normalization."""
        assert abs(normalize_angle(370) - 10) < 0.001
        assert abs(normalize_angle(-10) - 350) < 0.001
        assert abs(normalize_angle(180) - 180) < 0.001

    def test_degrees_to_radians(self):
        """Test degree to radian conversion."""
        assert abs(degrees_to_radians(180) - math.pi) < 0.001
        assert abs(degrees_to_radians(90) - math.pi/2) < 0.001

    def test_radians_to_degrees(self):
        """Test radian to degree conversion."""
        assert abs(radians_to_degrees(math.pi) - 180) < 0.001
        assert abs(radians_to_degrees(math.pi/2) - 90) < 0.001

    def test_calculate_bearing(self):
        """Test bearing calculation."""
        bearing = calculate_bearing(0, 0, 1, 0)
        assert 0 <= bearing < 360
        
        # Test known directions
        east_bearing = calculate_bearing(0, 0, 1, 0)
        north_bearing = calculate_bearing(0, 0, 0, 1)
        assert abs(east_bearing - 90) < 0.1 or abs(east_bearing - 270) < 0.1
        assert abs(north_bearing - 0) < 0.1 or abs(north_bearing - 360) < 0.1

    def test_point_to_line_distance(self):
        """Test point to line distance."""
        # Point (1,1) to line from (0,0) to (2,0)
        dist = point_to_line_distance(1, 1, 0, 0, 2, 0)
        assert abs(dist - 1.0) < 0.001

    def test_is_point_in_polygon(self):
        """Test point in polygon check."""
        # Square polygon
        square = [(0, 0), (2, 0), (2, 2), (0, 2)]
        assert is_point_in_polygon(1, 1, square) is True
        assert is_point_in_polygon(3, 3, square) is False
        assert is_point_in_polygon(0, 0, square) is True  # On vertex

    def test_calculate_polygon_area(self):
        """Test polygon area calculation."""
        # Unit square
        square = [(0, 0), (1, 0), (1, 1), (0, 1)]
        area = calculate_polygon_area(square)
        assert abs(area - 1.0) < 0.001

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        dt = datetime(2023, 12, 25, 15, 30, 45)
        formatted = format_timestamp(dt)
        assert "2023-12-25 15:30:45" in formatted
        
        # Test custom format
        custom = format_timestamp(dt, "%Y/%m/%d")
        assert custom == "2023/12/25"

    def test_parse_timestamp(self):
        """Test timestamp parsing."""
        dt = parse_timestamp("2023-12-25 15:30:45")
        assert dt.year == 2023
        assert dt.month == 12
        assert dt.day == 25
        assert dt.hour == 15

    def test_calculate_age_in_days(self):
        """Test age calculation."""
        start = datetime(2023, 1, 1)
        end = datetime(2023, 1, 11)
        age = calculate_age_in_days(start, end)
        assert age == 10
        
        # Test with current time
        recent = datetime.now() - timedelta(days=5)
        age_current = calculate_age_in_days(recent)
        assert 4 <= age_current <= 6  # Allow for test execution time

    def test_is_expired(self):
        """Test expiration check."""
        # Test not expired
        recent = datetime.now() - timedelta(days=1)
        assert is_expired(recent, duration_days=2) is False
        
        # Test expired
        old = datetime.now() - timedelta(days=5)
        assert is_expired(old, duration_days=2) is True

    def test_safe_divide(self):
        """Test safe division."""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=1.0) == 1.0

    def test_calculate_percentage(self):
        """Test percentage calculation."""
        assert calculate_percentage(25, 100) == 25.0
        assert calculate_percentage(1, 3) == pytest.approx(33.333, abs=0.01)

    def test_round_to_precision(self):
        """Test precision rounding."""
        assert round_to_precision(3.14159, 2) == 3.14
        assert round_to_precision(1.999, 0) == 2.0

    def test_get_enum_values(self):
        """Test enum value extraction."""
        values = get_enum_values(MotifCategory)
        assert isinstance(values, list)
        assert len(values) > 0
        assert all(isinstance(v, str) for v in values)

    def test_validate_enum_value(self):
        """Test enum value validation."""
        assert validate_enum_value("chaos", MotifCategory) is True
        assert validate_enum_value("invalid", MotifCategory) is False

    def test_deep_merge_dicts(self):
        """Test deep dictionary merging."""
        dict1 = {"a": 1, "b": {"c": 2}}
        dict2 = {"b": {"d": 3}, "e": 4}
        merged = deep_merge_dicts(dict1, dict2)
        assert merged["a"] == 1
        assert merged["b"]["c"] == 2
        assert merged["b"]["d"] == 3
        assert merged["e"] == 4

    def test_flatten_dict(self):
        """Test dictionary flattening."""
        nested = {"a": {"b": {"c": 1}}, "d": 2}
        flattened = flatten_dict(nested)
        assert flattened["a.b.c"] == 1
        assert flattened["d"] == 2

    def test_unflatten_dict(self):
        """Test dictionary unflattening."""
        flat = {"a.b.c": 1, "d": 2}
        unflattened = unflatten_dict(flat)
        assert unflattened["a"]["b"]["c"] == 1
        assert unflattened["d"] == 2

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        dirty = "file<>:\"/\\|?*name.txt"
        clean = sanitize_filename(dirty)
        assert "<" not in clean
        assert ">" not in clean
        assert ":" not in clean
        assert "file" in clean
        assert "name.txt" in clean

    def test_truncate_string(self):
        """Test string truncation."""
        long_text = "This is a very long string that needs truncation"
        truncated = truncate_string(long_text, 20)
        assert len(truncated) <= 20
        
        # Test with custom suffix
        custom = truncate_string(long_text, 20, suffix="...")
        assert custom.endswith("...")

    def test_count_words(self):
        """Test word counting."""
        text = "Hello world this is a test"
        assert count_words(text) == 6
        assert count_words("") == 0
        assert count_words("   ") == 0

    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "machine learning artificial intelligence data science"
        keywords = extract_keywords(text, max_keywords=3)
        assert isinstance(keywords, list)
        assert len(keywords) <= 3
        assert all(isinstance(k, str) for k in keywords)

    def test_calculate_similarity(self):
        """Test text similarity calculation."""
        sim1 = calculate_similarity("hello world", "hello world")
        assert sim1 == 1.0
        
        sim2 = calculate_similarity("hello", "world")
        assert 0.0 <= sim2 <= 1.0

    def test_normalize_text(self):
        """Test text normalization."""
        text = "  Hello, WORLD!  123  "
        normalized = normalize_text(text)
        assert normalized == "hello, world! 123"

    def test_validate_json_schema(self):
        """Test JSON schema validation."""
        data = {"name": "test", "value": 42}
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number"}
            }
        }
        # Note: This might fail if jsonschema is not available
        try:
            result = validate_json_schema(data, schema)
            assert isinstance(result, bool)
        except ImportError:
            pytest.skip("jsonschema not available")

    def test_generate_hash(self):
        """Test hash generation."""
        hash1 = generate_hash("test data")
        hash2 = generate_hash("test data")
        hash3 = generate_hash("different data")
        
        assert hash1 == hash2  # Same data = same hash
        assert hash1 != hash3  # Different data = different hash
        assert isinstance(hash1, str)
        assert len(hash1) > 0

    def test_encode_base64(self):
        """Test base64 encoding."""
        text = "Hello, World!"
        encoded = encode_base64(text)
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        
        # Test it's valid base64
        try:
            base64.b64decode(encoded)
        except Exception:
            pytest.fail("Invalid base64 encoding")

    def test_decode_base64(self):
        """Test base64 decoding."""
        text = "Hello, World!"
        encoded = base64.b64encode(text.encode()).decode()
        decoded = decode_base64(encoded)
        assert decoded == text

    def test_compress_string(self):
        """Test string compression."""
        text = "This is a test string for compression" * 10
        compressed = compress_string(text)
        assert isinstance(compressed, bytes)
        assert len(compressed) < len(text.encode())  # Should be smaller

    def test_decompress_string(self):
        """Test string decompression."""
        text = "This is a test string for compression"
        compressed = zlib.compress(text.encode())
        decompressed = decompress_string(compressed)
        assert decompressed == text

    def test_compression_roundtrip(self):
        """Test compression/decompression roundtrip."""
        original = "Test data for compression and decompression roundtrip"
        compressed = compress_string(original)
        decompressed = decompress_string(compressed)
        assert decompressed == original

    def test_estimate_motif_compatibility_edge_cases(self):
        """Test edge cases in motif compatibility estimation."""
        from backend.systems.motif.utils import _generate_compatibility_reason
        
        # Test the private function for compatibility reasons
        reason_high = _generate_compatibility_reason(MotifCategory.CHAOS, MotifCategory.WAR, 0.8)
        assert "strongly reinforce" in reason_high
        
        reason_medium = _generate_compatibility_reason(MotifCategory.HOPE, MotifCategory.PEACE, 0.5)
        assert "complements" in reason_medium
        
        reason_neutral = _generate_compatibility_reason(MotifCategory.JUSTICE, MotifCategory.MYSTERY, 0.0)
        assert "coexist neutrally" in reason_neutral
        
        reason_conflict = _generate_compatibility_reason(MotifCategory.CHAOS, MotifCategory.PEACE, -0.5)
        assert "conflicts" in reason_conflict
        
        reason_strong_conflict = _generate_compatibility_reason(MotifCategory.WAR, MotifCategory.PEACE, -0.8)
        assert "strongly opposes" in reason_strong_conflict

    def test_motif_to_narrative_context_with_effects(self):
        """Test motif narrative context with effects and time calculations."""
        from datetime import datetime, timedelta
        from backend.systems.motif.models import MotifEffect
        
        # Create a motif with effects and timing
        motif = Motif(
            id="effect-test",
            name="Death Approaching",
            description="A motif of death",
            category=MotifCategory.DEATH,
            scope=MotifScope.GLOBAL,
            intensity=8.0,  # High intensity for "overwhelming" theme
            theme="death",
            end_time=datetime.utcnow() + timedelta(days=5),
            effects=[
                MotifEffect(
                    target="characters",
                    magnitude=0.5,
                    description="NPCs become more fearful"
                ),
                MotifEffect(
                    target="narrative",
                    magnitude=0.3,
                    description="Death-related events increase"
                )
            ]
        )
        
        context = motif_to_narrative_context(motif)
        
        # Test themes include both category-specific and intensity-based
        assert "mortality and loss" in context["themes"]
        assert "overwhelming death" in context["themes"]
        
        # Test effect descriptions
        assert len(context["effects"]) > 0
        assert any("NPCs are more likely" in effect for effect in context["effects"])
        
        # Test remaining days calculation
        assert context["remaining_days"] > 0
        assert context["remaining_days"] <= 5

    def test_motif_to_narrative_context_no_effects(self):
        """Test motif narrative context without effects."""
        motif = Motif(
            id="simple-test",
            name="Simple Hope",
            description="A simple hope motif",
            category=MotifCategory.HOPE,
            scope=MotifScope.LOCAL,
            intensity=3.0,  # Low intensity, no "overwhelming" theme
            theme="hope",
            effects=[]  # No effects
        )
        
        context = motif_to_narrative_context(motif)
        
        # Test themes for hope category
        assert "optimism despite adversity" in context["themes"]
        # Low intensity should not add "overwhelming" theme
        assert not any("overwhelming" in theme for theme in context["themes"])
        
        # Test empty effects
        assert context["effects"] == []

    def test_calculate_motif_spread_beyond_range(self):
        """Test motif spread calculation beyond effective range."""
        motif = Motif(
            id="spread-test",
            name="Local Spread Test",
            description="Test local spread",
            category=MotifCategory.CHAOS,
            scope=MotifScope.LOCAL,  # Local scope has 0.5 multiplier
            intensity=5.0,
            theme="chaos"
        )
        
        # Test beyond effective range (LOCAL scope has 0.5 multiplier, so max = 50)
        spread = calculate_motif_spread(motif, distance=60.0, max_distance=100.0)
        assert spread is None  # Should return None when beyond range
        
        # Test within effective range 
        spread_within = calculate_motif_spread(motif, distance=20.0, max_distance=100.0)
        # At distance 20, with LOCAL scope (50 max), decay = 1 - (20/50) = 0.6
        # Effective intensity = 5.0 * 0.6 = 3.0, which should be included
        assert spread_within is not None
        assert spread_within["effective_intensity"] > 1.0
        
        # Test edge case close to threshold
        spread_edge = calculate_motif_spread(motif, distance=49.0, max_distance=100.0)
        # At distance 49, decay = 1 - (49/50) = 0.02, intensity = 5 * 0.02 = 0.1 < 1
        assert spread_edge is None  # Below threshold

    def test_calculate_motif_spread_global_scope(self):
        """Test motif spread with global scope."""
        motif = Motif(
            id="global-spread-test",
            name="Global Spread Test",
            description="Test global spread",
            category=MotifCategory.WAR,
            scope=MotifScope.GLOBAL,  # Global scope has 2.0 multiplier
            intensity=6.0,
            theme="war"
        )
        
        # Test within extended range (GLOBAL scope has 2.0 multiplier, so max = 200)
        spread = calculate_motif_spread(motif, distance=150.0, max_distance=100.0)
        assert spread is not None
        assert spread["scope"] == "global"
        assert spread["effective_intensity"] > 0

    def test_synthesize_motifs_empty_list(self):
        """Test motif synthesis with empty list."""
        synthesis = synthesize_motifs([])
        
        assert synthesis["theme"] == "neutral"
        assert synthesis["intensity"] == 0
        assert synthesis["tone"] == "neutral"
        assert synthesis["narrative_direction"] == "steady"
        assert synthesis["descriptors"] == []
        assert synthesis["conflicts"] is False
        assert "No active motifs" in synthesis["synthesis_summary"]

    def test_synthesize_motifs_with_tone_attributes(self):
        """Test motif synthesis with tone and narrative_direction attributes."""
        # Create motifs with tone and narrative_direction attributes
        motif1 = Motif(
            id="tone-test-1",
            name="Dark War",
            description="A dark war motif",
            category=MotifCategory.WAR,
            scope=MotifScope.LOCAL,
            intensity=7.0,
            theme="war"
        )
        # Manually set tone and narrative_direction attributes
        motif1.tone = "dark"
        motif1.narrative_direction = "descending"
        
        motif2 = Motif(
            id="tone-test-2",
            name="Light Hope",
            description="A light hope motif",
            category=MotifCategory.HOPE,
            scope=MotifScope.LOCAL,
            intensity=4.0,
            theme="hope"
        )
        motif2.tone = "light"
        motif2.narrative_direction = "ascending"
        
        synthesis = synthesize_motifs([motif1, motif2])
        
        # Check that tone and direction are properly synthesized
        assert synthesis["tone"] in ["dark", "light", "neutral"]
        assert synthesis["narrative_direction"] in ["descending", "ascending", "steady"]
        assert synthesis["intensity"] > 0

    def test_synthesize_motifs_with_none_attributes(self):
        """Test motif synthesis when tone/narrative_direction are None."""
        motif = Motif(
            id="none-test",
            name="None Attributes",
            description="Test with None attributes",
            category=MotifCategory.MYSTERY,
            scope=MotifScope.LOCAL,
            intensity=5.0,
            theme="mystery"
        )
        # Explicitly set to None to test the None handling
        motif.tone = None
        motif.narrative_direction = None
        
        synthesis = synthesize_motifs([motif])
        
        # Should default to neutral/steady when None
        assert synthesis["tone"] == "neutral"
        assert synthesis["narrative_direction"] == "steady"

    def test_get_region_motif_context_formats(self):
        """Test different format types for region motif context."""
        motifs = [
            Motif(
                id="format-test",
                name="Format Test",
                description="Test motif for formatting",
                category=MotifCategory.CHAOS,
                scope=MotifScope.REGIONAL,
                intensity=6.0,
                theme="chaos"
            )
        ]
        
        # Test descriptive format (default)
        descriptive = get_region_motif_context(motifs, format_type="descriptive")
        assert isinstance(descriptive, str)
        assert len(descriptive) > 0
        
        # Test other formats
        summary = get_region_motif_context(motifs, format_type="summary")
        assert isinstance(summary, str)
        
        detailed = get_region_motif_context(motifs, format_type="detailed")
        assert isinstance(detailed, str)

    def test_utility_functions_error_handling(self):
        """Test error handling in various utility functions."""
        
        # Test safe_divide with various edge cases
        assert safe_divide(float('inf'), 1.0) == float('inf')
        assert safe_divide(1.0, float('inf')) == 0.0
        
        # Test calculate_percentage with edge cases
        assert calculate_percentage(0, 0) == 0.0
        assert calculate_percentage(50, 0) == 0.0
        
        # Test validate_coordinates with None and invalid types
        assert validate_coordinates(None, None) is False
        
        # Test normalize_angle with extreme values
        assert normalize_angle(720) == 0
        assert normalize_angle(-720) == 0

    def test_text_processing_edge_cases(self):
        """Test edge cases in text processing functions."""
        
        # Test count_words with various whitespace
        assert count_words("\t\n\r  ") == 0
        assert count_words("word1\tword2\nword3\rword4") == 4
        
        # Test extract_keywords with empty/short text
        keywords_empty = extract_keywords("", max_keywords=5)
        assert keywords_empty == []
        
        keywords_short = extract_keywords("a", max_keywords=5)
        assert len(keywords_short) <= 1
        
        # Test calculate_similarity edge cases
        assert calculate_similarity("", "") == 1.0
        assert calculate_similarity("", "text") == 0.0
        
        # Test truncate_string edge cases
        assert truncate_string("", 10) == ""
        assert truncate_string("short", 10) == "short"
        assert truncate_string("exact", 5) == "exact"

    def test_timestamp_edge_cases(self):
        """Test edge cases in timestamp functions."""
        from datetime import datetime
        
        # Test format_timestamp with microseconds
        dt_micro = datetime(2023, 1, 1, 12, 0, 0, 123456)
        formatted = format_timestamp(dt_micro, "%Y-%m-%d %H:%M:%S.%f")
        assert "123456" in formatted
        
        # Test parse_timestamp with invalid format
        try:
            parse_timestamp("invalid-date", "%Y-%m-%d")
            assert False, "Should have raised exception"
        except ValueError:
            pass  # Expected
        
        # Test calculate_age_in_days with same datetime
        now = datetime.now()
        age = calculate_age_in_days(now, now)
        assert age == 0

    def test_polygon_and_geometry_edge_cases(self):
        """Test edge cases in polygon and geometry functions."""
        
        # Test calculate_polygon_area with minimal polygon (triangle)
        triangle = [(0, 0), (1, 0), (0, 1)]
        area = calculate_polygon_area(triangle)
        assert abs(area - 0.5) < 0.001
        
        # Test is_point_in_polygon with edge cases
        square = [(0, 0), (2, 0), (2, 2), (0, 2)]
        
        # Test point exactly on edge
        assert is_point_in_polygon(1, 0, square) is True  # On bottom edge
        assert is_point_in_polygon(0, 1, square) is True  # On left edge
        
        # Test point_to_line_distance with vertical and horizontal lines
        # Vertical line from (1,0) to (1,2), point (0,1)
        dist_vertical = point_to_line_distance(0, 1, 1, 0, 1, 2)
        assert abs(dist_vertical - 1.0) < 0.001
        
        # Horizontal line from (0,1) to (2,1), point (1,0) 
        dist_horizontal = point_to_line_distance(1, 0, 0, 1, 2, 1)
        assert abs(dist_horizontal - 1.0) < 0.001

    def test_encoding_edge_cases(self):
        """Test edge cases in encoding functions."""
        
        # Test generate_hash with different algorithms
        hash_sha256 = generate_hash("test", "sha256")
        hash_md5 = generate_hash("test", "md5")
        assert hash_sha256 != hash_md5
        assert len(hash_sha256) > len(hash_md5)  # SHA256 is longer than MD5
        
        # Test base64 with special characters
        special_text = "Special chars: àáâãäåæçèé"
        encoded_special = encode_base64(special_text)
        decoded_special = decode_base64(encoded_special)
        assert decoded_special == special_text
        
        # Test compression with very short string (might not compress well)
        short_text = "hi"
        compressed_short = compress_string(short_text)
        decompressed_short = decompress_string(compressed_short)
        assert decompressed_short == short_text

    def test_dict_operations_edge_cases(self):
        """Test edge cases in dictionary operations."""
        
        # Test deep_merge_dicts with conflicting keys
        dict1 = {"a": {"b": 1, "c": 2}}
        dict2 = {"a": {"b": 99}}  # Conflicting key
        merged = deep_merge_dicts(dict1, dict2)
        assert merged["a"]["b"] == 99  # dict2 should override
        assert merged["a"]["c"] == 2   # dict1 should be preserved
        
        # Test flatten_dict with custom separator
        nested = {"a": {"b": 1}}
        flattened_custom = flatten_dict(nested, sep="_")
        assert "a_b" in flattened_custom
        
        # Test unflatten_dict with custom separator
        flat_custom = {"a_b": 1}
        unflattened_custom = unflatten_dict(flat_custom, sep="_")
        assert unflattened_custom["a"]["b"] == 1
        
        # Test with empty dictionaries
        assert deep_merge_dicts({}, {}) == {}
        assert flatten_dict({}) == {}
        assert unflatten_dict({}) == {}

    def test_filename_sanitization_edge_cases(self):
        """Test edge cases in filename sanitization."""
        
        # Test with only invalid characters
        only_invalid = "<>:\"/\\|?*"
        sanitized = sanitize_filename(only_invalid)
        assert len(sanitized) > 0  # Should replace with safe characters
        assert not any(char in sanitized for char in only_invalid)
        
        # Test with mixed valid and invalid
        mixed = "valid_name<invalid>.txt"
        sanitized_mixed = sanitize_filename(mixed)
        assert "valid_name" in sanitized_mixed
        assert ".txt" in sanitized_mixed
        assert "<" not in sanitized_mixed
        assert ">" not in sanitized_mixed
        
        # Test with empty string
        sanitized_empty = sanitize_filename("")
        assert isinstance(sanitized_empty, str) 