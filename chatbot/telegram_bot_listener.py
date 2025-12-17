import os
import asyncio
import json
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SESSIONS_FILE = 'shared_sessions.json'

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

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When you reply in Telegram, this captures it and logs it"""
    user_id = str(update.effective_user.id)
    
    # Only accept replies from YOU
    if user_id != TELEGRAM_CHAT_ID:
        return
    
    your_reply = update.message.text
    
    # Check if this is a reply to a customer question
    if update.message.reply_to_message:
        original_message_id = str(update.message.reply_to_message.message_id)
        
        # Load sessions from file
        sessions = load_sessions()
        
        if original_message_id in sessions:
            session_info = sessions[original_message_id]
            
            # Log your reply for training (customer will see it as bot response)
            try:
                import requests
                response = requests.post('http://localhost:5001/human_response', json={
                    'session_id': session_info['session_id'],
                    'reply': your_reply,
                    'query': session_info['query']
                })
                
                if response.status_code == 200:
                    await update.message.reply_text(
                        f"✅ Response logged for training!\n\n"
                        f"Customer asked: {session_info['query']}\n\n"
                        f"Your answer: {your_reply}\n\n"
                        f"💡 This will train the bot to answer similar questions when you're offline."
                    )
                else:
                    await update.message.reply_text("⚠️ Couldn't log response.")
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}")
            
            # Remove from pending and save
            del sessions[original_message_id]
            save_sessions(sessions)
        else:
            await update.message.reply_text("⚠️ This customer session has expired or was already answered.")
    else:
        await update.message.reply_text("ℹ️ Please reply to a customer question to send your answer.")

async def toggle_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle human mode ON/OFF with /toggle command"""
    global human_mode_active
    human_mode_active = not human_mode_active
    status = "ON ✅" if human_mode_active else "OFF ❌"
    
    if human_mode_active:
        message = f"🟢 Human Mode: {status}\n\nYou'll get notifications for ALL customer questions.\nYou answer everything!"
    else:
        message = f"🔴 Human Mode: {status}\n\nBot is handling all questions automatically.\nGet some rest! 😴"
    
    await update.message.reply_text(message)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check status with /status command"""
    status = "ON ✅" if human_mode_active else "OFF ❌"
    sessions = load_sessions()
    pending_count = len(sessions)
    
    mode_description = "You're answering questions" if human_mode_active else "Bot is auto-responding"
    
    await update.message.reply_text(
        f"🤖 Bot Status\n\n"
        f"Human Mode: {status}\n"
        f"Mode: {mode_description}\n"
        f"Pending Responses: {pending_count}\n\n"
        f"Use /toggle to switch modes"
    )

def main():
    """Start the Telegram bot listener"""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("toggle", toggle_mode))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply))
    
    print("🤖 Telegram bot listener started!")
    print("Commands:")
    print("  /toggle - Turn human mode ON/OFF")
    print("  /status - Check current status")
    print("\n💡 When Human Mode is ON:")
    print("   - You get Telegram alerts for customer questions")
    print("   - You reply, and it looks like the bot to customers")
    print("   - Your answers get logged for bot training")
    
    # Run the bot
    app.run_polling()

if __name__ == "__main__":
    main()
