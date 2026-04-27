from fastapi import APIRouter

from app.api.health import router as router_health
from app.api.v1 import router as router_v1


router = APIRouter(prefix="/api")
router.include_router(router=router_health)
router.include_router(router=router_v1)
