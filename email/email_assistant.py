#!/usr/bin/env python3
"""
Divine Tribe Email Assistant
Main script - ties everything together
Reads emails, generates responses, sends for approval
"""

import os
import re
import asyncio
import json
from typing import Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv
import anthropic

# Import our modules
from woo_client import WooCommerceClient
from gmail_client import GmailClient
from telegram_approval import TelegramApproval
from training import AutoReadTrainer

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

CLAUDE_MODEL = "claude-3-5-haiku-20241022"
REQUIRE_APPROVAL = os.getenv('REQUIRE_APPROVAL', 'true').lower() == 'true'
EMAIL_CHECK_INTERVAL = int(os.getenv('EMAIL_CHECK_INTERVAL', 60))

# Patterns that should be flagged for manual review
FLAG_PATTERNS = [
    r'\b(refund|money back|charge\s*back|chargeback)\b',
    r'\b(lawyer|attorney|legal|sue|lawsuit)\b',
    r'\b(bbb|better business bureau)\b',
    r'\b(scam|fraud|rip\s*off|ripoff)\b',
    r'\b(terrible|horrible|worst|angry|furious|pissed)\b',
    r'\b(cancel|cancelled|canceled)\s*(my)?\s*(order|subscription)\b',
]

# Patterns for auto-archive (spam/marketing)
SPAM_PATTERNS = [
    r'\b(unsubscribe|opt.out|marketing)\b',
    r'\b(viagra|cialis|pharmacy)\b',
    r'\b(winner|lottery|prize|million\s*dollars)\b',
    r'\b(nigerian|prince)\b',
]

# Patterns for auto-read (no response needed, just mark as read)
AUTO_READ_PATTERNS = [
    # Shipping notifications
    r'(your.*(package|order|shipment).*(shipped|delivered|out for delivery|in transit))',
    r'(tracking.*update|delivery.*notification)',
    r'\b(usps|ups|fedex|dhl)\b.*(tracking|delivered|shipment)',
    # Order confirmations (not questions)
    r'(order.*confirm|thank.*you.*for.*your.*(order|purchase))',
    r'(receipt.*for.*your.*(order|purchase|payment))',
    # Auto-replies
    r'(auto.?reply|automatic.*reply|out.*of.*office|away.*from.*office)',
    r'(this.*is.*an.*automated.*message)',
    r'(do.*not.*reply.*to.*this.*email)',
    # Payment notifications
    r'(payment.*(received|confirmed|processed|successful))',
    r'(invoice.*paid|paid.*invoice)',
    # Newsletter/marketing (that slip through)
    r'(weekly.*digest|monthly.*newsletter|daily.*update)',
    r'(view.*in.*browser|email.*preferences)',
    # System notifications
    r'(subscription.*(confirm|active|renew))',
    r'(account.*(created|verified|updated))',
    r'(password.*(reset|changed))',
    # No-reply senders
    r'(noreply|no-reply|donotreply)',
]

# Sender domains/addresses to auto-read (known automated senders)
AUTO_READ_SENDERS = [
    'noreply@',
    'no-reply@',
    'donotreply@',
    'notifications@',
    'mailer-daemon@',
    'postmaster@',
    '@usps.com',
    '@ups.com',
    '@fedex.com',
    '@dhl.com',
    '@shipstation.com',
    '@shopify.com',
    '@paypal.com',
    '@square.com',
    '@stripe.com',
    '@woocommerce.com',
    '@automattic.com',
    'shipment-tracking@',
    'order-update@',
    'tracking-updates@',
]


