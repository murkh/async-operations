import logging
from pymongo import AsyncMongoClient, ASCENDING
from .config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncMongoClient = None
    db = None


db_helper = MongoDB()


async def init_db():
    if db_helper.db is not None:
        logger.info("Initializing MongoDB indexes...")
        # For list_by_user without status filter
        await db_helper.db.documents.create_index(
            [("user_id", ASCENDING), ("created_at", -1)]
        )
        # For list_by_user with status filter (ESR: user_id=eq, status=eq, created_at=sort)
        await db_helper.db.documents.create_index(
            [("user_id", ASCENDING), ("status", ASCENDING), ("created_at", -1)]
        )
        # For deduplication and content-based lookups
        await db_helper.db.documents.create_index([("content_hash", ASCENDING)])
        logger.info("MongoDB indexes initialized.")


async def connect_to_mongo():
    try:
        db_helper.client = AsyncMongoClient(settings.MONGO_URI)
        db_helper.db = db_helper.client[settings.MONGO_DB]
        # Verify connection
        await db_helper.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
        raise e


async def close_mongo_connection():
    if db_helper.client:
        await db_helper.client.close()


async def get_db():
    if db_helper.db is None:
        await connect_to_mongo()
    return db_helper.db
