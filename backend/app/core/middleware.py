import time
from typing import Callable, Dict, Optional
import logging
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import redis.asyncio as aioredis
import json
from datetime import datetime, timedelta
import hashlib

from .config import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Log the request
        logger.info(f"Request started: {request.method} {request.url.path} from {client_ip}")
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log the response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Duration: {duration:.3f}s"
            )
            
            # Add X-Process-Time header
            response.headers["X-Process-Time"] = str(duration)
            
            return response
        except Exception as e:
            # Log the error
            logger.error(
                f"Request failed: {request.method} {request.url.path} - Error: {str(e)}",
                exc_info=True
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis
    """
    
    def __init__(self, app: FastAPI, redis_url: Optional[str] = None):
        super().__init__(app)
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis = None
        self.rate_limit = settings.RATE_LIMIT_PER_MINUTE
        self.window = 60  # 1 minute window
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for certain paths
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)
        
        # Use IP and path as the rate limit key
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        
        # Create a unique key for this IP and endpoint
        key = f"ratelimit:{hashlib.md5(f'{client_ip}:{path}'.encode()).hexdigest()}"
        
        # Check if we're using Redis for rate limiting
        if self.redis_url:
            # Initialize Redis connection if needed
            if self.redis is None:
                try:
                    self.redis = await aioredis.from_url(self.redis_url)
                except Exception as e:
                    logger.error(f"Failed to connect to Redis: {str(e)}")
                    # If Redis connection fails, bypass rate limiting
                    return await call_next(request)
            
            # Get current count
            count = await self.redis.get(key)
            
            if count is None:
                # First request in this window
                await self.redis.set(key, 1, ex=self.window)
            elif int(count) >= self.rate_limit:
                # Rate limit exceeded
                logger.warning(f"Rate limit exceeded for {client_ip} on {path}")
                return Response(
                    content=json.dumps({
                        "error": True,
                        "message": "Too many requests",
                        "code": 429
                    }),
                    status_code=429,
                    media_type="application/json",
                    headers={"Retry-After": str(self.window)}
                )
            else:
                # Increment the counter
                await self.redis.incr(key)
        
        # Process the request
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        # This is a basic policy - should be customized for the application
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


def add_middleware(app: FastAPI) -> None:
    """
    Add all middleware to the FastAPI application
    """
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate limiting (if Redis is configured)
    if settings.REDIS_URL:
        app.add_middleware(RateLimitMiddleware, redis_url=settings.REDIS_URL) 