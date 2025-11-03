#!/usr/bin/env python3
"""
Divine Tribe Chatbot - 100 Question Test Suite
Tests all major functionality: products, support, technical, returns, image generation
Run this from terminal to test your chatbot's responses
"""

import requests
import json
import time
from datetime import datetime

# Your chatbot endpoint
CHATBOT_URL = "http://localhost:5001/chat"

# 100 Test Questions organized by category
TEST_QUESTIONS = [
    # ==================== PRODUCT INQUIRIES (30 questions) ====================
    # V5 XL Questions (Main Product)
    "What is the V5 XL?",
    "tell me about the v5",
    "how much is the V5 XL?",
    "v5 xl specs",
    "what makes v5 xl good for flavor?",
    "v5 vs v5 xl difference",
    "show me the v5 xl",
    "i want to buy a v5",
    "what coil does v5 xl use?",
    "v5 xl ceramic cup",
    
    # Core Questions (Main Product)
    "what is the core?",
    "core deluxe features",
    "how much is the core?",
    "core 2.0 vs core deluxe",
    "which core should i buy?",
    "core erig",
    "portable core",
    "core with recycler top",
    "core heat settings",
    "core vs v5",
    
    # Nice Dreamz Questions
    "what is nice dreamz?",
    "nice dreams fogger",
    "how does nice dreamz work?",
    "nice dreamz with core",
    "nice dreamz cleaning",
    
    # Ruby Twist Questions
    "what is ruby twist?",
    "ruby twist ball vape",
    "ruby twist controller",
    "wireless ruby twist",
    "how to use ruby twist",
    
    # Cub Questions
    "what is the cub?",
    "cub cleaner",
    "do i need the cub?",
    "cub with core",
    
    # ==================== ACCESSORIES & PARTS (15 questions) ====================
    "replacement heater for v5",
    "sic cup",
    "titanium cup",
    "carb cap",
    "glass adapter",
    "510 extension cable",
    "do you have batteries?",
    "what mod should i use?",
    "pico mod",
    "arctic fox firmware",
    "tc mode settings",
    "o-rings for v5",
    "quartz cup",
    "need a new coil",
    "top flow adapter",
    
    # ==================== BEGINNER/RECOMMENDATION (10 questions) ====================
    "what should i buy as a beginner?",
    "best product for flavor?",
    "most portable option?",
    "easiest to use?",
    "what's your most popular product?",
    "i'm new to vaping",
    "first time buyer",
    "what do you recommend?",
    "best starter kit?",
    "complete setup",
    
    # ==================== SUPPORT & RETURNS (15 questions) ====================
    "my atomizer is broken",
    "product arrived damaged",
    "need to return this",
    "how do i get a refund?",
    "warranty information",
    "my v5 won't fire",
    "getting no vapor",
    "tastes burnt",
    "leaking",
    "won't heat up",
    "coil not working",
    "broken glass",
    "missing parts",
    "wrong item shipped",
    "i need help",
    
    # ==================== TECHNICAL TROUBLESHOOTING (15 questions) ====================
    "how to set temperature?",
    "what wattage for v5?",
    "tcr settings",
    "resistance reading wrong",
    "mod says no atomizer",
    "how to lock resistance?",
    "arctic fox setup",
    "temp control not working",
    "coil reading too high",
    "short circuit error",
    "how to clean v5?",
    "how to replace coil?",
    "how to install cup?",
    "maintenance tips",
    "how often to replace",
    
    # ==================== COMPARISON QUESTIONS (8 questions) ====================
    "v5 xl vs core deluxe",
    "sic vs titanium cup",
    "which is better for flavor?",
    "most durable option?",
    "cheapest product?",
    "premium option?",
    "desktop vs portable",
    "ruby twist vs v5",
    
    # ==================== IMAGE GENERATION REQUESTS (5 questions) ====================
    "create an image of the v5 xl",
    "show me a picture of divine tribe logo",
    "generate futuristic vaporizer",
    "make an image of core with purple smoke",
    "create divine tribe artwork",
    
    # ==================== MISC/EDGE CASES (12 questions) ====================
    "hello",
    "hi there",
    "thanks",
    "goodbye",
    "tell me about elephants",
    "what's 2+2?",
    "who is the president?",
    "asdf",
    "...",
    "help",
    "???",
    "website"
]

def test_single_question(question, session_id="test_session"):
    """Send a single question to the chatbot and get response"""
    try:
        payload = {
            "message": question,
            "session_id": session_id
        }
        
        response = requests.post(
            CHATBOT_URL,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data.get("response", ""),
                "intent": data.get("intent", "unknown"),
                "status_code": 200
            }
        else:
            return {
                "success": False,
                "response": f"HTTP {response.status_code}",
                "intent": "error",
                "status_code": response.status_code
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "response": "❌ Connection failed - Is chatbot running on port 5001?",
            "intent": "error",
            "status_code": 0
        }
    except Exception as e:
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            "intent": "error",
            "status_code": 0
        }

