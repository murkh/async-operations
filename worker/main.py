import asyncio
import logging
import random
from datetime import datetime, timezone

from bson import ObjectId

from app.core.database import connect_to_mongo, close_mongo_connection
from app.services.redis_service import redis_service
from app.schemas.documents import DocumentStatus
from app.core.database import db_helper
from app.core.logging import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger("worker")


async def process_document(document_id: str):

    db = db_helper.db

    # Atomically pick up and mark as processing
    doc = await db.documents.find_one_and_update(
        {
            "_id": ObjectId(document_id),
            "status": DocumentStatus.QUEUED
        },
        {
            "$set": {
                "status": DocumentStatus.PROCESSING,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        return_document=True
    )

    if not doc:
        logger.warning(f"Document {document_id} not found or already being processed")
        return

    content_hash = doc.get("content_hash")
    user_id = doc.get("user_id")
    logger.info(
        f"Processing document {document_id} (User: {user_id})",
        extra={"document_id": document_id, "user_id": user_id, "content_hash": content_hash}
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Simulate Work
            sleep_time = random.uniform(10, 30)
            await asyncio.sleep(sleep_time)

            if random.random() < 0.10:
                raise Exception("Simulated network failure")

            logger.info(
                f"Successfully processed document {document_id}",
                extra={"document_id": document_id, "user_id": user_id}
            )
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

            return

        except Exception as e:
            if attempt < max_retries - 1:
                wait_backoff = 2**attempt
                logger.warning(
                    f"Attempt {attempt + 1} failed for {document_id}: {e}. Retrying in {wait_backoff}s...",
                    extra={"document_id": document_id, "attempt": attempt + 1, "error": str(e)}
                )
                await asyncio.sleep(wait_backoff)
            else:
                logger.error(
                    f"All attempts failed for document {document_id}. Marking as FAILED. Error: {e}",
                    extra={"document_id": document_id, "error": str(e)},
                    exc_info=True
                )
                update_filter = {
                    "content_hash": content_hash,
                    "status": [DocumentStatus.QUEUED, DocumentStatus.PROCESSING],
                }

                affected_docs = await db.documents.find(update_filter).to_list(
                    length=100
                )
                for affected_doc in affected_docs:
                    await redis_service.decrement_active_jobs(affected_doc["user_id"])

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


async def main():

    await connect_to_mongo()
    await redis_service.connect()
    logger.info("Worker connected to MongoDB and Redis")

    redis_client = redis_service.redis_client
    queue_name = redis_service.queue_name

    try:
        while True:
            result = await redis_client.blpop(queue_name, timeout=1)

            if result:
                _, document_id = result
                logger.info(f"Received job for document {document_id}")
                asyncio.create_task(process_document(document_id))

    except asyncio.CancelledError:
        logger.info("Worker cancelled, shutting down...")
    except Exception as e:
        logger.error(f"Worker error: {e}")
    finally:
        await close_mongo_connection()
        await redis_service.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
