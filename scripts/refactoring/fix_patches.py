import re
import sys
from pathlib import Path

def fix_patches(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace patch targets from static methods to exposed functions
    replacements = [
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.create_relationship"', 
         r'"backend.systems.auth_user.services.create_auth_relationship"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.update_relationship"', 
         r'"backend.systems.auth_user.services.update_auth_relationship"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.remove_relationship"', 
         r'"backend.systems.auth_user.services.remove_auth_relationship"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.get_relationship"', 
         r'"backend.systems.auth_user.services.get_auth_relationship"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.check_permission"', 
         r'"backend.systems.auth_user.services.check_permission"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.add_permission"', 
         r'"backend.systems.auth_user.services.add_permission"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.remove_permission"', 
         r'"backend.systems.auth_user.services.remove_permission"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.set_ownership"', 
         r'"backend.systems.auth_user.services.set_ownership"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.get_user_characters"', 
         r'"backend.systems.auth_user.services.get_user_characters"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.get_character_users"', 
         r'"backend.systems.auth_user.services.get_character_users"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.transfer_ownership"', 
         r'"backend.systems.auth_user.services.transfer_ownership"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.bulk_create_relationships"', 
         r'"backend.systems.auth_user.services.bulk_create_relationships"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.bulk_remove_relationships"', 
         r'"backend.systems.auth_user.services.bulk_remove_relationships"'),
        (r'"backend\.systems\.auth_user\.services\.auth_relationships\.AuthRelationshipService\.check_multi_character_permission"', 
         r'"backend.systems.auth_user.services.check_multi_character_permission"'),
    ]
    
    new_content = content
    for old, new in replacements:
        new_content = re.sub(old, new, new_content)
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed patch targets in {file_path}")

if __name__ == "__main__":
    test_file = Path("tests/systems/auth_user/unit/test_auth_relationships.py")
    fix_patches(test_file) 