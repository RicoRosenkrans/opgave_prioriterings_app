from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
import os
from dotenv import load_dotenv

load_dotenv()

# Hent database URL fra miljøvariabel
DATABASE_URL = os.getenv("DATABASE_URL")

# Konverter postgres:// til postgresql:// (Heroku specifik fix)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Opret async engine
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL logging
    pool_pre_ping=True,  # Connection health checks
)

# Opret async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for SQLAlchemy models
Base = declarative_base()

# Database initialization function
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Database cleanup function
async def close_db():
    await engine.dispose()

# Dependency for FastAPI
async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close() 