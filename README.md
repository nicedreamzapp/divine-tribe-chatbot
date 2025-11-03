<div align="center">

# ✨ Divine Tribe AI Chatbot ✨

### 🚀 Dual-Mode System: Mistral AI + Human-in-the-Loop via Telegram

<img src="https://via.placeholder.com/800x400/10b981/ffffff?text=Divine+Tribe+AI+Assistant" alt="Divine Tribe Chatbot Banner" width="85%" style="border-radius: 20px; margin: 30px 0; box-shadow: 0 15px 40px rgba(0,0,0,0.4);">

**🔥 Mistral 7B AI • Smart Support • AI Image Generation • RLHF Learning 🔥**  
Built for **Divine Tribe Vaporizers** • Works **24/7** • Self-improving AI  

---

## 🎉 **PRODUCTION READY WITH MISTRAL AI & FLUX ART** 🎉

[![Visit Website](https://img.shields.io/badge/Visit-ineedhemp.com-10b981?style=for-the-badge&logo=safari&logoColor=white)](https://ineedhemp.com)

</div>

---

## 📋 What's New in v3.2

### 🎯 **Critical Fixes Applied**
- ✅ **Email Typo Fixed** - Correct spelling: matt@ineedhemp.com (aggressive post-processing)
- ✅ **Shorter Responses** - 250 tokens max (was 400), more concise
- ✅ **Cub Description Fixed** - Correctly described as cleaning tool used WITH Core/Nice Dreamz
- ✅ **Better Product Ranking** - V5 XL prioritized for flavor, Core Deluxe for beginners
- ✅ **No Hallucinations** - Removed made-up troubleshooting steps

### 🤖 **Mistral AI Integration**
- 🧠 **Mistral 7B via Ollama** - Local AI inference (no cloud APIs)
- 🎯 **Context-Aware** - Intent detection: shopping, support, tech_specs, comparison
- 💬 **Conversation Memory** - Remembers last 10 exchanges per session
- 📊 **RLHF Training** - Logs conversations for continuous improvement

### 👤 **100% Human Mode**
- 📱 **Telegram Integration** - All messages route to YOU
- 🔄 **Zero AI** - Complete human control when needed
- 📝 **Training Logger** - Your responses train the AI
- 🎭 **Seamless to Customer** - They never know it's you!

---

## 🎨 AI Image Generation with FLUX

<table>
<tr>
<td width="50%">

### 🖼️ **Local FLUX.1 Image Generation**
- 🎨 **ComfyUI Integration** — Full workflow automation
- 🚀 **FLUX.1 [schnell]** — 22GB model running locally
- 💾 **100% Local** — No cloud APIs, complete privacy
- ⚡ **Real-time Generation** — Create product mockups instantly
- 🖱️ **Click to Save** — Full resolution downloads

</td>
<td width="50%">

### 🔮 **Customer Features**
- 📸 **Product Visualizations** — "Show me a V5 in action"
- 🎨 **Custom Designs** — "Create a dragon using a vaporizer"
- 🌈 **Style Transfer** — "Make it look cyberpunk"
- 🔄 **Variations** — Generate multiple options
- 💬 **Chat Integration** — Request images in conversation

</td>
</tr>
</table>

---

## ✨ Core Features

<table>
<tr>
<td width="50%">

### 🎯 **Intelligent Product Search**
- 📊 **138 Products Organized** — Hierarchical priority system
- 🔍 **Smart Search** — V5 finds V5 XL, Core finds Core Deluxe
- 🚫 **No Spam** — Only shows top 2 relevant products
- ⚡ **Fast Response** — Under 100 words per answer

</td>
<td width="50%">

### 🤖 **Dual-Mode Operation**
- 🤖 **AI Mode** (`chatbot_modular.py`) — Mistral responds
- 👤 **Human Mode** (`chatbot_with_human.py`) — Telegram relay
- 🔄 **Quick Switch** — `chatbot` command to toggle
- 📝 **Training Loop** — Human answers → AI learns

</td>
</tr>
<tr>
<td width="50%">

### 🛠️ **Smart Support Handling**
- 📦 **Returns/Warranties** — Routes to matt@ineedhemp.com
- 🔧 **Troubleshooting** — 2-3 specific steps only
- 📧 **Contact Routing** — Support vs sales inquiries
- ❌ **No Hallucinations** — Only factual information

</td>
<td width="50%">

### 🧪 **Testing & Quality**
- ✅ **16 Problem-Area Tests** — Email, length, accuracy
- 🎯 **Intent Classification** — 6 categories with confidence
- 📊 **Response Validation** — No repetitive answers
- 📈 **Performance Metrics** — Track success rates

</td>
</tr>
</table>

---

## 🚀 Quick Start

### 📋 **One-Command Launch**
```bash
# After setup, just type:
chatbot

# Menu appears:
[1] 🤖 AI Mode (Mistral automated)
[2] 👤 Human Mode (Telegram)
[3] 🔄 Quick Switch
[Q] Quit
```

### ⚙️ **Initial Setup**
```bash
# Install Ollama first
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral

# Clone repository
cd ~/Desktop
git clone [your-repo-url] "dataset for Tribe Chatbot"
cd "dataset for Tribe Chatbot"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask flask-cors ollama python-telegram-bot nest-asyncio python-dotenv --break-system-packages

# Set up Telegram (optional, for human mode)
cp config_template.py config.py
# Edit config.py with your Telegram bot token

# Run!
python3 chatbot_modular.py
```

---

## 🧠 Module Architecture

### 📁 **Active Modules**
| Module | Purpose | Status |
|---|---|---|
| `chatbot_modular.py` | Mistral AI chatbot | ✅ ACTIVE |
| `chatbot_with_human.py` | 100% human mode | ✅ ACTIVE |
| `enhanced_classifier.py` | Intent detection | ✅ ACTIVE |
| `product_database.py` | Hierarchical search | ✅ ACTIVE |
| `image_generator.py` | FLUX image creation | ✅ ACTIVE |
| `conversation_memory.py` | Context awareness | ✅ ACTIVE |
| `conversation_logger.py` | RLHF training data | ✅ ACTIVE |

### 🎯 **System Prompt Strategy**
```python
# Intent-specific prompts for Mistral
- support → Route to matt@ineedhemp.com with order# + photos
- shopping → Recommend 1-2 products MAX (Beginners→Core, Flavor→V5)
- product_info → Top 2 products only, brief description
- tech_specs → Specific temps/watts/settings
- comparison → 3-4 bullet points: flavor, ease, portability, price
```

---

## 🧪 Testing Suite

### **Run Problem-Area Tests**
```bash
# Test the 16 critical problem areas
python3 test_problem_areas.py

# Expected results:
# ✅ Email typos: 0
# ✅ Responses too long: 0
# ✅ Cub description wrong: 0
```

### **Test Image Generation**
```bash
# Start ComfyUI first
cd ~/Desktop/ComfyUI-FLUX-Project/ComfyUI
python main.py --listen --port 8188

# Test image endpoint
curl -X POST http://localhost:5001/generate_image \
  -H "Content-Type: application/json" \
  -d '{"prompt": "divine tribe vaporizer futuristic", "session_id": "test"}'
```

---

## 📊 Performance Metrics

<div align="center">

| Feature | Performance | Notes |
|---|---|---|
| **Chat Response** | 1-2 seconds | Mistral 7B local |
| **Product Search** | <500ms | 138 products indexed |
| **Image Generation** | 60-90 seconds | FLUX.1 on local GPU |
| **Support Routing** | Instant | Email redirection |
| **Response Length** | 50-100 words | Enforced via num_predict=250 |
| **Email Accuracy** | 100% | Post-processing fixes typos |

</div>

---

## 🔧 Key Business Rules

### ✅ **Product Recommendations**
- **Beginners** → Core Deluxe (6 preset temps, easiest)
- **Flavor Seekers** → V5 XL (pure ceramic, best flavor)
- **Desktop Power** → Ruby Twist (ball vape design)
- **Concentrates** → Nice Dreamz (fogger design)
- **Cleaning** → Cub (use WITH Core or Nice Dreamz, never alone)

### 📧 **Support Email**
- **CRITICAL:** matt@ineedhemp.com (NOT ineedheemp)
- **Returns/Refunds** → Email with order# + photos
- **Warranty** → Email with description + photos
- **Troubleshooting** → 2-3 steps, then suggest email if persists

### 🚫 **What NOT to Do**
- ❌ Don't recommend replacement parts unless asked
- ❌ Don't suggest Cub as standalone product
- ❌ Don't give generic troubleshooting (be specific)
- ❌ Don't mention Core 2.0 (obsolete, only Core Deluxe)
- ❌ Don't write responses over 100 words

---

## 🌐 Web Integration

### **Glassmorphic Chat Widget**
```html
<!-- Beautiful see-through design -->
- 🎨 Dark theme with green accents (#10b981)
- 💎 Glassmorphic transparency (75% opacity)
- 📱 Mobile responsive with keyboard handling
- ⚡ Real-time polling for human responses
- 🎭 Smooth animations and hover effects
```

**Features:**
- 💬 Ask Question button → Mistral AI response
- 🎨 Generate Art button → FLUX image creation
- 📞 Human mode polling → Get YOUR Telegram replies
- 🌊 See-through design shows website behind

---

## 📞 Support & Contact

<div align="center">

### 💬 **Need Help?**

[![Email Support](https://img.shields.io/badge/Email-matt@ineedhemp.com-red?style=for-the-badge&logo=gmail)](mailto:matt@ineedhemp.com)
[![Website](https://img.shields.io/badge/Website-ineedhemp.com-10b981?style=for-the-badge&logo=safari)](https://ineedhemp.com)
[![Reddit](https://img.shields.io/badge/Reddit-r/DivineTribeVaporizers-FF4500?style=for-the-badge&logo=reddit)](https://www.reddit.com/r/DivineTribeVaporizers/)

</div>

---

## 🎯 Version History

### **v3.2 (Current) - Aggressive Fixes**
- ✅ Email typo post-processing
- ✅ Shortened responses (250 tokens)
- ✅ Fixed Cub description
- ✅ Better system prompts

### **v3.1 - Mistral Integration**
- 🧠 Ollama + Mistral 7B
- 📊 Intent-aware prompts
- 💬 Conversation memory

### **v3.0 - Human Mode**
- 📱 Telegram integration
- 👤 100% human override
- 📝 Training logger

### **v2.0 - FLUX Images**
- 🎨 ComfyUI integration
- 🖼️ Local image generation

---

<div align="center">

## 🌟 **Project Statistics** 🌟

[![Lines of Code](https://img.shields.io/badge/Lines_of_Code-8000%2B-blue?style=for-the-badge)]()
[![Active Modules](https://img.shields.io/badge/Active_Modules-7-green?style=for-the-badge)]()
[![Test Coverage](https://img.shields.io/badge/Problem_Tests-100%25_Pass-brightgreen?style=for-the-badge)]()
[![Mistral AI](https://img.shields.io/badge/Mistral-7B_Local-purple?style=for-the-badge)]()

### 🚀 **Version 3.2 - Mistral AI + FLUX + Human Mode**

</div>

---

<div align="center">
<sub>© 2025 Divine Tribe AI Chatbot • Mistral 7B • FLUX Images • Telegram Human Mode • Self-Learning</sub>
</div>
