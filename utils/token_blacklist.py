from redis.asyncio import Redis
from configs.redis_config import redis_client
from utils.jwt_handler import verify_token

BLACKLIST_PREFIX = "blacklisted_token:"


async def blacklist_token(token: str) -> None:
    payload = verify_token(token)
    exp = payload.get("exp")
    if exp:
        from datetime import datetime, timezone
        remaining = exp - int(datetime.now(timezone.utc).timestamp())
        if remaining > 0:
            await redis_client.setex(f"{BLACKLIST_PREFIX}{token}", remaining, "1")


async def is_token_blacklisted(token: str) -> bool:
    result = await redis_client.get(f"{BLACKLIST_PREFIX}{token}")
    return result is not None
