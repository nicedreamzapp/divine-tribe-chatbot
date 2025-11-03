#!/usr/bin/env python3
"""
FIXED smart_responder.py - Better handling for batteries, cables, damaged products
"""

import json
import re
from typing import Dict, List, Optional

class SmartResponder:
    """Enhanced response generator with recommendations"""
    
    def __init__(self, json_file='products_organized.json'):
        self.json_file = json_file
        self.recommendations = {
            "beginner": {
                "product": "Core Deluxe",
                "reason": "easiest to use with 6 pre-set temperatures, portable, complete kit",
                "link": "https://ineedhemp.com/product/core-deluxe/"
            },
            "flavor": {
                "product": "V5 XL",
                "reason": "#1 for pure flavor with ceramic side and bottom heating",
                "link": "https://ineedhemp.com/product/v5-xl/"
            },
            "portable": {
                "product": "V5 XL or Core Deluxe",
                "reason": "V5 XL is ultra-portable with mod, Core Deluxe is all-in-one portable",
                "link": "https://ineedhemp.com"
            },
            "powerful": {
                "product": "Ruby Twist Ball Vape",
                "reason": "desktop ball vape with dual controllers for maximum power",
                "link": "https://ineedhemp.com/product/ruby-twist/"
            }
        }
    
    def generate_response(self, user_message, intent_data, session_id=None, context=None):
        """
        Generate response - signature matches original chatbot
        """
        query = user_message
        intent = intent_data.get('intent', 'general') if isinstance(intent_data, dict) else intent_data
        query_lower = query.lower()
        
        # NEW: Handle specific accessory questions FIRST
        if self._is_battery_query(query_lower):
            return self._handle_battery_query()
        
        if self._is_cable_query(query_lower):
            return self._handle_cable_query()
        
        # NEW: Handle damage/return queries
        if self._is_damage_query(query_lower):
            return self._generate_support_response(query_lower)
        
        # Handle recommendation requests
        if self._is_recommendation_request(query_lower):
            return self._generate_recommendation(query_lower)
        
        # Search for products based on query
        from modules.product_database import ProductDatabase
        db = ProductDatabase(self.json_file)
        products = db.search(query, max_results=5)
        
        # Handle product info requests
        if intent == "product_info":
            if products:
                return self._format_product_results(products, query_lower)
            else:
                return self._no_products_found(query_lower)
        
        # Handle pricing
        if intent == "pricing":
            if products:
                return self._format_pricing(products)
            return "Check ineedhemp.com for current pricing and availability."
        
        # Handle comparisons
        if intent == "comparison":
            return self._generate_comparison(query_lower, products)
        
        # Handle support
        if intent == "support":
            return self._generate_support_response(query_lower)
        
        # Handle shopping intent
        if intent == "shopping":
            if "beginner" in query_lower or "first" in query_lower or "start" in query_lower:
                return self._recommend_beginner()
            return self._generate_shopping_response(products)
        
        # Handle technical
        if intent == "tech_specs":
            return self._generate_tech_response(query_lower)
        
        # Handle greetings
        if intent == "greeting":
            return "👋 Hi! I can help you find Divine Tribe products or answer questions. What are you looking for?"
        
        # Handle follow-ups
        if intent == "follow_up":
            return self._handle_follow_up(query_lower, context)
        
        # Default fallback
        return "I can help you find Divine Tribe vaporizers! Try asking about the V5 XL (best flavor), Core Deluxe (easiest), or Ruby Twist (desktop power)."
    
    def _is_battery_query(self, query: str) -> bool:
        """Check if asking about batteries"""
        return "batter" in query or "power supply" in query or "18650" in query
    
    def _handle_battery_query(self) -> str:
        """Handle battery questions"""
        return ("🔋 **Battery Options:**\n\n"
                "• **V5 XL** - Use any 18650-compatible 510 mod (Pico recommended)\n"
                "• **Core Deluxe** - Built-in rechargeable battery included!\n\n"
                "Most customers get the **Pico Plus mod** (75W) which comes with our bundles.\n\n"
                "[Shop Mods](https://ineedhemp.com)")
    
    def _is_cable_query(self, query: str) -> bool:
        """Check if asking about cables"""
        return ("510" in query and "cable" in query) or "extension cable" in query or "510 extension" in query
    
    def _handle_cable_query(self) -> str:
        """Handle 510 cable questions"""
        return ("🔌 **510 Extension Cables:**\n\n"
                "Check the accessories section on ineedhemp.com for 510 cables and adapters.\n\n"
                "Or email matt@ineedhemp.com for specific cable recommendations!")
    
    def _is_damage_query(self, query: str) -> bool:
        """Check if reporting damage/issues"""
        damage_words = ['damaged', 'arrived broken', 'wrong item', 'missing', 'refund']
        return any(word in query for word in damage_words)
    
    def _is_recommendation_request(self, query: str) -> bool:
        """Detect if user is asking for a recommendation"""
        patterns = [
            r"what should i (buy|get|purchase)",
            r"(recommend|suggestion)",
            r"best (for|product)",
            r"which (one|product)",
            r"(beginner|new|first time)",
            r"most (portable|powerful|easy)",
            r"easiest to use",
            r"top (pick|choice)",
            r"good for flavor",
            r"popular"
        ]
        return any(re.search(pattern, query) for pattern in patterns)
    
    def _generate_recommendation(self, query: str) -> str:
        """Generate product recommendation based on query"""
        
        # Beginner recommendations
        if any(word in query for word in ["beginner", "new", "first", "start", "easy", "easiest"]):
            return self._recommend_beginner()
        
        # Flavor recommendations
        if any(word in query for word in ["flavor", "taste", "terp"]):
            rec = self.recommendations["flavor"]
            return (f"🏆 For the **best flavor**, go with the **{rec['product']}**!\n\n"
                   f"Why? {rec['reason']}. Pure ceramic means you taste nothing but your concentrate.\n\n"
                   f"[Shop {rec['product']}]({rec['link']})")
        
        # Portable recommendations
        if any(word in query for word in ["portable", "travel", "small", "compact"]):
            return ("📱 **Most Portable Options:**\n\n"
                   "• **V5 XL** - Ultra-compact with any 510 mod\n"
                   "• **Core Deluxe** - All-in-one portable eRig\n\n"
                   "V5 XL is smaller but needs a mod. Core is ready to go.\n\n"
                   "[Compare on site](https://ineedhemp.com)")
        
        # Power recommendations
        if any(word in query for word in ["powerful", "strong", "desktop", "ball vape"]):
            rec = self.recommendations["powerful"]
            return (f"⚡ For **maximum power**, the **{rec['product']}** is king!\n\n"
                   f"{rec['reason']}.\n\n"
                   f"[Shop {rec['product']}]({rec['link']})")
        
        # Popular/general recommendation
        if any(word in query for word in ["popular", "best", "top", "recommend"]):
            return ("🌟 **Top Divine Tribe Products:**\n\n"
                   "1. **V5 XL** - #1 for pure flavor, ceramic perfection\n"
                   "2. **Core Deluxe** - Easiest to use, perfect for beginners\n"
                   "3. **Ruby Twist** - Desktop power with ball vape technology\n\n"
                   "What matters most to you - flavor, ease, or power?")
        
        # Default recommendation
        return self._recommend_beginner()
    
    def _recommend_beginner(self) -> str:
        """Recommend product for beginners"""
        rec = self.recommendations["beginner"]
        return (f"👋 **New to Divine Tribe? Start with the Core Deluxe!**\n\n"
               f"✅ {rec['reason']}\n"
               f"✅ No learning curve - just turn on and go\n"
               f"✅ Includes everything you need\n\n"
               f"[Shop Core Deluxe]({rec['link']})")
    
    def _format_product_results(self, products: List[Dict], query: str) -> str:
        """Format product search results"""
        
        if not products:
            return self._no_products_found(query)
        
        # Check if asking about specific product
        is_specific = any(term in query for term in ["what is", "tell me about", "show me"])
        
        if is_specific and len(products) == 1:
            # Detailed single product response
            p = products[0]
            return (f"**{p['name']}**\n\n"
                   f"{p.get('short_description', 'Premium Divine Tribe product')}\n\n"
                   f"[View Product]({p['url']})")
        
        # Multiple products or list response
        response = "Found:\n\n"
        for i, product in enumerate(products[:5], 1):
            response += f"{i}. **{product['name']}**\n   [View]({product['url']})\n\n"
        
        if len(products) > 5:
            response += f"...and {len(products) - 5} more on [ineedhemp.com](https://ineedhemp.com)"
        
        return response.strip()
    
    def _no_products_found(self, query: str) -> str:
        """Response when no products match search"""
        
        # Check what they're looking for
        if "battery" in query or "batteries" in query:
            return self._handle_battery_query()
        
        if "510" in query and "cable" in query:
            return self._handle_cable_query()
        
        if "quartz" in query:
            return ("🏺 Divine Tribe specializes in **ceramic and SiC cups** for pure flavor.\n\n"
                   "Quartz options may be available - check ineedhemp.com or ask matt@ineedhemp.com")
        
        # Generic not found
        return ("Couldn't find that exact item. Try:\n"
               "• **V5 XL** - best flavor\n"
               "• **Core Deluxe** - easiest to use\n"
               "• **Ruby Twist** - desktop power\n\n"
               "Or search on [ineedhemp.com](https://ineedhemp.com)")
    
    def _format_pricing(self, products: List[Dict]) -> str:
        """Format pricing information"""
        if not products:
            return "Check ineedhemp.com for current pricing."
        
        p = products[0]
        price = p.get('price_display', 'Check website')
        return f"**{p['name']}**: {price}\n\n[Buy Now]({p['url']})"
    
    def _generate_comparison(self, query: str, products: List[Dict] = None) -> str:
        """Generate product comparisons"""
        
        # V5 vs Core
        if "v5" in query and "core" in query:
            return ("**V5 XL vs Core Deluxe:**\n\n"
                   "**V5 XL:**\n"
                   "✅ #1 for pure flavor (ceramic)\n"
                   "✅ Ultra-portable\n"
                   "✅ Rebuildable\n"
                   "❌ Needs separate mod\n\n"
                   "**Core Deluxe:**\n"
                   "✅ Easiest to use (6 preset temps)\n"
                   "✅ All-in-one (built-in battery)\n"
                   "✅ Perfect for beginners\n"
                   "❌ Less customizable\n\n"
                   "Flavor? V5. Ease? Core.")
        
        # SiC vs Ti vs Ceramic
        if any(term in query for term in ["sic", "titanium", "ceramic", "cup"]):
            return ("**Cup Materials:**\n\n"
                   "• **Ceramic** (V5 XL) - Purest flavor, best taste\n"
                   "• **SiC** - Fast heating, very durable\n"
                   "• **Titanium** - Long-lasting, efficient\n\n"
                   "For flavor chasers: Ceramic wins. For convenience: SiC or Ti.")
        
        # Generic comparison
        return "For detailed comparisons, check specs at ineedhemp.com or email matt@ineedhemp.com"
    
    def _generate_support_response(self, query: str) -> str:
        """Generate support-related responses"""
        
        # Returns/refunds/damage
        if any(word in query for word in ["return", "refund", "send back", "broken", "damaged", "wrong", "arrived"]):
            return ("📧 **Returns & Warranty:**\n\n"
                   "Email **matt@ineedhemp.com** with:\n"
                   "• Your order number\n"
                   "• Photos of the issue\n"
                   "• Description of the problem\n\n"
                   "Matt handles all returns, replacements, and warranty claims directly.")
        
        # Cleaning
        if "clean" in query:
            return ("🧼 **Cleaning Tips:**\n\n"
                   "• Use 99% isopropyl alcohol\n"
                   "• Soak coils/cups in ISO\n"
                   "• Avoid water on electronics\n"
                   "• Clean connections regularly\n\n"
                   "Full guides at ineedhemp.com/guides")
        
        # Troubleshooting
        if any(word in query for word in ["won't fire", "not working", "no vapor", "error"]):
            return ("🔧 **Quick Troubleshooting:**\n\n"
                   "1. Check coil is tight\n"
                   "2. Lock resistance when cold\n"
                   "3. Verify temp control mode (Ni200)\n"
                   "4. Clean all connections\n\n"
                   "Still stuck? Email matt@ineedhemp.com with details!")
        
        # Generic support
        return ("📧 **Need Support?**\n\n"
               "Email matt@ineedhemp.com with your question and order number.\n"
               "Response usually within 24 hours!")
    
    def _generate_shopping_response(self, products: List[Dict] = None) -> str:
        """Generate shopping/browsing responses"""
        if products:
            return self._format_product_results(products, "")
        return "Browse all products at [ineedhemp.com](https://ineedhemp.com)"
    
    def _generate_tech_response(self, query: str) -> str:
        """Generate technical specification responses"""
        
        if "firmware" in query or "arctic fox" in query:
            return ("**Firmware Info:**\n\n"
                   "• Download Arctic Fox from ineedhemp.com/downloads\n"
                   "• Flash using NFE Tools\n"
                   "• Compatible with Pico mods\n\n"
                   "Setup guides available on site!")
        
        if "settings" in query or "temperature" in query or "tcr" in query:
            return ("**Temp Control Settings:**\n\n"
                   "• Mode: Ni200 (TC-Ni)\n"
                   "• Temp: 360-420°F (start low)\n"
                   "• Wattage: 30-35W\n"
                   "• Lock resistance when cold!\n\n"
                   "Full setup guides at ineedhemp.com")
        
        return "For technical specs, visit ineedhemp.com/specs or email matt@ineedhemp.com"
    
    def _handle_follow_up(self, query: str, context: Dict = None) -> str:
        """Handle follow-up questions using context"""
        if context and "last_product" in context:
            return f"Regarding the {context['last_product']}, what would you like to know?"
        return "What would you like to know more about?"


# Convenience function for easy importing
def generate_response(intent: str, query: str, products: List[Dict] = None,
                     context: Dict = None) -> str:
    """Quick response generation"""
    responder = SmartResponder()
    return responder.generate_response(intent, query, products, context)
