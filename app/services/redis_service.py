import redis.asyncio as redis


from app.core.config import settings


class RedisService:
    def __init__(self):
        self.redis_client = None

    async def connect(self):
        self.redis_client = redis.from_url(settings.redis_uri, decode_responses=True)

    async def close(self):
        if self.redis_client:
            await self.redis_client.close()


redis_service = RedisService()
