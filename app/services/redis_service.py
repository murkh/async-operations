import logging
import hashlib
import redis.asyncio as redis

from app.core.config import settings


class RedisService:
    def __init__(self):
        self.redis_client = None
        self.queue_name = "document_queue"
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await self.redis_client.ping()
            self.logger.info("Successfully connected to Redis")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            raise e

    async def close(self):
        if self.redis_client:
            await self.redis_client.close()

    @staticmethod
    def compute_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _get_user_job_key(self, user_id: str) -> str:
        return f"active_jobs:{user_id}"

    def _get_inflight_key(self, content_hash: str) -> str:
        return f"inflight:{content_hash}"

    def _get_cache_key(self, content_hash: str) -> str:
        return f"cache:{content_hash}"

    async def increment_active_jobs(self, user_id: str):
        key = self._get_user_job_key(user_id)
        await self.redis_client.incr(key)
        await self.redis_client.expire(key, 3600)

    async def decrement_active_jobs(self, user_id: str):
        key = self._get_user_job_key(user_id)
        val = await self.redis_client.decr(key)
        if val < 0:
            await self.redis_client.set(key, 0)

    async def get_cached_summary(self, content_hash: str) -> str | None:
        key = self._get_cache_key(content_hash)
        return await self.redis_client.get(key)

    async def cache_summary(self, content_hash: str, summary: str):
        key = self._get_cache_key(content_hash)
        await self.redis_client.setex(key, settings.CACHE_TTL_SECONDS, summary)

    async def set_hash_inflight(self, content_hash: str, ttl: int = 600) -> bool:
        """Set hash as inflight only if it's not already there. Returns True if set, False otherwise."""
        key = self._get_inflight_key(content_hash)
        # Using set with nx=True makes it atomic: only sets if it doesn't exist
        result = await self.redis_client.set(key, "1", ex=ttl, nx=True)
        return result is True

    async def remove_hash_inflight(self, content_hash: str):
        key = self._get_inflight_key(content_hash)
        await self.redis_client.delete(key)

    async def enqueue_doc(self, document_id: str):
        await self.redis_client.rpush(self.queue_name, document_id)

    async def can_process_job(self, user_id: str) -> bool:
        """Check if user has reached the active job limit."""
        key = self._get_user_job_key(user_id)
        current_jobs = await self.redis_client.get(key)
        if current_jobs and int(current_jobs) >= settings.MAX_ACTIVE_JOBS_PER_USER:
            return False
        return True


redis_service = RedisService()
