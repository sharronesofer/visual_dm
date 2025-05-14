"""Tests for security middleware and configurations."""

import time
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

from app.main import app
from app.core.config import config

client = TestClient(app)

def test_cors_headers():
    """Test CORS headers are properly set."""
    response = client.options(
        "/api/docs",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "Content-Type" in response.headers["access-control-allow-headers"]

def test_cors_disallowed_origin():
    """Test CORS blocks disallowed origins."""
    response = client.get(
        "/api/docs",
        headers={"Origin": "http://evil.com"}
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers

def test_basic_security_headers():
    """Test basic security headers are present."""
    response = client.get("/api/docs")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-xss-protection"] == "1; mode=block"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"

def test_advanced_security_headers():
    """Test advanced security headers are set."""
    response = client.get("/api/docs")
    
    # Test Permissions-Policy
    assert "permissions-policy" in response.headers
    policy = response.headers["permissions-policy"]
    assert "camera=()" in policy
    assert "geolocation=()" in policy
    
    # Test Cross-Origin policies
    assert response.headers["cross-origin-embedder-policy"] == "require-corp"
    assert response.headers["cross-origin-opener-policy"] == "same-origin"
    assert response.headers["cross-origin-resource-policy"] == "same-origin"

@pytest.mark.parametrize("is_production", [True, False])
def test_production_security_headers(is_production):
    """Test production-specific security headers."""
    with patch("app.core.config.config.is_production", is_production):
        response = client.get("/api/docs")
        
        # HSTS header
        if is_production:
            assert "strict-transport-security" in response.headers
            assert "max-age=31536000" in response.headers["strict-transport-security"]
        else:
            assert "strict-transport-security" not in response.headers
            
        # Expect-CT header
        if is_production:
            assert "expect-ct" in response.headers
            assert "enforce" in response.headers["expect-ct"]
        else:
            assert "expect-ct" not in response.headers
            
        # CSP header
        if is_production:
            assert "content-security-policy" in response.headers
            csp = response.headers["content-security-policy"]
            assert "default-src 'self'" in csp
            assert "frame-ancestors 'none'" in csp
        else:
            assert "content-security-policy" not in response.headers

def test_api_cache_control():
    """Test cache control headers for API endpoints."""
    response = client.get("/api/docs")
    assert response.headers["cache-control"] == "no-store, no-cache, must-revalidate, proxy-revalidate"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["expires"] == "0"

@pytest.mark.parametrize("is_production", [True, False])
def test_rate_limiting(is_production):
    """Test rate limiting functionality."""
    with patch("app.core.config.config.is_production", is_production):
        # Make multiple requests
        for i in range(70):  # More than the 60 per minute limit
            response = client.get("/api/docs")
            
            if is_production:
                # Check rate limit headers
                assert "x-ratelimit-limit" in response.headers
                assert "x-ratelimit-remaining" in response.headers
                
                # If we've exceeded the limit
                if i >= 60:
                    assert response.status_code == 429
                    assert response.json()["type"] == "rate_limit_exceeded"
                    break
            else:
                # Rate limiting should be disabled in development
                assert response.status_code == 200
                assert "x-ratelimit-limit" not in response.headers

def test_cookie_security():
    """Test cookie security settings."""
    with patch("app.core.config.config.is_production", True):
        response = client.get("/api/docs")
        cookie_header = response.headers.get("set-cookie", "")
        
        assert "HttpOnly" in cookie_header
        assert "Secure" in cookie_header
        assert "SameSite=Strict" in cookie_header
        assert "Path=/" in cookie_header 