from fastapi import Depends

from app.models.db import get_database
from app.models.db.types import DataBase
from .document_service import DocumentService
from ..repositories.document_repository import DocumentRepository


def get_document_service(
    db: DataBase = Depends(get_database),
) -> DocumentService:
    repository = DocumentRepository(db)
    return DocumentService(repository)
