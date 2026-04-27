from typing import Optional
from fastapi import APIRouter, status, Depends, Query

from app.schemas.documents import (
    DocumentResponse,
    DocumentCreate,
    DocumentUpdate,
    DocumentListResponse,
    DocumentStatus,
)
from app.services.document_service import DocumentService
from app.services.deps import get_document_service


router = APIRouter(prefix="/documents")


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    doc: DocumentCreate, svc: DocumentService = Depends(get_document_service)
):
    return await svc.create_document(doc)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[DocumentStatus] = None,
    svc: DocumentService = Depends(get_document_service),
):
    return await svc.list_user_documents(user_id, page, page_size, status)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str, svc: DocumentService = Depends(get_document_service)
):
    return await svc.get_document(document_id)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    doc_update: DocumentUpdate,
    svc: DocumentService = Depends(get_document_service),
):
    return await svc.update_document(document_id, doc_update)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str, svc: DocumentService = Depends(get_document_service)
):
    await svc.delete_document(document_id)
    return None
