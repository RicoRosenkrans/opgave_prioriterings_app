import pytest
from app.ai.chains.base import with_fallback
import asyncio

@pytest.mark.asyncio
async def test_fallback_success():
    @with_fallback(fallback_value="fallback")
    async def test_func():
        return "success"
    
    result = await test_func()
    assert result == "success"

@pytest.mark.asyncio
async def test_fallback_after_timeout():
    @with_fallback(fallback_value="fallback", timeout=0.1)
    async def test_func():
        await asyncio.sleep(0.2)  # Længere end timeout
        return "success"
    
    result = await test_func()
    assert result == "fallback"

@pytest.mark.asyncio
async def test_fallback_after_error():
    @with_fallback(fallback_value="fallback")
    async def test_func():
        raise ValueError("Test error")
    
    result = await test_func()
    assert result == "fallback"

@pytest.mark.asyncio
async def test_fallback_retry_logic():
    call_count = 0
    
    @with_fallback(fallback_value="fallback", max_retries=3)
    async def test_func():
        nonlocal call_count
        call_count += 1
        raise ValueError("Test error")
    
    result = await test_func()
    assert result == "fallback"
    assert call_count == 3  # Skulle have forsøgt 3 gange 