#!/usr/bin/env python3
"""
Divine Tribe Email Assistant - Web Dashboard
Gmail-like interface for managing customer emails
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, session
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path for shared modules

load_dotenv()

# Get the project root directory

app = Flask(__name__,
            template_folder='templates/web',
            static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'divine-tribe-email-secret-2024')
CORS(app)

# =============================================================================
# AUTHENTICATION (Session-based)
# =============================================================================

DASHBOARD_USER = os.getenv('DASHBOARD_USER', 'tribe')
DASHBOARD_PASS = os.getenv('DASHBOARD_PASS', 'emails')

def requires_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == DASHBOARD_USER and password == DASHBOARD_PASS:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials'

    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - Divine Tribe Email Assistant</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                background: #1a1a2e;
                color: #eee;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .login-box {
                background: #16213e;
                padding: 40px;
                border-radius: 10px;
                width: 300px;
            }
            h1 { color: #facc15; font-size: 1.3rem; margin-bottom: 20px; text-align: center; }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #333;
                border-radius: 6px;
                background: #1a1a2e;
                color: #eee;
                font-size: 1rem;
                box-sizing: border-box;
            }
            input:focus { outline: none; border-color: #facc15; }
            button {
                width: 100%;
                padding: 12px;
                background: #facc15;
                color: #000;
                border: none;
                border-radius: 6px;
                font-size: 1rem;
                font-weight: bold;
                cursor: pointer;
                margin-top: 10px;
            }
            button:hover { background: #fbbf24; }
            .error { color: #ef4444; text-align: center; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>Divine Tribe Email Assistant</h1>
            ''' + (f'<p class="error">{error}</p>' if error else '') + '''
            <form method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    '''


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

# Smart responder (lazy load)
_smart_responder = None

def get_smart_responder():
    global _smart_responder
    if _smart_responder is None:
        try:
            from smart_responder import generate_email_response, log_email_interaction
            _smart_responder = {
                'generate': generate_email_response,
                'log': log_email_interaction
            }
            print("Smart responder loaded (RAG + CAG + WooCommerce)")
        except Exception as e:
            print(f"Smart responder not available: {e}")
            _smart_responder = {'generate': None, 'log': None}
    return _smart_responder

# Initialize Gmail client (lazy load to avoid startup issues)
gmail_client = None

def get_gmail_client():
    """Get or create Gmail client"""
    global gmail_client
    if gmail_client is None:
        try:
            from gmail_client import GmailClient
            gmail_client = GmailClient()
            print("✅ Gmail client initialized")
        except Exception as e:
            print(f"⚠️ Gmail client not available: {e}")
    return gmail_client

# Database setup
DB_PATH = 'email_history.db'


def init_db():
    """Initialize SQLite database for email history"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Emails table
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            thread_id TEXT,
            from_email TEXT,
            from_name TEXT,
            subject TEXT,
            body TEXT,
            received_at TIMESTAMP,
            status TEXT DEFAULT 'unread',
            category TEXT,
            draft_response TEXT,
            sent_response TEXT,
            responded_at TIMESTAMP,
            order_number TEXT,
            thread_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add thread_count column if it doesn't exist (for existing databases)
    try:
        c.execute('ALTER TABLE emails ADD COLUMN thread_count INTEGER DEFAULT 1')
    except:
        pass  # Column already exists

    # Customer history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            email TEXT PRIMARY KEY,
            name TEXT,
            total_orders INTEGER DEFAULT 0,
            total_spent REAL DEFAULT 0,
            first_contact TIMESTAMP,
            last_contact TIMESTAMP,
            notes TEXT
        )
    ''')

    # Actions log
    c.execute('''
        CREATE TABLE IF NOT EXISTS actions_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT,
            action TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized")


init_db()