def run_test_suite():
    """Run all 100 test questions"""
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     DIVINE TRIBE CHATBOT - 100 QUESTION TEST SUITE       ║
    ║                                                           ║
    ║  Testing: Products, Support, Technical, Returns, Images  ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    print(f"\n🔗 Testing endpoint: {CHATBOT_URL}")
    print(f"📋 Total questions: {len(TEST_QUESTIONS)}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # First, check if chatbot is responsive
    print("🔍 Checking chatbot connection...")
    test_result = test_single_question("hello")
    
    if not test_result["success"]:
        print("\n❌ CHATBOT NOT RESPONDING!")
        print(f"Error: {test_result['response']}")
        print("\nMake sure your chatbot is running:")
        print("  cd ~/Desktop/dataset\\ for\\ Tribe\\ Chatbot/")
        print("  python3 chatbot_modular.py")
        return None
    
    print("✅ Chatbot is responsive!\n")
    print("=" * 70)
    
    results = []
    session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    for idx, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{idx:3d}/100] Testing: {question}")
        
        result = test_single_question(question, session_id)
        
        results.append({
            "question_number": idx,
            "question": question,
            "response": result["response"],
            "intent": result["intent"],
            "success": result["success"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Print summary
        if result["success"]:
            response_preview = result["response"][:80] + "..." if len(result["response"]) > 80 else result["response"]
            print(f"   Intent: {result['intent']}")
            print(f"   Response: {response_preview}")
        else:
            print(f"   ❌ FAILED: {result['response']}")
        
        # Small delay to not overwhelm
        time.sleep(0.2)
    
    print("\n" + "=" * 70)
    return results

def analyze_results(results):
    """Analyze test results and generate report"""
    
    if not results:
        return
    
    print("\n\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                    TEST RESULTS ANALYSIS                  ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # Success rate
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    print(f"\n✅ Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    
    # Intent distribution
    intents = {}
    for r in results:
        intent = r["intent"]
        intents[intent] = intents.get(intent, 0) + 1
    
    print("\n📊 Intent Distribution:")
    for intent, count in sorted(intents.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * (count // 2)
        print(f"   {intent:20s} {count:3d} {bar}")
    
    # Check support handling
    support_keywords = ["return", "broken", "warranty", "damaged", "refund", "help", "wrong"]
    support_questions = [r for r in results if any(kw in r["question"].lower() for kw in support_keywords)]
    
    print(f"\n🔧 Support Questions Analysis ({len(support_questions)} questions):")
    email_mentioned = sum(1 for sq in support_questions if "matt@ineedhemp.com" in sq["response"].lower())
    print(f"   ✉️  Email routing: {email_mentioned}/{len(support_questions)}")
    
    # Check product recommendations
    product_keywords = ["v5", "core", "ruby", "nice dreamz", "cub"]
    product_questions = [r for r in results if any(kw in r["question"].lower() for kw in product_keywords)]
    
    print(f"\n📦 Product Questions Analysis ({len(product_questions)} questions):")
    has_link = sum(1 for pq in product_questions if "ineedhemp.com" in pq["response"])
    print(f"   🔗 Product links provided: {has_link}/{len(product_questions)}")
    
    # Check image generation
    image_questions = [r for r in results if "create" in r["question"].lower() or "generate" in r["question"].lower() or "image" in r["question"].lower()]
    
    if image_questions:
        print(f"\n🎨 Image Generation Requests ({len(image_questions)} questions):")
        for iq in image_questions:
            status = "✅" if "image" in iq["response"].lower() else "❌"
            print(f"   {status} {iq['question']}")
    
    # Problem areas
    print("\n⚠️  Potential Issues:")
    
    # Check for generic responses
    generic_responses = [r for r in results if len(r["response"]) < 50 and r["success"]]
    if generic_responses:
        print(f"   📝 {len(generic_responses)} responses seem too short")
    
    # Check for repeated responses
    response_counts = {}
    for r in results:
        resp = r["response"][:100]  # First 100 chars
        response_counts[resp] = response_counts.get(resp, 0) + 1
    
    repeated = [(resp, count) for resp, count in response_counts.items() if count > 3]
    if repeated:
        print(f"   🔁 {len(repeated)} responses repeated 4+ times")
        for resp, count in repeated[:3]:
            print(f"      '{resp[:60]}...' ({count}x)")
    
    # Failures
    failures = [r for r in results if not r["success"]]
    if failures:
        print(f"\n❌ Failed Questions ({len(failures)}):")
        for f in failures[:10]:  # Show first 10
            print(f"   • {f['question']}")
    
    return intents, support_questions, product_questions

def save_results(results):
    """Save results to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full results saved to: {filename}")
    
    # Also create a readable text report
    report_filename = f"test_report_{timestamp}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("DIVINE TRIBE CHATBOT TEST REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        for r in results:
            f.write(f"Question {r['question_number']}: {r['question']}\n")
            f.write(f"Intent: {r['intent']}\n")
            f.write(f"Response: {r['response']}\n")
            f.write("-" * 70 + "\n\n")
    
    print(f"📄 Readable report saved to: {report_filename}")

def main():
    """Main test execution"""
    
    # Run the test suite
    results = run_test_suite()
    
    if results:
        # Analyze results
        analyze_results(results)
        
        # Save to files
        save_results(results)
        
        print("\n✨ Testing complete!\n")
        print("Next steps:")
        print("  1. Review the generated reports")
        print("  2. Identify areas needing improvement")
        print("  3. Update chatbot modules as needed")
        print("  4. Re-run this test to verify fixes\n")
    
    else:
        print("\n⚠️  Test suite did not complete. Check chatbot status.\n")

if __name__ == "__main__":
    main()
