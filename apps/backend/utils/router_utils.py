"""
Common utilities for router implementations
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Any
from datetime import date
import logging

from models.database_models import DashboardWidget, User

logger = logging.getLogger(__name__)

class RouterUtils:
    """Common utilities used across all routers"""
    
    @staticmethod
    def get_default_user_id(db: Session) -> str:
        """Get default user ID for development purposes"""
        default_user = db.query(User).filter(User.email == "default@brainboard.com").first()
        if not default_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Default user not found. Please ensure database is initialized."
            )
        return default_user.id
    
    @staticmethod
    def verify_widget_exists(db: Session, widget_id: str, widget_type: Optional[str] = None) -> DashboardWidget:
        """
        Verify that a widget exists and optionally check its type
        
        Args:
            db: Database session
            widget_id: Widget ID to check
            widget_type: Optional widget type to verify
            
        Returns:
            DashboardWidget object
            
        Raises:
            HTTPException: If widget not found or type mismatch
        """
        query = db.query(DashboardWidget).filter(DashboardWidget.id == widget_id)
        
        if widget_type:
            query = query.filter(DashboardWidget.widget_type == widget_type)
        
        widget = query.first()
        
        if not widget:
            error_detail = f"Widget not found"
            if widget_type:
                error_detail = f"{widget_type.title()} widget not found"
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_detail
            )
        
        return widget
    
    @staticmethod
    def handle_database_error(operation: str, error: Exception) -> None:
        """
        Standardized database error handling
        
        Args:
            operation: Description of the operation that failed
            error: The exception that occurred
            
        Raises:
            HTTPException: With appropriate status code and message
        """
        logger.error(f"Database error during {operation}: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to {operation}: {str(error)}"
        )
    
    @staticmethod
    def validate_pagination(skip: int = 0, limit: int = 100) -> tuple[int, int]:
        """
        Validate and normalize pagination parameters
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (validated_skip, validated_limit)
        """
        skip = max(0, skip)
        limit = min(max(1, limit), 1000)  # Cap at 1000 records
        return skip, limit
    
    @staticmethod
    def format_success_response(message: str, data: Optional[Any] = None) -> dict:
        """
        Format a standardized success response
        
        Args:
            message: Success message
            data: Optional data to include
            
        Returns:
            Formatted response dictionary
        """
        response = {"message": message}
        if data is not None:
            response["data"] = data
        return response
