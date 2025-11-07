#!/usr/bin/env python3
"""
Divine Tribe Chatbot v8.0 - CONTEXT-AWARE HYBRID (CLEAN)
✅ CAG Cache for instant facts
✅ Context Manager for follow-up questions
✅ Mistral for reasoning & advice
✅ Markdown rendering
✅ Multi-turn conversation awareness
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

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.product_database import ProductDatabase
from modules.conversation_memory import ConversationMemory
from modules.conversation_logger import ConversationLogger

# Import CAG and Agent Router
try:
    from modules.cag_cache import CAGCache
    from modules.agent_router import AgentRouter
    CAG_AVAILABLE = True
    print("✅ CAG + Agent Router loaded!")
except ImportError:
    CAG_AVAILABLE = False
    print("⚠️  CAG not available")

# Import Context Manager
try:
    from modules.context_manager import ContextManager
    CONTEXT_MANAGER_AVAILABLE = True
    print("✅ Context Manager loaded!")
except ImportError:
    CONTEXT_MANAGER_AVAILABLE = False
    print("⚠️  ContextManager not available")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize all systems
database = ProductDatabase('products_organized.json')
memory = ConversationMemory(max_history=10)
logger = ConversationLogger()
context_manager = ContextManager() if CONTEXT_MANAGER_AVAILABLE else None

# Initialize CAG + Agent Router
if CAG_AVAILABLE:
    cag_cache = CAGCache()
    agent_router = AgentRouter(cag_cache, database)
    print("✅ CAG Cache: 5 main products cached")
    print("✅ Agent Router: Smart routing enabled")
else:
    cag_cache = None
    agent_router = None

print("✅ Mistral AI integrated!")
print("✅ Context awareness active!")
print("✅ Markdown rendering enabled!")
print("📦 Loaded products")


def convert_markdown_to_html(text: str) -> str:
    """Convert markdown formatting to HTML for beautiful display"""
    html = markdown.markdown(text, extensions=['nl2br'])
    return html


def resolve_query_with_context(query: str, session_id: str) -> tuple:
    """
    Resolve query using context manager for follow-up questions.
    
    Returns: (resolved_query, context_dict)
    """
    if not context_manager:
        return query, None
    
    # Check if this is a follow-up question
    follow_up_context = context_manager.resolve_follow_up(session_id, query)
    
    if follow_up_context and follow_up_context.get('referent_products'):
        # User said "it", "that", etc - we know what they mean!
        products = follow_up_context['referent_products']
        
        if products:
            product_name = products[0].get('name', 'Unknown')
            print(f"🔗 Follow-up resolved: '{query}' → about '{product_name}'")
            
            # Expand the query with context
            resolved_query = f"{query} {product_name}"
            return resolved_query, follow_up_context
    
    return query, None


def generate_response_with_mistral(
    query: str,
    intent: str,
    products: List[Dict],
    session_id: str,
    context: Optional[Dict] = None,
    max_tokens: int = 1500
) -> str:
    """
    Generate response with Mistral using context awareness.
    Adapts conversation style based on intent - matches human support patterns.
    """
    history = memory.get_history(session_id)
    
    # Build context from products
    if products:
        product_context = "\n\n".join([
            f"**{p['name']}**\nPrice: {p.get('price', 'Check website')}\nURL: {p.get('url', 'https://ineedhemp.com')}\nDescription: {p.get('description', '')[:300]}"
            for p in products[:3]
        ])
    else:
        product_context = "No specific products found for this query."
    
    # Get conversation context from context_manager
    conversation_summary = ""
    if context_manager:
        summary = context_manager.get_conversation_summary(session_id)
        if summary.get('user_preferences'):
            prefs = summary['user_preferences']
            conversation_summary = f"\n\nUser preferences: {', '.join(f'{k}={v}' for k, v in prefs.items())}"
        
        if summary.get('last_products'):
            last_prods = summary['last_products']
            conversation_summary += f"\nRecently discussed: {', '.join(last_prods[:2])}"
    
    # Build intent-specific system prompt (MATCHES HUMAN PATTERNS!)
    base_rules = """CRITICAL RULES:
