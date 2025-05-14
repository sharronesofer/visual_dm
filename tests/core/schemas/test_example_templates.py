"""
Tests for example review templates.
"""

import pytest
from app.core.schemas.example_templates import ExampleTemplates
from app.core.schemas.review_template_validator import ReviewTemplateValidator

@pytest.fixture
def templates():
    """Create an example templates instance for testing."""
    return ExampleTemplates()

@pytest.fixture
def validator():
    """Create a validator instance for testing."""
    return ReviewTemplateValidator()

def test_get_all_templates(templates):
    """Test getting all available templates."""
    all_templates = templates.get_all_templates()
    
    assert len(all_templates) == 8  # We have 8 template types
    template_names = {t['name'] for t in all_templates}
    
    expected_names = {
        "Basic Code Review",
        "Detailed Code Review",
        "Quick Code Review",
        "Architecture Review",
        "Security Review",
        "Performance Review",
        "Accessibility Review",
        "API Review"
    }
    
    assert template_names == expected_names

def test_basic_code_review_template(templates, validator):
    """Test the basic code review template."""
    template = templates.get_basic_code_review_template()
    
    assert template['name'] == "Basic Code Review"
    assert template['version'] == "1.0.0"
    assert template['category'] == "code"
    
    # Validate template structure
    errors = validator.validate_template(template)
    assert errors is None, f"Template validation failed with errors: {errors}"
    
    # Check sections
    section_titles = {s['title'] for s in template['sections']}
    expected_sections = {
        "Code Quality",
        "Functionality",
        "Security",
        "Documentation",
        "Testing"
    }
    assert section_titles == expected_sections

def test_detailed_code_review_template(templates, validator):
    """Test the detailed code review template."""
    template = templates.get_detailed_code_review_template()
    
    assert template['name'] == "Detailed Code Review"
    assert template['version'] == "1.0.0"
    assert template['category'] == "code"
    assert template['metadata']['recommendedFrequency'] == 'major-changes'
    
    # Validate template structure
    errors = validator.validate_template(template)
    assert errors is None, f"Template validation failed with errors: {errors}"
    
    # Should have additional sections
    section_titles = {s['title'] for s in template['sections']}
    assert "Performance" in section_titles
    assert "Maintainability" in section_titles
    assert "Integration" in section_titles

def test_quick_code_review_template(templates, validator):
    """Test the quick code review template."""
    template = templates.get_quick_code_review_template()
    
    assert template['name'] == "Quick Code Review"
    assert template['version'] == "1.0.0"
    assert template['category'] == "code"
    assert template['metadata']['recommendedFrequency'] == 'per-commit'
    assert template['metadata']['estimatedDuration'] == '5-15min'
    
    # Validate template structure
    errors = validator.validate_template(template)
    assert errors is None, f"Template validation failed with errors: {errors}"
    
    # Should only have essential sections
    assert len(template['sections']) == 2
    section_titles = {s['title'] for s in template['sections']}
    assert section_titles == {"Code Quality", "Functionality"}

def test_performance_review_template(templates, validator):
    """Test the performance review template."""
    template = templates.get_performance_review_template()
    
    assert template['name'] == "Performance Review"
    assert template['version'] == "1.0.0"
    assert 'performance' in template['metadata']['tags']
    
    # Validate template structure
    errors = validator.validate_template(template)
    assert errors is None, f"Template validation failed with errors: {errors}"
    
    # Check performance-specific sections
    section_titles = {s['title'] for s in template['sections']}
    expected_sections = {
        "Algorithmic Efficiency",
        "Resource Usage",
        "Scalability",
        "Caching",
        "Optimization"
    }
    assert section_titles == expected_sections

def test_accessibility_review_template(templates, validator):
    """Test the accessibility review template."""
    template = templates.get_accessibility_review_template()
    
    assert template['name'] == "Accessibility Review"
    assert template['version'] == "1.0.0"
    assert 'accessibility' in template['metadata']['tags']
    assert 'wcag' in template['metadata']['tags']
    
    # Validate template structure
    errors = validator.validate_template(template)
    assert errors is None, f"Template validation failed with errors: {errors}"
    
    # Check accessibility-specific sections
    section_titles = {s['title'] for s in template['sections']}
    expected_sections = {
        "WCAG Compliance",
        "Keyboard Navigation",
        "Screen Reader Compatibility",
        "Visual Accessibility",
        "Cognitive Accessibility"
    }
    assert section_titles == expected_sections

def test_api_review_template(templates, validator):
    """Test the API review template."""
    template = templates.get_api_review_template()
    
    assert template['name'] == "API Review"
    assert template['version'] == "1.0.0"
    assert 'api' in template['metadata']['tags']
    assert template['metadata']['recommendedFrequency'] == 'per-endpoint'
    
    # Validate template structure
    errors = validator.validate_template(template)
    assert errors is None, f"Template validation failed with errors: {errors}"
    
    # Check API-specific sections
    section_titles = {s['title'] for s in template['sections']}
    expected_sections = {
        "API Design",
        "API Security",
        "API Documentation",
        "API Testing",
        "API Versioning"
    }
    assert section_titles == expected_sections

def test_template_question_types(templates):
    """Test that templates contain different question types."""
    template = templates.get_basic_code_review_template()
    
    question_types = set()
    for section in template['sections']:
        for question in section['questions']:
            question_types.add(question['type'])
    
    # Should have at least rating, choice, and text questions
    assert 'rating' in question_types
    assert 'choice' in question_types
    assert 'text' in question_types

def test_template_metadata(templates):
    """Test that templates have required metadata."""
    for template in templates.get_all_templates():
        assert 'metadata' in template
        assert 'tags' in template['metadata']
        assert 'recommendedFrequency' in template['metadata']
        assert 'estimatedDuration' in template['metadata']
        assert isinstance(template['metadata']['tags'], list)
        assert len(template['metadata']['tags']) > 0

def test_question_metadata(templates):
    """Test that questions have proper metadata."""
    template = templates.get_detailed_code_review_template()
    
    for section in template['sections']:
        for question in section['questions']:
            assert 'metadata' in question
            assert 'hint' in question['metadata']
            
            if question['type'] == 'rating':
                assert 'ratingScale' in question['metadata']
                assert 'min' in question['metadata']['ratingScale']
                assert 'max' in question['metadata']['ratingScale']
            elif question['type'] == 'choice':
                assert 'options' in question
                assert isinstance(question['options'], list)
                assert len(question['options']) > 0 