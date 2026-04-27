from typing import Optional, List, Tuple
from bson import ObjectId

from pymongo.database import Database
from app.schemas.documents import DocumentStatus


class DocumentRepository:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.documents

    async def create(self, doc_data: dict) -> str:
        """Insert a new document and return its ID."""
        result = await self.collection.insert_one(doc_data)
        return str(result.inserted_id)

    async def get_by_id(self, doc_id: str) -> Optional[dict]:
        """Retrieve a document by its ID."""
        if not ObjectId.is_valid(doc_id):
            return None
        return await self.collection.find_one({"_id": ObjectId(doc_id)})

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        status: Optional[DocumentStatus] = None,
    ) -> Tuple[List[dict], int]:
        """List documents for a user with pagination and optional status filter."""
        query = {"user_id": user_id}
        if status:
            query["status"] = status.value

        cursor = (
            self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        total = await self.collection.count_documents(query)

        return docs, total

    async def update(self, doc_id: str, update_data: dict) -> bool:
        """Update a document by its ID."""
        if not ObjectId.is_valid(doc_id):
            return False
        result = await self.collection.update_one(
            {"_id": ObjectId(doc_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete(self, doc_id: str) -> bool:
        """Delete a document by its ID."""
        if not ObjectId.is_valid(doc_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0
