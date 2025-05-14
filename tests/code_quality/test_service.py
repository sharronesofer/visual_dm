import pytest
from unittest.mock import Mock
from app.code_quality.metrics import CodeQualityMetrics
from app.code_quality.service import CodeQualityService

def test_service_initialization():
    service = CodeQualityService()
    assert isinstance(service, CodeQualityService)
    assert hasattr(service, 'analyzers')
    assert hasattr(service, 'config')

def test_analyze_codebase_returns_default_metrics():
    service = CodeQualityService()
    metrics = service.analyze_codebase('.')
    assert isinstance(metrics, CodeQualityMetrics)
    # All metrics should be default values
    assert metrics.readability.complexity_score == 0.0
    assert metrics.best_practices.lint_violations == 0
    assert metrics.modularity.coupling_score == 0.0
    assert metrics.maintainability.cyclomatic_complexity == 0.0
    assert metrics.performance.algorithm_efficiency_score == 0.0
    assert metrics.error_handling.exception_handling_coverage == 0.0
    assert metrics.documentation.docstring_coverage == 0.0
    assert metrics.overall_score == 0.0

def test_generate_report_text_format():
    service = CodeQualityService()
    metrics = CodeQualityMetrics()
    report = service.generate_report(metrics, format_type='text')
    assert isinstance(report, str)
    assert 'Code Quality Report:' in report
    assert 'Readability:' in report
    assert 'Best Practices:' in report
    assert 'Overall Score:' in report

def test_generate_report_default_format():
    service = CodeQualityService()
    metrics = CodeQualityMetrics()
    report = service.generate_report(metrics, format_type='json')
    assert isinstance(report, str)
    # Should fallback to str(metrics) for unknown format
    assert 'ReadabilityMetrics' in report or 'readability' in report

def test_service_with_mock_analyzer():
    mock_analyzer = Mock()
    service = CodeQualityService(mock_analyzer)
    assert mock_analyzer in service.analyzers 