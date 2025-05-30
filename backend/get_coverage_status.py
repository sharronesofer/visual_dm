#!/usr/bin/env python3
"""
Backend Coverage Status Reporter

Generates a comprehensive report of the current backend testing status
including collection statistics, execution results, and coverage metrics.
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

class CoverageStatusReporter:
    def __init__(self, backend_root: str = None):
        self.backend_root = Path(backend_root or '.')
        self.report_data = {}
        
    def get_collection_stats(self):
        """Get test collection statistics"""
        print("📊 Analyzing test collection...")
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                '--collect-only', '-q'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                # Parse the collection summary line
                for line in lines:
                    if 'collected' in line and ('items' in line or 'errors' in line):
                        # Example: "collected 2918 items / 152 errors / 27 skipped"
                        parts = line.split('/')
                        collected_part = parts[0].strip()
                        
                        # Extract numbers
                        import re
                        collected_match = re.search(r'collected (\d+) items?', collected_part)
                        error_match = re.search(r'(\d+) errors?', line) if len(parts) > 1 else None
                        skip_match = re.search(r'(\d+) skipped', line) if len(parts) > 2 else None
                        
                        self.report_data['collection'] = {
                            'total_collected': int(collected_match.group(1)) if collected_match else 0,
                            'collection_errors': int(error_match.group(1)) if error_match else 0,
                            'skipped': int(skip_match.group(1)) if skip_match else 0,
                            'status': 'success'
                        }
                        break
            else:
                self.report_data['collection'] = {
                    'status': 'failed',
                    'error': result.stderr[:500]
                }
                
        except Exception as e:
            self.report_data['collection'] = {
                'status': 'error',
                'error': str(e)
            }
    
    def run_sample_execution(self):
        """Run a sample of tests to get execution statistics"""
        print("🧪 Running sample test execution...")
        
        try:
            # Run a small subset of tests
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                'tests/systems/analytics/', '-v', '--tb=short', '--maxfail=10'
            ], capture_output=True, text=True, timeout=60)
            
            # Parse the test results
            output_lines = result.stdout.split('\n')
            
            passed = failed = skipped = 0
            for line in output_lines:
                if ' PASSED ' in line:
                    passed += 1
                elif ' FAILED ' in line:
                    failed += 1
                elif ' SKIPPED ' in line:
                    skipped += 1
            
            self.report_data['sample_execution'] = {
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'total_run': passed + failed + skipped,
                'success_rate': round((passed / (passed + failed)) * 100, 1) if (passed + failed) > 0 else 0
            }
            
        except Exception as e:
            self.report_data['sample_execution'] = {
                'error': str(e)
            }
    
    def get_system_breakdown(self):
        """Get breakdown by system"""
        print("🔍 Analyzing test breakdown by system...")
        
        test_systems = {}
        tests_dir = self.backend_root / 'tests' / 'systems'
        
        if tests_dir.exists():
            for system_dir in tests_dir.iterdir():
                if system_dir.is_dir() and not system_dir.name.startswith('.'):
                    test_files = list(system_dir.glob('**/*test*.py'))
                    test_systems[system_dir.name] = len(test_files)
        
        self.report_data['system_breakdown'] = test_systems
    
    def check_critical_files(self):
        """Check for presence of critical backend files"""
        print("📋 Checking critical backend files...")
        
        critical_files = [
            'systems/world_generation/enums.py',
            'systems/shared/validation.py',
            'systems/shared/config.py',
            'tests/conftest.py',
            'pytest.ini'
        ]
        
        file_status = {}
        for file_path in critical_files:
            full_path = self.backend_root / file_path
            file_status[file_path] = {
                'exists': full_path.exists(),
                'size': full_path.stat().st_size if full_path.exists() else 0
            }
        
        self.report_data['critical_files'] = file_status
    
    def generate_recommendations(self):
        """Generate recommendations based on current status"""
        recommendations = []
        
        collection = self.report_data.get('collection', {})
        if collection.get('collection_errors', 0) > 0:
            recommendations.append(f"🔧 Fix {collection['collection_errors']} remaining collection errors")
        
        sample = self.report_data.get('sample_execution', {})
        if sample.get('success_rate', 0) < 80:
            recommendations.append(f"🎯 Improve test success rate (currently {sample.get('success_rate', 0)}%)")
        
        if collection.get('total_collected', 0) > 2500:
            recommendations.append("✅ Good test coverage - consider running full test suite")
        
        if len(recommendations) == 0:
            recommendations.append("✨ Testing infrastructure looks healthy!")
        
        self.report_data['recommendations'] = recommendations
    
    def print_report(self):
        """Print formatted coverage report"""
        print("\n" + "=" * 60)
        print("🎯 BACKEND TESTING COVERAGE STATUS REPORT")
        print("=" * 60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Collection Status
        collection = self.report_data.get('collection', {})
        print("📊 TEST COLLECTION STATUS")
        print("-" * 30)
        if collection.get('status') == 'success':
            print(f"✅ Total Tests Discovered: {collection.get('total_collected', 0):,}")
            print(f"❌ Collection Errors: {collection.get('collection_errors', 0)}")
            print(f"⏭️  Skipped Tests: {collection.get('skipped', 0)}")
            
            success_rate = 100 - (collection.get('collection_errors', 0) / max(collection.get('total_collected', 1), 1) * 100)
            print(f"📈 Collection Success Rate: {success_rate:.1f}%")
        else:
            print(f"❌ Collection Failed: {collection.get('error', 'Unknown error')}")
        print()
        
        # Sample Execution
        sample = self.report_data.get('sample_execution', {})
        if 'error' not in sample:
            print("🧪 SAMPLE TEST EXECUTION")
            print("-" * 30)
            print(f"✅ Passed: {sample.get('passed', 0)}")
            print(f"❌ Failed: {sample.get('failed', 0)}")
            print(f"⏭️  Skipped: {sample.get('skipped', 0)}")
            print(f"📊 Success Rate: {sample.get('success_rate', 0)}%")
            print()
        
        # System Breakdown
        systems = self.report_data.get('system_breakdown', {})
        if systems:
            print("🔍 SYSTEM TEST BREAKDOWN")
            print("-" * 30)
            sorted_systems = sorted(systems.items(), key=lambda x: x[1], reverse=True)
            for system, count in sorted_systems[:10]:  # Top 10
                print(f"{system:20} {count:3d} test files")
            print()
        
        # Critical Files
        files = self.report_data.get('critical_files', {})
        print("📋 CRITICAL FILES STATUS")
        print("-" * 30)
        for file_path, status in files.items():
            icon = "✅" if status['exists'] else "❌"
            size_info = f"({status['size']:,} bytes)" if status['exists'] else ""
            print(f"{icon} {file_path} {size_info}")
        print()
        
        # Recommendations
        recommendations = self.report_data.get('recommendations', [])
        print("💡 RECOMMENDATIONS")
        print("-" * 30)
        for rec in recommendations:
            print(f"  {rec}")
        print()
        
        # Overall Status
        total_tests = collection.get('total_collected', 0)
        errors = collection.get('collection_errors', 0)
        
        if total_tests > 2500 and errors < 200:
            status = "🟢 GOOD"
            message = "Testing infrastructure is in good shape!"
        elif total_tests > 1000 and errors < 500:
            status = "🟡 FAIR"
            message = "Some issues remain but tests are mostly functional."
        else:
            status = "🔴 NEEDS WORK"
            message = "Significant testing issues need to be addressed."
        
        print("🎯 OVERALL STATUS")
        print("-" * 30)
        print(f"{status} - {message}")
        print("=" * 60)
    
    def run_report(self):
        """Run complete coverage status report"""
        print("🎯 Generating Backend Testing Coverage Status Report...")
        print()
        
        try:
            self.get_collection_stats()
            self.run_sample_execution()
            self.get_system_breakdown()
            self.check_critical_files()
            self.generate_recommendations()
            
            self.print_report()
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    reporter = CoverageStatusReporter()
    reporter.run_report() 