#!/usr/bin/env python3
"""
rag_retriever.py - Modern RAG retrieval system
IMPROVED: Aggressive keyword matching for ALL product categories
Now matches ANY noun from user queries to product names (jars, shirts, hoodies, etc.)
"""

import json
import re
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict


class RAGRetriever:
    """
    Hybrid RAG retrieval system:
    1. Aggressive keyword index (auto-built from ALL product names)
    2. Vector semantic search (meaning-based)
    3. Keyword/lexical search (exact matching)
    4. Priority-based ranking (main kits first)
    5. Cross-signal fusion (combine all signals)
    """

    def __init__(self, vector_store=None):
        self.vector_store = vector_store
        self.products = []
        self.product_index = {}
        self.canonical_map = {}

        # NEW: Keyword-to-products index (auto-built from product names)
        self.keyword_index = defaultdict(list)

        # NEW: Category keywords for broad category matching
        self.category_keywords = {
            'hemp_clothing': ['hemp', 'clothing', 'clothes', 'apparel', 'shirt', 'shirts',
                              't-shirt', 'tshirt', 'hoodie', 'hoodies', 'pants', 'boxer',
                              'boxers', 'shorts', 'fleece', 'cargo', 'washcloth', 'digicam'],
            'jars': ['jar', 'jars', 'glass', 'uv', 'storage', 'container', 'puck'],
            'bubblers': ['bubbler', 'bubblers', 'hydratube', 'hydratubes', 'hydra tube',
                        'water attachment', 'water attachments', 'water filtration',
                        'hubble bubble', 'hubble'],
            'accessories': ['coil', 'cup', 'cap', 'tip', 'top',
                           'banger', 'nail', 'donut', 'heater', 'battery', 'mod', 'pico'],
            'vaporizers': ['vaporizer', 'vape', 'vapes', 'atomizer', 'erig', 'e-rig',
                          'enail', 'e-nail', 'diffuser'],
        }

        # NEW: Singular/plural mappings for better matching
        self.plural_map = {
            'jar': 'jars', 'jars': 'jar',
            'shirt': 'shirts', 'shirts': 'shirt',
            'hoodie': 'hoodies', 'hoodies': 'hoodie',
            'pant': 'pants', 'pants': 'pant',
            'boxer': 'boxers', 'boxers': 'boxer',
            'short': 'shorts', 'shorts': 'short',
            'vape': 'vapes', 'vapes': 'vape',
            'coil': 'coils', 'coils': 'coil',
            'cup': 'cups', 'cups': 'cup',
            'donut': 'donuts', 'donuts': 'donut',
            'washcloth': 'washcloths', 'washcloths': 'washcloth',
            'bubbler': 'bubblers', 'bubblers': 'bubbler',
            'hydratube': 'hydratubes', 'hydratubes': 'hydratube',
        }

        # NEW: Synonym mappings (different words for same thing)
        self.synonym_map = {
            # Bubbler/Hydratube/Water attachment are the same thing
            'bubbler': ['hydratube', 'hydra tube', 'water attachment', 'water filtration', 'glass attachment'],
            'hydratube': ['bubbler', 'hydra tube', 'water attachment', 'water filtration', 'glass attachment'],
            'water attachment': ['bubbler', 'hydratube', 'hydra tube', 'water filtration'],
            'water filtration': ['bubbler', 'hydratube', 'water attachment'],
            # Cup/Heater synonyms
            'heater cup': ['cup', 'crucible', 'insert'],
            'crucible': ['cup', 'heater cup', 'insert'],
        }

        # MAIN KITS - PRIORITY ORDER
        self.main_kits_priority = [
            # Concentrates (in recommendation order)
            ('xl_core_deluxe', 'XL Deluxe Core eRig Kit- Now with 6 Heat Settings', 1),
            ('xl_core_recycler', 'XL Recycler Top Core Deluxe eRig', 2),
            ('v5_xl', 'Divine Crossing XL v5 Rebuildable Concentrate Heater', 3),
            ('v5', 'Divine Crossing v5 Rebuildable Concentrate Heater', 4),
            ('v5_xl_bundle', 'XL v5 Rebuildable Heater, Pico Plus & Hubble Bubble', 5),
            ('v5_pico', 'Divine Crossing v5 Rebuildable Heater & Pico Plus', 6),

            # Dry Herb (in recommendation order)
            ('ruby_twist', 'Ruby Twist Injector - Dry Herb Desktop Kit', 1),
            ('gen2_dc', 'Gen 2 DC Ceramic Rebuildable Dry Herb Heater', 2),
        ]

        # Retrieval weights
        self.weights = {
            'semantic': 0.4,
            'lexical': 0.3,
            'priority': 0.2,
            'business_rules': 0.1
        }

        # Common stop words to ignore in keyword extraction
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'now', 'just', 'also', 'very', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'up', 'down', 'out', 'off', 'over',
            'under', 'again', 'further', 'then', 'once', 'here', 'there', 'any',
            'about', 'your', 'our', 'my', 'his', 'her', 'its', 'their', 'me',
            'him', 'us', 'them', 'kit', 'set', 'qty', 'available', 'wholesale',
        }
    
    def load_products(self, products: List[Dict], business_rules: Dict = None):
        """Load products and build indices"""
        self.products = products

        # Build product index (handle missing 'id' field)
        for i, product in enumerate(products):
            product_id = product.get('id', product.get('name', f'product_{i}'))
            self.product_index[product_id] = product
            if 'id' not in product:
                product['id'] = product_id

        # Build canonical mappings
        self._build_canonical_map()

        # NEW: Build aggressive keyword index from ALL product names
        self._build_keyword_index()

        print(f"✅ RAG Retriever loaded {len(products)} products")
        print(f"✅ Keyword index: {len(self.keyword_index)} unique keywords")

    def _build_keyword_index(self):
        """
        Build keyword-to-products index from ALL product names.
        This enables matching ANY noun (jars, shirts, hoodies, etc.) to products.
        """
        self.keyword_index = defaultdict(list)

        for product in self.products:
            name = product.get('name', '')
            category = product.get('category', '')
            product_id = product.get('id', name)

            # Extract keywords from product name
            keywords = self._extract_keywords(name)

            # Also add category as a keyword
            if category:
                keywords.add(category.lower().replace('_', ' '))
                for word in category.lower().split('_'):
                    if len(word) > 2:
                        keywords.add(word)

            # Add each keyword to the index
            for keyword in keywords:
                if product_id not in [p.get('id') for p in self.keyword_index[keyword]]:
                    self.keyword_index[keyword].append(product)

                # Also add singular/plural variant
                if keyword in self.plural_map:
                    variant = self.plural_map[keyword]
                    if product_id not in [p.get('id') for p in self.keyword_index[variant]]:
                        self.keyword_index[variant].append(product)

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text (product names, descriptions)"""
        # Normalize text
        text = text.lower()
        # Remove special characters but keep hyphens for compound words
        text = re.sub(r'[^\w\s\-]', ' ', text)

        keywords = set()
        words = text.split()

        for word in words:
            # Skip stop words and very short words
            if word in self.stop_words or len(word) < 3:
                continue

            # Skip pure numbers
            if word.isdigit():
                continue

            keywords.add(word)

            # Handle hyphenated words (e.g., "t-shirt" -> "tshirt", "t", "shirt")
            if '-' in word:
                parts = word.split('-')
                for part in parts:
                    if len(part) >= 2 and part not in self.stop_words:
                        keywords.add(part)
                # Also add without hyphen
                keywords.add(word.replace('-', ''))

        return keywords
    
    def _build_canonical_map(self):
        """Build canonical product name mappings for main kits"""
        
        self.canonical_map = {
            # V5 XL mappings (prioritize XL over regular)
            'v5 xl': 'v5_xl',
            'v5xl': 'v5_xl',
            'xl v5': 'v5_xl',
            'v 5 xl': 'v5_xl',
            'v5 extra large': 'v5_xl',
            
            # V5 mappings (default to XL when just saying "v5")
            'v5': 'v5_xl',
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
        Main retrieval method - IMPROVED with aggressive keyword matching.
        Now matches ANY noun from user queries to product names.
        """
        query_lower = query.lower().strip()

        # STAGE 0: Direct keyword index lookup (NEW - most reliable for specific nouns)
        direct_matches = self._direct_keyword_lookup(query_lower)
        if direct_matches:
            print(f"🎯 DIRECT KEYWORD MATCH: Found {len(direct_matches)} products")
            # Still apply reranking and filtering
            reranked = self._rerank_with_priority(
                [(p, 1000) for p in direct_matches], query_lower, context
            )
            filtered = self._filter_accessories(reranked, query_lower)
            if filtered:
                return filtered[:top_k]

        # STAGE 1: Check for main kit queries (vaporizers)
        main_kit_results = self._check_main_kits(query_lower)
        if main_kit_results:
            print(f"🎯 MAIN KIT MATCH: Found {len(main_kit_results)} main products")
            return main_kit_results[:top_k]

        # STAGE 2: Semantic + Keyword hybrid search
        all_results = []

        # Get semantic results if available
        if self.vector_store and self.vector_store.embeddings:
            semantic_results = self.vector_store.semantic_search(query_lower, top_k=20)
            for product_id, score in semantic_results:
                product = self.vector_store.get_product(product_id)
                if product:
                    all_results.append((product, score * 100, 'semantic'))

        # Get keyword results (improved version)
        keyword_results = self._keyword_search(query_lower)
        for product, score in keyword_results:
            all_results.append((product, score, 'keyword'))

        if not all_results:
            return []

        # STAGE 3: Merge and deduplicate
        seen = set()
        merged = []
        for product, score, source in all_results:
            prod_id = product.get('id', product.get('name'))
            if prod_id not in seen:
                seen.add(prod_id)
                merged.append((product, score))

        # STAGE 4: Rerank with priority boost
        reranked = self._rerank_with_priority(merged, query_lower, context)

        # STAGE 5: Filter out replacement parts
        filtered = self._filter_accessories(reranked, query_lower)

        return filtered[:top_k]

    def _direct_keyword_lookup(self, query: str) -> List[Dict]:
        """
        NEW: Direct lookup in keyword index for specific product nouns.
        Returns products that match ANY keyword in the query.
        This is the most reliable method for queries like "jars", "hoodies", "shirts".
        Now also checks synonyms (bubbler = hydratube = water attachment).
        """
        query_words = set(query.lower().split())
        matched_products = []
        matched_ids = set()

        # Also check for multi-word phrases
        query_phrases = [query.lower()]
        words = query.lower().split()
        for i in range(len(words)):
            for j in range(i + 1, min(i + 4, len(words) + 1)):
                query_phrases.append(' '.join(words[i:j]))

        # Expand query words with synonyms
        expanded_words = set(query_words)
        for word in list(query_words):
            if word in self.synonym_map:
                expanded_words.update(self.synonym_map[word])
        # Also check phrases for synonyms
        for phrase in query_phrases:
            if phrase in self.synonym_map:
                expanded_words.update(self.synonym_map[phrase])

        # Check each query word/phrase against the keyword index
        for word in expanded_words:
            # Skip stop words
            if word in self.stop_words or len(word) < 3:
                continue

            # Direct match in keyword index
            if word in self.keyword_index:
                for product in self.keyword_index[word]:
                    prod_id = product.get('id', product.get('name'))
                    if prod_id not in matched_ids:
                        matched_ids.add(prod_id)
                        matched_products.append(product)

            # Check singular/plural variant
            if word in self.plural_map:
                variant = self.plural_map[word]
                if variant in self.keyword_index:
                    for product in self.keyword_index[variant]:
                        prod_id = product.get('id', product.get('name'))
                        if prod_id not in matched_ids:
                            matched_ids.add(prod_id)
                            matched_products.append(product)

        # Check category keywords for broader matching
        for category, keywords in self.category_keywords.items():
            if any(kw in query.lower() for kw in keywords):
                # Find all products in this category
                for product in self.products:
                    prod_category = product.get('category', '').lower()
                    prod_id = product.get('id', product.get('name'))

                    # Match by category field
                    if category.replace('_', '') in prod_category.replace('_', ''):
                        if prod_id not in matched_ids:
                            matched_ids.add(prod_id)
                            matched_products.append(product)

                    # Also match by category keyword in product name
                    prod_name = product.get('name', '').lower()
                    if any(kw in prod_name for kw in keywords if len(kw) > 3):
                        if prod_id not in matched_ids:
                            matched_ids.add(prod_id)
                            matched_products.append(product)

        return matched_products
    
    def _check_main_kits(self, query: str) -> List[Dict]:
        """
        Check if query is asking about main product categories.
        Now handles hemp clothing, jars, AND vaporizers.
        """
        results = []
        query_lower = query.lower()

        # CHECK 1: Hemp Clothing queries (NEW)
        is_clothing = any(kw in query_lower for kw in self.category_keywords['hemp_clothing'])
        if is_clothing:
            for product in self.products:
                category = product.get('category', '').lower()
                name = product.get('name', '').lower()

                # Match hemp_clothing category OR clothing keywords in name
                if 'hemp_clothing' in category or 'clothing' in category:
                    results.append(product)
                elif any(kw in name for kw in ['hemp', 'shirt', 'hoodie', 'pants', 'boxer', 'fleece', 'cargo', 'washcloth']):
                    # Only if not a vaporizer
                    if 'heater' not in name and 'vaporizer' not in name:
                        results.append(product)

            if results:
                print(f"🎯 HEMP CLOTHING MATCH: Found {len(results)} products")
                return results

        # CHECK 2: Jar queries (NEW)
        is_jar = any(kw in query_lower for kw in ['jar', 'jars', 'glass jar', 'uv jar', 'storage'])
        if is_jar:
            for product in self.products:
                name = product.get('name', '').lower()
                if 'jar' in name or ('glass' in name and 'jar' in query_lower):
                    results.append(product)

            if results:
                print(f"🎯 JAR MATCH: Found {len(results)} products")
                # Sort: UV jars first, then clear, then others
                def jar_priority(p):
                    name = p.get('name', '').lower()
                    if 'clear' in query_lower and 'clear' in name:
                        return 0
                    if 'uv' in query_lower and 'uv' in name:
                        return 0
                    if 'uv' in name:
                        return 1
                    return 2
                results.sort(key=jar_priority)
                return results

        # CHECK 3: Flower/dry herb queries
        is_flower = any(w in query_lower for w in ['flower', 'dry herb', 'herb', 'bud'])
        is_concentrate = any(w in query_lower for w in ['concentrate', 'wax', 'dab', 'rosin', 'shatter', 'oil', 'hash', 'resin'])

        if is_flower and not is_concentrate:
            for product in self.products:
                name = product.get('name', '')
                if 'Ruby Twist Injector - Dry Herb Desktop Kit' in name:
                    results.append(product)
                elif 'Gen 2 DC Ceramic Rebuildable Dry Herb Heater' in name and 'Wholesale' not in name:
                    results.append(product)
            if results:
                return results

        # CHECK 4: V5 queries (prioritize XL)
        if 'v5' in query_lower or 'v 5' in query_lower:
            priority_names = [
                'Divine Crossing XL v5 Rebuildable Concentrate Heater',  # XL FIRST
                'XL v5 Rebuildable Heater, Pico Plus & Hubble Bubble',
                'Divine Crossing v5 Rebuildable Heater & Pico Plus',
                'Divine Crossing v5 Rebuildable Concentrate Heater',  # Regular V5 last
            ]

            for priority_name in priority_names:
                for product in self.products:
                    if priority_name in product.get('name', ''):
                        results.append(product)
                        if len(results) >= 4:
                            return results

            if results:
                return results

        # CHECK 5: Concentrate or general vape queries
        is_beginner = any(w in query_lower for w in ['beginner', 'new', 'first time', 'starter', 'easy'])
        if is_concentrate or 'vaporizer' in query_lower or 'vape' in query_lower or is_beginner:
            priority_names = [
                'XL Deluxe Core eRig Kit- Now with 6 Heat Settings',  # Core first for beginners
                'XL Recycler Top Core Deluxe eRig',
                'Divine Crossing XL v5 Rebuildable Concentrate Heater',  # XL before regular
                'Divine Crossing v5 Rebuildable Heater & Pico Plus',
            ]

            for priority_name in priority_names:
                for product in self.products:
                    if priority_name in product.get('name', ''):
                        results.append(product)
                        if len(results) >= 4:
                            return results

            if results:
                return results

        return results
    
    def _keyword_search(self, query: str) -> List[Tuple[Dict, float]]:
        """
        IMPROVED keyword search - more aggressive matching.
        Handles partial matches, singular/plural, and category terms.
        """
        results = []
        query_words = query.lower().split()
        query_lower = query.lower()

        # Expand query words with singular/plural variants
        expanded_words = set()
        for word in query_words:
            if len(word) > 2:
                expanded_words.add(word)
                if word in self.plural_map:
                    expanded_words.add(self.plural_map[word])

        for product in self.products:
            score = 0
            name = product.get('name', '').lower()
            desc = product.get('description', '').lower()
            category = product.get('category', '').lower()

            # Check expanded query words
            for word in expanded_words:
                # Exact word match in name (highest score)
                if re.search(rf'\b{re.escape(word)}\b', name):
                    score += 200
                # Partial match in name (still good)
                elif word in name:
                    score += 150
                # Match in category
                elif word in category:
                    score += 120
                # Match in description
                elif word in desc:
                    score += 50

            # Boost for category matches
            for cat_name, cat_keywords in self.category_keywords.items():
                if any(kw in query_lower for kw in cat_keywords):
                    if cat_name.replace('_', '') in category.replace('_', ''):
                        score += 300  # Big boost for category match

            # Boost for exact phrase match in name
            if len(query_lower) > 3 and query_lower in name:
                score += 500

            if score > 0:
                results.append((product, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:30]  # Return more results for better coverage
    
    def _rerank_with_priority(self, candidates: List[Tuple[Dict, float]], query: str, context: Optional[Dict]) -> List[Dict]:
        """
        Rerank with priority boost for ALL product categories.
        Boosts main vape kits, hemp clothing, jars, etc. based on query context.
        """
        scored = []
        query_lower = query.lower()

        # Detect query category intent
        is_clothing_query = any(kw in query_lower for kw in self.category_keywords['hemp_clothing'])
        is_jar_query = any(kw in query_lower for kw in self.category_keywords['jars'])
        is_flower_query = any(w in query_lower for w in ['flower', 'dry herb', 'herb', 'bud'])
        is_concentrate_query = any(w in query_lower for w in ['concentrate', 'wax', 'dab', 'rosin', 'hash', 'resin', 'shatter'])
        is_vape_query = any(w in query_lower for w in ['vape', 'vaporizer', 'atomizer', 'erig'])

        for product, base_score in candidates:
            score = base_score
            name = product.get('name', '')
            name_lower = name.lower()
            category = product.get('category', '').lower()

            # HEMP CLOTHING BOOST (when query is about clothing)
            if is_clothing_query:
                if 'hemp_clothing' in category or 'clothing' in category:
                    score += 20000  # Highest priority for clothing queries
                elif any(kw in name_lower for kw in ['hemp', 'shirt', 'hoodie', 'pants', 'boxer', 'fleece', 'cargo']):
                    score += 18000
                # Penalize vaporizers when asking about clothing
                if 'vaporizer' in name_lower or 'heater' in name_lower or 'erig' in name_lower:
                    score -= 10000

            # JAR BOOST (when query is about jars/storage)
            if is_jar_query:
                if 'jar' in name_lower or 'glass' in name_lower:
                    score += 20000
                if 'uv' in name_lower and ('jar' in name_lower or 'glass' in name_lower):
                    score += 5000  # Extra boost for UV jars
                if 'clear' in query_lower and 'clear' in name_lower:
                    score += 5000  # Boost if asking for clear jars specifically

            # MAIN VAPE KIT BOOST (when query is about vapes)
            if is_vape_query or is_concentrate_query or is_flower_query:
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

            # PENALIZE replacement parts (unless specifically asking for them)
            if 'replacement' not in query_lower and 'spare' not in query_lower:
                if 'replacement' in name_lower or 'spare' in name_lower:
                    score -= 5000
                if category == 'replacement_parts':
                    score -= 5000

            # Material-specific boosts for vaporizers
            if is_flower_query and ('Ruby Twist' in name or 'Gen 2 DC' in name):
                score += 8000
            elif is_flower_query and 'v5' in name_lower and not is_clothing_query:
                score -= 3000  # Don't show V5 for flower

            if is_concentrate_query and ('Core' in name or 'v5' in name_lower):
                score += 8000
            elif is_concentrate_query and ('Ruby' in name or 'Gen 2' in name):
                score -= 3000  # Don't show dry herb for concentrates

            scored.append((product, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored]
    
    def _filter_accessories(self, products: List[Dict], query: str) -> List[Dict]:
        """
        Filter out replacement parts unless specifically asked.
        Never filters out hemp clothing, jars, or other main product categories.
        """
        query_lower = query.lower()

        # If asking for accessories/replacement parts, don't filter
        accessory_words = ['replacement', 'spare', 'part', 'accessory', 'tip', 'cap', 'bowl']
        if any(word in query_lower for word in accessory_words):
            return products

        # Check if query is about non-vaporizer categories (never filter these)
        is_clothing_query = any(kw in query_lower for kw in self.category_keywords['hemp_clothing'])
        is_jar_query = any(kw in query_lower for kw in self.category_keywords['jars'])

        filtered = []
        for product in products:
            name = product.get('name', '').lower()
            category = product.get('category', '').lower()

            # NEVER filter out hemp clothing when asking about clothing
            if is_clothing_query:
                if 'hemp_clothing' in category or 'clothing' in category:
                    filtered.append(product)
                    continue
                if any(kw in name for kw in ['shirt', 'hoodie', 'pants', 'boxer', 'fleece']):
                    filtered.append(product)
                    continue

            # NEVER filter out jars when asking about jars
            if is_jar_query:
                if 'jar' in name or 'glass' in name:
                    filtered.append(product)
                    continue

            # Skip replacement parts for other queries
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
    """Test the RAG retriever with various query types"""
    import json

    print("\n" + "="*70)
    print("RAG RETRIEVER TEST - Aggressive Keyword Matching")
    print("="*70 + "\n")

    # Load products
    try:
        with open('products_clean.json', 'r') as f:
            data = json.load(f)
            # Handle both formats: direct list or dict with 'products' key
            if isinstance(data, dict) and 'products' in data:
                products = data['products']
            elif isinstance(data, list):
                products = data
            else:
                print("❌ Unexpected products_clean.json format")
                return
    except FileNotFoundError:
        print("❌ products_clean.json not found. Run from project root.")
        return

    # Initialize retriever
    retriever = RAGRetriever()
    retriever.load_products(products)

    # Test queries that previously failed
    test_queries = [
        # Hemp clothing queries (these were failing)
        "hemp clothing",
        "do you sell hoodies",
        "what kinds of hemp clothes do you sell",
        "shirts",
        "hemp hoodies",

        # Jar queries (these were failing)
        "jars",
        "clear jars",
        "uv jars",
        "glass jars",

        # Vaporizer queries (should still work)
        "v5",
        "beginner vaporizer",
        "flower vape",
        "concentrate vape",
    ]

    print("Testing queries:\n")
    for query in test_queries:
        results = retriever.retrieve(query, top_k=3)
        print(f"Query: '{query}'")
        if results:
            for i, p in enumerate(results, 1):
                name = p.get('name', 'Unknown')[:50]
                category = p.get('category', 'N/A')
                print(f"  {i}. {name}... [{category}]")
        else:
            print("  ❌ No results found!")
        print()

    print("="*70)
    print("Test complete!")
    print("="*70)


if __name__ == "__main__":
    test_rag_retriever()
