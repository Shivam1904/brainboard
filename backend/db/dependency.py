"""
Database dependency injection.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session

# ============================================================================
# DEPENDENCY FUNCTIONS
# ============================================================================
async def get_db_session_dependency() -> AsyncSession:
    """Get database session dependency."""
    async for session in get_session():
        yield session 