- Use ONLY the product information provided below
- NEVER make up product names, features, or specifications
- NEVER mention products not in the list below
- Make product names bold and linked: **[Product Name](url)**
- Email for support: matt@ineedhemp.com
- Website: https://ineedhemp.com"""

    # INTENT-SPECIFIC PROMPTS (matches human conversation patterns)
    if intent == 'reasoning' or intent == 'general':
        # For "what should I buy" type questions
        system_prompt = f"""You are Divine Tribe's helpful product advisor, just like Matt who runs the company.

🚨 MANDATORY FIRST QUESTION 🚨

When someone asks "what should I buy" or asks for recommendations:
YOU MUST ONLY ASK: "What material do you use - **dry herb (flower)** or **concentrates (wax/dabs)**?"

Then STOP and wait for their answer.

Do NOT mention any products yet.
Do NOT say "if they say" or show your reasoning.
Just ask the question and nothing else.

EXAMPLE:
User: "what should I buy for flavor"
You: "Great question! Do you use **dry herb (flower)** or **concentrates (wax/dabs)**?"

User: "best for beginners"
You: "I can help! Do you use **dry herb (flower)** or **concentrates (wax/dabs)**?"

AFTER they answer "concentrates" or "dry herb", THEN recommend:
• Concentrates + Flavor → V5 XL with Glass Vortex Top
• Concentrates + Beginner → Core Deluxe  
• Dry Herb (any need) → Ruby Twist

{base_rules}

AVAILABLE PRODUCTS:
{product_context}
{conversation_summary}"""

    elif intent == 'troubleshooting':
        # For technical problems
        system_prompt = f"""You are Divine Tribe's technical support specialist.

YOUR TROUBLESHOOTING APPROACH (MATCH HUMAN SUPPORT):
1. Ask diagnostic questions first (like "What's your resistance reading?")
2. Guide them through basic checks
3. Only escalate to Matt if needed

EXAMPLE CONVERSATION PATTERN:
User: "my v5 won't work"
You: "Let's troubleshoot this together! First question - is it giving you a resistance reading? If so, what Ω value do you see?

If you're getting a reading around 0.45-0.52Ω, let's check your settings:
• TCR: Should be 180-245
• Wattage: 35-40W
• Temperature: 380-490°F

Let me know what you find and we'll figure this out!"

Be conversational, ask questions, guide them step by step.

{base_rules}

PRODUCT CONTEXT:
{product_context}
{conversation_summary}"""

    elif intent == 'comparison':
        # For "X vs Y" questions
        system_prompt = f"""You are Divine Tribe's product comparison expert.

YOUR COMPARISON STYLE:
1. List the key differences in simple bullet points
2. Give a clear recommendation based on use case
3. End with "Choose X if..." statements

EXAMPLE:
User: "v5 xl vs core deluxe"
You: "Great question! Here's the breakdown:

**V5 XL:**
• Best flavor
• Rebuildable (for tinkerers)
• Needs a 510 mod
• More customizable

**Core Deluxe:**
• Easiest to use
• All-in-one eRig
• Preset temperatures
• Better for beginners

**Choose V5 XL if:** You want the best flavor and don't mind using a mod
**Choose Core Deluxe if:** You want simplicity and an all-in-one device

What's more important to you - flavor/customization or ease of use?"

{base_rules}

AVAILABLE PRODUCTS:
{product_context}
{conversation_summary}"""

    else:
        # General fallback
        system_prompt = f"""You are Divine Tribe's friendly AI assistant.

Be conversational and helpful. Match the customer's tone - if they're frustrated, be empathetic. If they're excited, match their energy!

{base_rules}

AVAILABLE PRODUCTS:
{product_context}
{conversation_summary}"""

    # Add recent conversation history
    conversation = []
    for exchange in history[-3:]:
        conversation.append(f"User: {exchange['user']}")
        conversation.append(f"Assistant: {exchange['bot'][:100]}...")
    
    if conversation:
        system_prompt += f"\n\nRECENT CONVERSATION:\n" + "\n".join(conversation)
    
    # Generate with Mistral
    try:
        response = ollama.generate(
            model='mistral',
            prompt=f"User query: {query}",
            system=system_prompt,
            options={
                'temperature': 0.7,
                'num_predict': max_tokens,
                'top_p': 0.9
            }
        )
        return response['response'].strip()
    except Exception as e:
        print(f"Mistral error: {e}")
        return "I'm having trouble right now. Email matt@ineedhemp.com for help! 😊"


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Main chat endpoint with FULL context awareness + Mistral hybrid"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # STEP 1: Resolve follow-up questions using context
    resolved_query, follow_up_context = resolve_query_with_context(user_message, session_id)
    
    # Check if this is an answer to a question
    is_answer = follow_up_context and follow_up_context.get('is_answer', False)
    
    # STEP 2: Get conversation context for retrieval
    retrieval_context = None
    if context_manager:
        retrieval_context = context_manager.get_retrieval_context(session_id)
    
    # STEP 3: Route the query (if it's an answer, skip routing and go straight to Mistral)
    if is_answer:
        # User is answering a question - go to Mistral reasoning
        products = database.search(user_message, max_results=3, context=retrieval_context)
        bot_response = generate_response_with_mistral(
            user_message,
            'reasoning',
            products,
            session_id,
            context=follow_up_context,
            max_tokens=300
        )
        intent = 'reasoning'
        products_shown = products
    elif CAG_AVAILABLE and agent_router:
        routing = agent_router.route(resolved_query, context=retrieval_context)
        route = routing['route']
        
        print(f"🎯 Route: {route} | Reasoning: {routing['reasoning']}")
        
        # CUSTOMER SERVICE ROUTES (Priority 1-5)
        if route == 'troubleshooting':
            bot_response = routing['data']
            intent = 'troubleshooting'
            products_shown = []
            # If response is generic, enhance with Mistral
            if not bot_response or 'tell me more' in bot_response.lower():
                products = database.search(resolved_query, max_results=2, context=retrieval_context)
                bot_response = generate_response_with_mistral(
                    user_message,
                    'troubleshooting',
                    products,
                    session_id,
                    context=follow_up_context,
                    max_tokens=500
                )
        
        elif route == 'how_to':
            bot_response = routing['data']
            intent = 'how_to'
            products_shown = []
        
        elif route == 'warranty':
            bot_response = routing['data']
            intent = 'warranty'
            products_shown = []
        
        elif route == 'return':
            bot_response = routing['data']
            intent = 'return'
            products_shown = []
        
        elif route == 'order':
            bot_response = routing['data']
            intent = 'order'
            products_shown = []
        
        # MISTRAL REASONING (for advice/recommendations)
        elif route == 'mistral':
            intent = 'reasoning'
            products = database.search(resolved_query, max_results=3, context=retrieval_context)
            bot_response = generate_response_with_mistral(
                user_message,
                intent,
                products,
                session_id,
                context=follow_up_context
            )
            products_shown = products
        
        # PRODUCT INFO (Cached)
        elif route == 'cache':
            bot_response = routing['data']
            intent = 'product_info'
            products_shown = [cag_cache.get_cached_product(routing.get('product_key', ''))]
        
        # SUPPORT INFO (Cached)
        elif route == 'support':
            bot_response = routing['data']
            intent = 'support'
            products_shown = []
        
        # COMPARISON (Cached)
        elif route == 'comparison':
            bot_response = routing['data']
            intent = 'comparison'
            products_shown = []
        
        # CATEGORY LISTING (NEW! - for jars, glass, cups)
        elif route == 'category':
            bot_response = routing['data']
            intent = 'category'
            products_shown = []
        
        # REJECT OFF-TOPIC
        elif route == 'reject':
            bot_response = routing['data']
            intent = 'off_topic'
            products_shown = []
        
        # RAG SEARCH (For accessories)
        elif route == 'rag':
            intent = 'product_search'
            bot_response = agent_router.execute_rag_search(resolved_query, max_results=5)
            products_shown = []
        
        # GENERAL (Use Mistral)
        else:
            intent = 'general'
            bot_response = generate_response_with_mistral(
                user_message,
                intent,
                [],
                session_id,
                max_tokens=250
            )
            products_shown = []
    
    else:
        # FALLBACK: Simple search
        print("⚠️  CAG not available - using fallback")
        products = database.search(resolved_query, max_results=5, context=retrieval_context)
        bot_response = generate_response_with_mistral(user_message, 'general', products, session_id)
        products_shown = products
        intent = 'fallback'
    
    # Convert markdown to HTML
    bot_response_html = convert_markdown_to_html(bot_response)
    
    # STEP 4: Update all memory systems
    memory.add_exchange(session_id, user_message, bot_response, intent)
    
    # Update context manager with products shown
    if context_manager and products_shown:
        # Convert product names to full product dicts for context
        product_dicts = []
        for p in products_shown:
            if isinstance(p, dict) and p:  # Make sure it's a valid dict
                product_dicts.append(p)
            elif isinstance(p, str):
                # Try to find product by name
                found = database.get_by_name(p)
                if found:
                    product_dicts.append(found)
        
        if product_dicts:  # Only add if we have valid products
            context_manager.add_exchange(
                session_id,
                user_message,
                bot_response,
                products_shown=product_dicts,
                intent=intent
            )
    
    # Log conversation
    logger.log_conversation(
        session_id=session_id,
        user_query=user_message,
        bot_response=bot_response,
        products_shown=products_shown if isinstance(products_shown, list) else [],
        intent=intent,
        confidence=1.0
    )
    
    return jsonify({
        'response': bot_response_html,
        'status': 'success',
        'intent': intent,
        'session_id': session_id
    })


