#!/usr/bin/env python3
import os
import subprocess
import sys

# Configuration
BACKEND_DIR = os.path.abspath("../backend")

def run_command(cmd, cwd=None):
    """Run a command and return its output and exit code."""
    try:
        if cwd is None:
            cwd = BACKEND_DIR
        process = subprocess.run(cmd, shell=True, text=True, capture_output=True, cwd=cwd)
        return process.stdout.strip(), process.stderr.strip(), process.returncode
    except Exception as e:
        return "", str(e), 1

def test_imports():
    """Test that critical imports still work."""
    print("Testing imports after consolidation...\n")
    
    cmd = f"python {os.path.join(BACKEND_DIR, 'test_imports.py')}"
    stdout, stderr, exit_code = run_command(cmd)
    
    print(stdout)
    if stderr:
        print(f"Error output:\n{stderr}")
    
    if exit_code != 0:
        print(f"⚠️ Import test failed with exit code {exit_code}")
    else:
        print("✅ Import test passed!")
    
    return exit_code == 0

def test_pytest():
    """Run a basic pytest to ensure core functionality still works."""
    print("\nRunning basic pytest tests...\n")
    
    # Run only a subset of tests for speed
    cmd = "cd backend && python -m pytest tests/unit/core -v"
    stdout, stderr, exit_code = run_command(cmd, cwd=os.path.dirname(BACKEND_DIR))
    
    print(stdout)
    if stderr:
        print(f"Error output:\n{stderr}")
    
    if exit_code != 0:
        print(f"⚠️ pytest failed with exit code {exit_code}")
    else:
        print("✅ pytest passed!")
    
    return exit_code == 0

def fix_pydantic_v2_issues():
    """Fix common issues with Pydantic v2 migration."""
    print("\nChecking for Pydantic v2 compatibility issues...\n")
    
    # Common patterns that need to be fixed for Pydantic v2
    fixes = [
        {
            'pattern': 'PostgresDsn.build',
            'file_pattern': '**/config/*.py',
            'message': '⚠️ Found PostgresDsn.build which is deprecated in Pydantic v2'
        },
        {
            'pattern': 'Schema(',
            'file_pattern': '**/models/*.py',
            'message': '⚠️ Found Schema() which is renamed to model_schema() in Pydantic v2'
        }
    ]
    
    for fix in fixes:
        cmd = f'find {BACKEND_DIR} -path "{fix["file_pattern"]}" -type f -exec grep -l "{fix["pattern"]}" {{}} \\;'
        stdout, _, _ = run_command(cmd)
        
        if stdout:
            print(fix['message'])
            print("Found in files:")
            for file in stdout.split('\n'):
                if file.strip():
                    print(f"  - {file}")
            print("\nConsider updating these files for Pydantic v2 compatibility.")
    
    # One specific fix for PostgresDsn.build
    print("\nAttempting to fix PostgresDsn.build usage...")
    config_file = os.path.join(BACKEND_DIR, 'config', 'config.py')
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
        
        if 'PostgresDsn.build' in content:
            # Create backup
            with open(f"{config_file}.bak", 'w') as f:
                f.write(content)
            
            # Replace with Pydantic v2 compatible code
            updated_content = content.replace(
                'PostgresDsn.build(',
                'str(PostgresDsn.build('
            ).replace(
                'user=values.get("POSTGRES_USER")',
                'username=values.get("POSTGRES_USER")'
            )
            
            if 'str(PostgresDsn.build(' in updated_content and ')' in updated_content:
                # Add closing parenthesis for str()
                updated_content = updated_content.replace(
                    'str(PostgresDsn.build(', 
                    'str(PostgresDsn.build('
                ).replace(
                    ')',
                    '))'
                )
            
            with open(config_file, 'w') as f:
                f.write(updated_content)
            
            print(f"✅ Updated {config_file} for Pydantic v2 compatibility")
            print(f"  Backup saved to {config_file}.bak")

def main():
    """Run all tests."""
    print("Starting tests after consolidation...")
    
    # Test imports
    imports_ok = test_imports()
    
    # Try to fix pydantic issues
    fix_pydantic_v2_issues()
    
    # Run pytest
    pytest_ok = test_pytest()
    
    # Results
    print("\n" + "=" * 50)
    print("Consolidation Test Results:")
    print("-" * 50)
    print(f"Imports: {'✅ OK' if imports_ok else '❌ Failed'}")
    print(f"pytest: {'✅ OK' if pytest_ok else '❌ Failed'}")
    print("=" * 50)
    
    if not (imports_ok and pytest_ok):
        print("\n⚠️ Some tests failed. Please check the output above for details.")
        return 1
    else:
        print("\n✅ All tests passed! The consolidation was successful.")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 