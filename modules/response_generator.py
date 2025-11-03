#!/usr/bin/env python3
"""
Response Generator - Builds intelligent prompts for the LLM
UPDATED VERSION - Stricter URL enforcement, filters spare parts unless asked
"""

from typing import Dict, List
from modules.product_search import ProductSearch
from modules.query_classifier import QueryClassifier
from modules.knowledge_base import KnowledgeBase

class ResponseGenerator:
    def __init__(self, products_json_path: str):
        self.search = ProductSearch(products_json_path)
        self.classifier = QueryClassifier()
        self.kb = KnowledgeBase()
        print("✓ Response Generator initialized")
    
    def build_product_context(self, products: List[Dict], max_products: int = 8) -> str:
        if not products:
            return """=== NO PRODUCTS FOUND ===
⚠️ ⚠️ ⚠️ CRITICAL WARNING ⚠️ ⚠️ ⚠️

NO matching products found in our catalog of 134 products.

YOU MUST RESPOND:
"I don't see that specific item in our catalog. Can you tell me more about what you're looking for? Or I can show you our main product categories:
- V5 & Cub (concentrate atomizers)
- Core 2.0 Deluxe (eRigs)  
- Ruby Twist & Gen 2 DC (dry herb)
- Lightning Pen (portable)
- Glass accessories
- Hemp clothing
- UV glass jars"

DO NOT INVENT ANY PRODUCTS. DO NOT MAKE UP LINKS. DO NOT CREATE FAKE DESCRIPTIONS.
"""
        
        context = "=== AVAILABLE PRODUCTS (COPY THESE EXACT URLS!) ===\n\n"
        context += "⚠️⚠️⚠️ CRITICAL INSTRUCTION: Every product below has TWO things you MUST copy EXACTLY:\n"
        context += "1. PRODUCT NAME (copy character-for-character)\n"
        context += "2. URL (copy the ENTIRE url exactly as shown)\n\n"
        
        for i, p in enumerate(products[:max_products], 1):
            context += f"{i}. PRODUCT NAME: {p['name']}\n"
            context += f"   URL: {p['url']}\n"
            context += f"   ⚠️ When mentioning this product, write: [{p['name']}]({p['url']})\n"
            context += f"   PRICE: {p['price']}\n"
            desc = p.get('full_description', '')[:400].strip()
            if desc:
                context += f"   DESCRIPTION: {desc}\n"
            if any(word in p['name'].lower() for word in ['kit', 'bundle', 'complete']):
                context += f"   ✅ COMPLETE KIT (recommend first!)\n"
            if any(word in p['name'].lower() for word in ['replacement', 'spare']):
                context += f"   🔧 REPLACEMENT PART (only mention if asked for parts)\n"
            context += "\n"
        
        context += "\n🚨 URL ENFORCEMENT RULES 🚨\n"
        context += f"• These are the ONLY {len(products)} products you can mention\n"
        context += "• You MUST use the EXACT url shown above for each product\n"
        context += "• DO NOT modify, shorten, or change any URL\n"
        context += "• DO NOT use the same URL for multiple different products\n"
        context += "• If you mention a product, it MUST be from this list with its EXACT URL\n"
        context += "• Format: [EXACT PRODUCT NAME FROM ABOVE](EXACT URL FROM ABOVE)\n\n"
        return context
    
    def build_system_prompt(self, query: str, classification: Dict, product_context: str) -> str:
        intent = classification['intent']
        
        base = f"""You are the AI assistant for Divine Tribe Vaporizers (ineedhemp.com).

=== ANTI-HALLUCINATION RULES (ABSOLUTELY CRITICAL!) ===
⚠️ NEVER MENTION: Storz & Bickel, Mighty, Crafty, Pax, DynaVap, Grasshopper, Firefly, Arizer, Volcano, Sticky Brick, Flowermate, Boundless, Puffco, or ANY other brand
⚠️ ONLY mention products listed in "AVAILABLE PRODUCTS" section below
⚠️ If AVAILABLE PRODUCTS says "No matching products", you MUST say: "I don't see that specific item in our catalog. Can you describe what you're looking for?"
⚠️ DO NOT invent product names, URLs, prices, specifications, or emojis
⚠️ DO NOT create numbered lists of products not in AVAILABLE PRODUCTS
⚠️ Every product name MUST come from AVAILABLE PRODUCTS - copy it EXACTLY
⚠️ Every URL MUST come from AVAILABLE PRODUCTS - copy it EXACTLY

=== HOW TO USE PRODUCT DATA ===
1. Read the AVAILABLE PRODUCTS section carefully
2. Find products that match the user's query
3. Copy EXACT product name from "PRODUCT NAME:" field
4. Copy EXACT URL from "URL:" field - DO NOT MODIFY IT
5. Use info from "DESCRIPTION:" field to answer questions
6. Format as: [EXACT PRODUCT NAME](EXACT URL)

Example:
If AVAILABLE PRODUCTS shows:
"PRODUCT NAME: Divine Crossing v5 Rebuildable Concentrate Heater
URL: https://ineedhemp.com/product/divine-crossing-v5-rebuildable-concentrate-ceramic-heater/
DESCRIPTION: Pure ceramic heater with side and bottom heating..."

You write:
[Divine Crossing v5 Rebuildable Concentrate Heater](https://ineedhemp.com/product/divine-crossing-v5-rebuildable-concentrate-ceramic-heater/)
This features pure ceramic heating with side and bottom heat for exceptional flavor.

🚨 CRITICAL: Each product has a DIFFERENT URL. Never reuse the same URL for different products!

=== MANDATORY LINK FORMAT ===
🔗 EVERY product mention MUST use this exact format: [Product Name](url)
✅ CORRECT: [XL Deluxe Core eRig Kit](https://ineedhemp.com/product/xl-deluxe-core-erig-kit/)
❌ WRONG: XL Deluxe Core eRig Kit (no link)
❌ WRONG: **XL Deluxe Core eRig Kit** (bold but no link)
❌ WRONG: [XL Deluxe Core eRig Kit](https://ineedhemp.com/product/core/) (wrong URL!)

Copy the EXACT product name and URL from the AVAILABLE PRODUCTS section.

=== OUR PRODUCT CATEGORIES ===

⚠️ CRITICAL: ONLY 3 PRODUCTS ARE FOR DRY HERB - ALL OTHERS ARE FOR CONCENTRATES ONLY ⚠️

DRY HERB VAPORIZERS (ONLY THESE THREE):
• Ruby Twist (ball vape - premium desktop) - DRY HERB ONLY
• Gen 2 DC (ceramic rebuildable) - DRY HERB ONLY
• Thermal Twist (ball-less desktop) - DRY HERB ONLY

CONCENTRATE VAPORIZERS (ALL OTHERS):
• V5 (BEST for concentrates - pure ceramic pathway, no metal in vapor path)
• Core 2.0 Deluxe (eRig for CONCENTRATES - 6 heat settings, all models: 2.0, 2.1, XL, XL Deluxe)
• Nice Dreamz Fogger (CONCENTRATES - stainless steel edition)
• Cub (adapter for Core/Nice Dreamz/TUG owners ONLY - cleans coils + reads resistance) - CONCENTRATES
• Lightning Pen (CONCENTRATES - most portable, standalone ONLY, never use on mod)
• TUG 2.0 (CONCENTRATES e-rig)
• V4/V4.5 (CONCENTRATES - older generation)

⚠️ NEVER say Core, V5, Lightning Pen, Nice Dreamz, or TUG work with dry herb - CONCENTRATES ONLY!

⚠️ IF CUSTOMER ASKS "Does V5 work with flower/dry herb?" → Answer: "No, the V5 is for concentrates only. For dry herb/flower, you need the Ruby Twist, Thermal Twist, or Gen 2 DC."

⚠️ V5 does NOT work with flower, even with bottomless banger. V5 = CONCENTRATES ONLY.

=== CUB ADAPTER RULES (CRITICAL!) ===
⚠️ ONLY mention Cub if customer has: Core, Nice Dreamz, or TUG
⚠️ DO NOT mention Cub for: V5, V4, Lightning Pen, Ruby Twist, or general questions
⚠️ Cub is ONLY for cleaning Core/Nice Dreamz/TUG coils and reading resistance

When customer HAS Core/Nice Dreamz/TUG and has issues:
1. **Recommend Cub adapter** - ONLY way to clean their coils back to white
2. **Cub reads resistance** - helps diagnose coil issues (normal: 0.42-0.51Ω)
3. Say: "The Cub is essential for Core/Nice Dreamz/TUG owners"
4. Provide link to: [The Cub Base Adapter](url from AVAILABLE PRODUCTS)

=== BROKEN/CRACKED GLASS POLICY ===
When customer mentions broken, cracked, or damaged glass (tops, bubblers, hydratubes, etc.):
1. Ask them to email a photo to: matt@ineedhemp.com
2. Say: "Please send a photo of the damage to matt@ineedhemp.com and we'll take care of you"
3. Mention: "We usually replace broken glass in most cases"
4. DO NOT promise replacement without seeing photo first
5. Be empathetic and helpful

=== REPLACEMENT PARTS STRATEGY ===
• All devices have cheap replacement parts
• Search AVAILABLE PRODUCTS for exact part needed
• Provide direct links
• Mention discount code

=== DISCOUNT CODE ===
Code: {self.kb.discount_code} = {self.kb.discount_amount}
⚠️ ONLY mention discount code ONCE per conversation - check if it's already in conversation history before mentioning it again!

=== COMMUNITY ===
Discord: {self.kb.discord_url}
Reddit: {self.kb.reddit_url}
Email: {self.kb.support_email}

"""
        
        if intent == 'troubleshooting':
            base += """
=== TROUBLESHOOTING PRIORITY ===
1. **Check lead wires** in screw holes (must be visible - 90% of issues!)
2. **Check resistance** (0.42-0.51Ω at room temp)
3. **For Core/Nice Dreamz/TUG issues ONLY**: Recommend Cub adapter with link
4. Clean with isopropyl alcohol
5. Check heater condition
6. **For broken/cracked glass**: Ask them to email photo to matt@ineedhemp.com (we usually replace)
7. NEVER suggest buying new device - always try fixes first
8. End with: Community links for real-time help

⚠️ DO NOT mention Cub unless customer specifically mentions having Core, Nice Dreamz, or TUG

REMEMBER: Format all product recommendations as [Product Name](url)
"""
        
        elif intent == 'recommendation':
            base += f"""
=== RECOMMENDATION PRIORITY ===

**For Beginners:** {self.kb.get_beginner_recommendation()}

**V5 vs Cub Decision (CRITICAL):**
ONLY recommend Cub if customer explicitly states they have Core, Nice Dreamz, or TUG.

If customer has Core/Nice Dreamz/TUG:
• Recommend: [The Cub Base Adapter](url) - ESSENTIAL! Only way to clean their coils + reads resistance

If customer does NOT have Core/Nice Dreamz/TUG:
• Recommend: [Divine Crossing v5](url) - Pure ceramic, no metal, best standalone option

**Purest Flavor:** V5 + Glass Vortex Top (ceramic + glass only, zero metal)

**Dry Herb Options:**
• Desktop: Ruby Twist (ball vape) or Thermal Twist (ball-less)
• Portable: Gen 2 DC

**Concentrate Options:**
• Most Portable: Lightning Pen
• Best Overall: Core 2.0 Deluxe
• Purest: V5
• Budget: V4

**International Customers:**
• V5 kit is modular and easy to transport
• Pico Plus mod recommended
• Mention spare parts availability
• UPS shipping preferred

ALWAYS format as: [Product Name](url)
ALWAYS mention code: {self.kb.discount_code}
"""
        
        elif intent == 'parts':
            base += """
=== SPARE PARTS PRIORITY ===
1. Find EXACT part from AVAILABLE PRODUCTS
2. Format as: [Replacement Part Name](url)
3. Mention: "All parts sold very cheap"
4. Provide price from AVAILABLE PRODUCTS
5. Include discount code
6. For broken parts: ask if it broke during normal use or specific incident

Common parts:
• Quartz cups (V4)
• Ceramic cups (V5, Nice Dreamz)
• Heater coils (all devices)
• O-rings (all devices)
• Glass tops (Core, V5, Cub)

REMEMBER: Format all parts as [Part Name](url)
"""
        
        elif intent == 'compatibility':
            base += """
=== COMPATIBILITY INFO ===
• V5: Works with bottomless bangers → any glass rig
• Cub: Works with bottomless bangers + cleans Core coils + reads resistance
• Core (ALL models): Get Cub adapter - ESSENTIAL for cleaning!
• Lightning Pen: ⚠️ STANDALONE ONLY - never use on mod!
• Nice Dreamz: XL cups, requires Cub for cleaning
• V4: Works with bottomless bangers

REMEMBER: Format all products as [Product Name](url)
"""
        
        elif intent == 'pricing':
            base += f"""
=== PRICING PRIORITY ===
1. Show EXACT prices from AVAILABLE PRODUCTS
2. Format as: [Product Name](url) - $XX.XX
3. ALWAYS mention: Use code **{self.kb.discount_code}** for {self.kb.discount_amount}!
4. Mention: Kits save money vs buying parts separately
5. International shipping: UPS available

REMEMBER: Format all products as [Product Name](url)
"""
        
        elif intent == 'light_offtopic':
            base += """
=== LIGHT OFF-TOPIC (HUMOR MODE ACTIVATED!) ===
The user asked about something unrelated but not serious (sports, weather, movies, food, etc.)

RESPONSE STRATEGY:
1. **Brief playful acknowledgment** (1-2 sentences max)
2. **Make a light connection** to Divine Tribe products
3. **Recommend 1-2 products** with links: [Product Name](url)
4. **Include discount code** naturally

EXAMPLES OF GOOD RESPONSES:
User: "What's the weather like?"
Response: "I don't track weather, but if it's cold out, at least your concentrates stay fresh! Speaking of staying warm, check out the [Core 2.0 Deluxe eRig](url) for cozy indoor sessions. Use code thankyou10 for 10% off!"

User: "Who won the game last night?"
Response: "No idea about the game, but sounds like you need to celebrate or drown your sorrows! The [Lightning Pen](url) is perfect for portable victory laps. Code thankyou10 for 10% off!"

User: "What movie should I watch?"
Response: "Can't help with movies, but for your next viewing party, the [Nice Dreamz Fogger](url) creates some seriously cinematic vapor clouds! Use thankyou10 for 10% off."

User: "I'm hungry, what should I eat?"
Response: "Can't cook for you, but the [V5 Heater](url) will definitely satisfy your other cravings! Check it out. Code thankyou10 saves you 10%."

Keep it SHORT (3-4 sentences max), FUN, and always pivot to products with proper [Product Name](url) links.
"""
        
        elif intent == 'off_topic':
            base += """
=== OFF-TOPIC RESPONSE ===
1. Brief humorous acknowledgment
2. Pivot to relevant Divine Tribe product
3. Format as: [Product Name](url)
4. Include discount code
"""
        
        base += f"\n{product_context}\n"
        
        # Add community links for help queries
        help_keywords = ['help', 'question', 'how', 'should', 'recommend', 'problem', 'issue', 'broken', 'not working']
        if any(word in query.lower() for word in help_keywords):
            base += f"\n💬 For real-time help: Discord: {self.kb.discord_url} | Reddit: {self.kb.reddit_url}\n"
        
        base += """
=== FINAL CRITICAL REMINDERS ===
1. ✅ ALWAYS format products as: [Product Name](url)
2. ✅ Copy EXACT names and URLs from AVAILABLE PRODUCTS above
3. ✅ NEVER use the same URL for different products
4. ✅ Use DESCRIPTION field to answer questions accurately
5. ✅ Mention discount code: thankyou10
6. ❌ NEVER invent product names - they must be in AVAILABLE PRODUCTS
7. ❌ NEVER invent URLs - they must be in AVAILABLE PRODUCTS
8. ❌ NEVER reuse URLs for different products
9. ❌ NEVER mention other brands (Pax, Mighty, etc.)
10. ❌ NEVER create product lists not in AVAILABLE PRODUCTS
11. ❌ NEVER add emojis to product names (🚀🌱 etc.)
12. ❌ If AVAILABLE PRODUCTS is empty, say you don't have that item

Your response will be formatted to make product links bold and underlined automatically.
Just use the [Product Name](url) format with EXACT data from AVAILABLE PRODUCTS.

Help the customer with accurate information from our 134 products only. Be specific and helpful.
"""
        
        return base
    
    def generate_context(self, user_query: str) -> Dict:
        classification = self.classifier.classify(user_query)
        intent = classification['intent']
        
        # Expanded product-related keywords - if ANY of these are in query, we MUST search
        product_keywords = [
            # Vape products
            'v5', 'v4', 'v3', 'core', 'lightning', 'ruby', 'cub', 'nice dreamz', 'fogger', 'tug',
            'gen 2', 'thermal twist', 'ball vape', 'dry herb', 'herb', 'flower',
            # Product types
            'vape', 'vaporizer', 'atomizer', 'heater', 'coil', 'erig', 'e-rig', 'enail', 'e-nail',
            'pen', 'mod', 'battery', 'pico', 'istick',
            # Parts and accessories
            'glass', 'top', 'cup', 'crucible', 'bucket', 'quartz', 'ceramic', 'sic', 'silicon carbide',
            'titanium', 'carb cap', 'banger', 'bubbler', 'hydratube', 'recycler', 'vortex',
            'o-ring', 'oring', 'replacement', 'spare', 'part', 'tool', 'dab tool',
            'coil', 'heater coil', 'flex coil', 'gooseneck',
            # Clothing
            'hoodie', 'shirt', 't-shirt', 'tshirt', 'clothing', 'pants', 'cargo', 'boxers', 'shorts',
            'hemp clothing', 'hemp shirt', 'fleece',
            # Containers
            'jar', 'jars', 'container', 'glass jar', 'uv glass', 'storage',
            # General product queries
            'kit', 'bundle', 'package', 'complete', 'deluxe', 'xl',
            'product', 'products', 'sell', 'have', 'buy', 'purchase', 'order',
            'main', 'popular', 'best', 'recommend', 'what do you',
            # Specific issues
            'broken', 'crack', 'leak', 'resistance', 'ohm', 'not working', 'issue', 'problem'
        ]
        
        # Check if query contains ANY product-related keywords
        query_lower = user_query.lower()
        is_product_related = any(keyword in query_lower for keyword in product_keywords)
        
        # Also check intent-based triggers
        search_intents = ['product_inquiry', 'recommendation', 'parts', 'compatibility', 'pricing', 'troubleshooting']
        should_search = intent in search_intents or is_product_related
        
        products = []
        if should_search:
            # ALWAYS search when product-related
            products = self.search.search(user_query, max_results=8)
            
            # If no products found but query was product-related, that's critical info
            if not products and is_product_related:
                print(f"⚠️ WARNING: Product query '{user_query}' returned no results!")
        
        product_context = self.build_product_context(products)
        system_prompt = self.build_system_prompt(user_query, classification, product_context)
        
        return {
            'system_prompt': system_prompt,
            'classification': classification,
            'products': products,
            'intent': intent,
            'confidence': classification['confidence'],
            'is_product_query': is_product_related
        }
    
    def get_quick_response(self, user_query: str) -> str:
        """Quick responses for simple queries - including hard-coded empathy for serious topics"""
        query_lower = user_query.lower().strip()
        
        # Check for order cancellation FIRST
        if 'cancel' in query_lower and 'order' in query_lower:
            return self._handle_order_cancellation(user_query)
        
        # Check for inappropriate queries (DMT, drugs, etc)
        if any(word in query_lower for word in ['dmt', 'freebas', 'freebase', 'drug', 'illegal']):
            return self._handle_inappropriate(user_query)
        
        # Check for flower/dry herb questions about wrong products
        if any(word in query_lower for word in ['flower', 'dry herb', 'herb', 'bud', 'cannabis flower']):
            # List of products that are CONCENTRATES ONLY
            concentrate_products = ['v5', 'core', 'cub', 'lightning', 'nice dreamz', 'nice dreams',
                                   'tug', 'v4', 'bottomless banger', 'banger']
            
            # If asking about any concentrate product with flower/herb
            if any(product in query_lower for product in concentrate_products):
                return self._handle_flower_question(user_query)
        
        # Check for serious topics - return empathy response immediately (no AI)
        classification = self.classifier.classify(user_query)
        
        if classification.get('is_serious'):
            # HARD-CODED EMPATHY RESPONSE - No AI, no sales, pure human compassion
            return self._get_empathy_response(user_query)
        
        # No other quick responses - let LLM handle everything else
        return None
    
    def _handle_flower_question(self, query: str) -> str:
        """Handle flower/dry herb questions - only Ruby Twist, Thermal Twist, and Gen 2 DC work"""
        return (
            "No, that product is for concentrates only. For dry herb/flower, you need one of these:\n\n"
            "• **[Dual Controller Wired & Wireless Ruby Twist Ball Vape](https://ineedhemp.com/product/dual-controller-wired-and-wireless-ruby-twist-ball-vape/)** - Premium desktop\n"
            "• **[Thermal Twist Injector (Ball-less)](https://ineedhemp.com/product/thermal-twist-injector-ball-less-dry-herb-desktop-option-kits-and-parts/)** - Ball-less desktop\n"
            "• **[Gen 2 DC Ceramic Rebuildable Dry Herb Heater](https://ineedhemp.com/product/gen-2-dc-ceramic-rebuildable-dry-herb-heater/)** - Portable option\n\n"
            "These are the ONLY Divine Tribe products that work with dry herb. All other products (V5, Core, Lightning Pen, etc.) are for concentrates only.\n\n"
            "Use code **thankyou10** for 10% off!"
        )
    
    def _get_empathy_response(self, query: str) -> str:
        """
        Hard-coded empathy responses for serious topics
        OLD SCHOOL - No AI, just predetermined compassionate responses
        """
        query_lower = query.lower()
        
        # Detect specific serious topic types
        if any(word in query_lower for word in ['suicide', 'suicidal', 'kill myself', 'kill themselves', 'end my life', 'want to die']):
            return """I'm so sorry you're going through this difficult time. What you're experiencing matters, and there are people who want to help.

**Immediate Support:**
• **988 Suicide & Crisis Lifeline** (US): Call or text 988
• **Crisis Text Line**: Text HOME to 741741
• **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/

Please reach out to someone you trust, or contact one of these resources. You don't have to face this alone.

If you need help with vaping products another time, I'm here. But right now, please focus on getting support. Take care."""

        elif any(word in query_lower for word in ['died', 'death', 'passed away', 'funeral', 'grief', 'mourning']):
            return """I'm truly sorry for your loss. Grief is one of the hardest things we go through, and there's no right way to process it.

If you need support:
• **GriefShare**: https://www.griefshare.org (grief support groups)
• **National Alliance for Grieving Children**: https://childrengrieve.org
• Consider talking to a counselor or trusted friend

Please take all the time you need. If there's anything I can help with regarding Divine Tribe products in the future, I'm here. But for now, take care of yourself."""

        elif any(word in query_lower for word in ['depressed', 'depression', 'hopeless', 'can\'t go on']):
            return """I hear you, and I'm sorry you're feeling this way. Depression can make everything feel overwhelming, but you don't have to face it alone.

**Resources that can help:**
• **988 Suicide & Crisis Lifeline**: Call or text 988
• **SAMHSA National Helpline**: 1-800-662-4357 (free, confidential, 24/7)
• **Psychology Today Therapist Finder**: https://www.psychologytoday.com/us/therapists

Please consider reaching out to a mental health professional or someone you trust. You deserve support.

If you need help with products another time, I'm here. Take care of yourself."""

        elif any(word in query_lower for word in ['cancer', 'terminal', 'illness', 'hospital', 'dying']):
            return """I'm so sorry you or someone you care about is going through this. Facing serious illness is incredibly difficult.

**Support Resources:**
• **CancerCare**: 1-800-813-4673 (free counseling and support)
• **American Cancer Society**: 1-800-227-2345
• **CaringBridge**: https://www.caringbridge.org (connect with loved ones)

Please lean on your support system and medical team during this time. If there's anything I can help with regarding our products later, I'm here. Wishing you strength."""

        else:
            # General serious topic response
            return """I hear that you're going through something difficult. Please know that support is available:

**Crisis Support:**
• **988 Suicide & Crisis Lifeline**: Call or text 988
• **Crisis Text Line**: Text HOME to 741741
• **SAMHSA National Helpline**: 1-800-662-4357

If you're in crisis, please reach out to one of these resources or call 911. You don't have to face this alone.

Take care of yourself. I'm here if you need help with Divine Tribe products another time."""

    def _handle_order_cancellation(self, query: str) -> str:
        """Handle order cancellation - Matt's template"""
        return (
            "Sorry to hear this! No problem - please email us at matt@ineedhemp.com "
            "with your order details and we will cancel and refund right away. "
            "Thanks, Matt"
        )
    
    def _handle_inappropriate(self, query: str) -> str:
        """Handle DMT and inappropriate queries - Matt's template"""
        return (
            "Believe it or not, we get this question asked a lot. Due to regulations and legal issues, "
            "we cannot help you with this. However, we hope you can find all the information you need "
            "from online communities - there's a ton of resources which will show you exactly what products "
            "to buy from whoever you choose."
        )
