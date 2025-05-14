"""
Tests for the review template factory.
"""

import pytest
from datetime import datetime
from app.core.schemas.review_template_factory import ReviewTemplateFactory
from app.core.schemas.review_template_validator import ReviewTemplateValidator

@pytest.fixture
def factory():
    """Create a factory instance for testing."""
    return ReviewTemplateFactory()

def test_create_code_review_template(factory):
    """Test creating a code review template."""
    template = factory.create_code_review_template()
    
    assert template['name'] == "Code Review Template"
    assert template['version'] == "1.0.0"
    assert template['category'] == "code"
    assert len(template['sections']) == 5
    
    # Verify sections
    section_titles = [s['title'] for s in template['sections']]
    assert "Code Quality" in section_titles
    assert "Functionality" in section_titles
    assert "Security" in section_titles
    assert "Documentation" in section_titles
    assert "Testing" in section_titles
    
    # Verify metadata
    assert 'code-quality' in template['metadata']['tags']
    assert template['metadata']['recommendedFrequency'] == 'per-pr'

def test_create_architecture_review_template(factory):
    """Test creating an architecture review template."""
    template = factory.create_architecture_review_template()
    
    assert template['name'] == "Architecture Review Template"
    assert template['version'] == "1.0.0"
    assert template['category'] == "architecture"
    assert len(template['sections']) == 5
    
    # Verify sections
    section_titles = [s['title'] for s in template['sections']]
    assert "Design Principles" in section_titles
    assert "Scalability" in section_titles
    assert "Maintainability" in section_titles
    assert "Security Architecture" in section_titles
    assert "Integration" in section_titles
    
    # Verify metadata
    assert 'architecture' in template['metadata']['tags']
    assert template['metadata']['recommendedFrequency'] == 'major-changes'

def test_create_security_review_template(factory):
    """Test creating a security review template."""
    template = factory.create_security_review_template()
    
    assert template['name'] == "Security Review Template"
    assert template['version'] == "1.0.0"
    assert template['category'] == "security"
    assert len(template['sections']) == 5
    
    # Verify sections
    section_titles = [s['title'] for s in template['sections']]
    assert "Authentication" in section_titles
    assert "Authorization" in section_titles
    assert "Data Protection" in section_titles
    assert "Vulnerability Assessment" in section_titles
    assert "Compliance" in section_titles
    
    # Verify metadata
    assert 'security' in template['metadata']['tags']
    assert template['metadata']['recommendedFrequency'] == 'monthly'

def test_custom_template_name_and_version(factory):
    """Test creating a template with custom name and version."""
    name = "Custom Review Template"
    version = "2.0.0"
    template = factory.create_code_review_template(name=name, version=version)
    
    assert template['name'] == name
    assert template['version'] == version

def test_section_question_structure(factory):
    """Test the structure of sections and questions in templates."""
    template = factory.create_code_review_template()
    
    # Test first section structure
    section = template['sections'][0]
    assert 'title' in section
    assert 'description' in section
    assert 'questions' in section
    
    # Test question structure
    question = section['questions'][0]
    assert 'text' in question
    assert 'type' in question
    assert 'required' in question
    assert 'metadata' in question

def test_rating_question_metadata(factory):
    """Test the metadata structure of rating questions."""
    template = factory.create_code_review_template()
    
    # Find a rating question
    rating_question = None
    for section in template['sections']:
        for question in section['questions']:
            if question['type'] == 'rating':
                rating_question = question
                break
        if rating_question:
            break
    
    assert rating_question is not None
    assert 'ratingScale' in rating_question['metadata']
    assert 'min' in rating_question['metadata']['ratingScale']
    assert 'max' in rating_question['metadata']['ratingScale']

def test_choice_question_options(factory):
    """Test the options structure of choice questions."""
    template = factory.create_code_review_template()
    
    # Find a choice question
    choice_question = None
    for section in template['sections']:
        for question in section['questions']:
            if question['type'] == 'choice':
                choice_question = question
                break
        if choice_question:
            break
    
    assert choice_question is not None
    assert 'options' in choice_question
    assert isinstance(choice_question['options'], list)
    assert len(choice_question['options']) > 0

def test_template_validation(factory):
    """Test that created templates pass validation."""
    validator = ReviewTemplateValidator()
    
    # Test all template types
    templates = [
        factory.create_code_review_template(),
        factory.create_architecture_review_template(),
        factory.create_security_review_template()
    ]
    
    for template in templates:
        # This should not raise any validation errors
        errors = validator.validate_template(template)
        assert errors is None, f"Template validation failed with errors: {errors}" 