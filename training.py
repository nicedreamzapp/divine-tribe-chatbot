"""
Training module for Divine Tribe Email Assistant
Learns which senders should be auto-read based on Gmail labels
"""

import os
import json
from typing import Dict, List, Set
from datetime import datetime

# Training data file
TRAINING_FILE = os.path.join(os.path.dirname(__file__), 'auto_read_training.json')


class AutoReadTrainer:
    """Manages auto-read training data from Gmail labels"""

    def __init__(self):
        self.data = self._load()
        print(f"✅ Training loaded: {len(self.data.get('senders', []))} auto-read senders")

    def _load(self) -> Dict:
        """Load training data from file"""
        try:
            if os.path.exists(TRAINING_FILE):
                with open(TRAINING_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load training data: {e}")

        return {
            'senders': [],      # Exact email addresses
            'domains': [],      # @domain.com patterns
            'examples': [],     # Log of trained emails
        }

    def _save(self):
        """Save training data to file"""
        try:
            with open(TRAINING_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"❌ Could not save training data: {e}")

    def add_sender(self, email_data: Dict) -> tuple:
        """
        Add a sender to the auto-read training list
        Returns (sender, domain) that were added
        """
        sender = (email_data.get('from_email') or '').lower().strip()
        subject = email_data.get('subject') or ''

        if not sender:
            return None, None

        # Extract domain
        domain = None
        if '@' in sender:
            domain = '@' + sender.split('@')[1]

        # Add sender if not already tracked
        if sender not in self.data['senders']:
            self.data['senders'].append(sender)
            print(f"   📚 Trained sender: {sender}")

        # Add domain if not already tracked
        if domain and domain not in self.data['domains']:
            self.data['domains'].append(domain)
            print(f"   📚 Trained domain: {domain}")

        # Save example
        example = {
            'sender': sender,
            'domain': domain,
            'subject': subject,
            'trained_at': datetime.now().isoformat(),
        }
        self.data['examples'].append(example)

        # Keep only last 1000 examples
        if len(self.data['examples']) > 1000:
            self.data['examples'] = self.data['examples'][-1000:]

        self._save()
        return sender, domain

    def is_auto_read(self, email_data: Dict) -> bool:
        """Check if this email should be auto-read based on training"""
        sender = (email_data.get('from_email') or '').lower().strip()

        if not sender:
            return False

        # Check exact sender match
        if sender in self.data.get('senders', []):
            return True

        # Check domain match
        if '@' in sender:
            domain = '@' + sender.split('@')[1]
            if domain in self.data.get('domains', []):
                return True

        return False

    def get_stats(self) -> str:
        """Get training statistics as a string"""
        senders = self.data.get('senders', [])
        domains = self.data.get('domains', [])
        examples = self.data.get('examples', [])

        stats = "=" * 50 + "\n"
        stats += "AUTO-READ TRAINING STATS\n"
        stats += "=" * 50 + "\n\n"
        stats += f"Trained senders: {len(senders)}\n"
        stats += f"Trained domains: {len(domains)}\n"
        stats += f"Total examples:  {len(examples)}\n\n"

        if domains:
            stats += "Trained domains (all emails from these auto-read):\n"
            for d in sorted(domains):
                stats += f"  • {d}\n"
            stats += "\n"

        if senders:
            stats += "Recent trained senders:\n"
            for s in senders[-15:]:
                stats += f"  • {s}\n"

        return stats

    def list_all(self) -> Dict:
        """Return all training data"""
        return self.data


# Quick test / CLI
if __name__ == "__main__":
    trainer = AutoReadTrainer()
    print(trainer.get_stats())
