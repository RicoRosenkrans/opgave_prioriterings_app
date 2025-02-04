from typing import Optional, Dict, Any
import asyncio
from functools import wraps
import logging
from app.core.cache import cache_response

logger = logging.getLogger(__name__)

def with_fallback(fallback_value: Any, max_retries: int = 3, timeout: int = 10):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    # Kør funktionen med timeout
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout
                    )
                    return result
                except asyncio.TimeoutError:
                    logger.warning(
                        f"Timeout på forsøg {attempt + 1}/{max_retries} "
                        f"for {func.__name__}"
                    )
                except Exception as e:
                    logger.error(
                        f"Fejl på forsøg {attempt + 1}/{max_retries} "
                        f"for {func.__name__}: {str(e)}"
                    )
                
                # Vent lidt længere mellem hvert forsøg
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
            
            logger.error(
                f"Alle forsøg fejlede for {func.__name__}, "
                f"returnerer fallback værdi"
            )
            return fallback_value
        return wrapper
    return decorator 