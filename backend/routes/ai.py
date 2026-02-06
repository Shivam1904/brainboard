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

# Default user ID for development
DEFAULT_USER_ID = "user_001"

# ============================================================================
# DEPENDENCIES
# ============================================================================

def get_default_user_id() -> str:
    """Get default user ID for development."""
    return DEFAULT_USER_ID

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
        
        await ai_websocket_manager.connect(websocket, connection_id)
        
        await ai_websocket_manager.send_message(connection_id, {
            "type": "connection",
            "connection_id": connection_id,
            "message": "Connected to Brainboard AI Service",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await ai_websocket_manager.send_thinking_step(connection_id, "welcome", "AI service ready! Send me a message to get started.")

        # Use websocket.iter_text() for cleaner WebSocket handling
        async for message in websocket.iter_text():
            try:
                message_data = json.loads(message)

                user_message = message_data.get("message", "")
                conversation_history = message_data.get("conversation_history", [])
                
                if not user_message:
                    await ai_websocket_manager.send_error(connection_id, "No message provided")
                    continue

                async def websocket_callback(step: str, details: str):
                    """Callback function to send real-time updates via WebSocket."""
                    try:
                        await ai_websocket_manager.send_thinking_step(connection_id, step, details)
                    except Exception as e:
                        logger.error(f"Error in websocket callback: {e}")

                existing_context = ai_websocket_manager.get_context(connection_id)
                
                if not existing_context:
                    await ai_websocket_manager.send_error(connection_id, "Connection context not found")
                    continue

                # Use orchestrator directly - no service wrapper needed!
                response = await orchestrator.process_user_message(
                    user_message=user_message,
                    conversation_history=conversation_history,
                    websocket_callback=websocket_callback,
                    connection_id=connection_id,
                    existing_context=existing_context
                )
                await ai_websocket_manager.send_response(connection_id, response)
                # No need to handle response or context updates - orchestrator handles everything

            except json.JSONDecodeError as e:
                await ai_websocket_manager.send_error(connection_id, "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error handling AI message: {e}")
                try:
                    await ai_websocket_manager.send_error(connection_id, f"Internal server error: {str(e)}")
                except:
                    break
                
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