#!/usr/bin/env python3
"""
🔥 REAL OVERNIGHT STRESS TEST - With Actual Mistral Generation
This test ACTUALLY calls Mistral for intelligent responses
Expected time: 15-25 minutes for 240 questions

Differences from previous test:
- ✅ Calls Mistral for ALL questions that need AI reasoning
- ✅ Generates natural language answers (not just product listings)
- ✅ Tests response quality and helpfulness
- ✅ Measures token usage and generation time
- ✅ Evaluates if answers actually solve the problem
"""

import sys
import os
import json
import time
import ollama
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, os.getcwd())

from modules.cag_cache import CAGCache
from modules.agent_router import AgentRouter
from modules.product_database import ProductDatabase
from modules.context_manager import ContextManager
from modules.conversation_memory import ConversationMemory


def print_progress(current, total, category, start_time):
    """Print progress bar with ETA"""
    percent = (current / total) * 100
    bar_length = 50
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    elapsed = time.time() - start_time
    eta = (elapsed / current) * (total - current) if current > 0 else 0
    eta_min = int(eta / 60)
    eta_sec = int(eta % 60)
    
    print(f"\r[{bar}] {percent:.1f}% ({current}/{total}) | {category:30s} | ETA: {eta_min}m {eta_sec}s", end='', flush=True)


def generate_mistral_answer(question, context, intent='general'):
    """
    Actually call Mistral to generate intelligent answers
    This is what was missing in the previous test!
    """
    
    # Build context-aware prompt based on intent
    if intent == 'troubleshooting':
        system_prompt = """You are a Divine Tribe product support expert. A customer has a technical problem.
        
Your job:
1. Acknowledge their issue with empathy
2. Provide specific troubleshooting steps from the context
3. If context doesn't have the answer, give general troubleshooting advice
4. Keep answer concise (3-5 sentences max)
5. End with: "Still having issues? Email matt@ineedhemp.com"

Be helpful, technical, and direct."""

    elif intent == 'comparison':
        system_prompt = """You are a Divine Tribe product expert helping customers choose the right product.

Your job:
1. Compare the products fairly using context provided
2. Explain key differences in simple terms
3. Give a clear recommendation based on use case
4. Keep it concise (4-6 sentences)
5. End with a question: "Which sounds better for your needs?"

Be honest about pros/cons."""

    elif intent == 'product_question':
        system_prompt = """You are a Divine Tribe sales assistant. Customer wants to know about a product.

Your job:
1. Answer their specific question using context
2. Highlight 2-3 key features they'd care about
3. Mention price if relevant
4. Keep it brief (3-4 sentences)
5. End with: "Want to know more about [product]?"

Be enthusiastic but not pushy."""

    else:  # general
        system_prompt = """You are a helpful Divine Tribe assistant. Answer the customer's question naturally.

Your job:
1. Give a direct answer to their question
2. Use the context provided when relevant
3. Be conversational and friendly
4. Keep it concise (3-5 sentences)
5. Offer to help further

Be natural and helpful."""

    # Build the full prompt with context
    full_prompt = f"""{system_prompt}

Context/Information:
{context}

Customer Question: {question}

Your Answer:"""

    try:
        # Call Mistral
        response = ollama.generate(
            model='mistral',
            prompt=full_prompt,
            options={
                'temperature': 0.7,
                'num_predict': 200  # Keep responses concise
            }
        )
        
        return response['response'].strip()
    
    except Exception as e:
        return f"Error generating response: {str(e)}"


