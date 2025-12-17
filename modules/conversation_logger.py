#!/usr/bin/env python3
"""
conversation_logger.py - Tracks all chatbot interactions for RLHF feedback
CLEANED: Better file handling, thread-safe writes, error recovery
"""

import json
import os
import fcntl
from datetime import datetime
from typing import Dict, List, Optional


class ConversationLogger:
    """
    Logs all conversations for analysis and RLHF training
    Thread-safe with file locking
    """
    
    def __init__(self, log_dir: str = "conversation_logs"):
        """Initialize conversation logger"""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        print(f"✓ Conversation Logger initialized - saving to {log_dir}/")
    
    def log_conversation(
        self,
        session_id: str,
        user_query: str,
        bot_response: str,
        products_shown: List,
        intent: str,
        confidence: float
    ) -> str:
        """
        Log a single conversation exchange
        
        Args:
            session_id: Unique session identifier
            user_query: User's query
            bot_response: Bot's response
            products_shown: Products shown (list of dicts or list of names)
            intent: Classified intent
            confidence: Confidence score
        
        Returns:
            chat_id for this exchange
        """
        # Generate unique chat ID
        timestamp = datetime.now()
        chat_id = f"{session_id}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Handle products_shown - can be list of dicts OR list of strings
        if products_shown:
            if isinstance(products_shown[0], dict) if products_shown else False:
                # List of product dicts
                product_names = [p.get('name', 'Unknown') for p in products_shown]
                product_urls = [p.get('url', '') for p in products_shown]
            else:
                # List of product name strings
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
            'feedback': None,
            'feedback_timestamp': None
        }
        
        # Save to daily log file
        date_str = timestamp.strftime('%Y-%m-%d')
        log_file = os.path.join(self.log_dir, f"{date_str}.json")
        
        # Thread-safe write with file locking
        self._write_log_entry(log_file, log_entry)
        
        return chat_id
    
    def _write_log_entry(self, log_file: str, log_entry: Dict):
        """Write log entry with file locking for thread safety"""
        try:
            if os.path.exists(log_file):
                # File exists, append to it
                with open(log_file, 'r+') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        # Corrupted file, start fresh
                        print(f"⚠️  Corrupted log file {log_file}, starting fresh")
                        logs = []
                    
                    logs.append(log_entry)
                    f.seek(0)
                    f.truncate()
                    json.dump(logs, f, indent=2)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Unlock
            else:
                # New file
                logs = [log_entry]
                with open(log_file, 'w') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    json.dump(logs, f, indent=2)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        except Exception as e:
            print(f"⚠️  Failed to log conversation: {e}")
            # Don't crash if logging fails
    
    def get_logs_by_date(self, date_str: str) -> List[Dict]:
        """
        Get all logs for a specific date (YYYY-MM-DD)
        
        Args:
            date_str: Date string in format YYYY-MM-DD
        
        Returns:
            List of log entries
        """
        log_file = os.path.join(self.log_dir, f"{date_str}.json")
        
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️  Corrupted log file: {log_file}")
            return []
        except Exception as e:
            print(f"⚠️  Error reading log file: {e}")
            return []
    
    def get_recent_logs(self, days: int = 1) -> List[Dict]:
        """
        Get logs from last N days
        
        Args:
            days: Number of days to retrieve
        
        Returns:
            List of log entries
        """
        all_logs = []
        
        # Get all log files
        try:
            log_files = sorted([
                f for f in os.listdir(self.log_dir)
                if f.endswith('.json')
            ])
        except Exception as e:
            print(f"⚠️  Error listing log files: {e}")
            return []
        
        # Get most recent files
        for log_file in log_files[-days:]:
            try:
                with open(os.path.join(self.log_dir, log_file), 'r') as f:
                    all_logs.extend(json.load(f))
            except Exception as e:
                print(f"⚠️  Error reading {log_file}: {e}")
                continue
        
        return all_logs
    
    def update_feedback(self, chat_id: str, feedback: str, reason: str = "") -> bool:
        """
        Update feedback for a specific chat_id
        
        Args:
            chat_id: Chat ID to update
            feedback: Feedback value (e.g., "good", "bad")
            reason: Optional reason for feedback
        
        Returns:
            True if successfully updated
        """
        # Search through log files to find the chat
        try:
            log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.json')]
        except Exception as e:
            print(f"⚠️  Error listing log files: {e}")
            return False
        
        for log_file in log_files:
            log_path = os.path.join(self.log_dir, log_file)
            
            try:
                with open(log_path, 'r+') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        continue
                    
                    # Find and update the specific chat
                    updated = False
                    for log in logs:
                        if log['chat_id'] == chat_id:
                            log['feedback'] = feedback
                            log['feedback_reason'] = reason
                            log['feedback_timestamp'] = datetime.now().isoformat()
                            updated = True
                            break
                    
                    if updated:
                        # Save updated logs
                        f.seek(0)
                        f.truncate()
                        json.dump(logs, f, indent=2)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        return True
                    
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            except Exception as e:
                print(f"⚠️  Error updating feedback in {log_file}: {e}")
                continue
        
        return False
    
    def get_unfeedback_logs(self, limit: int = 20) -> List[Dict]:
        """
        Get logs that don't have feedback yet
        
        Args:
            limit: Maximum number of logs to return
        
        Returns:
            List of log entries without feedback
        """
        unfeedback = []
        
        try:
            log_files = sorted(
                [f for f in os.listdir(self.log_dir) if f.endswith('.json')],
                reverse=True
            )
        except Exception as e:
            print(f"⚠️  Error listing log files: {e}")
            return []
        
        for log_file in log_files:
            try:
                with open(os.path.join(self.log_dir, log_file), 'r') as f:
                    logs = json.load(f)
                
                for log in logs:
                    if log.get('feedback') is None:
                        unfeedback.append(log)
                        if len(unfeedback) >= limit:
                            return unfeedback
            
            except Exception as e:
                print(f"⚠️  Error reading {log_file}: {e}")
                continue
        
        return unfeedback
    
    def get_stats(self) -> Dict:
        """
        Get logging statistics
        
        Returns:
            Dictionary with stats
        """
        try:
            log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.json')]
        except Exception as e:
            print(f"⚠️  Error getting stats: {e}")
            return {
                'error': str(e),
                'total_conversations': 0,
                'with_feedback': 0,
                'without_feedback': 0,
                'days_logged': 0
            }
        
        total_conversations = 0
        total_with_feedback = 0
        
        for log_file in log_files:
            try:
                with open(os.path.join(self.log_dir, log_file), 'r') as f:
                    logs = json.load(f)
                    total_conversations += len(logs)
                    total_with_feedback += sum(1 for log in logs if log.get('feedback') is not None)
            except Exception as e:
                print(f"⚠️  Error processing {log_file}: {e}")
                continue
        
        return {
            'total_conversations': total_conversations,
            'with_feedback': total_with_feedback,
            'without_feedback': total_conversations - total_with_feedback,
            'days_logged': len(log_files),
            'feedback_percentage': round(total_with_feedback / total_conversations * 100, 1) if total_conversations > 0 else 0
        }
    
    def export_for_training(self, output_file: str = "training_data.jsonl"):
        """
        Export logs in JSONL format for RLHF training
        
        Args:
            output_file: Output file path
        
        Returns:
            Number of entries exported
        """
        try:
            log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.json')]
        except Exception as e:
            print(f"⚠️  Error exporting: {e}")
            return 0
        
        exported = 0
        
        with open(output_file, 'w') as out:
            for log_file in log_files:
                try:
                    with open(os.path.join(self.log_dir, log_file), 'r') as f:
                        logs = json.load(f)
                    
                    for log in logs:
                        # Only export logs with feedback
                        if log.get('feedback') is not None:
                            training_entry = {
                                'prompt': log['user_query'],
                                'completion': log['bot_response'],
                                'feedback': log['feedback'],
                                'intent': log['intent']
                            }
                            out.write(json.dumps(training_entry) + '\n')
                            exported += 1
                
                except Exception as e:
                    print(f"⚠️  Error processing {log_file}: {e}")
                    continue
        
        print(f"✅ Exported {exported} training entries to {output_file}")
        return exported


def test_conversation_logger():
    """Test the conversation logger"""
    print("\n" + "="*70)
    print("CONVERSATION LOGGER TEST")
    print("="*70 + "\n")
    
    logger = ConversationLogger(log_dir="test_logs")
    
    # Log some conversations
    print("Logging test conversations...")
    for i in range(3):
        chat_id = logger.log_conversation(
            session_id="test_session",
            user_query=f"Test query {i+1}",
            bot_response=f"Test response {i+1}",
            products_shown=["Product A", "Product B"],
            intent="test",
            confidence=0.95
        )
        print(f"  Logged: {chat_id}")
    
    # Get stats
    print("\nLogger Stats:")
    stats = logger.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get recent logs
    print("\nRecent Logs:")
    recent = logger.get_recent_logs(days=1)
    print(f"  Found {len(recent)} recent logs")
    
    # Clean up test logs
    import shutil
    shutil.rmtree("test_logs")
    print("\n✓ Test logs cleaned up")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    test_conversation_logger()
