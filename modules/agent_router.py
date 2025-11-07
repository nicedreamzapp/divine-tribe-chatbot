#!/usr/bin/env python3
"""
agent_router.py - Context Engineering Agent with Customer Service Intelligence
Routes queries to: CAG Cache, RAG Search, Support, Troubleshooting, or Rejection

PRIORITY ORDER (CRITICAL):
1. Off-topic rejection
2. Customer service (troubleshooting, returns, warranty, how-to, orders)
3. Product cache (for product info queries)
4. Mistral reasoning (for advice/comparison)
5. RAG search (for accessories)
"""

from typing import Dict, Tuple, Optional
import re


class AgentRouter:
    """
    The "brain" that decides what to do with each query.
    NOW WITH CUSTOMER SERVICE INTELLIGENCE!
    """
    
    def __init__(self, cag_cache, product_database):
        """
        Args:
            cag_cache: CAGCache instance
            product_database: ProductDatabase instance (for RAG)
        """
        self.cache = cag_cache
        self.db = product_database
        
        # Off-topic rejection patterns
        self.offtopic_patterns = [
            r'\b(elephant|france|capital|cake|weather|bitcoin|president|python|pizza|movie|car|garden|workout|pasta|japan|guitar|photo|poem|math|stock)\b',
            r'\b(recipe|travel|learn|tips)\b'
        ]
        
        # Customer service patterns (NEW!)
        self.troubleshooting_keywords = [
            'broken', 'not working', 'stopped working', 'won\'t work', 'doesn\'t work',
            'leaking', 'leaky', 'cracked', 'damaged', 'defective',
            'issue', 'problem', 'help', 'fix', 'repair',
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
    
    def route(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Main routing logic with CUSTOMER SERVICE PRIORITY.
        
        Returns:
            {
                'route': 'cache'|'rag'|'support'|'troubleshooting'|'how_to'|'warranty'|'return'|'order'|'mistral'|'reject',
                'data': response data or None,
                'reasoning': why this route was chosen
            }
        """
        query_lower = query.lower().strip()
        
        # ROUTE 1: Off-topic rejection (always first)
        if self._is_offtopic(query_lower):
            return {
                'route': 'reject',
                'data': self._get_rejection_message(),
                'reasoning': 'Off-topic query detected'
            }
        
        # ROUTE 2: CUSTOMER SERVICE CHECKS (BEFORE PRODUCTS!)
        
        # 2A: Troubleshooting (device problems)
        if self._is_troubleshooting(query_lower):
            response = self.cache.get_troubleshooting_response(query)
            return {
                'route': 'troubleshooting',
                'data': response,
                'reasoning': 'User has a technical problem - troubleshooting needed',
                'query': query  # Pass through for Mistral if needed
            }
        
        # 2B: How-to questions (instructions)
        if self._is_how_to_question(query_lower):
            response = self.cache.get_how_to_response(query)
            return {
                'route': 'how_to',
                'data': response,
                'reasoning': 'User needs instructions',
                'query': query  # Pass through for Mistral if needed
            }
        
        # 2C: Warranty claims
        if self._is_warranty_claim(query_lower):
            response = self.cache.get_warranty_response(query)
            return {
                'route': 'warranty',
                'data': response,
                'reasoning': 'Warranty claim detected'
            }
        
        # 2D: Returns/refunds
        if self._is_return_request(query_lower):
            response = self.cache.get_return_response(query)
            return {
                'route': 'return',
                'data': response,
                'reasoning': 'Return/refund request detected'
            }
        
        # 2E: Order inquiries
        if self._is_order_inquiry(query_lower):
            response = self.cache.get_order_response(query)
            return {
                'route': 'order',
                'data': response,
                'reasoning': 'Order status inquiry'
            }
        
        # ROUTE 3: Mistral reasoning (advice/comparison questions)
        if self._needs_mistral_reasoning(query_lower):
            return {
                'route': 'mistral',
                'data': None,
                'reasoning': 'Needs AI reasoning for advice/recommendation',
                'query': query
            }
        
        # ROUTE 4: Cached main products (product info)
        product_key = self.cache.check_cache(query)
        if product_key:
            response = self.cache.format_product_response(product_key)
            return {
                'route': 'cache',
                'data': response,
                'reasoning': f'Matched cached product: {product_key}',
                'product_key': product_key
            }
        
        # ROUTE 5: Cached support info
        support = self.cache.get_support_info(query)
        if support:
            return {
                'route': 'support',
                'data': support,
                'reasoning': 'Matched support query'
            }
        
        # ROUTE 6: Cached comparisons
        comparison = self.cache.get_comparison(query)
        if comparison:
            return {
                'route': 'comparison',
                'data': comparison,
                'reasoning': 'Matched comparison query'
            }
        
        # ROUTE 7: Smart category listings (NEW! - prevents jar/cup/glass confusion)
        category_listing = self.cache.get_category_listing(query)
        if category_listing:
            return {
                'route': 'category',
                'data': category_listing,
                'reasoning': 'Matched category listing (jars, glass, cups)'
            }
        
        # ROUTE 8: RAG search for accessories/parts
        if self._needs_rag_search(query_lower):
            return {
                'route': 'rag',
                'data': None,
                'reasoning': 'Needs RAG search for accessories/parts',
                'query': query
            }
        
        # ROUTE 8: General/conversational
        if self._is_general_question(query_lower):
            return {
                'route': 'general',
                'data': None,
                'reasoning': 'General conversational query'
            }
        
        # Default: Try RAG search
        return {
            'route': 'rag',
            'data': None,
            'reasoning': 'Default to RAG search',
            'query': query
        }
    
    def _is_troubleshooting(self, query: str) -> bool:
        """
        Detect if user has a technical problem.
        Examples: "my v5 won't work", "leaking", "not heating"
        """
        return any(keyword in query for keyword in self.troubleshooting_keywords)
    
    def _is_how_to_question(self, query: str) -> bool:
        """
        Detect if user needs instructions.
        Examples: "how do I clean", "how to use", "settings"
        """
        return any(keyword in query for keyword in self.how_to_keywords)
    
    def _is_warranty_claim(self, query: str) -> bool:
        """
        Detect warranty claims.
        Examples: "warranty", "defective", "broken on arrival"
        """
        return any(keyword in query for keyword in self.warranty_keywords)
    
    def _is_return_request(self, query: str) -> bool:
        """
        Detect return/refund requests.
        Examples: "how do I return", "refund", "send it back"
        """
        return any(keyword in query for keyword in self.return_keywords)
    
    def _is_order_inquiry(self, query: str) -> bool:
        """
        Detect order status questions.
        Examples: "where is my order", "tracking", "hasn't arrived"
        """
        return any(keyword in query for keyword in self.order_keywords)
    
    def _needs_mistral_reasoning(self, query: str) -> bool:
        """
        Detect if query needs AI reasoning/advice.
        Examples: "which should I buy", "what's better", "recommend"
        """
        reasoning_indicators = [
            'which', 'what should', 'recommend', 'suggest', 'advice',
            'better', 'best for', 'which one', 'help me choose',
            'good for', 'right for', 'vs', 'versus', 'compare',
            'difference between', 'worth it', 'is it good'
        ]
        
        return any(indicator in query for indicator in reasoning_indicators)
    
    def _is_offtopic(self, query: str) -> bool:
        """Check if query is off-topic"""
        for pattern in self.offtopic_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    def _get_rejection_message(self) -> str:
        """Polite rejection for off-topic queries"""
        return """I'm the Divine Tribe product assistant - I can only help with:

🌿 Divine Tribe vaporizer products
💬 Product recommendations & comparisons  
🔧 Technical support & troubleshooting
📦 Orders, shipping, and returns

For other topics, I'd recommend searching Google or asking a general AI assistant!"""
    
    def _needs_rag_search(self, query: str) -> bool:
        """Check if query needs RAG search (accessories, parts, etc.)"""
        accessory_keywords = [
            'jar', 'insert', 'sic', 'titanium cup', 'ceramic cup',
            'quartz', 'glass', 'bubbler', 'carb cap', 'o-ring', 'screen',
            'spare', 'bottomless banger', 'hydratube', '510 cable', 'mod',
            'pico', 'arctic fox', 'battery', 'terp slurper', 'enail', 'coil'
        ]
        
        # Only search for accessories if NOT asking about problems
        if self._is_troubleshooting(query) or self._is_how_to_question(query):
            return False
        
        return any(keyword in query for keyword in accessory_keywords)
    
    def _is_general_question(self, query: str) -> bool:
        """Check if it's a general conversational query"""
        general_patterns = [
            'hello', 'hi ', 'hey', 'thanks', 'thank you',
            'how are you', 'what can you do', 'help me',
            'what is divine tribe', 'who are you'
        ]
        
        return any(pattern in query for pattern in general_patterns)
    
    def execute_rag_search(self, query: str, max_results: int = 5) -> str:
        """
        Execute RAG search and format response beautifully.
        Bold product names with links, clean spacing, NO TRUNCATION.
        HTML cleaning to remove junk from descriptions.
        """
        results = self.db.search(query, max_results=max_results)
        
        if not results:
            return f"I couldn't find products matching '{query}'.\n\n🌐 Browse all products: https://ineedhemp.com\n📧 Need help? Email matt@ineedhemp.com"
        
        # Format results beautifully - NO CHARACTER LIMITS
        response = f"🔍 **Found {len(results)} product(s) for '{query}':**\n\n"
        
        for i, product in enumerate(results, 1):
            name = product.get('name', 'Unknown Product')
            price = product.get('price', 'Check website')
            url = product.get('url', 'https://ineedhemp.com')
            desc = product.get('description', '')
            
            # Clean description - remove HTML entities and extra whitespace
            desc = re.sub(r'\\n', ' ', desc)  # Remove \n
            desc = re.sub(r'\s+', ' ', desc)  # Collapse multiple spaces
            desc = re.sub(r'<[^>]+>', '', desc)  # Remove HTML tags
            desc = desc.strip()
            
            # Bold linked product name - FULL NAME
            response += f"{i}. **[{name}]({url})**\n"
            
            if price and price != 'Check website':
                response += f"   💰 Price: {price}\n"
            
            if desc and len(desc) > 20:
                # Show first 150 chars of CLEANED description
                desc_preview = desc[:150] + "..." if len(desc) > 150 else desc
                response += f"   📝 {desc_preview}\n"
            
            response += "\n"
        
        response += f"📧 Questions? Email matt@ineedhemp.com\n"
        response += f"🌐 View all: https://ineedhemp.com"
        
        return response
    
    def get_stats(self) -> Dict:
        """Get routing statistics"""
        return {
            'cached_products': len(self.cache.cached_products),
            'total_products_in_db': len(self.db.products),
            'support_info_items': len(self.cache.support_info),
            'rejection_patterns': len(self.offtopic_patterns),
            'customer_service_enabled': True
        }


# Convenience function
def route_query(query: str, cag_cache, product_database) -> Dict:
    """Quick routing function"""
    router = AgentRouter(cag_cache, product_database)
    return router.route(query)


# Testing
def test_agent_router():
    """Test the agent router with customer service scenarios"""
    print("\n" + "="*70)
    print("AGENT ROUTER TEST - WITH CUSTOMER SERVICE")
    print("="*70 + "\n")
    
    # Import dependencies
    import sys
    sys.path.insert(0, '/mnt/user-data/uploads')
    
    from cag_cache import CAGCache
    from product_database import ProductDatabase
    
    cache = CAGCache()
    db = ProductDatabase('/mnt/user-data/uploads/products_organized.json')
    router = AgentRouter(cache, db)
    
    # Test queries including customer service
    test_queries = [
        ("my v5 cup is cracked", "Should route to TROUBLESHOOTING/WARRANTY"),
        ("how do I clean my core deluxe", "Should route to HOW_TO"),
        ("my order hasn't arrived", "Should route to ORDER"),
        ("what should I buy for flavor", "Should route to MISTRAL"),
        ("what is the v5 xl", "Should use CACHE"),
        ("uv jars", "Should use RAG"),
        ("warranty info", "Should use WARRANTY"),
        ("how to return", "Should use RETURN"),
        ("v5 xl vs core", "Should use COMPARISON")
    ]
    
    for query, expected in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: '{query}'")
        print(f"Expected: {expected}")
        print(f"{'='*70}")
        
        result = router.route(query)
        
        print(f"✅ Route: {result['route'].upper()}")
        print(f"💭 Reasoning: {result['reasoning']}")
        
        if result['data']:
            print(f"\n📄 Response Preview:")
            preview = result['data'][:200] + "..." if len(result['data']) > 200 else result['data']
            print(preview)
    
    # Print stats
    print(f"\n{'='*70}")
    print("ROUTER STATS")
    print(f"{'='*70}")
    stats = router.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    test_agent_router()
