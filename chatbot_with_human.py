#!/usr/bin/env python3
"""
Divine Tribe Chatbot - 100% HUMAN MODE (FIXED)
NO AI - Every message goes to YOU via Telegram
✅ Fixed: Each question gets unique ID (no more response mixing!)
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
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

os.makedirs('human_responses', exist_ok=True)

memory = ConversationMemory(max_history=10)
logger = ConversationLogger()
telegram_handler = TelegramHandler()

print("✅ 100% HUMAN MODE - No AI")
print("📱 All messages go to Telegram")
print("🧠 Logging enabled for training")
print("🔧 Fixed: Unique message IDs prevent response mixing")

async def send_to_human(user_message: str, message_id: str) -> str:
    """Send question to Telegram with unique message ID"""
    await telegram_handler.send_alert(user_message, message_id)
    return "Let me help you with that! 🤔 One moment..."

@app.route('/')
def home():
    human_status = "ON ✅" if is_human_mode_active() else "OFF ❌"
    return f"<h1>👤 Divine Tribe - 100% Human Mode (FIXED)</h1><p>Status: {human_status}</p>"

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
        
        # ✅ FIX: Create UNIQUE message ID for this specific question
        message_id = f"{session_id}_{int(time.time() * 1000)}"
        
        bot_response = asyncio.run(send_to_human(user_message, message_id))
        
        # ✅ Return message_id so HTML can poll for the right response
        return jsonify({
            'response': bot_response,
            'status': 'success',
            'session_id': session_id,
            'message_id': message_id  # ← NEW!
        })
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/get_human_response', methods=['GET', 'OPTIONS'])
def get_human_response():
    """Poll for human response using unique message_id"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # ✅ FIX: Use message_id instead of session_id
        message_id = request.args.get('message_id')
        
        if not message_id:
            return jsonify({'has_response': False, 'error': 'No message_id provided'})
        
        # Look for response file with this specific message_id
        files = glob.glob(f'human_responses/{message_id}*.json')
        
        if files:
            with open(files[0], 'r') as f:
                response_data = json.load(f)
            
            # ✅ Delete file immediately after reading
            os.remove(files[0])
            print(f"✅ Delivered response for {message_id}")
            
            return jsonify({
                'has_response': True,
                'response': response_data['reply']
            })
        
        return jsonify({'has_response': False})
        
    except Exception as e:
        print(f"❌ Polling error: {str(e)}")
        return jsonify({'has_response': False, 'error': str(e)})

@app.route('/human_response', methods=['POST'])
def human_response():
    """Receive your Telegram reply and save it"""
    try:
        data = request.json
        message_id = data.get('session_id')  # Telegram sends as session_id
        your_reply = data.get('reply')
        customer_query = data.get('query')
        
        # ✅ Save with message_id (not session_id)
        response_file = f"human_responses/{message_id}.json"
        with open(response_file, 'w') as f:
            json.dump({
                'reply': your_reply,
                'timestamp': datetime.now().isoformat(),
                'message_id': message_id
            }, f)
        
        # Extract session_id from message_id for logging
        session_id = message_id.split('_')[0] if '_' in message_id else message_id
        
        logger.log_conversation(
            session_id=session_id,
            user_query=customer_query,
            bot_response=your_reply,
            products_shown=[],
            intent="human_response",
            confidence=1.0
        )
        
        memory.add_exchange(session_id, customer_query, your_reply, "human_response")
        
        print(f"✅ Your response saved:")
        print(f"   Message ID: {message_id}")
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
    print("👤 DIVINE TRIBE - 100% HUMAN MODE (FIXED)")
    print("="*70)
    print("✅ NO AI - Every message goes to YOU")
    print("✅ Telegram alerts for all questions")
    print("✅ Your responses logged for AI training")
    print("✅ FIXED: Unique message IDs prevent response mixing")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
