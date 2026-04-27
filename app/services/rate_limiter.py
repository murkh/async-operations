import time
import logging
from app.services.redis_service import redis_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(
        self, 
        requests_limit: int = settings.RATE_LIMIT_REQUESTS, 
        window_seconds: int = settings.RATE_LIMIT_WINDOW_SECONDS
    ):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds

    async def is_rate_limited(
        self, 
        identifier: str, 
        requests_limit: int = None, 
        window_seconds: int = None
    ) -> bool:
        """
        Check if the identifier (IP or User ID) has exceeded the rate limit.
        Uses a sliding window algorithm with Redis Sorted Sets.
        """
        requests_limit = requests_limit or self.requests_limit
        window_seconds = window_seconds or self.window_seconds

        if not redis_service.redis_client:
            logger.warning("Redis client not initialized, skipping rate limiting")
            return False

        key = f"rate_limit:{identifier}"
        now = time.time()
        window_start = now - self.window_seconds

        try:
            # Create a pipeline for atomic operations
            async with redis_service.redis_client.pipeline(transaction=True) as pipe:
                # Remove timestamps older than the window
                pipe.zremrangebyscore(key, 0, window_start)
                # Count current timestamps in the window
                pipe.zcard(key)
                # Add current timestamp
                pipe.zadd(key, {str(now): now})
                # Set expiry on the key to clean up eventually
                pipe.expire(key, self.window_seconds)
                
                # Execute pipeline
                _, count, _, _ = await pipe.execute()

            if count >= self.requests_limit:
                logger.info(f"Rate limit exceeded for {identifier}: {count}/{self.requests_limit}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error in rate limiter: {e}", exc_info=True)
            return False

rate_limiter = RateLimiter()
