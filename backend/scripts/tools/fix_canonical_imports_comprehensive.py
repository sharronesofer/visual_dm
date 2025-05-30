#!/usr/bin/env python3
"""
Comprehensive Canonical Import Fixer for Backend Systems

This script systematically fixes all import issues in the backend systems
to ensure they follow the canonical backend.systems.* format.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class CanonicalImportFixer:
    """Fixes canonical import issues across the backend systems."""
    
    def __init__(self, backend_path: str = "backend"):
        self.backend_path = Path(backend_path)
        self.systems_path = self.backend_path / "systems"
        self.fixed_files = []
        
    def fix_all_imports(self):
        """Fix all canonical import issues."""
        print("Starting comprehensive canonical import fixes...")
        
        # Fix specific known issues
        self._fix_economy_services_init()
        self._fix_economy_models_init()
        self._fix_shared_utils_common_init()
        self._fix_shared_error_imports()
        
        # Scan for other import issues
        self._scan_and_fix_imports()
        
        print(f"Fixed imports in {len(self.fixed_files)} files")
        return self.fixed_files
    
    def _fix_economy_services_init(self):
        """Fix economy services __init__.py imports."""
        file_path = self.systems_path / "economy" / "services" / "__init__.py"
        if not file_path.exists():
            return
            
        print(f"Fixing {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix the imports
        fixes = [
            ("from backend.systems.economy.resource_service", 
             "from backend.systems.economy.services.resource_service"),
            ("from backend.systems.economy.trade_service", 
             "from backend.systems.economy.services.trade_service"),
            ("from backend.systems.economy.market_service", 
             "from backend.systems.economy.services.market_service"),
            ("from backend.systems.economy.futures_service", 
             "from backend.systems.economy.services.futures_service"),
            ("from backend.systems.economy.economy_service", 
             "from backend.systems.economy.services.economy_service"),
        ]
        
        for old, new in fixes:
            content = content.replace(old, new)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        self.fixed_files.append(str(file_path))
    
    def _fix_economy_models_init(self):
        """Fix economy models __init__.py imports."""
        file_path = self.systems_path / "economy" / "models" / "__init__.py"
        if not file_path.exists():
            return
            
        print(f"Fixing {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix the imports
        fixes = [
            ("from backend.systems.economy.resource", 
             "from backend.systems.economy.models.resource"),
            ("from backend.systems.economy.trade_route", 
             "from backend.systems.economy.models.trade_route"),
            ("from backend.systems.economy.market", 
             "from backend.systems.economy.models.market"),
            ("from backend.systems.economy.commodity_future", 
             "from backend.systems.economy.models.commodity_future"),
            ("from backend.systems.economy.economic_metric", 
             "from backend.systems.economy.models.economic_metric"),
        ]
        
        for old, new in fixes:
            content = content.replace(old, new)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        self.fixed_files.append(str(file_path))
    
    def _fix_shared_utils_common_init(self):
        """Fix shared utils common __init__.py imports."""
        file_path = self.systems_path / "shared" / "utils" / "common" / "__init__.py"
        if not file_path.exists():
            return
            
        print(f"Fixing {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix the imports
        fixes = [
            ("from backend.systems.shared.error", 
             "from backend.systems.shared.utils.common.error"),
            ("from backend.systems.shared.validation", 
             "from backend.systems.shared.utils.common.validation"),
            ("from backend.systems.shared.logging", 
             "from backend.systems.shared.utils.common.logging"),
        ]
        
        for old, new in fixes:
            content = content.replace(old, new)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        self.fixed_files.append(str(file_path))
    
    def _fix_shared_error_imports(self):
        """Fix shared error module imports by creating missing files or fixing paths."""
        # Check if error.py exists in shared/utils/common/
        error_file = self.systems_path / "shared" / "utils" / "common" / "error.py"
        
        if not error_file.exists():
            # Create a basic error module
            print(f"Creating missing error module at {error_file}")
            
            error_content = '''"""
Common error classes for the Visual DM backend.
"""

class VisualDMError(Exception):
    """Base exception for Visual DM errors."""
    pass

class ValidationError(VisualDMError):
    """Raised when validation fails."""
    pass

class ConfigurationError(VisualDMError):
    """Raised when configuration is invalid."""
    pass

class DataError(VisualDMError):
    """Raised when data operations fail."""
    pass

class ServiceError(VisualDMError):
    """Raised when service operations fail."""
    pass
'''
            
            with open(error_file, 'w') as f:
                f.write(error_content)
            
            self.fixed_files.append(str(error_file))
    
    def _scan_and_fix_imports(self):
        """Scan all Python files and fix common import patterns."""
        print("Scanning for additional import issues...")
        
        python_files = list(self.systems_path.rglob("*.py"))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Common problematic patterns and their fixes
                patterns = [
                    # Fix relative imports to utils
                    (r'from \.\.utils\.', 'from backend.systems.shared.utils.'),
                    (r'from \.utils\.', 'from backend.systems.shared.utils.'),
                    
                    # Fix non-canonical backend.utils imports
                    (r'from backend\.utils\.', 'from backend.systems.shared.utils.'),
                    
                    # Fix missing .models. in paths
                    (r'from backend\.systems\.(\w+)\.(\w+) import', 
                     r'from backend.systems.\1.models.\2 import'),
                    
                    # Fix missing .services. in paths
                    (r'from backend\.systems\.(\w+)\.(\w+_service) import', 
                     r'from backend.systems.\1.services.\2 import'),
                ]
                
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content)
                
                # Only write if content changed
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"Fixed imports in {file_path}")
                    self.fixed_files.append(str(file_path))
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if a file should be skipped during processing."""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            ".git",
            "htmlcov",
            ".pytest_cache",
            "logs",
            "analytics_data",
            "fix_canonical_imports",  # Skip our own scripts
            "task47_backend_development_protocol.py"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)

def main():
    """Main execution function."""
    fixer = CanonicalImportFixer()
    fixed_files = fixer.fix_all_imports()
    
    print("\n" + "="*60)
    print("CANONICAL IMPORT FIXES COMPLETED")
    print("="*60)
    print(f"Total files fixed: {len(fixed_files)}")
    
    if fixed_files:
        print("\nFixed files:")
        for file_path in fixed_files:
            print(f"  - {file_path}")
    
    print("\nTesting import after fixes...")
    try:
        import sys
        sys.path.insert(0, str(Path.cwd()))
        from backend.systems.economy.services.futures_service import FuturesService
        print("✅ Import test successful!")
    except Exception as e:
        print(f"❌ Import test failed: {e}")

if __name__ == "__main__":
    main() 