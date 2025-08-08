"""
Database dependency injection.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import AsyncSessionLocal

# ============================================================================
# DEPENDENCY FUNCTIONS
# ============================================================================
async def get_db_session_dependency() -> AsyncSession:
    """
    Get database session dependency.
    
    This ensures each request gets a fresh session and proper cleanup.
    The session is automatically closed when the request completes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            # Rollback on any exception
            await session.rollback()
            raise
        finally:
            # Always close the session
            await session.close() 