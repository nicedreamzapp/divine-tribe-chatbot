#!/usr/bin/env python3
"""Enhanced Query Classifier - Fixed"""

class EnhancedQueryClassifier:
    def __init__(self):
        self.product_keywords = [
            'v5', 'core', 'ruby', 'twist', 'controller', 'nice dreamz', 
            'dreamz', 'fogger', 'lightning', 'pen', 'cub', 'hubble', 
            'bubble', 'glass', 'mod', 'pico', 'rim'
        ]
    
    def classify(self, query: str, has_history: bool = False):
        query_lower = query.lower()
        
        # Check for products FIRST
        for keyword in self.product_keywords:
            if keyword in query_lower:
                if 'how much' in query_lower or 'price' in query_lower:
                    return {'intent': 'pricing', 'confidence': 0.9}
                return {'intent': 'product_info', 'confidence': 0.9}
        
        # Then check greetings
        if query_lower in ['hi', 'hello', 'hey', 'sup', 'yo']:
            return {'intent': 'greeting', 'confidence': 0.95}
        
        # Shopping intent
        if any(word in query_lower for word in ['need', 'want', 'looking for', 'show me', 'buy']):
            return {'intent': 'shopping', 'confidence': 0.85}
        
        # Support
        if any(word in query_lower for word in ['help', 'broken', 'issue', 'problem', 'support']):
            return {'intent': 'support', 'confidence': 0.8}
        
        # Follow-up
        if has_history and any(word in query_lower for word in ['it', 'that', 'this', 'one']):
            return {'intent': 'follow_up', 'confidence': 0.75}
        
        return {'intent': 'general', 'confidence': 0.5}
