from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from backend.app.core.config import settings

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

Base = declarative_base()

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