# =============================================================================
# DATABASE HELPERS
# =============================================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def save_email(email_data):
    """Save an email to the database"""
    conn = get_db()
    c = conn.cursor()

    c.execute('''
        INSERT OR REPLACE INTO emails
        (id, thread_id, from_email, from_name, subject, body, received_at, status, category, draft_response, order_number, thread_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        email_data.get('id'),
        email_data.get('thread_id'),
        email_data.get('from_email'),
        email_data.get('from_name', ''),
        email_data.get('subject'),
        email_data.get('body'),
        email_data.get('received_at', datetime.now().isoformat()),
        email_data.get('status', 'unread'),
        email_data.get('category', 'general'),
        email_data.get('draft_response'),
        email_data.get('order_number'),
        email_data.get('thread_count', 1)
    ))

    # Update customer record
    c.execute('''
        INSERT OR REPLACE INTO customers (email, name, last_contact, first_contact)
        VALUES (?, ?, ?, COALESCE((SELECT first_contact FROM customers WHERE email = ?), ?))
    ''', (
        email_data.get('from_email'),
        email_data.get('from_name'),
        datetime.now().isoformat(),
        email_data.get('from_email'),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_emails(status=None, limit=50):
    """Get emails from database"""
    conn = get_db()
    c = conn.cursor()

    if status:
        c.execute('SELECT * FROM emails WHERE status = ? ORDER BY received_at DESC LIMIT ?', (status, limit))
    else:
        c.execute('SELECT * FROM emails ORDER BY received_at DESC LIMIT ?', (limit,))

    emails = [dict(row) for row in c.fetchall()]
    conn.close()
    return emails


def get_email(email_id):
    """Get single email by ID"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM emails WHERE id = ?', (email_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def update_email_status(email_id, status):
    """Update email status"""
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE emails SET status = ? WHERE id = ?', (status, email_id))
    conn.commit()
    conn.close()


def save_sent_response(email_id, response):
    """Save the sent response"""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        UPDATE emails
        SET sent_response = ?, responded_at = ?, status = 'sent'
        WHERE id = ?
    ''', (response, datetime.now().isoformat(), email_id))
    conn.commit()
    conn.close()


def log_action(email_id, action, details=''):
    """Log an action for audit trail"""
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO actions_log (email_id, action, details) VALUES (?, ?, ?)',
              (email_id, action, details))
    conn.commit()
    conn.close()


