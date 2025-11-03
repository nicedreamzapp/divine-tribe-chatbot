#!/usr/bin/env python3
"""
Divine Tribe Chatbot - WITH HUMAN-IN-THE-LOOP via Telegram
Customer never knows if it's human or bot - seamless experience!
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import json
import os
from modules.response_generator import ResponseGenerator
from modules.conversation import ConversationManager
from modules.conversation_logger import ConversationLogger
from telegram_handler import TelegramHandler, is_human_mode_active
import asyncio
import nest_asyncio
nest_asyncio.apply()
import random
import re
from datetime import datetime
import time
import glob

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.secret_key = 'divine_tribe_ollama_2025'

# Create directory for human responses
os.makedirs('human_responses', exist_ok=True)

print("Loading product catalog...")
with open('complete_products_full.json', 'r') as f:
    PRODUCTS = json.load(f)
print(f"✔ Loaded {len(PRODUCTS)} products")

print("Loading smart modules...")
response_gen = ResponseGenerator('complete_products_full.json')
conversation_mgr = ConversationManager()
conversation_logger = ConversationLogger()
telegram_handler = TelegramHandler()
print("✔ Smart modules ready")
print("✔ RLHF conversation logging enabled")
print("✔ Telegram human-in-the-loop ready")

print("✔ Using Ollama with Mistral model")

HUMOR_TEMPLATES = [
    "😄 {topic}? That's outside my wheelhouse! But speaking of amazing experiences...",
    "🤔 Interesting! But you know what I *really* know about?",
]

# Track discount code mentions per session
discount_code_mentioned = {}

def format_product_names_bold(text):
    """Format product names: bold + underlined + link embedded"""
    text = re.sub(
        r'\[([^\]]+)\]\((https?://[^)]+)\)',
        r'<a href="\2" target="_blank" style="font-weight:700;text-decoration:underline;color:#10b981">\1</a>',
        text
    )
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    return text

def remove_duplicate_discount_code(response: str, session_id: str) -> str:
    """Remove discount code from response if already mentioned in this session"""
    if session_id in discount_code_mentioned and discount_code_mentioned[session_id]:
        response = re.sub(r'[Uu]se\s+(?:code\s+)?["\']?thankyou10["\']?\s+for\s+\d+%\s+off[^.!]*[.!]?', '', response)
        response = re.sub(r'[Dd]on\'t\s+forget\s+to\s+use\s+(?:the\s+)?(?:our\s+)?discount\s+code\s+["\']?thankyou10["\']?[^.!]*[.!]?', '', response)
        response = re.sub(r'[Cc]ode\s+["\']?thankyou10["\']?\s+(?:saves|for)[^.!]*[.!]?', '', response)
        response = re.sub(r'[Rr]emember\s+to\s+use\s+(?:code\s+)?["\']?thankyou10["\']?[^.!]*[.!]?', '', response)
        response = re.sub(r'\n\n+', '\n\n', response).strip()
    else:
        if 'thankyou10' in response.lower():
            discount_code_mentioned[session_id] = True
    return response

def generate_bot_response(user_message: str, session_id: str = 'default') -> str:
    """Original bot logic - used when human mode is OFF"""
    context = response_gen.generate_context(user_message)
    classification = context['classification']
    has_products = len(context.get('products', [])) > 0
    
    if classification['is_off_topic'] and not has_products:
        humor = random.choice(HUMOR_TEMPLATES).format(topic=user_message[:40])
        pivot = "the Core 2.0 Deluxe! Code thankyou10 for 10% off! ✨"
        response = humor + " " + pivot
        discount_code_mentioned[session_id] = True
        
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
        quick_response = remove_duplicate_discount_code(quick_response, session_id)
        conversation_mgr.add_exchange(session_id, user_message, quick_response)
        
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
    
    response = ollama.chat(
        model='mistral',
        messages=messages,
        options={'temperature': 0.7, 'top_p': 0.9, 'num_predict': 400}
    )
    
    cleaned_response = response['message']['content'].strip()
    cleaned_response = remove_duplicate_discount_code(cleaned_response, session_id)
    formatted_response = format_product_names_bold(cleaned_response)
    
    conversation_mgr.add_exchange(session_id, user_message, cleaned_response)
    
    conversation_logger.log_conversation(
        session_id=session_id,
        user_query=user_message,
        bot_response=cleaned_response,
        products_shown=context.get('products', []),
        intent=classification['intent'],
        confidence=classification['confidence']
    )
    
    return formatted_response

async def send_to_human(user_message: str, session_id: str) -> str:
    """Send question to you via Telegram"""
    await telegram_handler.send_alert(user_message, session_id)
    return "Let me help you with that! 🤔 One moment..."

@app.route('/')
def home():
    human_status = "ON ✅" if is_human_mode_active() else "OFF ❌"
    return f"""
    <h1>✅ Divine Tribe Chatbot - Human-in-the-Loop</h1>
    <p>🚀 Mistral 7B via Ollama</p>
    <p>👤 Human Mode: {human_status}</p>
    <p>📱 Telegram notifications enabled</p>
    <p>🎭 Customer never knows if human or bot!</p>
    """

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            response = jsonify({'error': 'No message provided'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        if is_human_mode_active():
            bot_response = asyncio.run(send_to_human(user_message, session_id))
        else:
            bot_response = generate_bot_response(user_message, session_id)
        
        response = jsonify({'response': bot_response, 'status': 'success', 'session_id': session_id})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        response = jsonify({'error': str(e), 'status': 'error'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/get_human_response', methods=['GET', 'OPTIONS'])
def get_human_response():
    """Check if human has replied to this session"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    try:
        session_id = request.args.get('session_id')
        files = glob.glob(f'human_responses/{session_id}*.json')
        
        if files:
            with open(files[0], 'r') as f:
                response_data = json.load(f)
            
            os.remove(files[0])
            
            result = jsonify({
                'has_response': True,
                'response': response_data['reply']
            })
            result.headers.add('Access-Control-Allow-Origin', '*')
            return result
        
        result = jsonify({'has_response': False})
        result.headers.add('Access-Control-Allow-Origin', '*')
        return result
            
    except Exception as e:
        print(f"Error checking human response: {str(e)}")
        result = jsonify({'has_response': False})
        result.headers.add('Access-Control-Allow-Origin', '*')
        return result

