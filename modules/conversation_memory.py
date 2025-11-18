#!/usr/bin/env python3
"""
conversation_memory.py - Tracks conversation history per session
CLEANED: Better memory management, cleaner API
"""

from typing import Dict, List, Optional
from datetime import datetime
from collections import deque


class ConversationMemory:
    """
    Maintains conversation history for multi-turn conversations
    Keeps track of recent exchanges per session
    """
    
    def __init__(self, max_history: int = 5):
        """
        Initialize conversation memory
        
        Args:
            max_history: Maximum number of exchanges to keep per session
        """
        self.max_history = max_history
        self.sessions = {}  # session_id -> deque of exchanges
        print(f"✓ Conversation Memory initialized (max {max_history} exchanges per session)")
    
    def add_exchange(
        self,
        session_id: str,
        user_message: str,
        bot_response: str,
        intent: str = None,
        products_shown: List[Dict] = None
    ):
        """Add a conversation exchange to memory"""
        # Create session if doesn't exist
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=self.max_history)
        
        # Create exchange record
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'bot': bot_response,
            'intent': intent,
            'products': [p.get('name') for p in (products_shown or [])]
        }
        
        # Add to session history
        self.sessions[session_id].append(exchange)
    
    def get_history(self, session_id: str, max_turns: int = None) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session to retrieve
            max_turns: Maximum number of turns to return (default: all)
        
        Returns:
            List of exchange dictionaries
        """
        if session_id not in self.sessions:
            return []
        
        history = list(self.sessions[session_id])
        
        if max_turns:
            return history[-max_turns:]
        
        return history
    
    def get_context_string(self, session_id: str, max_turns: int = 3) -> str:
        """
        Get formatted context string for LLM prompt
        
        Args:
            session_id: Session to retrieve
            max_turns: Maximum number of recent turns to include
        
        Returns:
            Formatted string with conversation history
        """
        history = self.get_history(session_id, max_turns)
        
        if not history:
            return ""
        
        context = "=== RECENT CONVERSATION ===\n\n"
        
        for i, exchange in enumerate(history, 1):
            context += f"Turn {i}:\n"
            context += f"User: {exchange['user']}\n"
            
            # Truncate long bot responses
            bot_text = exchange['bot']
            if len(bot_text) > 200:
                bot_text = bot_text[:200] + "..."
            context += f"Assistant: {bot_text}\n"
            
            if exchange.get('intent'):
                context += f"(Intent: {exchange['intent']})\n"
            
            context += "\n"
        
        context += "=== END CONVERSATION ===\n"
        return context
    
    def has_mentioned_product(self, session_id: str, product_name: str) -> bool:
        """
        Check if a specific product was mentioned in this session
        
        Args:
            session_id: Session to check
            product_name: Product name to search for
        
        Returns:
            True if product was mentioned
        """
        history = self.get_history(session_id)
        product_lower = product_name.lower()
        
        for exchange in history:
            # Check in products shown
            if any(product_lower in p.lower() for p in exchange.get('products', [])):
                return True
            
            # Check in user message
            if product_lower in exchange['user'].lower():
                return True
            
            # Check in bot response
            if product_lower in exchange['bot'].lower():
                return True
        
        return False
    
    def get_last_intent(self, session_id: str) -> Optional[str]:
        """Get the intent from the last exchange"""
        history = self.get_history(session_id, max_turns=1)
        
        if history:
            return history[0].get('intent')
        
        return None
    
    def get_last_user_message(self, session_id: str) -> Optional[str]:
        """Get the last user message"""
        history = self.get_history(session_id, max_turns=1)
        
        if history:
            return history[0].get('user')
        
        return None
    
    def get_last_products(self, session_id: str) -> List[str]:
        """Get products from last exchange"""
        history = self.get_history(session_id, max_turns=1)
        
        if history:
            return history[0].get('products', [])
        
        return []
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            print(f"🗑️  Cleared session: {session_id}")
    
    def get_active_sessions(self) -> int:
        """Get number of active sessions"""
        return len(self.sessions)
    
    def get_session_summary(self, session_id: str) -> Dict:
        """
        Get summary statistics for a session
        
        Returns:
            Dictionary with session stats
        """
        if session_id not in self.sessions:
            return {
                'exists': False,
                'exchanges': 0,
                'intents': [],
                'products_mentioned': []
            }
        
        history = self.get_history(session_id)
        
        intents = [ex.get('intent') for ex in history if ex.get('intent')]
        products = []
        for ex in history:
            products.extend(ex.get('products', []))
        
        return {
            'exists': True,
            'exchanges': len(history),
            'intents': intents,
            'products_mentioned': list(set(products)),
            'first_exchange': history[0]['timestamp'] if history else None,
            'last_exchange': history[-1]['timestamp'] if history else None
        }
    
    def detect_follow_up(self, session_id: str, current_query: str) -> bool:
        """
        Detect if current query is a follow-up question
        
        Args:
            session_id: Session to check
            current_query: Current user query
        
        Returns:
            True if this appears to be a follow-up
        """
        query_lower = current_query.lower().strip()
        
        # Follow-up indicators
        follow_up_words = [
            'it', 'that', 'this', 'those', 'them', 'the same', 'same one',
            'what about', 'also', 'and', 'too', 'as well',
            'yes', 'no', 'yeah', 'nah', 'yep', 'nope',
            'ok', 'okay', 'thanks', 'got it', 'i see'
        ]
        
        # Check if query starts with follow-up words
        starts_with_followup = any(query_lower.startswith(word) for word in follow_up_words)
        
        # Check if query is very short (likely referring to previous context)
        is_short = len(query_lower.split()) <= 3
        
        # Check if there's recent history
        has_history = len(self.get_history(session_id, max_turns=1)) > 0
        
        return has_history and (starts_with_followup or is_short)
    
    def get_context_products(self, session_id: str) -> List[str]:
        """Get list of all products mentioned in this session"""
        history = self.get_history(session_id)
        products = set()
        
        for exchange in history:
            products.update(exchange.get('products', []))
        
        return list(products)
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        total_exchanges = sum(len(self.sessions[sid]) for sid in self.sessions)
        
        return {
            'active_sessions': len(self.sessions),
            'total_exchanges': total_exchanges,
            'max_history_per_session': self.max_history
        }
    
    def cleanup_old_sessions(self, max_sessions: int = 100):
        """
        Keep only the most recent sessions
        Useful for preventing memory bloat
        """
        if len(self.sessions) <= max_sessions:
            return 0
        
        # Get sessions sorted by last update (newest first)
        sessions_by_time = []
        for sid, history in self.sessions.items():
            if history:
                last_time = history[-1]['timestamp']
                sessions_by_time.append((sid, last_time))
        
        sessions_by_time.sort(key=lambda x: x[1], reverse=True)
        
        # Keep only the newest max_sessions
        sessions_to_keep = set(sid for sid, _ in sessions_by_time[:max_sessions])
        
        # Delete old sessions
        deleted = 0
        for sid in list(self.sessions.keys()):
            if sid not in sessions_to_keep:
                del self.sessions[sid]
                deleted += 1
        
        if deleted > 0:
            print(f"🗑️  Cleaned up {deleted} old sessions")
        
        return deleted


def test_conversation_memory():
    """Test conversation memory"""
    print("\n" + "="*70)
    print("CONVERSATION MEMORY TEST")
    print("="*70 + "\n")
    
    memory = ConversationMemory(max_history=3)
    session_id = "test_session"
    
    # Add some exchanges
    exchanges = [
        ("what's the best vape for beginners", "I recommend the Core XL Deluxe", "recommendation"),
        ("tell me more about it", "The Core XL Deluxe is an all-in-one eRig", "product_info"),
        ("what about the v5", "The V5 is a rebuildable atomizer", "product_info"),
        ("how much is it", "The V5 is $XX", "pricing")
    ]
    
    for user, bot, intent in exchanges:
        memory.add_exchange(session_id, user, bot, intent)
    
    # Test history
    print("Full History:")
    history = memory.get_history(session_id)
    for i, ex in enumerate(history, 1):
        print(f"  {i}. User: {ex['user'][:40]}...")
        print(f"     Bot: {ex['bot'][:40]}...")
    
    # Test context string
    print("\nContext String:")
    context = memory.get_context_string(session_id, max_turns=2)
    print(context[:200] + "...")
    
    # Test summary
    print("\nSession Summary:")
    summary = memory.get_session_summary(session_id)
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Test follow-up detection
    print("\nFollow-up Detection:")
    test_queries = ["tell me more", "what about the price", "a new vaporizer for flower"]
    for query in test_queries:
        is_followup = memory.detect_follow_up(session_id, query)
        print(f"  '{query}': {'YES' if is_followup else 'NO'}")
    
    # Test stats
    print("\nMemory Stats:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    test_conversation_memory()
