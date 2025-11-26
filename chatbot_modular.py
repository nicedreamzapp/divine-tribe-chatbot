#!/usr/bin/env python3
"""
Divine Tribe Chatbot - Production Ready
Clean responses, no confusing terminology
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import List, Dict, Optional
import json
import ollama
import re
import sys
import os
import markdown

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.product_database import ProductDatabase
from modules.conversation_memory import ConversationMemory
from modules.conversation_logger import ConversationLogger
from modules.image_generator import ImageGenerator

try:
    from modules.cag_cache import CAGCache
    from modules.agent_router import AgentRouter
    CAG_AVAILABLE = True
except ImportError:
    CAG_AVAILABLE = False

try:
    from modules.context_manager import ContextManager
    CONTEXT_MANAGER_AVAILABLE = True
except ImportError:
    CONTEXT_MANAGER_AVAILABLE = False

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize systems
database = ProductDatabase('products_clean.json')
memory = ConversationMemory(max_history=10)
logger = ConversationLogger()
context_manager = ContextManager() if CONTEXT_MANAGER_AVAILABLE else None
image_gen = ImageGenerator()

if CAG_AVAILABLE:
    cag_cache = CAGCache()
    agent_router = AgentRouter(cag_cache, database, context_manager)
else:
    cag_cache = None
    agent_router = None

print("✅ Divine Tribe Chatbot - Production Ready")
print(f"✅ Products loaded: {len(database.products)}")
print(f"✅ Image generation: {'Enabled' if image_gen.check_comfyui_running() else 'Offline'}")


def convert_markdown_to_html(text: str) -> str:
    """Convert markdown to HTML"""
    return markdown.markdown(text, extensions=['nl2br'])


def clean_product_description(product: Dict) -> str:
    """
    Clean product description - Remove "hash-ready" and confusing terms
    """
    name = product.get('name', '')
    desc = product.get('description', '')
    
    # Remove "hash-ready" phrase completely
    desc = re.sub(r'\bhash[-\s]ready\b[^.]*\.?', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'hash-ready right out of the box[,.]?', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'It\'s hash-ready[^.]*\.', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'Plus, it\'s hash-ready[^.]*\.', '', desc, flags=re.IGNORECASE)
    
    # Clean up any double spaces or periods from removals
    desc = re.sub(r'\s+', ' ', desc)
    desc = re.sub(r'\.+', '.', desc)
    
    # Clean HTML tags
    desc = re.sub(r'<[^>]+>', '', desc)
    desc = desc.strip()[:300]
    
    return desc


def resolve_query_with_context(query: str, session_id: str) -> tuple:
    """Resolve follow-up questions using context"""
    if not context_manager:
        return query, None
    
    follow_up_context = context_manager.resolve_follow_up(session_id, query)
    
    if follow_up_context and follow_up_context.get('referent_products'):
        products = follow_up_context['referent_products']
        if products:
            product_name = products[0].get('name', 'Unknown')
            print(f"🔗 Follow-up: '{query}' → '{product_name[:30]}...'")
            return f"{query} {product_name}", follow_up_context
    
    return query, None


def generate_conversational_product_response(
    query: str,
    products: List[Dict],
    session_id: str
) -> str:
    """
    Generate conversational response with CLEANED product descriptions
    STRICT: Only use facts from RAG data, no hallucinating
    """
    if not products:
        return "I couldn't find products for that. What are you looking for?\n\n📧 matt@ineedhemp.com"

    # Build product context with FULL descriptions for accuracy
    product_details = []
    for p in products[:5]:
        name = p.get('name', 'Unknown')
        url = p.get('url', 'https://ineedhemp.com')
        desc = p.get('description', '')

        # Clean HTML but keep all product facts
        desc = re.sub(r'<[^>]+>', ' ', desc)
        desc = re.sub(r'@keyframes[^}]+\}[^}]*\}', '', desc)  # Remove CSS
        desc = re.sub(r'\.[a-zA-Z-]+\s*\{[^}]*\}', '', desc)  # Remove CSS classes
        desc = re.sub(r'document\.addEventListener[^;]+;', '', desc)  # Remove JS
        desc = re.sub(r'\\n', ' ', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()

        # Extract key specs (GSM, materials, sizes)
        specs = []
        import re as regex
        gsm_match = regex.search(r'(\d+)\s*GSM', desc, regex.IGNORECASE)
        if gsm_match:
            specs.append(f"Weight: {gsm_match.group(1)} GSM")

        product_details.append(f"PRODUCT: {name}\nURL: {url}\nSPECS: {', '.join(specs) if specs else 'See description'}\nDESCRIPTION: {desc[:500]}")

    product_context = "\n\n---\n\n".join(product_details)

    # Get conversation history
    history = memory.get_history(session_id, max_turns=2)
    history_text = ""
    if history:
        history_text = "\n\nRecent conversation:\n"
        for ex in history:
            history_text += f"User: {ex['user']}\n"

    # STRICT PROMPT - Only use RAG data, no hallucinating
    system_prompt = f"""You are Divine Tribe's product advisor. You MUST follow these rules strictly:

