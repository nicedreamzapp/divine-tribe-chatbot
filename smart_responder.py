#!/usr/bin/env python3
"""
Smart Email Responder - Integrates chatbot intelligence into email responses
Uses RAG, CAG, and WooCommerce for smart, accurate responses
"""

import os
import re
import json
from datetime import datetime
from typing import Optional, Dict, Tuple
from dotenv import load_dotenv
import anthropic

# Import chatbot modules
from modules.cag_cache import CAGCache
from modules.rag_retriever import RAGRetriever
from modules.product_database import ProductDatabase
from woo_client import WooCommerceClient

load_dotenv()

# Initialize components
claude = anthropic.Anthropic()
CLAUDE_MODEL = "claude-3-5-haiku-20241022"

# Lazy-loaded components
_rag_retriever = None
_product_db = None
_woo_client = None
_cag_cache = None


def get_rag():
    global _rag_retriever
    if _rag_retriever is None:
        _rag_retriever = RAGRetriever()
        # Load products
        try:
            import json
            products_path = os.path.join(os.path.dirname(__file__), 'products_clean.json')
            with open(products_path, 'r') as f:
                data = json.load(f)
                # Handle nested format
                products = data.get('products', data) if isinstance(data, dict) else data
                _rag_retriever.load_products(products)
                print(f"RAG loaded {len(products)} products")
        except Exception as e:
            print(f"RAG product load error: {e}")
    return _rag_retriever


def get_products():
    global _product_db
    if _product_db is None:
        _product_db = ProductDatabase()
    return _product_db


def get_woo():
    global _woo_client
    if _woo_client is None:
        try:
            _woo_client = WooCommerceClient()
        except:
            pass
    return _woo_client


def get_cag():
    global _cag_cache
    if _cag_cache is None:
        _cag_cache = CAGCache()
    return _cag_cache


# =============================================================================
# EMAIL INTENT DETECTION
# =============================================================================

def classify_email(subject: str, body: str) -> Dict:
    """Classify email intent and extract key info"""
    text = f"{subject} {body}".lower()

    result = {
        'intent': 'general',
        'order_numbers': [],
        'product_mentions': [],
        'is_urgent': False,
        'needs_order_lookup': False
    }

    # Extract order numbers (formats: #123456, order 123456, order# 123456)
    order_patterns = [
        r'#(\d{5,7})',
        r'order\s*#?\s*(\d{5,7})',
        r'order\s+number\s*:?\s*(\d{5,7})',
    ]
    for pattern in order_patterns:
        matches = re.findall(pattern, text)
        result['order_numbers'].extend(matches)
    result['order_numbers'] = list(set(result['order_numbers']))

    # Detect intent
    if any(w in text for w in ['where is my order', 'tracking', 'shipped', 'delivery', 'when will']):
        result['intent'] = 'order_status'
        result['needs_order_lookup'] = True
    elif any(w in text for w in ['return', 'refund', 'exchange', 'send back']):
        result['intent'] = 'return_request'
        result['needs_order_lookup'] = bool(result['order_numbers'])
    elif any(w in text for w in ['not working', 'broken', 'defective', 'warranty', 'issue', 'problem']):
        result['intent'] = 'technical_support'
    elif any(w in text for w in ['recommend', 'which', 'best', 'looking for', 'suggestion', 'should i get']):
        result['intent'] = 'product_recommendation'
    elif any(w in text for w in ['how to', 'how do', 'settings', 'temperature', 'use the']):
        result['intent'] = 'usage_question'
    elif any(w in text for w in ['price', 'cost', 'discount', 'coupon', 'sale']):
        result['intent'] = 'pricing'
    elif any(w in text for w in ['cancel', 'urgent', 'asap', 'immediately']):
        result['is_urgent'] = True

    # Detect product mentions
    product_keywords = ['v5', 'core', 'dtv5', 'dtv4', 'sic', 'titanium', 'quartz', 'pico', 'rimC', 'sequoia']
    for kw in product_keywords:
        if kw.lower() in text:
            result['product_mentions'].append(kw)

    return result


