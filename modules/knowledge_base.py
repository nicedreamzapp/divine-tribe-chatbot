#!/usr/bin/env python3
"""
Knowledge Base - Divine Tribe product knowledge, rules, and priorities
"""

from typing import Dict, List, Optional

class KnowledgeBase:
    def __init__(self):
        self.discount_code = "thankyou10"
        self.discount_amount = "10% off"
        self.discord_url = "https://discord.com/invite/aC4Pv6J75s"
        self.reddit_url = "https://www.reddit.com/r/DivineTribeVaporizers/"
        self.support_email = "matt@ineedhemp.com"
        
        self.product_facts = {
            'v5': {
                'description': 'Latest handheld atomizer with PURE CERAMIC pathway',
                'resistance': '0.42-0.51Ω',
                'pure_pathway': 'NO METAL in vapor path - pure ceramic only!',
                'ultimate_setup': 'V5 + Glass Vortex Top = ceramic + glass ONLY (purest possible)',
                'works_with': 'Bottomless bangers for water filtration',
                'recommend_when': 'Customer wants purest flavor OR does not have Core/Nice Dreams'
            },
            'cub': {
                'description': 'Essential adapter for Core/Nice Dreams owners',
                'superpower': 'ONLY way to clean Core coils!',
                'dual_purpose': 'Standalone atomizer + coil cleaning tool',
                'pathway': 'Has some metal in vapor pathway',
                'works_with': 'Bottomless bangers (like V5)',
                'recommend_when': 'Customer has Core OR Nice Dreams (essential!)',
                'vs_v5': 'V5 = pure ceramic (no metal), Cub = some metal but cleans Core coils'
            },
            'core': {
                'description': 'Core 2.0 Deluxe - 6 heat settings, titanium sleeve',
                'resistance': '0.42-0.51Ω',
                'must_have_accessory': 'Cub adapter (ONLY way to clean Core coils!)',
            },
            'lightning_pen': {
                'description': 'SMALLEST cup-style pen on market',
                'resistance': '0.31-0.37Ω (DIFFERENT - standalone only!)',
                'warning': 'NEVER use on mod - standalone only!'
            },
            'ruby_twist': {
                'description': 'Latest & greatest for dry herb',
                'special': 'Controllers also heat terp slurpers!'
            }
        }
        
        self.v5_vs_cub_logic = {
            'has_core_or_nice_dreams': {
                'recommend': 'Cub',
                'message': 'Since you have a Core/Nice Dreams, the **Cub adapter** is essential! It\'s the ONLY way to clean your coils back to white.'
            },
            'wants_purest_flavor': {
                'recommend': 'V5',
                'message': 'For purest flavor, go with the **V5** - pure ceramic pathway with NO metal! Add the **Glass Vortex Top** for ceramic + glass ONLY.',
                'ultimate': 'V5 + Glass Vortex Top = absolute purest setup'
            },
            'no_preference': {
                'recommend': 'V5',
                'message': 'The **V5** is our latest atomizer with a pure ceramic pathway.'
            }
        }
        
        self.recommendation_priority = {
            'beginner': [('Core 2.0 Deluxe', 'Most recommended')],
            'portable': [('Lightning Pen', 'Smallest, most discreet')],
            'performance': [('Ruby Twist', 'Best dry herb')],
        }
        
        self.troubleshooting_steps = [
            {'step': 1, 'action': 'Check lead wires in screw holes', 'detail': 'Wires must be VISIBLE inside holes. 90% of issues!'},
            {'step': 2, 'action': 'Check resistance', 'detail': 'Normal: 0.42-0.51Ω at room temp'},
            {'step': 3, 'action': 'Clean with isopropyl', 'detail': 'Clean all contact points'},
            {'step': 4, 'action': 'Check heater condition', 'detail': 'If damaged, need new heater (cheap!)'}
        ]
    
    def get_beginner_recommendation(self) -> str:
        return "Core 2.0 Deluxe - standalone, powerful, easy!"
    
    def get_discount_mention(self) -> str:
        return f"Use code **{self.discount_code}** for {self.discount_amount}!"
    
    def get_community_links(self, markdown: bool = True) -> str:
        if markdown:
            return f"[Discord]({self.discord_url}) and [Reddit]({self.reddit_url}) for help!"
        return f"Discord: {self.discord_url} | Reddit: {self.reddit_url}"
    
    def recommend_v5_or_cub(self, has_core: bool = False, wants_pure: bool = False) -> Dict:
        if has_core:
            return self.v5_vs_cub_logic['has_core_or_nice_dreams']
        elif wants_pure:
            return self.v5_vs_cub_logic['wants_purest_flavor']
        return self.v5_vs_cub_logic['no_preference']
