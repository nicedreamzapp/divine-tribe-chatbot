"""
Telegram Approval System - Send drafts to Matt for approval
Divine Tribe Email Assistant
"""

import os
import json
import asyncio
from typing import Dict, Optional, Callable
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

load_dotenv()

# Training log file for learning auto-read patterns
TRAINING_LOG_FILE = os.path.join(os.path.dirname(__file__), 'auto_read_training.json')


class TelegramApproval:
    """Handle email approval via Telegram"""

    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.app = None
        self.pending_approvals = {}  # message_id -> email_data
        self.callbacks = {
            'on_approve': None,
            'on_reject': None,
            'on_flag': None,
            'on_edit': None,
            'on_mark_read': None  # New callback for training
        }

        # Load existing training data
        self.training_data = self._load_training_data()

        if self.bot_token:
            self.app = Application.builder().token(self.bot_token).build()
            self._setup_handlers()
            print("✅ Telegram approval system initialized")
        else:
            print("⚠️  Telegram bot token not set")

    def _setup_handlers(self):
        """Set up Telegram command and callback handlers"""
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("status", self._cmd_status))
        self.app.add_handler(CommandHandler("pending", self._cmd_pending))
        self.app.add_handler(CommandHandler("training", self._cmd_training))
        self.app.add_handler(CallbackQueryHandler(self._handle_callback))
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self._handle_edit_response
        ))

    def _load_training_data(self) -> Dict:
        """Load training data from file"""
        try:
            if os.path.exists(TRAINING_LOG_FILE):
                with open(TRAINING_LOG_FILE, 'r') as f:
                    data = json.load(f)
                    print(f"✅ Loaded {len(data.get('senders', []))} trained senders, {len(data.get('subjects', []))} subject patterns")
                    return data
        except Exception as e:
            print(f"⚠️  Could not load training data: {e}")

        return {'senders': [], 'subjects': [], 'examples': []}

    def _save_training_data(self):
        """Save training data to file"""
        try:
            with open(TRAINING_LOG_FILE, 'w') as f:
                json.dump(self.training_data, f, indent=2)
            print(f"✅ Training data saved ({len(self.training_data.get('senders', []))} senders)")
        except Exception as e:
            print(f"❌ Could not save training data: {e}")

    def add_to_training(self, email_data: Dict):
        """Add an email to the training data for auto-read"""
        sender = (email_data.get('from_email') or '').lower().strip()
        subject = email_data.get('subject') or ''

        # Extract sender domain
        if '@' in sender:
            domain = '@' + sender.split('@')[1]
        else:
            domain = sender

        # Add sender if not already tracked
        if sender and sender not in self.training_data['senders']:
            self.training_data['senders'].append(sender)

        # Also track the domain
        if domain and domain not in self.training_data['senders']:
            self.training_data['senders'].append(domain)

        # Save example for reference
        example = {
            'sender': sender,
            'subject': subject,
            'date': datetime.now().isoformat(),
        }
        self.training_data['examples'].append(example)

        # Keep only last 500 examples
        if len(self.training_data['examples']) > 500:
            self.training_data['examples'] = self.training_data['examples'][-500:]

        self._save_training_data()
        return sender, domain

    def is_trained_auto_read(self, email_data: Dict) -> bool:
        """Check if this email matches trained auto-read patterns"""
        sender = (email_data.get('from_email') or '').lower().strip()

        # Check exact sender match
        if sender in self.training_data.get('senders', []):
            return True

        # Check domain match
        if '@' in sender:
            domain = '@' + sender.split('@')[1]
            if domain in self.training_data.get('senders', []):
                return True

        return False

    def get_training_stats(self) -> str:
        """Get training statistics"""
        senders = self.training_data.get('senders', [])
        examples = self.training_data.get('examples', [])

        stats = f"📊 Training Stats\n\n"
        stats += f"Trained senders/domains: {len(senders)}\n"
        stats += f"Total examples: {len(examples)}\n\n"

        if senders:
            stats += "Recent trained senders:\n"
            for s in senders[-10:]:
                stats += f"  • {s}\n"

        return stats

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "📧 Divine Tribe Email Assistant\n\n"
            "I'll send you customer emails for approval.\n\n"
            "Commands:\n"
            "/status - Check system status\n"
            "/pending - See pending approvals\n"
            "/training - View auto-read training stats"
        )

    async def _cmd_training(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /training command - show training stats"""
        stats = self.get_training_stats()
        await update.message.reply_text(stats)

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        pending_count = len(self.pending_approvals)
        await update.message.reply_text(
            f"📊 Email Assistant Status\n\n"
            f"Pending approvals: {pending_count}\n"
            f"System: Online ✅"
        )

    async def _cmd_pending(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pending command - show all pending approvals"""
        if not self.pending_approvals:
            await update.message.reply_text("✅ No pending approvals!")
            return

        msg = f"📋 Pending Approvals ({len(self.pending_approvals)}):\n\n"
        for msg_id, data in self.pending_approvals.items():
            msg += f"• From: {data.get('from_email', 'Unknown')}\n"
            msg += f"  Subject: {data.get('subject', 'No subject')[:40]}...\n\n"

        await update.message.reply_text(msg)

    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button presses"""
        query = update.callback_query
        await query.answer()

        data = query.data
        parts = data.split(':')

        if len(parts) != 2:
            return

        action, approval_id = parts

        if approval_id not in self.pending_approvals:
            await query.edit_message_text("⚠️ This approval has expired or was already handled.")
            return

        email_data = self.pending_approvals[approval_id]

        if action == 'approve':
            await query.edit_message_text(
                f"✅ APPROVED\n\n"
                f"To: {email_data.get('from_email')}\n"
                f"Subject: Re: {email_data.get('subject')}\n\n"
                f"Sending response..."
            )
            if self.callbacks['on_approve']:
                await self.callbacks['on_approve'](approval_id, email_data)
            del self.pending_approvals[approval_id]

        elif action == 'reject':
            await query.edit_message_text(
                f"❌ REJECTED\n\n"
                f"Email from {email_data.get('from_email')} will not be answered automatically.\n"
                f"Handle manually if needed."
            )
            if self.callbacks['on_reject']:
                await self.callbacks['on_reject'](approval_id, email_data)
            del self.pending_approvals[approval_id]

        elif action == 'flag':
            await query.edit_message_text(
                f"🚩 FLAGGED FOR MANUAL REVIEW\n\n"
                f"Email from {email_data.get('from_email')}\n"
                f"Subject: {email_data.get('subject')}\n\n"
                f"Marked for your personal attention."
            )
            if self.callbacks['on_flag']:
                await self.callbacks['on_flag'](approval_id, email_data)
            del self.pending_approvals[approval_id]

        elif action == 'mark_read':
            # Training: mark this sender as auto-read in the future
            sender, domain = self.add_to_training(email_data)
            await query.edit_message_text(
                f"📖 MARKED AS READ-ONLY\n\n"
                f"Email from {email_data.get('from_email')}\n"
                f"Subject: {email_data.get('subject')}\n\n"
                f"✅ Trained: Future emails from this sender will be auto-read.\n"
                f"   Sender: {sender}\n"
                f"   Domain: {domain}\n\n"
                f"Use /training to see all trained senders."
            )
            if self.callbacks['on_mark_read']:
                await self.callbacks['on_mark_read'](approval_id, email_data)
            del self.pending_approvals[approval_id]

        elif action == 'edit':
            context.user_data['editing'] = approval_id
            await query.edit_message_text(
                f"✏️ EDIT MODE\n\n"
                f"Original response:\n"
                f"---\n"
                f"{email_data.get('draft_response', '')[:500]}\n"
                f"---\n\n"
                f"Send me the corrected response text.\n"
                f"Or send /cancel to cancel editing."
            )

    async def _handle_edit_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle edited response text from user"""
        if 'editing' not in context.user_data:
            return

        approval_id = context.user_data['editing']

        if update.message.text == '/cancel':
            del context.user_data['editing']
            await update.message.reply_text("❌ Edit cancelled.")
            # Re-send the approval message
            if approval_id in self.pending_approvals:
                await self.send_for_approval(self.pending_approvals[approval_id])
            return

        if approval_id not in self.pending_approvals:
            del context.user_data['editing']
            await update.message.reply_text("⚠️ This approval has expired.")
            return

        # Update the draft response
        email_data = self.pending_approvals[approval_id]
        email_data['draft_response'] = update.message.text
        email_data['was_edited'] = True

        del context.user_data['editing']

        # Confirm and offer to send
        keyboard = [
            [
                InlineKeyboardButton("✅ Send Edited", callback_data=f"approve:{approval_id}"),
                InlineKeyboardButton("✏️ Edit Again", callback_data=f"edit:{approval_id}"),
            ],
            [
                InlineKeyboardButton("❌ Reject", callback_data=f"reject:{approval_id}"),
            ]
        ]

        await update.message.reply_text(
            f"📝 EDITED RESPONSE\n\n"
            f"To: {email_data.get('from_email')}\n"
            f"Subject: Re: {email_data.get('subject')}\n\n"
            f"---\n"
            f"{update.message.text[:800]}\n"
            f"---\n\n"
            f"Send this response?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    def set_callback(self, event: str, callback: Callable):
        """
        Set callback for approval events
        Events: on_approve, on_reject, on_flag, on_edit
        """
        if event in self.callbacks:
            self.callbacks[event] = callback

    async def send_for_approval(self, email_data: Dict) -> str:
        """
        Send an email draft to Telegram for approval
        Returns approval_id
        """
        if not self.app or not self.chat_id:
            print("⚠️  Telegram not configured")
            return None

        # Generate unique approval ID
        approval_id = f"{email_data.get('id', 'unknown')}_{datetime.now().strftime('%H%M%S')}"

        # Store in pending
        self.pending_approvals[approval_id] = email_data

        # Build message
        from_email = email_data.get('from_email', 'Unknown')
        subject = email_data.get('subject', 'No subject')
        body = email_data.get('body', '')[:500]
        draft = email_data.get('draft_response', '')[:800]
        thread_count = email_data.get('thread_count', 1)

        # Build conversation history section if this is a thread
        conversation_section = ""
        if thread_count > 1:
            thread_messages = email_data.get('thread_messages', [])
            conversation_section = f"\n📜 FULL CONVERSATION ({thread_count} messages):\n"
            for i, msg in enumerate(thread_messages, 1):
                msg_from = msg.get('from_email', 'Unknown')
                msg_date = msg.get('date', '')
                msg_body = msg.get('body', '')[:400]  # Truncate each message

                # Identify sender
                if 'ineedhemp.com' in msg_from.lower():
                    sender_label = "💬 [YOU]"
                else:
                    sender_label = "👤 [CUSTOMER]"

                conversation_section += f"\n{sender_label} ({msg_date[:20]}...)\n{msg_body}\n"
                if i < len(thread_messages):
                    conversation_section += "---\n"

            conversation_section += "\n" + "="*30 + "\n"

        message = (
            f"📧 NEW EMAIL - APPROVAL NEEDED\n\n"
            f"From: {from_email}\n"
            f"Subject: {subject}\n"
            f"{'🔄 Thread: ' + str(thread_count) + ' messages' if thread_count > 1 else ''}\n"
            f"{conversation_section}"
            f"\n--- LATEST CUSTOMER MESSAGE ---\n"
            f"{body}\n\n"
            f"--- SUGGESTED RESPONSE ---\n"
            f"{draft}\n\n"
            f"---"
        )

        # Telegram has 4096 char limit - truncate if needed
        if len(message) > 4000:
            # Keep the essential parts: header, latest message, and suggested response
            truncated_message = (
                f"📧 NEW EMAIL - APPROVAL NEEDED\n\n"
                f"From: {from_email}\n"
                f"Subject: {subject}\n"
                f"{'🔄 Thread: ' + str(thread_count) + ' messages (full history truncated)' if thread_count > 1 else ''}\n\n"
                f"--- LATEST CUSTOMER MESSAGE ---\n"
                f"{body}\n\n"
                f"--- SUGGESTED RESPONSE ---\n"
                f"{draft}\n\n"
                f"---"
            )
            message = truncated_message[:4000] + "...\n[Message truncated]"

        # Build buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve:{approval_id}"),
                InlineKeyboardButton("✏️ Edit", callback_data=f"edit:{approval_id}"),
            ],
            [
                InlineKeyboardButton("📖 Just Read", callback_data=f"mark_read:{approval_id}"),
                InlineKeyboardButton("🚩 Flag", callback_data=f"flag:{approval_id}"),
            ],
            [
                InlineKeyboardButton("❌ Reject", callback_data=f"reject:{approval_id}"),
            ]
        ]

        try:
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            print(f"📤 Sent approval request: {approval_id}")
            return approval_id
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return None

    async def send_alert(self, message: str):
        """Send a simple alert message (no approval needed)"""
        if not self.app or not self.chat_id:
            return

        try:
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=f"🔔 {message}"
            )
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")

    async def send_flagged_email(self, email_data: Dict, reason: str = "Needs attention"):
        """Send a flagged email notification (no auto-response generated)"""
        if not self.app or not self.chat_id:
            return

        from_email = email_data.get('from_email', 'Unknown')
        subject = email_data.get('subject', 'No subject')
        body = email_data.get('body', '')[:800]
        thread_count = email_data.get('thread_count', 1)

        # Build conversation history section if this is a thread
        conversation_section = ""
        if thread_count > 1:
            thread_messages = email_data.get('thread_messages', [])
            conversation_section = f"\n📜 FULL CONVERSATION ({thread_count} messages):\n"
            for i, msg in enumerate(thread_messages, 1):
                msg_from = msg.get('from_email', 'Unknown')
                msg_date = msg.get('date', '')
                msg_body = msg.get('body', '')[:400]

                if 'ineedhemp.com' in msg_from.lower():
                    sender_label = "💬 [YOU]"
                else:
                    sender_label = "👤 [CUSTOMER]"

                conversation_section += f"\n{sender_label} ({msg_date[:20]}...)\n{msg_body}\n"
                if i < len(thread_messages):
                    conversation_section += "---\n"

            conversation_section += "\n" + "="*30 + "\n"

        message = (
            f"🚨 FLAGGED EMAIL - MANUAL RESPONSE NEEDED\n\n"
            f"Reason: {reason}\n\n"
            f"From: {from_email}\n"
            f"Subject: {subject}\n"
            f"{'🔄 Thread: ' + str(thread_count) + ' messages' if thread_count > 1 else ''}\n"
            f"{conversation_section}"
            f"\n--- LATEST MESSAGE ---\n"
            f"{body}\n\n"
            f"---\n\n"
            f"Please respond manually in Gmail."
        )

        # Telegram has 4096 char limit - truncate if needed
        if len(message) > 4000:
            truncated_message = (
                f"🚨 FLAGGED EMAIL - MANUAL RESPONSE NEEDED\n\n"
                f"Reason: {reason}\n\n"
                f"From: {from_email}\n"
                f"Subject: {subject}\n"
                f"{'🔄 Thread: ' + str(thread_count) + ' messages (truncated)' if thread_count > 1 else ''}\n\n"
                f"--- LATEST MESSAGE ---\n"
                f"{body}\n\n"
                f"---\n\n"
                f"Please respond manually in Gmail."
            )
            message = truncated_message[:4000] + "...\n[Message truncated]"

        try:
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )
        except Exception as e:
            print(f"❌ Failed to send flagged email alert: {e}")

    def run_polling(self):
        """Start the bot in polling mode (blocking)"""
        if self.app:
            print("🤖 Starting Telegram bot...")
            self.app.run_polling()

    async def start_webhook(self, webhook_url: str, port: int = 8443):
        """Start the bot with webhook (for production)"""
        if self.app:
            await self.app.bot.set_webhook(webhook_url)
            # Webhook handling would go here
            pass


# Quick test
if __name__ == "__main__":
    approval = TelegramApproval()

    if approval.app:
        # Test sending an approval
        async def test():
            test_email = {
                'id': 'test123',
                'from_email': 'customer@test.com',
                'subject': 'Where is my order #5678?',
                'body': 'Hi, I ordered a Core XL last week and haven\'t received any shipping info. Can you help?',
                'draft_response': 'Hi!\n\nThanks for reaching out. Let me look up your order #5678.\n\nYour order shipped yesterday via USPS Priority Mail. Here\'s your tracking number: 9400111899223456789012\n\nYou should receive it within 2-3 business days.\n\nLet me know if you have any other questions!\n\nBest,\nMatt'
            }
            await approval.send_for_approval(test_email)

        # asyncio.run(test())
        print("Run approval.run_polling() to start the bot")
    else:
        print("⚠️  Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