**ABSOLUTE RULES - NEVER BREAK THESE:**

1. **ONLY STATE FACTS FROM THE PRODUCT DATA BELOW** - Do NOT make up specs, weights, features, or comparisons
2. If a spec (like GSM, weight, size) is in the product description, quote it EXACTLY
3. If you don't see a specific fact in the data, say "check the product page for details"
4. **NEVER GUESS OR INFER** - If Digicam says 280 GSM and Thick says 260 GSM, Digicam is HEAVIER (higher number = heavier)
5. For comparisons: List the EXACT specs from each product side by side
6. Format links as: **[Product Name](url)**
7. Use terminology: "concentrates" and "flower" (not "hash-ready")

**PRODUCT KNOWLEDGE:**
- Vaporizers for concentrates: Core XL Deluxe (beginner), V5/XL V5 (advanced)
- Vaporizers for flower: Ruby Twist, Gen 2 DC
- Hemp clothing: T-shirts, hoodies, pants, boxers
- Storage: UV glass jars

**RETRIEVED PRODUCT DATA (USE ONLY THIS):**

{product_context}
{history_text}

User's question: {query}

Remember: ONLY use facts from the product data above. Do not invent features or specs."""

    try:
        response = ollama.chat(
            model='mistral',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': query}
            ]
        )
        
        bot_response = response['message']['content'].strip()
        bot_response += "\n\n📧 Questions? Email matt@ineedhemp.com"
        return bot_response
        
    except Exception as e:
        print(f"❌ Mistral error: {e}")
        # Fallback
        response = "Here's what I found:\n\n"
        for i, p in enumerate(products[:5], 1):
            response += f"{i}. **[{p.get('name', 'Unknown')}]({p.get('url', 'https://ineedhemp.com')})**\n\n"
        return response + "📧 matt@ineedhemp.com"


def generate_general_knowledge_response(
    query: str,
    session_id: str,
    is_business_related: bool = False
) -> str:
    """Generate response for general knowledge questions"""

    history = memory.get_history(session_id, max_turns=3)
    history_context = ""
    if history:
        history_context = "\n\nRECENT CONVERSATION:\n"
        for ex in history:
            history_context += f"User: {ex['user']}\n"
            history_context += f"You: {ex['bot'][:100]}...\n"

    # ALWAYS identify as Divine Tribe assistant - NEVER have an identity crisis
    system_prompt = f"""You are Divine Tribe's helpful assistant chatbot on https://ineedhemp.com

**CRITICAL IDENTITY - NEVER FORGET:**
- You ARE Divine Tribe's chatbot
- You DO sell products at https://ineedhemp.com
- Divine Tribe is located in Humboldt County, California
- Owner: Matt Macosko
- Contact: matt@ineedhemp.com

**ABOUT DIVINE TRIBE:**
- Founded by Matt Macosko
- Based in Humboldt County, California
- Specializes in: Cannabis vaporizers (concentrates & dry herb), hemp clothing, glass storage jars
- Products: Core eRig, V5/V5 XL (concentrates), Ruby Twist, Gen 2 DC (flower), hemp apparel, UV glass jars
- Ships internationally (discreet packaging)
- Discount code: thankyou10 for 10% off
- Known for great customer service and eco-friendly practices

**RULES:**
1. Answer their question helpfully and accurately
2. If the question relates to products/shopping/shipping, remind them about ineedhemp.com
3. NEVER say "I don't sell products" - you ARE the Divine Tribe store chatbot!
4. NEVER mention competitor brands
5. For creative requests (stories, jokes, raps), feel free to be fun and engaging
6. Keep responses conversational

{history_context}

