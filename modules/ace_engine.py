#!/usr/bin/env python3
"""
ACE Engine - Agentic Context Engineering
Automatically evolves system prompts based on human feedback
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple

class ACEEngine:
    def __init__(self):
        """Initialize ACE engine"""
        self.feedback_log_path = "feedback_log.json"
        self.rules_path = "modules/learned_rules.py"
        print("\n" + "="*80)
        print("ACE ENGINE - AGENTIC CONTEXT ENGINEERING")
        print("="*80 + "\n")
    
    def load_feedback(self) -> List[Dict]:
        """Load all feedback from feedback_log.json"""
        if not os.path.exists(self.feedback_log_path):
            print("❌ No feedback_log.json found!")
            print("Run 'python3 feedback_interface.py' first to review conversations")
            return []
        
        with open(self.feedback_log_path, 'r') as f:
            return json.load(f)
    
    def analyze_bad_patterns(self, feedback: List[Dict]) -> Dict[str, List[str]]:
        """Analyze bad responses to find patterns"""
        bad_feedback = [f for f in feedback if f['rating'] == 'BAD']
        
        print(f"📊 Analyzing {len(bad_feedback)} bad responses...")
        
        # Group by common issues
        patterns = defaultdict(list)
        
        for fb in bad_feedback:
            reason = fb['reason'].lower()
            
            # Detect common failure patterns
            if any(word in reason for word in ['hallucination', 'made up', 'fake', 'invented', 'doesnt exist', "doesn't exist"]):
                patterns['hallucination'].append(fb)
            elif any(word in reason for word in ['wrong product', 'incorrect product', 'recommended wrong']):
                patterns['wrong_product'].append(fb)
            elif any(word in reason for word in ['cub', 'mentioned cub', 'shouldnt mention cub']):
                patterns['unnecessary_cub'].append(fb)
            elif any(word in reason for word in ['accessory', 'should recommend main', 'kit instead']):
                patterns['prioritize_kits'].append(fb)
            elif any(word in reason for word in ['emoji', 'added emoji', 'modified name']):
                patterns['emoji_in_names'].append(fb)
            elif any(word in reason for word in ['link', 'url', 'broken link']):
                patterns['broken_links'].append(fb)
            else:
                patterns['other'].append(fb)
        
        return patterns
    
    def generate_rules(self, patterns: Dict[str, List[str]]) -> List[str]:
        """Generate new rules based on bad patterns"""
        rules = []
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        print("\n🧠 GENERATING NEW RULES:\n")
        
        if patterns['hallucination']:
            rule = f"""
# RULE #{len(rules)+1} (learned {timestamp}):
# Pattern: Hallucination detected ({len(patterns['hallucination'])} times)
# Fix: When product not found, MUST say "I don't see that in our catalog"
ANTI_HALLUCINATION_STRICT = True
"""
            rules.append(rule)
            print(f"✓ Rule #{len(rules)}: Anti-hallucination enforcement")
        
        if patterns['wrong_product']:
            rule = f"""
# RULE #{len(rules)+1} (learned {timestamp}):
# Pattern: Recommended wrong products ({len(patterns['wrong_product'])} times)
# Fix: When user asks for 'main products', prioritize KITS over accessories
PRIORITIZE_KITS_FOR_MAIN = True
"""
            rules.append(rule)
            print(f"✓ Rule #{len(rules)}: Prioritize complete kits")
        
        if patterns['unnecessary_cub']:
            rule = f"""
# RULE #{len(rules)+1} (learned {timestamp}):
# Pattern: Mentioned Cub when shouldn't ({len(patterns['unnecessary_cub'])} times)
# Fix: ONLY mention Cub if customer explicitly has Core/Nice Dreamz/TUG
CUB_ONLY_FOR_CORE_OWNERS = True
"""
            rules.append(rule)
            print(f"✓ Rule #{len(rules)}: Restrict Cub mentions")
        
        if patterns['prioritize_kits']:
            rule = f"""
# RULE #{len(rules)+1} (learned {timestamp}):
# Pattern: Showed accessories instead of main products ({len(patterns['prioritize_kits'])} times)
# Fix: Boost 'kit' and 'bundle' products in search scoring
KIT_BOOST_MULTIPLIER = 2.5
"""
            rules.append(rule)
            print(f"✓ Rule #{len(rules)}: Boost kit priority in search")
        
        if patterns['emoji_in_names']:
            rule = f"""
# RULE #{len(rules)+1} (learned {timestamp}):
# Pattern: Added emojis to product names ({len(patterns['emoji_in_names'])} times)
# Fix: Use EXACT product names from catalog, no modifications
EXACT_PRODUCT_NAMES_ONLY = True
"""
            rules.append(rule)
            print(f"✓ Rule #{len(rules)}: Enforce exact product names")
        
        if patterns['broken_links']:
            rule = f"""
