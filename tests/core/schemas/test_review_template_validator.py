"""
Tests for the review template validator.
"""

import pytest
from datetime import datetime
from jsonschema import ValidationError
from app.core.schemas.review_template_validator import ReviewTemplateValidator

@pytest.fixture
def validator():
    """Create a validator instance for testing."""
    return ReviewTemplateValidator()

@pytest.fixture
def valid_question():
    """Create a valid question for testing."""
    return {
        'text': 'Is the code well-documented?',
        'type': 'rating',
        'required': True,
        'metadata': {
            'hint': 'Check for docstrings and inline comments',
            'ratingScale': {
                'min': 1,
                'max': 5,
                'labels': {
                    '1': 'Poor',
                    '3': 'Acceptable',
                    '5': 'Excellent'
                }
            }
        }
    }

@pytest.fixture
def valid_section(valid_question):
    """Create a valid section for testing."""
    return {
        'title': 'Documentation',
        'description': 'Evaluate the code documentation quality',
        'questions': [valid_question]
    }

@pytest.fixture
def valid_template(valid_section):
    """Create a valid template for testing."""
    return {
        'name': 'Code Review Template',
        'description': 'Standard template for code reviews',
        'version': '1.0.0',
        'category': 'code',
        'sections': [valid_section],
        'metadata': {
            'tags': ['code-quality', 'documentation'],
            'recommendedFrequency': 'sprint'
        },
        'is_active': True,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }

def test_validate_valid_template(validator, valid_template):
    """Test that a valid template passes validation."""
    errors = validator.validate_template(valid_template)
    assert errors is None

def test_validate_invalid_template_missing_required(validator, valid_template):
    """Test that template validation fails when required fields are missing."""
    del valid_template['name']
    errors = validator.validate_template(valid_template)
    assert errors is not None
    assert any('name' in error for error in errors)

def test_validate_invalid_template_version_format(validator, valid_template):
    """Test that template validation fails with invalid version format."""
    valid_template['version'] = 'invalid'
    errors = validator.validate_template(valid_template)
    assert errors is not None
    assert any('version' in error for error in errors)

def test_validate_valid_section(validator, valid_section):
    """Test that a valid section passes validation."""
    errors = validator.validate_section(valid_section)
    assert errors is None

def test_validate_invalid_section_missing_required(validator, valid_section):
    """Test that section validation fails when required fields are missing."""
    del valid_section['title']
    errors = validator.validate_section(valid_section)
    assert errors is not None
    assert any('title' in error for error in errors)

def test_validate_valid_question(validator, valid_question):
    """Test that a valid question passes validation."""
    errors = validator.validate_question(valid_question)
    assert errors is None

def test_validate_invalid_question_type(validator, valid_question):
    """Test that question validation fails with invalid question type."""
    valid_question['type'] = 'invalid'
    errors = validator.validate_question(valid_question)
    assert errors is not None
    assert any('type' in error for error in errors)

def test_create_template(validator):
    """Test creating a template using the helper method."""
    sections = [{
        'title': 'Test Section',
        'questions': [{
            'text': 'Test Question',
            'type': 'text',
            'required': True
        }]
    }]
    
    template = validator.create_template(
        name='Test Template',
        description='Test Description',
        version='1.0.0',
        category='code',
        sections=sections
    )
    
    assert template['name'] == 'Test Template'
    assert template['version'] == '1.0.0'
    assert len(template['sections']) == 1

def test_create_template_invalid(validator):
    """Test that creating an invalid template raises ValidationError."""
    with pytest.raises(ValidationError):
        validator.create_template(
            name='Test Template',
            description='Test Description',
            version='invalid',  # Invalid version format
            category='code',
            sections=[]  # Empty sections (invalid)
        )

def test_create_section(validator):
    """Test creating a section using the helper method."""
    questions = [{
        'text': 'Test Question',
        'type': 'text',
        'required': True
    }]
    
    section = validator.create_section(
        title='Test Section',
        questions=questions,
        description='Test Description'
    )
    
    assert section['title'] == 'Test Section'
    assert len(section['questions']) == 1

def test_create_section_invalid(validator):
    """Test that creating an invalid section raises ValidationError."""
    with pytest.raises(ValidationError):
        validator.create_section(
            title='Test Section',
            questions=[]  # Empty questions (invalid)
        )

def test_create_question(validator):
    """Test creating a question using the helper method."""
    question = validator.create_question(
        text='Test Question',
        type='choice',
        required=True,
        options=['Yes', 'No'],
        metadata={'hint': 'Test hint'}
    )
    
    assert question['text'] == 'Test Question'
    assert question['type'] == 'choice'
    assert len(question['options']) == 2

def test_create_question_invalid_type(validator):
    """Test that creating a question with invalid type raises ValidationError."""
    with pytest.raises(ValidationError):
        validator.create_question(
            text='Test Question',
            type='invalid'  # Invalid question type
        )

def test_create_choice_question_without_options(validator):
    """Test that creating a choice question without options is valid."""
    question = validator.create_question(
        text='Test Question',
        type='choice'
    )
    assert question['text'] == 'Test Question'
    assert question['type'] == 'choice'
    assert 'options' not in question

def test_create_rating_question_with_scale(validator):
    """Test creating a rating question with a custom scale."""
    metadata = {
        'ratingScale': {
            'min': 1,
            'max': 10,
            'labels': {
                '1': 'Poor',
                '5': 'Average',
                '10': 'Excellent'
            }
        }
    }
    
    question = validator.create_question(
        text='Rate the code quality',
        type='rating',
        metadata=metadata
    )
    
    assert question['type'] == 'rating'
    assert question['metadata']['ratingScale']['max'] == 10 