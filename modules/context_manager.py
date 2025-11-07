#!/usr/bin/env python3
"""
context_manager.py - Intelligent conversation context tracking
Remembers what products were discussed, user preferences, and conversation flow
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import deque


class ContextManager:
    """
    Manages conversation context for better RAG retrieval.
    
    Tracks:
    - Products mentioned in conversation
    - User's stated preferences (flavor, portability, etc.)
    - Last query intent
    - Conversation flow (are they comparing? troubleshooting?)
    - Follow-up context (when user says "it" or "that one")
    """
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.sessions = {}  # session_id -> session context
    
    def get_or_create_session(self, session_id: str) -> Dict:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'history': deque(maxlen=self.max_history),
                'mentioned_products': set(),
                'last_products': [],  # Last products shown/discussed
                'user_preferences': {},
                'conversation_state': 'initial',  # initial, browsing, comparing, troubleshooting
                'last_category': None,
                'last_intent': None,
                'follow_up_context': None,
                'created_at': datetime.now(),
                'last_updated': datetime.now()
            }
        
        return self.sessions[session_id]
    
    def add_exchange(
        self,
        session_id: str,
        user_query: str,
        bot_response: str,
        products_shown: List[Dict] = None,
        intent: str = None,
        extracted_info: Dict = None
    ):
        """
        Add a conversation exchange and update context.
        
        Args:
            session_id: Unique session identifier
            user_query: User's query
            bot_response: Bot's response
            products_shown: List of products shown to user
            intent: Classified intent of the query
            extracted_info: Any additional extracted information
        """
        session = self.get_or_create_session(session_id)
        
        # Add to history
        exchange = {
            'timestamp': datetime.now(),
            'user_query': user_query,
            'bot_response': bot_response,
            'products_shown': products_shown or [],
            'intent': intent,
            'extracted_info': extracted_info or {}
        }
        session['history'].append(exchange)
        
        # Update context
        if products_shown:
            session['last_products'] = products_shown
            
            # Track mentioned products (FIXED: handle missing IDs)
            for product in products_shown:
                # Use ID if available, otherwise use name as fallback
                product_id = product.get('id', product.get('name', 'unknown'))
                session['mentioned_products'].add(product_id)
            
            # Update last category
            if products_shown:
                session['last_category'] = products_shown[0].get('category')
        
        # Update intent
        if intent:
            session['last_intent'] = intent
            
            # Update conversation state based on intent
            if intent == 'comparison':
                session['conversation_state'] = 'comparing'
            elif intent == 'support':
                session['conversation_state'] = 'troubleshooting'
            elif intent in ['product_info', 'shopping']:
                session['conversation_state'] = 'browsing'
        
        # Extract user preferences from query
        preferences = self._extract_preferences(user_query)
        if preferences:
            session['user_preferences'].update(preferences)
        
        # Update follow-up context
        session['follow_up_context'] = self._build_follow_up_context(session)
        
        # Update timestamp
        session['last_updated'] = datetime.now()
    
    def _extract_preferences(self, query: str) -> Dict[str, Any]:
        """
        Extract user preferences from query.
        
        Examples:
        - "best for flavor" → {'priority': 'flavor'}
        - "beginner friendly" → {'experience_level': 'beginner'}
        - "portable" → {'form_factor': 'portable'}
        """
        query_lower = query.lower()
        preferences = {}
        
        # Experience level
        if any(w in query_lower for w in ['beginner', 'new', 'first time', 'starter']):
            preferences['experience_level'] = 'beginner'
        elif any(w in query_lower for w in ['advanced', 'experienced', 'expert']):
            preferences['experience_level'] = 'advanced'
        
        # Form factor
        if any(w in query_lower for w in ['portable', 'travel', 'compact', 'small']):
            preferences['form_factor'] = 'portable'
        elif any(w in query_lower for w in ['desktop', 'home', 'stationary']):
            preferences['form_factor'] = 'desktop'
        
        # Priority features
        if any(w in query_lower for w in ['flavor', 'taste', 'terp']):
            preferences['priority'] = 'flavor'
        elif any(w in query_lower for w in ['powerful', 'strong', 'potent']):
            preferences['priority'] = 'power'
        elif any(w in query_lower for w in ['easy', 'simple', 'convenient']):
            preferences['priority'] = 'ease_of_use'
        elif any(w in query_lower for w in ['cheap', 'affordable', 'budget']):
            preferences['priority'] = 'price'
        
        # Material preference
        if any(w in query_lower for w in ['dry herb', 'flower', 'bud']):
            preferences['material'] = 'dry_herb'
        elif any(w in query_lower for w in ['concentrate', 'wax', 'dab', 'oil']):
            preferences['material'] = 'concentrate'
        
        return preferences
    
    def _build_follow_up_context(self, session: Dict) -> Optional[Dict]:
        """
        Build context for follow-up questions.
        
        When user says "tell me more about it" or "what about that one",
        we need to know what "it" refers to.
        """
        if not session['last_products']:
            return None
        
        return {
            'referent_products': session['last_products'],
            'referent_category': session['last_category'],
            'can_use_pronouns': True  # User can say "it", "that", "this"
        }
    
    def resolve_follow_up(self, session_id: str, query: str) -> Optional[Dict]:
        """
        Resolve follow-up references like "it", "that one", "what about this".
        Also detects when user is ANSWERING a question.
        
        Returns:
            Context dict with resolved references, or None if not a follow-up
        """
        session = self.get_or_create_session(session_id)
        query_lower = query.lower().strip()
        
        # Check if this is a follow-up query (pronoun references)
        follow_up_indicators = [
            'it', 'that', 'this', 'them', 'those', 'these',
            'what about', 'tell me more', 'how about',
            'the one', 'that one', 'this one'
        ]
        
        is_follow_up = any(indicator in query_lower for indicator in follow_up_indicators)
        
        # Check if this is an ANSWER to a previous question
        is_answer = self._is_answering_question(session, query_lower)
        
        if not is_follow_up and not is_answer:
            return None
        
        # Return follow-up context if available
        context = session.get('follow_up_context')
        
        # Add answer flag if detected
        if is_answer and context:
            context['is_answer'] = True
            context['answer_text'] = query
        
        return context
    
    def _is_answering_question(self, session: Dict, query: str) -> bool:
        """
        Detect if user is answering a question from the bot.
        
        Examples:
        Bot: "Do you use dry herb or concentrates?"
        User: "concentrates" ← This is an answer!
        """
        # Check last exchange
        if not session['history']:
            return False
        
        last_exchange = list(session['history'])[-1]
        last_bot_response = last_exchange.get('bot_response', '').lower()
        
        # Check if last bot message was a question
        if '?' not in last_bot_response:
            return False
        
        # Common answer patterns
        answer_patterns = [
            'concentrates', 'concentrate', 'wax', 'dabs', 'dry herb', 'herb', 'flower',
            'beginner', 'advanced', 'yes', 'no', 'yeah', 'nope',
            'flavor', 'power', 'portability', 'portable', 'handheld', 'desktop'
        ]
        
        # Single word/phrase answers are often responses
        return len(query.split()) <= 2 and any(pattern in query for pattern in answer_patterns)
    
    
    def get_conversation_summary(self, session_id: str) -> Dict:
        """
        Get a summary of the conversation so far.
        Useful for providing to LLM as context.
        """
        session = self.get_or_create_session(session_id)
        
        return {
            'total_exchanges': len(session['history']),
            'conversation_state': session['conversation_state'],
            'last_intent': session['last_intent'],
            'last_category': session['last_category'],
            'mentioned_products': list(session['mentioned_products']),
            'user_preferences': session['user_preferences'],
            'last_products': [p.get('name', 'Unknown') for p in session['last_products'][:3]]
        }
    
    def get_retrieval_context(self, session_id: str) -> Dict:
        """
        Get context specifically for RAG retrieval.
        This helps the retriever boost relevant products.
        """
        session = self.get_or_create_session(session_id)
        
        return {
            'last_category': session['last_category'],
            'conversation_state': session['conversation_state'],
            'user_preferences': session['user_preferences'],
            'mentioned_product_ids': list(session['mentioned_products'])
        }
    
    def should_show_comparison(self, session_id: str) -> bool:
        """
        Determine if user is likely comparing products.
        Useful for deciding whether to show multiple products vs. single product.
        """
        session = self.get_or_create_session(session_id)
        
        # Check last few queries for comparison indicators
        recent_queries = [ex['user_query'].lower() for ex in list(session['history'])[-3:]]
        
        comparison_indicators = ['vs', 'versus', 'compare', 'difference', 'better', 'which']
        
        return any(
            any(indicator in query for indicator in comparison_indicators)
            for query in recent_queries
        )
    
    def get_context_for_llm(self, session_id: str, max_exchanges: int = 3) -> str:
        """
        Format conversation context as text for LLM.
        Returns a concise summary of recent conversation.
        """
        session = self.get_or_create_session(session_id)
        
        if not session['history']:
            return "This is the start of the conversation."
        
        # Get recent exchanges
        recent = list(session['history'])[-max_exchanges:]
        
        context_parts = []
        
        # Add conversation summary
        if session['user_preferences']:
            prefs = session['user_preferences']
            context_parts.append(f"User preferences: {', '.join(f'{k}={v}' for k, v in prefs.items())}")
        
        # Add recent exchanges
        context_parts.append("\nRecent conversation:")
        for i, ex in enumerate(recent, 1):
            context_parts.append(f"User: {ex['user_query']}")
            if ex['products_shown']:
                products = ', '.join(p.get('name', 'Unknown')[:30] for p in ex['products_shown'][:2])
                context_parts.append(f"Bot showed: {products}")
        
        return '\n'.join(context_parts)
    
    def clear_session(self, session_id: str):
        """Clear a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def clear_old_sessions(self, hours: int = 24):
        """Clear sessions older than specified hours"""
        from datetime import timedelta
        
        now = datetime.now()
        cutoff = now - timedelta(hours=hours)
        
        old_sessions = [
            sid for sid, session in self.sessions.items()
            if session['last_updated'] < cutoff
        ]
        
        for sid in old_sessions:
            del self.sessions[sid]
        
        if old_sessions:
            print(f"🗑️  Cleared {len(old_sessions)} old sessions")


