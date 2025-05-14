import sys
import os

# Support both package and direct script import
if __package__ is None and __name__ == "service":
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from metrics import CodeQualityMetrics
else:
    from .metrics import CodeQualityMetrics

from typing import Optional, Dict, Any, List

class CodeQualityService:
    """
    Service for analyzing code quality and generating reports.
    Supports dependency injection for analyzer strategies.
    """
    def __init__(self, *analyzers, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the service with optional analyzers and configuration.
        Args:
            analyzers: Analyzer strategy instances.
            config: Optional configuration dictionary.
        """
        self.analyzers = analyzers
        self.config = config or {}

    def analyze_codebase(self, path: str) -> CodeQualityMetrics:
        """
        Analyze the codebase at the given path and return code quality metrics.
        Args:
            path: Path to the codebase root directory.
        Returns:
            CodeQualityMetrics: Aggregated metrics for the codebase.
        """
        # Placeholder: return default metrics for now
        return CodeQualityMetrics()

    def generate_report(self, metrics: CodeQualityMetrics, format_type: str = 'text') -> str:
        """
        Generate a report from the given metrics.
        Args:
            metrics: CodeQualityMetrics object.
            format_type: Output format ('text', 'json', etc.).
        Returns:
            str: Formatted report string.
        """
        if format_type == 'text':
            return self._generate_text_report(metrics)
        # Future: add support for other formats
        return str(metrics)

    def _generate_text_report(self, metrics: CodeQualityMetrics) -> str:
        """
        Generate a human-readable text report from metrics.
        Args:
            metrics: CodeQualityMetrics object.
        Returns:
            str: Text report.
        """
        lines = [
            'Code Quality Report:',
            f'Readability: {metrics.readability}',
            f'Best Practices: {metrics.best_practices}',
            f'Modularity: {metrics.modularity}',
            f'Maintainability: {metrics.maintainability}',
            f'Performance: {metrics.performance}',
            f'Error Handling: {metrics.error_handling}',
            f'Documentation: {metrics.documentation}',
            f'Overall Score: {metrics.overall_score}',
        ]
        return '\n'.join(lines) 