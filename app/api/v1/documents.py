from fastapi import APIRouter, status, Depends

from app.models.schemas import DocumentResponse, DocumentCreate
from app.services.document_service import DocumentService
from app.api.deps import get_document_service


router = APIRouter(prefix="/documents")


@router.post(
    "/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED
)
async def create_document(
    doc: DocumentCreate, svc: DocumentService = Depends(get_document_service)
):
    return await svc.create_document(doc)
