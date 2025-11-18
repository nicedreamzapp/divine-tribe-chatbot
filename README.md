# 🤖 Divine Tribe AI Chatbot

Intelligent product recommendation chatbot with semantic search, instant cached answers, and AI image generation.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

## What It Does

- **Smart Product Recommendations** - Natural language search with semantic understanding
- **AI Image Generation** - Custom artwork with FLUX/ComfyUI (60-90 seconds)
- **Instant Cached Answers** - Common questions answered in <0.1s
- **Conversational Memory** - Remembers context across conversation
- **RLHF Ready** - Logs all conversations for continuous improvement

**Live Chat:** Available at [ineedhemp.com](https://ineedhemp.com)

## Recent Updates (Nov 2025)

### ✅ Production-Ready Improvements
- **No Hallucinations** - Uses only real product data from products_clean.json
- **Better Routing** - Creative queries handled naturally by general knowledge mode
- **Enhanced Comparisons** - Product comparison questions get detailed answers
- **Priority Ranking** - Main products always show first in search results
- **Cleaner Responses** - Uses clear, customer-friendly terminology

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Ollama (Mistral local) |
| Embeddings | sentence-transformers |
| Search | Hybrid semantic + keyword RAG |
| Cache | CAG (instant answers) |
| Backend | Flask + Python 3.9+ |
| Image Gen | ComfyUI + FLUX |
| SSL | Nginx + Let's Encrypt |
| Hosting | VPS + SSH tunnel |

## Architecture
```
User Query
    ↓
Intent Classification
    ↓
┌─────────┬──────────┬──────────┬──────────┐
│ Cache   │ Search   │ Image    │ General  │
│ <0.1s   │ RAG      │ Gen      │ AI       │
└────┬────┴────┬─────┴────┬─────┴────┬─────┘
     │         │          │          │
     └─────────┴──────────┴──────────┘
              ↓
         Mistral LLM
              ↓
        Final Response
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
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
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
sudo certbot --nginx -d your-domain.com
```

**4. Permanent SSH Tunnel from Mac to VPS**

**Create service file on Mac:**
```bash
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
# Load and start the service
sudo launchctl load /Library/LaunchDaemons/com.divinetribe.chatbot.tunnel.plist
sudo launchctl start com.divinetribe.chatbot.tunnel
```

Your chatbot is now accessible at `https://your-domain.com` 24/7!

## Project Structure
```
divine-tribe-chatbot/
│
├── chatbot_modular.py          # Main Flask server
├── chatbot_with_human.py       # Human-in-loop mode
├── chatbot_launcher.command    # Quick launcher script
│
├── modules/
│   ├── agent_router.py         # Routes queries to handlers
│   ├── cag_cache.py           # Cached answers
│   ├── context_manager.py     # Conversation context
│   ├── conversation_logger.py  # Training data logger
│   ├── conversation_memory.py  # Short-term memory
│   ├── image_generator.py     # ComfyUI/FLUX integration
│   ├── product_database.py    # Product search engine
│   ├── rag_retriever.py       # Semantic search
│   └── vector_store.py        # Embeddings cache
│
├── products_clean.json         # Product catalog (143 products)
├── product_embeddings.pkl      # Cached embeddings (auto-generated)
└── conversation_logs/          # Training data
```

## Key Features

### 🎯 Intelligent Search

- Semantic understanding (not just keyword matching)
- Context-aware follow-up questions
- Prioritizes main products over accessories
- Deduplication (143 unique products)

### ⚡ Instant Cached Answers

Common questions answered in <0.1s without calling the LLM:
- Product comparisons
- Troubleshooting guides
- Setup instructions
- Company information

### 🧠 Conversational Memory

- Tracks products mentioned in conversation
- Remembers user preferences
- Resolves follow-up references ("tell me more about it")
- Detects when user is answering questions

### 🎨 AI Image Generation

- Integrated ComfyUI + FLUX model
- 60-90 second generation time
- Base64 encoded for web display
- Automatic cleanup

**Example:** "create an image of a sunset over mountains"

### 📊 RLHF Training Data

All conversations logged for:
- Performance analysis
- Fine-tuning training data
- Quality improvement

## API Endpoints

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|---------------|
| `/chat` | POST | Send message, get response | 0.1s - 3s |
| `/generate_image` | POST | Create AI artwork | 60-90s |
| `/health` | GET | Server status | <0.1s |

**Chat Example:**
```bash
curl -X POST https://your-domain.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "what do you recommend for beginners",
    "session_id": "user_123"
  }'
```

**Response:**
```json
{
  "response": "<p>For beginners, I recommend...</p>",
  "status": "success",
  "route": "rag"
}
```

## Configuration

### Update Product Catalog
Edit `products_clean.json` - embeddings rebuild automatically.

**Format:**
```json
[
  {
    "name": "Product Name",
    "url": "https://yoursite.com/product/...",
    "description": "Product description...",
    "category": "main_products"
  }
]
```

### Add Cached Answers
Edit `modules/cag_cache.py` to add new cached responses.

### Customize System Prompt
Edit `chatbot_modular.py` to change chatbot personality and instructions.

## Testing

### Run Test Suite
```bash
python test_chatbot_50_questions.py
```

Generates test results analyzing:
- Route distribution
- Response quality
- Recommendation accuracy

## Troubleshooting

### Issue: Image generation fails
**Solution:** 
1. Start ComfyUI: `cd ~/ComfyUI && python main.py`
2. Verify FLUX model is installed
3. Check `http://localhost:8188` is accessible

### Issue: Generic responses
**Solution:**
1. Check `products_clean.json` exists
2. Verify Mistral model: `ollama list`
3. Check logs for errors

### Issue: SSH tunnel disconnects
**Solution:**
1. Use LaunchDaemon (see Production Setup)
2. Monitor: `tail -f /tmp/chatbot-tunnel.log`

## Model Consolidation

**Saved 66GB disk space** by consolidating models:
```bash
~/AI_Models/
├── ComfyUI/
│   ├── unet/flux1-schnell.safetensors (22GB)
│   ├── clip/t5xxl_fp16.safetensors (9.1GB)
│   ├── clip/clip_l.safetensors (235MB)
│   └── vae/ae.safetensors (320MB)
└── TTS/xtts_v2_model.pth (1.7GB)

# Projects symlink to shared files
ln -s ~/AI_Models/ComfyUI/unet ~/ComfyUI/models/unet
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Products indexed | 143 unique items |
| Cache hit rate | ~40% of queries |
| Avg response (cached) | <0.1s |
| Avg response (search) | 1-3s |
| Avg response (image) | 60-90s |
| Vector dimensions | 384 |

## Security

**Excluded from repo:**
- API tokens/keys
- User conversation logs (GDPR)
- SSH keys
- Virtual environment files

See `.gitignore` for complete list.

## Roadmap

- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Product image search
- [ ] Fine-tuned model on company data
- [ ] Analytics dashboard

## Contact

- **Website:** [ineedhemp.com](https://ineedhemp.com)
- **Email:** matt@ineedhemp.com

## License

Proprietary - Divine Tribe / Nice Dreamz LLC

---

**Built by Matt @ Divine Tribe**  
Powered by Mistral AI & ComfyUI FLUX  
Humboldt County, California 🌲

*Last Updated: November 2025*
