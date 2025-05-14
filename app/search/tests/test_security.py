"""Tests for search security components."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import jwt
from datetime import datetime, timedelta

from app.search.security import (
    SearchPermissions,
    get_current_user_permissions,
    check_search_permissions,
    SearchRateLimiter
)
from app.search.middleware import SearchSecurityMiddleware
from app.search.config import settings
from app.search.exceptions import SearchSecurityError

# Test app setup
app = FastAPI()
app.add_middleware(SearchSecurityMiddleware)

@app.get("/api/v1/search/test")
async def test_endpoint():
    return {"message": "success"}

client = TestClient(app)

# Test data
TEST_SECRET_KEY = "test_secret_key"
TEST_USER_ID = "test_user"
TEST_ROLES = ["search:read", "search:write"]

def create_test_token(
    user_id: str = TEST_USER_ID,
    permissions: list[str] = TEST_ROLES,
    expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    """Create a test JWT token.
    
    Args:
        user_id: User ID to include in token
        permissions: List of permissions to include
        expires_delta: Token expiration time
        
    Returns:
        JWT token string
    """
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": user_id,
        "permissions": permissions,
        "exp": expire
    }
    return jwt.encode(
        to_encode,
        TEST_SECRET_KEY,
        algorithm=settings.token_algorithm
    )

# Middleware tests
def test_middleware_allows_non_search_paths():
    """Test that middleware allows non-search paths."""
    response = client.get("/other/path")
    assert response.status_code == 404  # 404 because path doesn't exist

def test_middleware_checks_ip_allowlist():
    """Test IP allowlist checking."""
    with patch("app.search.config.settings.ip_allowlist", ["127.0.0.1"]):
        response = client.get(
            "/api/v1/search/test",
            headers={"X-Forwarded-For": "127.0.0.1"}
        )
        assert response.status_code == 200
        
        response = client.get(
            "/api/v1/search/test",
            headers={"X-Forwarded-For": "1.2.3.4"}
        )
        assert response.status_code == 403

def test_middleware_checks_ip_blocklist():
    """Test IP blocklist checking."""
    with patch("app.search.config.settings.ip_blocklist", ["1.2.3.4"]):
        response = client.get(
            "/api/v1/search/test",
            headers={"X-Forwarded-For": "1.2.3.4"}
        )
        assert response.status_code == 403
        
        response = client.get(
            "/api/v1/search/test",
            headers={"X-Forwarded-For": "127.0.0.1"}
        )
        assert response.status_code == 200

def test_middleware_adds_security_headers():
    """Test that security headers are added."""
    response = client.get("/api/v1/search/test")
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "X-XSS-Protection" in response.headers
    assert "Referrer-Policy" in response.headers
    assert "Content-Security-Policy" in response.headers
    assert "X-Response-Time" in response.headers

# Permission tests
@pytest.mark.asyncio
async def test_get_current_user_permissions():
    """Test permission extraction from token."""
    token = create_test_token()
    
    with patch("app.search.security.verify_token") as mock_verify:
        mock_verify.return_value = {
            "sub": TEST_USER_ID,
            "permissions": TEST_ROLES
        }
        
        permissions = await get_current_user_permissions(
            security_scopes=Mock(scopes=["search:read"]),
            token=token
        )
        
        assert "search:read" in permissions
        assert "search:write" in permissions

@pytest.mark.asyncio
async def test_check_search_permissions():
    """Test permission checking."""
    check = check_search_permissions(["search:read"])
    
    # Should pass with required permission
    assert await check(["search:read", "search:write"])
    
    # Should raise exception without required permission
    with pytest.raises(Exception):
        await check(["search:write"])

# Rate limiter tests
@pytest.mark.asyncio
async def test_rate_limiter():
    """Test rate limiting."""
    limiter = SearchRateLimiter("search")
    mock_user = Mock(id=TEST_USER_ID)
    
    # First request should pass
    assert await limiter.check_rate_limit(mock_user)
    
    # Mock rate limit exceeded
    with patch("app.search.security.SearchSecurityConfig") as mock_config:
        mock_config.return_value.rate_limits = {
            "search": {"limit": 1, "window": 60}
        }
        mock_config.return_value.rate_limiter.is_rate_limited.return_value = (
            True,
            {"X-RateLimit-Remaining": "0"}
        )
        
        with pytest.raises(Exception):
            await limiter.check_rate_limit(mock_user)

# Integration tests
def test_protected_endpoint_with_valid_token():
    """Test endpoint access with valid token."""
    token = create_test_token()
    response = client.get(
        "/api/v1/search/test",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_protected_endpoint_with_invalid_token():
    """Test endpoint access with invalid token."""
    response = client.get(
        "/api/v1/search/test",
        headers={"Authorization": "Bearer invalid"}
    )
    assert response.status_code == 401

def test_protected_endpoint_without_token():
    """Test endpoint access without token."""
    response = client.get("/api/v1/search/test")
    assert response.status_code == 401

def test_rate_limiting_integration():
    """Test rate limiting integration."""
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Configure low rate limit for test
    with patch("app.search.config.settings") as mock_settings:
        mock_settings.search_rate_limit = 2
        mock_settings.search_rate_limit_window = 60
        
        # First requests should succeed
        response = client.get("/api/v1/search/test", headers=headers)
        assert response.status_code == 200
        
        response = client.get("/api/v1/search/test", headers=headers)
        assert response.status_code == 200
        
        # Third request should be rate limited
        response = client.get("/api/v1/search/test", headers=headers)
        assert response.status_code == 429
        assert "Retry-After" in response.headers 