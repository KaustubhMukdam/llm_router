import os
import redis
from typing import Optional

_redis_client: Optional[redis.Redis] = None


def _get_client() -> Optional[redis.Redis]:
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        return None

    try:
        _redis_client = redis.Redis.from_url(
            redis_url,
            decode_responses=True
        )
        return _redis_client
    except Exception:
        return None


def get(key: str) -> Optional[str]:
    client = _get_client()
    if client is None:
        return None

    try:
        return client.get(key)
    except Exception:
        return None


def set(key: str, value: str, ttl: int) -> None:
    client = _get_client()
    if client is None:
        return

    try:
        client.setex(key, ttl, value)
    except Exception:
        return