# =============================================================================
# INFORMATION GATHERING
# =============================================================================

def lookup_order(order_number: str) -> Optional[Dict]:
    """Look up order from WooCommerce"""
    woo = get_woo()
    if not woo:
        return None

    try:
        order = woo.get_order(order_number)
        if order:
            return {
                'id': order.get('id'),
                'status': order.get('status'),
                'total': order.get('total'),
                'date_created': order.get('date_created'),
                'shipping': order.get('shipping', {}),
                'line_items': [{'name': i.get('name'), 'quantity': i.get('quantity')}
                              for i in order.get('line_items', [])],
                'tracking': order.get('meta_data', [])  # May contain tracking info
            }
    except Exception as e:
        print(f"Order lookup error: {e}")
    return None


def search_products(query: str) -> str:
    """Search for relevant products using RAG"""
    try:
        rag = get_rag()
        results = rag.retrieve(query, top_k=5)

        if not results:
            return ""

        product_info = []
        for r in results:
            product_info.append(f"- {r.get('name', 'Unknown')}: {r.get('description', '')[:200]}")
            if r.get('url'):
                product_info.append(f"  Link: {r.get('url')}")

        return "\n".join(product_info)
    except Exception as e:
        print(f"RAG search error: {e}")
        return ""


def check_cag_cache(query: str) -> Optional[str]:
    """Check if we have a cached answer"""
    try:
        cag = get_cag()
        cached = cag.check_cache(query)
        if cached:
            return cached
    except Exception as e:
        print(f"CAG cache error: {e}")
    return None


# =============================================================================
# RESPONSE GENERATION
# =============================================================================

def generate_smart_response(email_data: Dict) -> Tuple[str, Dict]:
    """
    Generate intelligent email response using all available context
    Returns: (response_text, metadata)
    """
    subject = email_data.get('subject', '')
    body = email_data.get('body', '')
    from_email = email_data.get('from_email', '')
    from_name = email_data.get('from_name', '')

    # Step 1: Classify email intent
    classification = classify_email(subject, body)

    # Step 2: Gather relevant information
    context_parts = []
    metadata = {
        'intent': classification['intent'],
        'used_cag': False,
        'used_rag': False,
        'used_woo': False,
        'order_info': None
    }

    # Check CAG cache first for common questions
    query = f"{subject} {body}"
    cached_answer = check_cag_cache(query)
    if cached_answer:
        metadata['used_cag'] = True
        context_parts.append(f"CACHED ANSWER (use this as basis):\n{cached_answer}")

    # Look up order if needed
    if classification['needs_order_lookup'] and classification['order_numbers']:
        for order_num in classification['order_numbers']:
            order_info = lookup_order(order_num)
            if order_info:
                metadata['used_woo'] = True
                metadata['order_info'] = order_info
                context_parts.append(f"""
ORDER #{order_num} INFORMATION:
- Status: {order_info.get('status', 'Unknown')}
- Total: ${order_info.get('total', 'Unknown')}
- Date: {order_info.get('date_created', 'Unknown')}
- Items: {', '.join([f"{i['name']} x{i['quantity']}" for i in order_info.get('line_items', [])])}
""")

    # Search products if relevant
    if classification['intent'] in ['product_recommendation', 'usage_question', 'technical_support']:
        product_context = search_products(query)
        if product_context:
            metadata['used_rag'] = True
            context_parts.append(f"RELEVANT PRODUCTS:\n{product_context}")

    # Step 3: Build system prompt
    context_str = "\n\n".join(context_parts) if context_parts else "No additional context available."

    system_prompt = f"""You are Matt's email assistant for Divine Tribe (ineedhemp.com), a vaporizer company.

EMAIL CLASSIFICATION:
- Intent: {classification['intent']}
- Urgent: {classification['is_urgent']}
- Products mentioned: {', '.join(classification['product_mentions']) or 'None'}

GATHERED CONTEXT:
{context_str}

RESPONSE RULES:
1. Be friendly, helpful, and sound human - not robotic
2. Keep responses concise but complete
3. Sign as "Matt" from "Divine Tribe"
4. NEVER make up order information - only use provided order data
5. If you don't have order info, ask for order number or suggest checking their email confirmation
6. Include relevant product links when helpful
7. For returns: 30-day return policy, must be unused/original packaging
8. For warranty: Most products have 1-year warranty

COMMUNITY LINKS (include when relevant):
- Discord: https://discord.com/invite/f3qwvp56be
- Reddit: https://www.reddit.com/r/DivineTribeVaporizers/

Write ONLY the email response body. No subject line. Start with greeting using customer's name if available."""

    # Step 4: Generate response
    try:
        customer_name = from_name.split()[0] if from_name else ""

        response = claude.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[{
                'role': 'user',
                'content': f"""Customer email:

From: {from_name} <{from_email}>
Subject: {subject}

{body}

---
Write a helpful response."""
            }]
        )

        response_text = response.content[0].text.strip()
        return response_text, metadata

    except Exception as e:
        print(f"Claude error: {e}")
        return None, metadata


