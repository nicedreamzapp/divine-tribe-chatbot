#!/usr/bin/env python3
"""
Conversation Logger - Tracks all chatbot interactions for RLHF feedback
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class ConversationLogger:
    def __init__(self, log_dir: str = "conversation_logs"):
        """Initialize conversation logger"""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        print(f"✓ Conversation Logger initialized - saving to {log_dir}/")
    
    def log_conversation(self,
                        session_id: str,
                        user_query: str,
                        bot_response: str,
                        products_shown: List[Dict],
                        intent: str,
                        confidence: float) -> str:
        """
        Log a single conversation exchange
        Returns: chat_id for this exchange
        """
        # Generate unique chat ID
        timestamp = datetime.now()
        chat_id = f"{session_id}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Handle products_shown - can be list of dicts OR list of strings
        if products_shown:
            if isinstance(products_shown[0], dict):
                # List of product dicts
                product_names = [p['name'] for p in products_shown]
                product_urls = [p['url'] for p in products_shown]
            else:
                # List of product name strings (already extracted)
                product_names = products_shown
                product_urls = []
        else:
            product_names = []
            product_urls = []
        
        # Create log entry
        log_entry = {
            'chat_id': chat_id,
            'session_id': session_id,
            'timestamp': timestamp.isoformat(),
            'user_query': user_query,
            'bot_response': bot_response,
            'products_shown': product_names,
            'product_urls': product_urls,
            'intent': intent,
            'confidence': confidence,
            'feedback': None,  # Will be filled by feedback_interface
            'feedback_timestamp': None
        }
        
        # Save to daily log file
        date_str = timestamp.strftime('%Y-%m-%d')
        log_file = os.path.join(self.log_dir, f"{date_str}.json")
        
        # Load existing logs or create new list
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Append new log
        logs.append(log_entry)
        
        # Save back to file
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return chat_id
    
    def get_logs_by_date(self, date_str: str) -> List[Dict]:
        """Get all logs for a specific date (YYYY-MM-DD)"""
        log_file = os.path.join(self.log_dir, f"{date_str}.json")
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r') as f:
            return json.load(f)
    
    def get_recent_logs(self, days: int = 1) -> List[Dict]:
        """Get logs from last N days"""
        all_logs = []
        
        # Get all log files
        log_files = sorted([f for f in os.listdir(self.log_dir) if f.endswith('.json')])
        
        # Get most recent files
        for log_file in log_files[-days:]:
            with open(os.path.join(self.log_dir, log_file), 'r') as f:
                all_logs.extend(json.load(f))
        
        return all_logs
    
    def update_feedback(self, chat_id: str, feedback: str, reason: str = "") -> bool:
        """Update feedback for a specific chat_id"""
        # Search through log files to find the chat
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.json')]
        
        for log_file in log_files:
            log_path = os.path.join(self.log_dir, log_file)
            with open(log_path, 'r') as f:
                logs = json.load(f)
            
            # Find and update the specific chat
            for log in logs:
                if log['chat_id'] == chat_id:
                    log['feedback'] = feedback
                    log['feedback_reason'] = reason
                    log['feedback_timestamp'] = datetime.now().isoformat()
                    
                    # Save updated logs
                    with open(log_path, 'w') as f:
                        json.dump(logs, f, indent=2)
                    
                    return True
        
        return False
    
    def get_unfeedback_logs(self, limit: int = 20) -> List[Dict]:
        """Get logs that don't have feedback yet"""
        unfeedback = []
        
        log_files = sorted([f for f in os.listdir(self.log_dir) if f.endswith('.json')], reverse=True)
        
        for log_file in log_files:
            with open(os.path.join(self.log_dir, log_file), 'r') as f:
                logs = json.load(f)
            
            for log in logs:
                if log['feedback'] is None:
                    unfeedback.append(log)
                    if len(unfeedback) >= limit:
                        return unfeedback
        
        return unfeedback
    
    def get_stats(self) -> Dict:
        """Get logging statistics"""
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.json')]
        
        total_conversations = 0
        total_with_feedback = 0
        
        for log_file in log_files:
            with open(os.path.join(self.log_dir, log_file), 'r') as f:
                logs = json.load(f)
                total_conversations += len(logs)
                total_with_feedback += sum(1 for log in logs if log['feedback'] is not None)
        
        return {
            'total_conversations': total_conversations,
            'with_feedback': total_with_feedback,
            'without_feedback': total_conversations - total_with_feedback,
            'days_logged': len(log_files)
        }
