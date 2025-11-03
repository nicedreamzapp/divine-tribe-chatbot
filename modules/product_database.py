#!/usr/bin/env python3
"""Product Database Module for Tribe Chatbot"""

import json
import logging
from typing import List, Dict, Optional

class ProductDatabase:
    def __init__(self, products_file: str = "products_organized.json"):
        self.logger = logging.getLogger(__name__)
        self.products_file = products_file
        self.organized_data = {}
        self.load_products()
        
    def load_products(self):
        try:
            with open(self.products_file, 'r', encoding='utf-8') as f:
                self.organized_data = json.load(f)
            total = self.organized_data["metadata"]["total_products"]
            self.logger.info(f"Loaded {total} products")
        except FileNotFoundError:
            # Fall back to old format
            try:
                with open('complete_products_full.json', 'r') as f:
                    products = json.load(f)
                    self.organized_data = {
                        "metadata": {"total_products": len(products)},
                        "categories": {"main_products": {"products": products}},
                        "product_index": {},
                        "search_index": {}
                    }
            except:
                self.organized_data = {
                    "metadata": {"total_products": 0},
                    "categories": {},
                    "product_index": {},
                    "search_index": {}
                }
    
    def search_products(self, query: str, max_results: int = 5) -> List[Dict]:
        if not query:
            return self.get_featured_products(max_results)
        
        query_lower = query.lower()
        found_products = []
        
        # Search in categories
        for category in self.organized_data.get("categories", {}).values():
            for product in category.get("products", []):
                if query_lower in product.get("name", "").lower():
                    found_products.append(product)
                    if len(found_products) >= max_results:
                        return found_products
        
        return found_products
    
    def get_featured_products(self, max_results: int = 5) -> List[Dict]:
        main_products = self.organized_data.get("categories", {}).get("main_products", {}).get("products", [])
        return main_products[:max_results]
