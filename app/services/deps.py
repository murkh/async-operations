from fastapi import Depends
from pymongo.database import Database

from app.core.database import get_db
from .document_service import DocumentService
from ..repositories.document_repository import DocumentRepository


def get_document_service(
    db: Database = Depends(get_db),
) -> DocumentService:
    repository = DocumentRepository(db)
    return DocumentService(repository)
