import logging
import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import AppException
from app.core.config import settings


logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(f"AppException: {exc.detail} (Code: {exc.status_code})")
        content = {
            "status": "error",
            "code": exc.status_code,
            "message": exc.detail,
            "detail": exc.detail,
        }
        if settings.DEBUG:
            content["traceback"] = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )

        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        content = {
            "status": "error",
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error",
        }
        if settings.DEBUG:
            content["message"] = str(exc)
            content["traceback"] = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )
