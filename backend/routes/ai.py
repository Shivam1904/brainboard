"""
AI routes for direct API access to AI operations.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import logging

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from datetime import date

from orchestrators.ai_orchestrator import AIOrchestrator
from schemas.ai import (
    DailyPlanResponse, WebSummaryResponse, ActivityGenerationResponse,
    AIErrorResponse
)

# ============================================================================
# CONSTANTS
# ============================================================================
router = APIRouter(prefix="/api/v1/ai", tags=["AI Operations"])

from config import settings

# ============================================================================
# DEPENDENCIES
# ============================================================================

def get_default_user_id() -> str:
    """Get default user ID for development."""
    return settings.DEFAULT_USER_ID

# ============================================================================
# AI ENDPOINTS
# ============================================================================

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@router.get("/health")
async def ai_health_check():
    """
    Check the health of AI services.
    
    This endpoint:
    - Verifies AI orchestrator is operational
    - Checks database connectivity
    - Returns health status
    """
    orchestrator = None
    try:
        orchestrator = AIOrchestrator()
        health_result = await orchestrator.get_configuration_summary()
        
        return {
            "status": "healthy",
            "ai_orchestrator": health_result,
            "message": "AI services are operational"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "ai_orchestrator": {
                "status": "unhealthy",
                "message": f"AI orchestrator health check failed: {str(e)}"
            },
            "message": "AI services are not operational"
        }

# ============================================================================
# WEBSOCKET ENDPOINT FOR REAL-TIME AI CHAT
# ============================================================================

import json
import uuid
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any

from services.ai_websocket_manager import AIWebSocketManager

# Global WebSocket manager instance
ai_websocket_manager = AIWebSocketManager()

@router.websocket("/ws")
async def websocket_ai(websocket: WebSocket):
    """
    WebSocket endpoint for real-time AI chat using the orchestrator directly.
    Connect to: ws://localhost:8989/api/v1/ai/ws
    """
    connection_id = str(uuid.uuid4())
    orchestrator = None
    
    try:
        # Create orchestrator with its own database session
        orchestrator = AIOrchestrator()
        
        # Delegate session handling to manager
        await ai_websocket_manager.handle_session(websocket, connection_id, orchestrator)
                
    except WebSocketDisconnect:
        logger.info(f"AI WebSocket disconnected: {connection_id}")
    except Exception as e:        
        logger.error(f"AI WebSocket error: {e}")
    finally:
        # Clean up resources
        ai_websocket_manager.disconnect(connection_id)

@router.get("/websocket/health")
async def websocket_health():
    """Health check endpoint for AI WebSocket service."""
    return {
        "status": "healthy",
        "active_connections": len(ai_websocket_manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    } 