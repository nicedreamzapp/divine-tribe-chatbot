# Divine Tribe AI

> **Customer support that learns. Email + Chat powered by shared intelligence.**

[![Claude](https://img.shields.io/badge/AI-Claude%203.5-blueviolet)]()
[![RAG](https://img.shields.io/badge/RAG-Hybrid%205--Signal-green)]()
[![CAG](https://img.shields.io/badge/CAG-Cached%20Answers-orange)]()
[![FLUX](https://img.shields.io/badge/Images-FLUX%20Local-red)]()

---

## The Journey

```
v1  Mistral 7B Local    Fast but context-limited, couldn't hold conversations
         |
         v
v2  Claude API          Smarter reasoning, 200k token context, better understanding
         |
         v
v3  Hybrid RAG/CAG      Instant cached answers + semantic product search
         |
         v
v4  Dual System         Email + Chat sharing one brain  <-- YOU ARE HERE
```

### Why We Switched from Mistral

Started with **Mistral 7B** running locally - fast responses, no API costs. But limitations became clear:

- **4k token context** - couldn't remember conversation history
- **Struggled with nuance** - missed product recommendations
- **No chain-of-thought** - gave wrong answers confidently
- **Hallucinated products** - made up features that didn't exist

Moved to **Claude 3.5 Haiku** - the sweet spot of speed and intelligence:

- **200k token context** - remembers entire conversation threads
- **Better reasoning** - understands "I want something for concentrates under $150"
- **Honest uncertainty** - says "I'm not sure" instead of making things up
- **Follows instructions** - respects our tone, policies, and routing rules

---

## Architecture

```
         +------------------+     +------------------+
         |   EMAIL INBOX    |     |  CHAT WIDGET     |
         |   Gmail API      |     |  Web / Telegram  |
         +--------+---------+     +--------+---------+
                  |                        |
                  +----------+-------------+
                             |
                             v
                  +----------+-------------+
                  |     AGENT ROUTER       |
                  |  Intent Classification |
                  +----------+-------------+
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
  +------+------+    +-------+-------+   +------+------+
  |  CAG CACHE  |    |  RAG SEARCH   |   | IMAGE GEN   |
  | Pre-cached  |    | 5-Signal      |   | FLUX Local  |
  | Answers     |    | Hybrid        |   | Unfiltered  |
  +------+------+    +-------+-------+   +------+------+
         |                   |                   |
         +-------------------+-------------------+
                             |
                             v
                  +----------+-------------+
                  |      CLAUDE 3.5        |
                  |   Response Generation  |
                  +----------+-------------+
                             |
                             v
                  +----------+-------------+
                  |    LEARN & IMPROVE     |
                  |  Approved = Training   |
                  +------------------------+
```

---

## The Intelligence Stack

### 1. CAG Cache (Cached Augmented Generation)

Pre-built answers for common questions - **instant responses, zero API calls**:

```python
# Quick Answers (immediate)
- Discount codes: "thankyou10 for 10% off"
- International shipping: "Yes, we ship to Canada, UK, Europe, Australia..."
- Terminology: "A spacer keeps the heater from touching the housing"
- V5 settings: "TCR 180-200, 480°F, 38W max"
- Core heat levels: All 6 color settings with temps

# Product Comparisons
- V5 vs V5 XL: "XL has longer top piece, 30% bigger cup"
- Core vs V5: "Core = easy all-in-one, V5 = more control"
- Core vs Fogger: "Core = simple, Fogger = forced air"

# Troubleshooting (Reddit-proven solutions)
- "Check Atomizer" error → Tighten 510 pin
- Resistance jumping → Clean threads
- Leaking → Load less, lower temp
- No vapor → Check wattage and battery

# Customer Service Templates
- Damaged items → Photo + order number process
- Wrong items → Quick resolution flow
- Missing items → Verification steps
```

### 2. RAG Retriever (Retrieval Augmented Generation)

**5-signal hybrid retrieval** - not just keyword matching:

```python
RETRIEVAL_SIGNALS = {
    'keyword_index':    # Auto-built from ALL product names (jars, shirts, hoodies, etc.)
    'semantic_search':  # Vector embeddings - meaning-based similarity (0.4 weight)
    'lexical_search':   # Exact text matching with singular/plural expansion (0.3 weight)
    'priority_boost':   # Main kits ranked higher than accessories (0.2 weight)
    'business_rules':   # XL before regular V5, Core XL before older models (0.1 weight)
}
```

**Smart category detection:**
- "jars" → UV glass storage products
- "hoodies" → Hemp clothing category
- "bubblers" → Also matches "hydratube", "water attachment" (synonyms)
- "v5" → Defaults to XL (the recommended version)

**Replacement parts filtering:**
- Searches return main products by default
- Accessories only show when specifically asked

### 3. FLUX Image Generation (Local + Unfiltered)

**No cloud APIs. No content filters. Your hardware, your rules.**

```python
# Local ComfyUI Integration
SERVER = "127.0.0.1:8188"
MODEL = "flux1-schnell.safetensors"
CLIP = ["clip_l.safetensors", "t5xxl_fp16.safetensors"]
VAE = "ae.safetensors"
LORA = "flux-realism-xlabs.safetensors"

# Output
RESOLUTION = 1024x1024
STEPS = 4  # Fast generation
SAMPLER = "euler"
```

**Why local matters:**
- No "this content violates our policies" rejections
- No per-image API costs
- Full creative control
- Generated images auto-deleted after encoding (privacy)

**Content moderation** (we handle it ourselves):
- Inappropriate requests get playful redirects
- "Maybe check out a V5 XL to relax instead?"
- No hard blocks - just guidance back to products

### 4. Agent Router (Intent Classification)

Every query gets classified before processing:

```
Query: "where's my order #123456"
  → Route: order_inquiry
  → Action: WooCommerce lookup + status response

Query: "v5 not heating"
  → Route: troubleshooting
  → Action: CAG cache → Reddit-proven solutions

Query: "best vape for concentrates"
  → Route: rag_search
  → Action: Product search → Prioritize Core XL, V5 XL

Query: "draw me a sunset"
  → Route: image_request
  → Action: Redirect to image generator

Query: "tell me a joke"
  → Route: general_mistral
  → Action: Claude handles general chat
```

**Competitor handling:**
- Mentions of Puffco, Storz & Bickel, PAX, etc.
- Neutral response, redirect to Divine Tribe strengths
- "I focus on Divine Tribe products..."

---

## Data Pipeline

### Product Data (`products_clean.json`)

**465KB of product knowledge** - scraped from ineedhemp.com:

```json
{
  "name": "XL Deluxe Core eRig Kit- Now with 6 Heat Settings",
  "url": "https://ineedhemp.com/product/xl-deluxe-core-erig",
  "description": "All-in-one concentrate vaporizer...",
  "category": "vaporizers",
  "price": "165-185"
}
```

Categories include:
- Vaporizers (Core, V5, Ruby Twist, Fogger)
- Atomizers & Heaters
- Hemp Clothing (shirts, hoodies, boxers, pants)
- Glass Jars (UV and clear)
- Bubblers/Hydratubes
- Accessories & Replacement Parts

### Embeddings (`product_embeddings.pkl`)

**683KB of vector embeddings** - pre-computed for semantic search:

```python
# Using sentence-transformers
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(product_descriptions)
```

Enables queries like:
- "something for beginners" → Core XL Deluxe
- "best flavor device" → V5 XL
- "portable concentrate vape" → Multiple options ranked

### YouTube Knowledge (`youtube_knowledge.json`)

Extracted from Matt's tutorial videos:
- V5 settings walkthrough
- Pico Plus setup guide
- Cleaning instructions
- TCR dialing tips

---

## Two Apps, One Brain

| Feature | Email Assistant | Chatbot |
|---------|----------------|---------|
| **Input** | Gmail inbox | Web widget / Telegram |
| **Output** | Draft → Human approves → Send | Instant response |
| **Speed** | Batch processing | Real-time |
| **Learning** | Approved responses train system | Conversations improve RAG |
| **Order Lookup** | WooCommerce API | WooCommerce API |
| **Images** | N/A | FLUX generation |

**Shared Components:**
- RAG retriever (same product search)
- CAG cache (same instant answers)
- WooCommerce client (same order data)
- Claude prompts (same tone/rules)

---

## Email Workflow (Human-in-Loop)

```
1. Email arrives in Gmail
         |
         v
2. Bot classifies intent
   - Order status?
   - Product question?
   - Return request?
   - Needs escalation?
         |
         v
3. Bot gathers context
   - CAG: Check for cached answer
   - RAG: Search relevant products
   - WOO: Look up order if needed
         |
         v
4. Claude generates draft
         |
         v
5. Draft sent to Matt (web dashboard)
   [APPROVE] [EDIT] [FLAG]
         |
         v
6. Only approved emails get sent
         |
         v
7. Approved = Training signal
   - Response logged for learning
   - Similar future emails handled faster
```

**Auto-Read Training:**
- Mark generic emails (shipping notifications, order confirmations) as "just read"
- System learns patterns
- Future similar emails auto-marked

---

## Project Structure

```
Divine Tribe Email Assistant/
├── modules/                 # SHARED INTELLIGENCE
│   ├── agent_router.py      # Query classification
│   ├── cag_cache.py         # Cached answers (43KB of knowledge)
│   ├── rag_retriever.py     # 5-signal hybrid search
│   ├── image_generator.py   # FLUX via ComfyUI
│   ├── vector_store.py      # Embedding search
│   ├── product_database.py  # Product lookup
│   ├── context_manager.py   # Session tracking
│   ├── conversation_memory.py
│   ├── conversation_logger.py
│   ├── intent_classifier.py
│   └── query_preprocessor.py
│
├── data/                    # KNOWLEDGE BASE
│   ├── products_clean.json  # All products (465KB)
│   ├── product_embeddings.pkl # Vector embeddings (683KB)
│   ├── youtube_knowledge.json # Tutorial content
│   └── conversation_logs/   # Learning data
│
├── email/                   # EMAIL APP
│   ├── web_dashboard.py     # Flask dashboard
│   ├── smart_responder.py   # Response generation
│   ├── gmail_client.py      # Gmail API
│   ├── woo_client.py        # WooCommerce API
│   └── training.py          # Auto-read training
│
├── chatbot/                 # CHAT APP
│   └── [chat implementation]
│
├── templates/web/           # Dashboard UI
│   └── inbox.html
│
├── credentials/             # Git-ignored
│   └── [API keys]
│
└── .env                     # Config (git-ignored)
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| AI Brain | Claude 3.5 Haiku |
| RAG Search | Sentence Transformers + Custom Hybrid |
| CAG Cache | Python dictionaries (43KB pre-built) |
| Image Gen | FLUX via ComfyUI (local) |
| Email | Gmail API |
| Orders | WooCommerce REST API |
| Dashboard | Flask |
| Process Mgmt | PM2 |
| Hosting | VPS (Ubuntu) |

---

## Key Features

- **Shared Learning** - Email & chat feed the same AI brain
- **Human-in-Loop** - All emails require approval (for now)
- **5-Signal RAG** - Semantic + lexical + keyword + priority + business rules
- **CAG Cache** - 100+ pre-built answers for instant response
- **WooCommerce Live** - Real order status, no stale data
- **FLUX Local** - Unfiltered image generation on your hardware
- **Auto-Read Training** - Learns what emails to skip
- **Content Moderation** - Playful redirects instead of hard blocks
- **Competitor Neutral** - Doesn't trash-talk, just redirects

---

## Community

- **Discord:** https://discord.com/invite/f3qwvp56be
- **Reddit:** https://www.reddit.com/r/DivineTribeVaporizers/
- **YouTube:** https://www.youtube.com/@divinetribe1
- **Shop:** https://ineedhemp.com
- **Email:** matt@ineedhemp.com

---

## Remember

> **When in doubt, flag for human review. Never send without approval.**

---

*Built for [Divine Tribe](https://ineedhemp.com) by Matt Macosko*
