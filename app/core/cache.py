from redis import asyncio as aioredis
import json
from typing import Optional, Any
import os
from functools import wraps
import asyncio

# Redis connection
redis = aioredis.from_url(
    os.getenv("REDIS_URL", "redis://localhost"),
    encoding="utf-8",
    decode_responses=True
)

class CacheManager:
    def __init__(self, expire_time: int = 3600):
        self.redis = redis
        self.default_expire = expire_time

    async def get(self, key: str) -> Optional[str]:
        try:
            return await self.redis.get(key)
        except Exception:
            return None

    async def set(
        self,
        key: str,
        value: str,
        expire: int = None
    ) -> bool:
        try:
            await self.redis.set(
                key,
                value,
                ex=expire or self.default_expire
            )
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False

def cache_response(expire_time: int = 3600):
    def decorator(func):
        # Opret en delt cache manager instance for hver dekoreret funktion
        cache = CacheManager(expire_time=expire_time)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generer cache key baseret på funktion og argumenter
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Prøv at hente fra cache først
            cached_result = await cache.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Hvis ikke i cache, kald original funktion
            result = await func(*args, **kwargs)
            
            # Gem resultatet i cache
            await cache.set(
                cache_key,
                json.dumps(result),
                expire_time
            )
            
            return result
        return wrapper
    return decorator 