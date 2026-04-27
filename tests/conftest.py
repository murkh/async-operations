import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient
from app.main import app
from app.core.config import settings
from app.core.database import connect_to_mongo, db_helper
from app.services.redis_service import redis_service


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def setup_db():

    settings.MONGO_DB = "test_document_insights"

    await connect_to_mongo()

    if db_helper.db is not None:
        await db_helper.db.documents.delete_many({})

    await redis_service.connect()
    await redis_service.redis_client.flushdb()

    yield

    if db_helper.db is not None:
        await db_helper.db.documents.delete_many({})

    await redis_service.redis_client.flushdb()
