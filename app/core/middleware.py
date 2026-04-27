import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request details
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"{method} {path} - {response.status_code} - {process_time:.2f}ms",
                extra={
                    "method": method,
                    "path": path,
                    "client_host": client_host,
                    "status_code": response.status_code,
                    "process_time_ms": process_time,
                }
            )
            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"{method} {path} - Failed - {process_time:.2f}ms - Error: {str(e)}",
                extra={
                    "method": method,
                    "path": path,
                    "client_host": client_host,
                    "process_time_ms": process_time,
                    "error": str(e),
                },
                exc_info=True
            )
            raise e
