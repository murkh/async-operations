import asyncio
import logging
import random
from datetime import datetime, timezone

from bson import ObjectId

from .celery_app import celery_app
from app.core.database import connect_to_mongo, close_mongo_connection
from app.services.redis_service import redis_service
from app.schemas.documents import DocumentStatus
from app.core.database import db_helper


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("worker")


async def _process_document_logic(document_id: str):
    db = db_helper.db

    # Fetch the document
    doc = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        logger.warning(f"Document {document_id} not found in database")
        return
    content_hash = doc.get("content_hash")
    user_id = doc.get("user_id")

    logger.info(f"Processing document {document_id} (User: {user_id})")

    await db.documents.update_one(
        {"_id": ObjectId(document_id)},
        {
            "$set": {
                "status": DocumentStatus.PROCESSING,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    # Simulate Work
    sleep_time = random.uniform(10, 30)
    await asyncio.sleep(sleep_time)

    if random.random() < 0.10:
        raise Exception("Simulated network failure")

    logger.info(f"Successfully processed document {document_id}")
    summary = f"Summary for: {doc.get('title', 'Unknown')}. Processing took {sleep_time:.2f} seconds. Content length: {len(doc.get('content', ''))} chars."

    update_filter = {
        "content_hash": content_hash,
        "status": {"$in": [DocumentStatus.QUEUED, DocumentStatus.PROCESSING]},
    }

    affected_docs = await db.documents.find(update_filter).to_list(length=100)
    for affected_doc in affected_docs:
        await redis_service.decrement_active_jobs(affected_doc["user_id"])

    await db.documents.update_many(
        update_filter,
        {
            "$set": {
                "status": DocumentStatus.COMPLETED,
                "summary": summary,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    if content_hash:
        await redis_service.cache_summary(content_hash, summary)
        await redis_service.remove_hash_inflight(content_hash)


@celery_app.task(name="worker.main.process_document", bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    """Celery task wrapper for document processing."""

    async def run_task():
        await connect_to_mongo()
        await redis_service.connect()
        try:
            return await _process_document_logic(document_id)
        finally:
            await close_mongo_connection()
            await redis_service.close()

    try:
        return asyncio.run(run_task())
    except Exception as exc:
        logger.warning(f"Task failed for document {document_id}: {str(exc)}")
        # Exponential backoff: 2, 4, 8...
        countdown = 2**self.request.retries

        # If we exhausted retries, we need to handle the failure state in DB
        if self.request.retries >= self.max_retries:
            logger.error(f"All retries failed for document {document_id}")

            async def handle_failure():
                await connect_to_mongo()
                await redis_service.connect()
                try:
                    db = db_helper.db
                    doc = await db.documents.find_one({"_id": ObjectId(document_id)})
                    if doc:
                        content_hash = doc.get("content_hash")
                        update_filter = {
                            "content_hash": content_hash,
                            "status": {
                                "$in": [
                                    DocumentStatus.QUEUED,
                                    DocumentStatus.PROCESSING,
                                ]
                            },
                        }
                        affected_docs = await db.documents.find(update_filter).to_list(
                            length=100
                        )
                        for affected_doc in affected_docs:
                            await redis_service.decrement_active_jobs(
                                affected_doc["user_id"]
                            )

                        await db.documents.update_many(
                            update_filter,
                            {
                                "$set": {
                                    "status": DocumentStatus.FAILED,
                                    "updated_at": datetime.now(timezone.utc),
                                }
                            },
                        )
                        if content_hash:
                            await redis_service.remove_hash_inflight(content_hash)
                finally:
                    await close_mongo_connection()
                    await redis_service.close()

            asyncio.run(handle_failure())
            raise exc

        raise self.retry(exc=exc, countdown=countdown)
