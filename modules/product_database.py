#!/usr/bin/env python3
"""
product_database.py - Product database with modern RAG retrieval
CLEANED: Optimized search, better error handling
"""

import json
from typing import List, Dict, Optional
from modules.vector_store import VectorStore
from modules.rag_retriever import RAGRetriever


class ProductDatabase:
    """
    Product database with hybrid RAG search
    Combines semantic search + keyword matching + priority boosting
    """
    
    def __init__(self, json_file: str = 'products_clean.json'):
        self.json_file = json_file
        self.products = []
        self.format_type = None
        
        # Initialize RAG components
        self.vector_store = None
        self.rag_retriever = None
        
        # Load products
        self._load_products()
        
        # Initialize modern RAG system
        self._initialize_rag_system()
    
    def _load_products(self):
        """Load products from JSON file"""
        print(f"📦 Loading products from {self.json_file}")
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Detect format
            if isinstance(data, list):
                self.products = data
                self.format_type = 'clean'
                print(f"✅ Loaded {len(self.products)} products")
                print(f"   Format: Clean (no variations, no HTML)")
            
            elif isinstance(data, dict) and 'products' in data:
                self.products = data['products']
                self.format_type = 'legacy'
                print(f"✅ Loaded {len(self.products)} products")
                print(f"   Format: Legacy (with variations)")
            
            else:
                raise ValueError("Unknown JSON format")
        
        except FileNotFoundError:
            print(f"❌ Error: {self.json_file} not found!")
            self.products = []
        
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            self.products = []
        
        except Exception as e:
            print(f"❌ Unexpected error loading products: {e}")
            self.products = []
    
    def _initialize_rag_system(self):
        """Initialize modern RAG retrieval system"""
        if not self.products:
            print("⚠️  No products loaded, skipping RAG initialization")
            return
        
        print("🚀 Initializing Modern RAG System...")
        
        try:
            # Initialize vector store
            self.vector_store = VectorStore()
            self.vector_store.build_index(self.products)
            
            # Initialize RAG retriever
            self.rag_retriever = RAGRetriever(vector_store=self.vector_store)
            self.rag_retriever.load_products(self.products)
            
            print("✅ Modern RAG System ready!")
        
        except Exception as e:
            print(f"⚠️  RAG initialization failed: {e}")
            print("   Falling back to keyword search only")
            self.rag_retriever = None
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search products using modern RAG retrieval
        
        Args:
            query: Search query
            max_results: Maximum number of results
            context: Optional conversation context
        
        Returns:
            List of product dictionaries
        """
        if not self.products:
            print("⚠️  No products available")
            return []
        
        if not query or not query.strip():
            print("⚠️  Empty query")
            return []
        
        # Use RAG retriever if available
        if self.rag_retriever:
            try:
                results = self.rag_retriever.retrieve(
                    query=query,
                    top_k=max_results,
                    context=context
                )
                
                print(f"🔍 Retrieved {len(results)} products for '{query}'")
                if results:
                    print(f"   Top: {results[0].get('name', 'Unknown')[:50]}...")
                
                return results
            
            except Exception as e:
                print(f"❌ RAG search error: {e}")
                return self._fallback_keyword_search(query, max_results)
        
        else:
            # Fallback to simple keyword search
            return self._fallback_keyword_search(query, max_results)
    
    def _fallback_keyword_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Simple keyword-based fallback search"""
        query_lower = query.lower()
        query_words = query_lower.split()
        
        scored_products = []
        
        for product in self.products:
            score = 0
            name = product.get('name', '').lower()
            desc = product.get('description', '').lower()
            
            # Score based on keyword matches
            for word in query_words:
                if len(word) > 2:  # Skip short words
                    if word in name:
                        score += 10
                    elif word in desc:
                        score += 3
            
            if score > 0:
                scored_products.append((product, score))
        
        # Sort by score
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        results = [p for p, _ in scored_products[:max_results]]
        
        print(f"🔍 Fallback search: {len(results)} products for '{query}'")
        return results
    
    def get_product_by_name(self, name: str) -> Optional[Dict]:
        """Get product by exact name match"""
        for product in self.products:
            if product.get('name', '').lower() == name.lower():
                return product
        return None
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get product by ID"""
        for product in self.products:
            if product.get('id') == product_id:
                return product
        return None
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get all products in a category"""
        return [
            p for p in self.products
            if p.get('category', '').lower() == category.lower()
        ]
    
    def get_all_categories(self) -> List[str]:
        """Get list of all unique categories"""
        categories = set()
        for product in self.products:
            cat = product.get('category')
            if cat:
                categories.add(cat)
        return sorted(list(categories))
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {
            'total_products': len(self.products),
            'format': self.format_type,
            'categories': len(self.get_all_categories()),
            'rag_enabled': self.rag_retriever is not None,
            'vector_store_size': len(self.vector_store.embeddings) if self.vector_store else 0
        }
        return stats
    
    def reload(self):
        """Reload products from JSON file"""
        print("🔄 Reloading products...")
        self._load_products()
        self._initialize_rag_system()
        print("✅ Reload complete")


def test_product_database():
    """Test the product database"""
    print("\n" + "="*70)
    print("PRODUCT DATABASE TEST")
    print("="*70 + "\n")
    
    # Initialize
    db = ProductDatabase('products_clean.json')
    
    # Stats
    print("\nDatabase Stats:")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test searches
    test_queries = [
        "v5",
        "core deluxe",
        "ruby twist",
        "concentrate vaporizer",
        "dry herb"
    ]
    
    print("\nTest Searches:")
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        results = db.search(query, max_results=3)
        for i, product in enumerate(results, 1):
            print(f"    {i}. {product.get('name', 'Unknown')[:50]}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    test_product_database()
