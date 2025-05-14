"""Middleware components for search functionality."""

from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import ipaddress
import time
from datetime import datetime

from .config import settings
from .exceptions import SearchSecurityError

class SearchSecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for handling search security."""
    
    def __init__(self, app):
        """Initialize middleware."""
        super().__init__(app)
        
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint
            
        Returns:
            Response from the next middleware/endpoint
            
        Raises:
            HTTPException: If security checks fail
        """
        try:
            # Check if path is under /api/v1/search
            if not request.url.path.startswith("/api/v1/search"):
                return await call_next(request)
                
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Check IP allowlist/blocklist
            self._check_ip_access(client_ip)
            
            # Add security headers
            response = await call_next(request)
            self._add_security_headers(response)
            
            return response
            
        except SearchSecurityError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
            
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request.
        
        Args:
            request: The incoming request
            
        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get the first IP in the chain
            return forwarded_for.split(",")[0].strip()
            
        # Fall back to direct client IP
        return request.client.host
        
    def _check_ip_access(self, ip: str) -> None:
        """Check if IP is allowed to access the API.
        
        Args:
            ip: IP address to check
            
        Raises:
            SearchSecurityError: If IP is not allowed
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check blocklist first
            if settings.ip_blocklist:
                for blocked in settings.ip_blocklist:
                    if self._ip_in_network(ip_obj, blocked):
                        raise SearchSecurityError(f"IP {ip} is blocked")
                        
            # Then check allowlist if enabled
            if settings.ip_allowlist:
                allowed = False
                for allowed_ip in settings.ip_allowlist:
                    if self._ip_in_network(ip_obj, allowed_ip):
                        allowed = True
                        break
                if not allowed:
                    raise SearchSecurityError(f"IP {ip} is not in allowlist")
                    
        except ValueError as e:
            raise SearchSecurityError(f"Invalid IP address: {e}")
            
    def _ip_in_network(self, ip: ipaddress.ip_address, network: str) -> bool:
        """Check if IP is in network.
        
        Args:
            ip: IP address to check
            network: Network or IP to check against (CIDR notation supported)
            
        Returns:
            True if IP is in network
        """
        try:
            if "/" in network:
                return ip in ipaddress.ip_network(network)
            return ip == ipaddress.ip_address(network)
        except ValueError:
            return False
            
    def _add_security_headers(self, response: Response) -> None:
        """Add security headers to response.
        
        Args:
            response: Response to add headers to
        """
        # Basic security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Add timestamp
        response.headers["X-Response-Time"] = str(time.time())
        
        # Add request ID if present
        if hasattr(response, "request_id"):
            response.headers["X-Request-ID"] = response.request_id 