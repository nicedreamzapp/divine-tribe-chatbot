#!/usr/bin/env python3
from typing import Dict, Optional

class IntentClassifier:
    def __init__(self, cag_cache):
        self.cag_cache = cag_cache
    
    def classify(self, preprocessed: Dict, context: Dict = None) -> Dict:
        context = context or {}
        
        if preprocessed['url']:
            return {'intent': 'specific_product', 'confidence': 1.0, 'reasoning': 'URL provided'}
        
        # Check for troubleshooting/how-to keywords (before cache!)
        query_lower = preprocessed['cleaned']
        
        # Troubleshooting keywords
        trouble_words = [
            'won\'t heat', 'not heating', 'resistance reading', 'flashing', 'error',
            'short', 'tastes burnt', 'burnt taste', 'leaking', 'no vapor', 'broken',
            'not working', 'problem', 'issue', 'fix', 'cracked', 'jumping',
            'wont heat', 'wont turn on', 'cant turn on', 'doesnt work'
        ]
        if any(word in query_lower for word in trouble_words):
            return {'intent': 'troubleshooting', 'confidence': 0.9, 'reasoning': 'Troubleshooting detected'}
        
        # How-to keywords
        how_to_words = ['how to', 'how do i', 'clean', 'what temp', 'settings', 'tcr',
                       'arctic fox', 'install', 'setup', 'instructions']
        if any(word in query_lower for word in how_to_words):
            return {'intent': 'how_to', 'confidence': 0.9, 'reasoning': 'How-to detected'}
        
        if 'troubleshooting' in preprocessed.get('intent_hints', []):
            return {'intent': 'troubleshooting', 'confidence': 0.9, 'reasoning': 'Troubleshooting detected'}
        
        # Check for return/warranty/order keywords (before cache!)
        query_lower = preprocessed['cleaned']
        if any(word in query_lower for word in ['return', 'refund', 'send back', 'exchange']):
            return {'intent': 'return', 'confidence': 0.9, 'reasoning': 'Return request detected'}
        if any(word in query_lower for word in ['warranty', 'guarantee', 'defective', 'doa']):
            return {'intent': 'warranty', 'confidence': 0.9, 'reasoning': 'Warranty inquiry detected'}
        if any(word in query_lower for word in ['order', 'tracking', 'shipped', 'delivery', 'where is my']):
            return {'intent': 'order', 'confidence': 0.9, 'reasoning': 'Order status inquiry detected'}
        
        material = preprocessed.get('material_type')
        if material == 'concentrate':
            return {'intent': 'material_shopping', 'confidence': 0.85, 'reasoning': 'Concentrate query', 'metadata': {'material': material}}
        if material == 'dry_herb':
            return {'intent': 'material_shopping', 'confidence': 0.85, 'reasoning': 'Dry herb query', 'metadata': {'material': material}}
        if material == 'both':
            return {'intent': 'both_materials', 'confidence': 0.9, 'reasoning': 'Both materials'}
        
        cache_result = self._check_cache(preprocessed)
        if cache_result:
            return {'intent': cache_result['intent'], 'confidence': 0.95, 'reasoning': 'Cache hit', 'cached_response': cache_result['response']}
        
        if preprocessed['product_mention']:
            if 'shopping' in preprocessed['intent_hints']:
                return {'intent': 'shopping', 'confidence': 0.8, 'reasoning': 'Product + shopping'}
            return {'intent': 'product_info', 'confidence': 0.8, 'reasoning': 'Product mention'}
        
        if 'comparison' in preprocessed['intent_hints']:
            return {'intent': 'comparison', 'confidence': 0.85, 'reasoning': 'Comparison'}
        if 'shopping' in preprocessed['intent_hints']:
            return {'intent': 'shopping', 'confidence': 0.7, 'reasoning': 'Shopping intent'}
        
        return {'intent': 'general', 'confidence': 0.3, 'reasoning': 'Default'}
    
    def _check_cache(self, preprocessed: Dict) -> Optional[Dict]:
        query = preprocessed['cleaned']
        troubleshooting_words = ['broken', 'not working', 'problem', 'issue', 'fix', 'help', 'cracked', 'leaking']
        if any(word in query for word in troubleshooting_words):
            return None
        product_key = self.cag_cache.check_cache(query)
        if product_key:
            return {'intent': 'product_info', 'response': self.cag_cache.format_product_response(product_key)}
        comparison = self.cag_cache.get_comparison(query)
        if comparison:
            return {'intent': 'comparison', 'response': comparison}
        return None
