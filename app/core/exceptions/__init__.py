from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception for all application errors."""

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        detail: str = "Resource not found",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers
        )


class BadRequestException(AppException):
    """Exception raised for bad requests."""

    def __init__(
        self, detail: str = "Bad request", headers: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers
        )


class UnauthorizedException(AppException):
    """Exception raised when authentication is required or failed."""

    def __init__(
        self, detail: str = "Unauthorized", headers: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers
        )


class ForbiddenException(AppException):
    """Exception raised when access is denied."""

    def __init__(
        self, detail: str = "Forbidden", headers: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers
        )


class ConflictException(AppException):
    """Exception raised when there is a conflict in the resource state."""

    def __init__(
        self, detail: str = "Conflict", headers: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers
        )


class RateLimitException(AppException):
    """Exception raised when rate limits are exceeded."""

    def __init__(
        self,
        detail: str = "Too many requests",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=headers,
        )


class InternalServerException(AppException):
    """Exception raised for internal server errors."""

    def __init__(
        self,
        detail: str = "Internal server error",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
        )


class UnprocessableEntityException(AppException):
    """Exception raised for validation errors or unprocessable entities."""

    def __init__(
        self,
        detail: str = "Unprocessable entity",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            headers=headers,
        )
