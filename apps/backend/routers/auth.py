from fastapi import APIRouter, HTTPException, status
from datetime import timedelta

from models.schemas import Token, User
from core.auth import create_access_token
from core.config import settings

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user_id: str):
    """
    Simple login endpoint for development
    In production, this would integrate with AWS Cognito
    """
    try:
        # Create access token
        access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_id}, 
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/register", response_model=Token)
async def register(user_id: str, email: str):
    """
    Simple registration endpoint for development
    In production, this would integrate with AWS Cognito
    """
    try:
        # In a real implementation, you would:
        # 1. Validate email format
        # 2. Check if user already exists
        # 3. Create user in Cognito
        # 4. Send verification email
        
        # For now, just create a token
        access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_id}, 
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/me", response_model=User)
async def get_current_user_info():
    """
    Get current user information
    In production, this would fetch from AWS Cognito
    """
    # Mock user data for development
    return User(
        id="dev-user-123",
        email="dev@example.com",
        full_name="Development User",
        created_at="2025-01-01T00:00:00"
    )