# Convenience testing
def test_context_manager():
    """Test the context manager"""
    print("\n" + "="*70)
    print("CONTEXT MANAGER TEST")
    print("="*70 + "\n")
    
    cm = ContextManager()
    session_id = "test_session"
    
    # Simulate conversation
    exchanges = [
        {
            'query': "what's best for flavor?",
            'products': [{'id': 'prod_1', 'name': 'V5 XL', 'category': 'main_products'}],
            'intent': 'shopping'
        },
        {
            'query': "tell me more about it",
            'products': [{'id': 'prod_1', 'name': 'V5 XL', 'category': 'main_products'}],
            'intent': 'product_info'
        },
        {
            'query': "what about for beginners?",
            'products': [{'id': 'prod_2', 'name': 'Core Deluxe', 'category': 'main_products'}],
            'intent': 'shopping'
        }
    ]
    
    for ex in exchanges:
        cm.add_exchange(
            session_id,
            ex['query'],
            "Bot response here",
            ex['products'],
            ex['intent']
        )
    
    # Test features
    print("Conversation Summary:")
    summary = cm.get_conversation_summary(session_id)
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\nContext for LLM:")
    print(cm.get_context_for_llm(session_id))
    
    print("\nRetrieval Context:")
    print(cm.get_retrieval_context(session_id))
    
    # Test follow-up resolution
    follow_up = cm.resolve_follow_up(session_id, "tell me more about it")
    print(f"\nFollow-up resolved: {follow_up is not None}")


if __name__ == "__main__":
    test_context_manager()
