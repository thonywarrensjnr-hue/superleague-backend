from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import asyncpg
import logging
from contextlib import asynccontextmanager

from app.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Convert postgresql:// to postgresql+asyncpg:// for async support
DATABASE_URL = settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=10,
    pool_pre_ping=True  # Verify connections before using
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


class DatabaseManager:
    """Database manager with connection pooling and error handling"""

    def __init__(self):
        self.engine = engine
        self.session_local = AsyncSessionLocal

    @asynccontextmanager
    async def get_session(self):
        """Get database session with automatic closing"""
        session = self.session_local()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()

    async def execute_sql(self, query: str, *args):
        """Execute raw SQL with parameters (for simple queries)"""
        conn = await asyncpg.connect(settings.DATABASE_URL)
        try:
            if args:
                return await conn.fetch(query, *args)
            else:
                return await conn.fetch(query)
        finally:
            await conn.close()

    async def create_tables(self):
        """Create all tables (for development)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully")

    async def drop_tables(self):
        """Drop all tables (for development)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Tables dropped successfully")


# Create global database manager
db_manager = DatabaseManager()


# Dependency to get database session
async def get_db():
    """FastAPI dependency for database session"""
    async with db_manager.get_session() as session:
        yield session