#!/usr/bin/env python3
"""
Divine Tribe Chatbot - Ollama with Better Formatting + RLHF Logging
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import json
from modules.response_generator import ResponseGenerator
from modules.conversation import ConversationManager
from modules.conversation_logger import ConversationLogger
import random
import re

app = Flask(__name__)
app.secret_key = 'divine_tribe_ollama_2025'
CORS(app, resources={r"/chat": {"origins": "*"}}, supports_credentials=True)

print("Loading product catalog...")
with open('complete_products_full.json', 'r') as f:
    PRODUCTS = json.load(f)
print(f"✓ Loaded {len(PRODUCTS)} products")

print("Loading smart modules...")
response_gen = ResponseGenerator('complete_products_full.json')
conversation_mgr = ConversationManager()
conversation_logger = ConversationLogger()  # NEW: RLHF logging
print("✓ Smart modules ready")
print("✓ RLHF conversation logging enabled")

print("✓ Using Ollama with Mistral model")

HUMOR_TEMPLATES = [
    "😄 {topic}? That's outside my wheelhouse! But speaking of amazing experiences...",
    "🤔 Interesting! But you know what I *really* know about?",
]

def format_product_names_bold(text):
    """Format product names: bold + underlined + link embedded"""
    # Convert [Product Name](url) markdown to bold, underlined link
    text = re.sub(
        r'\[([^\]]+)\]\((https?://[^)]+)\)',
        r'<a href="\2" target="_blank" style="font-weight:700;text-decoration:underline;color:#10b981">\1</a>',
        text
    )
    
    # Remove any other ** markdown (we don't want anything else bold)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    return text

def generate_response(user_message: str, session_id: str = 'default') -> str:
    context = response_gen.generate_context(user_message)
    classification = context['classification']
    
    if classification['is_off_topic']:
        humor = random.choice(HUMOR_TEMPLATES).format(topic=user_message[:40])
        pivot = "the Core 2.0 Deluxe! Code thankyou10 for 10% off! ✨"
        response = humor + " " + pivot
        
        # LOG THIS CONVERSATION
        conversation_logger.log_conversation(
            session_id=session_id,
            user_query=user_message,
            bot_response=response,
            products_shown=[],
            intent=classification['intent'],
            confidence=classification['confidence']
        )
        
        return response
    
    quick_response = response_gen.get_quick_response(user_message)
    if quick_response:
        conversation_mgr.add_exchange(session_id, user_message, quick_response)
        
        # LOG THIS CONVERSATION
        conversation_logger.log_conversation(
            session_id=session_id,
            user_query=user_message,
            bot_response=quick_response,
            products_shown=[],
            intent=classification['intent'],
            confidence=classification['confidence']
        )
        
        return format_product_names_bold(quick_response)
    
    history = conversation_mgr.get_context(session_id, max_turns=2)
    
    messages = [{"role": "system", "content": context['system_prompt']}]
    
    if history:
        for turn in history:
            messages.append({"role": "user", "content": turn['user']})
            messages.append({"role": "assistant", "content": turn['assistant'][:150]})
    
    messages.append({"role": "user", "content": user_message})
    
    # Call Ollama with options for faster response
    response = ollama.chat(
        model='mistral',
        messages=messages,
        options={
            'temperature': 0.7,
            'top_p': 0.9,
            'num_predict': 400
        }
    )
    
    cleaned_response = response['message']['content'].strip()
    formatted_response = format_product_names_bold(cleaned_response)
    
    conversation_mgr.add_exchange(session_id, user_message, cleaned_response)
    
    # LOG THIS CONVERSATION WITH PRODUCTS
    conversation_logger.log_conversation(
        session_id=session_id,
        user_query=user_message,
        bot_response=cleaned_response,
        products_shown=context.get('products', []),
        intent=classification['intent'],
        confidence=classification['confidence']
    )
    
    return formatted_response

@app.route('/')
def home():
    return """
    <h1>✅ Divine Tribe Chatbot - Ollama Powered</h1>
    <p>🚀 Mistral 7B via Ollama</p>
    <p>✅ V5 vs Cub logic FIXED</p>
    <p>🧠 Smart modules</p>
    <p>📊 RLHF logging enabled</p>
    """

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        bot_response = generate_response(user_message, session_id)
        return jsonify({'response': bot_response, 'status': 'success', 'session_id': session_id})
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

if __name__ == '__main__':
    print("\n" + "=" * 90)
    print("DIVINE TRIBE CHATBOT - OLLAMA POWERED + RLHF")
    print("=" * 90)
    print("✓ Mistral 7B (fast & accurate)")
    print("✓ Bold formatting for products")
    print("✓ Optimized for speed")
    print("✓ RLHF conversation logging to conversation_logs/")
    print("=" * 90 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
