"""
Conversation Utilities
Handles conversation history functionality.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConversationUtils:
    """Utility class for handling conversation history."""
    
    def get_conversation_history(self, context: Any) -> List[Dict[str, str]]:
        """Get conversation history from context."""
        try:
            if hasattr(context, 'user_chats') and context.user_chats:
                # Ensure proper format with 'role' and 'msg' keys
                formatted_history = []
                
                # Handle different data types gracefully
                if isinstance(context.user_chats, list):
                    for chat in context.user_chats:
                        if isinstance(chat, dict):
                            # Ensure we have both role and msg
                            role = chat.get('role', 'unknown')
                            msg = chat.get('msg', '')
                            
                            # Skip empty messages
                            if msg and msg.strip():
                                formatted_history.append({
                                    'role': role,
                                    'msg': msg.strip()
                                })
                        elif isinstance(chat, str):
                            # Handle case where chat might be a string
                            logger.warning(f"Found string chat entry: {chat}")
                            formatted_history.append({
                                'role': 'unknown',
                                'msg': chat
                            })
                        else:
                            logger.warning(f"Unexpected chat entry type: {type(chat)}, content: {chat}")
                elif isinstance(context.user_chats, dict):
                    # Handle case where user_chats might be a dict
                    logger.warning(f"user_chats is a dict instead of list: {context.user_chats}")
                    return []
                else:
                    logger.warning(f"Unexpected user_chats type: {type(context.user_chats)}")
                    return []
                
                logger.info(f"Extracted {len(formatted_history)} messages from conversation history")
                return formatted_history
            else:
                logger.info("No user_chats found in context or user_chats is empty")
                return []
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            logger.error(f"Context type: {type(context)}")
            logger.error(f"Context has user_chats: {hasattr(context, 'user_chats')}")
            if hasattr(context, 'user_chats'):
                logger.error(f"user_chats type: {type(context.user_chats)}")
                logger.error(f"user_chats content: {context.user_chats}")
            return []
    
    def format_conversation_history(self, history: List[Dict[str, str]]) -> Optional[str]:
        """Format conversation history for prompt."""
        
        if not history:
            return ""
        
        formatted = ["* With respect to this conversation: * "]
        
        for i, entry in enumerate(history.slice(0, -1)):
            if isinstance(entry, dict):
                role = entry.get('role', 'unknown')
                role = 'user' if role == 'user' else 'ai_response'
                msg = entry.get('msg', '')
                formatted.append(f"{role.upper()}: \"{msg}\"")
        # Simple repetition warning
        formatted.append(f"\n** REPLY TO THE MESSAGE: **\n\n")
        for i, entry in enumerate(history.slice(-1)):
            if isinstance(entry, dict):
                msg = entry.get('msg', '')
                formatted.append(f"USER: \"{msg}\"\n\n")
                
        return "\n".join(formatted) 