@app.route('/')
def home():
    return "<h1>🤖 Divine Tribe AI v8.0 - Context-Aware Hybrid System</h1>"


@app.route('/generate_image', methods=['POST', 'OPTIONS'])
def generate_image():
    """Generate AI images using ComfyUI"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        from modules.image_generator import ImageGenerator
        gen = ImageGenerator()
        
        if not gen.check_comfyui_running():
            response = jsonify({'status': 'error', 'message': 'Image generator offline'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        result = gen.generate_for_chatbot(prompt)
        
        if result['has_image']:
            response = jsonify({'status': 'success', 'image_data': result['image_data']})
        else:
            response = jsonify({'status': 'error', 'message': 'Generation failed'})
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        response = jsonify({'status': 'error', 'message': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        ollama_status = "connected"
        try:
            ollama.list()
        except:
            ollama_status = "offline"
        
        stats = database.get_search_stats()
        stats['cag_enabled'] = CAG_AVAILABLE
        stats['context_manager_enabled'] = CONTEXT_MANAGER_AVAILABLE
        stats['mistral_routing_enabled'] = True
        
        return jsonify({
            'status': 'healthy',
            'ollama': ollama_status,
            'search_stats': stats,
            'context_manager': CONTEXT_MANAGER_AVAILABLE,
            'cag_cache': CAG_AVAILABLE
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 DIVINE TRIBE CHATBOT v8.0 - CONTEXT-AWARE HYBRID")
    print("="*70)
    print("✅ CAG Cache: Instant facts (no LLM)")
    print("✅ Context Manager: Follow-up question awareness")
    print("✅ Mistral Routing: AI reasoning for advice")
    print("✅ Markdown: Beautiful formatting")
    print("✅ Multi-turn: Remembers conversation flow")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
