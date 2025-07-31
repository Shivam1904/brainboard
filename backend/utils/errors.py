"""
Standardized error handling utilities.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import HTTPException, status
from typing import Dict, Any

# ============================================================================
# ERROR CONSTANTS
# ============================================================================
class ErrorMessages:
    """Standard error messages."""
    NOT_FOUND = "Resource not found"
    VALIDATION_ERROR = "Invalid input data"
    DATABASE_ERROR = "Database operation failed"
    INTERNAL_ERROR = "Internal server error"

# ============================================================================
# ERROR FUNCTIONS
# ============================================================================
def raise_not_found(detail: str = ErrorMessages.NOT_FOUND) -> HTTPException:
    """Raise 404 Not Found error."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )

def raise_validation_error(detail: str = ErrorMessages.VALIDATION_ERROR) -> HTTPException:
    """Raise 422 Validation Error."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail
    )

def raise_database_error(detail: str = ErrorMessages.DATABASE_ERROR) -> HTTPException:
    """Raise 500 Database Error."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail
    )

def raise_internal_error(detail: str = ErrorMessages.INTERNAL_ERROR) -> HTTPException:
    """Raise 500 Internal Server Error."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail
    ) 