# RULE #{len(rules)+1} (learned {timestamp}):
# Pattern: Broken or incorrect URLs ({len(patterns['broken_links'])} times)
# Fix: Copy EXACT URLs from AVAILABLE PRODUCTS, never modify
EXACT_URLS_ONLY = True
"""
            rules.append(rule)
            print(f"✓ Rule #{len(rules)}: Enforce exact URLs")
        
        return rules
    
    def update_response_generator(self, rules: List[str]):
        """Update response_generator.py with new learned rules"""
        rules_content = f'''#!/usr/bin/env python3
"""
LEARNED RULES - Auto-generated by ACE Engine
Last updated: {datetime.now().isoformat()}

These rules were learned from human feedback (RLHF).
DO NOT EDIT MANUALLY - use feedback_interface.py + ace_engine.py
"""

{chr(10).join(rules)}

def apply_rules_to_prompt(base_prompt: str) -> str:
    """Apply learned rules to system prompt"""
    
    enhanced_prompt = base_prompt
    
    # Add learned rules section
    enhanced_prompt += """
    
=== LEARNED RULES (FROM HUMAN FEEDBACK) ===
"""
    
    if ANTI_HALLUCINATION_STRICT:
        enhanced_prompt += """
⚠️ CRITICAL: If product not in AVAILABLE PRODUCTS, you MUST respond:
"I don't see that specific item in our catalog of 134 products."
DO NOT suggest similar products unless they are in AVAILABLE PRODUCTS.
"""
    
    if PRIORITIZE_KITS_FOR_MAIN:
        enhanced_prompt += """
⚠️ CRITICAL: When user asks about "main products" or "what do you sell":
ONLY show complete KITS (with 'kit' or 'bundle' in name).
DO NOT show accessories, replacement parts, or standalone components.
"""
    
    if CUB_ONLY_FOR_CORE_OWNERS:
        enhanced_prompt += """
⚠️ CRITICAL: ONLY mention Cub adapter if customer explicitly states:
"I have a Core" or "I own Nice Dreamz" or "I have TUG"
If customer asks about V5, troubleshooting (without Core), or general questions:
DO NOT MENTION CUB AT ALL.
"""
    
    if globals().get('KIT_BOOST_MULTIPLIER'):
        enhanced_prompt += f"""
⚠️ Search priority: Complete kits get {KIT_BOOST_MULTIPLIER}x scoring boost.
Accessories should appear AFTER main products unless specifically requested.
"""
    
    if EXACT_PRODUCT_NAMES_ONLY:
        enhanced_prompt += """
⚠️ CRITICAL: Use EXACT product names from AVAILABLE PRODUCTS.
DO NOT add emojis (🚀🌱❄️ etc.) to product names.
DO NOT modify product names in any way.
"""
    
    if EXACT_URLS_ONLY:
        enhanced_prompt += """
⚠️ CRITICAL: Use EXACT URLs from AVAILABLE PRODUCTS.
DO NOT modify, shorten, or create URLs.
Copy and paste the exact URL shown in AVAILABLE PRODUCTS.
"""
    
    return enhanced_prompt
'''
        
        # Save learned rules
        with open(self.rules_path, 'w') as f:
            f.write(rules_content)
        
        print(f"\n✅ Saved learned rules to: {self.rules_path}")
        print("\nNext step: Restart chatbot to apply new rules!")
        print("  cd ~/Desktop/dataset\\ for\\ Tribe\\ Chatbot")
        print("  source venv/bin/activate")
        print("  python3 chatbot_modular.py")
    
    def learn(self):
        """Main learning process"""
        # Load feedback
        feedback = self.load_feedback()
        
        if not feedback:
            return
        
        print(f"📚 Loaded {len(feedback)} feedback entries")
        
        # Count ratings
        good = sum(1 for f in feedback if f['rating'] == 'GOOD')
        bad = sum(1 for f in feedback if f['rating'] == 'BAD')
        
        print(f"✅ Good responses: {good}")
        print(f"❌ Bad responses: {bad}")
        
        if bad == 0:
            print("\n🎉 No bad responses! Chatbot is performing well.")
            return
        
        # Analyze patterns
        patterns = self.analyze_bad_patterns(feedback)
        
        # Generate rules
        rules = self.generate_rules(patterns)
        
        if not rules:
            print("\n⚠️  No patterns detected. Need more feedback.")
            return
        
        # Update response generator
        self.update_response_generator(rules)
        
        print("\n" + "="*80)
        print("LEARNING COMPLETE")
        print("="*80)
        print(f"Generated {len(rules)} new rules from {bad} bad responses")
        print("Chatbot will now avoid these mistakes!")
        print("="*80 + "\n")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ACE Engine - Learn from feedback')
    parser.add_argument('--learn', action='store_true', help='Analyze feedback and generate rules')
    
    args = parser.parse_args()
    
    engine = ACEEngine()
    
    if args.learn:
        engine.learn()
    else:
        print("Usage: python3 ace_engine.py --learn")

if __name__ == '__main__':
    main()

