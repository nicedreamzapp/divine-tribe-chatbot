#!/usr/bin/env python3
"""
Feedback Interface - Terminal UI for reviewing and rating chatbot conversations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.conversation_logger import ConversationLogger
import json
from datetime import datetime

class FeedbackInterface:
    def __init__(self):
        """Initialize feedback interface"""
        self.logger = ConversationLogger()
        self.feedback_log_path = "feedback_log.json"
        print("\n" + "="*80)
        print("DIVINE TRIBE CHATBOT - FEEDBACK INTERFACE")
        print("="*80 + "\n")
    
    def display_conversation(self, log: dict, index: int, total: int):
        """Display a single conversation for review"""
        print("\n" + "="*80)
        print(f"CONVERSATION {index}/{total}")
        print("="*80)
        print(f"\n📅 Time: {log['timestamp']}")
        print(f"🔖 Chat ID: {log['chat_id']}")
        print(f"🎯 Intent: {log['intent']} (confidence: {log['confidence']})")
        print(f"\n👤 USER QUERY:\n{log['user_query']}")
        print(f"\n🤖 BOT RESPONSE:\n{log['bot_response']}")
        
        if log['products_shown']:
            print(f"\n📦 PRODUCTS SHOWN ({len(log['products_shown'])}):")
            for i, (name, url) in enumerate(zip(log['products_shown'], log['product_urls']), 1):
                print(f"   {i}. {name}")
                print(f"      {url}")
        else:
            print("\n📦 PRODUCTS SHOWN: None")
        
        print("\n" + "-"*80)
    
    def get_feedback(self):
        """Get feedback input from user"""
        print("\nRATE THIS RESPONSE:")
        print("  [g] GOOD - Correct response")
        print("  [b] BAD - Incorrect/problematic response")
        print("  [s] SKIP - Review later")
        print("  [q] QUIT - Exit feedback interface")
        
        while True:
            choice = input("\nYour rating: ").lower().strip()
            
            if choice in ['g', 'good']:
                reason = input("Why was this good? (optional): ").strip()
                return 'GOOD', reason
            elif choice in ['b', 'bad']:
                reason = input("Why was this bad? (required): ").strip()
                if not reason:
                    print("❌ Please explain why this was bad")
                    continue
                return 'BAD', reason
            elif choice in ['s', 'skip']:
                return 'SKIP', ''
            elif choice in ['q', 'quit']:
                return 'QUIT', ''
            else:
                print("❌ Invalid choice. Use g/b/s/q")
    
    def save_feedback(self, chat_id: str, rating: str, reason: str):
        """Save feedback to feedback_log.json"""
        # Load existing feedback log
        if os.path.exists(self.feedback_log_path):
            with open(self.feedback_log_path, 'r') as f:
                feedback_log = json.load(f)
        else:
            feedback_log = []
        
        # Add new feedback entry
        feedback_entry = {
            'chat_id': chat_id,
            'rating': rating,
            'reason': reason,
            'feedback_timestamp': datetime.now().isoformat()
        }
        
        feedback_log.append(feedback_entry)
        
        # Save back to file
        with open(self.feedback_log_path, 'w') as f:
            json.dump(feedback_log, f, indent=2)
        
        # Also update the conversation log
        self.logger.update_feedback(chat_id, rating, reason)
    
    def review_conversations(self, days: int = 1, limit: int = 20):
        """Main review loop"""
        # Get unreviewed conversations
        logs = self.logger.get_unfeedback_logs(limit=limit)
        
        if not logs:
            print("✅ No unreviewed conversations found!")
            print("\nTry:")
            print("  python3 feedback_interface.py --days 7  # Review last 7 days")
            return
        
        print(f"\n📋 Found {len(logs)} unreviewed conversations")
        
        reviewed_count = 0
        good_count = 0
        bad_count = 0
        
        for i, log in enumerate(logs, 1):
            self.display_conversation(log, i, len(logs))
            
            rating, reason = self.get_feedback()
            
            if rating == 'QUIT':
                print(f"\n✅ Reviewed {reviewed_count} conversations")
                break
            elif rating == 'SKIP':
                print("⏭️  Skipped")
                continue
            else:
                self.save_feedback(log['chat_id'], rating, reason)
                reviewed_count += 1
                
                if rating == 'GOOD':
                    good_count += 1
                    print("✅ Marked as GOOD")
                elif rating == 'BAD':
                    bad_count += 1
                    print("❌ Marked as BAD")
        
        # Show summary
        print("\n" + "="*80)
        print("REVIEW SUMMARY")
        print("="*80)
        print(f"Total reviewed: {reviewed_count}")
        print(f"✅ Good: {good_count}")
        print(f"❌ Bad: {bad_count}")
        print("\nNext step: Run 'python3 ace_engine.py --learn' to improve the chatbot!")
        print("="*80 + "\n")
    
    def show_stats(self):
        """Show statistics about logged conversations"""
        stats = self.logger.get_stats()
        
        print("\n" + "="*80)
        print("CONVERSATION STATISTICS")
        print("="*80)
        print(f"Total conversations: {stats['total_conversations']}")
        print(f"With feedback: {stats['with_feedback']}")
        print(f"Without feedback: {stats['without_feedback']}")
        print(f"Days logged: {stats['days_logged']}")
        print("="*80 + "\n")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Review chatbot conversations')
    parser.add_argument('--days', type=int, default=1, help='Number of days to review (default: 1)')
    parser.add_argument('--limit', type=int, default=20, help='Max conversations to review (default: 20)')
    parser.add_argument('--stats', action='store_true', help='Show statistics only')
    
    args = parser.parse_args()
    
    interface = FeedbackInterface()
    
    if args.stats:
        interface.show_stats()
    else:
        interface.review_conversations(days=args.days, limit=args.limit)

if __name__ == '__main__':
    main()

