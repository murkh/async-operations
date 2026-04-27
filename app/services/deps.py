from fastapi import Depends, Request
from pymongo.database import Database

from app.core.database import get_db
from .document_service import DocumentService
from ..repositories.document_repository import DocumentRepository


def get_document_service(
    db: Database = Depends(get_db),
) -> DocumentService:
    repository = DocumentRepository(db)
    return DocumentService(repository)


def RateLimit(requests: int = None, window: int = None):
    async def dependency(request: Request):
        from app.services.rate_limiter import rate_limiter
        from app.core.config import settings
        from starlette.exceptions import HTTPException
        from fastapi import status

        client_ip = request.client.host if request.client else "unknown"
        limit = requests or settings.RATE_LIMIT_REQUESTS
        period = window or settings.RATE_LIMIT_WINDOW_SECONDS

        if await rate_limiter.is_rate_limited(client_ip, limit, period):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )
        return True

    return dependency
