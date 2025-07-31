"""
Database engine configuration.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import StaticPool

# ============================================================================
# CONSTANTS
# ============================================================================
# Database URL for SQLite
DATABASE_URL = "sqlite+aiosqlite:///./brainboard.db"

# Engine settings
ENGINE_ECHO = False  # Set to True for SQL query logging

# SQLite specific settings
SQLITE_CHECK_SAME_THREAD = False

# ============================================================================
# ENGINE CONFIGURATION
# ============================================================================
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=ENGINE_ECHO,
    poolclass=StaticPool,
    connect_args={"check_same_thread": SQLITE_CHECK_SAME_THREAD}
)

# ============================================================================
# ENGINE FUNCTIONS
# ============================================================================
async def get_engine() -> AsyncEngine:
    """Get the database engine."""
    return engine

async def close_engine():
    """Close the database engine."""
    await engine.dispose() 