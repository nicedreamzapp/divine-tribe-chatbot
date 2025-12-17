#!/usr/bin/env python3
"""
Divine Tribe Discord Support Bot
Answers product questions, checks orders, provides troubleshooting help
"""

import discord
from discord.ext import commands
import asyncio
import os
import sys
import logging
import re

# Add directories to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.join(script_dir, 'chatbot'))

# Import the chatbot modules
from modules.agent_router import AgentRouter
from modules.order_verify import handle_order_inquiry, get_safe_order_info, format_order_response
from modules.cag_cache import CAGCache
from modules.product_database import ProductDatabase
from modules.conversation_logger import ConversationLogger

# Try to import context manager
try:
    from modules.context_manager import ContextManager
    context_manager = ContextManager()
except ImportError:
    context_manager = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TribeSupportBot')

# =============================================================================
# CONFIGURATION
# =============================================================================

# Discord Bot Token (from environment variable)
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Channel ID where bot should respond
SUPPORT_CHANNEL_ID = 1450732212843450452

# =============================================================================
# BOT SETUP
# =============================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!tribe ', intents=intents)

# Initialize the chatbot components
print("Loading product database...")
database = ProductDatabase('data/products_clean.json')
print(f"✅ Loaded {len(database.products)} products")

print("Loading CAG cache...")
cag_cache = CAGCache()

print("Initializing agent router...")
router = AgentRouter(cag_cache, database, context_manager)
print("✅ Agent router ready")

print("Initializing conversation logger...")
conversation_logger = ConversationLogger(log_dir='conversation_logs')
print("✅ Conversation logger ready (Discord chats will be saved)")

# Store pending order verifications per user
pending_verifications = {}  # user_id -> challenge dict

# =============================================================================
# HELPERS
# =============================================================================

