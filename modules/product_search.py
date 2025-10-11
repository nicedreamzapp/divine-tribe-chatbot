#!/usr/bin/env python3
"""
Smart Product Search - Retrieves only relevant products based on query
Searches BOTH product names AND descriptions for better matching
Prioritizes complete kits and glass accessories over replacement parts
"""

import json
from typing import List, Dict, Optional
from difflib import get_close_matches

class ProductSearch:
    def __init__(self, json_path: str):
        """Load products and build search indexes"""
        with open(json_path, 'r') as f:
            self.products = json.load(f)
        
        print(f"✓ Loaded {len(self.products)} products for search")
        
        # Build fast lookup indexes
        self.name_index = {p['name'].lower(): p for p in self.products}
        self.keyword_index = self._build_keyword_index()
        
        # Category mapping - searches both names and descriptions
        self.category_keywords = {
            'v5': ['v5', 'version 5', 'divine crossing v5', 'dc v5', 'v5 xl'],
            'v4': ['v4', 'v4.5', 'version 4', 'divine crossing v4', 'crucible'],
            'core': ['core', 'erig', 'e-rig', 'core 2.0', 'xl core', 'core deluxe', 'core 2.1', 'xl deluxe'],
            'lightning': ['lightning', 'lightning pen', 'quest lightning'],
            'nice_dreamz': ['nice dreamz', 'nice dreams', 'fogger', 'concentrate fogger'],
            'ruby_twist': ['ruby twist', 'ruby', 'ball vape', 'wireless ruby', 'dual controller'],
            'gen2_dry_herb': ['gen 2 dc', 'gen2', 'gen 2', 'dry herb heater'],
            'thermal_twist': ['thermal twist', 'ball-less'],
            'tug': ['tug', 'tug 2.0', 'crossing tug'],
            'cub': ['cub', 'cub base', 'cub adapter', 'xl cub'],
            'dry_herb': ['dry herb', 'flower', 'herb vape', 'desktop herb'],
            'glass': ['glass', 'rig', 'recycler', 'bubbler', 'sidecar', 'glass top', 'glass slide', 'vortex', 'hydratube', 'grenade'],
            'terp_slurper': ['terp slurper', 'slurper'],
            'coil': ['coil', 'heater', 'heating element', 'heater coil', 'rebuildable'],
            'cup': ['cup', 'sic', 'quartz', 'titanium', 'ti cup', 'aln', 'crucible', 'bucket', 'ceramic cup'],
            'spare_parts': ['spare', 'replacement', 'extra', 'tool', 'o-ring', 'oring'],
            'carb_cap': ['carb cap', 'cap', 'ez carb', 'bubble carb', 'vortex carb'],
            'banger': ['banger', 'bottomless'],
            'mod': ['pico', 'pico plus', 'istick', 'power supply', 'battery mod'],
            'enail': ['enail', 'e-nail', 'controller', 'flex coil', 'gooseneck'],
        }
        
        # Keywords that indicate user wants a COMPLETE product, not a replacement part
        self.complete_kit_indicators = ['kit', 'complete', 'bundle', 'package', 'set']
        self.glass_accessory_indicators = ['glass', 'top', 'recycler', 'sidecar', 'slide', 'bubbler']
        self.replacement_indicators = ['base', 'replacement', 'spare', 'extra', 'part']
        
        # Main product indicators (complete atomizers, not accessories)
        self.main_product_indicators = ['rebuildable heater', 'rebuildable concentrate', 'power supply',
                                        'kit', 'deluxe', 'bundle', 'erig', 'e-rig', 'fogger',
                                        'vaporizer', 'pen', 'twist', 'gen 2 dc']
        
        # Accessory indicators (should be lower priority unless specifically asked)
        self.accessory_indicators = ['upgrade', 'replacement', 'spare', 'cup', 'top', 'glass top',
                                     'heater cup', 'vortex top', 'o-ring', 'oring', 'carb cap',
                                     'slide', 'bubbler', 'banger', 'sleeve', 'spacer', 'tool']
    
    def _build_keyword_index(self) -> Dict[str, List[Dict]]:
        """Build keyword to product mapping - includes BOTH name and description"""
        index = {}
        
        for product in self.products:
            name = product['name'].lower()
            desc = product.get('full_description', '').lower()
            
            # Extract meaningful words (2+ chars for better matching)
            # IMPORTANT: Search BOTH name AND description
            text = name + ' ' + desc
            words = set([w.strip('.,!?()[]{}') for w in text.split() if len(w) >= 2])
            
            for word in words:
                if word not in index:
                    index[word] = []
                if product not in index[word]:  # Avoid duplicates
                    index[word].append(product)
        
        return index
    
    def _is_complete_kit(self, product: Dict) -> bool:
        """Check if product is a complete kit (not a replacement part)"""
        name_lower = product['name'].lower()
        desc_lower = product.get('full_description', '').lower()
        
        # Check if it's explicitly a kit/complete product
        has_kit_words = any(word in name_lower or word in desc_lower for word in self.complete_kit_indicators)
        
        # Check if it's a replacement part
        is_replacement = any(word in name_lower for word in ['base only', 'replacement base', 'spare base'])
        
        return has_kit_words and not is_replacement
    
    def _is_glass_accessory(self, product: Dict) -> bool:
        """Check if product is a glass top/slide/accessory (people love these!)"""
        name_lower = product['name'].lower()
        
        # Check for glass accessories
        glass_terms = ['glass top', 'glass slide', 'recycler top', 'sidecar', 'bubbler',
                       'glass pathway', 'vortex top', 'grenade glass', 'ez carb', 'hydratube']
        
        return any(term in name_lower for term in glass_terms)
    
    def _is_main_product(self, product: Dict) -> bool:
        """Check if product is a main product (complete atomizer/kit) vs accessory"""
        name_lower = product['name'].lower()
        desc_lower = product.get('full_description', '').lower()
        
        # Check if it's a main product
        is_main = any(indicator in name_lower or indicator in desc_lower
                     for indicator in self.main_product_indicators)
        
        # Check if it's just an accessory
        is_accessory = any(indicator in name_lower for indicator in self.accessory_indicators)
        
        # Main product must have main indicators AND not be purely an accessory
        # Exception: kits with accessories are still main products
        if 'kit' in name_lower or 'bundle' in name_lower:
            return True
        
        # "Rebuildable heater" = main product even if it has "cup" in name
        if 'rebuildable heater' in name_lower or 'rebuildable concentrate' in name_lower:
            return True
        
        # "Upgrade" or "replacement" = accessory
        if 'upgrade' in name_lower or 'replacement' in name_lower:
            return False
        
        return is_main and not is_accessory
    
    def _is_accessory_only(self, product: Dict) -> bool:
        """Check if product is accessory only (not a main atomizer)"""
        name_lower = product['name'].lower()
        
        # These are clearly accessories
        accessory_only_terms = ['upgrade', 'replacement heater cup', 'spare parts',
                               'o-ring', 'oring', 'replacement top', 'replacement glass',
                               'carb cap', 'sleeve', 'spacer', 'tool set']
        
        return any(term in name_lower for term in accessory_only_terms)
    
    def search(self, query: str, max_results: int = 8) -> List[Dict]:
        """
        Smart search with priority - searches BOTH names AND descriptions:
        1. Standard complete kits (XL Deluxe Core eRig Kit)
        2. Glass accessory kits (Recycler Top, Glass Slides)
        3. Other complete products
        4. Accessories
        5. Replacement bases (ONLY if specifically asked for)
        """
        query_lower = query.lower().strip()
        
        if not query_lower:
            return []
        
        # Special handling for very broad queries like "main products", "what do you sell", "list products"
        broad_queries = ['main product', 'all product', 'what do you sell', 'what do you have',
                        'list product', 'show me product', 'your product', 'product list',
                        'what you sell', 'what products']
        
        if any(broad in query_lower for broad in broad_queries):
            # Return top main products across all categories
            main_products = []
            
            # Priority order: complete kits first
            for product in self.products:
                name_lower = product['name'].lower()
                is_main = self._is_main_product(product)
                is_kit = 'kit' in name_lower or 'bundle' in name_lower
                
                if is_main or is_kit:
                    main_products.append(product)
                
                if len(main_products) >= max_results:
                    break
            
            return main_products[:max_results]
        
        # Detect if user is specifically asking for replacement parts
        asking_for_base = any(phrase in query_lower for phrase in [
            'just the base', 'only the base', 'replacement base', 'spare base',
            'base only', 'need a new base', 'base replacement'
        ])
        
        # Detect troubleshooting queries - should return Cub for Core issues
        is_core_troubleshooting = any(word in query_lower for word in ['core', 'xl deluxe', '2.0', '2.1']) and \
                                  any(word in query_lower for word in ['issue', 'problem', 'vapor', 'clean', 'resistance', 'ohm', 'broken', 'not working'])
        
        # Remove filler words
        filler_words = {'what', 'do', 'you', 'have', 'tell', 'me', 'about', 'the', 'a', 'an',
                        'is', 'are', 'should', 'i', 'buy', 'get', 'how', 'much', 'why',
                        'where', 'can', 'need', 'want', 'for', 'my', 'with', 'any', 'all'}
        
        query_words = [w for w in query_lower.split() if w not in filler_words]
        
        # Score products
        scores = {}
        
        # 1. Exact name match
        if query_lower in self.name_index:
            return [self.name_index[query_lower]]
        
        # 2. Score all products - CHECK BOTH NAME AND DESCRIPTION
        for product in self.products:
            name_lower = product['name'].lower()
            desc_lower = product.get('full_description', '').lower()
            score = 0
            
            # Full query in name = highest score
            if query_lower in name_lower:
                score += 100
            
            # Full query in description = good score
            if query_lower in desc_lower:
                score += 50
            
            # Check each query word in BOTH name and description
            for word in query_words:
                if word in name_lower:
                    score += 15  # Name matches are important
                
                if word in desc_lower:
                    score += 5  # Description matches are helpful
            
            # PRIORITY SYSTEM
            if score > 0:
                # Check product type
                is_kit = self._is_complete_kit(product)
                is_glass = self._is_glass_accessory(product)
                is_main_product = self._is_main_product(product)
                is_accessory_only = self._is_accessory_only(product)
                is_base_only = 'base' in name_lower and 'kit' not in name_lower and 'complete' not in name_lower and not is_glass
                is_standard_kit = 'kit' in name_lower and 'xl deluxe core' in name_lower and not any(word in name_lower for word in ['recycler', 'sidecar'])
                is_cub = 'cub' in name_lower and 'adapter' in name_lower
                
                # Special boost for Cub if Core troubleshooting
                if is_core_troubleshooting and is_cub:
                    score += 500  # HIGHEST priority for Core issues
                
                # Detect if query is asking for main product (not accessory)
                asking_for_main = not any(word in query_lower for word in ['cup', 'top', 'glass', 'replacement', 'spare', 'upgrade', 'accessory', 'o-ring', 'carb cap'])
                
                if asking_for_main:
                    # User asking generally about product - prioritize MAIN products!
                    if is_main_product and not is_accessory_only:
                        score += 300  # HIGHEST: Main atomizers and complete kits
                    elif is_accessory_only:
                        score -= 200  # PENALTY: Hide accessories unless specifically asked
                
                if not asking_for_base:
                    # General prioritization
                    if is_standard_kit:
                        score += 250  # HIGHEST: Standard XL Deluxe Core eRig Kit
                    elif is_glass and not asking_for_main:
                        score += 200  # HIGH: Glass tops/slides (only if asked for accessories)
                    elif is_kit:
                        score += 150  # Good: Other complete kits
                    elif is_base_only:
                        score -= 100  # PENALTY: Replacement base (hide unless asked)
                else:
                    # User specifically wants base
                    if is_base_only:
                        score += 200
            
            if score > 0:
                product_id = product['name']
                scores[product_id] = scores.get(product_id, 0) + score
        
        # 3. Category keyword matching - search descriptions too!
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    for product in self.products:
                        name_lower = product['name'].lower()
                        desc_lower = product.get('full_description', '').lower()
                        
                        if keyword in name_lower:
                            product_id = product['name']
                            base_score = 20
                            
                            # Extra boost for glass accessories
                            if self._is_glass_accessory(product):
                                base_score += 30
                            
                            scores[product_id] = scores.get(product_id, 0) + base_score
                        
                        # Also check description
                        elif keyword in desc_lower:
                            product_id = product['name']
                            scores[product_id] = scores.get(product_id, 0) + 10
        
        # 4. Keyword index search (already includes descriptions)
        for word in query_words:
            if word in self.keyword_index:
                for product in self.keyword_index[word]:
                    product_id = product['name']
                    scores[product_id] = scores.get(product_id, 0) + 3
        
        # Sort by score
        if scores:
            sorted_products = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            results = []
            for product_name, score in sorted_products[:max_results]:
                for p in self.products:
                    if p['name'] == product_name:
                        results.append(p)
                        break
            return results
        
        # 5. Fuzzy fallback
        all_names = list(self.name_index.keys())
        matches = get_close_matches(query_lower, all_names, n=max_results, cutoff=0.5)
        return [self.name_index[m] for m in matches]
    
    def get_by_keywords(self, keywords: List[str], max_results: int = 10) -> List[Dict]:
        """Get products matching any of the keywords - searches descriptions too"""
        scores = {}
        
        for keyword in keywords:
            for product in self.products:
                name_lower = product['name'].lower()
                desc_lower = product.get('full_description', '').lower()
                
                if keyword.lower() in name_lower:
                    product_id = product['name']
                    scores[product_id] = scores.get(product_id, 0) + 15
                elif keyword.lower() in desc_lower:
                    product_id = product['name']
                    scores[product_id] = scores.get(product_id, 0) + 5
        
        if not scores:
            return []
        
        sorted_products = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for product_name, score in sorted_products[:max_results]:
            for p in self.products:
                if p['name'] == product_name:
                    results.append(p)
                    break
        
        return results
    
    def get_all_products(self) -> List[Dict]:
        """Return all products"""
        return self.products
