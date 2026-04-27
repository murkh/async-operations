from pymongo import AsyncMongoClient
from .config import settings


class MongoDB:
    client: AsyncMongoClient = None
    db = None


db_helper = MongoDB()


async def connect_to_mongo():
    db_helper.client = AsyncMongoClient(settings.MONGO_URI)
    db_helper.db = db_helper.client[settings.MONGO_DB]


async def close_mongo_connection():
    if db_helper.client:
        await db_helper.client.close()


async def get_db():
    if db_helper.db is None:
        await connect_to_mongo()
    return db_helper.db
