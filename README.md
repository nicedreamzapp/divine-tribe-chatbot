# Divine Tribe AI Assistant

Hybrid AI system powering **customer support emails** and **live chat** for [Divine Tribe](https://ineedhemp.com).

## Evolution

Started with **Mistral 7B** for local inference - fast but limited context and reasoning. Switched to **Claude** for:
- Better understanding of complex customer questions
- Longer context for email threads
- More accurate product recommendations
- Smarter conversation memory

The hybrid RAG/CAG architecture remained - just upgraded the brain.

## What It Does

| App | Purpose |
|-----|---------|
| **Email Assistant** | Reads Gmail, drafts responses, human approves before sending |
| **Chatbot** | Live chat widget + Telegram bot for instant support |

Both apps share the same intelligence - every conversation makes the system smarter.

## How It Works

```
Customer Question (Email or Chat)
              ↓
     ┌────────────────┐
     │  Check Cache   │  ← Instant answers to common questions
     └────────────────┘
              ↓
     ┌────────────────┐
     │  Search RAG    │  ← Find relevant products & knowledge
     └────────────────┘
              ↓
     ┌────────────────┐
     │  Order Lookup  │  ← WooCommerce integration
     └────────────────┘
              ↓
     ┌────────────────┐
     │   Claude AI    │  ← Generate helpful response
     └────────────────┘
              ↓
     Human Review (email) / Direct Send (chat)
              ↓
     ┌────────────────┐
     │  Learn & Save  │  ← Good responses improve the system
     └────────────────┘
```

## Intelligence System

### RAG (Retrieval Augmented Generation)
Searches product database using semantic embeddings. Finds relevant products, specs, and knowledge to ground AI responses in real data.

### CAG (Cached Augmented Generation)
Caches approved responses to common questions. Provides instant answers without API calls. Grows smarter from every approved email.

### Shared Learning
- Conversation logs from both email and chat
- Approved responses train the cache
- Customer patterns improve over time

## Features

- **Human-in-the-loop** - All emails require approval
- **Customer verification** - Order lookups require verification
- **Auto-read training** - Learn which emails need no response
- **Order integration** - Live WooCommerce data
- **Multi-channel** - Email, web chat, Telegram

## Project Structure

```
├── modules/          # Shared AI modules (RAG, CAG, etc.)
├── data/             # Product data & knowledge base
├── chatbot/          # Chat application
├── email/            # Email application
└── templates/        # Response templates
```

## Tech

- Python / Flask
- Claude AI (Anthropic)
- Gmail API
- WooCommerce API
- Sentence Transformers

---

*Customer support AI for Divine Tribe*
