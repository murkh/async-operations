import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.services.rate_limiter import rate_limiter

logger = logging.getLogger("api")

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Identify the client (IP address by default)
        # You could also use a session token or API key if available in headers
        client_ip = request.client.host if request.client else "unknown"
        
        # We can also check for user_id in headers if your app uses it
        # For example: user_id = request.headers.get("X-User-ID", client_ip)
        
        # Exclude health check and docs from rate limiting if desired
        path = request.url.path
        if path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        if await rate_limiter.is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip} on {path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "error": "rate_limit_exceeded"
                }
            )

        return await call_next(request)
