#!/usr/bin/env python3
"""
IMPROVED product_database.py - Better product search and matching
Fixes V5 XL search issues and improves accuracy
"""

import json
import re
from typing import List, Dict, Optional
from difflib import SequenceMatcher

class ProductDatabase:
    """Enhanced product database with better search"""
    
    def __init__(self, json_file="products_organized.json"):
        self.json_file = json_file
        self.products = []
        self.load_products()
        
        # Product aliases for better matching
        self.aliases = {
            "v5": ["v5 xl", "v5xl", "v 5"],
            "core": ["core deluxe", "core 2.0"],
            "nice dreamz": ["nice dreams", "dreamz", "dreams"],
            "ruby twist": ["ruby", "ball vape"],
            "cub": ["the cub"],
            "pico": ["pico mod", "pico plus"],
        }
        
        # Priority products (should appear first)
        self.priority_products = [
            "v5 xl",
            "core deluxe",
            "ruby twist",
            "nice dreamz",
            "cub"
        ]
    
    def load_products(self):
        """Load products from JSON"""
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
                
                # Get the categories section
                categories = data.get('categories', {})
                
                # Flatten all products from categories
                for category_name, category_data in categories.items():
                    if isinstance(category_data, dict) and 'products' in category_data:
                        products_in_category = category_data['products']
                        
                        for product in products_in_category:
                            product['category'] = category_name
                            product['priority'] = category_data.get('priority', 2)
                            self.products.append(product)
                
                print(f"✅ Loaded {len(self.products)} products from {len(categories)} categories")
                
        except FileNotFoundError:
            print(f"⚠️  Product file not found: {self.json_file}")
            self.products = []
        except Exception as e:
            print(f"❌ Error loading products: {e}")
            import traceback
            traceback.print_exc()
            self.products = []
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Enhanced search with better matching
        """
        if not query or not self.products:
            return []
        
        query_lower = query.lower().strip()
        
        # Expand query with aliases
        expanded_terms = self._expand_query(query_lower)
        
        # Score all products
        scored_products = []
        for product in self.products:
            score = self._calculate_match_score(product, query_lower, expanded_terms)
            if score > 0:
                scored_products.append((score, product))
        
        # Sort by score (highest first)
        scored_products.sort(key=lambda x: x[0], reverse=True)
        
        # Return top matches
        results = [p for _, p in scored_products[:max_results]]
        
        return results
    
    def _expand_query(self, query: str) -> List[str]:
        """Expand query with known aliases"""
        terms = [query]
        
        for key, aliases in self.aliases.items():
            if key in query:
                terms.extend(aliases)
        
        return list(set(terms))
    
    def _calculate_match_score(self, product: Dict, query: str, expanded_terms: List[str]) -> float:
        """
        Calculate how well a product matches the query
        Higher score = better match
        """
        score = 0.0
        product_name = product.get('name', '').lower()
        product_desc = product.get('description', '').lower()
        product_full = f"{product_name} {product_desc}"
        
        # 1. EXACT NAME MATCH (highest priority)
        if query == product_name:
            score += 1000
        
        # 2. EXACT TERM IN NAME
        query_words = query.split()
        name_words = product_name.split()
        
        # Check for V5 XL specifically
        if "v5" in query and "xl" in query:
            if "v5" in product_name and "xl" in product_name:
                score += 500  # High priority for V5 XL matches
        
        if "v5" in query:
            if "v5" in product_name:
                score += 300
                if "xl" in product_name:
                    score += 200  # Boost for V5 XL
        
        # Core matching
        if "core" in query:
            if "core" in product_name:
                score += 300
                if "deluxe" in product_name:
                    score += 200  # Prioritize Core Deluxe over 2.0
                elif "2.0" in product_name:
                    score += 50  # Lower score for old Core 2.0
        
        # 3. WORD MATCHING
        for query_word in query_words:
            if len(query_word) > 2:  # Skip very short words
                for name_word in name_words:
                    # Exact word match in name
                    if query_word == name_word:
                        score += 100
                    # Partial word match
                    elif query_word in name_word or name_word in query_word:
                        score += 50
                    # Similar words (fuzzy)
                    elif self._similarity(query_word, name_word) > 0.8:
                        score += 30
        
        # 4. EXPANDED TERMS MATCHING
        for term in expanded_terms:
            if term in product_full:
                score += 80
        
        # 5. SUBSTRING MATCHING
        if query in product_name:
            score += 150
        elif query in product_full:
            score += 50
        
        # 6. PRIORITY BOOST
        # Boost priority products
        product_priority = product.get('priority', 2)
        if product_priority == 1:
            score += 100
        elif product_priority == 1.5:
            score += 50
        
        # Extra boost for flagship products
        for priority_name in self.priority_products:
            if priority_name in product_name:
                score += 75
        
        # 7. CATEGORY RELEVANCE
        category = product.get('category', '')
        
        # Penalize replacement parts unless specifically asked
        if category == "replacement_parts":
            if not any(word in query for word in ["replacement", "part", "repair", "broken"]):
                score -= 200  # Heavy penalty for parts
        
        # 8. ATTRIBUTE MATCHING
        if "flavor" in query:
            if "v5" in product_name and "xl" in product_name:
                score += 150  # V5 XL is best for flavor
        
        if "beginner" in query or "easy" in query:
            if "core" in product_name and "deluxe" in product_name:
                score += 150  # Core Deluxe best for beginners
        
        if "portable" in query:
            if "v5" in product_name or "core" in product_name:
                score += 100
        
        if "desktop" in query or "ball vape" in query:
            if "ruby" in product_name or "twist" in product_name:
                score += 150
        
        return score
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, a, b).ratio()
    
    def get_by_name(self, name: str) -> Optional[Dict]:
        """Get specific product by exact name"""
        name_lower = name.lower()
        for product in self.products:
            if product.get('name', '').lower() == name_lower:
                return product
        return None
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get all products in a category"""
        return [p for p in self.products if p.get('category') == category]
    
    def get_main_products(self) -> List[Dict]:
        """Get main/priority products only"""
        return [p for p in self.products if p.get('priority', 2) <= 1.5]
    
    def search_accessories(self, query: str) -> List[Dict]:
        """Search specifically for accessories"""
        accessories = [p for p in self.products if p.get('category') in ['accessories', 'replacement_parts']]
        
        query_lower = query.lower()
        results = []
        
        for acc in accessories:
            name = acc.get('name', '').lower()
            if query_lower in name or any(word in name for word in query_lower.split()):
                results.append(acc)
        
        return results[:5]


# Convenience function
def search_products(query: str, max_results: int = 5) -> List[Dict]:
    """Quick product search"""
    db = ProductDatabase()
    return db.search(query, max_results)


def get_product_by_name(name: str) -> Optional[Dict]:
    """Get specific product"""
    db = ProductDatabase()
    return db.get_by_name(name)
