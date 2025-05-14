from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ReadabilityMetrics:
    """Metrics related to code readability."""
    formatting_consistency: float = 0.0  # 0-100
    naming_conventions: float = 0.0      # 0-100
    complexity_score: float = 0.0        # Lower is better
    avg_line_length: float = 0.0
    comment_density: float = 0.0
    readability_index: float = 0.0

@dataclass
class BestPracticesMetrics:
    """Metrics related to adherence to best practices."""
    lint_violations: int = 0
    naming_convention_score: float = 0.0
    deprecated_usage_count: int = 0
    code_style_adherence: float = 0.0

@dataclass
class ModularityMetrics:
    """Metrics related to code modularity."""
    coupling_score: float = 0.0
    cohesion_score: float = 0.0
    module_count: int = 0
    dependency_count: int = 0

@dataclass
class MaintainabilityMetrics:
    """Metrics related to code maintainability."""
    cyclomatic_complexity: float = 0.0
    code_duplication_percentage: float = 0.0
    test_coverage: float = 0.0
    change_impact_score: float = 0.0

@dataclass
class PerformanceMetrics:
    """Metrics related to code performance."""
    algorithm_efficiency_score: float = 0.0
    resource_usage_flags: Dict[str, bool] = field(default_factory=dict)
    optimization_opportunities: int = 0

@dataclass
class ErrorHandlingMetrics:
    """Metrics related to error handling and fault tolerance."""
    exception_handling_coverage: float = 0.0
    error_recovery_score: float = 0.0
    fault_tolerance_rating: float = 0.0

@dataclass
class DocumentationMetrics:
    """Metrics related to code documentation."""
    docstring_coverage: float = 0.0
    api_documentation_completeness: float = 0.0
    comment_quality_score: float = 0.0

@dataclass
class CodeQualityMetrics:
    """Composite metrics for overall code quality assessment."""
    readability: ReadabilityMetrics = field(default_factory=ReadabilityMetrics)
    best_practices: BestPracticesMetrics = field(default_factory=BestPracticesMetrics)
    modularity: ModularityMetrics = field(default_factory=ModularityMetrics)
    maintainability: MaintainabilityMetrics = field(default_factory=MaintainabilityMetrics)
    performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    error_handling: ErrorHandlingMetrics = field(default_factory=ErrorHandlingMetrics)
    documentation: DocumentationMetrics = field(default_factory=DocumentationMetrics)
    overall_score: float = 0.0 