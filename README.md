# 🤖 Divine Tribe AI Chatbot

Product recommendation chatbot with RAG search, cached answers, and AI image generation.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

## What It Does

- Recommends products based on natural language queries
- Generates custom artwork with FLUX/ComfyUI
- Caches common answers for instant responses
- Learns from conversation logs

**Live:** https://chat.marijuanaunion.com

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Ollama (Mistral local) |
| Embeddings | sentence-transformers |
| Search | Hybrid semantic + keyword |
| Cache | CAG (instant answers) |
| Backend | Flask + Python 3.9+ |
| Image Gen | ComfyUI + FLUX |
| SSL | Nginx + Let's Encrypt |

## Architecture

```
User Query
    ↓
Intent Classification
    ↓
┌─────────┬──────────┬──────────┐
│ Cache   │ RAG      │ Image    │
│ <0.1s   │ Search   │ Gen      │
└────┬────┴────┬─────┴────┬─────┘
     │         │          │
     └─────────┴──────────┘
              ↓
         Mistral LLM
              ↓
          Response
```

## Quick Start

### Installation

```bash
git clone https://github.com/nicedreamzapp/divine-tribe-chatbot.git
cd divine-tribe-chatbot

python3 -m venv venv
source venv/bin/activate

pip install flask flask-cors ollama sentence-transformers numpy markdown
```

### Run Locally

```bash
# Start chatbot
python chatbot_modular.py
# Runs on http://localhost:5001
```

### Production Setup (VPS + HTTPS)

**Requirements:**
- VPS (Ubuntu 24.04+)
- Domain/subdomain pointed to VPS IP

**1. Install Nginx + Certbot**
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
    server_name your-subdomain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
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
sudo certbot --nginx -d your-subdomain.com
```

**4. SSH Tunnel from Mac to VPS**
```bash
# On your Mac (runs chatbot locally, tunnels to VPS)
ssh -R 0.0.0.0:5001:localhost:5001 root@your-vps-ip -N
```

Your chatbot is now accessible at `https://your-subdomain.com`

## Project Structure

```
divine-tribe-chatbot/
│
├── chatbot_modular.py          # Main Flask server
├── chatbot_with_human.py       # Human-in-loop mode
│
├── modules/
│   ├── agent_router.py         # Routes queries to appropriate handler
│   ├── cag_cache.py           # Cached answers
│   ├── context_manager.py     # Conversation context
│   ├── conversation_logger.py  # Logs for training
│   ├── conversation_memory.py  # Short-term memory
│   ├── image_generator.py     # ComfyUI integration
│   ├── intent_classifier.py   # Query classification
│   ├── product_database.py    # Product search
│   ├── query_preprocessor.py  # Query normalization
│   ├── rag_retriever.py       # Semantic + keyword search
│   └── vector_store.py        # Embeddings storage
│
└── products_clean.json         # Product catalog (143 items)
```

## Features

### Intelligent Search
- Semantic understanding (not just keywords)
- Context-aware follow-ups
- Material detection (concentrate vs dry herb)
- Deduplication (143 unique products, not 700+ variants)

### Cached Answers
```
Query: "what is the v5"
  ↓
Cache: HIT ✓
  ↓
Response: <0.1s (no LLM call)
```

### AI Image Generation
- Integrated ComfyUI + FLUX
- 60-90 second generation time
- Base64 encoded for web display

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Send message, get response |
| `/generate_image` | POST | Create AI artwork |
| `/health` | GET | Server status |

**Example:**
```bash
curl -X POST https://chat.marijuanaunion.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "best for concentrates",
    "session_id": "user_123"
  }'
```

## Model Consolidation

**Problem:** Multiple ComfyUI projects duplicated 10GB+ models across disk

**Solution:** 
- Created central `~/AI_Models/` directory
- Symlinked all projects to shared models
- **Result:** Saved 66GB disk space

```bash
~/AI_Models/
├── ComfyUI/
│   ├── checkpoints/flux1-schnell.safetensors (22GB)
│   ├── clip/t5xxl_fp16.safetensors (9.1GB)
│   └── clip/clip_l.safetensors (235MB)
└── TTS/xtts_v2_model.pth (1.7GB)

# All projects symlink to these shared files
```

## Configuration

### Update Product Catalog
Edit `products_clean.json` - embeddings rebuild automatically on next startup.

### Add Cached Answers
Edit `modules/cag_cache.py`:
```python
self.product_cache = {
    "keyword": {
        "keywords": ["trigger", "words"],
        "response": "Your cached answer...",
        "intent": "product_info"
    }
}
```

## Security Notes

**Not included in repo:**
- `telegram_handler.py` (contains bot tokens)
- `conversation_logs/` (user conversations)
- `*.pkl` (embeddings cache)
- `venv/` (virtual environment)

See `.gitignore` for full list.

## Contact

- **Website:** [ineedhemp.com](https://ineedhemp.com)
- **Email:** matt@ineedhemp.com

## License

Proprietary - Divine Tribe / Nice Dreamz LLC

---

Built by Matt @ Divine Tribe • Powered by Mistral AI & ComfyUI
