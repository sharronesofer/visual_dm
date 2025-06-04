from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from backend.infrastructure.core.config import settings

# Import Base from the correct location
try:
    from backend.infrastructure.shared.database.base import Base
except ImportError:
    # Fallback - create Base here if shared doesn't exist
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

# Sync SQLAlchemy setup
engine = None
SessionLocal = None

if settings.SQLALCHEMY_DATABASE_URI:
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async SQLAlchemy setup
async_engine = None
AsyncSessionLocal = None

if settings.ASYNC_SQLALCHEMY_DATABASE_URI:
    async_engine = create_async_engine(
        settings.ASYNC_SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
    )
    AsyncSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=async_engine, 
        class_=AsyncSession
    )


# Dependency for sync operations
def get_db():
    if not SessionLocal:
        raise Exception("Database connection not configured")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for async operations
async def get_async_db():
    if not AsyncSessionLocal:
        raise Exception("Async database connection not configured")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 