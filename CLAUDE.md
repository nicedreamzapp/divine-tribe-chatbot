# Divine Tribe Email Assistant

AI-powered email handler for Divine Tribe customer support. Reads emails, drafts responses, requires human approval before sending.

## Project Status: PLANNING

**Phase 1:** WooCommerce Order Lookup
**Phase 2:** Gmail Integration
**Phase 3:** Approval System
**Phase 4:** Continuous Training

---

## Core Rules

### CRITICAL: Human Approval Required

**For the first month (minimum), ALL outgoing emails require Matt's approval.**

- Bot reads email
- Bot drafts response
- Bot sends draft to Matt (via Telegram/dashboard)
- Matt approves, edits, or rejects
- Only approved responses get sent

**No exceptions. No auto-send. Ever. Until explicitly enabled.**

---

## Customer Verification

Before providing ANY order information, verify identity:

**Option A:** Order Number + Zip Code
**Option B:** Last Name + Zip Code

```
Customer: "Where's my order?"
Bot: "I'd be happy to help! Please provide:
     - Your order number AND zip code, OR
     - Your last name AND zip code"
```

**Never reveal order details without verification.**

---

## Email Response Rules

### Tone & Voice
- Friendly, helpful, human-sounding
- Use customer's first name when available
- Sign off as "Matt" or "The Divine Tribe Team"
- Keep responses concise but complete

### What the Bot CAN Do
- Look up order status
- Provide tracking numbers
- Answer product questions (using Tribe Chatbot knowledge)
- Explain shipping timeframes
- Handle return/warranty inquiries
- Direct complex issues to Matt

### What the Bot CANNOT Do
- Issue refunds (flag for Matt)
- Make exceptions to policy (flag for Matt)
- Handle angry/escalated customers (flag for Matt)
- Discuss competitor products
- Make promises about delivery dates
- Share other customers' information

### Flagging for Human Review
These situations ALWAYS go to Matt, not auto-drafted:
- Angry or upset customer
- Refund requests over $50
- Legal threats or complaints
- Requests mentioning lawyers/BBB/chargebacks
- Anything the bot is unsure about
- Repeat complaints from same customer

---

## WooCommerce Integration

### API Access Needed
- **Consumer Key:** `ck_xxxx` (to be added)
- **Consumer Secret:** `cs_xxxx` (to be added)
- **Store URL:** `https://ineedhemp.com`
- **Permissions:** Read Only

### Order Data Available
- Order number
- Order status (processing, shipped, completed, refunded)
- Tracking number (if available)
- Items ordered
- Customer name & email
- Shipping address (zip for verification)
- Order date
- Order total

### Order Status Responses
```
Processing: "Your order is being prepared and will ship within 1-3 business days."
Shipped: "Your order has shipped! Tracking: {tracking_number}"
Completed: "Your order was delivered on {date}."
Refunded: "This order was refunded on {date}."
```

---

## Gmail Integration

### Scope
- Read incoming emails
- Draft responses (saved as drafts OR sent to approval queue)
- Send approved responses
- Label/archive handled emails

### Email Categories
1. **Order Status** - "Where's my order?" → Auto-draft with order lookup
2. **Product Questions** - Use Tribe Chatbot knowledge base
3. **Returns/Warranty** - Use standard policy responses
4. **Shipping Issues** - Lost/damaged packages
5. **Technical Support** - Device help, settings, troubleshooting
6. **Complaints** - Flag for Matt immediately
7. **Spam/Marketing** - Auto-archive, no response

### Gmail Labels (to be created)
- `Bot/Needs-Review` - Drafts waiting for approval
- `Bot/Approved` - Sent responses
- `Bot/Flagged` - Needs human attention
- `Bot/Auto-Archived` - Spam/marketing

---

## Approval Workflow

