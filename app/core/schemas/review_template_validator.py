"""
Validation module for review templates.
"""

import json
import os
from typing import Dict, Any, List, Optional, Union
from jsonschema import validate, ValidationError, Draft7Validator
from datetime import datetime
import re

class ReviewTemplateValidator:
    """Validator for review templates using JSON Schema."""
    
    def __init__(self):
        """Initialize the validator with the schema."""
        schema_path = os.path.join(os.path.dirname(__file__), 'review_template.schema.json')
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        self.validator = Draft7Validator(self.schema)
        
        # Load sub-schemas for sections and questions
        self.section_schema = self.schema['definitions']['section']
        self.question_schema = self.schema['definitions']['question']

    def validate_template(self, template: Dict[str, Any]) -> Union[List[str], None]:
        """
        Validate a review template against the schema.
        
        Args:
            template: The template to validate
            
        Returns:
            List of error messages if validation fails, None if validation succeeds
        """
        try:
            self.validator.validate(template)
            
            # Additional custom validations
            errors = []
            
            # Validate version format (semver)
            if not self._is_valid_semver(template.get('version', '')):
                errors.append("Version must follow semantic versioning (e.g., '1.0.0')")
            
            # Validate sections
            for section in template.get('sections', []):
                section_errors = self.validate_section(section)
                if section_errors:
                    errors.extend(section_errors)
            
            return errors if errors else None
            
        except ValidationError as e:
            return [str(e)]

    def validate_section(self, section: Dict[str, Any]) -> Union[List[str], None]:
        """
        Validate a section against the section schema.
        
        Args:
            section: The section to validate
            
        Returns:
            List of error messages if validation fails, None if validation succeeds
        """
        try:
            validate(instance=section, schema=self.section_schema)
            
            errors = []
            
            # Validate questions
            for question in section.get('questions', []):
                question_errors = self.validate_question(question)
                if question_errors:
                    errors.extend(question_errors)
            
            return errors if errors else None
            
        except ValidationError as e:
            return [str(e)]

    def validate_question(self, question: Dict[str, Any]) -> Union[List[str], None]:
        """
        Validate a question against the question schema.
        
        Args:
            question: The question to validate
            
        Returns:
            List of error messages if validation fails, None if validation succeeds
        """
        try:
            validate(instance=question, schema=self.question_schema)
            
            errors = []
            question_type = question.get('type')
            
            # Type-specific validations
            if question_type == 'choice' and 'options' in question:
                if not isinstance(question['options'], list) or len(question['options']) < 1:
                    errors.append("Choice questions must have at least one option")
                    
            elif question_type == 'rating':
                metadata = question.get('metadata', {})
                if 'ratingScale' in metadata:
                    scale = metadata['ratingScale']
                    if scale.get('min', 1) >= scale.get('max', 5):
                        errors.append("Rating scale minimum must be less than maximum")
                        
            return errors if errors else None
            
        except ValidationError as e:
            return [str(e)]

    def create_template(self, name: str, version: str, sections: List[Dict[str, Any]], 
                       description: Optional[str] = None, category: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new template with validation.
        
        Args:
            name: Template name
            version: Template version (semver)
            sections: List of sections
            description: Optional template description
            category: Optional template category
            metadata: Optional template metadata
            
        Returns:
            The created template dict
            
        Raises:
            ValidationError: If the template is invalid
        """
        template = {
            'name': name,
            'version': version,
            'sections': sections,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'is_active': True
        }
        
        if description:
            template['description'] = description
        if category:
            template['category'] = category
        if metadata:
            template['metadata'] = metadata
            
        errors = self.validate_template(template)
        if errors:
            raise ValidationError(f"Template validation failed: {', '.join(errors)}")
            
        return template

    def create_section(self, title: str, questions: List[Dict[str, Any]], 
                      description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new section with validation.
        
        Args:
            title: Section title
            questions: List of questions
            description: Optional section description
            
        Returns:
            The created section dict
            
        Raises:
            ValidationError: If the section is invalid
        """
        section = {
            'title': title,
            'questions': questions
        }
        
        if description:
            section['description'] = description
            
        errors = self.validate_section(section)
        if errors:
            raise ValidationError(f"Section validation failed: {', '.join(errors)}")
            
        return section

    def create_question(self, text: str, type: str, required: bool = False,
                       options: Optional[List[str]] = None, 
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new question with validation.
        
        Args:
            text: Question text
            type: Question type ('text', 'choice', 'rating')
            required: Whether the question is required
            options: Options for choice questions
            metadata: Optional question metadata
            
        Returns:
            The created question dict
            
        Raises:
            ValidationError: If the question is invalid
        """
        question = {
            'text': text,
            'type': type,
            'required': required
        }
        
        if options is not None:
            question['options'] = options
        if metadata:
            question['metadata'] = metadata
            
        errors = self.validate_question(question)
        if errors:
            raise ValidationError(f"Question validation failed: {', '.join(errors)}")
            
        return question

    def _is_valid_semver(self, version: str) -> bool:
        """Check if a version string follows semantic versioning."""
        pattern = r'^\d+\.\d+\.\d+(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$'
        return bool(re.match(pattern, version)) 