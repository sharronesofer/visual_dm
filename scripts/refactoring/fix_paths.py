import re
import sys
from pathlib import Path

def fix_paths(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace the import paths - now using the correct paths
    new_content = re.sub(
        r'"backend\.systems\.auth_user\.services\.AuthRelationshipService', 
        r'"backend.infrastructure.auth.auth_user.services.auth_relationships.AuthRelationshipService', 
        content
    )
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    test_file = Path("tests/systems/auth_user/unit/test_auth_relationships.py")
    fix_paths(test_file) 