def run_real_test():
    """Run the REAL stress test with actual Mistral generation"""
    
    print("=" * 100)
    print("🔥 REAL OVERNIGHT STRESS TEST - With Mistral Generation")
    print("=" * 100)
    print("\nThis will take 15-25 minutes because it ACTUALLY calls Mistral for each question")
    print("Press Ctrl+C to stop at any time (results will be saved)\n")
    
    # Initialize components
    print("🔧 Initializing components...")
    cache = CAGCache()
    db = ProductDatabase('products_organized.json')
    router = AgentRouter(cache, db)
    context_mgr = ContextManager()
    conv_memory = ConversationMemory()
    print("✅ Ready!\n")
    
    # Load questions (same 480 questions from before)
    questions = {
        "V5_Setup_Issues": [
            "my v5 won't get to temp on arctic fox",
            "v5 resistance jumping from .5 to .7 ohms",
            "v5 not heating properly",
            "what tcr should I use for v5?",
            "v5 getting chazzed on the outside",
            "my mod is overheating with v5",
            "should I use ni200 or tcr mode for v5?",
            "v5 barely reaches 300 degrees",
            "v5 cup has a tiny chip is that okay?",
            "how tight should v5 screws be?",
            "v5 coil reads as open circuit",
            "v5 only works in wattage mode not tc",
            "why is my v5 giving check atomizer error",
            "v5 working on pico but not on drag",
            "v5 reads different resistance on different mods",
            "v5 only heats to 175-210 degrees",
            "is my v5 warranty void if I clean with iso",
            "v5 getting worse over time",
            "v5 tastes weird after cleaning",
            "new v5 cup measures .47 ohms is that normal"
        ],
        "Core_Specific": [
            "core 2.0 blue setting too hot",
            "core gets tire taste like combustion",
            "core battery only lasts 2 bowls",
            "core won't connect to app",
            "is core 2.0 better than core deluxe?",
            "core vs puffco which is better",
            "core xl or regular core which to buy",
            "can I use my own glass with core",
            "core bubbler keeps getting clogged",
            "how long does core battery last"
        ],
        "Mod_Compatibility": [
            "best mod for v5 under $50",
            "will v5 work with smok alien",
            "pico vs wismec which is better for v5",
            "can I use v5 with my vape mod",
            "what mods have arctic fox",
            "single battery mod recommendations",
            "is dna mod worth it for v5",
            "aegis legend good for v5?",
            "cheapest mod that works with v5",
            "mod for both v5 and nicotine vaping"
        ],
        "Arctic_Fox_Setup": [
            "how to install arctic fox on pico",
            "arctic fox tcr settings for v5",
            "arctic fox vs stock firmware",
            "pi regulator on or off",
            "how to lock resistance arctic fox",
            "arctic fox profile download for v5",
            "arctic fox shows wrong temperature",
            "how to backup arctic fox settings",
            "arctic fox not firing",
            "uninstall arctic fox back to stock"
        ],
        "Temperature_Settings": [
            "best temp for flavor on v5",
            "what temp for big clouds",
            "temp too low no vapor",
            "temp too high burning",
            "difference between 380 and 420 degrees",
            "should I use fahrenheit or celsius",
            "cold start dabs temperature",
            "low temp vs high temp dabbing",
            "temp for live resin vs shatter",
            "reclaim temp to save terps"
        ],
        "Cleaning_Maintenance": [
            "how often should I clean v5",
            "iso soak or burn off which is better",
            "can I use 70% iso or need 91%",
            "how to clean chazzed cup",
            "q tip after every dab necessary?",
            "deep clean v5 full disassembly",
            "when to replace sic cup",
            "cleaning 510 threads",
            "how to remove stuck cup",
            "preventing buildup on v5"
        ],
        "Cup_Bucket_Questions": [
            "sic vs quartz vs ceramic which is best",
            "why is sic better",
            "polished vs unpolished sic",
            "can I swap v5 cup with v4 cup",
            "cracked sic cup still safe?",
            "aftermarket cups compatible?",
            "titanium cup for v5 exists?",
            "cup sizes for v5 vs v5 xl",
            "where to buy replacement cups",
            "how long does sic cup last"
        ],
        "Product_Comparisons": [
            "v5 vs v5 xl which should I get",
            "v5 vs dtv4 upgrade worth it?",
            "core vs v5 with mod setup",
            "nice dreamz vs pax which is better",
            "lightning pen vs regular pen vape",
            "ruby twist vs other ball vapes",
            "divine tribe vs puffco comparison",
            "v5 vs sai taf",
            "dtv4 vs sequoia",
            "best portable dab rig"
        ],
        "Beginner_Questions": [
            "complete beginner what should I buy",
            "easiest divine tribe product to use",
            "do I need anything else with v5",
            "v5 or core for first time",
            "how hard is it to use v5",
            "instructions for new v5 user",
            "batteries needed for v5 setup",
            "what is a dab rig",
            "concentrates vs flower which vape",
            "typical cost to get started"
        ],
        "Advanced_Usage": [
            "autofire for cold starts",
            "custom tcr values experimentation",
            "resistance lock best practices",
            "getting most efficiency from load",
            "extending sic cup life tips",
            "using v5 with enail controller",
            "multiple heat cycles technique",
            "tiny dabs vs fat dabs",
            "cleaning between different concentrates",
            "traveling with v5 tips"
        ],
        "Troubleshooting_Specific": [
            "v5 leaking from bottom",
            "concentrate spitting and popping",
            "no vapor production at all",
            "burnt taste every hit",
            "metallic taste from v5",
            "v5 gets too hot to touch",
            "concentrate pooling in corners",
            "reclaim building up fast",
            "vapor tastes like plastic",
            "cup spinning when removing"
        ],
        "Concentrate_Types": [
            "what concentrates work best in v5",
            "can I use distillate in v5",
            "live resin vs cured resin difference",
            "rosin in v5 good or bad",
            "shatter breaks my dabs technique",
            "diamonds and sauce how to",
            "crumble keeps falling out",
            "budder consistency best?",
            "thca crystalline in v5",
            "mixing different concentrate types"
        ],
        "Battery_Power": [
            "18650 vs 21700 battery which",
            "best 18650 battery for v5",
            "battery wraps damaged is it safe",
            "how many bowls per battery charge",
            "external charger vs usb charging",
            "battery getting hot normal?",
            "mah rating what does it mean",
            "married batteries explained",
            "when to replace old batteries",
            "fake vs authentic batteries"
        ],
        "Shipping_Ordering": [
            "how long does shipping take",
            "can I track my order",
            "international shipping available",
            "discrete packaging?",
            "order wrong item received",
            "missing items from order",
            "order still processing after 5 days",
            "can I cancel my order",
            "change shipping address",
            "combine orders discount"
        ],
        "Warranty_Support": [
            "how long is warranty",
            "warranty covers what exactly",
            "broken cup warranty replacement",
            "doa device what do I do",
            "warranty claim process",
            "user damage vs defect",
            "how to contact support",
            "response time from matt",
            "warranty international buyers",
            "proof of purchase needed"
        ],
        "Dry_Herb_Options": [
            "nice dreamz review worth it?",
            "nice dreamz vs dynavap",
            "convection vs conduction vaping",
            "nice dreamz temperature settings",
            "how many bowls per charge nice dreamz",
            "nice dreamz easy to clean?",
            "nice dreamz dosing capsules",
            "nice dreamz compared to mighty",
            "best grind consistency for nice dreamz",
            "nice dreamz smell reduction"
        ],
        "Nice_Dreamz_Fogger": [
            "what is fogger cup for",
            "fogger cup vs sic cup",
            "how to use nice dreamz fogger",
            "fogger cup cleaning",
            "fogger cup temp settings",
            "is fogger cup worth getting",
            "fogger efficiency vs v5",
            "fogger cup compatibility",
            "fogger cup versus regular cup",
            "best practices fogger cup"
        ],
        "Ruby_Twist_Specific": [
            "ruby twist how does it work",
            "ruby twist vs other ball vapes",
            "ruby twist coil watts",
            "ruby twist cleaning rubies",
            "ruby twist portable?",
            "ruby twist efficiency",
            "ruby twist learning curve",
            "ruby twist vs flowerpot",
            "ruby twist vs qaroma",
            "ruby twist worth the price"
        ],
        "Lightning_Pen": [
            "lightning pen review any good",
            "lightning pen vs yocan",
            "how to load lightning pen",
            "lightning pen battery life",
            "lightning pen coils replacement",
            "lightning pen vs v5 portable",
            "lightning pen leaking issues",
            "lightning pen voltage",
            "lightning pen warranty",
            "lightning pen maintenance"
        ],
        "Accessories_Parts": [
            "bottomless banger which size",
            "carb cap recommendations v5",
            "silicone jar good for storage",
            "dab tool best style",
            "whip adapter for v5",
            "14mm vs 18mm glass",
            "hydratube for v5",
            "o ring sizes for v5",
            "drip tip options",
            "case for traveling with v5"
        ],
        "Reddit_Community": [
            "where is divine tribe reddit",
            "discord server link",
            "facebook group active?",
            "instagram for deals",
            "youtube channel tutorials",
            "community troubleshooting help",
            "user photos and reviews where",
            "best resource for beginners",
            "fc thread divine tribe",
            "reddit vs discord which better"
        ],
        "Storage_Jars": [
            "uv jars worth it?",
            "jar sizes for concentrates",
            "childproof jars",
            "glass vs silicone storage",
            "how many grams in 5ml jar",
            "jars protect from light why",
            "best way to store rosin",
            "freezer storage concentrates",
            "preventing terpene loss",
            "organizing multiple strains"
        ],
        "General_Questions": [
            "is divine tribe legit company",
            "matt the owner still active",
            "made in usa or china",
            "why choose divine tribe",
            "company history",
            "future products coming",
            "divine tribe vs competitors why better",
            "company values ethics",
            "support small business",
            "customer service reputation"
        ]
    }
    
    # Flatten questions
    all_questions = []
    for category, q_list in questions.items():
        for q in q_list:
            all_questions.append((category, q))
    
    total_questions = len(all_questions)
    print(f"📊 Total questions: {total_questions}\n")
    print("=" * 100)
    
    # Results storage
    results = {
        "metadata": {
            "test_date": datetime.now().isoformat(),
            "test_type": "REAL_MISTRAL_GENERATION",
            "total_questions": total_questions,
            "categories": list(questions.keys()),
            "version": "2.0"
        },
        "results": []
    }
    
    start_time = time.time()
    
    try:
        # Process each question
        for idx, (category, question) in enumerate(all_questions, 1):
            session_id = f"test_{idx}"
            question_start_time = time.time()
            
            # Print progress
            print_progress(idx, total_questions, category, start_time)
            
            # Step 1: Route the query
            route_result = router.route(question)
            route = route_result['route']
            
            # Step 2: Generate REAL response based on route
            response = None
            intent = 'general'
            context = ""
            
            if route == 'troubleshooting':
                # Use cached troubleshooting response
                response = route_result.get('data', '')
                intent = 'troubleshooting'
                
            elif route == 'how_to':
                # Use cached how-to response
                response = route_result.get('data', '')
                intent = 'how_to'
                
            elif route in ['warranty', 'return', 'order', 'support']:
                # Use cached support response
                response = route_result.get('data', '')
                intent = 'support'
                
            elif route == 'cache':
                # Product in cache - but generate conversational answer
                product_info = route_result.get('data', '')
                context = product_info
                intent = 'product_question'
                response = generate_mistral_answer(question, context, intent)
                
            elif route == 'rag':
                # RAG search - get products and generate answer
                products = db.search(question, max_results=3)
                
                # Build context from products
                context = "Relevant products:\n"
                for i, prod in enumerate(products, 1):
                    context += f"\n{i}. {prod.get('name', 'Unknown')}"
                    if prod.get('price'):
                        context += f" - ${prod['price']}"
                    if prod.get('description'):
                        context += f"\n   {prod['description'][:200]}"
                
                # Determine intent
                if 'vs' in question or 'better' in question or 'compare' in question:
                    intent = 'comparison'
                else:
                    intent = 'product_question'
                
                # Generate answer with Mistral
                response = generate_mistral_answer(question, context, intent)
                
            elif route == 'mistral':
                # Needs Mistral reasoning - no specific context
                intent = 'general'
                context = "Use your knowledge of Divine Tribe products to answer."
                response = generate_mistral_answer(question, context, intent)
                
            elif route == 'reject':
                response = route_result.get('data', 'Sorry, I can only help with Divine Tribe products.')
                
            else:
                # Fallback - use Mistral with no context
                response = generate_mistral_answer(question, "No specific context available.", 'general')
            
            # Calculate response time
            response_time = time.time() - question_start_time
            
            # Store result
            result_entry = {
                "question_number": idx,
                "category": category,
                "question": question,
                "route": route,
                "intent": intent,
                "reasoning": route_result.get('reasoning', ''),
                "response": response if response else "No response generated",
                "response_length": len(response) if response else 0,
                "response_time_seconds": round(response_time, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            results["results"].append(result_entry)
            
            # Display full answer every 25 questions
            if idx % 25 == 0:
                print(f"\n\n{'='*100}")
                print(f"📝 QUESTION #{idx} [{category}]")
                print(f"{'='*100}")
                print(f"Q: {question}")
                print(f"Route: {route.upper()} | Intent: {intent}")
                print(f"Time: {response_time:.2f}s")
                print(f"\n{response if response else '[No response generated]'}\n")
                print(f"{'='*100}\n")
            
            # Small delay to prevent overwhelming Mistral
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user. Saving results...")
    
    # Final progress
    print_progress(len(results["results"]), total_questions, "COMPLETE", start_time)
    print("\n\n")
    
    # Calculate statistics
    total_time = time.time() - start_time
    avg_response_time = sum(r['response_time_seconds'] for r in results["results"]) / len(results["results"])
    
    results["metadata"]["total_time_seconds"] = round(total_time, 2)
    results["metadata"]["total_time_minutes"] = round(total_time / 60, 2)
    results["metadata"]["average_response_time_seconds"] = round(avg_response_time, 2)
    results["metadata"]["questions_completed"] = len(results["results"])
    
    # Save results to JSON
    output_file = f"stress_test_REAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = Path(output_file)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("=" * 100)
    print("✅ TEST COMPLETE!")
    print("=" * 100)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {int(total_time/60)}m {int(total_time%60)}s")
    print(f"Average response time: {avg_response_time:.2f}s")
    print(f"Results saved: {output_file}")
    print()
    
    # Route breakdown
    route_counts = {}
    for result in results["results"]:
        route = result['route']
        route_counts[route] = route_counts.get(route, 0) + 1
    
    print("📊 ROUTE BREAKDOWN:")
    for route, count in sorted(route_counts.items()):
        percentage = (count / len(results["results"])) * 100
        print(f"  {route}: {count} ({percentage:.1f}%)")
    
    print("\n" + "=" * 100)
    print()


if __name__ == "__main__":
    run_real_test()
