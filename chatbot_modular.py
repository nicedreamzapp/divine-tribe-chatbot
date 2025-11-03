#!/usr/bin/env python3
"""
Divine Tribe Chatbot - FIXED VERSION
- Proper intent detection
- No repetitive responses  
- Correct URL handling
- Context awareness
- Image generation support
- NOW USING ORGANIZED PRODUCTS
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from modules.enhanced_classifier import EnhancedQueryClassifier
from modules.smart_responder import SmartResponder
from modules.product_database import ProductDatabase
from modules.conversation_memory import ConversationMemory
from modules.conversation_logger import ConversationLogger

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize components with ORGANIZED products
classifier = EnhancedQueryClassifier()
responder = SmartResponder('products_organized.json')  # CHANGED TO USE ORGANIZED JSON
database = ProductDatabase('products_organized.json')  # ALREADY CORRECT
memory = ConversationMemory(max_history=10)
logger = ConversationLogger()

print("✅ Fixed chatbot ready - No more repetitive responses!")
print("📦 Using organized product database with hierarchy")

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    # Check conversation history
    has_history = len(memory.get_history(session_id)) > 0
    
    # Classify intent properly
    intent_data = classifier.classify(user_message, has_history)
    
    # Get context from memory
    context = {
        'last_product': memory.get_last_user_message(session_id),
        'history': memory.get_history(session_id, max_turns=2)
    }
    
    # Generate appropriate response
    bot_response = responder.generate_response(
        user_message,
        intent_data,
        session_id,
        context
    )
    
    # Save to memory
    memory.add_exchange(session_id, user_message, bot_response, intent_data['intent'])
    
    # Log conversation
    logger.log_conversation(
        session_id=session_id,
        user_query=user_message,
        bot_response=bot_response,
        products_shown=[],
        intent=intent_data['intent'],
        confidence=intent_data['confidence']
    )
    
    return jsonify({
        'response': bot_response,
        'status': 'success',
        'intent': intent_data['intent'],
        'session_id': session_id
    })

@app.route('/')
def home():
    return """
    <h1>Divine Tribe Chatbot - FIXED with Organized Products</h1>
    <p>✅ Proper intent detection</p>
    <p>✅ No repetitive responses</p>
    <p>✅ Correct URL handling</p>
    <p>✅ Context awareness</p>
    <p>✅ AI Image Generation</p>
    <p>✅ Hierarchical product organization</p>
    <p>📦 Main products prioritized</p>
    <p>🔧 Replacement parts hidden unless requested</p>
    """

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
        print(f"Image generation error: {str(e)}")
        response = jsonify({'status': 'error', 'message': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Check if products loaded
        product_count = len(database.organized_data.get('product_index', {}))
        return jsonify({
            'status': 'healthy',
            'products_loaded': product_count,
            'version': '2.0',
            'using_organized': True
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
