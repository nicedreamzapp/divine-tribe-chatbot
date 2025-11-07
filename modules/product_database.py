#!/usr/bin/env python3
"""
product_database.py - Modern RAG orchestrator
Integrates vector search + hybrid retrieval + context management
"""

import json
from typing import List, Dict, Optional

# Import our RAG components
try:
    from modules.vector_store import VectorStore
    from modules.rag_retriever import RAGRetriever
    MODERN_RAG_AVAILABLE = True
except ImportError:
    print("⚠️  Modern RAG components not found. Using fallback mode.")
    MODERN_RAG_AVAILABLE = False


class ProductDatabase:
    """
    Modern RAG-powered product database.
    
    Architecture:
    1. Vector Store - Semantic embeddings
    2. RAG Retriever - Hybrid search + reranking
    3. Business Rules - From your metadata
    4. Context Awareness - From conversation history
    """
    
    def __init__(self, json_file: str = "products_organized.json"):
        self.json_file = json_file
        self.products = []
        self.business_rules = {}
        
        # Initialize RAG components
        self.vector_store = None
        self.rag_retriever = None
        
        # Load products
        self.load_products()
        
        # Build modern RAG system
        if MODERN_RAG_AVAILABLE:
            self._initialize_modern_rag()
        else:
            print("⚠️  Running in fallback mode (keyword search only)")
    
    def load_products(self):
        """Load products from JSON"""
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            
            # Extract business rules
            metadata = data.get('metadata', {})
            self.business_rules = metadata.get('business_rules', {})
            
            # Extract all products
            categories = data.get('categories', {})
            
            for category_name, category_data in categories.items():
                if isinstance(category_data, dict) and 'products' in category_data:
                    for product in category_data['products']:
                        # Enrich product with metadata
                        product['category'] = category_name
                        product['category_display'] = category_data.get('display_name', category_name)
                        product['priority'] = category_data.get('priority', 2)
                        
                        self.products.append(product)
            
            print(f"✅ Loaded {len(self.products)} products")
            print(f"✅ Business rules: {len(self.business_rules)}")
            
        except Exception as e:
            print(f"❌ Error loading products: {e}")
            self.products = []
    
    def _initialize_modern_rag(self):
        """Initialize modern RAG components"""
        print("🚀 Initializing Modern RAG System...")
        
        # Initialize vector store
        self.vector_store = VectorStore(cache_file="product_embeddings.pkl")
        
        # Build embeddings (or load from cache)
        self.vector_store.build_embeddings(self.products, force_rebuild=False)
        
        # Initialize RAG retriever
        self.rag_retriever = RAGRetriever(vector_store=self.vector_store)
        self.rag_retriever.load_products(self.products, self.business_rules)
        
        print("✅ Modern RAG System ready!")
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Main search interface - uses modern RAG if available.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            context: Conversation context (from ContextManager)
            
        Returns:
            List of product dictionaries, ranked by relevance
        """
        if not query or not self.products:
            return []
        
        # Use modern RAG if available
        if MODERN_RAG_AVAILABLE and self.rag_retriever:
            return self.rag_retriever.retrieve(query, max_results, context)
        
        # Fallback to simple keyword search
        return self._fallback_search(query, max_results)
    
    def _fallback_search(self, query: str, max_results: int) -> List[Dict]:
        """
        Fallback keyword search when modern RAG not available.
        Simple but functional.
        """
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            score = 0
            name = product['name'].lower()
            desc = product.get('description', '').lower()
            
            # Simple scoring
            if query_lower in name:
                score += 100
            elif query_lower in desc:
                score += 50
            
            # Priority boost
            priority = product.get('priority', 999)
            if priority == 1:
                score += 50
            
            if score > 0:
                results.append((score, product))
        
        # Sort and return top results
        results.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in results[:max_results]]
    
    def get_by_name(self, name: str) -> Optional[Dict]:
        """Get product by exact name"""
        name_lower = name.lower()
        for product in self.products:
            if product.get('name', '').lower() == name_lower:
                return product
        return None
    
    def get_by_id(self, product_id: str) -> Optional[Dict]:
        """Get product by ID"""
        for product in self.products:
            if product.get('id') == product_id:
                return product
        return None
    
    def get_main_products(self) -> List[Dict]:
        """Get all main products (priority 1)"""
        return [p for p in self.products if p.get('priority') == 1]
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get all products in a category"""
        return [p for p in self.products if p.get('category') == category]
    
    def rebuild_embeddings(self):
        """Force rebuild of vector embeddings"""
        if MODERN_RAG_AVAILABLE and self.vector_store:
            print("🔄 Rebuilding embeddings...")
            self.vector_store.build_embeddings(self.products, force_rebuild=True)
            print("✅ Embeddings rebuilt!")
        else:
            print("⚠️  Modern RAG not available - cannot rebuild embeddings")
    
    def get_search_stats(self) -> Dict:
        """Get statistics about the search system"""
        stats = {
            'total_products': len(self.products),
            'main_products': len([p for p in self.products if p.get('priority') == 1]),
            'accessories': len([p for p in self.products if p.get('priority') == 2]),
            'replacement_parts': len([p for p in self.products if p.get('priority') == 3]),
            'modern_rag_enabled': MODERN_RAG_AVAILABLE,
            'embeddings_built': False
        }
        
        if self.vector_store and self.vector_store.embeddings:
            stats['embeddings_built'] = True
            stats['embeddings_count'] = len(self.vector_store.embeddings)
        
        if self.rag_retriever:
            stats['canonical_mappings'] = len(self.rag_retriever.canonical_map)
        
        return stats


# Convenience function
def search_products(query: str, max_results: int = 5) -> List[Dict]:
    """Quick search function"""
    db = ProductDatabase()
    return db.search(query, max_results)


# Testing
def test_product_database():
    """Test the product database with modern RAG"""
    print("\n" + "="*70)
    print("PRODUCT DATABASE TEST (Modern RAG)")
    print("="*70 + "\n")
    
    db = ProductDatabase('products_organized.json')
    
    # Print stats
    print("\nSearch System Stats:")
    stats = db.get_search_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test queries
    test_queries = [
        "v5",
        "v5 xl",
        "core",
        "jars",
        "best for flavor",
        "beginner",
        "ruby twist"
    ]
    
    print("\n" + "="*70)
    print("SEARCH TESTS")
    print("="*70)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        results = db.search(query, max_results=3)
        
        if results:
            for i, product in enumerate(results, 1):
                print(f"  {i}. {product['name'][:60]}...")
                print(f"     Priority: {product['priority']}, Category: {product['category']}")
        else:
            print("  No results found")


if __name__ == "__main__":
    test_product_database()
