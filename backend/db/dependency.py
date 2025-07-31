"""
Dependency injection configuration.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .session import AsyncSessionLocal

async def get_db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close() 