#!/usr/bin/env python3
"""
Divine Tribe Chatbot - MISTRAL AI with AGGRESSIVE FIXES
- Forces correct email spelling
- Fixed Cub description
- Post-processing to catch typos
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import ollama
import re
from modules.enhanced_classifier import EnhancedQueryClassifier
from modules.product_database import ProductDatabase
from modules.conversation_memory import ConversationMemory
from modules.conversation_logger import ConversationLogger

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

classifier = EnhancedQueryClassifier()
database = ProductDatabase('products_organized.json')
memory = ConversationMemory(max_history=10)
logger = ConversationLogger()

print("✅ Mistral AI integrated!")
print("📦 Loaded 138 products from organized database")
print("🧠 Smart modules active")
print("⚡ Aggressive fixes enabled (email typo correction)")

def build_system_prompt(intent, products, query):
    """Build system prompt - AGGRESSIVE about email spelling"""
    
    base = """You are a helpful Divine Tribe vaporizer expert. Be CONCISE (under 100 words).

KEY PRODUCTS:
- V5 XL = Best FLAVOR (pure ceramic)
- Core Deluxe = EASIEST for beginners (6 temps)
- Ruby Twist = DESKTOP power (ball vape)
- Nice Dreamz = Fogger for concentrates
- Cub = CLEANING tool (use WITH Core or Nice Dreamz, NEVER alone)

⚠️ CRITICAL EMAIL RULE ⚠️
The support email is: matt@ineedhemp.com
CORRECT: ineedhemp.com (ONE 'e' in "ineed")
WRONG: ineedheemp.com (DO NOT ADD EXTRA 'e')
WRONG: ineedhemps.com
ONLY USE: matt@ineedhemp.com

OTHER RULES:
- Keep responses SHORT and focused
- Format links: **[Product Name](URL)**"""

    if intent == "support":
        if any(word in query.lower() for word in ["return", "refund", "broken", "damaged", "wrong"]):
            return base + "\n\n🚨 CRITICAL: Email matt@ineedhemp.com (spell: i-n-e-e-d-h-e-m-p) with order# + photos."
        else:
            return base + "\n\nProvide 2-3 troubleshooting steps, then suggest emailing matt@ineedhemp.com if needed."
    
    elif intent == "shopping" or any(word in query.lower() for word in ["beginner", "recommend", "should i"]):
        return base + "\n\nRecommend 1-2 products MAX. Beginners→Core Deluxe. Flavor→V5 XL."
    
    elif intent == "product_info" and products:
        prod_text = "\n".join([f"- {p['name']}: {p.get('price_display', 'N/A')}" for p in products[:2]])
        return base + f"\n\nRELEVANT:\n{prod_text}\n\nDescribe briefly (2-3 sentences)."
    
    elif intent == "pricing" and products:
        prod_text = "\n".join([f"- {p['name']}: {p.get('price_display', 'See site')}" for p in products[:2]])
        return base + f"\n\nPRICES:\n{prod_text}\n\nList price + link only."
    
    elif intent == "comparison":
        return base + "\n\nCompare in 3-4 bullet points: flavor, ease, portability, price."
    
    elif intent == "tech_specs":
        return base + "\n\nGive specific temps/watts/settings. No generic advice."
    
    else:
        return base

def fix_response_typos(response: str) -> str:
    """Post-processing: Fix email typos and other issues"""
    
    # Fix all email typos
    response = re.sub(r'matt@ineedheemp\.com', 'matt@ineedhemp.com', response, flags=re.IGNORECASE)
    response = re.sub(r'matt@ineed+h+e+m+p\.com', 'matt@ineedhemp.com', response, flags=re.IGNORECASE)
    response = re.sub(r'ineedheemp\.com', 'ineedhemp.com', response, flags=re.IGNORECASE)
    
    # Fix Cub descriptions
    if 'cub' in response.lower():
        # If mentions Cub but doesn't say it's used WITH something, clarify
        if 'cleaning' in response.lower() and 'with' not in response.lower() and 'alone' not in response.lower():
            response = response.replace('cleaning tool', 'cleaning tool (use with Core or Nice Dreamz)')
    
    return response

def generate_response_with_mistral(user_message, intent, products, session_id):
    """Generate response with Mistral + aggressive post-processing"""
    
    try:
        system_prompt = build_system_prompt(intent, products, user_message)
        history = memory.get_history(session_id)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        for turn in history[-2:]:
            messages.append({"role": "user", "content": turn['user']})
            messages.append({"role": "assistant", "content": turn['bot'][:150]})
        
        messages.append({"role": "user", "content": user_message})
        
        response = ollama.chat(
            model='mistral',
            messages=messages,
            options={
                'temperature': 0.7,
                'num_predict': 250,
                'top_p': 0.9
            }
        )
        
        bot_response = response['message']['content'].strip()
        
        # AGGRESSIVE FIX: Post-process to catch typos
        bot_response = fix_response_typos(bot_response)
        
        return bot_response
        
    except Exception as e:
        print(f"❌ Mistral error: {e}")
        return "I can help with Divine Tribe products! V5 XL (flavor), Core Deluxe (easy), Ruby Twist (power). What interests you?"

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    has_history = len(memory.get_history(session_id)) > 0
    intent_data = classifier.classify(user_message, has_history)
    intent = intent_data['intent']
    products = database.search(user_message, max_results=5)
    
    bot_response = generate_response_with_mistral(user_message, intent, products, session_id)
    memory.add_exchange(session_id, user_message, bot_response, intent)
    
    logger.log_conversation(
        session_id=session_id,
        user_query=user_message,
        bot_response=bot_response,
        products_shown=[p['name'] for p in products[:3]] if products else [],
        intent=intent,
        confidence=intent_data['confidence']
    )
    
    return jsonify({'response': bot_response, 'status': 'success', 'intent': intent, 'session_id': session_id})

@app.route('/')
def home():
    return "<h1>🤖 Divine Tribe Chatbot - Mistral AI v3.2 (Aggressive Fixes)</h1>"

@app.route('/generate_image', methods=['POST', 'OPTIONS'])
def generate_image():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        data = request.json
        prompt = data.get('prompt', '')
        from modules.image_generator import ImageGenerator
        gen = ImageGenerator()
        if not gen.check_comfyui_running():
            return jsonify({'status': 'error', 'message': 'Image generator offline'})
        result = gen.generate_for_chatbot(prompt)
        if result['has_image']:
            return jsonify({'status': 'success', 'image_data': result['image_data']})
        else:
            return jsonify({'status': 'error', 'message': 'Generation failed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/health', methods=['GET'])
def health():
    try:
        ollama_status = "connected"
        try:
            ollama.list()
        except:
            ollama_status = "offline"
        return jsonify({'status': 'healthy', 'products_loaded': len(database.products), 'ollama': ollama_status, 'model': 'mistral', 'version': '3.2-aggressive-fixes'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 DIVINE TRIBE CHATBOT - MISTRAL AI")
    print("="*70)
    print("✅ Aggressive email typo correction")
    print("✅ Fixed Cub description")
    print("✅ Shorter responses (250 tokens)")
    print("✅ Post-processing enabled")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
