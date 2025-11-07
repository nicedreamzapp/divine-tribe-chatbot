"""
CAG Cache - Complete Version Compatible with Agent Router
Enhanced with Reddit community solutions and all required methods
"""

class CAGCache:
    """
    Fast lookup system for frequently asked questions
    Uses Reddit-proven solutions for troubleshooting
    Compatible with AgentRouter
    """
    
    def __init__(self):
        # Main product cache with full details
        self.cached_products = {
            'v5': {
                'name': 'V5',
                'full_name': 'V5 Advanced Concentrate Atomizer',
                'description': 'The legendary V5 - Divine Tribe\'s most popular atomizer. Features a silicon carbide cup that delivers pure flavor and massive clouds. Works with any 510 threaded mod.',
                'price': '$40-50',
                'features': [
                    '✨ Silicon carbide (SiC) cup - incredible flavor',
                    '🔥 Works 350-500°F',
                    '⚡ Requires mod with 30W+ capability',
                    '🎯 Perfect for beginners and experts',
                    '🧼 Easy to clean - qtip between dabs'
                ],
                'keywords': ['what is v5', 'what is the v5', 'tell me about v5', 'buy v5', 'v five atomizer', 'version 5'],
                'url': 'https://ineedhemp.com/product/v5/'
            },
            'v5_xl': {
                'name': 'V5 XL',
                'full_name': 'V5 XL Extended Life Atomizer',
                'description': 'Everything you love about the V5, but BIGGER! 30% larger cup means more concentrate per load and even better heat distribution.',
                'price': '$50-60',
                'features': [
                    '🚀 30% larger SiC cup than regular V5',
                    '💨 Massive clouds and extended sessions',
                    '🔥 Same great SiC technology',
                    '⚡ Needs 35W+ mod',
                    '👑 The king of Divine Tribe atomizers'
                ],
                'keywords': ['v5 xl', 'v5xl', 'v 5 xl', 'extra large', 'bigger v5'],
                'url': 'https://ineedhemp.com/product/v5-xl/'
            },
            'core_deluxe': {
                'name': 'Core 2.0 Deluxe',
                'full_name': 'Core 2.0 Deluxe Wireless Enail',
                'description': 'The ultimate all-in-one e-rig. No mod needed! Built-in battery, water attachment included, and the same legendary SiC cup technology.',
                'price': '$199-249',
                'features': [
                    '📱 Complete kit - nothing else needed',
                    '🔋 Built-in 3000mAh battery',
                    '💧 Glass bubbler included',
                    '🎯 Digital temp control (Bluetooth app)',
                    '✈️ Portable and discreet',
                    '🏆 Best value complete setup'
                ],
                'keywords': ['core', 'core 2', 'core deluxe', 'e-rig', 'enail', 'wireless', 'all in one'],
                'url': 'https://ineedhemp.com/product/core-2-0-deluxe/'
            },
            'nice_dreamz': {
                'name': 'Nice Dreamz Vaporizer',
                'full_name': 'Nice Dreamz Portable Flower Vaporizer',
                'description': 'Premium dry herb vaporizer with true convection heating. Perfect for flower enthusiasts who want pure, flavorful vapor.',
                'price': '$129-149',
                'features': [
                    '🌿 Designed for dry herb (flower)',
                    '🌡️ Precise temperature control',
                    '🔥 True convection heating',
                    '🔋 Long battery life',
                    '💨 Pure flavor, no combustion',
                    '📏 Compact and portable'
                ],
                'keywords': ['nice dreamz', 'nicedreamz', 'nice dreams', 'flower', 'dry herb', 'herb vaporizer'],
                'url': 'https://ineedhemp.com/product/nice-dreamz/'
            },
            'lightning_pen': {
                'name': 'Lightning Pen',
                'full_name': 'Lightning Pen Concentrate Vaporizer',
                'description': 'Ultra-discreet pen-style vaporizer for concentrates. Perfect for on-the-go sessions with reliable performance.',
                'price': '$39-49',
                'features': [
                    '✏️ Pen-style - super discreet',
                    '⚡ Quick heat-up time',
                    '🎯 Easy to use - perfect for beginners',
                    '💼 Pocket-friendly size',
                    '🔋 USB rechargeable'
                ],
                'keywords': ['lightning pen', 'pen', 'lightning', 'discrete', 'portable pen'],
                'url': 'https://ineedhemp.com/product/lightning-pen/'
            }
        }
        
        # REDDIT-PROVEN TROUBLESHOOTING SOLUTIONS
        self.troubleshooting = {
            # V5 Resistance Issues (from r/DivineTribeVaporizers)
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
                    '🔥 **Temperature settings**: Start at 380-400°F',
                    '📊 **TCR mode**: Use TCR 245-250 for best results',
                    '🔋 **Battery charge**: Low battery = weak heating',
                    '🧹 **Dirty cup**: Buildup reduces heat transfer - clean with alcohol',
                    '⏱️ **Preheat longer**: Give it 15-20 seconds before hitting'
                ],
                'keywords': ['not heating', 'no vapor', 'weak hits', 'not working', 'cold', "won't heat", 'barely heats', "doesn't get hot", 'not reaching temp']
            },
            'v5_chazzed': {
                'problem': 'V5 cup is chazzed (burnt/discolored)',
                'reddit_solutions': [
                    '🔥 **Burn-off method (BEST)**: Hold mod upside down, fire at 38W for 2 minutes',
                    '⚡ **For Core users**: Remove cup, attach to any mod that does 40W',
                    '⏱️ **Repeat until clean**: Let cool between cycles, repeat until no vapor',
                    '🧹 **Prevention**: Q-tip after every session, don\'t exceed 450°F',
                    '💧 **Iso soak backup**: If burn-off doesn\'t work, soak in 91%+ iso overnight'
                ],
                'prevention': 'Clean after every use, keep temps under 420°F for daily use',
                'keywords': ['chazzed', 'chaz', 'burnt cup', 'discolored', 'black residue', 'cleaning cup']
            },
            'v5_burning_taste': {
                'problem': 'V5 producing burnt or harsh taste',
                'reddit_solutions': [
                    '🌡️ **Lower temperature**: Start at 360-380°F for flavor',
                    '🧹 **Clean the cup**: Burnt residue ruins flavor - qtip after every session',
                    '📏 **Smaller loads**: Big loads burn on edges',
                    '⏱️ **Shorter draws**: Long draws overheat the oil',
                    '🔄 **New coil**: After 100+ sessions, cups lose efficiency'
                ],
                'perfect_flavor_settings': '360-380°F, rice grain loads, clean after every use',
                'keywords': ['burnt', 'burning', 'harsh', 'bad taste', 'burnt taste']
            },
            'core_battery': {
                'problem': 'Core 2.0 battery issues',
                'reddit_solutions': [
                    '🔌 **Charging issues**: Use provided USB-C cable, try different adapter',
                    '🔋 **Battery life short**: Lower temperature, shorter sessions',
                    '❄️ **Cold weather**: Battery drains faster in cold - warm it up',
                    '🔄 **Power cycle**: Turn off completely, charge fully, restart',
                    '📱 **App connection**: Update app, toggle Bluetooth off/on'
                ],
                'keywords': ['core battery', 'wont charge', 'battery dead', 'core not charging']
            },
            'core_bluetooth': {
                'problem': 'Core 2.0 Bluetooth connection issues',
                'reddit_solutions': [
                    '📱 **Forget and repair**: Delete device from Bluetooth, pair again',
                    '🔄 **Restart both**: Phone and Core completely off/on',
                    '📍 **Location permissions**: App needs location enabled',
                    '🔋 **Core battery**: Won\'t connect if battery under 20%',
                    '📲 **App update**: Make sure you have latest version',
                    '📏 **Distance**: Keep phone within 10 feet during use'
                ],
                'keywords': ['bluetooth', 'wont connect', 'app', 'connection', 'pairing']
            },
            'arctic_fox_setup': {
                'problem': 'V5 not working properly with Arctic Fox firmware',
                'reddit_solutions': [
                    '🔧 **Use TCR mode**: Set TCR to 245-250 (not Ni200)',
                    '⚡ **Wattage**: Set to 33-35W',
                    '🌡️ **Temperature**: Start at 380-400°F',
                    '🔒 **Lock resistance**: Lock at room temp (0.45-0.48 ohms typical)',
                    '📊 **Profile settings**: Pre-heat 1 second, PI-Regulator ON',
                    '🔄 **If still issues**: Try firmware reset and reconfigure'
                ],
                'if_still_broken': 'Check r/DivineTribeVaporizers for Arctic Fox profiles - many users share their working configs',
                'keywords': ['arctic fox', 'arcticfox', 'af firmware', 'wont get to temp', "won't reach temp", 'tcr', 'firmware']
            },
            'mod_compatibility': {
                'problem': 'Mod compatibility or setup issues with V5',
                'reddit_solutions': [
                    '⚡ **Minimum wattage**: Mod must support 30W+ (35W+ for XL)',
                    '🌡️ **TC support required**: Must have temperature control',
                    '🔋 **Battery**: Use quality 18650s (Sony VTC6, Samsung 25R)',
                    '📊 **Recommended mods**: Pico, Wismec, Aegis series work great',
                    '🔧 **Settings**: TCR 245-250, 33-35W, lock resistance at room temp'
                ],
                'keywords': ['mod', 'what mod', 'mod recommendation', 'compatible mod', 'which mod', 'pico', 'wismec', 'aegis']
            }
        }
        
        # CUSTOMER SERVICE RESPONSES
        self.support_info = {
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
        
        # PRODUCT COMPARISONS
        self.comparisons = {
            'v5_vs_v5xl': '''
**V5 vs V5 XL - Which to choose?**

**Regular V5** 💰 $40-50
✅ Perfect for solo use
✅ More portable
✅ Easier to clean
✅ Uses less concentrate
Choose if: Budget-conscious, solo sessions, new to dabbing

**V5 XL** 💰 $50-60  
✅ 30% bigger cup
✅ Massive clouds
✅ Better for sharing
✅ Longer sessions
Choose if: Want huge hits, share with friends, have concentrate to spare

**Bottom line**: Can't go wrong either way! XL is worth the $10 if you want bigger sessions.
            ''',
            'v5_vs_core': '''
**V5 vs Core 2.0 - Mod or E-rig?**

**V5 Setup** 💰 $100-150 total (V5 + mod)
✅ More flexible (swap atomizers)
✅ Replaceable batteries
✅ More power options
✅ Cheaper to start
❌ Requires buying separate mod
❌ Learning curve for settings
Choose if: Already have a mod, want flexibility, don't mind learning

**Core 2.0 Deluxe** 💰 $200-250 complete
✅ Everything included (glass, battery, atomizer)
✅ App control (super easy)
✅ More portable
✅ Looks cleaner
❌ Can't swap batteries
❌ Limited to Core atomizer
Choose if: Want complete setup, value convenience, like app control

**Bottom line**: Core is "iPhone" (just works), V5 is "Android" (more control).
            ''',
            'flower_vs_concentrate': '''
**Flower vs Concentrate - Which Vape?**

**Nice Dreamz** (Flower) 🌿 $129-149
✅ For dry herb / flower
✅ More natural experience
✅ Cheaper per session
✅ True convection heating
Choose if: You prefer flower, want longer sessions, more budget-friendly material

**V5 or Core** (Concentrate) 💎 $40-250
✅ For wax, shatter, rosin
✅ More potent
✅ More discreet
✅ Faster effects
Choose if: You prefer concentrates, want stronger effects, value discretion

**Can't decide?** Many people have both! Different experiences for different occasions.
            '''
        }
        
        # HOW-TO GUIDES
        self.how_to = {
            'v5_first_time': '''
**First Time Using Your V5:**

1. **Charge your mod** - Full battery first!
2. **Install atomizer** - Hand-tighten only (don't force)
3. **Check resistance** - Should read 0.40-0.52 ohms
4. **Set temp** - Start at 380°F (or 30W in wattage mode)
5. **Rice grain size** - Seriously, don't overfill!
6. **Preheat 10 seconds** - Let it warm up
7. **Draw slowly** - Gentle, steady draw
8. **Q-tip while warm** - Clean between sessions

**Pro tip**: First few sessions, season the cup at 450°F empty for 20 seconds, then q-tip. This burns off any manufacturing residue.
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

**After Every Session (30 seconds)**:
1. While cup is still warm, use dry q-tip
2. Swab the cup gently
3. Done! This prevents buildup

**Deep Clean (Weekly)**:
1. Remove cup from atomizer
2. Soak cup in 91%+ isopropyl alcohol (10 mins)
3. Rinse with water
4. Let air dry completely
5. Reassemble

**Pro tips**:
- Never clean with water while hot (can crack!)
- Don't forget to clean the threads too
- Replace cup after 100-150 sessions for best flavor

**For Core 2.0**: Same process, but also clean the glass bubbler regularly!
            ''',
            'mod_recommendations': '''
**Best Mods for V5:**

**Budget** 💰 $30-50:
- Pico 75W
- iStick Pico
- Rim C

**Mid-Range** 💰 $50-80:
- Wismec Reuleaux RX Gen3
- Aegis Solo/Mini
- Pico 25

**Premium** 💰 $80-150:
- DNA mods (Lost Vape, etc.)
- Aegis Legend
- YiHi SX minis

**What you need**:
- At least 30W output (35W+ for XL)
- Temperature Control (TC) support
- Replaceable 18650 battery
- Reputable brand

**Pro tip**: Aegis series is super durable (drop-proof, water-resistant). Great for daily use!
            '''
        }
        
    def check_cache(self, query: str) -> str:
        """
        Check if query matches a cached product
        Returns product key if found, None otherwise
        """
        query_lower = query.lower()
        
        for product_key, product_data in self.cached_products.items():
            if any(keyword in query_lower for keyword in product_data['keywords']):
                return product_key
        
        return None
    
    def get_troubleshooting(self, query: str) -> dict:
        """
        Check if query matches a troubleshooting issue
        Returns troubleshooting data if found, None otherwise
        """
        query_lower = query.lower()
        
        for issue_key, issue_data in self.troubleshooting.items():
            if any(keyword in query_lower for keyword in issue_data['keywords']):
                return issue_data
        
        return None
    
    def get_support_info(self, query: str) -> str:
        """
        Check if query is asking for customer service info
        """
        query_lower = query.lower()
        
        support_keywords = {
            'warranty': ['warranty', 'guarantee', 'broken', 'defect'],
            'returns': ['return', 'refund', 'send back'],
            'shipping': ['shipping', 'delivery', 'tracking', 'when will'],
            'order_status': ['order status', 'where is my', 'order', 'shipped'],
            'contact': ['contact', 'email', 'support', 'help', 'customer service']
        }
        
        for info_type, keywords in support_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return self.support_info.get(info_type)
        
        return None
    
    def get_comparison(self, query: str) -> str:
        """
        Check if query is asking for a product comparison
        """
        query_lower = query.lower()
        
        if ('v5' in query_lower and 'xl' in query_lower) or ('v5' in query_lower and 'xlarge' in query_lower):
            return self.comparisons['v5_vs_v5xl']
        
        if ('v5' in query_lower or 'mod' in query_lower) and 'core' in query_lower:
            return self.comparisons['v5_vs_core']
        
        if ('flower' in query_lower or 'herb' in query_lower) and ('concentrate' in query_lower or 'wax' in query_lower or 'dab' in query_lower):
            return self.comparisons['flower_vs_concentrate']
        
        if 'vs' in query_lower or 'versus' in query_lower or 'compared' in query_lower or 'difference between' in query_lower:
            return "I can compare products for you! Which ones are you looking at? (e.g., V5 vs V5 XL, V5 vs Core, flower vs concentrate)"
        
        return None
    
    def get_category_listing(self, query: str) -> str:
        """
        Check if query is asking for a category listing
        Required by AgentRouter
        """
        query_lower = query.lower()
        
        # Check if asking for listings
        if any(phrase in query_lower for phrase in ['show me all', 'what jars', 'what atomizers', 'what coils', 'list of']):
            return "category_listing_detected"
        
        return None
    
    def get_how_to(self, query: str) -> str:
        """
        Check if query is asking for how-to instructions
        """
        query_lower = query.lower()
        
        # Check for cleaning first (specific)
        if any(word in query_lower for word in ['clean', 'cleaning', 'how to clean', 'maintenance']):
            return self.how_to.get('cleaning')
        
        # Check for settings
        if any(word in query_lower for word in ['settings', 'what temp', 'tcr', 'what watt']):
            return self.how_to.get('v5_settings')
        
        # Check for first time use
        if any(phrase in query_lower for phrase in ['first time', 'how to use', 'getting started', 'new to', 'just got']):
            return self.how_to.get('v5_first_time')
        
        # Check for mod recommendations
        if any(word in query_lower for word in ['what mod', 'recommend mod', 'best mod', 'which mod']):
            return self.how_to.get('mod_recommendations')
        
        return None
    
    def format_product_response(self, product_key: str) -> str:
        """
        Format a complete product response with all details
        Returns the full cached response - NO truncation
        """
        product = self.cached_products.get(product_key)
        if not product:
            return None
        
        # Build complete response
        response = f"**{product['full_name']}** 💰 {product['price']}\n\n"
        response += f"{product['description']}\n\n"
        response += "**Key Features:**\n"
        for feature in product['features']:
            response += f"{feature}\n"
        response += f"\n[Shop Now]({product['url']})"
        
        return response
    
    def format_troubleshooting_response(self, issue_data: dict) -> str:
        """
        Format a troubleshooting response with Reddit solutions
        """
        response = f"**Problem**: {issue_data['problem']}\n\n"
        response += "**Community-Proven Solutions** (from r/DivineTribeVaporizers):\n\n"
        
        for i, solution in enumerate(issue_data['reddit_solutions'], 1):
            response += f"{solution}\n\n"
        
        if 'prevention' in issue_data:
            response += f"**Prevention**: {issue_data['prevention']}\n\n"
        
        if 'perfect_flavor_settings' in issue_data:
            response += f"**Perfect Settings**: {issue_data['perfect_flavor_settings']}\n\n"
        
        if 'if_still_broken' in issue_data:
            response += f"⚠️ **Still having issues?** {issue_data['if_still_broken']}\n\n"
        
        return response
    
    def get_troubleshooting_response(self, query: str) -> str:
        """
        Get troubleshooting response for a query
        Alias method for agent_router compatibility
        """
        issue = self.get_troubleshooting(query)
        if issue:
            return self.format_troubleshooting_response(issue)
        return None

    def get_how_to_response(self, query: str) -> str:
        """Agent router compatibility"""
        return self.get_how_to(query)
    
    def get_comparison_response(self, query: str) -> str:
        """Agent router compatibility"""
        return self.get_comparison(query)
    
    def get_support_response(self, query: str) -> str:
        """Agent router compatibility"""
        return self.get_support_info(query)
    
    def get_troubleshooting_response(self, query: str) -> str:
        """Agent router compatibility"""
        issue = self.get_troubleshooting(query)
        return self.format_troubleshooting_response(issue) if issue else None
    
    def get_category_listing(self, query: str) -> str:
        """Agent router compatibility"""
        query_lower = query.lower()
        if any(phrase in query_lower for phrase in ['show me all', 'what jars', 'what atomizers']):
            return "category_listing"
        return None

    def get_warranty_response(self, query: str) -> str:
        """Agent router compatibility - warranty info"""
        if 'warranty' in query.lower() or 'guarantee' in query.lower():
            return self.support_info.get('warranty')
        return None
    
    def get_return_response(self, query: str) -> str:
        """Agent router compatibility - return info"""
        if 'return' in query.lower() or 'refund' in query.lower():
            return self.support_info.get('returns')
        return None
    
    def get_order_response(self, query: str) -> str:
        """Agent router compatibility - order info"""
        if 'order' in query.lower() or 'tracking' in query.lower() or 'shipping' in query.lower():
            return self.support_info.get('order_status')
        return None
    
    def get_how_to_response(self, query: str) -> str:
        """Agent router compatibility"""
        return self.get_how_to(query)
    
    def get_comparison_response(self, query: str) -> str:
        """Agent router compatibility"""
        return self.get_comparison(query)
    
    def get_support_response(self, query: str) -> str:
        """Agent router compatibility"""
        return self.get_support_info(query)
    
    def get_troubleshooting_response(self, query: str) -> str:
        """Agent router compatibility"""
        issue = self.get_troubleshooting(query)
        return self.format_troubleshooting_response(issue) if issue else None
    
    def get_category_listing(self, query: str) -> str:
        """Agent router compatibility"""
        query_lower = query.lower()
        if any(phrase in query_lower for phrase in ['show me all', 'what jars', 'what atomizers', 'list of', 'all products']):
            return "category_listing"
        return None
