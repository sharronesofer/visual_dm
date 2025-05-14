"""
Factory for creating common review template patterns.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .review_template_validator import ReviewTemplateValidator

class ReviewTemplateFactory:
    """Factory class for generating review templates."""
    
    def __init__(self):
        """Initialize the factory with a validator."""
        self.validator = ReviewTemplateValidator()

    def create_code_review_template(self, name: str = "Code Review Template",
                                  version: str = "1.0.0") -> Dict[str, Any]:
        """
        Create a standard code review template.
        
        Args:
            name: Template name
            version: Template version
            
        Returns:
            A complete code review template
        """
        sections = [
            self._create_code_quality_section(),
            self._create_functionality_section(),
            self._create_security_section(),
            self._create_documentation_section(),
            self._create_testing_section()
        ]
        
        metadata = {
            'tags': ['code-quality', 'security', 'testing'],
            'recommendedFrequency': 'per-pr',
            'estimatedDuration': '30-60min'
        }
        
        return self.validator.create_template(
            name=name,
            version=version,
            description="Comprehensive code review template covering code quality, functionality, security, documentation, and testing",
            category="code",
            sections=sections,
            metadata=metadata
        )

    def create_architecture_review_template(self, name: str = "Architecture Review Template",
                                         version: str = "1.0.0") -> Dict[str, Any]:
        """
        Create a template for architecture reviews.
        
        Args:
            name: Template name
            version: Template version
            
        Returns:
            An architecture review template
        """
        sections = [
            self._create_design_principles_section(),
            self._create_scalability_section(),
            self._create_maintainability_section(),
            self._create_security_architecture_section(),
            self._create_integration_section()
        ]
        
        metadata = {
            'tags': ['architecture', 'design', 'scalability'],
            'recommendedFrequency': 'major-changes',
            'estimatedDuration': '2-4hours'
        }
        
        return self.validator.create_template(
            name=name,
            version=version,
            description="Comprehensive architecture review template for evaluating system design and architecture decisions",
            category="architecture",
            sections=sections,
            metadata=metadata
        )

    def create_security_review_template(self, name: str = "Security Review Template",
                                      version: str = "1.0.0") -> Dict[str, Any]:
        """
        Create a template for security reviews.
        
        Args:
            name: Template name
            version: Template version
            
        Returns:
            A security review template
        """
        sections = [
            self._create_authentication_section(),
            self._create_authorization_section(),
            self._create_data_protection_section(),
            self._create_vulnerability_section(),
            self._create_compliance_section()
        ]
        
        metadata = {
            'tags': ['security', 'compliance', 'risk-assessment'],
            'recommendedFrequency': 'monthly',
            'estimatedDuration': '2-3hours'
        }
        
        return self.validator.create_template(
            name=name,
            version=version,
            description="Comprehensive security review template for assessing application security measures",
            category="security",
            sections=sections,
            metadata=metadata
        )

    def _create_code_quality_section(self) -> Dict[str, Any]:
        """Create a section for code quality review."""
        questions = [
            self.validator.create_question(
                text="Is the code well-formatted and following style guidelines?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check indentation, naming conventions, and overall code organization",
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
            ),
            self.validator.create_question(
                text="Are there any code smells or anti-patterns?",
                type="choice",
                required=True,
                options=['Yes', 'No'],
                metadata={'hint': "Look for duplicate code, long methods, or complex conditionals"}
            ),
            self.validator.create_question(
                text="What improvements would you suggest for code quality?",
                type="text",
                required=False,
                metadata={'hint': "Suggest specific refactoring opportunities"}
            )
        ]
        
        return self.validator.create_section(
            title="Code Quality",
            description="Evaluate the overall quality and maintainability of the code",
            questions=questions
        )

    def _create_functionality_section(self) -> Dict[str, Any]:
        """Create a section for functionality review."""
        questions = [
            self.validator.create_question(
                text="Does the code correctly implement the required functionality?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Compare implementation against requirements",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="Are edge cases handled appropriately?",
                type="choice",
                required=True,
                options=['Yes', 'No', 'Partially'],
                metadata={'hint': "Consider input validation, error handling, and boundary conditions"}
            )
        ]
        
        return self.validator.create_section(
            title="Functionality",
            description="Assess if the code correctly implements the required functionality",
            questions=questions
        )

    def _create_security_section(self) -> Dict[str, Any]:
        """Create a section for security review."""
        questions = [
            self.validator.create_question(
                text="Are there any potential security vulnerabilities?",
                type="choice",
                required=True,
                options=['Yes', 'No', 'Need Investigation'],
                metadata={'hint': "Check for common security issues like XSS, CSRF, SQL injection"}
            ),
            self.validator.create_question(
                text="Is sensitive data handled securely?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Review data encryption, secure storage, and transmission",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            )
        ]
        
        return self.validator.create_section(
            title="Security",
            description="Evaluate security aspects of the code",
            questions=questions
        )

    def _create_documentation_section(self) -> Dict[str, Any]:
        """Create a section for documentation review."""
        questions = [
            self.validator.create_question(
                text="Is the code adequately documented?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check for clear comments, docstrings, and API documentation",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="Are there any areas that need better documentation?",
                type="text",
                required=False,
                metadata={'hint': "Identify specific areas needing more documentation"}
            )
        ]
        
        return self.validator.create_section(
            title="Documentation",
            description="Assess the quality and completeness of documentation",
            questions=questions
        )

    def _create_testing_section(self) -> Dict[str, Any]:
        """Create a section for testing review."""
        questions = [
            self.validator.create_question(
                text="Are there sufficient unit tests?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check test coverage and quality",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="What additional tests would you recommend?",
                type="text",
                required=False,
                metadata={'hint': "Suggest specific test cases or types of testing"}
            )
        ]
        
        return self.validator.create_section(
            title="Testing",
            description="Evaluate the testing strategy and coverage",
            questions=questions
        )

    def _create_design_principles_section(self) -> Dict[str, Any]:
        """Create a section for design principles review."""
        questions = [
            self.validator.create_question(
                text="Does the design follow SOLID principles?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Evaluate adherence to Single Responsibility, Open-Closed, etc.",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="Are there any violations of key design principles?",
                type="text",
                required=True,
                metadata={'hint': "Identify specific violations and suggest improvements"}
            )
        ]
        
        return self.validator.create_section(
            title="Design Principles",
            description="Evaluate adherence to software design principles",
            questions=questions
        )

    def _create_scalability_section(self) -> Dict[str, Any]:
        """Create a section for scalability review."""
        questions = [
            self.validator.create_question(
                text="How well does the architecture handle scaling?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Consider both vertical and horizontal scaling",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="Are there any potential bottlenecks?",
                type="text",
                required=True,
                metadata={'hint': "Identify performance bottlenecks and scaling limitations"}
            )
        ]
        
        return self.validator.create_section(
            title="Scalability",
            description="Assess the system's ability to scale",
            questions=questions
        )

    def _create_maintainability_section(self) -> Dict[str, Any]:
        """Create a section for maintainability review."""
        questions = [
            self.validator.create_question(
                text="How maintainable is the codebase?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Consider code organization, modularity, and documentation",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="What aspects could improve maintainability?",
                type="text",
                required=True,
                metadata={'hint': "Suggest specific improvements for maintainability"}
            )
        ]
        
        return self.validator.create_section(
            title="Maintainability",
            description="Evaluate long-term maintainability of the system",
            questions=questions
        )

    def _create_security_architecture_section(self) -> Dict[str, Any]:
        """Create a section for security architecture review."""
        questions = [
            self.validator.create_question(
                text="Are security concerns addressed at the architectural level?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Evaluate security patterns and principles in the architecture",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="What security improvements would you recommend?",
                type="text",
                required=True,
                metadata={'hint': "Suggest architectural-level security improvements"}
            )
        ]
        
        return self.validator.create_section(
            title="Security Architecture",
            description="Assess security measures at the architectural level",
            questions=questions
        )

    def _create_integration_section(self) -> Dict[str, Any]:
        """Create a section for integration review."""
        questions = [
            self.validator.create_question(
                text="How well does the system integrate with other components?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Evaluate integration patterns and interfaces",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="Are there any integration concerns?",
                type="text",
                required=True,
                metadata={'hint': "Identify potential integration issues or improvements"}
            )
        ]
        
        return self.validator.create_section(
            title="Integration",
            description="Evaluate system integration aspects",
            questions=questions
        )

    def _create_authentication_section(self) -> Dict[str, Any]:
        """Create a section for authentication review."""
        questions = [
            self.validator.create_question(
                text="How robust is the authentication system?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Evaluate authentication mechanisms and security",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="Are there any authentication vulnerabilities?",
                type="text",
                required=True,
                metadata={'hint': "Identify potential authentication security issues"}
            )
        ]
        
        return self.validator.create_section(
            title="Authentication",
            description="Assess authentication mechanisms and security",
            questions=questions
        )

    def _create_authorization_section(self) -> Dict[str, Any]:
        """Create a section for authorization review."""
        questions = [
            self.validator.create_question(
                text="Is authorization properly implemented?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Evaluate access control and permissions",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="What authorization improvements are needed?",
                type="text",
                required=True,
                metadata={'hint': "Suggest improvements to authorization system"}
            )
        ]
        
        return self.validator.create_section(
            title="Authorization",
            description="Evaluate authorization and access control",
            questions=questions
        )

    def _create_data_protection_section(self) -> Dict[str, Any]:
        """Create a section for data protection review."""
        questions = [
            self.validator.create_question(
                text="How well is sensitive data protected?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Evaluate data encryption and protection measures",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="Are there any data protection concerns?",
                type="text",
                required=True,
                metadata={'hint': "Identify potential data security issues"}
            )
        ]
        
        return self.validator.create_section(
            title="Data Protection",
            description="Assess data security and protection measures",
            questions=questions
        )

    def _create_vulnerability_section(self) -> Dict[str, Any]:
        """Create a section for vulnerability assessment."""
        questions = [
            self.validator.create_question(
                text="Are there any known vulnerabilities?",
                type="choice",
                required=True,
                options=['Yes', 'No', 'Need Investigation'],
                metadata={'hint': "Check against common vulnerability databases"}
            ),
            self.validator.create_question(
                text="What security testing has been performed?",
                type="text",
                required=True,
                metadata={'hint': "Document security testing and results"}
            )
        ]
        
        return self.validator.create_section(
            title="Vulnerability Assessment",
            description="Evaluate known vulnerabilities and security testing",
            questions=questions
        )

    def _create_compliance_section(self) -> Dict[str, Any]:
        """Create a section for compliance review."""
        questions = [
            self.validator.create_question(
                text="Does the system meet compliance requirements?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check against relevant compliance standards",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.validator.create_question(
                text="What compliance improvements are needed?",
                type="text",
                required=True,
                metadata={'hint': "Identify gaps in compliance and suggest improvements"}
            )
        ]
        
        return self.validator.create_section(
            title="Compliance",
            description="Assess compliance with security standards and regulations",
            questions=questions
        ) 