# =============================================================================
# EMAIL LOGGING FOR LEARNING
# =============================================================================

def log_email_interaction(email_data: Dict, response: str, metadata: Dict, feedback: str = None):
    """Log email interaction for future learning/training"""
    log_dir = "email_logs"
    os.makedirs(log_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"emails_{today}.jsonl")

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'email_id': email_data.get('id'),
        'from_email': email_data.get('from_email'),
        'subject': email_data.get('subject'),
        'body': email_data.get('body'),
        'intent': metadata.get('intent'),
        'used_cag': metadata.get('used_cag'),
        'used_rag': metadata.get('used_rag'),
        'used_woo': metadata.get('used_woo'),
        'response': response,
        'feedback': feedback,  # 'approved', 'edited', 'rejected'
        'edited_response': None  # Fill in if user edits
    }

    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def get_similar_past_emails(query: str, limit: int = 3) -> list:
    """Find similar past emails for context (future: use embeddings)"""
    # For now, simple keyword matching
    # Future: embed emails and use vector similarity
    log_dir = "email_logs"
    if not os.path.exists(log_dir):
        return []

    similar = []
    query_words = set(query.lower().split())

    for filename in sorted(os.listdir(log_dir), reverse=True)[:7]:  # Last 7 days
        if not filename.endswith('.jsonl'):
            continue

        filepath = os.path.join(log_dir, filename)
        with open(filepath, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get('feedback') == 'approved':
                        email_words = set(f"{entry.get('subject', '')} {entry.get('body', '')}".lower().split())
                        overlap = len(query_words & email_words)
                        if overlap > 3:
                            similar.append({
                                'subject': entry.get('subject'),
                                'response': entry.get('edited_response') or entry.get('response'),
                                'score': overlap
                            })
                except:
                    continue

    # Sort by relevance and return top matches
    similar.sort(key=lambda x: x['score'], reverse=True)
    return similar[:limit]


# =============================================================================
# MAIN API
# =============================================================================

def generate_email_response(email_data: Dict) -> Dict:
    """
    Main entry point - generate smart response for an email
    Returns dict with response and metadata
    """
    response_text, metadata = generate_smart_response(email_data)

    if response_text:
        # Log the interaction
        log_email_interaction(email_data, response_text, metadata)

    return {
        'response': response_text,
        'intent': metadata.get('intent'),
        'used_cag': metadata.get('used_cag'),
        'used_rag': metadata.get('used_rag'),
        'used_woo': metadata.get('used_woo'),
        'order_info': metadata.get('order_info')
    }


# Quick test
if __name__ == "__main__":
    test_email = {
        'id': 'test_001',
        'from_email': 'test@example.com',
        'from_name': 'John Doe',
        'subject': 'Which vape for concentrates?',
        'body': 'Hey, I\'m new to vaping and looking for something good for concentrates. Budget around $150. What do you recommend?'
    }

    print("Testing smart responder...")
    result = generate_email_response(test_email)
    print(f"\nIntent: {result['intent']}")
    print(f"Used CAG: {result['used_cag']}")
    print(f"Used RAG: {result['used_rag']}")
    print(f"\nResponse:\n{result['response']}")
