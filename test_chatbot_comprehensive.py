#!/usr/bin/env python3
"""
Comprehensive Chatbot Test Suite
Tests 100 real customer scenarios including returns, support, and products
"""

import requests
import json
import time
from datetime import datetime

# Test scenarios covering all customer needs
TEST_SCENARIOS = [
    # Product inquiries (20)
    "show me the V5",
    "tell me about the Core",
    "what's the Core Deluxe?",
    "I need a vaporizer",
    "Ruby Twist",
    "show me controllers",
    "what controllers work with Ruby Twist?",
    "Nice Dreamz Fogger",
    "Lightning Pen",
    "what's the Cub for?",
    "Hubble Bubble",
    "do you have glass attachments?",
    "what's your best product?",
    "beginner friendly options?",
    "what's best for flavor?",
    "portable vaporizers",
    "desktop vaporizers", 
    "cartridge batteries",
    "510 thread",
    "cleaning accessories",
    
    # Support & Returns (30)
    "I want to return my product",
    "how do I return this?",
    "my coil won't work",
    "my heater is broken",
    "the glass broke",
    "it's not heating up",
    "my Core won't turn on",
    "the battery died",
    "it tastes burnt",
    "how do I clean this?",
    "my V5 stopped working",
    "warranty information",
    "how long is the warranty?",
    "my order never arrived",
    "wrong item shipped",
    "missing parts in my order",
    "defective product",
    "it's leaking",
    "the button is stuck",
    "error message on screen",
    "won't charge",
    "auto shutoff not working",
    "temperature issues",
    "can't connect the parts",
    "o-rings are damaged",
    "where's my tracking?",
    "how to use the V5?",
    "Core instructions",
    "setup help",
    "troubleshooting guide",
    
    # Pricing & Shopping (20)
    "how much is the V5?",
    "Core Deluxe price?",
    "do you have discounts?",
    "any sales?",
    "coupon codes?",
    "bulk pricing?",
    "payment options",
    "do you take crypto?",
    "shipping costs?",
    "international shipping?",
    "how long for delivery?",
    "express shipping?",
    "in stock?",
    "when will it be back?",
    "pre-orders available?",
    "bundle deals?",
    "starter kits?",
    "what comes with it?",
    "accessories included?",
    "compare V5 and Core",
    
    # Technical Questions (15)
    "what temperature for concentrates?",
    "TCR settings?",
    "wattage mode or temp control?",
    "compatible mods?",
    "resistance reading?",
    "how to rebuild coils?",
    "wire gauge for V5?",
    "battery recommendations?",
    "firmware updates?",
    "Arctic Fox compatible?",
    "DNA mod settings?",
    "ohm reading too high",
    "what's autofire?",
    "session mode?",
    "how many watts?",
    
    # General & Misc (15)
    "hello",
    "hi there",
    "are you a bot?",
    "contact information",
    "where are you located?",
    "business hours?",
    "about Divine Tribe",
    "who is Matt?",
    "Reddit community?",
    "Discord server?",
    "YouTube videos?",
    "user manual?",
    "safety information",
    "age requirements?",
    "thank you"
]

def test_chatbot():
    """Run all test scenarios"""
    base_url = "http://localhost:5001/chat"
    results = []
    
    print(f"🧪 Testing {len(TEST_SCENARIOS)} scenarios...")
    print("=" * 60)
    
    for i, query in enumerate(TEST_SCENARIOS, 1):
        try:
            response = requests.post(base_url, json={
                "message": query,
                "session_id": f"test_{i}"
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "query": query,
                    "intent": data.get("intent", "unknown"),
                    "response": data.get("response", "No response"),
                    "status": "✅ OK"
                }
            else:
                result = {
                    "query": query,
                    "intent": "error",
                    "response": f"HTTP {response.status_code}",
                    "status": "❌ ERROR"
                }
        except Exception as e:
            result = {
                "query": query,
                "intent": "error", 
                "response": str(e),
                "status": "❌ FAILED"
            }
        
        results.append(result)
        
        # Print progress
        print(f"{i:3d}. {query[:40]:<40} {result['status']}")
        
        # Small delay to not overwhelm
        time.sleep(0.1)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("=" * 60)
    print(f"✅ Test complete! Results saved to: {output_file}")
    
    # Generate summary
    intents = {}
    for r in results:
        intent = r['intent']
        intents[intent] = intents.get(intent, 0) + 1
    
    print("\n📊 Intent Distribution:")
    for intent, count in sorted(intents.items(), key=lambda x: x[1], reverse=True):
        print(f"  {intent}: {count}")
    
    # Check for return/support handling
    print("\n🔧 Support Query Analysis:")
    support_queries = [r for r in results if any(word in r['query'].lower() 
                      for word in ['return', 'broken', 'warranty', 'help', 'fix'])]
    
    for sq in support_queries[:5]:  # Show first 5
        print(f"\nQ: {sq['query']}")
        print(f"A: {sq['response'][:100]}...")
    
    return results

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║   DIVINE TRIBE CHATBOT TEST SUITE         ║
    ║   100 Customer Scenarios                  ║
    ╚════════════════════════════════════════════╝
    """)
    
    print("\n⚠️  Make sure chatbot is running on port 5001!")
    input("Press Enter to start testing...")
    
    results = test_chatbot()