### Via Telegram (Recommended)
1. Email arrives in Gmail
2. Bot reads and drafts response
3. Bot sends to Matt via Telegram:
   ```
   📧 NEW EMAIL
   From: customer@email.com
   Subject: Where's my order #12345?

   --- CUSTOMER MESSAGE ---
   Hi, I ordered last week and haven't received shipping info...

   --- SUGGESTED RESPONSE ---
   Hi [Name],

   Your order #12345 shipped yesterday! Here's your tracking...

   [APPROVE] [EDIT] [FLAG]
   ```
4. Matt taps Approve → Bot sends email
5. Matt taps Edit → Opens edit interface
6. Matt taps Flag → Marks for manual handling

---

## Training & Improvement

### Feedback Loop
- Every approved response = positive training signal
- Every edited response = learn from correction
- Every rejected response = learn what NOT to do

### Monthly Review
- Review flagged emails
- Update response templates
- Add new FAQ answers
- Adjust tone/wording based on feedback

### Metrics to Track
- Emails handled per day
- Approval rate (approved vs edited vs rejected)
- Average response time
- Customer satisfaction (if measurable)

---

## Security & Privacy

### Data Protection
- Order data only shown to verified customers
- No storing of full credit card numbers
- Email content processed but not permanently stored
- API keys stored in environment variables, never in code

### Access Control
- Only Matt can approve/send emails
- Bot has read-only WooCommerce access
- Gmail access limited to support inbox only

---

## Integration with Tribe Chatbot

This system will use knowledge from the Tribe Chatbot:
- Product information
- Pricing and specs
- Community links (Discord, Reddit)
- Troubleshooting guides
- Policy information (shipping, returns, warranty)

**Reference:** `/Users/matthewmacosko/Desktop/Tribe Chatbot/`

---

## Setup Checklist

### WooCommerce
- [ ] Generate API keys (Read Only)
- [ ] Add keys to environment variables
- [ ] Test order lookup

### Gmail
- [ ] Create Google Cloud project
- [ ] Enable Gmail API
- [ ] Set up OAuth2 credentials
- [ ] Authorize app for Matt's Gmail
- [ ] Create email labels

### Telegram Bot
- [ ] Create new bot via BotFather (or reuse existing)
- [ ] Set up approval buttons
- [ ] Test notification flow

### Approval Dashboard (Optional)
- [ ] Web interface for reviewing emails
- [ ] Approve/Edit/Flag buttons
- [ ] History of handled emails

---

## Environment Variables Needed

```bash
# WooCommerce
WOOCOMMERCE_URL=https://ineedhemp.com
WOOCOMMERCE_KEY=ck_xxxx
WOOCOMMERCE_SECRET=cs_xxxx

# Gmail
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# Telegram
TELEGRAM_BOT_TOKEN=xxxx
TELEGRAM_CHAT_ID=xxxx

# Claude API (shared with chatbot)
ANTHROPIC_API_KEY=xxxx
```

---

## File Structure (Planned)

```
Divine Tribe Email Assistant/
├── CLAUDE.md              # This file - project rules & docs
├── email_assistant.py     # Main email handling script
├── woo_client.py          # WooCommerce API wrapper
├── gmail_client.py        # Gmail API wrapper
├── telegram_approval.py   # Telegram approval system
├── templates/             # Email response templates
│   ├── order_status.txt
│   ├── shipping_info.txt
│   ├── return_policy.txt
│   └── ...
├── .env                   # Environment variables (git-ignored)
└── requirements.txt       # Python dependencies
```

---

## Next Steps

1. **Matt provides:** WooCommerce API keys
2. **Build:** Order lookup module
3. **Matt provides:** Gmail API access (Google Cloud setup)
4. **Build:** Email reader + draft generator
5. **Build:** Telegram approval flow
6. **Test:** End-to-end with real emails
7. **Launch:** Start handling emails with 100% approval requirement

---

## Contact

Questions about this system: matt@ineedhemp.com

**Remember: When in doubt, flag for human review. Never send without approval.**
