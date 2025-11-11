#!/usr/bin/env python3
"""
rag_retriever.py - Modern RAG retrieval system
Combines semantic search + keyword matching + business rules + reranking
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
    3. Priority-based ranking (business rules)
    4. Cross-signal fusion (combine all signals)
    """
    
    def __init__(self, vector_store=None):
        self.vector_store = vector_store
        self.products = []
        self.product_index = {}
        self.canonical_map = {}
        self.business_rules = {}
        
        # Retrieval weights (tunable)
        self.weights = {
            'semantic': 0.4,      # Vector similarity weight
            'lexical': 0.3,       # Keyword matching weight
            'priority': 0.2,      # Priority boost weight
            'business_rules': 0.1 # Business logic weight
        }
    
    def load_products(self, products: List[Dict], business_rules: Dict = None):
        """Load products and build indices"""
        self.products = products
        self.business_rules = business_rules or {}
        
        # Build product index
        for product in products:
            self.product_index[product['id']] = product
        
        # Build canonical mappings
        self._build_canonical_map()
        
        print(f"✅ RAG Retriever loaded {len(products)} products")
    
    def _extract_product_nouns(self, query: str):
        """Extract product keywords"""
        keywords_dict = {
            'materials': ['hemp', 'silk', 'cotton', 'bamboo'],
            'clothing': ['shirt', 'hoodie', 'boxer', 'pants', 'tank', 'fleece'],
            'vape_products': ['v5', 'core', 'tug', 'fogger', 'lightning', 'ruby'],
            'accessories': ['jar', 'glass', 'bubbler', 'battery', 'charger'],
        }
        found = []
        query_lower = query.lower()
        for category, keywords in keywords_dict.items():
            for kw in keywords:
                if kw in query_lower:
                    found.append(kw)
        return found
    
    def _title_first_search(self, query: str, top_k: int):
        """Search product titles for extracted keywords"""
        keywords = self._extract_product_nouns(query)
        if not keywords:
            return []
        
        matches = []
        for product in self.products:
            score = sum(1 for kw in keywords if kw in product['name'].lower())
            if score > 0:
                matches.append((product, score))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches[:top_k]]
    
    def _build_canonical_map(self):
        """Build canonical product name mappings"""
        main_products = [p for p in self.products if p.get('priority') == 1]
        
        for product in main_products:
            name = product['name']
            name_lower = name.lower()
            
            # V5 XL mappings
            if 'divine crossing xl v5' in name_lower and 'rebuildable' in name_lower:
                mappings = [
                    'v5', 'v5 xl', 'v5xl', 'xl v5', 'v 5', 'v 5 xl',
                    'divine crossing v5', 'dc v5', 'divine v5',
                    'v5 rebuildable', 'v5 heater', 'v5 atomizer'
                ]
                for m in mappings:
                    self.canonical_map[m] = product['id']
            
            # Core Deluxe mappings
            elif 'core deluxe' in name_lower and 'erig' in name_lower:
                mappings = [
                    'core', 'core deluxe', 'core xl', 'xl core',
                    'deluxe core', 'core 2.0', 'core erig', 'xl deluxe',
                    'xl erig', 'core 2', 'deluxe'
                ]
                for m in mappings:
                    self.canonical_map[m] = product['id']
            
            # Nice Dreamz mappings
            elif 'nice dreamz' in name_lower and 'fogger' in name_lower:
                mappings = [
                    'nice dreamz', 'nice dreams', 'dreamz', 'dreams',
                    'fogger', 'nice dreamz fogger', 'dreamz fogger'
                ]
                for m in mappings:
                    self.canonical_map[m] = product['id']
            
            # Ruby Twist mappings
            elif 'ruby twist' in name_lower and 'ball vape' in name_lower:
                mappings = [
                    'ruby', 'ruby twist', 'twist', 'ball vape',
                    'ruby ball vape', 'ruby ball', 'desktop vape'
                ]
                for m in mappings:
                    self.canonical_map[m] = product['id']
            
            # Gen 2 DC mappings
            elif 'gen 2 dc' in name_lower and 'ceramic' in name_lower and 'wholesale' not in name_lower:
                mappings = [
                    'gen 2', 'gen 2 dc', 'gen2', 'generation 2',
                    'dc gen 2', 'gen 2 heater'
                ]
                for m in mappings:
                    self.canonical_map[m] = product['id']
            
            # Cub mappings
            elif name_lower.startswith('the cub') and 'bundle' not in name_lower:
                mappings = ['cub', 'the cub', 'cub adapter', 'cub base']
                for m in mappings:
                    self.canonical_map[m] = product['id']
        
        print(f"✅ Built {len(self.canonical_map)} canonical mappings")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Main retrieval method using hybrid search.
        
        Process:
        1. Check canonical match (instant return)
        2. Get semantic candidates (vector search)
        3. Get lexical candidates (keyword search)
        4. Fuse and rerank all candidates
        5. Apply business rules
        6. Return top_k results
        """
        query_lower = query.lower().strip()

        # STAGE 0: Title keyword search (FIRST - most direct match)
        query_words = set(query_lower.split())
        title_matches = []
        
        for product in self.products:
            title_lower = product['name'].lower()
            title_words = set(title_lower.split())
            matching_words = query_words & title_words
            
            if matching_words and len(matching_words) >= len(query_words) * 0.5:  # At least 50% of words match
                score = len(matching_words) / len(query_words)
                title_matches.append((product, score))
        
        if title_matches:
            title_matches.sort(key=lambda x: x[1], reverse=True)
            results = [m[0] for m in title_matches[:top_k]]
            print(f"📌 Found {len(results)} title matches for '{query}'")
            return results
        
        
        # STAGE 1: Canonical exact match (highest confidence)
        canonical_id = self.canonical_map.get(query_lower)
        if canonical_id:
            product = self.product_index[canonical_id]
            print(f"🎯 CANONICAL MATCH: {product['name']}")
            return [product]
        
        # STAGE 1.5: Check for comparison queries (v5 vs v5 xl)
        if ' vs ' in query_lower or ' versus ' in query_lower or 'difference between' in query_lower:
            # Extract both product names
            if 'v5 xl' in query_lower and 'v5' in query_lower:
                v5_id = self.canonical_map.get('v5')
                v5xl_id = self.canonical_map.get('v5 xl')
                if v5_id and v5xl_id:
                    print(f"🎯 COMPARISON MATCH: V5 vs V5 XL")
                    return [self.product_index[v5xl_id]]  # Return XL since it's the upgrade
        
        # STAGE 2: Hybrid retrieval
        candidates = self._get_hybrid_candidates(query, top_k * 3)
        
        # DEDUPLICATE by URL (remove duplicate products)
        candidates = self._deduplicate_by_url(candidates)
        
        # FILTER OUT WRONG PRODUCTS BEFORE RANKING
        query_lower = query.lower()
        
        # Filter 1: Dry herb queries - ONLY Ruby Twist and Gen 2
        if any(x in query_lower for x in ['flower', 'herb', 'dry herb', 'bud']):
            candidates = [c for c in candidates if any(x in c.get('name', '').lower() for x in ['ruby twist', 'gen 2', 'dc gen'])]
        
        # Filter 2: Remove SiC products UNLESS specifically asking about SiC/upgrades
        elif not any(x in query_lower for x in ['sic', 'silicon carbide', 'insert', 'upgrade', 'cup option']):
            candidates = [c for c in candidates if 'sic' not in c.get('name', '').lower() and 'silicon carbide' not in c.get('name', '').lower()]  # Get more candidates for reranking
        
        # STAGE 3: Rerank candidates using multiple signals
        ranked_results = self._rerank_candidates(query, candidates, context)
        
        # STAGE 4: Apply business rules and filters
        filtered_results = self._apply_business_rules(query, ranked_results)
        
        # Return top K
        final_results = filtered_results[:top_k]
        
        if final_results:
            print(f"🔍 Retrieved {len(final_results)} products for '{query}'")
            print(f"   Top: {final_results[0]['name'][:50]}...")
        
        return final_results
    
    def _get_hybrid_candidates(self, query: str, top_k: int) -> List[Dict]:
        """Get candidates from both semantic and lexical search"""
        candidates_dict = {}  # product_id -> (product, score)
        query_lower = query.lower()
        
        # CRITICAL FIX: For concentrate queries, force include priority products
        concentrate_keywords = ['wax', 'concentrate', 'dabs', 'dab', 'oil', 'shatter', 'budder', 'rosin']
        is_concentrate_query = any(kw in query_lower for kw in concentrate_keywords)
        
        if is_concentrate_query:
            # Force return ONLY the 5 priority concentrate products
            priority_products = self._get_priority_concentrate_products()
            if priority_products:
                return priority_products
        
        # Regular hybrid search for non-concentrate queries
        concentrate_keywords = ['wax', 'concentrate', 'dabs', 'dab', 'oil', 'shatter', 'budder', 'rosin',
                               'sauce', 'crumble', 'distillate', 'live resin', 'hash oil']
        is_concentrate_query = any(kw in query_lower for kw in concentrate_keywords)
        
        if is_concentrate_query:
            # STRICT WHITELIST: Only force these exact main products into candidates
            for product in self.products:
                if product.get('priority') in [1, 1.5]:
                    name = product['name']
                    
                    # Check against strict whitelist - ONLY complete vaporizers
                    is_main_vaporizer = (
                        # V5 XL Complete Kit (TOP PRIORITY)
                        ('XL v5 Rebuildable Heater, Pico Plus & Hubble Bubble Kit' in name) or
                        
                        # Core Deluxe Complete Kit
                        ('XL Deluxe Core eRig Kit' in name and 'Heat Settings' in name) or
                        
                        # V5 XL Heater Only (for existing battery owners)
                        ('Divine Crossing XL v5 Rebuildable Concentrate Heater' == name) or
                        
                        # Lightning Pen
                        ('Divine Crossing Lightning Pen Stainless Steel Diffuser for Concentrate' in name and 'Replacement' not in name) or
                        ('Lightning Pen Stainless Steel Diffuser for Concentrates (Past customer' in name) or
                        
                        # Nice Dreamz Fogger (main unit only, not accessories)
                        ('Nice Dreamz Fogger' in name and 'Glass Top Accessories' not in name and 'Replacement' not in name) or
                        
                        # The Tug
                        ('The Tug' in name and 'Replacement' not in name and 'TUG 2.0' not in name)
                    )
                    
                    # EXCLUDE replacement parts, accessories, upgrades
                    is_excluded = (
                        'Replacement' in name or
                        'replacement' in name.lower() or
                        'Cup Sets' in name or
                        'SIC' in name or
                        'Silicon Carbide' in name or
                        'Glass Top Accessories' in name or
                        'Polished XL' in name
                    )
                    
                    if is_main_vaporizer and not is_excluded:
                        product_id = product['id']
                        # Give higher base score to complete kits
                        base_score = 1.0 if 'Kit' in name else 0.7
                        candidates_dict[product_id] = (product, base_score)
        
        # Get semantic candidates (if available)
        if self.vector_store and self.vector_store.embeddings:
            semantic_results = self.vector_store.semantic_search(query, top_k=top_k)
            
            for product_id, score in semantic_results:
                if product_id in self.product_index:
                    product = self.product_index[product_id]
                    weighted_score = score * self.weights['semantic']
                    
                    if product_id in candidates_dict:
                        # Add to existing score
                        candidates_dict[product_id] = (product, candidates_dict[product_id][1] + weighted_score)
                    else:
                        candidates_dict[product_id] = (product, weighted_score)
        
        # Get lexical candidates (keyword matching)
        lexical_results = self._lexical_search(query, top_k=top_k)
        
        for product, score in lexical_results:
            product_id = product['id']
            weighted_score = score * self.weights['lexical']
            
            if product_id in candidates_dict:
                # Combine scores if product found by both methods
                existing_score = candidates_dict[product_id][1]
                candidates_dict[product_id] = (product, existing_score + weighted_score)
            else:
                candidates_dict[product_id] = (product, weighted_score)
        
        # Convert to list and sort by combined score
        candidates = [(p, s) for p, s in candidates_dict.values()]
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return [p for p, _ in candidates[:top_k]]
    
    def _lexical_search(self, query: str, top_k: int) -> List[Tuple[Dict, float]]:
        """Traditional keyword-based search"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        results = []
        
        for product in self.products:
            score = 0.0
            
            name = product['name'].lower()
            desc = product.get('description', '').lower()
            
            # Exact query in name
            if query_lower in name:
                score += 100
            
            # Exact query in description
            if query_lower in desc:
                score += 30
            
            # Word matching
            name_words = set(re.findall(r'\b\w+\b', name))
            desc_words = set(re.findall(r'\b\w+\b', desc))
            
            # Calculate overlap
            name_overlap = len(query_words & name_words)
            desc_overlap = len(query_words & desc_words)
            
            score += name_overlap * 20
            score += desc_overlap * 5
            
            if score > 0:
                results.append((product, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _rerank_candidates(
        self,
        query: str,
        candidates: List[Dict],
        context: Optional[Dict]
    ) -> List[Dict]:
        """
        Rerank candidates using multiple signals:
        1. Priority level
        2. Relevance to query
        3. Business rules
        4. Context awareness
        """
        query_lower = query.lower()
        
        scored_candidates = []
        
        for product in candidates:
            score = 0.0
            
            # SIGNAL 1: Priority boost (most important)
            priority = product.get('priority', 999)
            priority_scores = {1: 1000, 1.5: 500, 2: 200, 3: -500}
            score += priority_scores.get(priority, 0) * self.weights['priority']
            
            # SIGNAL 2: Query relevance
            name = product['name'].lower()
            if query_lower == name:
                score += 500
            elif query_lower in name:
                score += 200
            
            # SIGNAL 3: Business rules
            category = product.get('category', '')
            
            # Penalize replacement parts unless asked
            if category == 'replacement_parts':
                if not any(w in query_lower for w in ['replacement', 'part', 'spare']):
                    score -= 1000
            
            # Penalize bundles unless asked
            if 'bundle' in name or 'kit' in name:
                if not any(w in query_lower for w in ['bundle', 'kit']):
                    score -= 300
            
            # SIGNAL 4: Special query boosts
            boosts = {
                'jar': 200, 'jars': 200,
                'uv': 150,
                'glass': 100,
                'battery': 100
            }
            
            # CRITICAL: Boost main products based on material type
            
            # Concentrate keywords (wax, dabs, rosin, etc)
            concentrate_keywords = ['wax', 'concentrate', 'dabs', 'dab', 'oil', 'shatter', 'budder', 'rosin',
                                   'sauce', 'crumble', 'distillate', 'live resin', 'hash oil']
            is_concentrate_query = any(kw in query_lower for kw in concentrate_keywords)
            
            # Dry herb keywords (flower only)
            flower_keywords = ['flower', 'dry herb', 'herb', 'bud']
            is_flower_query = any(kw in query_lower for kw in flower_keywords)
            
            # Concentrate vaporizers (V5, Core, Nice Dreamz, Tug, Lightning Pen)
            concentrate_devices = ['v5', 'core', 'nice dreamz', 'tug', 'lightning pen', 'deluxe']
            is_concentrate_device = any(dev in name for dev in concentrate_devices)
            
            # Flower vaporizers (Ruby Twist, Gen 2 DC)
            flower_devices = ['ruby twist', 'gen 2', 'dc gen']
            is_flower_device = any(dev in name for dev in flower_devices)
            
            # Boost concentrate devices for concentrate queries
            if is_concentrate_query and is_concentrate_device and product.get('priority') in [1, 1.5]:
                score += 800
            
            # Boost flower devices for flower queries
            if is_flower_query and is_flower_device:
                score += 800
            
            # PENALIZE wrong device type for the query
            if is_concentrate_query and is_flower_device:
                score -= 1000  # Don't show Ruby Twist for "wax"
            
            if is_flower_query and is_concentrate_device:
                score -= 1000  # Don't show V5 for "flower"
            
            for keyword, boost in boosts.items():
                if keyword in query_lower and keyword in name:
                    score += boost
            
            # SIGNAL 5: Context awareness (if provided)
            if context:
                last_category = context.get('last_category')
                if last_category and last_category == category:
                    score += 100  # Boost if same category as last query
            
            scored_candidates.append((product, score))
        
        # Sort by final score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return [p for p, _ in scored_candidates]
    
    def _deduplicate_by_url(self, products: List[Dict]) -> List[Dict]:
        """Remove duplicate products by URL, keeping highest priority"""
        seen_urls = {}
        for product in products:
            url = product.get('url', '')
            if not url:
                continue
            
            if url not in seen_urls:
                seen_urls[url] = product
            else:
                # Keep product with higher priority (lower number = higher priority)
                existing_priority = seen_urls[url].get('priority', 999)
                current_priority = product.get('priority', 999)
                if current_priority < existing_priority:
                    seen_urls[url] = product
        
        return list(seen_urls.values())
    
    def _get_priority_concentrate_products(self) -> List[Dict]:
        """Get the exact 5 priority concentrate products in order"""
        priority_urls = [
            "https://ineedhemp.com/product/divine-crossing-xl-v5-rebuildable-heater-istick-pico-plus-power-supply/",
            "https://ineedhemp.com/product/recycler-top-core-erig/",
            "https://ineedhemp.com/product/the-original-nice-dreamz-essential-oil-fogger/",
            "https://ineedhemp.com/product/crossing-tug-2-0-e-rig/",
            "https://ineedhemp.com/product/lightning-pen-stainless-steel-diffuser-for-concentrates/"
        ]
        
        priority_products = []
        for url in priority_urls:
            for product in self.products:
                if product.get('url') == url:
                    priority_products.append(product)
                    break
        
        return priority_products
    
    def _apply_business_rules(self, query: str, products: List[Dict]) -> List[Dict]:
        """Apply business rules from metadata"""
        query_lower = query.lower()
        
        # Rule 1: Never show replacement parts unless explicitly asked
        if not any(w in query_lower for w in ['replacement', 'part', 'spare', 'coil']):
            products = [p for p in products if p.get('category') != 'replacement_parts']
        
        # Rule 2: Prioritize main products over accessories
        main_products = [p for p in products if p.get('priority') == 1]
        accessories = [p for p in products if p.get('priority') != 1]
        
        # If we have main products, put them first
        if main_products:
            return main_products + accessories
        
        return products
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get product by ID"""
        return self.product_index.get(product_id)


# Convenience function for testing
def test_rag_retriever():
    """Test the RAG retriever"""
    print("\n" + "="*70)
    print("RAG RETRIEVER TEST")
    print("="*70 + "\n")
    
    # Load products
    with open('products_organized.json', 'r') as f:
        data = json.load(f)
    
    categories = data.get('categories', {})
    products = []
    
    for cat_name, cat_data in categories.items():
        for product in cat_data.get('products', []):
            product['category'] = cat_name
            product['category_display'] = cat_data.get('display_name')
            product['priority'] = cat_data.get('priority', 2)
            products.append(product)
    
    # Create retriever
    retriever = RAGRetriever()
    retriever.load_products(products, data.get('metadata', {}).get('business_rules'))
    
    # Test queries
    test_queries = [
        "v5",
        "v5 xl",
        "core",
        "jars",
        "what is the v5 xl"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = retriever.retrieve(query, top_k=3)
        
        for i, product in enumerate(results, 1):
            print(f"  {i}. {product['name'][:60]}...")


if __name__ == "__main__":
    test_rag_retriever()
