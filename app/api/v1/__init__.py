from fastapi import APIRouter
from .documents import router as document_router

router = APIRouter(prefix="/v1")
router.include_router(document_router)
