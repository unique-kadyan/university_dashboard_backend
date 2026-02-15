import secrets
import string

from fastapi import HTTPException, status

from configs.redis_config import redis_client

OTP_PREFIX = "otp:"
OTP_ATTEMPTS_PREFIX = "otp_attempts:"
OTP_EXPIRY_SECONDS = 300
MAX_OTP_ATTEMPTS = 5


def generate_otp(length: int = 6) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))


async def store_otp(email: str, otp: str) -> None:
    await redis_client.setex(f"{OTP_PREFIX}{email}", OTP_EXPIRY_SECONDS, otp)
    await redis_client.delete(f"{OTP_ATTEMPTS_PREFIX}{email}")


async def verify_otp(email: str, otp: str) -> bool:
    attempts_key = f"{OTP_ATTEMPTS_PREFIX}{email}"
    attempts = await redis_client.get(attempts_key)
    if attempts and int(attempts) >= MAX_OTP_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP attempts. Please request a new OTP.",
        )

    stored_otp = await redis_client.get(f"{OTP_PREFIX}{email}")
    if stored_otp and stored_otp == otp:
        await redis_client.delete(f"{OTP_PREFIX}{email}")
        await redis_client.delete(attempts_key)
        return True

    await redis_client.incr(attempts_key)
    await redis_client.expire(attempts_key, OTP_EXPIRY_SECONDS)
    return False
