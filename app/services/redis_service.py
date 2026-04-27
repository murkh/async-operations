import hashlib
import redis.asyncio as redis

from app.core.config import settings


class RedisService:
    def __init__(self):
        self.redis_client = None
        self.queue_name = "document_queue"

    async def connect(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

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
        await self.redis_client.setex(key, settings.cache_ttl_seconds, summary)

    async def is_hash_inflight(self, content_hash: str) -> bool:
        key = self._get_inflight_key(content_hash)
        return await self.redis_client.exists(key) > 0

    async def set_hash_inflight(self, content_hash: str, ttl: int = 600):
        key = self._get_inflight_key(content_hash)
        await self.redis_client.setex(key, ttl, "1")

    async def enqueue_doc(self, document_id: str):
        await self.redis_client.rpush(self.queue_name, document_id)

    async def can_process_job(self, user_id: str) -> bool:
        """Check if user has reached the active job limit."""
        key = self._get_user_job_key(user_id)
        current_jobs = await self.redis_client.get(key)
        if current_jobs and int(current_jobs) >= settings.max_active_jobs_per_user:
            return False
        return True


redis_service = RedisService()
