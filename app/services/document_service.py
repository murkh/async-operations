from datetime import datetime
import math
from typing import Dict, Any, Optional
from ..core.exceptions import InternalServerException, NotFoundException
from .redis_service import redis_service, RedisService
from ..repositories.document_repository import DocumentRepository
from ..schemas.documents import (
    DocumentCreate,
    DocumentResponse,
    DocumentStatus,
)


class DocumentService:
    def __init__(self, repo: DocumentRepository):
        self.repo = repo

    async def create_document(self, doc: DocumentCreate) -> Dict[str, Any]:
        content_hash = RedisService.compute_hash(doc.content)
        cached_summary = await redis_service.get_cached_summary(content_hash)

        now = datetime.now()
        doc_dict = doc.dict()
        doc_dict["created_at"] = now
        doc_dict["updated_at"] = now

        if cached_summary:
            doc_dict["summary"] = cached_summary
            doc_dict["status"] = DocumentStatus.PROCESSED

            doc_id = await self.repo.create(doc_dict)
            doc_dict["id"] = doc_id
            return doc_dict

        doc_dict["status"] = DocumentStatus.QUEUED
        doc_dict["summary"] = None

        await redis_service.increment_active_jobs(doc.user_id)

        try:
            is_inflight = await redis_service.is_hash_inflight(content_hash)
            doc_id = await self.repo.create(doc_dict)

            if not is_inflight:
                await redis_service.set_hash_inflight(content_hash)
                await redis_service.enqueue_doc(doc_id)

            doc_dict["id"] = doc_id
            return doc_dict
        except Exception as e:
            print(f"Error creating document: {e}")
            await redis_service.decrement_active_jobs(doc.user_id)
            raise e

    async def get_document(self, doc_id: str) -> DocumentResponse:
        docs = await self.repo.get_by_id(doc_id)
        if not docs:
            raise NotFoundException("Document not found")
        return DocumentResponse(**docs)

    async def list_user_documents(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
        status_filter: Optional[DocumentStatus] = None,
    ) -> Dict[str, Any]:
        """List documents for a user with pagination."""
        skip = (page - 1) * page_size
        docs, total = await self.repo.list_by_user(
            user_id, skip, page_size, status_filter
        )

        formatted_docs = []
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            formatted_docs.append(doc)

        return {
            "items": formatted_docs,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": math.ceil(total / page_size) if total > 0 else 0,
        }
