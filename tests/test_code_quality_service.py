import sys
import os
import importlib.util
import pytest
from unittest.mock import Mock

CODE_QUALITY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/code_quality'))

# Dynamically import metrics.py
metrics_spec = importlib.util.spec_from_file_location("metrics", os.path.join(CODE_QUALITY_PATH, "metrics.py"))
metrics = importlib.util.module_from_spec(metrics_spec)
metrics_spec.loader.exec_module(metrics)

# Dynamically import service.py
service_spec = importlib.util.spec_from_file_location("service", os.path.join(CODE_QUALITY_PATH, "service.py"))
service = importlib.util.module_from_spec(service_spec)
service_spec.loader.exec_module(service)

def test_metrics_dataclasses_defaults():
    m = metrics.CodeQualityMetrics()
    assert isinstance(m.readability, metrics.ReadabilityMetrics)
    assert isinstance(m.best_practices, metrics.BestPracticesMetrics)
    assert isinstance(m.modularity, metrics.ModularityMetrics)
    assert isinstance(m.maintainability, metrics.MaintainabilityMetrics)
    assert isinstance(m.performance, metrics.PerformanceMetrics)
    assert isinstance(m.error_handling, metrics.ErrorHandlingMetrics)
    assert isinstance(m.documentation, metrics.DocumentationMetrics)

def test_code_quality_service_instantiation():
    s = service.CodeQualityService()
    assert isinstance(s, service.CodeQualityService)
    # With mock dependencies
    s2 = service.CodeQualityService(
        eslint_service=Mock(),
        complexity_analyzer=Mock(),
        documentation_checker=Mock(),
    )
    assert isinstance(s2, service.CodeQualityService)

def test_analyze_codebase_returns_default_metrics():
    s = service.CodeQualityService()
    m = s.analyze_codebase("/tmp")
    assert isinstance(m, metrics.CodeQualityMetrics)

def test_generate_report_returns_string():
    s = service.CodeQualityService()
    m = metrics.CodeQualityMetrics()
    report = s.generate_report(m)
    assert isinstance(report, str)
    assert "Code Quality Report" in report 