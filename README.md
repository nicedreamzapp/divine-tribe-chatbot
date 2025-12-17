<p align="center">
  <img src="https://img.shields.io/badge/Divine_Tribe-AI_Assistant-purple?style=for-the-badge&logo=robot&logoColor=white" alt="Divine Tribe"/>
  <img src="https://img.shields.io/badge/Powered_by-Claude_AI-blue?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude"/>
  <img src="https://img.shields.io/badge/Images-FLUX_AI-orange?style=for-the-badge&logo=image&logoColor=white" alt="FLUX"/>
</p>

<h1 align="center">
  🌿 Divine Tribe AI Assistant 🌿
</h1>

<p align="center">
  <i>Your friendly neighborhood chatbot for vaporizers, hemp gear, and AI-generated art!</i>
</p>

<p align="center">
  <a href="https://ineedhemp.com">🌐 Website</a> •
  <a href="https://discord.com/invite/f3qwvp56be">💬 Discord</a> •
  <a href="https://www.reddit.com/r/DivineTribeVaporizers/">📱 Reddit</a> •
  <a href="https://www.youtube.com/@divinetribe1">🎬 YouTube</a>
</p>

---

## 🎯 What Is This?

A **multi-platform AI system** that handles customer support, product questions, order lookups, and generates custom AI artwork!

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   🌐 WEBSITE ──────┐                                               │
│                    │                                               │
│   💬 DISCORD ──────┼──▶  🧠 AI BRAIN  ──▶  💬 Smart Responses      │
│                    │     (Claude +                                 │
│   📧 EMAIL ────────┘      RAG/CAG)     ──▶  🎨 AI Artwork          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features at a Glance

| Feature | 🌐 Web | 💬 Discord | 📧 Email | Description |
|:--------|:------:|:----------:|:--------:|:------------|
| 🛒 **Product Search** | ✅ | ✅ | ✅ | Find vaporizers, clothing, accessories |
| 📦 **Order Lookup** | ✅ | ✅ | ✅ | Check status with secure verification |
| 🎨 **AI Images** | ✅ | ↗️ | ↗️ | FLUX-powered artwork (web only) |
| 🔧 **Troubleshooting** | ✅ | ✅ | ✅ | Reddit-proven device solutions |
| 💬 **Smart Chat** | ✅ | ✅ | ✅ | Natural conversation with Claude |
| 📝 **Draft Approval** | ❌ | ❌ | ✅ | Human reviews before sending |

> *↗️ = Redirects to website for image generation*

---

## 🚀 The Evolution

```
┌──────────────────────────────────────────────────────────────────┐
│  📜 VERSION HISTORY                                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  v1 ░░░░░░░░░░  Mistral 7B Local                                │
│     └─▶ Fast but 4k context limit, hallucinated products        │
│                                                                  │
│  v2 ████░░░░░░  Claude API                                      │
│     └─▶ 200k context, better reasoning, honest uncertainty      │
│                                                                  │
│  v3 ████████░░  Hybrid RAG/CAG                                  │
│     └─▶ Instant cached answers + semantic product search        │
│                                                                  │
│  v4 ██████████  Dual System + FLUX  ◀── YOU ARE HERE            │
│     └─▶ Email + Chat + Images sharing one brain                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

<table>
<tr>
<td width="50%" valign="top">

### ☁️ VPS Server (24/7)
```
╔════════════════════════════╗
║  🖥️  ALWAYS-ON SERVER     ║
╠════════════════════════════╣
║                            ║
║  🤖 Chatbot API (port 5001)║
║  📦 143 Products Database  ║
║  🧠 RAG + CAG Intelligence ║
║  📧 Email Dashboard        ║
║  🎮 Discord Bot            ║
║  📊 355 Keyword Index      ║
║                            ║
╚════════════════════════════╝
```

</td>
<td width="50%" valign="top">

### 🍎 Mac (For Images)
```
╔════════════════════════════╗
║  💻 LOCAL WORKSTATION     ║
╠════════════════════════════╣
║                            ║
║  🎨 ComfyUI + FLUX AI      ║
║  🔗 SSH Tunnel → VPS       ║
║  🖼️ 1024x1024 Generation   ║
║  ⚡ ~10 sec per image      ║
║                            ║
╚════════════════════════════╝
```

</td>
</tr>
</table>

### 🔀 How Requests Flow

```
                              ┌─────────────────┐
                              │  User Request   │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  VPS Chatbot    │
                              │  (Agent Router) │
                              └────────┬────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
     ┌────────────────┐      ┌────────────────┐      ┌────────────────┐
     │  💬 Chat/FAQ   │      │  📦 Order      │      │  🎨 Image      │
     │  CAG Cache     │      │  WooCommerce   │      │  ═══tunnel═══▶ │
     │  RAG Search    │      │  Lookup        │      │  Mac ComfyUI   │
     └────────┬───────┘      └────────┬───────┘      └────────┬───────┘
              │                        │                        │
              └────────────────────────┴────────────────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │   Response! 🎉  │
                              └─────────────────┘
