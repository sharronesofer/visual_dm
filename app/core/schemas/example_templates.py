"""
Example review templates for common use cases.
"""

from typing import Dict, Any, List
from .review_template_factory import ReviewTemplateFactory

class ExampleTemplates:
    """Collection of example review templates."""
    
    def __init__(self):
        """Initialize with a template factory."""
        self.factory = ReviewTemplateFactory()

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """
        Get all available example templates.
        
        Returns:
            List of template dictionaries
        """
        return [
            self.get_basic_code_review_template(),
            self.get_detailed_code_review_template(),
            self.get_quick_code_review_template(),
            self.get_architecture_review_template(),
            self.get_security_review_template(),
            self.get_performance_review_template(),
            self.get_accessibility_review_template(),
            self.get_api_review_template()
        ]

    def get_basic_code_review_template(self) -> Dict[str, Any]:
        """
        Get a basic code review template suitable for most code changes.
        
        Returns:
            Template dictionary
        """
        return self.factory.create_code_review_template(
            name="Basic Code Review",
            version="1.0.0"
        )

    def get_detailed_code_review_template(self) -> Dict[str, Any]:
        """
        Get a detailed code review template for complex changes.
        
        Returns:
            Template dictionary
        """
        template = self.factory.create_code_review_template(
            name="Detailed Code Review",
            version="1.0.0"
        )
        
        # Add additional sections for a more thorough review
        template['sections'].extend([
            self.factory._create_performance_section(),
            self.factory._create_maintainability_section(),
            self.factory._create_integration_section()
        ])
        
        template['metadata']['recommendedFrequency'] = 'major-changes'
        template['metadata']['estimatedDuration'] = '1-2hours'
        
        return template

    def get_quick_code_review_template(self) -> Dict[str, Any]:
        """
        Get a streamlined template for quick reviews of small changes.
        
        Returns:
            Template dictionary
        """
        template = self.factory.create_code_review_template(
            name="Quick Code Review",
            version="1.0.0"
        )
        
        # Keep only essential sections
        template['sections'] = [
            self.factory._create_code_quality_section(),
            self.factory._create_functionality_section()
        ]
        
        template['metadata']['recommendedFrequency'] = 'per-commit'
        template['metadata']['estimatedDuration'] = '5-15min'
        
        return template

    def get_architecture_review_template(self) -> Dict[str, Any]:
        """
        Get a template for architecture reviews.
        
        Returns:
            Template dictionary
        """
        return self.factory.create_architecture_review_template(
            name="Architecture Review",
            version="1.0.0"
        )

    def get_security_review_template(self) -> Dict[str, Any]:
        """
        Get a template for security reviews.
        
        Returns:
            Template dictionary
        """
        return self.factory.create_security_review_template(
            name="Security Review",
            version="1.0.0"
        )

    def get_performance_review_template(self) -> Dict[str, Any]:
        """
        Get a template focused on performance review.
        
        Returns:
            Template dictionary
        """
        template = self.factory.create_code_review_template(
            name="Performance Review",
            version="1.0.0"
        )
        
        # Replace with performance-focused sections
        template['sections'] = [
            self._create_algorithmic_efficiency_section(),
            self._create_resource_usage_section(),
            self._create_scalability_section(),
            self._create_caching_section(),
            self._create_optimization_section()
        ]
        
        template['metadata']['tags'] = ['performance', 'optimization', 'scalability']
        template['metadata']['recommendedFrequency'] = 'release'
        template['metadata']['estimatedDuration'] = '2-3hours'
        
        return template

    def get_accessibility_review_template(self) -> Dict[str, Any]:
        """
        Get a template for accessibility reviews.
        
        Returns:
            Template dictionary
        """
        template = self.factory.create_code_review_template(
            name="Accessibility Review",
            version="1.0.0"
        )
        
        # Replace with accessibility-focused sections
        template['sections'] = [
            self._create_wcag_compliance_section(),
            self._create_keyboard_navigation_section(),
            self._create_screen_reader_section(),
            self._create_visual_accessibility_section(),
            self._create_cognitive_accessibility_section()
        ]
        
        template['metadata']['tags'] = ['accessibility', 'wcag', 'a11y']
        template['metadata']['recommendedFrequency'] = 'feature'
        template['metadata']['estimatedDuration'] = '1-2hours'
        
        return template

    def get_api_review_template(self) -> Dict[str, Any]:
        """
        Get a template for API reviews.
        
        Returns:
            Template dictionary
        """
        template = self.factory.create_code_review_template(
            name="API Review",
            version="1.0.0"
        )
        
        # Replace with API-focused sections
        template['sections'] = [
            self._create_api_design_section(),
            self._create_api_security_section(),
            self._create_api_documentation_section(),
            self._create_api_testing_section(),
            self._create_api_versioning_section()
        ]
        
        template['metadata']['tags'] = ['api', 'rest', 'endpoints']
        template['metadata']['recommendedFrequency'] = 'per-endpoint'
        template['metadata']['estimatedDuration'] = '30-60min'
        
        return template

    def _create_algorithmic_efficiency_section(self) -> Dict[str, Any]:
        """Create a section for algorithmic efficiency review."""
        questions = [
            self.factory.validator.create_question(
                text="What is the time complexity of the implementation?",
                type="text",
                required=True,
                metadata={'hint': "Analyze Big O notation for key operations"}
            ),
            self.factory.validator.create_question(
                text="Are there opportunities for algorithmic optimization?",
                type="text",
                required=True,
                metadata={'hint': "Consider alternative algorithms or data structures"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="Algorithmic Efficiency",
            description="Evaluate the computational efficiency of the implementation",
            questions=questions
        )

    def _create_resource_usage_section(self) -> Dict[str, Any]:
        """Create a section for resource usage review."""
        questions = [
            self.factory.validator.create_question(
                text="How efficient is the memory usage?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Consider memory allocation, deallocation, and potential leaks",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="Are system resources used appropriately?",
                type="text",
                required=True,
                metadata={'hint': "Review CPU, memory, disk, and network usage"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="Resource Usage",
            description="Assess the efficiency of resource utilization",
            questions=questions
        )

    def _create_caching_section(self) -> Dict[str, Any]:
        """Create a section for caching review."""
        questions = [
            self.factory.validator.create_question(
                text="Is caching implemented effectively?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Evaluate cache strategy, invalidation, and hit rates",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What caching improvements could be made?",
                type="text",
                required=True,
                metadata={'hint': "Suggest caching optimizations"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="Caching",
            description="Review caching implementation and effectiveness",
            questions=questions
        )

    def _create_optimization_section(self) -> Dict[str, Any]:
        """Create a section for optimization review."""
        questions = [
            self.factory.validator.create_question(
                text="What performance optimizations are implemented?",
                type="text",
                required=True,
                metadata={'hint': "List current optimization techniques"}
            ),
            self.factory.validator.create_question(
                text="Are there additional optimization opportunities?",
                type="text",
                required=True,
                metadata={'hint': "Suggest potential performance improvements"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="Optimization",
            description="Evaluate performance optimization opportunities",
            questions=questions
        )

    def _create_wcag_compliance_section(self) -> Dict[str, Any]:
        """Create a section for WCAG compliance review."""
        questions = [
            self.factory.validator.create_question(
                text="Does the implementation meet WCAG 2.1 standards?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check against WCAG 2.1 success criteria",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What WCAG compliance issues need to be addressed?",
                type="text",
                required=True,
                metadata={'hint': "List specific WCAG violations and remediation steps"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="WCAG Compliance",
            description="Assess compliance with Web Content Accessibility Guidelines",
            questions=questions
        )

    def _create_keyboard_navigation_section(self) -> Dict[str, Any]:
        """Create a section for keyboard navigation review."""
        questions = [
            self.factory.validator.create_question(
                text="Is keyboard navigation fully supported?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check tab order, focus indicators, and keyboard shortcuts",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What keyboard navigation improvements are needed?",
                type="text",
                required=True,
                metadata={'hint': "Identify keyboard accessibility issues"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="Keyboard Navigation",
            description="Evaluate keyboard accessibility support",
            questions=questions
        )

    def _create_screen_reader_section(self) -> Dict[str, Any]:
        """Create a section for screen reader compatibility review."""
        questions = [
            self.factory.validator.create_question(
                text="How well does the implementation work with screen readers?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Test with popular screen readers (NVDA, VoiceOver, etc.)",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What screen reader compatibility issues exist?",
                type="text",
                required=True,
                metadata={'hint': "Document screen reader testing results"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="Screen Reader Compatibility",
            description="Assess compatibility with screen readers",
            questions=questions
        )

    def _create_visual_accessibility_section(self) -> Dict[str, Any]:
        """Create a section for visual accessibility review."""
        questions = [
            self.factory.validator.create_question(
                text="Does the implementation meet color contrast requirements?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check color contrast ratios against WCAG standards",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What visual accessibility improvements are needed?",
                type="text",
                required=True,
                metadata={'hint': "Identify issues with color, contrast, and visual presentation"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="Visual Accessibility",
            description="Evaluate visual accessibility considerations",
            questions=questions
        )

    def _create_cognitive_accessibility_section(self) -> Dict[str, Any]:
        """Create a section for cognitive accessibility review."""
        questions = [
            self.factory.validator.create_question(
                text="How well does the implementation support cognitive accessibility?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Consider readability, predictability, and error prevention",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What cognitive accessibility improvements are needed?",
                type="text",
                required=True,
                metadata={'hint': "Suggest improvements for cognitive accessibility"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="Cognitive Accessibility",
            description="Assess support for cognitive accessibility",
            questions=questions
        )

    def _create_api_design_section(self) -> Dict[str, Any]:
        """Create a section for API design review."""
        questions = [
            self.factory.validator.create_question(
                text="Does the API follow RESTful principles?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check resource naming, HTTP methods, and status codes",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What API design improvements would you suggest?",
                type="text",
                required=True,
                metadata={'hint': "Suggest improvements to API design"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="API Design",
            description="Evaluate API design and RESTful principles",
            questions=questions
        )

    def _create_api_security_section(self) -> Dict[str, Any]:
        """Create a section for API security review."""
        questions = [
            self.factory.validator.create_question(
                text="How secure is the API implementation?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check authentication, authorization, and data protection",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What API security improvements are needed?",
                type="text",
                required=True,
                metadata={'hint': "Identify API security vulnerabilities"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="API Security",
            description="Assess API security measures",
            questions=questions
        )

    def _create_api_documentation_section(self) -> Dict[str, Any]:
        """Create a section for API documentation review."""
        questions = [
            self.factory.validator.create_question(
                text="Is the API well-documented?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check OpenAPI/Swagger docs, examples, and error responses",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What documentation improvements are needed?",
                type="text",
                required=True,
                metadata={'hint': "Suggest improvements to API documentation"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="API Documentation",
            description="Evaluate API documentation quality",
            questions=questions
        )

    def _create_api_testing_section(self) -> Dict[str, Any]:
        """Create a section for API testing review."""
        questions = [
            self.factory.validator.create_question(
                text="How thoroughly is the API tested?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check unit tests, integration tests, and test coverage",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What additional API tests are needed?",
                type="text",
                required=True,
                metadata={'hint': "Suggest additional test cases or scenarios"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="API Testing",
            description="Assess API test coverage and quality",
            questions=questions
        )

    def _create_api_versioning_section(self) -> Dict[str, Any]:
        """Create a section for API versioning review."""
        questions = [
            self.factory.validator.create_question(
                text="Is API versioning properly implemented?",
                type="rating",
                required=True,
                metadata={
                    'hint': "Check version strategy, backwards compatibility, and deprecation",
                    'ratingScale': {'min': 1, 'max': 5}
                }
            ),
            self.factory.validator.create_question(
                text="What versioning improvements are needed?",
                type="text",
                required=True,
                metadata={'hint': "Suggest improvements to API versioning"}
            )
        ]
        
        return self.factory.validator.create_section(
            title="API Versioning",
            description="Evaluate API versioning strategy",
            questions=questions
        ) 