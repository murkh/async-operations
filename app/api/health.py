from fastapi import APIRouter, Depends, HTTPException

from pymongo.database import Database
from app.core.database import get_db
from app.services.redis_service import redis_service


router = APIRouter(prefix="/health")


@router.get("")
async def health_check(db: Database = Depends(get_db)):
    health_status = {"status": "ok", "mongodb": "unknown", "redis": "unknown"}

    # Check Mongo
    try:
        await db.command("ping")
        health_status["mongodb"] = "ok"
    except Exception:
        health_status["mongodb"] = "error"
        health_status["status"] = "error"

    # Check Redis
    try:
        await redis_service.redis_client.ping()
        health_status["redis"] = "ok"
    except Exception:
        health_status["redis"] = "error"
        health_status["status"] = "error"

    if health_status["status"] == "error":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