```

---

## 🧠 The Brain: RAG + CAG Hybrid

<table>
<tr>
<td align="center" width="50%">

### 📚 RAG
**Retrieval Augmented Generation**

```
     Query
       │
       ▼
  ┌─────────┐
  │ 🔍 5-Signal Search    │
  ├─────────┤
  │ • Semantic (40%)      │
  │ • Lexical (30%)       │
  │ • Priority (20%)      │
  │ • Business (10%)      │
  └─────────┘
       │
       ▼
  Found Products
       │
       ▼
  Claude Response
```

*For: Product questions, comparisons*

</td>
<td align="center" width="50%">

### ⚡ CAG
**Cache Augmented Generation**

```
     Query
       │
       ▼
  ┌─────────┐
  │ 💾 Cache Lookup       │
  ├─────────┤
  │ • Policies            │
  │ • Settings            │
  │ • Troubleshooting     │
  │ • FAQ                 │
  └─────────┘
       │
       ▼
  ⚡ INSTANT!
  (No API call)
```

*For: Common questions, known issues*

</td>
</tr>
</table>

### 🎯 Smart Routing

| Route | Triggers | Example Query |
|:------|:---------|:--------------|
| `📦 order` | order #, tracking, where's my | "Where's my order #12345?" |
| `🛒 rag` | product names, recommendations | "Best vape for concentrates?" |
| `💾 cache` | policies, settings, how-to | "What's your return policy?" |
| `🔧 troubleshoot` | not working, error, problem | "My V5 shows check atomizer" |
| `🎨 image` | draw, create, generate, paint | "Draw a dragon vaping" |
| `💬 general` | everything else | "Tell me a joke" |

---

## 🎨 AI Image Generation

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  🎨 FLUX IMAGE PIPELINE                                           │
│                                                                    │
│  User: "epic sunset over mountains"                               │
│         │                                                          │
│         ▼                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│  │ VPS receives │ ──▶ │ SSH Tunnel   │ ──▶ │ Mac ComfyUI  │       │
│  │ request      │     │ port 8188    │     │ FLUX model   │       │
│  └──────────────┘     └──────────────┘     └──────────────┘       │
│                                                   │                │
│                                                   ▼                │
│                                            ┌──────────────┐       │
│                                            │ 🖼️ Generated │       │
│                                            │ 1024x1024    │       │
│                                            │ ~10 seconds  │       │
│                                            └──────────────┘       │
│                                                   │                │
│         ◀─────────────────────────────────────────┘                │
│         │                                                          │
│  User sees image!                                                  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

| Spec | Value |
|:-----|:------|
| 🎯 Model | FLUX Schnell |
| 📐 Resolution | 1024 × 1024 |
| ⚡ Speed | ~10 seconds |
| 🎨 Style | Photorealistic to artistic |
| 🔒 Privacy | No cloud, no filters, local only |

---

## 📁 Project Structure

```
Divine Tribe Email Assistant/
│
├── 🤖 chatbot/
│   ├── chatbot_modular.py        # Main chatbot engine
│   ├── telegram_handler.py       # Telegram integration
│   └── youtube_knowledge.py      # Tutorial content loader
│
├── 📧 email/
│   ├── email_assistant.py        # Email processor
│   ├── gmail_client.py           # Gmail API wrapper
│   ├── web_dashboard.py          # Admin interface
│   ├── woo_client.py             # WooCommerce orders
│   └── smart_responder.py        # Response generator
│
├── 🧩 modules/
│   ├── agent_router.py           # Smart query routing
│   ├── cag_cache.py              # Cached responses (43KB)
│   ├── rag_retriever.py          # 5-signal search
│   ├── product_database.py       # Product lookups
│   ├── image_generator.py        # FLUX integration
│   ├── order_verify.py           # Secure verification
│   ├── vector_store.py           # Embeddings
│   └── context_manager.py        # Session tracking
│
├── 📊 data/
│   ├── products_clean.json       # 143 products (465KB)
│   ├── product_embeddings.pkl    # Vectors (683KB)
│   └── youtube_knowledge.json    # Video transcripts
│
├── 🎨 ComfyUI/                   # Local only (not in git)
│   └── [FLUX models & workflows]
│
├── 📋 templates/web/
│   └── inbox.html                # Dashboard UI
│
└── 🔐 credentials/               # Git-ignored secrets
```

---

## 🚀 Quick Start

### 🎨 Start Image Generation (Mac)

```bash
# Double-click on Desktop:
iNeedHempChatBot.command
```

**You'll see:**
```
==================================================
  STARTING COMFYUI IMAGE SERVER
