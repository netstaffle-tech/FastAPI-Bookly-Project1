from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from src.config import Config

class Base(DeclarativeBase):
    pass

# Create async engine
async_engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,          # Set False in production
    pool_pre_ping=True, # Validate connections before using them
)

# Create database tables
async def init_db():
    async with async_engine.begin() as conn:
        # Import models so SQLAlchemy registers them on Base.metadata
        from src.books.models import Book  # noqa: F401
        #from src.auth.models import User

        await conn.run_sync(Base.metadata.create_all)

# Session factory (created only once)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# FastAPI dependency
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session