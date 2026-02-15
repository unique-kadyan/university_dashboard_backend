from fastapi import APIRouter
from sqlalchemy import text
from starlette.responses import JSONResponse

from configs.db_config import AsyncSessionLocal
from configs.redis_config import redis_client

health_router = APIRouter(tags=["Health"])


@health_router.get("/health")
async def health_check():
    health = {
        "status": "healthy",
        "checks": {
            "database": {"status": "unknown"},
            "redis": {"status": "unknown"},
        },
    }
    overall_healthy = True

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        health["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False

    try:
        await redis_client.ping()
        health["checks"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False

    health["status"] = "healthy" if overall_healthy else "degraded"
    status_code = 200 if overall_healthy else 503

    return JSONResponse(content=health, status_code=status_code)