==================================================
   ComfyUI [█████████████████████████████] 100% Ready!
==================================================

==================================================
  CONNECTING COMFYUI TO VPS
==================================================
   ComfyUI tunnel ready (VPS:8188 → Mac:8188)
==================================================

==========================================
  IMAGE GENERATION ACTIVE
==========================================

  ComfyUI: Running locally
  Tunnel:  VPS:8188 → Mac:8188

  [23:41:02] ComfyUI: Online
  [23:42:02] ComfyUI: Online
```

### 🖥️ VPS Commands

```bash
# Check status
pm2 status

# View logs
pm2 logs chatbot --lines 50

# Restart
pm2 restart chatbot
```

---

## 🔒 Security

| Protection | Description |
|:-----------|:------------|
| 🛡️ **Rate Limit** | 20 chat/min, 5 images/min |
| 🚫 **Abuse Block** | Auto-block rapid requests |
| 🔐 **Order Verify** | Zip + Order # required |
| 📝 **Char Limit** | 1000 max per message |
| 🔒 **DM Privacy** | Order info via Discord DM |
| ✅ **Approval** | Emails require human OK |

---

## 📊 Stats

<table>
<tr>
<td align="center">

### 📦 Products
```
    143
```
*in database*

</td>
<td align="center">

### 🔑 Keywords
```
    355
```
*indexed*

</td>
<td align="center">

### 🗺️ Mappings
```
     24
```
*canonical*

</td>
<td align="center">

### 💾 Cache
```
   43KB
```
*instant answers*

</td>
</tr>
</table>

---

## 🛠️ Tech Stack

| Layer | Technology |
|:------|:-----------|
| 🧠 AI Brain | Claude 3.5 Haiku |
| 🔍 Search | Sentence Transformers + Hybrid |
| 💾 Cache | Python (43KB pre-built) |
| 🎨 Images | FLUX via ComfyUI |
| 📧 Email | Gmail API |
| 🛒 Orders | WooCommerce REST |
| 🖥️ Dashboard | Flask |
| ⚙️ Process | PM2 |
| ☁️ Host | Ubuntu VPS |

---

## 📞 Connect

<table>
<tr>
<td align="center">

### 📧 Email
**matt@ineedhemp.com**

</td>
<td align="center">

### 💬 Discord
**[Join Server](https://discord.com/invite/f3qwvp56be)**

</td>
<td align="center">

### 📱 Reddit
**[r/DivineTribeVaporizers](https://reddit.com/r/DivineTribeVaporizers)**

</td>
<td align="center">

### 🌐 Shop
**[ineedhemp.com](https://ineedhemp.com)**

</td>
</tr>
</table>

---

<p align="center">
  <b>Made with 💚 in Humboldt County, California</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production-brightgreen?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/AI-Claude_3.5-blueviolet?style=flat-square" alt="AI"/>
  <img src="https://img.shields.io/badge/Images-FLUX-orange?style=flat-square" alt="Images"/>
  <img src="https://img.shields.io/badge/RAG-5_Signal-green?style=flat-square" alt="RAG"/>
</p>

<p align="center">
  <i>When in doubt, flag for human review. Never send without approval.</i>
</p>
