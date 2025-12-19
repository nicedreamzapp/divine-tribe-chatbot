"""
Gmail Client - Read and send emails
Divine Tribe Email Assistant
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, List
from datetime import datetime
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

# Gmail API scopes - what we're allowed to do
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',      # Read emails
    'https://www.googleapis.com/auth/gmail.send',          # Send emails
    'https://www.googleapis.com/auth/gmail.modify',        # Modify labels
    'https://www.googleapis.com/auth/gmail.labels',        # Manage labels
]


class GmailClient:
    """Handle all Gmail API interactions"""

    def __init__(self):
        self.credentials_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.json')
        self.email_address = os.getenv('GMAIL_ADDRESS', 'matt@ineedhemp.com')
        self.service = None
        self.labels = {}  # Cache label IDs

        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"❌ Missing {self.credentials_file} - Download from Google Cloud Console")
                    return

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for next time
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail client authenticated")
            self._cache_labels()
        except Exception as e:
            print(f"❌ Gmail authentication failed: {e}")

    def _cache_labels(self):
        """Cache label IDs for quick access"""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            for label in results.get('labels', []):
                self.labels[label['name']] = label['id']
        except Exception as e:
            print(f"⚠️  Could not cache labels: {e}")

    def create_label(self, label_name: str) -> Optional[str]:
        """Create a Gmail label if it doesn't exist"""
        if label_name in self.labels:
            return self.labels[label_name]

        try:
            label = self.service.users().labels().create(
                userId='me',
                body={
                    'name': label_name,
                    'labelListVisibility': 'labelShow',
                    'messageListVisibility': 'show'
                }
            ).execute()
            self.labels[label_name] = label['id']
            print(f"✅ Created label: {label_name}")
            return label['id']
        except Exception as e:
            print(f"❌ Could not create label {label_name}: {e}")
            return None

    def setup_labels(self):
        """Create all required labels for the email assistant"""
        required_labels = [
            'Bot/Needs-Review',
            'Bot/Approved',
            'Bot/Flagged',
            'Bot/Auto-Archived',
            'Bot/Auto-Read',
            'Bot/Processed',
            'Train-AutoRead',  # Label for training: mark emails to auto-read in future
        ]
        for label in required_labels:
            self.create_label(label)
        print("✅ All bot labels ready")

    def get_emails_by_label(self, label_name: str, max_results: int = 50) -> List[Dict]:
        """Get emails with a specific label"""
        if not self.service:
            return []

        label_id = self.labels.get(label_name)
        if not label_id:
            return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=[label_id],
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                email_data = self.get_email(msg['id'])
                if email_data:
                    emails.append(email_data)

            return emails

        except HttpError as e:
            print(f"❌ Error fetching emails by label: {e}")
            return []

    def get_unread_emails(self, max_results: int = 20) -> List[Dict]:
        """
        Get unread emails from inbox - ONE per thread (latest message only)
        Returns list of email dictionaries
        """
        if not self.service:
            return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_results * 5  # Fetch more to account for threads
            ).execute()

            messages = results.get('messages', [])
            threads = {}  # thread_id -> latest email

            for msg in messages:
                email_data = self.get_email(msg['id'])
                if email_data:
                    thread_id = email_data.get('thread_id')
                    if thread_id:
                        # Always keep the latest (messages are returned newest first by Gmail)
                        # But we want the last customer message, so we update if this is newer
                        if thread_id not in threads:
                            threads[thread_id] = email_data

            # Return as list, limited to max_results
            emails = list(threads.values())[:max_results]
            return emails

        except HttpError as e:
            print(f"❌ Error fetching emails: {e}")
            return []

    def get_thread(self, thread_id: str) -> List[Dict]:
        """
        Get all messages in a thread (full conversation history)
        Returns list of email dictionaries, oldest first
        """
        if not self.service:
            return []

        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            ).execute()

            messages = []
            for msg in thread.get('messages', []):
                email_data = self._parse_message(msg)
                if email_data:
                    messages.append(email_data)

            # Sort by date (oldest first for conversation flow)
            # Messages are typically returned in order, but let's be safe
            return messages

        except HttpError as e:
            print(f"❌ Error fetching thread {thread_id}: {e}")
            return []

    def _parse_message(self, message: Dict) -> Optional[Dict]:
        """Parse a Gmail message object into our email format"""
        headers = message.get('payload', {}).get('headers', [])

        email_data = {
            'id': message.get('id'),
            'thread_id': message.get('threadId'),
            'snippet': message.get('snippet', ''),
            'labels': message.get('labelIds', []),
            'date': None,
            'from': None,
            'from_email': None,
            'to': None,
            'subject': None,
            'body': None,
            'internal_date': message.get('internalDate', 0)  # Unix timestamp for sorting
        }

        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')

            if name == 'from':
                email_data['from'] = value
                if '<' in value:
                    email_data['from_email'] = value.split('<')[1].rstrip('>')
                else:
                    email_data['from_email'] = value
            elif name == 'to':
                email_data['to'] = value
            elif name == 'subject':
                email_data['subject'] = value
            elif name == 'date':
                email_data['date'] = value

        email_data['body'] = self._get_body(message.get('payload', {}))
        return email_data

    def format_thread_as_conversation(self, thread_messages: List[Dict], my_email: str = None) -> str:
        """
        Format a list of thread messages as a readable conversation
        Marks messages as [CUSTOMER] or [YOU] based on sender
        """
        if not my_email:
            my_email = self.email_address.lower()
        else:
            my_email = my_email.lower()

        conversation = []
        for msg in thread_messages:
            from_email = (msg.get('from_email') or '').lower()
            date = msg.get('date', 'Unknown date')
            body = msg.get('body', '').strip()

            # Clean up the body - remove quoted replies
            body = self._clean_body(body)

            if my_email in from_email or 'ineedhemp.com' in from_email:
                sender = "[DIVINE TRIBE / YOU]"
            else:
                sender = f"[CUSTOMER: {msg.get('from', from_email)}]"

            conversation.append(f"{sender}\nDate: {date}\n\n{body}")

        separator = "\n\n" + "="*50 + "\n\n"
        return separator.join(conversation)

    def _clean_body(self, body: str) -> str:
        """Remove quoted reply text from email body"""
        import re

        # Common patterns for quoted replies
        patterns = [
            r'\n>.*',  # Lines starting with >
            r'\nOn .* wrote:.*',  # "On [date] [person] wrote:"
            r'\n-+\s*Original Message\s*-+.*',  # Original Message dividers
            r'\n_{10,}.*',  # Long underscore dividers
            r'\nFrom:.*Sent:.*To:.*Subject:.*',  # Outlook-style headers
        ]

        # Find the earliest occurrence of any pattern
        earliest = len(body)
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
            if match and match.start() < earliest:
                earliest = match.start()

        # Return text before quoted content
        return body[:earliest].strip()

    def get_email(self, message_id: str) -> Optional[Dict]:
        """
        Get full email details by message ID
        """
        if not self.service:
            return None

        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message.get('payload', {}).get('headers', [])

            # Extract headers
            email_data = {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', []),
                'date': None,
                'from': None,
                'from_email': None,
                'to': None,
                'subject': None,
                'body': None
            }

            for header in headers:
                name = header.get('name', '').lower()
                value = header.get('value', '')

                if name == 'from':
                    email_data['from'] = value
                    # Extract just the email address
                    if '<' in value:
                        email_data['from_email'] = value.split('<')[1].rstrip('>')
                    else:
                        email_data['from_email'] = value
                elif name == 'to':
                    email_data['to'] = value
                elif name == 'subject':
                    email_data['subject'] = value
                elif name == 'date':
                    email_data['date'] = value

            # Extract body
            email_data['body'] = self._get_body(message.get('payload', {}))

            return email_data

        except HttpError as e:
            print(f"❌ Error fetching email {message_id}: {e}")
            return None

    def _get_body(self, payload: Dict) -> str:
        """Extract email body from payload - handles nested multipart structures"""
        # Try direct body first
        if 'body' in payload and payload['body'].get('data'):
            try:
                return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            except:
                pass

        # Handle multipart - recursively search for text content
        if 'parts' in payload:
            plain_text = None
            html_text = None

            for part in payload['parts']:
                mime_type = part.get('mimeType', '')

                # Direct text content
                if mime_type == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        try:
                            plain_text = base64.urlsafe_b64decode(data).decode('utf-8')
                        except:
                            pass

                elif mime_type == 'text/html':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        try:
                            html_text = base64.urlsafe_b64decode(data).decode('utf-8')
                        except:
                            pass

                # Nested multipart (multipart/alternative, multipart/related, etc.)
                elif mime_type.startswith('multipart/') or 'parts' in part:
                    nested = self._get_body(part)
                    if nested:
                        if not plain_text:
                            plain_text = nested

            # Prefer plain text, fallback to HTML
            return plain_text or html_text or ""

        return ""

    def send_email(self, to: str, subject: str, body: str, thread_id: str = None) -> bool:
        """
        Send an email
        If thread_id provided, sends as reply in that thread
        """
        if not self.service:
            return False

        try:
            message = MIMEMultipart()
            message['to'] = to
            message['from'] = self.email_address
            message['subject'] = subject

            message.attach(MIMEText(body, 'plain'))

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            send_body = {'raw': raw}
            if thread_id:
                send_body['threadId'] = thread_id

            self.service.users().messages().send(
                userId='me',
                body=send_body
            ).execute()

            print(f"✅ Email sent to {to}")
            return True

        except HttpError as e:
            print(f"❌ Error sending email: {e}")
            return False

    def create_draft(self, to: str, subject: str, body: str, thread_id: str = None) -> Optional[str]:
        """
        Create a draft email (doesn't send)
        Returns draft ID
        """
        if not self.service:
            return None

        try:
            message = MIMEMultipart()
            message['to'] = to
            message['from'] = self.email_address
            message['subject'] = subject

            message.attach(MIMEText(body, 'plain'))

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            draft_body = {'message': {'raw': raw}}
            if thread_id:
                draft_body['message']['threadId'] = thread_id

            draft = self.service.users().drafts().create(
                userId='me',
                body=draft_body
            ).execute()

            print(f"✅ Draft created for {to}")
            return draft['id']

        except HttpError as e:
            print(f"❌ Error creating draft: {e}")
            return None

    def send_draft(self, draft_id: str) -> bool:
        """Send an existing draft"""
        if not self.service:
            return False

        try:
            self.service.users().drafts().send(
                userId='me',
                body={'id': draft_id}
            ).execute()
            print(f"✅ Draft {draft_id} sent")
            return True
        except HttpError as e:
            print(f"❌ Error sending draft: {e}")
            return False

    def delete_draft(self, draft_id: str) -> bool:
        """Delete a draft"""
        if not self.service:
            return False

        try:
            self.service.users().drafts().delete(
                userId='me',
                id=draft_id
            ).execute()
            return True
        except HttpError as e:
            print(f"❌ Error deleting draft: {e}")
            return False

    def add_label(self, message_id: str, label_name: str) -> bool:
        """Add a label to an email"""
        if not self.service:
            return False

        label_id = self.labels.get(label_name)
        if not label_id:
            label_id = self.create_label(label_name)

        if not label_id:
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            return True
        except HttpError as e:
            print(f"❌ Error adding label: {e}")
            return False

    def remove_label(self, message_id: str, label_name: str) -> bool:
        """Remove a label from an email"""
        if not self.service:
            return False

        label_id = self.labels.get(label_name)
        if not label_id:
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': [label_id]}
            ).execute()
            return True
        except HttpError as e:
            print(f"❌ Error removing label: {e}")
            return False

    def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read"""
        if not self.service:
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as e:
            print(f"❌ Error marking as read: {e}")
            return False

    def archive_email(self, message_id: str) -> bool:
        """Archive an email (remove from inbox)"""
        if not self.service:
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except HttpError as e:
            print(f"❌ Error archiving email: {e}")
            return False

    def test_connection(self) -> bool:
        """Test if Gmail API connection works"""
        if not self.service:
            return False

        try:
            profile = self.service.users().getProfile(userId='me').execute()
            print(f"✅ Gmail connected: {profile.get('emailAddress')}")
            print(f"   Total messages: {profile.get('messagesTotal')}")
            return True
        except HttpError as e:
            print(f"❌ Gmail connection test failed: {e}")
            return False


# Quick test
if __name__ == "__main__":
    client = GmailClient()

    if client.test_connection():
        client.setup_labels()

        print("\n📧 Recent unread emails:")
        emails = client.get_unread_emails(5)
        for email in emails:
            print(f"  From: {email.get('from_email')}")
            print(f"  Subject: {email.get('subject')}")
            print(f"  Preview: {email.get('snippet', '')[:80]}...")
            print()
    else:
        print("⚠️  Set up Gmail API credentials first")
        print("   1. Go to Google Cloud Console")
        print("   2. Create project, enable Gmail API")
        print("   3. Create OAuth credentials")
        print("   4. Download as credentials.json")
