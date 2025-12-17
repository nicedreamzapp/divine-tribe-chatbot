import os
import asyncio
import json
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SESSIONS_FILE = 'shared_sessions.json'

# Track if human mode is ON or OFF
human_mode_active = True

def load_sessions():
    """Load pending sessions from file"""
    try:
        with open(SESSIONS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_sessions(sessions):
    """Save pending sessions to file"""
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)

class TelegramHandler:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID
        
    async def send_alert(self, customer_query, session_id):
        """Send customer question to you via Telegram"""
        try:
            message = f"🔔 NEW CUSTOMER QUESTION\n\n"
            message += f"❓ Question: {customer_query}\n\n"
            message += f"📱 Session: {session_id}\n\n"
            message += f"💬 Reply to this message to answer the customer!"
            
            sent_message = await self.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )
            
            # Store the session ID in shared file
            sessions = load_sessions()
            sessions[str(sent_message.message_id)] = {
                'session_id': session_id,
                'query': customer_query,
                'timestamp': datetime.now().isoformat()
            }
            save_sessions(sessions)
            
            return True
        except TelegramError as e:
            print(f"Error sending Telegram alert: {e}")
            return False
    
    async def toggle_human_mode(self, mode: bool):
        """Turn human mode ON or OFF"""
        global human_mode_active
        human_mode_active = mode
        status = "ON ✅" if mode else "OFF ❌"
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=f"Human Mode is now {status}"
        )

def is_human_mode_active():
    """Check if you're available to answer"""
    return human_mode_active

if __name__ == "__main__":
    print("Telegram Handler Ready!")
    handler = TelegramHandler()
    print(f"Bot will send alerts to Chat ID: {TELEGRAM_CHAT_ID}")
