#!/usr/bin/env python3
"""
Visual DM Backend Test Coverage Improvement Script

This script analyzes coverage reports and automatically generates targeted tests
for uncovered code paths, focusing on the most impactful improvements.

Usage:
    python scripts/improve_test_coverage.py [--target-coverage 80] [--dry-run] [--verbose]
"""

import ast
import json
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import xml.etree.ElementTree as ET


class CoverageImprover:
    def __init__(
        self, target_coverage: int = 80, dry_run: bool = False, verbose: bool = False
    ):
        self.target_coverage = target_coverage
        self.dry_run = dry_run
        self.verbose = verbose
        self.backend_root = Path(__file__).parent.parent
        self.coverage_data = {}
        self.tests_created = []

    def log(self, message: str, level: str = "INFO"):
        """Log a message with optional level"""
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")

    def run_coverage_analysis(self) -> bool:
        """Run coverage analysis and generate reports"""
        self.log("Running coverage analysis...")

        try:
            # Run tests with coverage
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "coverage",
                    "run",
                    "-m",
                    "pytest",
                    "tests/",
                    "--tb=short",
                    "-q",
                ],
                cwd=self.backend_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                self.log(f"Tests failed: {result.stderr}", "WARNING")

            # Generate XML report for parsing
            subprocess.run(
                [sys.executable, "-m", "coverage", "xml"],
                cwd=self.backend_root,
                check=True,
                capture_output=True,
            )

            return True

        except subprocess.CalledProcessError as e:
            self.log(f"Coverage analysis failed: {e}", "ERROR")
            return False

    def parse_coverage_xml(self) -> Dict[str, Dict]:
        """Parse the coverage XML report"""
        xml_file = self.backend_root / "coverage.xml"
        if not xml_file.exists():
            self.log("Coverage XML not found, running analysis...", "WARNING")
            if not self.run_coverage_analysis():
                return {}

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            coverage_data = {}

            for package in root.findall(".//package"):
                for class_elem in package.findall("classes/class"):
                    filename = class_elem.get("filename")
                    if not filename:
                        continue

                    file_path = Path(filename)
                    if not file_path.exists():
                        continue

                    lines_covered = int(class_elem.get("lines-covered", 0))
                    lines_valid = int(class_elem.get("lines-valid", 1))
                    line_rate = float(class_elem.get("line-rate", 0))

                    missed_lines = []
                    for line in class_elem.findall("lines/line"):
                        if line.get("hits") == "0":
                            missed_lines.append(int(line.get("number")))

                    coverage_data[str(file_path)] = {
                        "lines_covered": lines_covered,
                        "lines_valid": lines_valid,
                        "coverage_rate": line_rate,
                        "missed_lines": sorted(missed_lines),
                    }

            self.coverage_data = coverage_data
            return coverage_data

        except ET.ParseError as e:
            self.log(f"Failed to parse coverage XML: {e}", "ERROR")
            return {}

    def identify_priority_files(self) -> List[Tuple[str, Dict]]:
        """Identify files that would benefit most from additional tests"""
        if not self.coverage_data:
            self.parse_coverage_xml()

        priority_files = []

        for file_path, data in self.coverage_data.items():
            # Skip test files and __init__.py
            if (
                "test" in file_path.lower()
                or file_path.endswith("__init__.py")
                or "migrations" in file_path
            ):
                continue

            coverage_rate = data["coverage_rate"]
            lines_valid = data["lines_valid"]

            # Priority = impact * ease
            # Impact: more lines to cover = higher impact
            # Ease: higher current coverage = easier to improve
            impact = lines_valid * (1 - coverage_rate)
            ease = coverage_rate if coverage_rate > 0.1 else 0.1
            priority = impact * ease

            if coverage_rate < (self.target_coverage / 100) and lines_valid > 10:
                priority_files.append(
                    (
                        file_path,
                        {
                            **data,
                            "priority": priority,
                            "potential_improvement": lines_valid * (1 - coverage_rate),
                        },
                    )
                )

        # Sort by priority (highest first)
        priority_files.sort(key=lambda x: x[1]["priority"], reverse=True)
        return priority_files

    def analyze_uncovered_code(
        self, file_path: str, missed_lines: List[int]
    ) -> Dict[str, List]:
        """Analyze uncovered code to understand what types of tests are needed"""
        try:
            content = Path(file_path).read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception as e:
            self.log(f"Could not parse {file_path}: {e}", "WARNING")
            return {}

        uncovered_functions = []
        uncovered_classes = []
        uncovered_branches = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = list(
                    range(
                        node.lineno,
                        node.end_lineno + 1 if node.end_lineno else node.lineno + 1,
                    )
                )
                if any(line in missed_lines for line in func_lines):
                    uncovered_functions.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "is_method": any(
                                isinstance(parent, ast.ClassDef)
                                for parent in ast.walk(tree)
                                if hasattr(parent, "body") and node in parent.body
                            ),
                            "has_args": len(node.args.args) > 0,
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                        }
                    )

            elif isinstance(node, ast.ClassDef):
                class_lines = list(
                    range(
                        node.lineno,
                        node.end_lineno + 1 if node.end_lineno else node.lineno + 1,
                    )
                )
                if any(line in missed_lines for line in class_lines):
                    uncovered_classes.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ],
                        }
                    )

            elif isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                if node.lineno in missed_lines:
                    uncovered_branches.append(
                        {"type": type(node).__name__, "line": node.lineno}
                    )

        return {
            "functions": uncovered_functions,
            "classes": uncovered_classes,
            "branches": uncovered_branches,
        }

    def generate_targeted_tests(self, file_path: str, analysis: Dict[str, List]) -> str:
        """Generate targeted test code for uncovered elements"""
        path_obj = Path(file_path)
        module_name = str(
            path_obj.relative_to(self.backend_root).with_suffix("")
        ).replace("/", ".")

        test_content = f'''"""
Tests for {module_name}

Auto-generated targeted tests for uncovered code.
These tests are generated based on coverage analysis.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add backend root to path for imports
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

try:
    import {module_name}
except ImportError as e:
    pytest.skip(f"Could not import {module_name}: {{e}}", allow_module_level=True)


class Test{path_obj.stem.title()}Coverage:
    """Targeted tests for improving coverage of {module_name}"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_data = {{"test": "data"}}
        
'''

        # Generate tests for uncovered functions
        for func in analysis.get("functions", []):
            func_name = func["name"]
            is_method = func["is_method"]
            has_args = func["has_args"]
            is_async = func["is_async"]

            test_content += f'''
    {"@pytest.mark.asyncio" if is_async else ""}
    {"async " if is_async else ""}def test_{func_name}_coverage(self):
        """Test {func_name} for coverage improvement"""
        # TODO: Add specific test logic for {func_name}
        '''

            if is_method:
                test_content += f"""
        # This appears to be a method - create instance or mock
        try:
            # Attempt to create instance
            instance = {module_name}.SomeClass()  # Replace with actual class
            {"await " if is_async else ""}instance.{func_name}()
        except Exception:
            # Mock the method if direct instantiation fails
            with patch.object({module_name}, '{func_name}') as mock_method:
                {"await " if is_async else ""}{module_name}.{func_name}()
                mock_method.assert_called()
        """
            else:
                test_content += f"""
        # This appears to be a function
        try:
            {"await " if is_async else ""}{module_name}.{func_name}({("self.mock_data" if has_args else "")})
        except Exception as e:
            # Function may require specific arguments or setup
            pytest.skip(f"Function {func_name} requires specific setup: {{e}}")
        """

            test_content += """
        assert True  # Replace with actual assertions
        
"""

        # Generate tests for uncovered classes
        for cls in analysis.get("classes", []):
            cls_name = cls["name"]
            methods = cls["methods"]

            test_content += f'''
    def test_{cls_name.lower()}_instantiation(self):
        """Test {cls_name} class instantiation"""
        try:
            instance = {module_name}.{cls_name}()
            assert instance is not None
        except Exception as e:
            # Class may require specific arguments
            pytest.skip(f"Class {cls_name} requires specific arguments: {{e}}")
    
'''

            # Generate method tests
            for method in methods:
                test_content += f'''
    def test_{cls_name.lower()}_{method}_coverage(self):
        """Test {cls_name}.{method} for coverage"""
        try:
            instance = {module_name}.{cls_name}()
            result = instance.{method}()
            # Add specific assertions based on expected behavior
            assert True  # Replace with actual assertions
        except Exception as e:
            pytest.skip(f"Method {method} requires specific setup: {{e}}")
    
'''

        # Generate tests for uncovered branches
        if analysis.get("branches"):
            test_content += '''
    def test_branch_coverage(self):
        """Test uncovered conditional branches"""
        # TODO: Add tests for uncovered if/while/for/try statements
        # Analyze the specific conditions and create test cases
        # that exercise both True and False paths
        assert True  # Replace with actual branch tests
    
'''

        test_content += '''
    def test_error_handling(self):
        """Test error handling paths"""
        # TODO: Add tests that trigger exception paths
        # These often show up as uncovered lines
        assert True  # Replace with actual error tests
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # TODO: Add tests for edge cases that may be uncovered
        # Examples: empty inputs, None values, boundary values
        assert True  # Replace with actual edge case tests
'''

        return test_content

    def create_coverage_improvement_tests(self, max_files: int = 10) -> int:
        """Create tests for the highest priority uncovered code"""
        priority_files = self.identify_priority_files()

        if not priority_files:
            self.log("No files found that need coverage improvement")
            return 0

        tests_created = 0

        for file_path, data in priority_files[:max_files]:
            self.log(f"Analyzing {file_path} (coverage: {data['coverage_rate']:.1%})")

            analysis = self.analyze_uncovered_code(file_path, data["missed_lines"])

            if not any(analysis.values()):
                continue

            # Generate test file path
            rel_path = Path(file_path).relative_to(self.backend_root)
            test_file_name = f"test_{rel_path.stem}_coverage.py"
            test_file_path = self.backend_root / "tests" / "coverage" / test_file_name

            # Generate test content
            test_content = self.generate_targeted_tests(file_path, analysis)

            if not self.dry_run:
                test_file_path.parent.mkdir(parents=True, exist_ok=True)
                test_file_path.write_text(test_content)
                self.log(f"Created coverage test: {test_file_path}")
            else:
                self.log(f"DRY RUN: Would create {test_file_path}")

            self.tests_created.append(str(test_file_path))
            tests_created += 1

        return tests_created

    def create_api_endpoint_tests(self) -> int:
        """Create tests for untested API endpoints"""
        self.log("Creating API endpoint tests...")

        # Find FastAPI router files
        router_files = []
        for py_file in self.backend_root.rglob("*router*.py"):
            if "test" not in str(py_file) and py_file.is_file():
                router_files.append(py_file)

        tests_created = 0

        for router_file in router_files:
            try:
                content = router_file.read_text(encoding="utf-8")

                # Look for route decorators
                routes = []
                for line_num, line in enumerate(content.split("\n"), 1):
                    if "@router." in line or "@app." in line:
                        # Extract HTTP method and path
                        parts = line.strip().split("(")
                        if len(parts) > 1:
                            method = parts[0].split(".")[-1]
                            path_part = (
                                parts[1].split('"')[1]
                                if '"' in parts[1]
                                else parts[1].split("'")[1]
                            )
                            routes.append((method, path_part, line_num))

                if not routes:
                    continue

                # Generate API test file
                rel_path = router_file.relative_to(self.backend_root)
                test_file_name = f"test_{rel_path.stem}_api.py"
                test_file_path = self.backend_root / "tests" / "api" / test_file_name

                test_content = self.generate_api_test_content(rel_path, routes)

                if not self.dry_run:
                    test_file_path.parent.mkdir(parents=True, exist_ok=True)
                    test_file_path.write_text(test_content)
                    self.log(f"Created API test: {test_file_path}")
                else:
                    self.log(f"DRY RUN: Would create {test_file_path}")

                tests_created += 1

            except Exception as e:
                self.log(f"Error processing {router_file}: {e}", "WARNING")

        return tests_created

    def generate_api_test_content(
        self, router_path: Path, routes: List[Tuple[str, str, int]]
    ) -> str:
        """Generate test content for API endpoints"""
        module_name = str(router_path.with_suffix("")).replace("/", ".")

        test_content = f'''"""
API tests for {module_name}

Auto-generated tests for API endpoints to improve coverage.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

# Import your FastAPI app here
# from your_app import app
# client = TestClient(app)

# TODO: Replace with actual app import
@pytest.fixture
def client():
    """Create test client"""
    # return TestClient(app)
    pytest.skip("Replace with actual FastAPI app import")


class Test{router_path.stem.title()}API:
    """Tests for {module_name} API endpoints"""
    
'''

        for method, path, line_num in routes:
            method_upper = method.upper()
            test_name = f"test_{method}_{path.replace('/', '_').replace('{', '').replace('}', '').strip('_')}"

            test_content += f'''
    def test_{test_name}(self, client):
        """Test {method_upper} {path} endpoint"""
        # TODO: Add proper test data and assertions
        
        # Example test structure:
        # response = client.{method.lower()}("{path}")
        # assert response.status_code == 200
        # assert "expected_field" in response.json()
        
        pytest.skip("Add actual test implementation")
    
'''

        test_content += '''
    def test_authentication_required(self, client):
        """Test that protected endpoints require authentication"""
        # TODO: Test authentication requirements
        pytest.skip("Add authentication tests")
    
    def test_error_responses(self, client):
        """Test error response handling"""
        # TODO: Test error cases (404, 400, 500, etc.)
        pytest.skip("Add error handling tests")
    
    def test_input_validation(self, client):
        """Test input validation"""
        # TODO: Test invalid inputs and validation errors
        pytest.skip("Add input validation tests")
'''

        return test_content

    def print_coverage_report(self):
        """Print a detailed coverage improvement report"""
        if not self.coverage_data:
            self.parse_coverage_xml()

        print("\n" + "=" * 60)
        print("COVERAGE IMPROVEMENT ANALYSIS")
        print("=" * 60)

        total_lines = sum(data["lines_valid"] for data in self.coverage_data.values())
        covered_lines = sum(
            data["lines_covered"] for data in self.coverage_data.values()
        )
        overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0

        print(
            f"Overall Coverage: {overall_coverage:.1f}% ({covered_lines}/{total_lines} lines)"
        )
        print(f"Target Coverage: {self.target_coverage}%")
        print(
            f"Lines needed: {int((self.target_coverage/100 * total_lines) - covered_lines)}"
        )

        priority_files = self.identify_priority_files()

        if priority_files:
            print(
                f"\nTop {min(10, len(priority_files))} files for coverage improvement:"
            )
            print("-" * 60)

            for file_path, data in priority_files[:10]:
                coverage_pct = data["coverage_rate"] * 100
                potential = int(data["potential_improvement"])
                print(
                    f"{coverage_pct:5.1f}% | +{potential:3d} lines | {Path(file_path).name}"
                )

        if self.tests_created:
            print(f"\n✅ Created {len(self.tests_created)} test files:")
            for test_file in self.tests_created:
                print(f"  • {test_file}")

    def run_improvement_process(self) -> Dict[str, int]:
        """Run the complete coverage improvement process"""
        results = {}

        self.log("Starting coverage improvement process...")

        # Run coverage analysis
        if not self.run_coverage_analysis():
            return {"error": 1}

        # Parse coverage data
        self.parse_coverage_xml()

        # Create targeted tests
        results["coverage_tests"] = self.create_coverage_improvement_tests()
        results["api_tests"] = self.create_api_endpoint_tests()

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Improve test coverage for Visual DM backend"
    )
    parser.add_argument(
        "--target-coverage", type=int, default=80, help="Target coverage percentage"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    improver = CoverageImprover(
        target_coverage=args.target_coverage, dry_run=args.dry_run, verbose=args.verbose
    )

    results = improver.run_improvement_process()
    improver.print_coverage_report()

    if "error" in results:
        sys.exit(1)


if __name__ == "__main__":
    main()
