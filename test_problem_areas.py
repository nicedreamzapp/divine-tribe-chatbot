#!/usr/bin/env python3
"""
Focused test - Only problem areas
"""

import requests
import json
from datetime import datetime

CHATBOT_URL = "http://localhost:5001/chat"

PROBLEM_QUESTIONS = [
    "my product arrived damaged",
    "I need a refund",
    "warranty information",
    "atomizer is broken",
    "need to return this",
    "what is the cub?",
    "do i need the cub?",
    "cub cleaner",
    "cub with core",
    "can i use cub alone?",
    "what is v5 xl?",
    "tell me about core deluxe",
    "what should i buy as beginner?",
    "my v5 won't fire",
    "getting no vapor",
    "product leaking",
]

def test_question(question):
    try:
        response = requests.post(CHATBOT_URL, json={"message": question, "session_id": "test"}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return {"success": True, "response": data.get("response", ""), "intent": data.get("intent", "")}
        return {"success": False, "response": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "response": f"Error: {str(e)}"}

def main():
    print("\n" + "="*70)
    print("FOCUSED TEST - Problem Areas Only")
    print("="*70 + "\n")
    
    results = []
    
    for idx, question in enumerate(PROBLEM_QUESTIONS, 1):
        print(f"[{idx:2d}/{len(PROBLEM_QUESTIONS)}] {question}")
        result = test_question(question)
        
        if result["success"]:
            response = result["response"]
            issues = []
            
            if "matt@ineed" in response.lower():
                if "ineedheemp" in response.lower():
                    issues.append("EMAIL TYPO")
                elif "ineedhemp" in response.lower():
                    issues.append("EMAIL OK")
            
            word_count = len(response.split())
            if word_count > 100:
                issues.append(f"TOO LONG ({word_count} words)")
            else:
                issues.append(f"OK ({word_count} words)")
            
            if "cub" in question.lower():
                if "cleaning" in response.lower():
                    issues.append("CUB OK")
                else:
                    issues.append("CUB WRONG")
            
            print(f"   Intent: {result['intent']}")
            print(f"   Issues: {', '.join(issues)}")
            
            results.append({"question": question, "response": response, "issues": issues})
        else:
            print(f"   FAILED: {result['response']}")
        
        print()
    
    print("="*70)
    print("SUMMARY:")
    print("="*70)
    
    email_typos = sum(1 for r in results if any("EMAIL TYPO" in i for i in r.get("issues", [])))
    too_long = sum(1 for r in results if any("TOO LONG" in i for i in r.get("issues", [])))
    cub_wrong = sum(1 for r in results if any("CUB WRONG" in i for i in r.get("issues", [])))
    
    print(f"\nEmail typos: {email_typos}")
    print(f"Too long: {too_long}")
    print(f"Cub wrong: {cub_wrong}")
    
    if email_typos == 0 and too_long == 0 and cub_wrong == 0:
        print("\nALL FIXED!")
    else:
        print("\nStill has issues")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"problem_test_{timestamp}.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSaved: problem_test_{timestamp}.json\n")

if __name__ == "__main__":
    main()
