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
                for chat in context.user_chats:
                    if isinstance(chat, dict):
                        formatted_history.append({
                            'role': chat.get('role', 'unknown'),
                            'msg': chat.get('text', chat.get('msg', ''))
                        })
                print(f"🔍 Extracted {len(formatted_history)} messages from conversation history")
                return formatted_history
            print(f"🔍 No user_chats found in context")
            return []
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    def format_conversation_history(self, history: List[Dict[str, str]]) -> Optional[str]:
        """Format conversation history for prompt."""
        if not history:
            return None
        
        formatted = ["=== Conversation History ==="]
        formatted.append(f"--------------------------------")
        for i, entry in enumerate(history):
            if isinstance(entry, dict):
                role = entry.get('role', 'unknown')
                msg = entry.get('msg', entry.get('text', ''))
                if msg:
                    formatted.append(f"{role.capitalize()}: \"{msg}\"")
        
        if len(formatted) == 1:  # Only header
            formatted.append("No messages in conversation history")
        formatted.append(f"--------------------------------")
        
        return "\n".join(formatted) 