User's question: {query}"""
    
    try:
        response = ollama.chat(
            model='mistral',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': query}
            ]
        )
        
        bot_response = response['message']['content'].strip()

        # Always add contact info since we're always Divine Tribe
        if "matt@ineedhemp.com" not in bot_response.lower():
            bot_response += "\n\n📧 Questions? Email matt@ineedhemp.com"

        return bot_response
        
    except Exception as e:
        print(f"❌ Mistral error: {e}")
        return "I'd love to help with that! Could you rephrase your question?"


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Main chat endpoint"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default_session')
        
        if not user_message:
            return jsonify({'response': 'Please ask me something!', 'status': 'error'})
        
        print(f"\n{'='*70}")
        print(f"💬 User ({session_id}): {user_message}")
        print(f"{'='*70}")
        
        # STEP 1: Resolve follow-up context
        resolved_query, follow_up_context = resolve_query_with_context(user_message, session_id)
        
        # STEP 2: Get retrieval context
        retrieval_context = None
        if context_manager:
            retrieval_context = context_manager.get_retrieval_context(session_id)
        
        # STEP 3: Route the query
        if not agent_router:
            bot_response = "System not fully initialized. Email matt@ineedhemp.com"
        else:
            routing_result = agent_router.route(resolved_query, retrieval_context, session_id)
            route = routing_result['route']
            
            print(f"🎯 Route: {route} - {routing_result['reasoning']}")
            
            # Execute based on route
            if route in ['cache', 'troubleshooting', 'how_to', 'warranty', 'return', 'order', 'support', 'comparison', 'competitor_mention', 'quick_answer', 'image_request']:
                bot_response = routing_result['data']
            
            elif route == 'rag' or route == 'material_shopping':
                # Get products from RAG
                products = database.search(resolved_query, max_results=5, context=retrieval_context)
                
                # Filter out replacement parts
                products = [p for p in products if 'replacement' not in p.get('name', '').lower() and p.get('category', '').lower() != 'replacement_parts']
                
                print(f"🔍 Retrieved {len(products)} products")
                if products:
                    print(f"   Top: {products[0].get('name', 'Unknown')[:50]}...")
                
                # Generate conversational response with products
                bot_response = generate_conversational_product_response(
                    user_message,
                    products,
                    session_id
                )
                
                # Update context with products shown
                if context_manager and products:
                    context_manager.add_exchange(
                        session_id,
                        user_message,
                        bot_response,
                        products,
                        'product_search'
                    )
            
            elif route == 'general_mistral':
                bot_response = generate_general_knowledge_response(
                    resolved_query,
                    session_id,
                    routing_result.get('is_business_related', False)
                )
            
            else:
                bot_response = "I'm not sure how to help with that. Email matt@ineedhemp.com"
        
        # Update memory
        memory.add_exchange(session_id, user_message, bot_response)
        
        # Log conversation
        logger.log_conversation(session_id, user_message, bot_response, [], route, 1.0)
        
        # Convert markdown to HTML
        html_response = convert_markdown_to_html(bot_response)
        
        return jsonify({
            'response': html_response,
            'status': 'success',
            'route': route
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'response': 'Something went wrong. Email matt@ineedhemp.com for help!',
            'status': 'error'
        })


@app.route('/generate_image', methods=['POST', 'OPTIONS'])
def generate_image():
    """Image generation endpoint"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'has_image': False, 'error': 'No prompt provided'})
        
        print(f"\n🎨 IMAGE REQUEST: {prompt}")
        
        # Check if ComfyUI is running
        if not image_gen.check_comfyui_running():
            print("⚠️  ComfyUI not running")
            return jsonify({'has_image': False, 'error': 'Image generator offline'})
        
        # Generate image
        result = image_gen.generate_for_chatbot(prompt)
        
        if result.get('has_image'):
            print("✅ Image generated successfully")
        else:
            print("❌ Image generation failed")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Image generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'has_image': False, 'error': str(e)})


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    comfyui_status = image_gen.check_comfyui_running()
    return jsonify({
        'status': 'healthy',
        'products': len(database.products),
        'comfyui_running': comfyui_status
    })


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 DIVINE TRIBE CHATBOT - PRODUCTION MODE")
    print("="*70)
    print("✅ No 'hash-ready' terminology")
    print("✅ Clean responses: 'concentrates' and 'flower'")
    print("✅ XL V5 prioritized, Core easiest for beginners")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=True)
