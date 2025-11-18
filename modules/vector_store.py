#!/usr/bin/env python3
"""
vector_store.py - Vector embedding store for semantic search
CLEANED: Better caching, error handling, optimized search
"""

import pickle
import os
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
import numpy as np


class VectorStore:
    """
    Vector store for semantic product search
    Uses sentence transformers for embeddings
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', cache_file: str = 'product_embeddings.pkl'):
        self.model_name = model_name
        self.cache_file = cache_file
        self.model = None
        self.embeddings = {}  # product_id -> embedding vector
        self.products = {}    # product_id -> product dict
        
    def build_index(self, products: List[Dict]):
        """Build vector index from products"""
        print("🔄 Loading sentence embedding model...")
        
        try:
            self.model = SentenceTransformer(self.model_name)
            print("✅ Embedding model ready")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            return
        
        # Try to load cached embeddings
        if self._load_cache(products):
            print(f"✅ Loaded {len(self.embeddings)} cached embeddings")
            return
        
        # Build new embeddings
        print(f"🔨 Building embeddings for {len(products)} products...")
        self._build_embeddings(products)
        
        # Save cache
        self._save_cache()
        
        print(f"✅ Built {len(self.embeddings)} embeddings")
    
    def _build_embeddings(self, products: List[Dict]):
        """Build embeddings for all products"""
        for i, product in enumerate(products):
            # Generate product ID
            product_id = product.get('id', product.get('name', f'product_{i}'))
            
            # Build searchable text
            search_text = self._build_search_text(product)
            
            # Generate embedding
            try:
                embedding = self.model.encode(search_text, convert_to_numpy=True)
                self.embeddings[product_id] = embedding
                self.products[product_id] = product
            except Exception as e:
                print(f"⚠️  Failed to embed product {product_id}: {e}")
    
    def _build_search_text(self, product: Dict) -> str:
        """Build searchable text from product data"""
        parts = []
        
        # Name (most important)
        name = product.get('name', '')
        if name:
            parts.append(name)
            parts.append(name)  # Add twice for extra weight
        
        # Description
        desc = product.get('description', '')
        if desc:
            # Clean description
            import re
            desc = re.sub(r'<[^>]+>', '', desc)  # Remove HTML
            desc = re.sub(r'\\n', ' ', desc)     # Remove newlines
            desc = re.sub(r'\s+', ' ', desc)     # Normalize spaces
            desc = desc.strip()[:500]            # Limit length
            parts.append(desc)
        
        # Category
        category = product.get('category', '')
        if category:
            parts.append(category)
        
        return ' '.join(parts)
    
    def _load_cache(self, products: List[Dict]) -> bool:
        """Load cached embeddings if available and valid"""
        if not os.path.exists(self.cache_file):
            return False
        
        try:
            print(f"📂 Loading embeddings from cache: {self.cache_file}")
            with open(self.cache_file, 'rb') as f:
                cache = pickle.load(f)
            
            # Validate cache
            if 'model_name' not in cache or cache['model_name'] != self.model_name:
                print("⚠️  Cache model mismatch, rebuilding...")
                return False
            
            if 'embeddings' not in cache or 'products' not in cache:
                print("⚠️  Invalid cache format, rebuilding...")
                return False
            
            # Check if product list changed
            cached_product_count = len(cache['products'])
            current_product_count = len(products)
            
            if cached_product_count != current_product_count:
                print(f"⚠️  Product count changed ({cached_product_count} → {current_product_count}), rebuilding...")
                return False
            
            # Load cached data
            self.embeddings = cache['embeddings']
            self.products = cache['products']
            
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to load cache: {e}")
            return False
    
    def _save_cache(self):
        """Save embeddings to cache file"""
        try:
            cache = {
                'model_name': self.model_name,
                'embeddings': self.embeddings,
                'products': self.products
            }
            
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache, f)
            
            print(f"💾 Saved embeddings to cache: {self.cache_file}")
            
        except Exception as e:
            print(f"⚠️  Failed to save cache: {e}")
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Semantic search using vector similarity
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of (product_id, similarity_score) tuples
        """
        if not self.model or not self.embeddings:
            print("⚠️  Vector store not initialized")
            return []
        
        try:
            # Encode query
            query_embedding = self.model.encode(query, convert_to_numpy=True)
            
            # Calculate similarities
            similarities = []
            for product_id, product_embedding in self.embeddings.items():
                # Cosine similarity
                similarity = self._cosine_similarity(query_embedding, product_embedding)
                similarities.append((product_id, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            print(f"❌ Semantic search error: {e}")
            return []
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Get product by ID"""
        return self.products.get(product_id)
    
    def get_similar_products(self, product_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find similar products to a given product
        
        Args:
            product_id: Product ID to find similar products for
            top_k: Number of results
        
        Returns:
            List of (product_id, similarity_score) tuples
        """
        if product_id not in self.embeddings:
            print(f"⚠️  Product {product_id} not found in embeddings")
            return []
        
        product_embedding = self.embeddings[product_id]
        
        similarities = []
        for pid, emb in self.embeddings.items():
            if pid == product_id:
                continue  # Skip self
            
            similarity = self._cosine_similarity(product_embedding, emb)
            similarities.append((pid, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def clear_cache(self):
        """Delete cache file"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            print(f"🗑️  Deleted cache: {self.cache_file}")
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            'model': self.model_name,
            'embeddings_count': len(self.embeddings),
            'products_count': len(self.products),
            'cache_file': self.cache_file,
            'cache_exists': os.path.exists(self.cache_file)
        }


def test_vector_store():
    """Test the vector store"""
    print("\n" + "="*70)
    print("VECTOR STORE TEST")
    print("="*70 + "\n")
    
    # Sample products
    products = [
        {
            'id': 'v5',
            'name': 'Divine Crossing V5',
            'description': 'Rebuildable concentrate atomizer with ceramic cup',
            'category': 'concentrates'
        },
        {
            'id': 'core',
            'name': 'Core XL Deluxe',
            'description': 'All-in-one eRig for concentrates',
            'category': 'concentrates'
        },
        {
            'id': 'ruby',
            'name': 'Ruby Twist',
            'description': 'Desktop ball vape for dry herb',
            'category': 'dry_herb'
        }
    ]
    
    # Build index
    vs = VectorStore()
    vs.build_index(products)
    
    # Stats
    print("\nVector Store Stats:")
    stats = vs.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test search
    print("\nTest Searches:")
    test_queries = [
        "concentrate vaporizer",
        "dry herb device",
        "all in one erig"
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        results = vs.semantic_search(query, top_k=2)
        for product_id, score in results:
            product = vs.get_product(product_id)
            print(f"    {product['name']}: {score:.3f}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    test_vector_store()