def create_embed(title, description, color=0x00AA00):
    """Create a Discord embed with Divine Tribe branding"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    embed.set_footer(text="Divine Tribe Support Bot | divinetribe.com")
    return embed

def format_for_discord(text):
    """Convert any HTML to Discord markdown"""
    # Convert <strong> to **bold**
    text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text)
    # Convert <a href="url" target="_blank">text</a> to [text](url)
    text = re.sub(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', r'[\2](\1)', text)
    # Remove any other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text

# =============================================================================
# EVENT HANDLERS
# =============================================================================

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Support channel ID: {SUPPORT_CHANNEL_ID or "Any channel (when mentioned)"}')

    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="your questions | !tribe tribehelp"
        )
    )

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if we should respond
    should_respond = False
    query = message.content

    # Always respond if mentioned
    if bot.user.mentioned_in(message):
        should_respond = True
        # Remove the mention from the query
        query = re.sub(r'<@!?\d+>', '', query).strip()

    # Respond in support channel without needing mention
    elif SUPPORT_CHANNEL_ID and message.channel.id == SUPPORT_CHANNEL_ID:
        should_respond = True

    # Check for !tribe prefix
    elif message.content.startswith('!tribe '):
        should_respond = True
        query = message.content[7:].strip()  # Remove "!tribe "

    if not should_respond or not query:
        await bot.process_commands(message)
        return

    # Process the query
    try:
        response, is_order_related = await process_query(message.author.id, query)

        # Format for Discord
        response = format_for_discord(response)

        # If order-related, handle privately
        if is_order_related:
            try:
                # Delete the original message to protect privacy
                await message.delete()
            except discord.Forbidden:
                pass  # Bot doesn't have permission to delete

            try:
                # Send response via DM
                dm_channel = await message.author.create_dm()

                privacy_note = "🔒 **Your order info is private - only you can see this!**\n\n"
                full_response = privacy_note + response

                if len(full_response) > 2000:
                    chunks = [full_response[i:i+1900] for i in range(0, len(full_response), 1900)]
                    for chunk in chunks:
                        await dm_channel.send(chunk)
                else:
                    await dm_channel.send(full_response)

                # Post a brief note in the channel
                await message.channel.send(f"📬 {message.author.mention} Check your DMs for your order info! (kept private for your security)")

            except discord.Forbidden:
                # Can't DM user, reply in channel with warning
                await message.channel.send(f"{message.author.mention} I couldn't DM you. Please enable DMs from server members, then try again. (This keeps your order info private!)")
        else:
            # Regular response in channel
            if len(response) > 2000:
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                for chunk in chunks:
                    await message.reply(chunk)
            else:
                await message.reply(response)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        try:
            await message.reply("Sorry, I ran into an error. Please try again or contact matt@ineedhemp.com for help.")
        except:
            pass

    await bot.process_commands(message)

async def process_query(user_id, query, username="discord_user"):
    """
    Process a user query through the agent router.
    Returns (response, is_order_related) tuple.
    Logs all conversations for learning/improvement.
    """

    # Build context with any pending verification
    context = {}
    is_order_related = False

    if user_id in pending_verifications:
        context['pending_challenge'] = pending_verifications[user_id]
        context['pending_order_number'] = pending_verifications[user_id].get('order_number')
        is_order_related = True  # If we have pending verification, it's order-related

    # Route the query
    result = router.route(query, context)
    route = result.get('route', 'general')

    # Handle order verification flow
    if route == 'order':
        response = result.get('data', '')
        is_order_related = True  # Order route is always private

        # Store challenge for next message if verification needed
        if result.get('challenge'):
            pending_verifications[user_id] = result['challenge']
        elif result.get('pending_challenge'):
            pending_verifications[user_id] = result['pending_challenge']
        elif result.get('verified'):
            # Clear pending verification on success
            if user_id in pending_verifications:
                del pending_verifications[user_id]

        return response, is_order_related

    # Handle image requests - redirect to website (Discord doesn't have image gen)
    if route == 'image_request':
        response = "🎨 **Want to generate AI images?**\n\nImage generation is available on our website chatbot!\n\n👉 Visit **https://ineedhemp.com** and use the chat widget to create custom AI artwork.\n\nIs there anything else I can help you with here?"
        return response, False

    # For other routes, just return the response (not private)
    response = result.get('data', "I'm not sure how to help with that. Try asking about Divine Tribe products, order status, or troubleshooting!")

    # Log conversation for learning (but not order details for privacy)
    try:
        session_id = f"discord_{user_id}"
        # Don't log actual order data, just that it was an order query
        log_response = "[ORDER INFO REDACTED]" if is_order_related else response
        conversation_logger.log_conversation(
            session_id=session_id,
            user_message=query,
            bot_response=log_response,
            products_shown=[],
            intent=route,
            confidence=1.0
        )
    except Exception as e:
        logger.warning(f"Failed to log conversation: {e}")

    return response, is_order_related

# =============================================================================
# COMMANDS
# =============================================================================

@bot.command(name='tribehelp')
async def help_command(ctx):
    """Show help information"""
    embed = create_embed(
        "Divine Tribe Support Bot",
        "I'm here to help with all your Divine Tribe questions!",
        color=0x00AA00
    )

    embed.add_field(
        name="What I can do",
        value=(
            "**Order Status** - Check your order status and tracking\n"
            "**Product Questions** - Info about our devices\n"
            "**Troubleshooting** - Help with device issues\n"
            "**Settings** - Temperature, wattage, modes\n"
        ),
        inline=False
    )

    embed.add_field(
        name="How to use me",
        value=(
            "Just ask your question! You can:\n"
            "• Mention me: @Tribe Support Bot where's my order?\n"
            "• Use command: `!tribe order 199337`\n"
            "• Or just type in this channel!\n"
        ),
        inline=False
    )

    embed.add_field(
        name="Order Lookup",
        value=(
            "To check your order, just tell me your order number.\n"
            "I'll ask you to verify with your zip code, email, or last name for security."
        ),
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name='order')
async def order_command(ctx, order_number: str = None):
    """Check order status - handled privately via DM"""
    if not order_number:
        await ctx.reply("Please provide your order number. Example: `!tribe order 199337`")
        return

    async with ctx.channel.typing():
        response, _ = await process_query(ctx.author.id, f"order {order_number}")
        response = format_for_discord(response)

        # Delete original message and send via DM for privacy
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        try:
            dm_channel = await ctx.author.create_dm()
            privacy_note = "🔒 **Your order info is private - only you can see this!**\n\n"
            await dm_channel.send(privacy_note + response)
            await ctx.channel.send(f"📬 {ctx.author.mention} Check your DMs for your order info! (kept private for your security)")
        except discord.Forbidden:
            await ctx.channel.send(f"{ctx.author.mention} I couldn't DM you. Please enable DMs from server members, then try again.")

@bot.command(name='products')
async def products_command(ctx):
    """Show product info"""
    embed = create_embed(
        "Divine Tribe Products",
        "Here are our main product lines:",
        color=0x00AA00
    )

    embed.add_field(
        name="V5.5 (V5 Gen 2)",
        value="Our flagship concentrate atomizer with titanium, quartz, and SiC cups",
        inline=False
    )

    embed.add_field(
        name="Core 2.0",
        value="E-rig with app control and precise temperature",
        inline=False
    )

    embed.add_field(
        name="V4.5",
        value="Classic crucible atomizer, great for beginners",
        inline=False
    )

    embed.add_field(
        name="More Info",
        value="Ask me about any product for detailed specs and settings!",
        inline=False
    )

    await ctx.send(embed=embed)

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    if DISCORD_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("=" * 50)
        print("SETUP REQUIRED")
        print("=" * 50)
        print("\n1. Go to https://discord.com/developers/applications")
        print("2. Click 'New Application' and name it 'Tribe Support Bot'")
        print("3. Go to 'Bot' section and click 'Add Bot'")
        print("4. Copy the token and set it as DISCORD_CHATBOT_TOKEN")
        print("5. Enable 'Message Content Intent' in Bot settings")
        print("6. Go to OAuth2 > URL Generator")
        print("   - Select 'bot' scope")
        print("   - Select permissions: Send Messages, Read Messages, Embed Links")
        print("7. Use the generated URL to invite bot to your server")
        print("\nThen run this script again!")
        print("=" * 50)
    else:
        logger.info("Starting Divine Tribe Support Bot...")
        bot.run(DISCORD_BOT_TOKEN)
