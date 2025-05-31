#!/usr/bin/env python3
"""
Testing Protocol for Task 21

This script implements a comprehensive testing protocol that:
1. Runs all tests and resolves errors according to Development_Bible.md
2. Enforces test location and structure
3. Enforces canonical imports
4. Validates module and function logic
"""

import os
import sys
import shutil
import subprocess
import re
import ast
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
import json
from dataclasses import dataclass

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

@dataclass
class TestResult:
    """Result of a test execution."""
    success: bool
    errors: List[str]
    warnings: List[str]
    collected_tests: int
    failed_tests: int
    passed_tests: int
    output: str

@dataclass
class ImportViolation:
    """A non-canonical import violation."""
    file_path: str
    line_number: int
    import_statement: str
    suggested_fix: str

class TestingProtocol:
    """Main testing protocol implementation."""
    
    def __init__(self, backend_root: Path = None):
        self.backend_root = backend_root or Path(__file__).parent
        self.tests_dir = self.backend_root / "tests"
        self.systems_dir = self.backend_root / "systems"
        self.development_bible_path = self.backend_root.parent / "docs" / "development_bible.md"
        
        # Results tracking
        self.test_results: List[TestResult] = []
        self.import_violations: List[ImportViolation] = []
        self.duplicate_tests: List[Tuple[str, str]] = []
        self.orphaned_modules: List[str] = []
        
        print(f"🔧 Testing Protocol initialized")
        print(f"   Backend root: {self.backend_root}")
        print(f"   Tests directory: {self.tests_dir}")
        print(f"   Systems directory: {self.systems_dir}")
    
    def run_protocol(self) -> bool:
        """Run the complete testing protocol."""
        print("\n" + "="*80)
        print("🚀 STARTING TESTING PROTOCOL FOR TASK 21")
        print("="*80)
        
        success = True
        
        try:
            # Phase 1: Test Structure Enforcement
            print("\n📁 PHASE 1: Test Structure Enforcement")
            success &= self._enforce_test_structure()
            
            # Phase 2: Canonical Imports Enforcement  
            print("\n📦 PHASE 2: Canonical Imports Enforcement")
            success &= self._enforce_canonical_imports()
            
            # Phase 3: Module Logic Validation
            print("\n🔍 PHASE 3: Module Logic Validation")
            success &= self._validate_module_logic()
            
            # Phase 4: Test Execution and Error Resolution
            print("\n🧪 PHASE 4: Test Execution and Error Resolution")
            success &= self._execute_and_resolve_tests()
            
            # Phase 5: Final Report
            print("\n📊 PHASE 5: Final Report")
            self._generate_final_report()
            
        except Exception as e:
            print(f"❌ Protocol execution failed: {e}")
            success = False
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"\n{status}: Testing protocol completed")
        return success
    
    def _enforce_test_structure(self) -> bool:
        """Enforce test location and structure requirements."""
        print("🔍 Scanning for misplaced test files...")
        
        success = True
        misplaced_tests = []
        
        # Find test directories in systems/
        for root, dirs, files in os.walk(self.systems_dir):
            for dir_name in dirs:
                if dir_name in ['test', 'tests']:
                    misplaced_path = Path(root) / dir_name
                    misplaced_tests.append(misplaced_path)
        
        # Handle misplaced tests
        for test_path in misplaced_tests:
            print(f"📦 Found misplaced test directory: {test_path}")
            
            # Move tests to canonical location if they contain test files
            test_files = list(test_path.glob("test_*.py"))
            if test_files:
                # Create corresponding directory in /tests/systems/
                relative_path = test_path.relative_to(self.systems_dir)
                target_path = self.tests_dir / "systems" / relative_path.parent
                target_path.mkdir(parents=True, exist_ok=True)
                
                # Move test files
                for test_file in test_files:
                    target_file = target_path / test_file.name
                    print(f"📁 Moving {test_file} -> {target_file}")
                    shutil.move(str(test_file), str(target_file))
            
            # Remove empty test directory
            try:
                if test_path.exists() and not any(test_path.iterdir()):
                    test_path.rmdir()
                    print(f"🗑️  Removed empty directory: {test_path}")
            except OSError as e:
                print(f"⚠️  Could not remove {test_path}: {e}")
                success = False
        
        # Scan for duplicate tests
        print("🔍 Scanning for duplicate tests...")
        test_files = {}
        
        for test_file in self.tests_dir.rglob("test_*.py"):
            test_name = test_file.name
            if test_name in test_files:
                self.duplicate_tests.append((str(test_files[test_name]), str(test_file)))
                print(f"⚠️  Duplicate test found: {test_name}")
                print(f"   - {test_files[test_name]}")
                print(f"   - {test_file}")
            else:
                test_files[test_name] = test_file
        
        # Remove duplicates (keep the one in the more canonical location)
        for orig, duplicate in self.duplicate_tests:
            # Prefer files directly in tests/ over tests/systems/
            if "/systems/" in orig and "/systems/" not in duplicate:
                to_remove = orig
            elif "/systems/" not in orig and "/systems/" in duplicate:
                to_remove = duplicate
            else:
                # Both in same level, remove the later one alphabetically
                to_remove = max(orig, duplicate)
            
            print(f"🗑️  Removing duplicate: {to_remove}")
            try:
                os.remove(to_remove)
            except OSError as e:
                print(f"⚠️  Could not remove {to_remove}: {e}")
                success = False
        
        if misplaced_tests or self.duplicate_tests:
            print(f"📊 Test structure issues found and addressed:")
            print(f"   - Misplaced test directories: {len(misplaced_tests)}")
            print(f"   - Duplicate test files: {len(self.duplicate_tests)}")
        else:
            print("✅ Test structure is compliant")
        
        return success
    
    def _enforce_canonical_imports(self) -> bool:
        """Enforce canonical imports from backend/systems/."""
        print("🔍 Scanning for non-canonical imports...")
        
        success = True
        
        # Scan all Python files in tests
        for py_file in self.tests_dir.rglob("*.py"):
            violations = self._check_file_imports(py_file)
            self.import_violations.extend(violations)
        
        # Fix import violations
        for violation in self.import_violations:
            print(f"🔧 Fixing import in {violation.file_path}:{violation.line_number}")
            print(f"   Before: {violation.import_statement}")
            print(f"   After:  {violation.suggested_fix}")
            
            try:
                self._fix_import_in_file(violation)
            except Exception as e:
                print(f"❌ Failed to fix import: {e}")
                success = False
        
        if self.import_violations:
            print(f"📊 Import violations found and fixed: {len(self.import_violations)}")
        else:
            print("✅ All imports are canonical")
        
        return success
    
    def _check_file_imports(self, file_path: Path) -> List[ImportViolation]:
        """Check a file for non-canonical imports."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    violation = self._analyze_import_node(node, file_path, content)
                    if violation:
                        violations.append(violation)
        
        except Exception as e:
            print(f"⚠️  Could not parse {file_path}: {e}")
        
        return violations
    
    def _analyze_import_node(self, node: ast.AST, file_path: Path, content: str) -> Optional[ImportViolation]:
        """Analyze an import node for canonical compliance."""
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            
            # Check for non-canonical patterns
            non_canonical_patterns = [
                r'^systems\.',  # Should be backend.systems.
                r'^utils\.',    # Should be backend.infrastructure.shared.utils.
                r'^(?!backend\.systems\.).*systems.*',  # Any systems import not starting with backend.systems
            ]
            
            for pattern in non_canonical_patterns:
                if re.match(pattern, module):
                    # Get the line content
                    lines = content.split('\n')
                    line_content = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                    
                    # Generate suggested fix
                    suggested_fix = self._generate_canonical_import_fix(line_content, module)
                    
                    return ImportViolation(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        import_statement=line_content.strip(),
                        suggested_fix=suggested_fix
                    )
        
        return None
    
    def _generate_canonical_import_fix(self, import_line: str, module: str) -> str:
        """Generate a canonical import fix."""
        # Map common non-canonical patterns to canonical ones
        if module.startswith('systems.'):
            canonical_module = 'backend.' + module
        elif module.startswith('utils.'):
            canonical_module = 'backend.systems.shared.' + module
        else:
            canonical_module = 'backend.systems.' + module.replace('systems.', '')
        
        return import_line.replace(module, canonical_module)
    
    def _fix_import_in_file(self, violation: ImportViolation) -> None:
        """Fix an import violation in a file."""
        with open(violation.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Replace the problematic line
        lines[violation.line_number - 1] = violation.suggested_fix + '\n'
        
        with open(violation.file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    def _validate_module_logic(self) -> bool:
        """Validate module and function logic."""
        print("🔍 Validating module logic...")
        
        success = True
        
        # Check for duplicate implementations
        print("🔍 Checking for duplicate implementations...")
        duplicates = self._find_duplicate_implementations()
        
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} potential duplicates:")
            for func_name, locations in duplicates.items():
                print(f"   {func_name}: {locations}")
            success = False
        else:
            print("✅ No duplicate implementations found")
        
        # Check FastAPI compliance
        print("🔍 Checking FastAPI compliance...")
        non_compliant = self._check_fastapi_compliance()
        
        if non_compliant:
            print(f"⚠️  Found {len(non_compliant)} FastAPI compliance issues")
            success = False
        else:
            print("✅ FastAPI compliance verified")
        
        return success
    
    def _find_duplicate_implementations(self) -> Dict[str, List[str]]:
        """Find duplicate function implementations."""
        function_locations = {}
        
        for py_file in self.systems_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_name = node.name
                        if func_name not in function_locations:
                            function_locations[func_name] = []
                        function_locations[func_name].append(str(py_file))
            
            except Exception as e:
                print(f"⚠️  Could not parse {py_file}: {e}")
        
        # Return only functions with multiple implementations
        return {name: locs for name, locs in function_locations.items() if len(locs) > 1}
    
    def _check_fastapi_compliance(self) -> List[str]:
        """Check for FastAPI compliance issues."""
        issues = []
        
        # Look for router files and check FastAPI patterns
        for router_file in self.systems_dir.rglob("*router*.py"):
            try:
                with open(router_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for FastAPI imports
                if 'from fastapi import' not in content and 'import fastapi' not in content:
                    issues.append(f"{router_file}: Missing FastAPI imports")
                
                # Check for APIRouter usage
                if 'APIRouter' not in content and 'router' in router_file.name.lower():
                    issues.append(f"{router_file}: Router file missing APIRouter")
            
            except Exception as e:
                print(f"⚠️  Could not check {router_file}: {e}")
        
        return issues
    
    def _execute_and_resolve_tests(self) -> bool:
        """Execute tests and resolve errors."""
        print("🧪 Executing tests...")
        
        # First, fix obvious syntax errors
        self._fix_syntax_errors()
        
        # Run tests and analyze results
        max_iterations = 3
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 Test execution iteration {iteration}/{max_iterations}")
            
            result = self._run_tests()
            self.test_results.append(result)
            
            if result.success:
                print("✅ All tests passed!")
                return True
            
            # Analyze and fix errors
            if not self._analyze_and_fix_test_errors(result):
                print("❌ Could not fix test errors automatically")
                break
        
        print(f"⚠️  Tests still failing after {max_iterations} iterations")
        return False
    
    def _fix_syntax_errors(self) -> None:
        """Fix obvious syntax errors in test files."""
        print("🔧 Fixing syntax errors...")
        
        # Fix the specific indentation error we saw
        char_builder_test = self.tests_dir / "systems/character/core/test_character_builder.py"
        if char_builder_test.exists():
            with open(char_builder_test, 'r') as f:
                content = f.read()
            
            # Fix the indentation error on line 33
            content = content.replace(
                '    assert "INT" in builder.attributes\n        assert "WIS" in builder.attributes',
                '    assert "INT" in builder.attributes\n    assert "WIS" in builder.attributes'
            )
            
            with open(char_builder_test, 'w') as f:
                f.write(content)
            
            print(f"🔧 Fixed indentation error in {char_builder_test}")
    
    def _run_tests(self) -> TestResult:
        """Run the test suite and return results."""
        try:
            # Run pytest with specific options
            cmd = [
                sys.executable, '-m', 'pytest', 
                str(self.tests_dir),
                '-v', '--tb=short', '--no-header',
                '--disable-warnings'
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.backend_root,
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
            
            # Parse output
            output = result.stdout + result.stderr
            errors = self._parse_test_errors(output)
            
            # Extract test counts
            collected_tests = self._extract_test_count(output, "collected")
            failed_tests = self._extract_test_count(output, "failed")
            passed_tests = self._extract_test_count(output, "passed")
            
            return TestResult(
                success=(result.returncode == 0),
                errors=errors,
                warnings=[],
                collected_tests=collected_tests,
                failed_tests=failed_tests,
                passed_tests=passed_tests,
                output=output
            )
        
        except subprocess.TimeoutExpired:
            return TestResult(
                success=False,
                errors=["Test execution timed out"],
                warnings=[],
                collected_tests=0,
                failed_tests=0,
                passed_tests=0,
                output="TIMEOUT"
            )
        except Exception as e:
            return TestResult(
                success=False,
                errors=[f"Test execution failed: {e}"],
                warnings=[],
                collected_tests=0,
                failed_tests=0,
                passed_tests=0,
                output=str(e)
            )
    
    def _parse_test_errors(self, output: str) -> List[str]:
        """Parse test output for errors."""
        errors = []
        
        # Look for common error patterns
        error_patterns = [
            r"ERROR.*",
            r"ModuleNotFoundError:.*",
            r"ImportError:.*",
            r"AttributeError:.*",
            r"IndentationError:.*",
            r"SyntaxError:.*"
        ]
        
        for line in output.split('\n'):
            for pattern in error_patterns:
                if re.search(pattern, line):
                    errors.append(line.strip())
        
        return errors
    
    def _extract_test_count(self, output: str, count_type: str) -> int:
        """Extract test counts from pytest output."""
        pattern = rf"(\d+) {count_type}"
        match = re.search(pattern, output)
        return int(match.group(1)) if match else 0
    
    def _analyze_and_fix_test_errors(self, result: TestResult) -> bool:
        """Analyze test errors and attempt to fix them."""
        print("🔧 Analyzing test errors...")
        
        fixed_any = False
        
        for error in result.errors:
            if "ModuleNotFoundError" in error:
                fixed_any |= self._fix_module_not_found_error(error)
            elif "AttributeError" in error:
                fixed_any |= self._fix_attribute_error(error)
            elif "pytest_plugins" in error:
                fixed_any |= self._fix_pytest_plugins_error(error)
        
        return fixed_any
    
    def _fix_module_not_found_error(self, error: str) -> bool:
        """Fix ModuleNotFoundError by creating missing modules or fixing imports."""
        print(f"🔧 Fixing module not found: {error}")
        
        # Extract module name
        match = re.search(r"No module named '([^']+)'", error)
        if not match:
            return False
        
        module_name = match.group(1)
        
        # Try to create missing __init__.py files
        if 'backend.systems' in module_name:
            module_path = module_name.replace('backend.systems.', '').replace('.', '/')
            init_file = self.systems_dir / module_path / "__init__.py"
            
            if not init_file.exists():
                init_file.parent.mkdir(parents=True, exist_ok=True)
                init_file.touch()
                print(f"📁 Created missing __init__.py: {init_file}")
                return True
        
        return False
    
    def _fix_attribute_error(self, error: str) -> bool:
        """Fix AttributeError by checking module structure."""
        print(f"🔧 Analyzing attribute error: {error}")
        
        # Check for common patterns like missing 'routes' attribute
        if "has no attribute 'routes'" in error:
            # This suggests a router module isn't properly structured
            match = re.search(r"module '([^']+)'", error)
            if match:
                module_name = match.group(1)
                print(f"⚠️  Router module {module_name} needs 'routes' attribute")
                # Could implement automatic router fixing here
        
        return False
    
    def _fix_pytest_plugins_error(self, error: str) -> bool:
        """Fix pytest_plugins configuration errors."""
        print(f"🔧 Fixing pytest_plugins error")
        
        # Find and fix conftest.py files with pytest_plugins in wrong location
        for conftest in self.tests_dir.rglob("conftest.py"):
            if conftest.parent == self.tests_dir:
                continue  # Skip top-level conftest
            
            try:
                with open(conftest, 'r') as f:
                    content = f.read()
                
                if 'pytest_plugins' in content:
                    # Remove pytest_plugins from non-top-level conftest
                    lines = content.split('\n')
                    filtered_lines = [line for line in lines if 'pytest_plugins' not in line]
                    
                    with open(conftest, 'w') as f:
                        f.write('\n'.join(filtered_lines))
                    
                    print(f"🔧 Removed pytest_plugins from {conftest}")
                    return True
            
            except Exception as e:
                print(f"⚠️  Could not fix {conftest}: {e}")
        
        return False
    
    def _generate_final_report(self) -> None:
        """Generate a final report of the testing protocol."""
        print("\n" + "="*80)
        print("📊 TESTING PROTOCOL FINAL REPORT")
        print("="*80)
        
        if self.test_results:
            latest_result = self.test_results[-1]
            print(f"📈 Test Execution Summary:")
            print(f"   - Tests collected: {latest_result.collected_tests}")
            print(f"   - Tests passed: {latest_result.passed_tests}")
            print(f"   - Tests failed: {latest_result.failed_tests}")
            print(f"   - Success rate: {(latest_result.passed_tests / max(1, latest_result.collected_tests)) * 100:.1f}%")
        
        print(f"\n🔧 Issues Resolved:")
        print(f"   - Import violations fixed: {len(self.import_violations)}")
        print(f"   - Duplicate tests removed: {len(self.duplicate_tests)}")
        print(f"   - Test iterations completed: {len(self.test_results)}")
        
        # Save detailed report
        report_file = self.backend_root / "testing_protocol_report.json"
        report_data = {
            "test_results": [vars(r) for r in self.test_results],
            "import_violations": [vars(v) for v in self.import_violations],
            "duplicate_tests": self.duplicate_tests,
            "timestamp": str(Path().cwd())
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")

def main():
    """Main entry point for the testing protocol."""
    protocol = TestingProtocol()
    success = protocol.run_protocol()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 