class EmailAssistant:
    """Main email assistant that coordinates all components"""

    def __init__(self):
        print("=" * 60)
        print("🚀 DIVINE TRIBE EMAIL ASSISTANT")
        print("=" * 60)

        # Initialize Claude
        self.claude = anthropic.Anthropic()
        print("✅ Claude AI initialized")

        # Initialize components
        self.woo = WooCommerceClient()
        self.gmail = GmailClient()
        self.telegram = TelegramApproval()
        self.trainer = AutoReadTrainer()  # Gmail label-based training

        # Set up approval callbacks
        self.telegram.set_callback('on_approve', self._on_email_approved)
        self.telegram.set_callback('on_reject', self._on_email_rejected)
        self.telegram.set_callback('on_flag', self._on_email_flagged)
        self.telegram.set_callback('on_mark_read', self._on_email_mark_read)

        # Track processed emails
        self.processed_ids = set()

        # Load chatbot knowledge (for product questions)
        self.product_knowledge = self._load_product_knowledge()

        print("=" * 60)
        print(f"📧 Approval required: {REQUIRE_APPROVAL}")
        print(f"⏰ Check interval: {EMAIL_CHECK_INTERVAL}s")
        print("=" * 60)

    def _load_product_knowledge(self) -> str:
        """Load product info from the Tribe Chatbot"""
        knowledge = ""
        products_file = "/Users/matthewmacosko/Desktop/Tribe Chatbot/products_clean.json"

        try:
            with open(products_file, 'r') as f:
                products = json.load(f)
                # Create condensed product summary
                for p in products[:50]:  # Top 50 products
                    name = p.get('name', '')
                    desc = p.get('description', '')[:200]
                    url = p.get('url', '')
                    knowledge += f"- {name}: {desc}... ({url})\n"
                print(f"✅ Loaded {len(products)} products for reference")
        except Exception as e:
            print(f"⚠️  Could not load products: {e}")

        return knowledge

    def classify_email(self, email: Dict) -> Dict:
        """
        Classify an email into categories
        Returns: {category: str, should_flag: bool, flag_reason: str}
        """
        subject = (email.get('subject') or '').lower()
        body = (email.get('body') or '').lower()
        from_email = (email.get('from_email') or '').lower()
        combined = f"{subject} {body}"

        # Check TRAINED auto-read senders first (from Gmail label training)
        if self.trainer.is_auto_read(email):
            return {'category': 'auto_read', 'should_flag': False, 'flag_reason': 'trained'}

        # Check for auto-read senders (known automated senders)
        for sender_pattern in AUTO_READ_SENDERS:
            if sender_pattern.lower() in from_email:
                return {'category': 'auto_read', 'should_flag': False, 'flag_reason': None}

        # Check for auto-read content patterns
        for pattern in AUTO_READ_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                return {'category': 'auto_read', 'should_flag': False, 'flag_reason': None}

        # Check for spam
        for pattern in SPAM_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                return {'category': 'spam', 'should_flag': False, 'flag_reason': None}

        # Check for flags (needs human attention)
        for pattern in FLAG_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                return {
                    'category': 'flagged',
                    'should_flag': True,
                    'flag_reason': f"Matched pattern: {pattern}"
                }

        # Classify by content
        if re.search(r'(order|tracking|ship|deliver|where.*(is|my)|status)', combined):
            return {'category': 'order_status', 'should_flag': False, 'flag_reason': None}

        if re.search(r'(return|refund|exchange|send.back)', combined):
            return {'category': 'return', 'should_flag': False, 'flag_reason': None}

        if re.search(r'(broken|damaged|defect|not.work|doesn.t.work|dead)', combined):
            return {'category': 'damaged', 'should_flag': False, 'flag_reason': None}

        if re.search(r'(warranty|guarantee|replace)', combined):
            return {'category': 'warranty', 'should_flag': False, 'flag_reason': None}

        if re.search(r'(how.to|setup|setting|temperature|temp|clean|use)', combined):
            return {'category': 'technical', 'should_flag': False, 'flag_reason': None}

        if re.search(r'(which|best|recommend|difference|compare|vs)', combined):
            return {'category': 'product_question', 'should_flag': False, 'flag_reason': None}

        # Default to general
        return {'category': 'general', 'should_flag': False, 'flag_reason': None}

    def extract_order_number(self, text: str) -> Optional[str]:
        """Extract order number from email text"""
        patterns = [
            r'order\s*#?\s*(\d{4,8})',
            r'#(\d{4,8})',
            r'order\s*number[:\s]*(\d{4,8})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def extract_customer_name(self, email: Dict) -> str:
        """Extract first name from email"""
        from_field = email.get('from', '')

        # Try to get name from "Name <email>" format
        if '<' in from_field:
            name_part = from_field.split('<')[0].strip()
            if name_part:
                # Get first name
                return name_part.split()[0]

        # Fallback to "there" or "friend"
        return "there"

    async def generate_response(self, email: Dict, classification: Dict) -> str:
        """
        Use Claude to generate a response to the email
        """
        customer_name = self.extract_customer_name(email)
        order_number = self.extract_order_number(
            f"{email.get('subject', '')} {email.get('body', '')}"
        )

        # Build context for Claude
        order_context = ""
        if order_number:
            order = self.woo.get_order(order_number)
            if order:
                order_context = f"\n\nORDER INFO (#{order_number}):\n"
                order_context += self.woo.format_order_status(order)

        # Include conversation history if this is a thread
        conversation_context = ""
        thread_count = email.get('thread_count', 1)
        if thread_count > 1:
            conversation_context = f"""

CONVERSATION HISTORY ({thread_count} messages in this thread):
This is an ongoing conversation. Review the full history below to understand context.
{email.get('conversation_history', '')}

The latest message from the customer is what you need to respond to.
"""

        system_prompt = f"""You are Matt's email assistant for Divine Tribe (ineedhemp.com), a vaporizer and hemp products company.

CRITICAL RULES:
1. Be friendly, helpful, and conversational - sound like a real person, not a robot
2. Sign emails as "Matt" from "Divine Tribe"
3. Keep responses concise but complete
4. NEVER make up information about orders - only use the order info provided
5. For product questions, use the product knowledge provided
6. Always offer to help further
7. Include relevant links when helpful
8. If this is a follow-up in a conversation, acknowledge previous messages and continue naturally

CUSTOMER NAME: {customer_name}
EMAIL CATEGORY: {classification['category']}
{order_context}
{conversation_context}

PRODUCT KNOWLEDGE (use for product questions):
{self.product_knowledge[:3000]}

COMMUNITY LINKS (include when relevant):
- Discord: https://discord.com/invite/f3qwvp56be
- Reddit: https://www.reddit.com/r/DivineTribeVaporizers/
- YouTube: @divinetribe1

Write a response email. Do NOT include subject line - just the body."""

        try:
            response = self.claude.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                system=system_prompt,
                messages=[{
                    'role': 'user',
                    'content': f"Customer email:\n\nSubject: {email.get('subject', 'No subject')}\n\n{email.get('body', '')}"
                }]
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"❌ Claude error: {e}")
            return None

    async def process_email(self, email: Dict):
        """Process a single email"""
        email_id = email.get('id')

        if email_id in self.processed_ids:
            return

        from_email = email.get('from_email', 'Unknown')
        subject = email.get('subject', 'No subject')
        thread_id = email.get('thread_id')

        print(f"\n📧 Processing email from {from_email}")
        print(f"   Subject: {subject}")

        # Fetch full thread/conversation history
        thread_messages = []
        conversation_history = ""
        if thread_id:
            thread_messages = self.gmail.get_thread(thread_id)
            if len(thread_messages) > 1:
                print(f"   📜 Thread has {len(thread_messages)} messages")
                conversation_history = self.gmail.format_thread_as_conversation(thread_messages)

        # Add thread info to email data
        email['thread_messages'] = thread_messages
        email['conversation_history'] = conversation_history
        email['thread_count'] = len(thread_messages)

        # Classify
        classification = self.classify_email(email)
        print(f"   Category: {classification['category']}")

        # Handle auto-read (generic notifications, no response needed)
        if classification['category'] == 'auto_read':
            if classification.get('flag_reason') == 'trained':
                print(f"   📖 Auto-read: TRAINED sender ({from_email})")
            else:
                print("   📖 Auto-read: generic/notification email")
            self.gmail.mark_as_read(email_id)
            self.gmail.add_label(email_id, 'Bot/Auto-Read')
            self.processed_ids.add(email_id)
            return

        # Handle spam
        if classification['category'] == 'spam':
            print("   🗑️ Auto-archiving spam")
            self.gmail.archive_email(email_id)
            self.gmail.add_label(email_id, 'Bot/Auto-Archived')
            self.processed_ids.add(email_id)
            return

        # Handle flagged emails
        if classification['should_flag']:
            print(f"   🚩 Flagged: {classification['flag_reason']}")
            self.gmail.add_label(email_id, 'Bot/Flagged')
            await self.telegram.send_flagged_email(email, classification['flag_reason'])
            self.processed_ids.add(email_id)
            return

        # Generate response
        response = await self.generate_response(email, classification)

        if not response:
            print("   ⚠️ Could not generate response - flagging")
            self.gmail.add_label(email_id, 'Bot/Flagged')
            await self.telegram.send_flagged_email(email, "Could not generate response")
            return

        # Add response to email data
        email['draft_response'] = response
        email['classification'] = classification

        # Send for approval
        if REQUIRE_APPROVAL:
            print("   📤 Sending for approval...")
            self.gmail.add_label(email_id, 'Bot/Needs-Review')
            await self.telegram.send_for_approval(email)
        else:
            # Auto-send (only after training period!)
            print("   ✉️ Auto-sending response...")
            self._send_response(email)

        self.processed_ids.add(email_id)

    async def _on_email_approved(self, approval_id: str, email_data: Dict):
        """Called when an email is approved via Telegram"""
        print(f"✅ Email approved: {approval_id}")
        self._send_response(email_data)

    async def _on_email_rejected(self, approval_id: str, email_data: Dict):
        """Called when an email is rejected via Telegram"""
        print(f"❌ Email rejected: {approval_id}")
        email_id = email_data.get('id')
        if email_id:
            self.gmail.remove_label(email_id, 'Bot/Needs-Review')
            self.gmail.add_label(email_id, 'Bot/Flagged')

    async def _on_email_flagged(self, approval_id: str, email_data: Dict):
        """Called when an email is flagged via Telegram"""
        print(f"🚩 Email flagged: {approval_id}")
        email_id = email_data.get('id')
        if email_id:
            self.gmail.remove_label(email_id, 'Bot/Needs-Review')
            self.gmail.add_label(email_id, 'Bot/Flagged')

    async def _on_email_mark_read(self, approval_id: str, email_data: Dict):
        """Called when an email is marked as just-read via Telegram (training)"""
        print(f"📖 Email marked as read-only: {approval_id}")
        print(f"   Trained sender: {email_data.get('from_email')}")
        email_id = email_data.get('id')
        if email_id:
            self.gmail.mark_as_read(email_id)
            self.gmail.remove_label(email_id, 'Bot/Needs-Review')
            self.gmail.add_label(email_id, 'Bot/Auto-Read')

    def _send_response(self, email_data: Dict):
        """Send the email response"""
        to = email_data.get('from_email')
        original_subject = email_data.get('subject', '')
        subject = f"Re: {original_subject}" if not original_subject.startswith('Re:') else original_subject
        body = email_data.get('draft_response', '')
        thread_id = email_data.get('thread_id')

        success = self.gmail.send_email(to, subject, body, thread_id)

        if success:
            email_id = email_data.get('id')
            if email_id:
                self.gmail.mark_as_read(email_id)
                self.gmail.remove_label(email_id, 'Bot/Needs-Review')
                self.gmail.add_label(email_id, 'Bot/Approved')
            print(f"✅ Response sent to {to}")
        else:
            print(f"❌ Failed to send response to {to}")

    def learn_from_labels(self):
        """
        Check for emails with Train-AutoRead label and learn from them.
        This is how you train the system - just add the label in Gmail!
        """
        print("\n📚 Checking for training labels...")
        labeled_emails = self.gmail.get_emails_by_label('Train-AutoRead', max_results=50)

        if not labeled_emails:
            print("   No new training emails found")
            return

        print(f"   Found {len(labeled_emails)} emails with Train-AutoRead label")

        for email in labeled_emails:
            email_id = email.get('id')
            sender = email.get('from_email', 'Unknown')

            # Add to training
            self.trainer.add_sender(email)

            # Remove the training label (so we don't process again)
            self.gmail.remove_label(email_id, 'Train-AutoRead')

            # Mark as read and add Bot/Auto-Read label
            self.gmail.mark_as_read(email_id)
            self.gmail.add_label(email_id, 'Bot/Auto-Read')

        print(f"   ✅ Trained {len(labeled_emails)} new senders")

    async def check_emails(self):
        """Check for new emails and process them"""
        # First, learn from any labeled emails
        self.learn_from_labels()

        print("\n📬 Checking for new emails...")
        emails = self.gmail.get_unread_emails(max_results=10)
        print(f"   Found {len(emails)} unread emails")

        for email in emails:
            await self.process_email(email)

    async def run_loop(self):
        """Main loop - check emails periodically"""
        print("\n🔄 Starting email check loop...")

        while True:
            try:
                await self.check_emails()
            except Exception as e:
                print(f"❌ Error in email loop: {e}")

            print(f"⏰ Next check in {EMAIL_CHECK_INTERVAL}s")
            await asyncio.sleep(EMAIL_CHECK_INTERVAL)

    def run(self):
        """Start the email assistant"""
        # Test connections
        print("\n🔍 Testing connections...")

        woo_ok = self.woo.test_connection()
        gmail_ok = self.gmail.test_connection()

        if not woo_ok:
            print("⚠️  WooCommerce not connected - order lookup disabled")

        if not gmail_ok:
            print("❌ Gmail not connected - cannot proceed")
            print("   Run gmail_client.py first to authenticate")
            return

        # Set up Gmail labels
        self.gmail.setup_labels()

        # Start the main loop with Telegram bot
        print("\n🚀 Starting Email Assistant...")

        async def main():
            # Start email checking in background
            email_task = asyncio.create_task(self.run_loop())

            # Run Telegram bot (this blocks)
            # We need to run both concurrently
            if self.telegram.app:
                await self.telegram.app.initialize()
                await self.telegram.app.start()
                await self.telegram.app.updater.start_polling()

                try:
                    await email_task
                except asyncio.CancelledError:
                    pass
                finally:
                    await self.telegram.app.updater.stop()
                    await self.telegram.app.stop()
                    await self.telegram.app.shutdown()
            else:
                await email_task

        asyncio.run(main())


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    assistant = EmailAssistant()
    assistant.run()
