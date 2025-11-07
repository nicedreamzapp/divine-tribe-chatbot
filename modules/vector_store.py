#!/usr/bin/env python3
"""
vector_store.py - Semantic search using sentence embeddings
This enables understanding "v5" means "V5 XL" even without exact keyword match
"""

import json
import pickle
import os
from typing import List, Dict, Tuple
import numpy as np

# Try to import sentence-transformers, fall back to simple mode if not available
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("⚠️  sentence-transformers not installed. Running in keyword-only mode.")
    print("   Install with: pip install sentence-transformers")
    EMBEDDINGS_AVAILABLE = False


class VectorStore:
    """
    Semantic vector store for products using sentence embeddings.
    
    This allows fuzzy matching like:
    - "v5" → finds "V5 XL Rebuildable Heater"
    - "jar" → finds all jar products
    - "best for flavor" → finds V5 XL
    """
    
    def __init__(self, cache_file: str = "product_embeddings.pkl"):
        self.cache_file = cache_file
        self.model = None
        self.embeddings = {}  # product_id -> embedding vector
        self.products = {}    # product_id -> product dict
        
        if EMBEDDINGS_AVAILABLE:
            # Load a lightweight, fast model (all-MiniLM-L6-v2 is only 80MB)
            print("🔄 Loading sentence embedding model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Embedding model ready")
        else:
            print("⚠️  Running without embeddings (keyword search only)")
    
    def build_embeddings(self, products: List[Dict], force_rebuild: bool = False):
        """
        Build or load embeddings for all products.
        
        Args:
            products: List of product dictionaries
            force_rebuild: If True, rebuild even if cache exists
        """
        # Try to load from cache first
        if not force_rebuild and os.path.exists(self.cache_file):
            print(f"📂 Loading embeddings from cache: {self.cache_file}")
            try:
                with open(self.cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    self.embeddings = cached_data['embeddings']
                    self.products = cached_data['products']
                print(f"✅ Loaded {len(self.embeddings)} cached embeddings")
                return
            except Exception as e:
                print(f"⚠️  Cache load failed: {e}. Rebuilding...")
        
        if not EMBEDDINGS_AVAILABLE:
            print("⚠️  Cannot build embeddings without sentence-transformers")
            return
        
        # Build embeddings from scratch
        print(f"🔨 Building embeddings for {len(products)} products...")
        
        product_texts = []
        product_ids = []
        
        for product in products:
            product_id = product['id']
            
            # Create rich text representation for embedding
            text = self._create_embedding_text(product)
            
            product_texts.append(text)
            product_ids.append(product_id)
            self.products[product_id] = product
        
        # Generate embeddings in batch (faster)
        print("🧠 Generating embeddings...")
        embeddings_array = self.model.encode(
            product_texts, 
            show_progress_bar=True,
            batch_size=32
        )
        
        # Store embeddings
        for product_id, embedding in zip(product_ids, embeddings_array):
            self.embeddings[product_id] = embedding
        
        # Cache for future use
        self._save_cache()
        
        print(f"✅ Built and cached {len(self.embeddings)} embeddings")
    
    def _create_embedding_text(self, product: Dict) -> str:
        """
        Create rich text representation of product for embedding.
        
        This combines multiple fields to create semantic meaning:
        - Product name (most important)
        - Category
        - Description
        - Key features
        """
        parts = []
        
        # Product name (repeat 3x for emphasis)
        name = product.get('name', '')
        parts.append(name)
        parts.append(name)
        parts.append(name)
        
        # Category
        category = product.get('category_display', product.get('category', ''))
        parts.append(category)
        
        # Description (truncated to avoid overwhelming)
        desc = product.get('description', '')
        if desc:
            # Take first 500 chars for embedding
            parts.append(desc[:500])
        
        # Short description
        short_desc = product.get('short_description', '')
        if short_desc:
            parts.append(short_desc[:200])
        
        return ' '.join(parts)
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Search products using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (product_id, similarity_score) tuples, sorted by relevance
        """
        if not EMBEDDINGS_AVAILABLE or not self.embeddings:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Calculate cosine similarity with all products
        similarities = []
        
        for product_id, product_embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, product_embedding)
            similarities.append((product_id, float(similarity)))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_product(self, product_id: str) -> Dict:
        """Get product by ID"""
        return self.products.get(product_id, {})
    
    def _save_cache(self):
        """Save embeddings to cache file"""
        try:
            cache_data = {
                'embeddings': self.embeddings,
                'products': self.products
            }
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            print(f"💾 Saved embeddings cache to {self.cache_file}")
        except Exception as e:
            print(f"⚠️  Failed to save cache: {e}")
    
    def clear_cache(self):
        """Clear embeddings cache"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            print(f"🗑️  Cleared cache: {self.cache_file}")


# Convenience function for testing
def test_vector_store():
    """Test the vector store with sample data"""
    print("\n" + "="*70)
    print("VECTOR STORE TEST")
    print("="*70 + "\n")
    
    # Load products
    with open('products_organized.json', 'r') as f:
        data = json.load(f)
    
    categories = data.get('categories', {})
    products = []
    
    for cat_name, cat_data in categories.items():
        for product in cat_data.get('products', []):
            product['category'] = cat_name
            products.append(product)
    
    print(f"Loaded {len(products)} products")
    
    # Build vector store
    vs = VectorStore()
    vs.build_embeddings(products)
    
    # Test queries
    test_queries = [
        "v5",
        "v5 xl",
        "best flavor",
        "beginner",
        "jar",
        "glass",
        "ruby twist"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = vs.semantic_search(query, top_k=3)
        
        for i, (product_id, score) in enumerate(results, 1):
            product = vs.get_product(product_id)
            print(f"  {i}. {product['name'][:60]}... (score: {score:.3f})")


if __name__ == "__main__":
    test_vector_store()
