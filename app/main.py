from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import connect_to_mongo, close_mongo_connection
from app.services.redis_service import redis_service
from app.api import router
from app.core.exception_handler import setup_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import LoggingMiddleware
from app.core.rate_limit import RateLimitMiddleware

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await connect_to_mongo()
    from app.core.database import init_db
    await init_db()
    await redis_service.connect()
    yield

    # shutdown
    await close_mongo_connection()
    await redis_service.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
setup_exception_handlers(app)
app.include_router(router=router)