@app.route('/human_response', methods=['POST'])
def human_response():
    """Endpoint for telegram_bot_listener to send your replies back"""
    try:
        data = request.json
        session_id = data.get('session_id')
        your_reply = data.get('reply')
        customer_query = data.get('query')
        
        formatted_reply = format_product_names_bold(your_reply)
        
        response_file = f"human_responses/{session_id}.json"
        with open(response_file, 'w') as f:
            json.dump({
                'reply': formatted_reply,
                'timestamp': datetime.now().isoformat()
            }, f)
        
        conversation_logger.log_conversation(
            session_id=session_id,
            user_query=customer_query,
            bot_response=your_reply,
            products_shown=[],
            intent="human_response",
            confidence=1.0
        )
        
        conversation_mgr.add_exchange(session_id, customer_query, your_reply)
        
        print(f"✅ Human response saved for session {session_id}")
        print(f"   Q: {customer_query}")
        print(f"   A: {your_reply}")
        
        return jsonify({'status': 'success', 'message': 'Response saved and ready for customer'})
    except Exception as e:
        print(f"❌ Error saving human response: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
        
        result = gen.generate_for_chatbot(prompt)
        
        if result['has_image']:
            response = jsonify({'status': 'success', 'image_data': result['image_data']})
        else:
            response = jsonify({'status': 'error', 'message': 'Generation failed'})
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"Image generation error: {str(e)}")
        response = jsonify({'status': 'error', 'message': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

if __name__ == '__main__':
    print("\n" + "=" * 90)
    print("DIVINE TRIBE CHATBOT - HUMAN-IN-THE-LOOP MODE")
    print("=" * 90)
    print("✔ Mistral 7B (automated mode)")
    print("✔ Telegram integration (human mode)")
    print("✔ Image generation ready")
    print("✔ Toggle with /toggle command in Telegram")
    print("✔ Customer never knows if human or bot!")
    print("✔ Polling enabled - customer sees your replies in real-time!")
    print("✔ RLHF conversation logging enabled")
    print("=" * 90 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
