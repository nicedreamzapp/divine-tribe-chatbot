#!/usr/bin/env python3
"""
agent_router.py - Routes queries to appropriate handlers
FIXED: Creative/story queries go to general_mistral, not troubleshooting
"""

from typing import Dict, Tuple, Optional
import re

# Import enterprise components
try:
    from modules.query_preprocessor import QueryPreprocessor
    from modules.intent_classifier import IntentClassifier
    ENTERPRISE_MODE = True
except ImportError:
    ENTERPRISE_MODE = False
    print("⚠️  Enterprise components not found - running in standard mode")


class AgentRouter:
    """
    Routes queries intelligently:
    1. Troubleshooting/How-To → CAG cache
    2. Product queries → RAG search
    3. Company info → CAG cache
    4. General knowledge → Mistral
    """
    
    def __init__(self, cag_cache, product_database, context_manager=None):
        self.cache = cag_cache
        self.db = product_database
        self.context_manager = context_manager
        
        # Initialize enterprise components if available
        if ENTERPRISE_MODE:
            self.query_preprocessor = QueryPreprocessor()
            self.intent_classifier = IntentClassifier(cag_cache)
            print("✅ Agent Router initialized (ENTERPRISE MODE)")
        else:
            self.query_preprocessor = None
            self.intent_classifier = None
            print("✅ Agent Router initialized (STANDARD MODE)")
        
        # Competitor brands (filter these)
        self.competitor_brands = [
            'puffco', 'peak', 'puffco peak',
            'storz', 'bickel', 'storz & bickel', 'storz and bickel',
            'mighty', 'crafty', 'volcano',
            'arizer', 'solo', 'air', 'extreme q',
            'dynavap', 'vapcap',
            'davinci', 'iq', 'miqro',
            'firefly',
            'pax', 'pax 2', 'pax 3',
            'kandypens',
            'boundless',
            'healthy rips',
            'zeus'
        ]
        
        # Customer service patterns
        self.troubleshooting_keywords = [
            'broken', 'not working', 'stopped working', 'won\'t work', 'doesn\'t work',
            'leaking', 'leaky', 'cracked', 'damaged', 'defective',
            'won\'t heat', 'no vapor', 'not heating', 'burnt', 'taste bad',
            'resistance', 'ohm', 'reading'
        ]
        
        self.how_to_keywords = [
            'how do i', 'how to', 'how can i', 'instructions',
            'setup', 'set up', 'install', 'use', 'clean', 'maintain',
            'settings', 'temperature', 'what temp', 'tcr'
        ]
        
        self.warranty_keywords = [
            'warranty', 'guarantee', 'defective', 'broke', 'broken on arrival',
            'doa', 'dead on arrival', 'never worked'
        ]
        
        self.return_keywords = [
            'return', 'refund', 'exchange', 'send back', 'give back',
            'wrong item', 'didn\'t order'
        ]
        
        self.order_keywords = [
            'order', 'tracking', 'shipped', 'delivery', 'when will',
            'where is my', 'hasn\'t arrived', 'not received'
        ]
        
        # Business-related keywords (for product queries)
        self.product_keywords = [
            # Main vapes
            'v5', 'v 5', 'core', 'deluxe', 'tug', 'fogger', 'nice dreamz',
            'lightning pen', 'ruby twist', 'gen 2', 'generation 2',
            'cub', 'xl', 'extra large',
            
            # Product categories
            'vaporizer', 'vaporizers', 'vape', 'vapes', 'atomizer', 'atomizers', 'erig', 'e-rig', 'enail', 'e-nail',
            
            # Materials
            'concentrate', 'concentrates', 'wax', 'dab', 'dabs', 'oil', 'shatter', 'rosin', 'resin',
            'dry herb', 'flower', 'herb', 'bud',
            
            # Accessories
            'jar', 'jars', 'glass', 'bubbler', 'banger', 'cup', 'carb cap',
            'coil', 'heater', 'battery', 'mod', 'pico',
            
            # Hemp products
            'hemp', 'shirt', 't-shirt', 'tshirt', 'hoodie', 'clothing', 'boxer', 'clothes', 'apparel',
            
            # Company
            'divine tribe', 'ineedhemp', 'matt', 'divine crossing'
        ]
    
    def route(self, query: str, context: Optional[Dict] = None, session_id: str = "default") -> Dict:
        """Main routing logic - FIXED for creative queries"""
        query_lower = query.lower().strip()
        
        # ENTERPRISE PREPROCESSING
        if ENTERPRISE_MODE and self.query_preprocessor and self.intent_classifier:
            preprocessed = self.query_preprocessor.process(query)
            
            if self.context_manager:
                ctx = self.context_manager.get_retrieval_context(session_id)
            else:
                ctx = context or {}
            
            intent_result = self.intent_classifier.classify(preprocessed, ctx)
            intent = intent_result['intent']
            
            if 'cached_response' in intent_result:
                print(f"⚡ CACHE HIT: {query[:50]}")
                return {
                    'route': 'cache',
                    'data': intent_result['cached_response'],
                    'reasoning': 'CAG cache hit (enterprise mode)',
                    'confidence': intent_result['confidence']
                }
            
            if intent == 'material_shopping':
                print(f"🎯 Material shopping detected: {intent_result.get('metadata', {}).get('material')}")
                return {
                    'route': 'material_shopping',
                    'data': None,
                    'reasoning': f"Material shopping: {intent_result.get('metadata', {}).get('material')}",
                    'query': query,
                    'metadata': intent_result.get('metadata', {})
                }
        
        # ROUTE 1: COMPETITOR MENTIONS
        if self._mentions_competitors(query_lower):
            return {
                'route': 'competitor_mention',
                'data': self._get_competitor_response(query_lower),
                'reasoning': 'Competitor brand mentioned',
                'query': query
            }
        
        # ROUTE 2: CUSTOMER SERVICE
        
        # 2A: Troubleshooting (FIXED - excludes creative queries)
        if self._is_troubleshooting(query_lower):
            response = self.cache.get_troubleshooting_response(query)
            return {
                'route': 'troubleshooting',
                'data': response,
                'reasoning': 'Technical problem detected',
                'query': query
            }
        
        # 2B: How-to questions
        if self._is_how_to_question(query_lower):
            response = self.cache.get_how_to_response(query)
            return {
                'route': 'how_to',
                'data': response,
                'reasoning': 'How-to question',
                'query': query
            }
        
        # 2C: Warranty
        if self._is_warranty_claim(query_lower):
            response = self.cache.get_warranty_response(query)
            return {
                'route': 'warranty',
                'data': response,
                'reasoning': 'Warranty claim'
            }
        
        # 2D: Returns
        if self._is_return_request(query_lower):
            response = self.cache.get_return_response(query)
            return {
                'route': 'return',
                'data': response,
                'reasoning': 'Return request'
            }
        
        # 2E: Order status
        if self._is_order_inquiry(query_lower):
            response = self.cache.get_order_response(query)
            return {
                'route': 'order',
                'data': response,
                'reasoning': 'Order inquiry'
            }
        
        # ROUTE 2.5: COMPANY INFO
        company_queries = ['about divine tribe', 'what is divine tribe', 'who is divine tribe',
                          'tell me about divine tribe', 'how about divine tribe', 'what kind of vaporizers']
        if any(phrase in query_lower for phrase in company_queries):
            support_response = self.cache.get_support_info(query)
            if support_response:
                return {
                    'route': 'support',
                    'data': support_response,
                    'reasoning': 'Company info inquiry',
                    'query': query
                }
        
        # ROUTE 3: PRODUCT QUERIES (ALL GO TO RAG SEARCH)
        is_product_related = self._is_product_related(query_lower)
        
        if is_product_related:
            # 3A: Comparison queries
            comparison = self.cache.get_comparison(query_lower)
            if comparison:
                return {
                    'route': 'comparison',
                    'data': comparison,
                    'reasoning': 'Product comparison'
                }
            
            # 3B: ALL product queries go to RAG search
            return {
                'route': 'rag',
                'data': None,
                'reasoning': 'Product query - search products_clean.json',
                'query': query
            }
        
        # ROUTE 4: GENERAL KNOWLEDGE (Mistral)
        return {
            'route': 'general_mistral',
            'data': None,
            'reasoning': 'General knowledge question',
            'query': query,
            'is_business_related': is_product_related
        }
    
    def _is_product_related(self, query: str) -> bool:
        """Check if query is about YOUR products/business"""
        return any(keyword in query for keyword in self.product_keywords)
    
    def _mentions_competitors(self, query: str) -> bool:
        """Check if query mentions competitor brands"""
        return any(brand in query for brand in self.competitor_brands)
    
    def _is_troubleshooting(self, query: str) -> bool:
        """
        Check if user has a technical problem
        FIXED: Excludes creative/story/funny queries
        """
        # Don't match general help phrases
        if query in ['help', 'i need help', 'can you help', 'help me', 'i dont know anything about vapes help']:
            return False
        
        # FIXED: Don't match creative/story/funny requests
        creative_indicators = [
            'story', 'funny', 'joke', 'tell me about',
            'do bankers', 'are you', 'tell me a',
            'write', 'create', 'make up', 'imagine'
        ]
        if any(indicator in query for indicator in creative_indicators):
            return False
        
        # Only match specific technical issues
        return any(keyword in query for keyword in self.troubleshooting_keywords)
    
    def _is_how_to_question(self, query: str) -> bool:
        """Check if user needs instructions"""
        return any(keyword in query for keyword in self.how_to_keywords)
    
    def _is_warranty_claim(self, query: str) -> bool:
        """Check if user is making warranty claim"""
        return any(keyword in query for keyword in self.warranty_keywords)
    
    def _is_return_request(self, query: str) -> bool:
        """Check if user wants to return something"""
        return any(keyword in query for keyword in self.return_keywords)
    
    def _is_order_inquiry(self, query: str) -> bool:
        """Check if user is asking about their order"""
        return any(keyword in query for keyword in self.order_keywords)
    
    def _get_competitor_response(self, query: str) -> str:
        """Neutral response when competitors mentioned"""
        return """I focus on Divine Tribe products and can't provide detailed comparisons with other brands. 

However, I'm happy to explain what makes Divine Tribe unique:
- Rebuildable technology (save money long-term)
- Made in USA
- Direct pricing (no middleman markup)
- Active community support

What would you like to know about Divine Tribe specifically?

📧 Email: matt@ineedhemp.com
🌐 Shop: https://ineedhemp.com"""
    
    def execute_rag_search(self, query: str, max_results: int = 5, session_id: str = "default") -> str:
        """Execute RAG search and format response - prioritize main kits"""
        # Get context if available
        context = None
        if self.context_manager:
            context = self.context_manager.get_retrieval_context(session_id)
        
        # Execute search
        results = self.db.search(query, max_results=max_results, context=context)
        
        if not results:
            return f"I couldn't find products matching '{query}'.\n\n🌐 Browse all products: https://ineedhemp.com\n📧 Need help? Email matt@ineedhemp.com"
        
        # FILTER OUT REPLACEMENT PARTS
        filtered_results = [p for p in results if p.get('category', '').lower() != 'replacement_parts']
        
        if not filtered_results:
            filtered_results = results  # Fallback if all were replacement parts
        
        # Format results
        response = f"🔍 **Found {len(filtered_results)} product(s) for '{query}':**\n\n"
        
        for i, product in enumerate(filtered_results, 1):
            name = product.get('name', 'Unknown Product')
            url = product.get('url', 'https://ineedhemp.com')
            desc = product.get('description', '')
            
            # Clean description
            desc = re.sub(r'\\n', ' ', desc)
            desc = re.sub(r'\s+', ' ', desc)
            desc = re.sub(r'<[^>]+>', '', desc)
            desc = desc.strip()
            
            response += f"{i}. **[{name}]({url})**\n"
            
            if desc and len(desc) > 20:
                desc_preview = desc[:150] + "..." if len(desc) > 150 else desc
                response += f"   📝 {desc_preview}\n"
            
            response += "\n"
        
        response += f"📧 Questions? Email matt@ineedhemp.com\n"
        response += f"🌐 View all: https://ineedhemp.com"
        
        # Log to context if available
        if self.context_manager:
            self.context_manager.add_exchange(
                session_id=session_id,
                user_query=query,
                bot_response=response,
                products_shown=filtered_results,
                intent='rag_search'
            )
        
        return response
    
    def get_stats(self) -> Dict:
        """Get routing statistics"""
        stats = {
            'total_products_in_db': len(self.db.products),
            'support_info_items': len(self.cache.support_info),
            'mode': 'RAG_ONLY_FOR_PRODUCTS',
            'competitor_brands_blocked': len(self.competitor_brands),
            'customer_service_enabled': True,
            'enterprise_mode': ENTERPRISE_MODE
        }
        
        if self.context_manager:
            stats['active_sessions'] = len(self.context_manager.sessions)
        
        return stats
