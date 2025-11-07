<div align="center">

# ✨ Divine Tribe AI Chatbot ✨

### 🚀 Production E-Commerce AI: Mistral + RAG + FLUX + Telegram

<img src="https://via.placeholder.com/800x400/10b981/ffffff?text=Enterprise+AI+Chatbot+System" alt="Divine Tribe Chatbot Banner" width="85%" style="border-radius: 20px; margin: 30px 0; box-shadow: 0 15px 40px rgba(0,0,0,0.4);">

**🔥 Self-Hosted AI • 782 Products • Sub-3s Responses • 100% Uptime 🔥**  
Built for **[Divine Tribe Vaporizers](https://ineedhemp.com)** • Handles **Real Customer Support** • Enterprise-Grade Architecture

[![GitHub](https://img.shields.io/badge/GitHub-nicedreamzapp-181717?style=for-the-badge&logo=github)](https://github.com/nicedreamzapp)
[![Website](https://img.shields.io/badge/Live-ineedhemp.com-10b981?style=for-the-badge&logo=safari&logoColor=white)](https://ineedhemp.com)
[![Reddit](https://img.shields.io/badge/Community-r/DivineTribeVaporizers-FF4500?style=for-the-badge&logo=reddit)](https://www.reddit.com/r/DivineTribeVaporizers/)

</div>

---

## 🎯 Technical Highlights (Portfolio Showcase)

<table>
<tr>
<td width="50%" valign="top">

### 🧠 **AI/ML Architecture**
- **Mistral 7B** - Self-hosted via Ollama (no API costs)
- **RAG Pipeline** - Semantic search over 782 products
- **Sentence Transformers** - all-MiniLM-L6-v2 embeddings
- **Vector Search** - Custom similarity engine
- **Context Engineering** - Intent-aware system prompts
- **RLHF Training** - Conversation logging for improvement

</td>
<td width="50%" valign="top">

### ⚡ **Performance**
- **2.26s** avg response time (240-question stress test)
- **21.7 questions/min** throughput
- **100%** completion rate (no crashes)
- **61%** AI-generated responses
- **37%** instant cached responses
- **Sub-second** troubleshooting (Reddit solutions)

</td>
</tr>
</table>

---

## 🏗️ System Architecture

```mermaid
graph TB
    A[User Query] --> B{Agent Router}
    B -->|Cache Hit| C[CAG Cache<br/>37% instant]
    B -->|Need Context| D[RAG Retriever<br/>782 products]
    B -->|Need AI| E[Mistral 7B<br/>Context-aware]
    
    D --> F[Vector Search<br/>Semantic matching]
    F --> E
    
    C --> G[Response]
    E --> G
    
    G --> H[Post-Processing<br/>Email fix, length limit]
    H --> I[Customer]
    
    J[Conversation Logger] -.->|RLHF Training| K[(Training Data)]
    I -.->|Feedback| J
    
    style B fill:#10b981
    style E fill:#8b5cf6
    style C fill:#f59e0b
    style D fill:#3b82f6
```

### Key Components:

**1. Agent Router** (Smart Query Classification)
- Detects intent: troubleshooting, comparison, product_info, support
- Routes to optimal handler: cache (37%), RAG (40%), Mistral (21%)
- Rejects off-topic queries (1.7% accuracy)

**2. CAG Cache** (Canonical Answer Generation)
- Pre-written responses for common queries
- Reddit-proven troubleshooting solutions
- Instant response (<1ms)
- Covers 37% of traffic

**3. RAG Pipeline** (Retrieval-Augmented Generation)
- Sentence-BERT embeddings (384 dimensions)
- Cosine similarity search
- Top-K retrieval (K=3-5)
- Context injection into Mistral

**4. Mistral Integration** (Local LLM)
- 7B parameter model
- Intent-specific system prompts
- Temperature: 0.7 (creative but grounded)
- Max tokens: 200 (concise responses)
- No cloud APIs (100% self-hosted)

---

## 🎨 FLUX Image Generation

<table>
<tr>
<td width="50%" valign="top">

### 🖼️ **ComfyUI Integration**
- **FLUX.1 [schnell]** - 22GB diffusion model
- **Local GPU inference** - No API costs
- **Workflow automation** - JSON-driven generation
- **60-90s generation time** - M4 Pro optimization
- **Full-resolution downloads** - Customer-ready images

</td>
<td width="50%" valign="top">

### 🔌 **API Endpoints**
```python
POST /generate_image
{
  "prompt": "divine tribe v5 vaporizer cyberpunk",
  "session_id": "user_123"
}

Response: {
  "image_url": "/image/output.png",
  "generation_time": 73.2
}
```

</td>
</tr>
</table>

**Technical Implementation:**
- ComfyUI REST API integration
- Async image generation (non-blocking)
- WebSocket progress tracking
- Automatic file cleanup (24hr retention)
- NSFW content filtering

---

## 📊 Stress Test Results (240 Questions)

### Real-World Performance Analysis

<div align="center">

| Metric | Value | Grade |
|--------|-------|-------|
| **Avg Response Time** | 2.26s | A+ ⚡ |
| **Completion Rate** | 100% (240/240) | A+ ✅ |
| **Cache Hit Rate** | 37% | A 🎯 |
| **AI Generation Rate** | 61% | A 🧠 |
| **Quality Score** | 8.5/10 | A- ⭐ |
| **Rejection Accuracy** | 100% (4/4 off-topic) | A+ 🚫 |

</div>

**Test Details:**
- 240 real Reddit questions from r/DivineTribeVaporizers
- 24 categories (V5 setup, Core issues, mod compatibility, etc.)
- 11 minute 3 second total runtime
- Zero crashes or errors
- Full results: `stress_test_REAL_20251106_035954.json`

### Route Distribution:

```
RAG (Product Search + AI):  96 (40.0%) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mistral (Pure AI Reasoning): 50 (20.8%) ━━━━━━━━━━━━━━━━━━━━━
How-To Guides (Cached):      38 (15.8%) ━━━━━━━━━━━━━━━━
Product Cache:               20 (8.3%)  ━━━━━━━━━
Troubleshooting (Reddit):    15 (6.2%)  ━━━━━━━
Support (Warranty/Returns):  17 (7.1%)  ━━━━━━━━
Rejected (Off-topic):         4 (1.7%)  ━━
```

---

## 💡 Technical Innovations

### 1. **CAG Cache with Reddit Solutions**
Real troubleshooting steps from community, not AI hallucinations:
```python
'v5_resistance_high': {
    'problem': 'V5 showing high resistance (0.60+ ohms)',
    'reddit_solutions': [
        '🔧 Tighten the 510 pin (1/4 turn)',
        '🧹 Clean threads with alcohol',
        '⚡ Check mod 510 contact',
        '📊 Normal range: 0.40-0.52 ohms'
    ],
    'keywords': ['resistance', 'high ohm', 'check atomizer']
}
```

### 2. **Intent-Aware System Prompts**
Different AI behavior for different query types:
```python
if intent == 'troubleshooting':
    prompt = "You are a support expert. Give 2-3 specific steps..."
elif intent == 'comparison':
    prompt = "Compare products fairly. End with recommendation..."
elif intent == 'product_question':
    prompt = "Highlight 2-3 key features. Keep brief..."
```

### 3. **Hybrid Architecture**
Combines best of all approaches:
- **Cached** (37%): Instant, 100% accurate
- **RAG** (40%): Grounded in product data
- **LLM** (21%): Creative reasoning when needed
- **Human** (Optional): Telegram relay for complex cases

### 4. **Context Management**
Tracks conversation state for follow-ups:
```python
context_manager.update("user mentioned they have V5 XL")
# Next query automatically includes this context
```

---

## 🛠️ Tech Stack

<div align="center">

### **Backend**
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Mistral_7B-000000?style=for-the-badge)

### **AI/ML**
![Mistral](https://img.shields.io/badge/Mistral-7B-FF7000?style=for-the-badge)
![Sentence-BERT](https://img.shields.io/badge/Sentence_BERT-all--MiniLM--L6--v2-blue?style=for-the-badge)
![FLUX](https://img.shields.io/badge/FLUX.1-schnell-purple?style=for-the-badge)

### **Infrastructure**
![M4 Pro](https://img.shields.io/badge/M4_Pro-64GB_RAM-000000?style=for-the-badge&logo=apple&logoColor=white)
![Self-Hosted](https://img.shields.io/badge/Self_Hosted-100%25-10b981?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Telegram-Bot_API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)

</div>

---

## 📁 Project Structure

```
divine-tribe-chatbot/
├── 🤖 chatbot_modular.py          # Main Mistral AI chatbot
├── 👤 chatbot_with_human.py       # Telegram human-in-loop mode
├── 🎨 image_generator.py          # FLUX ComfyUI integration
├── 📊 products_organized.json     # 782 product database
│
├── modules/
│   ├── 🧠 agent_router.py         # Smart query routing
│   ├── ⚡ cag_cache.py            # Instant response cache
│   ├── 🔍 product_database.py     # Semantic search
│   ├── 🎯 enhanced_classifier.py  # Intent detection
│   ├── 💬 conversation_memory.py  # Context tracking
│   ├── 📝 conversation_logger.py  # RLHF training data
│   ├── 🌐 context_manager.py      # State management
│   └── 🔧 rag_retriever.py        # RAG pipeline
│
├── 🧪 test_overnight_REAL.py      # 240-question stress test
├── 📋 requirements.txt             # Python dependencies
├── 🔒 .gitignore                   # Protects sensitive data
└── 📖 README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites
```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral

# 2. Clone repository
git clone https://github.com/nicedreamzapp/divine-tribe-chatbot.git
cd divine-tribe-chatbot

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Run the Chatbot
```bash
# AI Mode (Mistral automated)
python3 chatbot_modular.py

# Human Mode (Telegram relay)
python3 chatbot_with_human.py

# Or use the launcher
python3 chatbot_launcher.py
```

### Run Stress Test
```bash
# Test with 240 real Reddit questions
python3 test_overnight_REAL.py

# Results saved to: stress_test_REAL_YYYYMMDD_HHMMSS.json
```

---

## 📈 Key Metrics & Achievements

### **Business Impact**
- ✅ **24/7 Support** - Handles customer queries around the clock
- ✅ **Zero API Costs** - 100% self-hosted (Mistral + FLUX local)
- ✅ **High Accuracy** - 8.5/10 quality score on Reddit questions
- ✅ **Fast Response** - 2.26s average (customers don't wait)
- ✅ **Scalable** - 21.7 questions/minute throughput

### **Technical Achievements**
- 🏆 **Hybrid AI** - Combines cache (fast) + RAG (accurate) + LLM (smart)
- 🏆 **No Hallucinations** - Reddit solutions (not AI guesses)
- 🏆 **Context-Aware** - Remembers conversation history
- 🏆 **Production Ready** - 100% completion rate (240/240 tests)
- 🏆 **Self-Improving** - RLHF training from conversations

### **Community Integration**
- 💬 **Reddit**: r/DivineTribeVaporizers (troubleshooting solutions)
- 🎮 **Discord**: https://discord.com/invite/aC4Pv6J75s
- 📺 **YouTube**: https://www.youtube.com/@divinetribe1

---

## 🧪 Testing & Quality Assurance

### **Comprehensive Test Suite**
```bash
# Run all tests
python3 test_overnight_REAL.py  # 240 Reddit questions
python3 test_problem_areas.py   # 16 critical issues
python3 test_cag_cache.py       # Cache hit rates
```

### **Monitored Issues**
- ✅ Email accuracy (matt@ineedhemp.com - not ineedheemp)
- ✅ Response length (200 tokens max, enforced)
- ✅ Product accuracy (no hallucinated products)
- ✅ Cub description (cleaning tool, not standalone)
- ✅ Routing accuracy (troubleshooting before sales)

---

## 💻 API Documentation

### **Chat Endpoint**
```python
POST /chat
Content-Type: application/json

{
  "message": "What's the best vaporizer for beginners?",
  "session_id": "user_12345"
}

Response:
{
  "response": "For beginners, I recommend the Core 2.0 Deluxe...",
  "intent": "product_recommendation",
  "products": [
    {"name": "Core 2.0 Deluxe", "price": "$199", "url": "..."}
  ],
  "response_time": 2.3
}
```

### **Image Generation Endpoint**
```python
POST /generate_image
Content-Type: application/json

{
  "prompt": "futuristic vaporizer in cyberpunk style",
  "session_id": "user_12345"
}

Response:
{
  "image_url": "/static/images/output_12345.png",
  "generation_time": 73.2,
  "prompt": "futuristic vaporizer in cyberpunk style"
}
```

---

## 🔒 Security & Privacy

### **Data Protection**
- ✅ No customer data stored in git
- ✅ Conversation logs excluded (.gitignore)
- ✅ Telegram tokens in config.py (not tracked)
- ✅ Local inference (no data sent to cloud)
- ✅ 24-hour image retention (auto-cleanup)

### **Safe Deployment**
```bash
# .gitignore protects:
- config.py (API keys)
- conversation_logs/ (customer privacy)
- *.pkl (model files - too large)
- stress_test_*.json (test data)
```

---

## 📊 Performance Benchmarks

### **Response Time Breakdown**
| Route | Avg Time | Use Case |
|-------|----------|----------|
| **Cache** | <0.01s ⚡ | Common questions (37%) |
| **RAG** | 2.58s 📊 | Product searches (40%) |
| **Mistral** | 3.07s 🧠 | Complex reasoning (21%) |
| **Support** | <0.01s 🎯 | Warranty/returns (2%) |

### **Quality by Intent**
| Intent | Responses | Quality | Example |
|--------|-----------|---------|---------|
| **Troubleshooting** | 15 | ⭐⭐⭐⭐⭐ | "v5 resistance high" → Reddit fix |
| **Comparison** | 12 | ⭐⭐⭐⭐ | "v5 vs core" → Fair analysis |
| **Product Info** | 96 | ⭐⭐⭐⭐ | "tell me about v5" → Features |
| **How-To** | 38 | ⭐⭐⭐⭐⭐ | "tcr settings" → Specific values |

---

## 🎯 Roadmap & Future Enhancements

### **In Progress**
- [ ] Multi-turn conversation improvements
- [ ] Fine-tune Mistral on Divine Tribe data
- [ ] A/B testing framework
- [ ] Real-time analytics dashboard

### **Planned**
- [ ] Voice interface (Whisper integration)
- [ ] Multi-language support (Spanish, French)
- [ ] Mobile app (React Native)
- [ ] Advanced RLHF training pipeline

### **Research**
- [ ] Experiment with Llama 3 70B
- [ ] Test FLUX.1 [dev] for higher quality images
- [ ] Explore RAG with long-context models (32k+ tokens)

---

## 📞 Contact & Links

<div align="center">

### **Portfolio & Social**

[![GitHub](https://img.shields.io/badge/GitHub-nicedreamzapp-181717?style=for-the-badge&logo=github)](https://github.com/nicedreamzapp)
[![Website](https://img.shields.io/badge/Website-ineedhemp.com-10b981?style=for-the-badge&logo=safari)](https://ineedhemp.com)
[![Reddit](https://img.shields.io/badge/Reddit-Community-FF4500?style=for-the-badge&logo=reddit)](https://www.reddit.com/r/DivineTribeVaporizers/)
[![Discord](https://img.shields.io/badge/Discord-Join_Us-5865F2?style=for-the-badge&logo=discord)](https://discord.com/invite/aC4Pv6J75s)
[![YouTube](https://img.shields.io/badge/YouTube-Tutorials-FF0000?style=for-the-badge&logo=youtube)](https://www.youtube.com/@divinetribe1)

**Business Inquiries:** matt@ineedhemp.com

</div>

---

## 📜 License & Attribution

**Project:** Divine Tribe AI Chatbot  
**Author:** [nicedreamzapp](https://github.com/nicedreamzapp)  
**Company:** Divine Tribe / ineedhemp.com  
**License:** Proprietary (Portfolio showcase)  

### **Technologies Used:**
- Mistral AI (Apache 2.0)
- Sentence Transformers (Apache 2.0)
- FLUX.1 (Apache 2.0)
- ComfyUI (GPL-3.0)
- Python, Flask, Ollama

---

## 🌟 Project Stats

<div align="center">

![Lines of Code](https://img.shields.io/badge/Lines_of_Code-12%2C000%2B-blue?style=for-the-badge)
![Test Coverage](https://img.shields.io/badge/Stress_Test-100%25_Pass-brightgreen?style=for-the-badge)
![Response Time](https://img.shields.io/badge/Avg_Response-2.26s-yellow?style=for-the-badge)
![AI Models](https://img.shields.io/badge/AI_Models-2_Local-purple?style=for-the-badge)

### **Production E-Commerce AI • Self-Hosted • Enterprise-Grade**

</div>

---

<div align="center">
<sub>© 2025 Divine Tribe AI Chatbot • Mistral 7B • FLUX.1 • RAG Pipeline • Built by nicedreamzapp</sub>
</div>
