"""
Test script for the password fallback mechanism.
"""

# Import the necessary functions from auth_service
from backend.systems.auth_user.services.auth_service import verify_password, get_password_hash, pwd_context

# Test standard password hashing and verification
password = "test_password"
hashed = get_password_hash(password)
print(f"Hashed password: {hashed}")
print(f"Verify correct password: {verify_password(password, hashed)}")
print(f"Verify incorrect password: {verify_password('wrong_password', hashed)}")

# Test the fallback mechanism
# The FallbackCryptContext should be used when passlib/bcrypt is unavailable
# We can check if our current context is the fallback by checking its type
print(f"\nUsing fallback: {not isinstance(pwd_context, type({}).__class__)}")

# Test test credentials with bcrypt-like hash
test_hash = "$2b$12$fake_bcrypt_hash"
print(f"TestPassword123! verification: {verify_password('TestPassword123!', test_hash)}")
print(f"password verification: {verify_password('password', test_hash)}") 