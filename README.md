# 🤖 Divine Tribe AI Chatbot

Product recommendation chatbot with RAG search, cached answers, and AI image generation.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

## What It Does

- **Smart Product Recommendations** - Natural language product search with semantic understanding
- **AI Image Generation** - Custom artwork with FLUX/ComfyUI (60-90 seconds)
- **Instant Cached Answers** - Common questions answered in <0.1s
- **Conversational Memory** - Remembers context across conversation
- **RLHF Ready** - Logs all conversations for training

**Live:** https://chat.marijuanaunion.com

## Recent Updates (Nov 2025)

### ✅ Production-Ready Improvements
- **No Hallucinations** - Removed all hardcoded product data, uses only products_clean.json
- **Clean Terminology** - Uses "concentrates" and "flower" (no confusing "hash-ready" terms)
- **Better Routing** - Creative queries go to general knowledge, not troubleshooting
- **Enhanced Comparisons** - "Core vs V5" gives actual comparison, not generic response
- **Mod Compatibility** - Lists compatible mods when asked "can I use my own mod"
- **Priority Ranking** - Main kits (Core XL, V5 XL) always show first
- **XL V5 First** - When asked "what is the v5", shows XL version first (it's the upgrade)

### 🎯 Key Fixes
- Fixed: Ruby Twist no longer mentions "hash-ready" (it's for flower only)
- Fixed: "i dont know anything about vapes" now shows products instead of troubleshooting
- Fixed: Creative queries like "tell me a funny story" work naturally
- Fixed: Image generation works with proper FLUX workflow

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Ollama (Mistral local) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Search | Hybrid semantic + keyword RAG |
| Cache | CAG (Customer Answer Graph) |
| Backend | Flask + Python 3.9+ |
| Image Gen | ComfyUI + FLUX schnell |
| SSL | Nginx + Let's Encrypt |
| Hosting | VPS + SSH tunnel |

## Architecture
```
User Query
    ↓
Query Preprocessing
    ↓
Intent Classification (Enterprise Mode)
    ↓
┌─────────┬──────────┬──────────┬──────────┐
│ Cache   │ RAG      │ Image    │ General  │
│ <0.1s   │ Search   │ Gen      │ Mistral  │
│         │ Vector+  │ 60-90s   │          │
│         │ Keyword  │          │          │
└────┬────┴────┬─────┴────┬─────┴────┬─────┘
     │         │          │          │
     └─────────┴──────────┴──────────┘
              ↓
         Mistral LLM
         (Conversational Layer)
              ↓
        Response + Context
```

## Quick Start

### Prerequisites
- Python 3.9+
- Ollama with Mistral model installed
- (Optional) ComfyUI with FLUX for image generation

### Installation
```bash
git clone https://github.com/nicedreamzapp/divine-tribe-chatbot.git
cd divine-tribe-chatbot

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

**requirements.txt:**
```
flask>=3.0.0
flask-cors>=4.0.0
ollama>=0.1.0
sentence-transformers>=2.2.0
numpy>=1.24.0
markdown>=3.5.0
```

### Run Locally
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Mistral model
ollama pull mistral

# Start chatbot
python chatbot_modular.py
# Runs on http://localhost:5001
```

### Production Setup (VPS + HTTPS)

**Requirements:**
- VPS (Ubuntu 24.04+, 2GB+ RAM)
- Domain/subdomain pointed to VPS IP
- SSH access to VPS

**1. Install Nginx + Certbot on VPS**
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y
```

**2. Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/chatbot
```
```nginx
server {
    listen 80;
    server_name chat.marijuanaunion.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;  # For image generation
    }
}
```
```bash
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**3. Get SSL Certificate**
```bash
sudo certbot --nginx -d chat.marijuanaunion.com
```

**4. Permanent SSH Tunnel from Mac to VPS**

**Create service file on Mac:**
```bash
# Create launch daemon
sudo nano /Library/LaunchDaemons/com.divinetribe.chatbot.tunnel.plist
```
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.divinetribe.chatbot.tunnel</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/ssh</string>
        <string>-R</string>
        <string>0.0.0.0:5001:localhost:5001</string>
        <string>root@YOUR_VPS_IP</string>
        <string>-N</string>
        <string>-o</string>
        <string>ServerAliveInterval=60</string>
        <string>-o</string>
        <string>ServerAliveCountMax=3</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/chatbot-tunnel.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/chatbot-tunnel.error.log</string>
</dict>
</plist>
```
```bash
# Load the service
sudo launchctl load /Library/LaunchDaemons/com.divinetribe.chatbot.tunnel.plist

# Start the service
sudo launchctl start com.divinetribe.chatbot.tunnel
```

Your chatbot is now accessible at `https://chat.marijuanaunion.com` 24/7!

## Project Structure
```
divine-tribe-chatbot/
│
├── chatbot_modular.py          # Main Flask server (AI mode)
├── chatbot_with_human.py       # Human-in-loop mode
├── chatbot_launcher.command    # Quick launcher script
│
├── modules/
│   ├── agent_router.py         # Routes queries (CLEANED)
│   ├── cag_cache.py           # Cached answers (Core vs V5 added)
│   ├── context_manager.py     # Conversation context (CLEANED)
│   ├── conversation_logger.py  # RLHF logging (thread-safe)
│   ├── conversation_memory.py  # Short-term memory (CLEANED)
│   ├── image_generator.py     # ComfyUI/FLUX integration
│   ├── intent_classifier.py   # Enterprise query classification
│   ├── product_database.py    # Product search engine (CLEANED)
│   ├── query_preprocessor.py  # Query normalization
│   ├── rag_retriever.py       # Hybrid RAG search (OPTIMIZED)
│   └── vector_store.py        # Embeddings cache (OPTIMIZED)
│
├── products_clean.json         # Product catalog (143 unique products)
├── product_embeddings.pkl      # Cached embeddings (auto-generated)
└── conversation_logs/          # RLHF training data
```

## Features

### 🎯 Intelligent Product Routing

**Main Products (Prioritized):**

**For Concentrates (wax, rosin, shatter, resin):**
1. Core XL Deluxe - Easiest for beginners (all-in-one)
2. V5 XL - Best flavor, needs separate mod
3. V5 - Standard size, needs separate mod

**For Flower (dry herb):**
1. Ruby Twist - Desktop ball vape
2. Gen 2 DC - Portable

**Query Examples:**
```
"what vaporizer for a beginner"
  → Core XL Deluxe (concentrates) or Ruby Twist (flower)

"what is the v5"
  → Shows XL V5 FIRST (upgraded version), then regular V5

"core vs v5 which is better"
  → Actual comparison with pros/cons

"can i use my own mod"
  → Lists compatible mods (Pico, Aegis, etc.)
```

### ⚡ Cached Answers (CAG System)
```
Query: "what is the difference between v5 and v5 xl"
  ↓
Cache: HIT ✓
  ↓
Response: <0.1s (no LLM call, no RAG search)
```

**Cached Categories:**
- Product comparisons (V5 vs XL, Core vs V5)
- Troubleshooting (resistance issues, leaking, not heating)
- How-to guides (cleaning, settings, first-time use)
- Company info (warranty, returns, shipping, about)
- Mod compatibility

### 🧠 Conversational Memory

- Tracks products mentioned
- Remembers user preferences (beginner, flavor priority, etc.)
- Resolves follow-ups ("tell me more about it")
- Detects when user is answering bot's questions

### 🎨 AI Image Generation

- Integrated ComfyUI + FLUX schnell model
- 60-90 second generation time
- Base64 encoded for web display
- Automatic cleanup of temp files

**Example:**
```
"create an image of a monkey in the jungle"
  → Generates photorealistic image via FLUX
```

### 📊 RLHF Training Data

All conversations logged to `conversation_logs/` for:
- Performance analysis
- Fine-tuning training data
- Quality improvement

**Export for training:**
```python
from modules.conversation_logger import ConversationLogger

logger = ConversationLogger()
logger.export_for_training("training_data.jsonl")
```

## API Endpoints

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|---------------|
| `/chat` | POST | Send message, get response | 0.1s (cache) - 3s (RAG+LLM) |
| `/generate_image` | POST | Create AI artwork | 60-90s |
| `/health` | GET | Server status | <0.1s |

**Chat Example:**
```bash
curl -X POST https://chat.marijuanaunion.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "best vape for concentrates for a beginner",
    "session_id": "user_123"
  }'
```

**Response:**
```json
{
  "response": "<p>For a beginner with concentrates, I recommend the <strong><a href='...'>Core XL Deluxe</a></strong>. It's all-in-one, just charge and go...</p>",
  "status": "success",
  "route": "rag"
}
```

## Configuration

### Update Product Catalog
Edit `products_clean.json` - embeddings rebuild automatically on next startup.

**Format:**
```json
[
  {
    "name": "Product Name",
    "url": "https://ineedhemp.com/product/...",
    "description": "Product description...",
    "category": "main_products"
  }
]
```

### Add Cached Answers
Edit `modules/cag_cache.py`:
```python
self.comparisons = {
    'product_vs_product': {
        'question': 'Product A vs Product B?',
        'answer': """**Comparison:**
        
Product A: Features...
Product B: Features..."""
    }
}
```

### Customize System Prompts
Edit `chatbot_modular.py` line ~130:
```python
system_prompt = f"""You are Divine Tribe's helpful product advisor.

**YOUR TERMINOLOGY:**
- For concentrates: "concentrates" (not "hash-ready")
- For flower: "flower" or "dry herb"

..."""
```

## Testing

### Run 50-Question Test Suite
```bash
python test_chatbot_50_questions.py
```

Generates:
- `test_results_TIMESTAMP.json` - Structured data
- `test_results_TIMESTAMP.txt` - Human-readable

**Analyzes:**
- Route distribution
- Response quality
- Product recommendations accuracy

## Troubleshooting

### Issue: "Image generator offline"
**Solution:** 
1. Start ComfyUI: `cd ~/ComfyUI && python main.py`
2. Verify FLUX model in `models/unet/flux1-schnell.safetensors`
3. Check `http://localhost:8188` is accessible

### Issue: Chatbot gives generic "I'm not sure" responses
**Solution:**
1. Check `products_clean.json` exists
2. Verify Mistral model: `ollama list`
3. Check logs for routing issues

### Issue: SSH tunnel disconnects
**Solution:**
1. Use `ServerAliveInterval=60` in SSH config
2. Set up LaunchDaemon (see Production Setup above)
3. Monitor: `tail -f /tmp/chatbot-tunnel.log`

## Model Consolidation

**Problem:** Multiple ComfyUI projects duplicated 10GB+ models across disk

**Solution:** 
- Created central `~/AI_Models/` directory
- Symlinked all projects to shared models
- **Result:** Saved 66GB disk space
```bash
~/AI_Models/
├── ComfyUI/
│   ├── unet/flux1-schnell.safetensors (22GB)
│   ├── clip/t5xxl_fp16.safetensors (9.1GB)
│   ├── clip/clip_l.safetensors (235MB)
│   └── vae/ae.safetensors (320MB)
└── TTS/xtts_v2_model.pth (1.7GB)

# All projects symlink to these shared files
ln -s ~/AI_Models/ComfyUI/unet ~/ComfyUI/models/unet
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Products indexed | 143 unique items |
| Cache hit rate | ~40% of queries |
| Avg response time (cached) | <0.1s |
| Avg response time (RAG) | 1-3s |
| Avg response time (image) | 60-90s |
| Embedding dimensions | 384 (MiniLM) |
| Vector search accuracy | ~85% semantic match |

## Security Notes

**Not included in repo:**
- `telegram_handler.py` (contains bot tokens)
- `conversation_logs/` (user conversations - GDPR)
- `*.pkl` (embeddings cache - regenerates automatically)
- `venv/` (virtual environment)
- SSH keys for VPS tunnel

See `.gitignore` for full list.

## Roadmap

- [ ] Add voice input/output
- [ ] Multi-language support
- [ ] Product image search
- [ ] Fine-tuned Mistral model on Divine Tribe data
- [ ] Analytics dashboard
- [ ] A/B testing framework

## Contact

- **Website:** [ineedhemp.com](https://ineedhemp.com)
- **Live Chat:** [chat.marijuanaunion.com](https://chat.marijuanaunion.com)
- **Email:** matt@ineedhemp.com
- **Community:** 
  - Reddit: r/DivineTribeVaporizers
  - Discord: https://discord.com/invite/aC4Pv6J75s

## License

Proprietary - Divine Tribe / Nice Dreamz LLC

---

**Built by Matt @ Divine Tribe**  
Powered by Mistral AI, ComfyUI FLUX & sentence-transformers  
Humboldt County, California 🌲

*Last Updated: November 2025*
