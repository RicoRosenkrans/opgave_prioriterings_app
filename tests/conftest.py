import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.main import app
from fastapi.testclient import TestClient
from app.models.base import get_session
import asyncio
import os
from typing import Generator
from unittest.mock import patch, AsyncMock

# Brug SQLite for tests
TEST_DB_PATH = "test.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    # Slet test database hvis den eksisterer
    if os.path.exists(TEST_DB_PATH):
        os.unlink(TEST_DB_PATH)

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False}
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

    # Cleanup efter tests
    if os.path.exists(TEST_DB_PATH):
        os.unlink(TEST_DB_PATH)

@pytest.fixture(autouse=True)
async def session(db_engine) -> AsyncSession:
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        # Ryd op efter hver test
        await session.rollback()

@pytest.fixture
def client(session: AsyncSession) -> Generator:
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_openai_key():
    """Automatically mock OpenAI API key for all tests"""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        yield 

@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis for all tests"""
    with patch('app.core.cache.redis') as mock:
        # Simuler en simpel in-memory cache
        cache_data = {}
        
        async def mock_get(key):
            return cache_data.get(key)
            
        async def mock_set(key, value, ex=None):
            cache_data[key] = value
            return True
            
        async def mock_delete(key):
            if key in cache_data:
                del cache_data[key]
            return True
            
        mock.get = AsyncMock(side_effect=mock_get)
        mock.set = AsyncMock(side_effect=mock_set)
        mock.delete = AsyncMock(side_effect=mock_delete)
        yield mock 