#!/usr/bin/env python3
"""
rag_retriever.py - Modern RAG retrieval system
Prioritizes main kits: XL V5 > V5, Core XL first
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict


class RAGRetriever:
    """
    Hybrid RAG retrieval system that combines:
    1. Vector semantic search (meaning-based)
    2. Keyword/lexical search (exact matching)
    3. Priority-based ranking (main kits first)
    4. Cross-signal fusion (combine all signals)
    """
    
    def __init__(self, vector_store=None):
        self.vector_store = vector_store
        self.products = []
        self.product_index = {}
        self.canonical_map = {}
        self.business_rules = {}
        
        # MAIN KITS - HIGHEST PRIORITY (in order of recommendation)
        self.main_kits_priority = [
            # Concentrates (in priority order)
            ('xl_core_deluxe', 'XL Deluxe Core eRig Kit- Now with 6 Heat Settings', 1),
            ('xl_core_recycler', 'XL Recycler Top Core Deluxe eRig', 2),
            ('v5_xl', 'Divine Crossing XL v5 Rebuildable Concentrate Heater', 3),  # XL before regular
            ('v5', 'Divine Crossing v5 Rebuildable Concentrate Heater', 4),
            ('v5_xl_bundle', 'XL v5 Rebuildable Heater, Pico Plus & Hubble Bubble', 5),
            ('v5_pico', 'Divine Crossing v5 Rebuildable Heater & Pico Plus', 6),
            
            # Dry Herb (in priority order)
            ('ruby_twist', 'Ruby Twist Injector - Dry Herb Desktop Kit', 1),
            ('gen2_dc', 'Gen 2 DC Ceramic Rebuildable Dry Herb Heater', 2),
        ]
        
        # Retrieval weights (tunable)
        self.weights = {
            'semantic': 0.4,
            'lexical': 0.3,
            'priority': 0.2,
            'business_rules': 0.1
        }
    
    def load_products(self, products: List[Dict], business_rules: Dict = None):
        """Load products and build indices"""
        self.products = products
        self.business_rules = business_rules or {}
        
        # Build product index (handle missing 'id' field)
        for i, product in enumerate(products):
            product_id = product.get('id', product.get('name', f'product_{i}'))
            self.product_index[product_id] = product
            # Store the ID back in the product for later use
            if 'id' not in product:
                product['id'] = product_id
        
        # Build canonical mappings
        self._build_canonical_map()
        
        print(f"✅ RAG Retriever loaded {len(products)} products")
    
    def _build_canonical_map(self):
        """Build canonical product name mappings for main kits"""
        
        # Map common searches to main kit products
        self.canonical_map = {
            # V5 XL mappings (prioritize XL over regular)
            'v5 xl': 'v5_xl',
            'v5xl': 'v5_xl',
            'xl v5': 'v5_xl',
            'v 5 xl': 'v5_xl',
            'v5 extra large': 'v5_xl',
            
            # V5 mappings (only match when NOT asking for XL)
            'v5': 'v5_xl',  # Default to XL when just saying "v5"
            'v 5': 'v5_xl',
            'version 5': 'v5_xl',
            'divine crossing v5': 'v5_xl',
            
            # Core mappings
            'core': 'xl_core_deluxe',
            'core deluxe': 'xl_core_deluxe',
            'xl core': 'xl_core_deluxe',
            'core xl': 'xl_core_deluxe',
            'xl deluxe': 'xl_core_deluxe',
            'core erig': 'xl_core_deluxe',
            'erig': 'xl_core_deluxe',
            
            # Dry herb mappings
            'ruby': 'ruby_twist',
            'ruby twist': 'ruby_twist',
            'ball vape': 'ruby_twist',
            'dry herb': 'ruby_twist',
            'flower': 'ruby_twist',
            
            'gen 2': 'gen2_dc',
            'gen2': 'gen2_dc',
            'generation 2': 'gen2_dc',
        }
        
        print(f"✅ Built {len(self.canonical_map)} canonical mappings")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Main retrieval method - prioritizes main kits
        V5 XL always comes before V5
        """
        query_lower = query.lower().strip()
        
        # STAGE 0: Check for main kit queries
        main_kit_results = self._check_main_kits(query_lower)
        if main_kit_results:
            print(f"🎯 MAIN KIT MATCH: Found {len(main_kit_results)} main products")
            return main_kit_results[:top_k]
        
        # STAGE 1: Semantic + Keyword hybrid search
        all_results = []
        
        # Get semantic results if available
        if self.vector_store and self.vector_store.embeddings:
            semantic_results = self.vector_store.semantic_search(query_lower, top_k=20)
            for product_id, score in semantic_results:
                product = self.vector_store.get_product(product_id)
                if product:
                    all_results.append((product, score * 100, 'semantic'))
        
        # Get keyword results
        keyword_results = self._keyword_search(query_lower)
        for product, score in keyword_results:
            all_results.append((product, score, 'keyword'))
        
        if not all_results:
            return []
        
        # STAGE 2: Merge and deduplicate
        seen = set()
        merged = []
        for product, score, source in all_results:
            prod_id = product.get('id', product.get('name'))
            if prod_id not in seen:
                seen.add(prod_id)
                merged.append((product, score))
        
        # STAGE 3: Rerank with priority boost
        reranked = self._rerank_with_priority(merged, query_lower, context)
        
        # STAGE 4: Filter out replacement parts
        filtered = self._filter_accessories(reranked, query_lower)
        
        return filtered[:top_k]
    
    def _check_main_kits(self, query: str) -> List[Dict]:
        """Check if query is asking about main kits - XL V5 always first"""
        results = []
        
        # Check for material type first
        is_flower = any(w in query for w in ['flower', 'dry herb', 'herb', 'bud'])
        is_concentrate = any(w in query for w in ['concentrate', 'wax', 'dab', 'rosin', 'shatter', 'oil', 'hash', 'resin'])
        
        # Beginner query
        is_beginner = any(w in query for w in ['beginner', 'new', 'first time', 'starter', 'easy'])
        
        # If asking about flower
        if is_flower and not is_concentrate:
            # Show Ruby Twist and Gen 2 DC
            for product in self.products:
                name = product.get('name', '')
                if 'Ruby Twist Injector - Dry Herb Desktop Kit' in name:
                    results.append(product)
                elif 'Gen 2 DC Ceramic Rebuildable Dry Herb Heater' in name and 'Wholesale' not in name:
                    results.append(product)
            if results:
                return results
        
        # If asking specifically about v5 (prioritize XL)
        if 'v5' in query or 'v 5' in query:
            # XL V5 FIRST
            priority_names = [
                'Divine Crossing XL v5 Rebuildable Concentrate Heater',
                'XL v5 Rebuildable Heater, Pico Plus & Hubble Bubble',
                'Divine Crossing v5 Rebuildable Heater & Pico Plus',
                'Divine Crossing v5 Rebuildable Concentrate Heater',
            ]
            
            for priority_name in priority_names:
                for product in self.products:
                    name = product.get('name', '')
                    if priority_name in name:
                        results.append(product)
                        if len(results) >= 4:
                            return results
            
            if results:
                return results
        
        # If asking about concentrates or general beginner
        if is_concentrate or 'vaporizer' in query or 'vape' in query or is_beginner:
            # Core first for beginners, then V5 XL
            priority_names = [
                'XL Deluxe Core eRig Kit- Now with 6 Heat Settings',
                'XL Recycler Top Core Deluxe eRig',
                'Divine Crossing XL v5 Rebuildable Concentrate Heater',  # XL before regular
                'Divine Crossing v5 Rebuildable Heater & Pico Plus',
            ]
            
            for priority_name in priority_names:
                for product in self.products:
                    name = product.get('name', '')
                    if priority_name in name:
                        results.append(product)
                        if len(results) >= 4:
                            return results
            
            if results:
                return results
        
        return results
    
    def _keyword_search(self, query: str) -> List[Tuple[Dict, float]]:
        """Simple keyword search"""
        results = []
        query_words = query.lower().split()
        
        for product in self.products:
            score = 0
            name = product.get('name', '').lower()
            desc = product.get('description', '').lower()
            
            # Check query words in name
            for word in query_words:
                if len(word) > 2:  # Skip short words
                    if word in name:
                        score += 100
                    elif word in desc:
                        score += 30
            
            if score > 0:
                results.append((product, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:20]
    
    def _rerank_with_priority(self, candidates: List[Tuple[Dict, float]], query: str, context: Optional[Dict]) -> List[Dict]:
        """Rerank with main kit priority boost - XL V5 > V5"""
        scored = []
        
        for product, base_score in candidates:
            score = base_score
            name = product.get('name', '')
            
            # MASSIVE BOOST for main kits (with priority order)
            if 'XL Deluxe Core eRig Kit' in name:
                score += 15000  # Highest for beginners
            elif 'XL Recycler Top Core Deluxe' in name:
                score += 14000
            elif 'Divine Crossing XL v5' in name:
                score += 13000  # XL V5 higher than regular V5
            elif 'Divine Crossing v5 Rebuildable Heater & Pico Plus' in name:
                score += 12000
            elif 'XL v5 Rebuildable Heater, Pico Plus & Hubble Bubble' in name:
                score += 11000
            elif 'Divine Crossing v5 Rebuildable Concentrate Heater' == name:
                score += 10000  # Regular V5 lower than XL
            elif 'Ruby Twist Injector' in name:
                score += 15000  # Top for flower
            elif 'Gen 2 DC Ceramic' in name and 'Wholesale' not in name:
                score += 14000
            
            # PENALIZE replacement parts and accessories
            category = product.get('category', '').lower()
            if 'replacement' in name.lower() or 'spare' in name.lower():
                score -= 5000
            if category == 'replacement_parts':
                score -= 5000
            
            # Boost based on material match
            is_flower_query = any(w in query for w in ['flower', 'dry herb', 'herb', 'bud'])
            is_concentrate_query = any(w in query for w in ['concentrate', 'wax', 'dab', 'rosin', 'hash', 'resin', 'shatter'])
            
            if is_flower_query and ('Ruby Twist' in name or 'Gen 2 DC' in name):
                score += 8000
            elif is_flower_query and 'v5' in name.lower():
                score -= 3000  # Don't show V5 for flower
            
            if is_concentrate_query and ('Core' in name or 'v5' in name.lower()):
                score += 8000
            elif is_concentrate_query and ('Ruby' in name or 'Gen 2' in name):
                score -= 3000  # Don't show dry herb for concentrates
            
            scored.append((product, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored]
    
    def _filter_accessories(self, products: List[Dict], query: str) -> List[Dict]:
        """Filter out accessories unless specifically asked"""
        
        # If asking for accessories, don't filter
        accessory_words = ['replacement', 'spare', 'part', 'accessory', 'tip', 'cap', 'bowl']
        if any(word in query for word in accessory_words):
            return products
        
        # Otherwise, remove replacement parts
        filtered = []
        for product in products:
            name = product.get('name', '').lower()
            category = product.get('category', '').lower()
            
            # Skip replacement parts
            if 'replacement' in name or 'spare' in name:
                continue
            if category == 'replacement_parts':
                continue
            
            filtered.append(product)
        
        return filtered
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get product by ID"""
        return self.product_index.get(product_id)


def test_rag_retriever():
    """Test the RAG retriever"""
    print("\n" + "="*70)
    print("RAG RETRIEVER TEST")
    print("="*70 + "\n")
    print("Run this test through product_database.py test instead")


if __name__ == "__main__":
    test_rag_retriever()
