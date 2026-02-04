import random
import string
from configs.redis_config import redis_client

OTP_PREFIX = "otp:"
OTP_EXPIRY_SECONDS = 300  # 5 minutes


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


async def store_otp(email: str, otp: str) -> None:
    await redis_client.setex(f"{OTP_PREFIX}{email}", OTP_EXPIRY_SECONDS, otp)


async def verify_otp(email: str, otp: str) -> bool:
    stored_otp = await redis_client.get(f"{OTP_PREFIX}{email}")
    if stored_otp and stored_otp == otp:
        await redis_client.delete(f"{OTP_PREFIX}{email}")
        return True
    return False
