import pytest
from app.core.cache import CacheManager, cache_response
from unittest.mock import patch, AsyncMock

@pytest.fixture
async def cache_manager():
    return CacheManager(expire_time=60)

@pytest.mark.asyncio
async def test_cache_set_get(cache_manager):
    # Test basic set/get
    await cache_manager.set("test_key", "test_value")
    result = await cache_manager.get("test_key")
    assert result == "test_value"

@pytest.mark.asyncio
async def test_cache_delete(cache_manager):
    await cache_manager.set("test_key", "test_value")
    await cache_manager.delete("test_key")
    result = await cache_manager.get("test_key")
    assert result is None

@pytest.mark.asyncio
async def test_cache_decorator():
    call_count = 0
    
    @cache_response(expire_time=60)
    async def test_func(param):
        nonlocal call_count
        call_count += 1
        return f"result_{param}"
    
    # Første kald skal gå igennem funktionen
    result1 = await test_func("test")
    assert result1 == "result_test"
    assert call_count == 1
    
    # Andet kald skal komme fra cache
    result2 = await test_func("test")
    assert result2 == "result_test"
    assert call_count == 1  # Stadig kun ét reelt kald

@pytest.mark.asyncio
async def test_cache_error_handling(cache_manager):
    with patch('app.core.cache.redis.get', side_effect=Exception("Redis error")):
        result = await cache_manager.get("test_key")
        assert result is None

    with patch('app.core.cache.redis.set', side_effect=Exception("Redis error")):
        success = await cache_manager.set("test_key", "test_value")
        assert not success 