#!/usr/bin/env python3
"""Enhanced Query Classifier - FIXED with better support/accessory detection"""

class EnhancedQueryClassifier:
    def __init__(self):
        self.product_keywords = [
            'v5', 'core', 'ruby', 'twist', 'controller', 'nice dreamz',
            'dreamz', 'fogger', 'lightning', 'pen', 'cub', 'hubble',
            'bubble', 'glass', 'mod', 'pico', 'rim', 'titanium', 'carb',
            'heater', 'coil', 'recycler', 'hydratube', 'sic', 'wireless'
        ]
        
        # IMPROVED: More support keywords
        self.support_keywords = [
            'return', 'warranty', 'broken', 'defective', 'leaking', 'charge',
            'error', 'clean', 'setup', 'troubleshoot', 'fix', 'replace',
            'damaged', 'refund', 'arrived', 'wrong', 'missing', 'help',
            "won't", 'not working', 'broken', 'issue', 'problem'
        ]
        
        self.tech_keywords = [
            'temp', 'tcr', 'wattage', 'ohm', 'firmware', 'autofire', 'session',
            'boost', 'rebuild', 'compatibility', 'settings', 'resistance',
            'lock', 'arctic fox'
        ]
        
        self.shopping_keywords = [
            'price', 'sale', 'discount', 'shipping', 'stock', 'bundle', 'buy'
        ]
        
        # NEW: Accessory-specific keywords
        self.accessory_keywords = [
            'battery', 'batteries', '510 cable', '510 extension', 'adapter',
            'charger', 'case', 'jar', 'container'
        ]
        
        # NEW: Recommendation keywords
        self.recommendation_keywords = [
            'recommend', 'should i buy', 'best', 'beginner', 'new', 'first time',
            'starter', 'easiest', 'portable', 'flavor', 'which', 'what should'
        ]
    
    def classify(self, query: str, has_history: bool = False):
        query_lower = query.lower()
        
        # Check for recommendations FIRST (before product search)
        if any(kw in query_lower for kw in self.recommendation_keywords):
            return {'intent': 'shopping', 'confidence': 0.9}
        
        # Support keywords - HIGHER PRIORITY
        if any(kw in query_lower for kw in self.support_keywords):
            return {'intent': 'support', 'confidence': 0.95}
        
        # Accessory queries
        if any(kw in query_lower for kw in self.accessory_keywords):
            return {'intent': 'product_info', 'confidence': 0.85}
        
        # Tech specs
        if any(kw in query_lower for kw in self.tech_keywords):
            if any(word in query_lower for word in ['vs', 'compare', 'difference']):
                return {'intent': 'comparison', 'confidence': 0.9}
            return {'intent': 'tech_specs', 'confidence': 0.9}
        
        # Shopping
        if any(kw in query_lower for kw in self.shopping_keywords):
            return {'intent': 'shopping', 'confidence': 0.85}
        
        # Products
        for keyword in self.product_keywords:
            if keyword in query_lower:
                if any(word in query_lower for word in ['vs', 'compare', 'difference']):
                    return {'intent': 'comparison', 'confidence': 0.9}
                if 'how much' in query_lower or 'price' in query_lower:
                    return {'intent': 'pricing', 'confidence': 0.9}
                return {'intent': 'product_info', 'confidence': 0.9}
        
        # Greetings
        if query_lower in ['hi', 'hello', 'hey', 'sup', 'yo', 'thanks', 'thank you']:
            return {'intent': 'greeting', 'confidence': 0.95}
        
        # Follow-up
        if has_history and any(word in query_lower for word in ['it', 'that', 'this', 'one']):
            return {'intent': 'follow_up', 'confidence': 0.75}
        
        return {'intent': 'general', 'confidence': 0.5}
