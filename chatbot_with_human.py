#!/usr/bin/env python3
"""
Divine Tribe Chatbot - 100% HUMAN MODE
NO AI - Every message goes to YOU via Telegram
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from modules.conversation_memory import ConversationMemory
from modules.conversation_logger import ConversationLogger
from telegram_handler import TelegramHandler, is_human_mode_active
import asyncio
import nest_asyncio
nest_asyncio.apply()
from datetime import datetime
import glob

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

os.makedirs('human_responses', exist_ok=True)

memory = ConversationMemory(max_history=10)
logger = ConversationLogger()
telegram_handler = TelegramHandler()

print("✅ 100% HUMAN MODE - No AI")
print("📱 All messages go to Telegram")
print("🧠 Logging enabled for training")

async def send_to_human(user_message: str, session_id: str) -> str:
    await telegram_handler.send_alert(user_message, session_id)
    return "Let me help you with that! 🤔 One moment..."

@app.route('/')
def home():
    human_status = "ON ✅" if is_human_mode_active() else "OFF ❌"
    return f"<h1>👤 Divine Tribe - 100% Human Mode</h1><p>Status: {human_status}</p>"

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        bot_response = asyncio.run(send_to_human(user_message, session_id))
        
        return jsonify({'response': bot_response, 'status': 'success', 'session_id': session_id})
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/get_human_response', methods=['GET', 'OPTIONS'])
def get_human_response():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        session_id = request.args.get('session_id')
        files = glob.glob(f'human_responses/{session_id}*.json')
        
        if files:
            with open(files[0], 'r') as f:
                response_data = json.load(f)
            os.remove(files[0])
            return jsonify({'has_response': True, 'response': response_data['reply']})
        
        return jsonify({'has_response': False})
    except Exception as e:
        return jsonify({'has_response': False})

@app.route('/human_response', methods=['POST'])
def human_response():
    try:
        data = request.json
        session_id = data.get('session_id')
        your_reply = data.get('reply')
        customer_query = data.get('query')
        
        response_file = f"human_responses/{session_id}.json"
        with open(response_file, 'w') as f:
            json.dump({'reply': your_reply, 'timestamp': datetime.now().isoformat()}, f)
        
        logger.log_conversation(
            session_id=session_id,
            user_query=customer_query,
            bot_response=your_reply,
            products_shown=[],
            intent="human_response",
            confidence=1.0
        )
        
        memory.add_exchange(session_id, customer_query, your_reply, "human_response")
        
        print(f"✅ Your response logged:")
        print(f"   Q: {customer_query}")
        print(f"   A: {your_reply}")
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate_image', methods=['POST', 'OPTIONS'])
def generate_image():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        data = request.json
        prompt = data.get('prompt', '')
        from modules.image_generator import ImageGenerator
        gen = ImageGenerator()
        result = gen.generate_for_chatbot(prompt)
        if result['has_image']:
            return jsonify({'status': 'success', 'image_data': result['image_data']})
        else:
            return jsonify({'status': 'error', 'message': 'Generation failed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("👤 DIVINE TRIBE - 100% HUMAN MODE")
    print("="*70)
    print("✅ NO AI - Every message goes to YOU")
    print("✅ Telegram alerts for all questions")
    print("✅ Your responses logged for AI training")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
