#!/usr/bin/env python3
"""
Conversation Manager - Handles conversation history and context
"""

from typing import Dict, List
from datetime import datetime

class ConversationManager:
    def __init__(self, max_history: int = 10):
        """Initialize conversation storage"""
        self.conversations = {}
        self.max_history = max_history
    
    def add_exchange(self, session_id: str, user_message: str, bot_response: str):
        """Add a conversation exchange"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            'user': user_message,
            'assistant': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last N exchanges
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history:]
    
    def get_context(self, session_id: str, max_turns: int = 3) -> List[Dict]:
        """Get recent conversation context"""
        if session_id not in self.conversations:
            return []
        
        return self.conversations[session_id][-max_turns:]
    
    def clear_session(self, session_id: str):
        """Clear a session's history"""
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self.conversations)