def get_customer_history(email):
    """Get all emails from a customer"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM emails WHERE from_email = ? ORDER BY received_at DESC', (email,))
    emails = [dict(row) for row in c.fetchall()]
    conn.close()
    return emails


# =============================================================================
# AI RESPONSE GENERATION (Smart - uses RAG, CAG, WooCommerce)
# =============================================================================

def generate_response(email_data):
    """Generate smart AI response using RAG, CAG, and WooCommerce"""
    responder = get_smart_responder()

    if responder['generate']:
        try:
            result = responder['generate'](email_data)
            return result.get('response'), result
        except Exception as e:
            print(f"Smart responder error: {e}")

    # Fallback to basic response if smart responder fails
    return _basic_response(email_data), {'intent': 'unknown', 'used_cag': False, 'used_rag': False, 'used_woo': False}


def _basic_response(email_data):
    """Fallback basic response if smart responder unavailable"""
    import anthropic
    claude = anthropic.Anthropic()

    try:
        response = claude.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            system="You are Matt's email assistant for Divine Tribe (ineedhemp.com). Be friendly and helpful. Sign as Matt.",
            messages=[{
                'role': 'user',
                'content': f"Reply to: {email_data.get('subject')}\n\n{email_data.get('body')}"
            }]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Basic response error: {e}")
        return None


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
@requires_auth
def index():
    """Main inbox view"""
    return render_template('inbox.html')


@app.route('/api/emails')
@requires_auth
def api_get_emails():
    """Get emails API"""
    status = request.args.get('status')
    emails = get_emails(status=status)
    return jsonify(emails)


@app.route('/api/emails/<email_id>')
@requires_auth
def api_get_email(email_id):
    """Get single email"""
    email = get_email(email_id)
    if email:
        return jsonify(email)
    return jsonify({'error': 'Not found'}), 404


@app.route('/api/emails/<email_id>/thread')
@requires_auth
def api_get_thread(email_id):
    """Get full thread conversation for an email"""
    email = get_email(email_id)
    if not email:
        return jsonify({'error': 'Not found'}), 404

    thread_id = email.get('thread_id')
    if not thread_id:
        # No thread, return single message
        return jsonify({
            'thread': [{
                'from': email.get('from_name') or email.get('from_email'),
                'from_email': email.get('from_email'),
                'date': email.get('received_at'),
                'body': email.get('body'),
                'is_customer': True
            }]
        })

    # Try to get full thread from Gmail
    gmail = get_gmail_client()
    if not gmail:
        return jsonify({
            'thread': [{
                'from': email.get('from_name') or email.get('from_email'),
                'from_email': email.get('from_email'),
                'date': email.get('received_at'),
                'body': email.get('body'),
                'is_customer': True
            }]
        })

    try:
        thread_messages = gmail.get_thread(thread_id)
        my_email = os.getenv('GMAIL_ADDRESS', 'divinetribe@ineedhemp.com').lower()

        formatted = []
        for msg in thread_messages:
            from_email = (msg.get('from_email') or '').lower()
            is_customer = my_email not in from_email and 'ineedhemp.com' not in from_email

            # Clean the body
            body = msg.get('body', '')
            if hasattr(gmail, '_clean_body'):
                body = gmail._clean_body(body)

            formatted.append({
                'from': msg.get('from', msg.get('from_email')),
                'from_email': msg.get('from_email'),
                'date': msg.get('date'),
                'body': body,
                'is_customer': is_customer
            })

        return jsonify({'thread': formatted, 'thread_count': len(formatted)})

    except Exception as e:
        print(f"Thread fetch error: {e}")
        return jsonify({
            'thread': [{
                'from': email.get('from_name') or email.get('from_email'),
                'from_email': email.get('from_email'),
                'date': email.get('received_at'),
                'body': email.get('body'),
                'is_customer': True
            }]
        })


@app.route('/api/emails/<email_id>/generate', methods=['POST'])
@requires_auth
def api_generate_response(email_id):
    """Generate smart AI response for email with full thread context"""
    email = get_email(email_id)
    if not email:
        return jsonify({'error': 'Not found'}), 404

    # Get full thread context for better AI responses
    thread_id = email.get('thread_id')
    thread_context = ""
    if thread_id:
        gmail = get_gmail_client()
        if gmail:
            try:
                thread_messages = gmail.get_thread(thread_id)
                my_email = os.getenv('GMAIL_ADDRESS', 'divinetribe@ineedhemp.com').lower()

                # Build conversation context (oldest first for context)
                parts = []
                for msg in thread_messages:
                    from_email = (msg.get('from_email') or '').lower()
                    sender = "CUSTOMER" if my_email not in from_email and 'ineedhemp.com' not in from_email else "DIVINE TRIBE"
                    body = msg.get('body', '')
                    if hasattr(gmail, '_clean_body'):
                        body = gmail._clean_body(body)
                    parts.append(f"[{sender}]: {body[:1500]}")  # Limit each message

                thread_context = "\n\n---\n\n".join(parts)
            except Exception as e:
                print(f"Thread context error: {e}")

    # Add thread context to email data for the responder
    email_with_context = dict(email)
    if thread_context:
        email_with_context['thread_context'] = thread_context
        email_with_context['body'] = f"FULL CONVERSATION THREAD:\n\n{thread_context}\n\n---\nLATEST MESSAGE TO RESPOND TO:\n{email.get('body', '')}"

    response, metadata = generate_response(email_with_context)
    if response:
        # Save draft and metadata
        conn = get_db()
        c = conn.cursor()
        c.execute('UPDATE emails SET draft_response = ?, category = ? WHERE id = ?',
                  (response, metadata.get('intent', 'general'), email_id))
        conn.commit()
        conn.close()

        return jsonify({
            'draft': response,
            'intent': metadata.get('intent'),
            'used_cag': metadata.get('used_cag'),
            'used_rag': metadata.get('used_rag'),
            'used_woo': metadata.get('used_woo'),
            'order_info': metadata.get('order_info')
        })
    return jsonify({'error': 'Could not generate response'}), 500


@app.route('/api/emails/<email_id>/done', methods=['POST'])
@requires_auth
def api_mark_done(email_id):
    """Mark email as done and log for learning (NO Gmail interaction)"""
    data = request.json
    response_text = data.get('response', '')
    was_edited = data.get('was_edited', False)

    email = get_email(email_id)
    if not email:
        return jsonify({'error': 'Not found'}), 404

    # Log for learning - track if response was edited
    responder = get_smart_responder()
    if responder['log']:
        try:
            feedback = 'edited' if was_edited else 'approved'
            responder['log'](email, response_text, {'intent': email.get('category')}, feedback)
        except Exception as e:
            print(f"Logging error: {e}")

    # Just update local status - NO Gmail interaction
    save_sent_response(email_id, response_text)
    log_action(email_id, 'marked_done', f'Draft created for {email.get("from_email")}')

    return jsonify({'success': True, 'message': 'Marked as done'})


@app.route('/api/emails/<email_id>/status', methods=['POST'])
@requires_auth
def api_update_status(email_id):
    """Update email status (read, archived, deleted, flagged)"""
    data = request.json
    status = data.get('status')

    if status not in ['unread', 'read', 'archived', 'deleted', 'flagged', 'sent']:
        return jsonify({'error': 'Invalid status'}), 400

    update_email_status(email_id, status)
    log_action(email_id, f'status_changed', f'Changed to {status}')

    return jsonify({'success': True})


@app.route('/api/emails/bulk', methods=['POST'])
@requires_auth
def api_bulk_action():
    """Bulk actions on multiple emails"""
    data = request.json
    email_ids = data.get('ids', [])
    action = data.get('action')

    for email_id in email_ids:
        if action == 'delete':
            update_email_status(email_id, 'deleted')
        elif action == 'archive':
            update_email_status(email_id, 'archived')
        elif action == 'read':
            update_email_status(email_id, 'read')
        elif action == 'flag':
            update_email_status(email_id, 'flagged')

        log_action(email_id, f'bulk_{action}', '')

    return jsonify({'success': True, 'count': len(email_ids)})


# =============================================================================
# AUTO-READ TRAINING - Mark emails as "just read" and train the system
# =============================================================================

# Lazy load trainer
_trainer = None

def get_trainer():
    """Get or create the auto-read trainer"""
    global _trainer
    if _trainer is None:
        try:
            from training import AutoReadTrainer
            _trainer = AutoReadTrainer()
        except Exception as e:
            print(f"⚠️ Trainer not available: {e}")
    return _trainer


@app.route('/api/emails/mark-auto-read', methods=['POST'])
@requires_auth
def api_mark_auto_read():
    """
    Mark selected emails as 'just read' - no response needed.
    Also trains the system to auto-read future emails from these senders.
    """
    data = request.json
    email_ids = data.get('ids', [])

    if not email_ids:
        return jsonify({'error': 'No emails selected'}), 400

    gmail = get_gmail_client()
    trainer = get_trainer()
    trained_count = 0

    for email_id in email_ids:
        # Get email data from database
        email = get_email(email_id)
        if not email:
            continue

        # Train the system on this sender
        if trainer:
            trainer.add_sender(email)
            trained_count += 1

        # Mark as read in Gmail (if connected)
        if gmail:
            try:
                gmail.mark_as_read(email_id)
                gmail.add_label(email_id, 'Bot/Auto-Read')
            except Exception as e:
                print(f"Gmail error for {email_id}: {e}")

        # Update local database
        update_email_status(email_id, 'read')
        log_action(email_id, 'marked_auto_read', f'Trained sender: {email.get("from_email")}')

    return jsonify({
        'success': True,
        'count': len(email_ids),
        'trained': trained_count
    })


@app.route('/api/customer/<email>')
@requires_auth
def api_customer_history(email):
    """Get customer history"""
    history = get_customer_history(email)
    return jsonify(history)


@app.route('/api/stats')
@requires_auth
def api_stats():
    """Get dashboard stats"""
    conn = get_db()
    c = conn.cursor()

    stats = {}

    c.execute('SELECT COUNT(*) FROM emails WHERE status = "unread"')
    stats['unread'] = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM emails WHERE status = "flagged"')
    stats['flagged'] = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM emails WHERE status = "sent"')
    stats['sent_today'] = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM emails')
    stats['total'] = c.fetchone()[0]

    conn.close()
    return jsonify(stats)


@app.route('/api/refresh', methods=['POST'])
@requires_auth
def api_refresh_emails():
    """Fetch unread emails from Gmail - clears old data and gets fresh list"""
    gmail = get_gmail_client()
    if not gmail:
        return jsonify({'error': 'Gmail not connected'}), 500

    # Clear old emails for a fresh start
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM emails WHERE status = "unread"')
    conn.commit()
    conn.close()

    emails = gmail.get_unread_emails(max_results=100)
    new_count = 0

    for e in emails:
        # Extract sender name from "Name <email>" format
        from_name = ''
        from_field = e.get('from', '')
        if '<' in from_field:
            from_name = from_field.split('<')[0].strip().strip('"')

        save_email({
            'id': e['id'],
            'thread_id': e.get('thread_id'),
            'from_email': e.get('from_email'),
            'from_name': from_name,
            'subject': e.get('subject'),
            'body': e.get('body', e.get('snippet', '')),
            'received_at': e.get('date'),
            'status': 'unread',
            'thread_count': 1  # Will be fetched when viewing thread
        })
        new_count += 1

    return jsonify({'success': True, 'new_emails': new_count})


# =============================================================================
# TRAINING DATA - Save good responses for RAG/CAG learning
# =============================================================================

TRAINING_FILE = 'training_responses.json'

def load_training_data():
    """Load existing training data"""
    if os.path.exists(TRAINING_FILE):
        try:
            with open(TRAINING_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'responses': [], 'stats': {'total': 0, 'edited': 0, 'approved': 0}}

def save_training_data(data):
    """Save training data to file"""
    with open(TRAINING_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@app.route('/api/emails/<email_id>/save-training', methods=['POST'])
@requires_auth
def api_save_training(email_id):
    """Save a good response for training the AI - with PII stripped"""
    data = request.json
    response_text = data.get('response', '')
    was_edited = data.get('was_edited', False)
    original_draft = data.get('original_draft', '')

    email = get_email(email_id)
    if not email:
        return jsonify({'error': 'Not found'}), 404

    if not response_text.strip():
        return jsonify({'error': 'No response to save'}), 400

    # Import privacy module for PII stripping
    try:
        from modules.privacy import strip_pii, hash_email
    except:
        # Fallback if module not available
        strip_pii = lambda x: x
        hash_email = lambda x: x[:8] + '...' if x else ''

    # Load existing training data
    training = load_training_data()

    # Create training example with PII STRIPPED
    example = {
        'id': email_id,
        'timestamp': datetime.now().isoformat(),
        'customer_hash': hash_email(email.get('from_email', '')),  # Hash, not actual email
        'subject': strip_pii(email.get('subject', '')),  # Strip PII
        'customer_message': strip_pii(email.get('body', '')),  # Strip PII
        'approved_response': strip_pii(response_text),  # Strip PII
        'was_edited': was_edited,
        'original_draft': strip_pii(original_draft) if was_edited else None,
        'category': email.get('category', 'general')
    }

    # Add to training data
    training['responses'].append(example)
    training['stats']['total'] += 1
    if was_edited:
        training['stats']['edited'] += 1
    else:
        training['stats']['approved'] += 1

    # Save to file
    save_training_data(training)

    # Log the action
    log_action(email_id, 'saved_for_training', f'Edited: {was_edited}')

    return jsonify({
        'success': True,
        'total_saved': training['stats']['total'],
        'message': 'Saved for training!'
    })


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("📧 DIVINE TRIBE EMAIL DASHBOARD")
    print("=" * 60)
    print("Open: http://localhost:5002")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5002, debug=True)
