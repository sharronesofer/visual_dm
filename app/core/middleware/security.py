"""Security middleware components."""

from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..config import config

def setup_cors(app: FastAPI) -> None:
    """Configure CORS for the application.
    
    Args:
        app: The FastAPI application instance
    """
    # Get allowed origins from config
    allowed_origins = config.api.cors_origins if config.api.cors_origins else ["http://localhost:3000"]
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
            "X-CSRF-Token"
        ],
        expose_headers=[
            "Content-Length",
            "Content-Range",
            "X-Total-Count"
        ],
        max_age=3600,  # Cache preflight requests for 1 hour
    )

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers to the response.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint
            
        Returns:
            Response with added security headers
        """
        response = await call_next(request)
        
        # Add basic security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add Feature-Policy/Permissions-Policy
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )
        
        # Add Cross-Origin-Embedder-Policy and Cross-Origin-Opener-Policy
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        
        # Add Cross-Origin-Resource-Policy
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        
        if config.is_production:
            # Add HSTS in production
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            # Add Expect-CT in production
            response.headers["Expect-CT"] = "max-age=86400, enforce"
            
            # Add CSP in production
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Needed for Swagger UI
                "style-src 'self' 'unsafe-inline'; "  # Needed for Swagger UI
                "img-src 'self' data:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "  # Additional clickjacking protection
                "form-action 'self'; "  # Restrict form submissions
                "base-uri 'self'; "  # Restrict base tag
                "object-src 'none'; "  # Disable plugins
                "require-trusted-types-for 'script'"  # Enable Trusted Types
            )
            
            # Set secure cookie policy in production
            response.headers["Set-Cookie"] = (
                "Path=/; "
                "HttpOnly; "
                "Secure; "
                "SameSite=Strict"
            )
        
        # Add Cache-Control header to prevent sensitive data caching
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response

def setup_security(app: FastAPI) -> None:
    """Configure security middleware for the application.
    
    Args:
        app: The FastAPI application instance
    """
    # Set up CORS
    setup_cors(app)
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware) 