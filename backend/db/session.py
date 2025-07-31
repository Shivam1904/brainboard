"""
Database session management.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db.engine import engine

# ============================================================================
# CONSTANTS
# ============================================================================
# Session settings
SESSION_EXPIRE_ON_COMMIT = False

# ============================================================================
# SESSION FACTORY
# ============================================================================
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=SESSION_EXPIRE_ON_COMMIT
)

# ============================================================================
# SESSION FUNCTIONS
# ============================================================================
async def get_session() -> AsyncSession:
    """Get a database session."""
    async with AsyncSessionLocal() as session:
        yield session 