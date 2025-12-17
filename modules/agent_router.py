#!/usr/bin/env python3
"""
agent_router.py - Routes queries to appropriate handlers
FIXED: Creative/story queries go to general_mistral, not troubleshooting
"""

from typing import Dict, Tuple, Optional
import re

# Import order verification for secure order lookups
try:
    from modules.order_verify import extract_order_number, handle_order_inquiry
    ORDER_VERIFY_AVAILABLE = True
except ImportError:
    ORDER_VERIFY_AVAILABLE = False
    print("⚠️  Order verification not available")

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
            'coil', 'heater', 'battery', 'mod', 'pico', 'storage', 'container',
            'hubble', 'bubble', 'hydratube', 'hydra tube', 'hubble bubble',
            
            # Hemp products
            'hemp', 'shirt', 't-shirt', 'tshirt', 'hoodie', 'clothing', 'boxer', 'boxers', 'clothes', 'apparel',
            'fleece', 'pants', 'shorts', 'cargo', 'washcloth', 'digicam', 'silk',

            # More accessories and parts
            'caps', 'carb cap', 'vortex cap', 'disc cap', 'vortex', 'disc', 'tip', 'tips', 'drip tip', 'mouthpiece',
            'sic', 'silicon carbide', 'crucible', 'insert', 'donut', 'spacer',
            'oring', 'o-ring', 'orings', 'spring', 'pin', 'post', 'clip',
            'adapter', 'stand', 'recycler', 'rig', 'water pipe',

            # Company
            'divine tribe', 'ineedhemp', 'matt', 'divine crossing'
        ]

        # Content moderation - inappropriate content patterns
        self.inappropriate_patterns = [
            # Explicit/adult content
            'naked', 'nude', 'nsfw', 'porn', 'sex', 'xxx',
            'no clothes', 'without clothes', 'undressed',
            'rubbing', 'touching body', 'erotic',
            # Violence
            'kill', 'murder', 'attack', 'weapon',
            # Other inappropriate
            'illegal', 'drugs', 'cocaine', 'heroin', 'meth',
        ]

    def route(self, query: str, context: Optional[Dict] = None, session_id: str = "default") -> Dict:
        """Main routing logic - FIXED for creative queries"""
        query_lower = query.lower().strip()

        # ROUTE -2: CHECK FOR PENDING ORDER VERIFICATION (highest priority)
        # If we're waiting for customer to verify their identity, route to order
        if context and context.get('pending_challenge'):
            if ORDER_VERIFY_AVAILABLE:
                result = handle_order_inquiry(query, context)
                return {
                    'route': 'order',
                    'data': result.get('response'),
                    'reasoning': 'Order verification answer',
                    'needs_verification': result.get('needs_verification', False),
                    'verified': result.get('verified', False),
                    'order_info': result.get('order_info'),
                    'challenge': result.get('challenge'),
                    'pending_challenge': result.get('pending_challenge'),
                    'needs_order_number': result.get('needs_order_number', False)
                }

        # ROUTE -1: CONTENT MODERATION (before anything else)
        if self._is_inappropriate(query_lower):
            return {
                'route': 'moderated',
                'data': self._get_moderation_response(),
                'reasoning': 'Content moderation - inappropriate request',
                'query': query
            }

        # ROUTE 0: CHECK FOR IMAGE GENERATION REQUESTS (before anything else)
        if self._is_image_request(query_lower):
            return {
                'route': 'image_request',
                'data': "🎨 **This looks like an image request!**\n\nTo generate AI images, please use the **'Generate Image'** button below the chat and enter your prompt there.\n\nThe image generator can create custom artwork based on your description!",
                'reasoning': 'Image generation request detected',
                'query': query
            }

        # ROUTE 0.5: QUICK ANSWERS (coupons, shipping, terminology)
        quick_answer = self.cache.get_quick_answer(query)
        if quick_answer:
            print(f"⚡ QUICK ANSWER: {query[:50]}")
            return {
                'route': 'quick_answer',
                'data': quick_answer,
                'reasoning': 'Quick answer cache hit',
                'query': query
            }

        # ROUTE 0.6: CUSTOMER SERVICE (damaged, missing, wrong items, atomizer errors)
        customer_service = self.cache.get_customer_service_response(query)
        if customer_service:
            print(f"🛎️ CUSTOMER SERVICE: {query[:50]}")
            return {
                'route': 'customer_service',
                'data': customer_service,
                'reasoning': 'Customer service issue detected',
                'query': query
            }

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
        
        # 2E: Order status - USE REAL WOOCOMMERCE LOOKUP
        if self._is_order_inquiry(query_lower):
            if ORDER_VERIFY_AVAILABLE:
                # Use real order verification with WooCommerce
                order_context = context or {}
                result = handle_order_inquiry(query, order_context)

                return {
                    'route': 'order',
                    'data': result.get('response'),
                    'reasoning': 'Order inquiry - WooCommerce lookup',
                    'needs_verification': result.get('needs_verification', False),
                    'verified': result.get('verified', False),
                    'order_info': result.get('order_info'),
                    'challenge': result.get('challenge'),  # Store in session for next turn
                    'needs_order_number': result.get('needs_order_number', False)
                }
            else:
                # Fallback to static response
                response = self.cache.get_order_response(query)
                return {
                    'route': 'order',
                    'data': response,
                    'reasoning': 'Order inquiry (static - WooCommerce unavailable)'
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
        FIXED: Excludes creative/story/funny queries and shipping/arrival issues
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

        # FIXED: Don't match shipping/arrival issues - those are customer service
        shipping_indicators = [
            'arrived', 'received', 'delivery', 'shipped', 'package',
            'order', 'came', 'missing', 'wrong item'
        ]
        if any(indicator in query for indicator in shipping_indicators):
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
        # Check for order keywords
        if any(keyword in query for keyword in self.order_keywords):
            return True

        # Also check if query is just an order number (5-7 digits)
        # This handles when user replies with just "199214"
        clean_query = query.strip().replace('#', '')
        if clean_query.isdigit() and 5 <= len(clean_query) <= 7:
            return True

        return False
    
    def _is_image_request(self, query: str) -> bool:
        """
        Detect image generation requests
        Looks for descriptive phrases about appearance, characters, scenes, art styles
        """
        query_lower = query.lower()

        # Direct image request indicators
        image_keywords = [
            'generate image', 'create image', 'make image', 'draw', 'picture of',
            'image of', 'generate a', 'create a picture', 'make a picture',
            'make me a', 'create me a', 'draw me a'
        ]
        if any(keyword in query_lower for keyword in image_keywords):
            return True

        # Art style indicators (like "by monet", "in the style of")
        art_indicators = [
            'by monet', 'by picasso', 'by van gogh', 'by dali', 'by warhol',
            'in the style of', 'art style', 'painting of', 'illustration of',
            'digital art', 'oil painting', 'watercolor', 'sketch of',
            'portrait of', 'landscape of', 'scene of'
        ]
        if any(indicator in query_lower for indicator in art_indicators):
            return True

        # Descriptive patterns that suggest image generation (appearance descriptions)
        appearance_patterns = [
            # Hair descriptions
            'blonde hair', 'brown hair', 'red hair', 'black hair', 'hair color',
            # Age descriptions
            'years old', 'year old',
            # Clothing descriptions in detail
            'wearing a', 'dressed in', 'yellow shorts', 'black top', 'blue shirt',
            # Character descriptions
            'boy with', 'girl with', 'man with', 'woman with', 'person with',
            # Action + appearance combos
            'running and', 'waving', 'standing', 'sitting',
            # Scene/setting descriptions
            'sunset', 'sunrise', 'golden hour', 'silhouette', 'rays of light',
            'sun rays', 'sunbeams', 'glowing', 'cinematic', 'dramatic lighting'
        ]

        # Count how many appearance patterns match
        matches = sum(1 for pattern in appearance_patterns if pattern in query_lower)

        # If multiple appearance descriptors, likely image request
        if matches >= 2:
            return True

        # Very long descriptive queries (100+ chars) with visual words are likely image prompts
        visual_words = ['color', 'light', 'dark', 'bright', 'shadow', 'sky', 'tree', 'forest',
                       'beach', 'mountain', 'city', 'building', 'animal', 'dog', 'cat', 'bear',
                       'unicycle', 'bicycle', 'car', 'house', 'grass', 'flower', 'ocean', 'water']
        if len(query) > 100:
            visual_matches = sum(1 for word in visual_words if word in query_lower)
            if visual_matches >= 3:
                return True

        # Short artistic prompts like "bear on a unicycle by monet"
        if len(query.split()) <= 10:
            # Check for [subject] + [by artist] pattern
            artists = ['monet', 'picasso', 'van gogh', 'dali', 'rembrandt', 'warhol', 'banksy']
            if any(f'by {artist}' in query_lower for artist in artists):
                return True

        return False

    def _is_inappropriate(self, query: str) -> bool:
        """Check if query contains inappropriate content"""
        return any(pattern in query for pattern in self.inappropriate_patterns)

    def _get_moderation_response(self) -> str:
        """Response for moderated/inappropriate content - playful redirect"""
        import random
        jokes = [
            "Whoa there! 😅 I think you need to chill... maybe with a nice session from the **Core XL Deluxe**? It's got 6 heat settings for the perfect vibe!",
            "Haha, that's a bit outside my wheelhouse! But you know what IS in my wheelhouse? Premium vaporizers! The **V5 XL** delivers amazing flavor if you're looking to relax. 🌿",
            "I appreciate the creativity, but let's channel that energy into something productive - like picking out a new vape! The **Ruby Twist** is perfect for dry herb enthusiasts! 🔥",
            "LOL, nice try! 😂 How about we redirect that energy? Our **Nice Dreamz Fogger** literally pushes vapor to you - effortless hits, no weird requests needed!",
            "That's... definitely a request! 🤣 Tell you what - our hemp clothing is pretty comfy. Maybe check out the **hemp boxers** for ultimate comfort instead?",
        ]

        response = random.choice(jokes)
        response += """

**Here's what I CAN help with:**
- 🔥 Vaporizers for concentrates or flower
- 👕 Comfy hemp clothing
- 🏺 UV glass storage jars
- 🔧 Troubleshooting your devices

🛒 Shop: https://ineedhemp.com
📧 Questions? Email matt@ineedhemp.com"""
        return response

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
