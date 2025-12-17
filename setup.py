#!/usr/bin/env python3
"""
Divine Tribe Email Assistant - Setup Script
Run this first to test connections and set up Gmail
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔧 DIVINE TRIBE EMAIL ASSISTANT - SETUP")
print("=" * 60)

# Check for .env file
if not os.path.exists('.env'):
    print("\n⚠️  No .env file found!")
    print("   Copy .env.example to .env and fill in your values:")
    print("   cp .env.example .env")
    sys.exit(1)

# Check required environment variables
required_vars = [
    ('WOOCOMMERCE_KEY', 'WooCommerce API'),
    ('WOOCOMMERCE_SECRET', 'WooCommerce API'),
    ('TELEGRAM_BOT_TOKEN', 'Telegram Bot'),
    ('TELEGRAM_CHAT_ID', 'Telegram Chat'),
    ('ANTHROPIC_API_KEY', 'Claude AI'),
]

missing = []
for var, name in required_vars:
    value = os.getenv(var, '')
    if not value or value.startswith('your_') or value.startswith('ck_your') or value.startswith('cs_your'):
        missing.append(f"  - {var} ({name})")

if missing:
    print("\n⚠️  Missing or placeholder values in .env:")
    for m in missing:
        print(m)
    print("\nFill these in before running the assistant.")

# Test WooCommerce
print("\n" + "=" * 40)
print("📦 Testing WooCommerce Connection...")
print("=" * 40)

try:
    from woo_client import WooCommerceClient
    woo = WooCommerceClient()
    if woo.test_connection():
        orders = woo.get_recent_orders(3)
        print(f"   Recent orders: {len(orders)}")
        for o in orders:
            print(f"   - #{o.get('id')} ({o.get('status')}) - ${o.get('total')}")
except Exception as e:
    print(f"❌ WooCommerce error: {e}")

# Test Gmail
print("\n" + "=" * 40)
print("📧 Testing Gmail Connection...")
print("=" * 40)

if not os.path.exists('credentials.json'):
    print("⚠️  No credentials.json found!")
    print("\nTo set up Gmail API:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project (or select existing)")
    print("3. Enable 'Gmail API'")
    print("4. Create OAuth 2.0 credentials (Desktop app)")
    print("5. Download as 'credentials.json'")
    print("6. Place in this folder")
else:
    try:
        from gmail_client import GmailClient
        gmail = GmailClient()
        if gmail.test_connection():
            gmail.setup_labels()
            emails = gmail.get_unread_emails(3)
            print(f"   Unread emails: {len(emails)}")
    except Exception as e:
        print(f"❌ Gmail error: {e}")
        print("   You may need to re-authenticate")

# Test Telegram
print("\n" + "=" * 40)
print("🤖 Testing Telegram Bot...")
print("=" * 40)

telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
telegram_chat = os.getenv('TELEGRAM_CHAT_ID', '')

if not telegram_token or telegram_token.startswith('your_'):
    print("⚠️  Telegram bot token not set")
    print("\nTo set up Telegram:")
    print("1. Message @BotFather on Telegram")
    print("2. Send /newbot and follow prompts")
    print("3. Copy the bot token to .env")
    print("4. Message your new bot")
    print("5. Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates")
    print("6. Find your chat_id in the response")
else:
    if not telegram_chat or telegram_chat.startswith('your_'):
        print("⚠️  Telegram chat ID not set")
        print(f"\nVisit: https://api.telegram.org/bot{telegram_token}/getUpdates")
        print("Send a message to your bot first, then check the URL for chat_id")
    else:
        print("✅ Telegram configured")
        print(f"   Bot token: {telegram_token[:10]}...")
        print(f"   Chat ID: {telegram_chat}")

# Summary
print("\n" + "=" * 60)
print("📋 SETUP SUMMARY")
print("=" * 60)
print("""
Next steps:

1. Fill in all values in .env file
2. Set up Gmail API credentials (credentials.json)
3. Set up Telegram bot (@BotFather)
4. Run: python email_assistant.py

The assistant will:
- Check Gmail for new emails every 60 seconds
- Generate response drafts using Claude AI
- Send drafts to you via Telegram for approval
- Only send emails YOU approve

First month: ALL emails require your approval
After training: Can enable auto-responses for simple queries
""")
