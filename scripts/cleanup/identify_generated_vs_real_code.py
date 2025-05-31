#!/usr/bin/env python3

import os
import re
from pathlib import Path
from collections import defaultdict
import ast

class CodeAnalyzer:
    def __init__(self, backend_dir):
        self.backend_dir = Path(backend_dir)
        self.analysis = {
            'real_code': [],
            'test_files': [],
            'generated_stubs': [],
            'mock_implementations': [],
            'test_utilities': [],
            'duplicate_utilities': [],
            'empty_or_minimal': []
        }
        
    def analyze_file(self, file_path):
        """Analyze a single Python file to categorize it"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic metrics
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            
            file_info = {
                'path': str(file_path),
                'total_lines': len(lines),
                'code_lines': len(non_empty_lines),
                'size_kb': file_path.stat().st_size / 1024
            }
            
            # Categorization logic
            if self.is_test_file(file_path, content):
                if self.is_real_test(content):
                    self.analysis['test_files'].append(file_info)
                else:
                    self.analysis['generated_stubs'].append(file_info)
            elif self.is_generated_stub(content):
                self.analysis['generated_stubs'].append(file_info)
            elif self.is_mock_implementation(content):
                self.analysis['mock_implementations'].append(file_info)
            elif self.is_test_utility(file_path, content):
                self.analysis['test_utilities'].append(file_info)
            elif self.is_minimal_or_empty(content):
                self.analysis['empty_or_minimal'].append(file_info)
            else:
                self.analysis['real_code'].append(file_info)
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def is_test_file(self, file_path, content):
        """Check if this is a test file"""
        name = file_path.name.lower()
        return (
            'test' in name or
            'test' in str(file_path).lower() or
            'pytest' in content or
            'unittest' in content or
            'def test_' in content
        )
    
    def is_real_test(self, content):
        """Check if test file contains real test logic vs just stubs"""
        # Real tests have assertions, setup logic, actual test scenarios
        real_test_indicators = [
            'assert ',
            'assertEqual',
            'assertTrue',
            'assertFalse',
            'assertRaises',
            'mock.patch',
            '@pytest.fixture',
            'setup_method',
            'teardown_method'
        ]
        
        # Count real test patterns
        real_patterns = sum(1 for indicator in real_test_indicators if indicator in content)
        
        # Stub test patterns
        stub_patterns = content.count('pass') + content.count('# TODO') + content.count('NotImplemented')
        
        return real_patterns > stub_patterns
    
    def is_generated_stub(self, content):
        """Check if this is a generated stub/placeholder"""
        stub_indicators = [
            'pass',
            '# TODO',
            '# FIXME',
            'NotImplementedError',
            'raise NotImplementedError',
            '...',  # Ellipsis placeholder
        ]
        
        # If file is mostly stubs
        stub_count = sum(content.count(indicator) for indicator in stub_indicators)
        total_functions = content.count('def ')
        
        return stub_count > 0 and (total_functions == 0 or stub_count >= total_functions * 0.7)
    
    def is_mock_implementation(self, content):
        """Check if this is a mock/fake implementation for testing"""
        mock_indicators = [
            'Mock',
            'MagicMock',
            'patch',
            'mock.',
            'fake_',
            'mock_',
            'stub_',
            'dummy_',
            'test_data',
            'mock_response'
        ]
        
        return any(indicator in content for indicator in mock_indicators)
    
    def is_test_utility(self, file_path, content):
        """Check if this is test infrastructure/utility code"""
        path_str = str(file_path).lower()
        utility_indicators = [
            'conftest.py',
            'fixtures',
            'test_utils',
            'testing_utils',
            'test_helpers',
            'setup.py' in path_str and 'test' in path_str,
            '__mocks__' in path_str,
            'factories' in path_str and 'test' in path_str
        ]
        
        return any(indicator in path_str for indicator in utility_indicators)
    
    def is_minimal_or_empty(self, content):
        """Check if file is essentially empty or just imports"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        non_comment_lines = [line for line in lines if not line.startswith('#')]
        
        # Remove imports and basic structure
        content_lines = [
            line for line in non_comment_lines 
            if not line.startswith('import ') 
            and not line.startswith('from ')
            and line not in ['', 'pass', '__all__ = []']
            and not line.startswith('"""')
            and not line.startswith("'''")
        ]
        
        return len(content_lines) <= 3
    
    def analyze_backend(self):
        """Analyze entire backend directory"""
        print("🔍 Analyzing backend structure...")
        
        python_files = list(self.backend_dir.rglob("*.py"))
        total_files = len(python_files)
        
        print(f"Found {total_files} Python files to analyze...")
        
        for i, file_path in enumerate(python_files):
            if i % 100 == 0:
                print(f"  Progress: {i}/{total_files}")
            self.analyze_file(file_path)
        
        self.print_analysis()
        return self.analysis
    
    def print_analysis(self):
        """Print analysis results"""
        print("\n" + "="*60)
        print("🎯 BACKEND CODE ANALYSIS RESULTS")
        print("="*60)
        
        total_files = sum(len(category) for category in self.analysis.values())
        
        for category, files in self.analysis.items():
            count = len(files)
            total_lines = sum(f['code_lines'] for f in files)
            total_size = sum(f['size_kb'] for f in files)
            percentage = (count / total_files * 100) if total_files > 0 else 0
            
            print(f"\n📁 {category.upper().replace('_', ' ')}:")
            print(f"   Files: {count} ({percentage:.1f}%)")
            print(f"   Lines: {total_lines:,}")
            print(f"   Size: {total_size:.1f} KB")
            
            if count > 0:
                print(f"   Examples:")
                for file_info in files[:3]:  # Show first 3 examples
                    rel_path = str(Path(file_info['path']).relative_to(self.backend_dir))
                    print(f"     - {rel_path} ({file_info['code_lines']} lines)")
        
        # Summary recommendations
        print(f"\n🎯 CLEANUP RECOMMENDATIONS:")
        
        # Calculate potential savings
        removable_files = (
            len(self.analysis['generated_stubs']) +
            len(self.analysis['mock_implementations']) +
            len(self.analysis['test_utilities']) +
            len(self.analysis['empty_or_minimal'])
        )
        
        removable_lines = (
            sum(f['code_lines'] for f in self.analysis['generated_stubs']) +
            sum(f['code_lines'] for f in self.analysis['mock_implementations']) +
            sum(f['code_lines'] for f in self.analysis['test_utilities']) +
            sum(f['code_lines'] for f in self.analysis['empty_or_minimal'])
        )
        
        keep_files = len(self.analysis['real_code']) + len(self.analysis['test_files'])
        keep_lines = (
            sum(f['code_lines'] for f in self.analysis['real_code']) +
            sum(f['code_lines'] for f in self.analysis['test_files'])
        )
        
        print(f"   ✅ KEEP: {keep_files} files ({keep_lines:,} lines)")
        print(f"   ❌ REMOVE: {removable_files} files ({removable_lines:,} lines)")
        print(f"   📉 REDUCTION: {removable_files/total_files*100:.1f}% files, {removable_lines/(keep_lines+removable_lines)*100:.1f}% lines")

if __name__ == "__main__":
    analyzer = CodeAnalyzer("backend/systems")
    analysis = analyzer.analyze_backend() 