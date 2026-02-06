"""
Context Connection Manager
Manages WebSocket connections and session IDs.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConnectionInfo:
    """Connection information for a WebSocket connection."""
    connection_id: str
    session_id: str
    connected_at: datetime
    last_activity: datetime

class ContextConnectionManager:
    """Manages WebSocket connections and session IDs."""
    
    def __init__(self):
        """Initialize the connection manager."""
        self.connections: Dict[str, ConnectionInfo] = {}
        # Store actual context objects for each connection
        self.contexts: Dict[str, Any] = {}
    
    def create_connection(self, connection_id: str = None) -> ConnectionInfo:
        """Create a new connection with a unique session ID."""
        if not connection_id:
            connection_id = str(uuid.uuid4())
        
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        connection_info = ConnectionInfo(
            connection_id=connection_id,
            session_id=session_id,
            connected_at=now,
            last_activity=now
        )
        
        # Store connection
        self.connections[connection_id] = connection_info
        
        logger.info(f"Created connection: {connection_id} with session: {session_id}")
        return connection_info
    
    def get_connection(self, connection_id: str) -> Optional[ConnectionInfo]:
        """Get connection information by connection ID."""
        return self.connections.get(connection_id)
    
    def update_activity(self, connection_id: str) -> bool:
        """Update last activity timestamp for a connection."""
        if connection_id in self.connections:
            self.connections[connection_id].last_activity = datetime.now()
            return True
        return False
    
    def disconnect_connection(self, connection_id: str) -> bool:
        """Disconnect a connection and clean up resources."""
        if connection_id not in self.connections:
            return False
        
        # Clean up both connection info and context
        del self.connections[connection_id]
        if connection_id in self.contexts:
            del self.contexts[connection_id]
        
        logger.info(f"Disconnected connection: {connection_id}")
        return True
    
    def get_context(self, connection_id: str, existing_context: Any = None) -> Any:
        """Get or create context for a connection."""
        connection_info = self.get_connection(connection_id)
        if not connection_info:
            # Create new connection if it doesn't exist
            connection_info = self.create_connection(connection_id)
        
        # Update activity
        self.update_activity(connection_id)
        
        # If existing context is provided, store it and return it
        if existing_context:
            logger.info(f"Storing provided existing context for connection: {connection_id}")
            self.contexts[connection_id] = existing_context
            return existing_context
        
        # Check if we have a stored context for this connection
        if connection_id in self.contexts:
            stored_context = self.contexts[connection_id]
            logger.info(f"Retrieved existing context for connection: {connection_id} with {len(getattr(stored_context, 'user_chats', []))} messages")
            return stored_context
        
        # Create basic context if none exists
        basic_context = self._create_basic_context(connection_id, connection_info.session_id)
        self.contexts[connection_id] = basic_context
        logger.info(f"Created new basic context for connection: {connection_id}")
        return basic_context
    
    def _create_basic_context(self, connection_id: str, session_id: str) -> Any:
        """Create a basic context object."""
        class BasicContext:
            def __init__(self):
                self.connection_id = connection_id
                self.session_id = session_id
                self.user_chats = []  # Always a list
                self.collected_variables = {}  # Always a dict
                self.missing_variables = []  # Always a list
                self.current_intent = 'unknown'
                self.created_at = datetime.now().isoformat()
                self.last_updated = datetime.now().isoformat()
            
            def to_dict(self):
                """Convert context to dictionary for JSON serialization."""
                return {
                    'connection_id': self.connection_id,
                    'session_id': self.session_id,
                    'user_chats': self.user_chats,
                    'collected_variables': self.collected_variables,
                    'missing_variables': self.missing_variables,
                    'current_intent': getattr(self, 'current_intent', 'unknown'),
                    'created_at': self.created_at,
                    'last_updated': self.last_updated
                }
            
            def __setattr__(self, name, value):
                """Override setattr to ensure data type consistency."""
                if name == 'user_chats' and not isinstance(value, list):
                    logger.warning(f"Attempted to set user_chats to non-list type: {type(value)}, converting to list")
                    if isinstance(value, dict):
                        value = [value]  # Convert dict to list with one item
                    elif value is None:
                        value = []
                    else:
                        value = [value]  # Convert other types to list
                elif name == 'collected_variables' and not isinstance(value, dict):
                    logger.warning(f"Attempted to set collected_variables to non-dict type: {type(value)}, converting to dict")
                    value = {} if value is None else dict(value) if hasattr(value, 'items') else {}
                elif name == 'missing_variables' and not isinstance(value, list):
                    logger.warning(f"Attempted to set missing_variables to non-list type: {type(value)}, converting to list")
                    value = [] if value is None else list(value) if hasattr(value, '__iter__') else [value]
                
                super().__setattr__(name, value)
        
        return BasicContext()
    
    def store_context(self, connection_id: str, context: Any) -> None:
        """Store a context object for a connection."""
        self.contexts[connection_id] = context
        logger.info(f"Stored context for connection: {connection_id} with {len(getattr(context, 'user_chats', []))} messages")
    
    def get_stored_context(self, connection_id: str) -> Optional[Any]:
        """Get a stored context object for a connection."""
        return self.contexts.get(connection_id) 