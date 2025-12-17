#!/usr/bin/env python3
"""
Query preprocessor - extracts intent signals from raw queries
"""
from typing import Dict, List
import re

class QueryPreprocessor:
    def __init__(self):
        # Material type keywords
        self.concentrate_keywords = [
            'wax', 'concentrate', 'dabs', 'dab', 'oil', 'shatter', 'budder',
            'rosin', 'sauce', 'crumble', 'distillate', 'live resin', 'hash oil'
        ]
        
        self.dry_herb_keywords = [
            'flower', 'dry herb', 'herb', 'bud', 'nugs'
        ]
        
        # Hemp/Clothing keywords - NEW!
        self.hemp_keywords = [
            'hemp', 'shirt', 'clothing', 'clothes', 'hoodie', 'boxer',
            'apparel', 'tank', 't-shirt', 'tshirt'
        ]
        
        # Intent hint keywords
        self.comparison_words = ['vs', 'versus', 'compare', 'difference between', 'better than']
        self.shopping_words = ['buy', 'purchase', 'recommend', 'best', 'top', 'which']
        self.troubleshooting_words = [
            'broken', 'not working', 'problem', 'issue', 'fix', 'help',
            'won\'t', 'wont', 'can\'t', 'cant', 'doesn\'t', 'doesnt',
            'error', 'wrong', 'bad'
        ]
        self.how_to_words = ['how to', 'how do', 'setup', 'install', 'use', 'clean']
        
        # Product name patterns
        self.product_patterns = {
            'v5': ['v5', 'v 5', 'version 5', 'divine crossing v5'],
            'v5_xl': ['v5 xl', 'v5xl', 'xl v5', 'v5 extra large'],
            'core': ['core', 'core 2.0', 'core deluxe'],
            'tug': ['tug', 'tug 2.0', 'tug deluxe'],
            'lightning': ['lightning pen', 'lightning'],
            'fogger': ['fogger', 'nice dreamz', 'nicedreamz'],
            'ruby': ['ruby', 'ruby twist', 'ball vape'],
            'gen2': ['gen 2', 'gen2', 'generation 2']
        }
    
    def process(self, query: str) -> Dict:
        """
        Process query and extract all useful signals.
        Returns a dict with normalized query + metadata.
        """
        query_lower = query.lower().strip()
        
        result = {
            'original': query,
            'cleaned': query_lower,
            'url': self._extract_url(query),
            'product_mention': self._detect_product(query_lower),
            'material_type': self._detect_material(query_lower),
            'category_filter': self._detect_category(query_lower),  # NEW!
            'intent_hints': self._extract_intent_hints(query_lower)
        }
        
        return result
    
    def _extract_url(self, query: str) -> str:
        """Extract ineedhemp.com URL if present"""
        url_pattern = r'https?://(?:www\.)?ineedhemp\.com/[^\s]+'
        match = re.search(url_pattern, query)
        return match.group(0) if match else None
    
    def _detect_product(self, query: str) -> str:
        """Detect which product is mentioned"""
        for product, patterns in self.product_patterns.items():
            if any(pattern in query for pattern in patterns):
                return product
        return None
    
    def _detect_material(self, query: str) -> str:
        """Detect if query is about concentrates or dry herb"""
        has_concentrate = any(kw in query for kw in self.concentrate_keywords)
        has_dry_herb = any(kw in query for kw in self.dry_herb_keywords)
        
        if has_concentrate and has_dry_herb:
            return 'both'
        elif has_concentrate:
            return 'concentrate'
        elif has_dry_herb:
            return 'dry_herb'
        return None
    
    def _detect_category(self, query: str) -> str:
        """NEW: Detect if query should filter to specific category"""
        # Hemp/clothing queries
        if any(kw in query for kw in self.hemp_keywords):
            return 'hemp_clothing'
        
        # Add more category filters as needed
        if 'jar' in query or 'container' in query:
            return 'jars'
        
        if 'glass' in query or 'bubbler' in query or 'adapter' in query:
            return 'glass'
        
        if 'battery' in query or 'charger' in query:
            return 'batteries'
        
        return None
    
    def _extract_intent_hints(self, query: str) -> List[str]:
        """Extract intent signals from query"""
        hints = []
        
        # Support queries (high priority)
        if any(word in query for word in self.troubleshooting_words):
            hints.append('troubleshooting')
        
        if any(word in query for word in self.how_to_words):
            hints.append('how_to')
        
        # Comparison
        if any(word in query for word in self.comparison_words):
            hints.append('comparison')
        
        # Shopping
        if any(word in query for word in self.shopping_words):
            hints.append('shopping')
        
        return hints
