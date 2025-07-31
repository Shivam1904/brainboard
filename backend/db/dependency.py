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
    """Get database session dependency."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 