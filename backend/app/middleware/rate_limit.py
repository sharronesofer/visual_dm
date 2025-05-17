import time
from typing import Callable, Dict, Optional
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import asyncio
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logger = logging.getLogger("api")

# Simple in-memory rate limiter - for production use Redis instead
class InMemoryRateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute in seconds
        self.client_requests: Dict[str, Dict[float, int]] = {}
        self.cleanup_interval = 300  # 5 minutes in seconds
        self._setup_cleanup()
    
    def _setup_cleanup(self):
        """Setup periodic cleanup of expired entries"""
        asyncio.create_task(self._periodic_cleanup())
    
    async def _periodic_cleanup(self):
        """Periodically clean up expired entries"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._cleanup_expired()
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {str(e)}")
    
    def _cleanup_expired(self):
        """Remove requests older than window_size"""
        current_time = time.time()
        cutoff = current_time - self.window_size
        
        for client_ip, timestamps in list(self.client_requests.items()):
            # Clean up old timestamps
            self.client_requests[client_ip] = {
                ts: count for ts, count in timestamps.items() if ts > cutoff
            }
            
            # Remove client if no timestamps left
            if not self.client_requests[client_ip]:
                del self.client_requests[client_ip]
    
    async def is_rate_limited(self, client_ip: str) -> bool:
        """Check if a client IP is currently rate limited"""
        current_time = time.time()
        cutoff = current_time - self.window_size
        
        # Initialize client record if not exists
        if client_ip not in self.client_requests:
            self.client_requests[client_ip] = {}
        
        # Clean up old timestamps
        self.client_requests[client_ip] = {
            ts: count for ts, count in self.client_requests[client_ip].items() if ts > cutoff
        }
        
        # Count total requests in the window
        total_requests = sum(self.client_requests[client_ip].values())
        
        # Track this request
        if current_time in self.client_requests[client_ip]:
            self.client_requests[client_ip][current_time] += 1
        else:
            self.client_requests[client_ip][current_time] = 1
            
        # Check if rate limit exceeded
        return total_requests >= self.requests_per_minute


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: ASGIApp, 
        requests_per_minute: int = 60,
        exclude_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.rate_limiter = InMemoryRateLimiter(requests_per_minute)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if await self.rate_limiter.is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."},
                headers={"Retry-After": "60"}
            )
        
        # Process the request
        return await call_next(request)

def setup_rate_limiting(app):
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["100 per hour"]
    )
    return limiter 