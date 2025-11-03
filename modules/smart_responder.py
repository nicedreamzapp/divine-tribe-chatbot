#!/usr/bin/env python3
"""Smart Responder Module - Fixed with proper support handling"""

import json
import random
from typing import Dict, List, Any

class SmartResponder:
    def __init__(self, products_file: str = 'products_organized.json'):
        self.products_file = products_file
        self.load_products()
        
    def load_products(self):
        """Load the organized products"""
        try:
            with open(self.products_file, 'r') as f:
                self.organized_data = json.load(f)
        except:
            self.organized_data = {"categories": {}, "product_index": {}, "search_index": {}}
    
    def search_products(self, query: str) -> List[Dict]:
        """Search for products based on query"""
        query_lower = query.lower()
        found_products = []
        
        for category_name, category_data in self.organized_data.get("categories", {}).items():
            for product in category_data.get("products", []):
                product_name = product.get("name", "").lower()
                if any(word in product_name for word in query_lower.split()):
                    found_products.append(product)
                    if len(found_products) >= 5:
                        break
        
        return found_products[:5]
    
    def generate_response(self, user_message: str, intent_data: Dict, session_id: str, context: Dict = None) -> str:
        """Generate response based on intent and context"""
        intent = intent_data.get('intent', 'general')
        message_lower = user_message.lower()
        
        # SUPPORT HANDLING - CHECK FIRST!
        support_keywords = ['return', 'broken', 'warranty', 'defective', 'refund', 'exchange', 
                          'won\'t work', 'not working', 'stopped working', 'doesn\'t work',
                          'won\'t turn on', 'won\'t charge', 'dead', 'died', 'damaged']
        
        if any(keyword in message_lower for keyword in support_keywords):
            # Returns and refunds
            if any(word in message_lower for word in ['return', 'refund', 'exchange']):
                return """For returns and refunds, please email us at matt@ineedhemp.com with:
- Your order number
- Reason for return
- Photos of the product (if damaged)

We have a 30-day return policy for unused items and will help with any defective products."""

            # Broken/defective products
            elif any(word in message_lower for word in ['broken', 'defective', 'damaged', 'broke']):
                return """I'm sorry to hear your product is damaged! Please email matt@ineedhemp.com with:
- Your order number
- Photos of the damage
- Description of what happened

We'll get you sorted out quickly with a replacement or refund."""

            # Not working/technical issues
            elif any(phrase in message_lower for phrase in ['won\'t work', 'not working', 'won\'t turn on', 
                                                            'stopped working', 'won\'t heat', 'no power']):
                return """Let's troubleshoot your device:

1. Check the battery is charged
2. Clean all connections with isopropyl alcohol
3. Check your settings (TCR: 200, Wattage: 30-37W)
4. Make sure coil is properly connected

Still not working? Email matt@ineedhemp.com with your issue and we'll help fix it or replace it!"""

            # Warranty
            elif 'warranty' in message_lower:
                return """Divine Tribe warranty information:
- Core/Nice Dreamz: 1 year warranty on base unit
- V5 and other heaters: 90 days on heater cups
- Glass: Not covered (fragile item)
- Batteries: 6 months

For warranty claims, email matt@ineedhemp.com with your order info."""

            # Coil/heater issues
            elif any(word in message_lower for word in ['coil', 'heater']) and \
                 any(word in message_lower for word in ['wont', 'not', 'broken']):
                return """For coil/heater issues:
1. Check resistance reading (should be 0.4-0.6 ohms)
2. Tighten the screws (not too tight!)
3. Check for broken wires
4. Try a different mod if possible

Need a replacement? Email matt@ineedhemp.com or check our replacement parts section."""

        # ORDER/SHIPPING ISSUES
        elif any(word in message_lower for word in ['tracking', 'ship', 'order', 'delivery']):
            if 'tracking' in message_lower:
                return "For tracking info, check your email for the shipping confirmation or email matt@ineedhemp.com with your order number."
            elif any(word in message_lower for word in ['never arrived', 'didn\'t arrive', 'lost']):
                return "If your order didn't arrive, please email matt@ineedhemp.com immediately with your order number. We'll track it down or send a replacement."
            else:
                return "For order and shipping questions, email matt@ineedhemp.com with your order number. We ship within 1-2 business days!"

        # GREETINGS
        elif intent == 'greeting':
            greetings = [
                "Hi there! How can I help you with Divine Tribe products today?",
                "Hello! Looking for vaporizers or need support?",
                "Hey! What can I help you find today?"
            ]
            return random.choice(greetings)
        
        # PRODUCT SEARCHES
        elif any(word in message_lower for word in ['show', 'need', 'want', 'looking', 'find']):
            products = self.search_products(user_message)
            if products:
                response = "Here's what I found:\n\n"
                for i, product in enumerate(products[:3], 1):
                    name = product.get('name', 'Unknown Product')
                    url = product.get('url', '#')
                    response += f"{i}. **{name}**\n   [View Product]({url})\n\n"
                return response
        
        # SPECIFIC PRODUCTS
        elif "v5" in message_lower:
            return "The V5 XL is our #1 product for flavor with pure ceramic technology! Visit: https://ineedhemp.com"
        elif "core" in message_lower:
            return "The Core Deluxe eRig is perfect for beginners! It's our upgraded Core with 6 heat settings. Visit: https://ineedhemp.com"
        elif "controller" in message_lower:
            return "Looking for controllers? The Ruby Twist controllers are what you need! Check them out at: https://ineedhemp.com"
        
        # CONTACT/SUPPORT INFO
        elif any(word in message_lower for word in ['contact', 'email', 'support', 'help']):
            return """Contact Divine Tribe:
📧 Email: matt@ineedhemp.com
💬 Reddit: r/DivineTribeVaporizers
🌐 Website: https://ineedhemp.com
Discord: Check our website for invite link"""
        
        # PRICING
        elif any(word in message_lower for word in ['price', 'cost', 'how much', '$']):
            return "For current pricing, please visit our website at https://ineedhemp.com - prices may vary based on current promotions!"
        
        # DEFAULT
        else:
            return "I can help you find products or assist with support issues. Try asking about the V5 XL, Core Deluxe, or if you need help with a problem, just describe what's wrong!"
