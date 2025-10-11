#!/usr/bin/env python3
"""
Query Classifier - Detects user intent and query type with serious topic detection
"""

from typing import Dict, List, Optional

class QueryClassifier:
    def __init__(self):
        """Initialize classification patterns"""
        
        # SERIOUS TOPICS - require empathy, NO SALES
        self.serious_keywords = [
            'suicide', 'suicidal', 'kill myself', 'kill themselves', 'kill herself', 'kill himself',
            'end my life', 'end it all', 'want to die', 'better off dead', 'no reason to live',
            'died', 'death', 'passed away', 'funeral', 'mourning', 'grief', 'grieving',
            'cancer', 'terminal', 'illness', 'hospital', 'hospice', 'dying',
            'depressed', 'depression', 'hopeless', 'can\'t go on', 'no point living',
            'abuse', 'abused', 'hurt myself', 'self harm', 'cutting', 'self-harm',
            'overdose', 'pills to end', 'hanging myself', 'jump off'
        ]
        
        # LIGHT OFFTOPIC - allow humor + gentle redirect + sales
        self.light_offtopic_keywords = [
            'weather', 'rain', 'snow', 'sunny', 'cold outside', 'hot outside',
            'sports', 'football', 'basketball', 'baseball', 'soccer', 'game score',
            'movie', 'film', 'show', 'netflix', 'tv series', 'actor', 'actress',
            'food', 'pizza', 'burger', 'hungry', 'restaurant', 'cooking',
            'joke', 'funny', 'laugh', 'haha', 'lol', 'tell me a joke',
            'music', 'song', 'band', 'concert', 'album',
            'video game', 'xbox', 'playstation', 'nintendo', 'gaming'
        ]
        
        self.patterns = {
            'troubleshooting': {
                'keywords': [
                    'not working', 'broken', 'issue', 'problem', 'help', 'fix',
                    'resistance', 'ohm', 'puddle', 'leak', 'atomizer short',
                    'no atomizer', 'flashing', 'error', 'wrong', "won't", "doesn't",
                    'temperature', 'temp', 'wont connect', 'low temp', 'no vapor',
                    'cracked', 'crack', 'broken glass'
                ],
                'priority': 10  # Highest priority
            },
            
            'recommendation': {
                'keywords': [
                    'recommend', 'suggest', 'best', 'should i', 'which one',
                    'what should', 'better', 'difference', 'compare', 'vs',
                    'beginner', 'starter', 'first time', 'new to', 'good for',
                    'buying', 'purchase', 'looking for'
                ],
                'priority': 8
            },
            
            'parts': {
                'keywords': [
                    'spare', 'replacement', 'extra', 'heater', 'coil', 'cup',
                    'o-ring', 'oring', 'screw', 'tool', 'part', 'need a',
                    'broken heater', 'new coil', 'replace'
                ],
                'priority': 9
            },
            
            'compatibility': {
                'keywords': [
                    'compatible', 'work with', 'fit', 'use with', 'pair',
                    'does it work', 'will it fit', 'can i use', 'match',
                    'goes with', 'attachment'
                ],
                'priority': 7
            },
            
            'pricing': {
                'keywords': [
                    'price', 'cost', 'how much', 'expensive', 'cheap',
                    'discount', 'coupon', 'code', 'sale', 'deal',
                    'budget', 'affordable', 'wholesale', 'bulk'
                ],
                'priority': 6
            },
            
            'product_inquiry': {
                'keywords': [
                    'what is', 'tell me about', 'explain', 'describe',
                    'info', 'information', 'details', 'specs', 'features',
                    'how does', 'whats', "what's the"
                ],
                'priority': 5
            },
            
            'off_topic': {
                'keywords': [],  # Detected separately via light_offtopic check
                'priority': 1,
                'exclude_if': ['vape', 'vapor', 'core', 'atomizer']  # Not off-topic if vape context
            },
            
            'general': {
                'keywords': [],  # Catch-all
                'priority': 2
            }
        }
        
        print("✓ Query Classifier initialized with serious topic detection")
    
    def is_serious_topic(self, query: str) -> bool:
        """Detect if query contains serious/emotional topics that need empathy"""
        query_lower = query.lower().strip()
        return any(keyword in query_lower for keyword in self.serious_keywords)
    
    def is_light_offtopic(self, query: str) -> bool:
        """Detect if query is light offtopic (humor appropriate)"""
        query_lower = query.lower().strip()
        # Exclude if vape-related terms present
        vape_terms = ['vape', 'vapor', 'core', 'atomizer', 'heater', 'coil', 'v5', 'v4', 'ruby', 'cub']
        has_vape_context = any(term in query_lower for term in vape_terms)
        
        if has_vape_context:
            return False
        
        return any(keyword in query_lower for keyword in self.light_offtopic_keywords)
    
    def classify(self, query: str) -> Dict:
        """
        Classify the query and return intent + confidence
        
        Returns:
            {
                'intent': 'troubleshooting',
                'confidence': 0.85,
                'secondary_intent': 'parts',
                'is_off_topic': False,
                'is_serious': False,
                'allow_humor': False
            }
        """
        query_lower = query.lower().strip()
        
        if not query_lower:
            return {
                'intent': 'general',
                'confidence': 0.0,
                'secondary_intent': None,
                'is_off_topic': False,
                'is_serious': False,
                'allow_humor': False
            }
        
        # CHECK FOR SERIOUS TOPICS FIRST - HIGHEST PRIORITY
        if self.is_serious_topic(query):
            return {
                'intent': 'serious_topic',
                'confidence': 1.0,
                'secondary_intent': None,
                'is_off_topic': False,
                'is_serious': True,
                'allow_humor': False,
                'requires_empathy': True
            }
        
        # Check for light offtopic
        if self.is_light_offtopic(query):
            return {
                'intent': 'light_offtopic',
                'confidence': 0.9,
                'secondary_intent': None,
                'is_off_topic': True,
                'is_serious': False,
                'allow_humor': True
            }
        
        # Score each intent (normal classification)
        scores = {}
        
        for intent_name, intent_data in self.patterns.items():
            score = 0
            keywords = intent_data.get('keywords', [])
            priority = intent_data.get('priority', 1)
            
            # Check for keyword matches
            for keyword in keywords:
                if keyword in query_lower:
                    score += priority
            
            # Handle exclusions (for off_topic)
            if 'exclude_if' in intent_data:
                for exclude_word in intent_data['exclude_if']:
                    if exclude_word in query_lower:
                        score = 0  # Nullify the score
                        break
            
            scores[intent_name] = score
        
        # Sort by score
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Primary intent
        primary_intent = sorted_intents[0][0] if sorted_intents[0][1] > 0 else 'general'
        primary_score = sorted_intents[0][1]
        
        # Secondary intent
        secondary_intent = sorted_intents[1][0] if len(sorted_intents) > 1 and sorted_intents[1][1] > 0 else None
        
        # Calculate confidence (normalize score)
        max_possible_score = max([p['priority'] for p in self.patterns.values()]) * 3  # Assume max 3 keyword matches
        confidence = min(primary_score / max_possible_score, 1.0) if primary_score > 0 else 0.5
        
        # Check if off-topic
        is_off_topic = primary_intent == 'off_topic' and confidence > 0.3
        
        return {
            'intent': primary_intent,
            'confidence': round(confidence, 2),
            'secondary_intent': secondary_intent,
            'is_off_topic': is_off_topic,
            'is_serious': False,
            'allow_humor': False,
            'all_scores': scores  # For debugging
        }
    
    def get_response_hints(self, classification: Dict) -> List[str]:
        """
        Get response hints based on classification
        Returns list of guidelines for the LLM
        """
        intent = classification['intent']
        hints = []
        
        if intent == 'serious_topic':
            # This should never reach LLM - handled by hard-coded response
            hints = [
                "Show empathy and compassion",
                "Provide mental health resources",
                "DO NOT mention products or sales",
                "Be human and caring"
            ]
        
        elif intent == 'light_offtopic':
            hints = [
                "Use brief humor to acknowledge topic",
                "Make a light connection to products",
                "Gentle redirect with product recommendation",
                "Include discount code naturally"
            ]
        
        elif intent == 'troubleshooting':
            hints = [
                "Start with lead wire check (90% of issues)",
                "Then check resistance (0.42-0.51Ω)",
                "Mention Discord/Reddit for real-time help",
                "Never suggest buying new unless absolutely necessary",
                "Recommend Cub adapter ONLY if customer has Core/Nice Dreamz/TUG"
            ]
        
        elif intent == 'recommendation':
            hints = [
                "Ask about priorities: ease, portability, performance, budget",
                "Core 2.0 Deluxe for beginners (most recommended)",
                "Lightning Pen for portable/discreet",
                "Ruby Twist for best dry herb experience",
                "Always mention 'thankyou10' discount code"
            ]
        
        elif intent == 'parts':
            hints = [
                "Find exact part from search results",
                "Mention parts sold very cheap",
                "All devices have spare parts available",
                "Include product URL",
                "Mention 'thankyou10' code"
            ]
        
        elif intent == 'compatibility':
            hints = [
                "Be specific about what works with what",
                "Mention portable e-nail setup (Cub + Core coil + 510 extension)",
                "v5 works with bottomless bangers",
                "Lightning Pen is standalone ONLY (never on mod)",
                "Include Discord link for complex compatibility"
            ]
        
        elif intent == 'pricing':
            hints = [
                "Show exact prices from search results",
                "Always mention 'thankyou10' for 10% off",
                "Mention kits save money vs buying separate",
                "Wholesale available for UV jars and hemp clothing"
            ]
        
        elif intent == 'product_inquiry':
            hints = [
                "Provide clear, concise product description",
                "Mention key features and use case",
                "Include price and URL",
                "Suggest complementary products if relevant"
            ]
        
        elif intent == 'off_topic':
            hints = [
                "Use humor response template",
                "Pivot naturally back to products",
                "Match topic to relevant product (movies→Nice Dreamz, portable→Lightning Pen)"
            ]
        
        else:  # general
            hints = [
                "Be helpful and friendly",
                "Ask clarifying questions if needed",
                "Mention discount code naturally"
            ]
        
        return hints
