from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.core.config import config as app_config # Get main app config

# Determine the async database URL
SYNC_DB_URL = app_config.database_url
ASYNC_DB_URL = SYNC_DB_URL

if SYNC_DB_URL.startswith("sqlite:///"):
    # For SQLite, ensure the async driver is specified
    ASYNC_DB_URL = SYNC_DB_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
elif SYNC_DB_URL.startswith("postgresql://"):
    # For PostgreSQL, ensure the async driver is specified (e.g., asyncpg)
    # Users should ideally set DATABASE_URL to postgresql+asyncpg://...
    # This is a basic attempt to convert if they haven't.
    if "+asyncpg" not in SYNC_DB_URL:
        ASYNC_DB_URL = SYNC_DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
# Add other database dialect transformations here if needed (e.g., MySQL)

# Create an async engine
async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=app_config.echo_sql, # Use echo_sql from config
    pool_size=app_config.SQLALCHEMY_POOL_SIZE, # Use global constant
    max_overflow=app_config.SQLALCHEMY_MAX_OVERFLOW, # Use global constant
    pool_timeout=app_config.SQLALCHEMY_POOL_TIMEOUT, # Use global constant
    pool_recycle=app_config.SQLALCHEMY_POOL_RECYCLE, # Use global constant
)

# Create a session factory bound to the engine
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_async_db() -> AsyncSession:
    \"\"\"FastAPI dependency to get an async database session.\"\"\"
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # Commit after successful endpoint execution
        except Exception:
            await session.rollback() # Rollback on error
            raise
        finally:
            await session.close()

# Optional: A function to create tables (useful for init or testing)
# from .models import Base # Assuming Base is accessible here, might need adjustment
# async def create_database_tables():
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all) 
