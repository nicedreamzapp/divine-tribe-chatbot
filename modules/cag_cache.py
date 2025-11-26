"""
CAG Cache - Troubleshooting, How-To, and Company Info Only
NO product cache - all products go through RAG search
FIXED: Added Core vs V5 comparison, mod compatibility info
"""

class CAGCache:
    
    def __init__(self):
        
        # Product comparisons (EXPANDED)
        self.comparisons = {
            'v5_vs_v5xl': {
                'question': 'What is the difference between V5 and V5 XL?',
                'answer': """**V5 vs V5 XL - The Only Differences:**

🔧 **Top Piece:** XL has a longer top piece
📏 **Cup Size:** XL has a bigger cup (30% larger)

That's it! Same technology, same quality. XL just holds more concentrate per load.

**Which to choose:**
- V5: Standard dabs, most users
- V5 XL: Bigger dabs, longer sessions

Both use same ceramic cups, same heating tech."""
            },
            'core_vs_v5': {
                'question': 'Core vs V5 - which is better?',
                'answer': """**Core XL Deluxe vs V5:**

**Core XL Deluxe** ✅
- All-in-one (no separate mod needed)
- Just charge and go
- Easiest for beginners
- 6 heat settings
- Perfect for someone new to vapes

**V5 / V5 XL** ⚡
- Needs separate mod (Pico, Aegis, etc.)
- More control over temperature
- Best flavor possible
- Rebuildable (save money long-term)
- Better for advanced users

**Bottom line:**
- Want easy? → Core XL Deluxe
- Want control? → V5 XL

Both are excellent for concentrates!"""
            },
            'core_vs_fogger': {
                'question': 'Core vs Nice Dreamz Fogger?',
                'answer': """**Core XL Deluxe:** Our newest eRig - easy-to-use, built like a tank. Simple, reliable, beginner-friendly. All-in-one design with 6 heat settings.

**Nice Dreamz Fogger:** Forced-air eRig - pushes vapor to you. Just breathe in, the device does the work.

**Which to choose:**
- Core XL Deluxe: Want simplicity and durability (our newest!)
- Fogger: Want effortless hits with forced air

Note: Core 2.0/2.1 are older models. The Core XL Deluxe is our current flagship."""
            }
            # NOTE: Core 2.1/2.0 upsell now in quick_answers section
        }

        # QUICK ANSWERS - Discounts, shipping, terminology
        self.quick_answers = {
            'coupon': {
                'keywords': ['coupon', 'coupon code', 'discount', 'discount code', 'promo', 'promo code', 'promocode'],
                'answer': """💰 **Divine Tribe Discount Code:**

Use code **thankyou10** for 10% off your order!

🛒 Shop: https://ineedhemp.com
📧 Questions? Email matt@ineedhemp.com"""
            },
            'black_friday': {
                'keywords': ['black friday', 'cyber monday', 'sale', 'holiday sale', 'thanksgiving sale'],
                'answer': """🛍️ **Divine Tribe Pricing:**

We try to keep our prices as low as possible year-round, so we don't typically do big Black Friday markdowns.

However, you can always use code **thankyou10** for 10% off!

🛒 Shop: https://ineedhemp.com
📧 Questions? Email matt@ineedhemp.com"""
            },
            'international_shipping': {
                'keywords': ['international', 'ship to', 'vietnam', 'canada', 'uk', 'europe', 'australia', 'overseas', 'outside us', 'outside usa', 'another country', 'other country'],
                'answer': """🌍 **International Shipping:**

Yes! We ship internationally to most countries, including:
- Canada
- UK & Europe
- Australia
- Vietnam
- And many more!

📦 **Shipping details:**
- Discreet packaging (plain brown box, no logos)
- Tracking provided
- Delivery time varies by country

🛒 Place your order at https://ineedhemp.com
📧 Shipping questions? Email matt@ineedhemp.com"""
            },
            'spacer': {
                'keywords': ['spacer', 'what is a spacer', 'what is spacer', 'spacers'],
                'answer': """🔧 **What is a Spacer?**

A spacer is a ceramic piece that keeps the heater from touching the metal housing, preventing premature heat transfer.

This applies to Divine Tribe heater devices and coils - it's a key component that helps maintain proper heat distribution.

📧 Questions? Email matt@ineedhemp.com"""
            },
            'drip_tips': {
                'keywords': ['drip tip', 'drip tips', 'mouthpiece', 'tip options', 'tip difference'],
                'answer': """💨 **Divine Tribe Drip Tips:**

We offer three types of drip tips for our vaporizers:

1. **Silicone** ⭐ Most Popular
   - Recommended by our shop and customers
   - Comfortable, heat-resistant, durable

2. **Glass**
   - Pure flavor, smooth feel
   - Easy to clean

3. **Metal**
   - Standard option
   - Durable, classic look

Based on customer feedback, **silicone is the most popular choice!**

📧 Questions? Email matt@ineedhemp.com"""
            },
            'microcontroller': {
                'keywords': ['microcontroller', 'micro controller', 'temperature controller', 'temp controller', 'enail controller', 'e-nail controller'],
                'answer': """🎛️ **Divine Tribe Temperature Controllers:**

Our microcontroller/temperature controller works with all the coils we sell!

**Available options:**
- **20mm eNail coil with controller** - Standalone eNail setup
- **Ruby Twist Kit** - Complete ball vape kit with controller
  👉 https://ineedhemp.com/product/ruby-twist-kit/

The controller provides precise temperature control for the best vaping experience.

📧 Questions? Email matt@ineedhemp.com"""
            },
            'coil_compatibility': {
                'keywords': ['nice dreamz atomizer', 'fogger atomizer', 'core atomizer', 'nice dreamz on core', 'atomizer work on', 'atomizer fit', 'coil compatible', 'coils compatible', 'work on the core', 'fit on the core', 'same coils', 'interchangeable', 'coil work'],
                'answer': """🔄 **Coil Compatibility:**

Yes! **All Core bases and Nice Dreamz Fogger share the same coil system** - they're fully interchangeable!

✅ Core 2.0
✅ Core 2.1
✅ Core XL Deluxe
✅ Nice Dreamz Fogger

All use the same modular coils. You can mix and match any coil on any of these bases!

📧 Questions? Email matt@ineedhemp.com"""
            },
            'core_21_upsell': {
                'keywords': ['core 2.1', 'core 2.0', 'should i get the core 2', 'buy the core 2', 'get the 2.1', 'get the 2.0', 'buying core 2', 'purchase core 2'],
                'answer': """**Looking at the Core 2.0/2.1?**

We recommend the **Core XL Deluxe** instead - it's our newest model!

**Why Core XL Deluxe is better:**
- Has the **XL coil option** (bigger cup, more vapor)
- Same easy-to-use design you'd expect
- Our current flagship product

**Good news:** All Core models (2.0, 2.1, XL Deluxe) and Nice Dreamz Fogger share the same coil system - fully interchangeable!

👉 Go with the **Core XL Deluxe** for the best experience.

📧 Questions? Email matt@ineedhemp.com"""
            }
            # NOTE: Hemp t-shirt comparisons go through RAG for accuracy
        }

        # REDDIT-PROVEN TROUBLESHOOTING SOLUTIONS
        self.troubleshooting = {
            'v5_resistance_high': {
                'problem': 'V5 showing high resistance (0.60+ ohms) or "Check Atomizer"',
                'reddit_solutions': [
                    '🔧 **Most Common Fix**: Tighten the 510 pin on bottom of V5 with small screwdriver (1/4 turn)',
                    '🧹 **Clean the threads**: Remove cup, clean all 510 threads with alcohol',
                    '⚡ **Check mod contact**: Clean mod 510 connection too',
                    '🔄 **Reseat everything**: Unscrew completely, reassemble carefully',
                    '📊 **Normal range**: 0.40-0.52 ohms (most common: 0.45-0.48)'
                ],
                'if_still_broken': 'If still reading high after tightening, email matt@ineedhemp.com - might need replacement post or cup',
                'keywords': ['resistance', 'high ohm', 'check atomizer', 'atomizer short', 'resistance high', 'wont fire', "won't fire", 'resistance jumping']
            },
            'v5_resistance_low': {
                'problem': 'V5 showing low resistance (below 0.40 ohms)',
                'reddit_solutions': [
                    '🔍 **Check for shorts**: Remove cup and inspect for any metal touching metal',
                    '🧹 **Clean everything**: Concentrate buildup can cause shorts',
                    '⚠️ **Broken spring pin**: If under 0.30 ohms, spring pin might be damaged',
                    '🔄 **Try different mod**: Could be mod reading incorrectly'
                ],
                'if_still_broken': 'Resistance below 0.30 usually means broken spring pin - email matt@ineedhemp.com',
                'keywords': ['resistance low', 'low ohm', 'atomizer short', 'shorting']
            },
            'v5_leaking': {
                'problem': 'V5 leaking concentrate from bottom',
                'reddit_solutions': [
                    '📏 **#1 Cause**: Using too much material (rice grain size only!)',
                    '🌡️ **Temperature too high**: Keep under 420°F to prevent overflow',
                    '🔧 **O-ring check**: Make sure bottom O-ring is properly seated',
                    '⏱️ **Let it cool**: Don\'t remove cup while hot',
                    '🧹 **Regular cleaning**: Buildup can block airflow and cause pressure',
                    '💨 **Don\'t pull too hard**: Gentle draws prevent splatter'
                ],
                'prevention': 'Rice grain size loads + temps under 420°F = no leaks',
                'keywords': ['leaking', 'leak', 'leaks', 'concentrate coming out', 'spilling']
            },
            'v5_not_heating': {
                'problem': 'V5 not producing vapor or heating slowly',
                'reddit_solutions': [
                    '⚡ **Check wattage**: Need 30-35W minimum (XL needs 35-40W)',
                    '🌡️ **Temperature too low**: Try 400-420°F',
                    '🔋 **Battery charge**: Low battery = weak heating',
                    '🧹 **Clean cup**: Buildup blocks heat transfer',
                    '📊 **Check resistance**: Should be 0.40-0.52 ohms',
                    '🔧 **Mod settings**: Make sure temp control is enabled (Ni/TCR mode)'
                ],
                'perfect_flavor_settings': 'TCR 245-250, 380-400°F, 33-35W',
                'keywords': ['not heating', 'no vapor', 'weak', 'barely heating', 'cold']
            },
            'v5_burnt_taste': {
                'problem': 'V5 producing burnt or bad taste',
                'reddit_solutions': [
                    '🌡️ **Temperature too high**: Lower to 380-400°F',
                    '⚡ **Wattage too high**: Lower to 32-35W',
                    '🧹 **Cup needs cleaning**: Old buildup tastes burnt',
                    '🔄 **Cup replacement**: After 100+ sessions, cup degrades',
                    '📏 **Less material**: Overloading causes burning'
                ],
                'prevention': 'Clean after every session with alcohol wipe or burn-off cleaning',
                'keywords': ['burnt', 'bad taste', 'nasty', 'harsh', 'gross taste', 'metallic']
            },
            'core_not_heating': {
                'problem': 'Core 2.0 not heating or heating slowly',
                'reddit_solutions': [
                    '🔋 **Charge it**: Needs good battery charge',
                    '🌡️ **Increase temp**: Try 450-500°F',
                    '🧹 **Clean cup**: Remove cup and clean with alcohol',
                    '🔄 **Reset device**: Turn off and on',
                    '📱 **Check app**: Make sure temp settings saved',
                    '⚡ **Firmware update**: Check for updates in app'
                ],
                'if_still_broken': 'Email matt@ineedhemp.com with order number',
                'keywords': ['core not heating', 'core cold', 'core weak']
            },
            'core_battery': {
                'problem': 'Core battery issues (not charging, dies quickly)',
                'reddit_solutions': [
                    '🔌 **Check cable**: Try different USB-C cable',
                    '⚡ **Check power source**: Use wall adapter, not computer USB',
                    '🔋 **Battery degradation**: After 300+ cycles, battery weakens',
                    '🌡️ **High temps drain faster**: Lower temp = longer battery',
                    '📱 **Standby drain**: Turn off when not using',
                    '❄️ **Cold weather**: Battery performs worse in cold'
                ],
                'if_still_broken': 'Battery should last 20-30 sessions. If not, email matt@ineedhemp.com',
                'keywords': ['battery', 'charging', 'wont charge', 'dies fast', 'dead']
            }
        }
        
        # CUSTOMER SERVICE RESPONSES
        self.support_info = {
            'about_divine_tribe': '''
🏢 **About Divine Tribe**

**Company Info:**
- **Founded by**: Matt Macosko
- **Location**: Humboldt County, California
- **Specializes in**: Cannabis vaporizers (concentrates & dry herb)
- **Philosophy**: Clean flavor, rebuildable technology, direct pricing

**Product Lines:**
- 🔥 Concentrate Vaporizers: V5, V5 XL atomizers, Core eRig
- 🌿 Dry Herb: Ruby Twist ball vape, Gen 2 DC
- 👕 Hemp Clothing: T-shirts, hoodies, boxers
- 🏺 Accessories: Storage jars, glass bubblers, carb caps

**Why Divine Tribe:**
✅ Made in USA / Quality materials
✅ Rebuildable = Save money long-term
✅ Direct pricing (no middleman markup)
✅ Excellent customer service
✅ Eco-friendly practices
✅ Wholesale options available

**Community:**
- 💬 Active Reddit: r/DivineTribeVaporizers
- 🎮 Discord: https://discord.com/invite/aC4Pv6J75s
- 📺 YouTube: @divinetribe1

📧 **Contact**: matt@ineedhemp.com
🌐 **Shop**: https://ineedhemp.com
            ''',
            'warranty': '''
🛡️ **Divine Tribe Warranty:**

- **Standard warranty**: 30 days from purchase
- **What's covered**: Manufacturing defects, DOA items
- **Not covered**: Normal wear, user damage, lost items
- **How to claim**: Email matt@ineedhemp.com with:
  • Order number
  • Photos of the issue
  • Description of the problem

Matt is super helpful and will make it right! 🙌
            ''',
            'returns': '''
↩️ **Return Policy:**

- **Timeframe**: 30 days from delivery
- **Condition**: Must be unused/unopened
- **Process**:
  1. Email matt@ineedhemp.com
  2. Include order number
  3. Explain reason for return
  4. Matt will provide return instructions

**Note**: Opened atomizers/used items can't be returned (health code), but Matt works with you on defects!
            ''',
            'shipping': '''
📦 **Shipping Info:**

- **Processing time**: 1-3 business days
- **Shipping time**: 3-7 days (USPS Priority)
- **Tracking**: Sent via email when shipped
- **International**: Available to most countries (longer delivery)
- **Discreet packaging**: Always! Plain brown box, no logos

Lost or stolen package? Email matt@ineedhemp.com with tracking number.
            ''',
            'order_status': '''
📊 **Check Your Order:**

1. **Check email**: Tracking sent to your order email
2. **Processing**: Orders ship within 1-3 business days
3. **Weekend orders**: Process on Monday
4. **Issues?**: Email matt@ineedhemp.com with order number

Matt personally handles orders and responds quick! 
            ''',
            'contact': '''
📧 **Get Help From Divine Tribe:**

**Email**: matt@ineedhemp.com
- Response time: Usually same day
- Matt personally responds!
- Include order # if relevant

**Community Support**:
- 💬 Reddit: https://www.reddit.com/r/DivineTribeVaporizers/
- 🎮 Discord: https://discord.com/invite/aC4Pv6J75s
- 📺 YouTube: https://www.youtube.com/@divinetribe1

For tech support, Reddit and Discord often have instant answers from the community!
            '''
        }
        
        # HOW-TO GUIDES (ADDED MOD COMPATIBILITY)
        self.how_to = {
            'v5_first_time': '''
**First Time Using Your V5:**

1. **Charge your mod** - Full battery first!
2. **Install atomizer** - Hand-tighten only (don't force)
3. **Check resistance** - Should read 0.40-0.52 ohms
4. **Set temp** - Start at 380°F (or 30W in wattage mode)
5. **Rice grain size** - Seriously, don't overfill!
6. **Draw slowly** - Gentle, steady draw
7. **Clean between sessions** - Alcohol wipe or burn-off cleaning

**Pro tip**: First few sessions, do a burn-off at 450°F empty for 20 seconds to remove any manufacturing residue.
            ''',
            'v5_settings': '''
**Optimal V5 Settings:**

**Temperature Mode (Recommended)**:
- Flavor: 360-380°F
- Balanced: 380-410°F  
- Clouds: 410-450°F
- TCR: 245-250 (if your mod supports it)

**Wattage Mode**:
- Start: 30W
- Sweet spot: 32-35W
- Max: 40W (don't go higher!)

**For V5 XL**:
- Add 5-10°F to temperatures above
- Use 35-40W in wattage mode

**Pro tip**: Most people love 390-400°F. Experiment to find YOUR perfect temp!
            ''',
            'cleaning': '''
**How to Clean Your V5:**

**After Every Session (Best method)**:
1. While cup is still warm, use alcohol wipe
2. Swab the cup gently
3. Done! This prevents buildup

**Burn-Off Cleaning (Weekly)**:
1. Empty cup completely
2. Set to 450°F or 38W
3. Fire for 20 seconds
4. Let cool, wipe with alcohol wipe
5. Repeat if needed

**Pro tips**:
- Never clean with water while hot (can crack!)
- Don't forget to clean the threads too
- Replace cup after 100-150 sessions for best flavor

**For Core 2.0**: Same process, but also clean the glass bubbler regularly with alcohol!
            ''',
            'mod_recommendations': '''
**Best Mods for V5:**

**YES - These Work Great** ✅
- **Pico 75W** - Most popular, cheap, reliable
- **iStick Pico** - Same as above
- **Rim C** - Budget option
- **Aegis Solo** - Durable, waterproof
- **Aegis Mini** - Compact version
- **Wismec Reuleaux RX Gen3** - Dual/triple battery
- **Voopoo Drag** - Popular choice
- **Geekvape Aegis X** - Premium option

**Required Features**:
- Temperature control (TC) mode
- At least 75W power
- 510 threading
- Supports Ni or TCR modes

**Settings**:
- Mode: Ni or TCR 245-250
- Temp: 380-420°F
- Wattage: 30-35W (XL: 35-40W)

**Can I use my own mod?**
Yes! As long as it has temp control and 510 threading, it'll work with V5.

📧 Questions? Email matt@ineedhemp.com
            '''
        }
    
    # DISABLED: Product cache - all products now go through RAG
    def check_cache(self, query: str) -> str:
        """DISABLED - returns None to force RAG search"""
        return None
    
    def format_product_response(self, product_key: str) -> str:
        """DISABLED - was using hardcoded fake data"""
        return None
    
    def get_troubleshooting(self, query: str) -> dict:
        """Get troubleshooting solution based on keywords"""
        query_lower = query.lower()
        
        for issue_key, issue_data in self.troubleshooting.items():
            keywords = issue_data.get('keywords', [])
            if any(keyword in query_lower for keyword in keywords):
                return issue_data
        
        return None
    
    def get_how_to(self, query: str) -> str:
        """Get how-to guide based on query"""
        query_lower = query.lower()
        
        if 'first time' in query_lower or 'new to' in query_lower or 'just got' in query_lower:
            return self.how_to.get('v5_first_time')
        
        if 'settings' in query_lower or 'temp' in query_lower or 'wattage' in query_lower or 'tcr' in query_lower:
            return self.how_to.get('v5_settings')
        
        if 'clean' in query_lower or 'maintenance' in query_lower:
            return self.how_to.get('cleaning')
        
        # FIXED: Mod questions now have answers
        if 'mod' in query_lower and any(w in query_lower for w in ['recommend', 'which', 'what', 'best', 'use', 'own', 'my', 'compatible']):
            return self.how_to.get('mod_recommendations')
        
        return None
    
    def get_support_info(self, query: str) -> str:
        """Check if query is asking for customer service info"""
        query_lower = query.lower()
        
        # Company info queries
        if any(phrase in query_lower for phrase in ['about divine tribe', 'who is divine tribe', 'divine tribe company', 'what is divine tribe', 'tell me about divine tribe', 'how about divine tribe', 'what kind of']):
            return self.support_info.get('about_divine_tribe')
        
        support_keywords = {
            'warranty': ['warranty', 'guarantee', 'defect'],
            'returns': ['return', 'refund', 'send back'],
            'shipping': ['shipping', 'delivery', 'tracking', 'when will'],
            'order_status': ['order status', 'where is my', 'order', 'shipped'],
            'contact': ['contact', 'email', 'support', 'customer service']
        }
        
        for info_type, keywords in support_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return self.support_info.get(info_type)
        
        return None
    
    def get_comparison(self, query: str) -> str:
        """Check if query is asking for a product comparison - EXPANDED"""
        query_lower = query.lower()
        
        # V5 vs V5 XL
        if ('v5' in query_lower or 'v 5' in query_lower) and ('xl' in query_lower or 'xlarge' in query_lower or 'extra large' in query_lower):
            comp = self.comparisons.get('v5_vs_v5xl')
            return comp['answer'] if isinstance(comp, dict) else comp
        
        # Core vs V5 - ADDED!
        if ('core' in query_lower and 'v5' in query_lower) or ('core' in query_lower and 'v 5' in query_lower):
            if any(word in query_lower for word in ['vs', 'versus', 'compared', 'difference', 'better', 'which']):
                comp = self.comparisons.get('core_vs_v5')
                return comp['answer'] if isinstance(comp, dict) else comp
        
        # Core vs Fogger
        if ('core' in query_lower and 'fogger' in query_lower) or ('core' in query_lower and 'nice dreamz' in query_lower):
            comp = self.comparisons.get('core_vs_fogger')
            return comp['answer'] if isinstance(comp, dict) else comp

        # NOTE: Core 2.1/2.0 questions now handled by quick_answers (core_21_upsell)
        
        # Generic comparison request - ONLY if no specific products mentioned
        # Don't return generic message if user mentioned specific products
        product_mentions = ['shirt', 'tshirt', 't-shirt', 'hoodie', 'hemp', 'digicam', 'jar', 'v5', 'core', 'atomizer']
        has_product_mention = any(p in query_lower for p in product_mentions)

        if ('vs' in query_lower or 'versus' in query_lower or 'compared' in query_lower or 'difference between' in query_lower or 'difference from' in query_lower):
            if not has_product_mention:
                return "I can compare products for you! Which ones are you looking at?"
            # If products mentioned, return None so RAG handles it
            return None

        return None
    
    def get_category_listing(self, query: str) -> str:
        """Check if query is asking for a category listing"""
        query_lower = query.lower()
        
        listing_phrases = [
            'show me all', 'list all', 'what jars', 'what atomizers',
            'what products', 'whole list', 'complete list', 'everything you have',
            'all your', 'all the'
        ]
        
        if any(phrase in query_lower for phrase in listing_phrases):
            return "category_listing"
        
        return None
    
    def format_troubleshooting_response(self, issue_data: dict) -> str:
        """Format a troubleshooting response with Reddit solutions"""
        response = f"**Problem**: {issue_data['problem']}\n\n"
        response += "**Community-Proven Solutions** (from r/DivineTribeVaporizers):\n\n"
        
        for solution in issue_data['reddit_solutions']:
            response += f"{solution}\n\n"
        
        if 'prevention' in issue_data:
            response += f"**Prevention**: {issue_data['prevention']}\n\n"
        
        if 'perfect_flavor_settings' in issue_data:
            response += f"**Perfect Settings**: {issue_data['perfect_flavor_settings']}\n\n"
        
        if 'if_still_broken' in issue_data:
            response += f"⚠️ **Still having issues?** {issue_data['if_still_broken']}\n\n"
        
        return response
    
    # Agent router compatibility methods
    def get_troubleshooting_response(self, query: str) -> str:
        """Agent router compatibility"""
        try:
            issue = self.get_troubleshooting(query)
            return self.format_troubleshooting_response(issue) if issue else "I'm not sure about that. Email matt@ineedhemp.com for help!"
        except Exception as e:
            print(f"Error in get_troubleshooting_response: {e}")
            return "I'm having trouble with that. Email matt@ineedhemp.com for help!"

    def get_how_to_response(self, query: str) -> str:
        """Agent router compatibility"""
        try:
            response = self.get_how_to(query)
            if response:
                return response
            # FIXED: Don't just say "not sure" for mod questions
            return "I'm not sure about that. Email matt@ineedhemp.com for help!"
        except Exception as e:
            print(f"Error in get_how_to_response: {e}")
            return "I'm having trouble with that. Email matt@ineedhemp.com for help!"

    def get_comparison_response(self, query: str) -> str:
        """Agent router compatibility"""
        return self.get_comparison(query)
    
    def get_support_response(self, query: str) -> str:
        """Agent router compatibility"""
        return self.get_support_info(query)
    
    def get_warranty_response(self, query: str) -> str:
        """Agent router compatibility - warranty info"""
        return self.support_info.get('warranty', '')
    
    def get_return_response(self, query: str) -> str:
        """Agent router compatibility - return info"""
        return self.support_info.get('returns', '')

    def get_order_response(self, query: str) -> str:
        """Agent router compatibility - order info"""
        return self.support_info.get('order_status', '')

    def get_quick_answer(self, query: str) -> str:
        """Check quick_answers for instant responses (coupons, shipping, terminology)"""
        query_lower = query.lower()

        for answer_key, answer_data in self.quick_answers.items():
            keywords = answer_data.get('keywords', [])
            if any(keyword in query_lower for keyword in keywords):
                return answer_data['answer']

        return None
