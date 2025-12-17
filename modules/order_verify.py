#!/usr/bin/env python3
"""
Secure Order Verification Module
Used by both Email Support and Chatbot
"""

import os
import re
from typing import Dict, Optional, Tuple
from datetime import datetime

# Try to import WooCommerce client
try:
    from woo_client import WooCommerceClient
    _woo = None
except:
    try:
        from email.woo_client import WooCommerceClient
        _woo = None
    except:
        WooCommerceClient = None
        _woo = None


def get_woo():
    """Get or create WooCommerce client"""
    global _woo
    if _woo is None and WooCommerceClient:
        try:
            _woo = WooCommerceClient()
        except Exception as e:
            print(f"WooCommerce not available: {e}")
    return _woo


# =============================================================================
# ORDER LOOKUP
# =============================================================================

def extract_order_number(text: str) -> Optional[str]:
    """Extract order number from text"""
    patterns = [
        r'#(\d{5,7})',
        r'order\s*#?\s*(\d{5,7})',
        r'order\s+number\s*:?\s*(\d{5,7})',
        r'\b(\d{6})\b',  # 6 digit numbers are likely order numbers
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1)
    return None


def lookup_order(order_number: str) -> Optional[Dict]:
    """
    Look up order from WooCommerce.
    Returns order data if found, None if not.
    """
    woo = get_woo()
    if not woo:
        return None

    try:
        order = woo.get_order(order_number)
        if order:
            return order
    except Exception as e:
        print(f"Order lookup error: {e}")

    return None


# =============================================================================
# VERIFICATION
# =============================================================================

def get_verification_challenge(order: Dict) -> Dict:
    """
    Generate a verification challenge for the customer.
    Returns masked hints they need to confirm.
    """
    billing = order.get('billing', {})
    shipping = order.get('shipping', {})

    # Get zip code - prefer billing (usually simpler 5-digit), fall back to shipping
    # Also store both for verification
    billing_zip = billing.get('postcode') or ''
    shipping_zip = shipping.get('postcode') or ''
    zip_code = billing_zip or shipping_zip  # Use billing first (usually 5-digit)

    # Get last name
    last_name = shipping.get('last_name') or billing.get('last_name') or ''

    # Get email
    email = billing.get('email', '')

    # Create masked versions - only use first 5 digits of zip
    zip_5 = zip_code.replace('-', '').replace(' ', '')[:5]
    masked_zip = f"**{zip_5[-3:]}" if len(zip_5) >= 3 else "***"
    masked_email = mask_email(email)
    masked_name = f"{last_name[0]}***" if last_name else "***"

    return {
        'order_id': order.get('id'),
        'order_number': str(order.get('id')),
        'zip_hint': masked_zip,
        'email_hint': masked_email,
        'name_hint': masked_name,
        # Store actual values for verification (don't send to client)
        '_zip': zip_code.lower().replace(' ', '').replace('-', ''),
        '_billing_zip': billing_zip.lower().replace(' ', '').replace('-', ''),
        '_shipping_zip': shipping_zip.lower().replace(' ', '').replace('-', ''),
        '_email': email.lower().strip(),
        '_last_name': last_name.lower().strip(),
    }


def mask_email(email: str) -> str:
    """Mask an email like j***n@gmail.com"""
    if not email or '@' not in email:
        return "***@***.***"

    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + "***"
    else:
        masked_local = local[0] + "***" + local[-1]

    return f"{masked_local}@{domain}"


def verify_customer(challenge: Dict, answer: str, method: str = 'auto') -> bool:
    """
    Verify customer's answer against the challenge.

    Methods:
    - 'auto': Try all methods (zip, email, name) - RECOMMENDED
    - 'zip': Verify zip code only
    - 'email': Verify email address only
    - 'name': Verify last name only
    """
    answer_clean = answer.lower().strip().replace(' ', '')

    if method == 'auto':
        # Try all verification methods - customer can provide any one
        # Check zip codes - only first 5 digits matter
        zips_to_check = [
            challenge.get('_zip', ''),
            challenge.get('_billing_zip', ''),
            challenge.get('_shipping_zip', '')
        ]
        answer_zip = answer_clean.replace('-', '')[:5]  # First 5 digits only
        for expected_zip in zips_to_check:
            expected_5 = expected_zip[:5] if expected_zip else ''
            if expected_5 and answer_zip == expected_5:
                return True

        # Check email
        expected_email = challenge.get('_email', '')
        if expected_email and answer_clean == expected_email:
            return True

        # Check last name
        expected_name = challenge.get('_last_name', '')
        if expected_name and answer_clean == expected_name:
            return True

        return False

    elif method == 'zip':
        expected = challenge.get('_zip', '')
        return answer_clean == expected or expected.endswith(answer_clean) or answer_clean.endswith(expected[-3:])

    elif method == 'email':
        expected = challenge.get('_email', '')
        return answer_clean == expected

    elif method == 'name':
        expected = challenge.get('_last_name', '')
        return answer_clean == expected

    return False


# =============================================================================
# ORDER INFO (after verification)
# =============================================================================

def get_safe_order_info(order: Dict) -> Dict:
    """
    Get order info that's safe to share after verification.
    Excludes sensitive payment details.
    """
    # Get line items
    items = []
    for item in order.get('line_items', []):
        items.append({
            'name': item.get('name'),
            'quantity': item.get('quantity'),
            'total': item.get('total')
        })

    # Get tracking info from meta
    tracking = None
    tracking_provider = None
    for meta in order.get('meta_data', []):
        key = meta.get('key', '')
        value = meta.get('value')

        # Check for WooCommerce Shipment Tracking plugin format
        if key == '_wc_shipment_tracking_items' and value:
            # This is stored as a list of tracking items
            if isinstance(value, list) and len(value) > 0:
                tracking_item = value[0]  # Get first tracking
                tracking = tracking_item.get('tracking_number')
                tracking_provider = tracking_item.get('tracking_provider', 'USPS')
                break
            elif isinstance(value, str):
                # Sometimes stored as JSON string
                import json
                try:
                    items = json.loads(value)
                    if items and len(items) > 0:
                        tracking = items[0].get('tracking_number')
                        tracking_provider = items[0].get('tracking_provider', 'USPS')
                        break
                except:
                    pass

        # Also check simple tracking fields
        elif key in ['_tracking_number', 'tracking_number', '_aftership_tracking_number']:
            tracking = value
            break

    # Format status nicely
    status_map = {
        'pending': 'Payment Pending',
        'processing': 'Being Prepared',
        'on-hold': 'On Hold',
        'completed': 'Completed/Delivered',
        'shipped': 'Shipped',
        'cancelled': 'Cancelled',
        'refunded': 'Refunded',
        'failed': 'Payment Failed'
    }

    raw_status = order.get('status', 'unknown')
    status = status_map.get(raw_status, raw_status.title())

    # Get dates
    date_created = order.get('date_created', '')
    date_completed = order.get('date_completed', '')

    return {
        'order_number': order.get('id'),
        'status': status,
        'status_raw': raw_status,
        'total': order.get('total'),
        'currency': order.get('currency', 'USD'),
        'items': items,
        'tracking': tracking,
        'tracking_provider': tracking_provider,
        'date_ordered': date_created[:10] if date_created else None,
        'date_completed': date_completed[:10] if date_completed else None,
        'item_count': len(items),
        'item_summary': ', '.join([f"{i['name']} x{i['quantity']}" for i in items[:3]])
    }


def format_order_response(info: Dict) -> str:
    """Format order info as a friendly response"""
    lines = [f"Order #{info['order_number']}:"]
    lines.append(f"Status: {info['status']}")

    if info.get('tracking'):
        tracking = info['tracking']
        provider = info.get('tracking_provider', 'USPS')
        # Create tracking link based on provider
        if provider == 'USPS':
            track_url = f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking}"
        elif provider == 'UPS':
            track_url = f"https://www.ups.com/track?tracknum={tracking}"
        elif provider == 'FedEx':
            track_url = f"https://www.fedex.com/fedextrack/?trknbr={tracking}"
        else:
            track_url = None

        if track_url:
            lines.append(f'Tracking: <a href="{track_url}" target="_blank"><strong>{tracking}</strong></a>')
        else:
            lines.append(f"Tracking: <strong>{tracking}</strong>")

    if info.get('items'):
        lines.append(f"Items: {info['item_summary']}")

    lines.append(f"Total: ${info['total']}")

    if info.get('date_ordered'):
        lines.append(f"Ordered: {info['date_ordered']}")

    # Add helpful status messages
    status = info.get('status_raw', '')
    if status == 'processing':
        lines.append("\nYour order is being prepared and will ship within 1-3 business days.")
    elif status == 'shipped' or info.get('tracking'):
        lines.append("\nYour order has shipped! Track it using the number above.")
    elif status == 'completed':
        lines.append("\nYour order was delivered. Enjoy!")

    return '\n'.join(lines)


# =============================================================================
# CONVERSATION FLOW HELPERS
# =============================================================================

class OrderVerificationSession:
    """
    Manages the verification flow for a customer.
    Stores state between messages.
    """

    def __init__(self, session_id: str = None):
        self.session_id = session_id
        self.order_number = None
        self.order = None
        self.challenge = None
        self.verified = False
        self.attempts = 0
        self.max_attempts = 3

    def start_lookup(self, order_number: str) -> Tuple[bool, str]:
        """
        Start the verification process.
        Returns (success, message)
        """
        self.order_number = order_number
        self.order = lookup_order(order_number)

        if not self.order:
            return False, f"I couldn't find order #{order_number}. Please double-check the number and try again."

        self.challenge = get_verification_challenge(self.order)

        # Ask for verification
        zip_hint = self.challenge.get('zip_hint', '***')
        return True, f"Found your order! For security, please confirm the zip code on the order (ends in {zip_hint}):"

    def verify(self, answer: str) -> Tuple[bool, str]:
        """
        Verify the customer's answer.
        Returns (verified, message)
        """
        if not self.challenge:
            return False, "Please provide your order number first."

        self.attempts += 1

        if verify_customer(self.challenge, answer, method='zip'):
            self.verified = True
            info = get_safe_order_info(self.order)
            response = format_order_response(info)
            return True, f"Verified! Here's your order info:\n\n{response}"

        if self.attempts >= self.max_attempts:
            return False, "Too many attempts. For security, please contact matt@ineedhemp.com for help with your order."

        remaining = self.max_attempts - self.attempts
        return False, f"That doesn't match our records. Please try again ({remaining} attempts left):"

    def get_order_info(self) -> Optional[Dict]:
        """Get order info if verified"""
        if self.verified and self.order:
            return get_safe_order_info(self.order)
        return None


# =============================================================================
# QUICK FUNCTIONS FOR AI RESPONSES
# =============================================================================

def handle_order_inquiry(text: str, context: Dict = None) -> Dict:
    """
    Handle an order inquiry from chatbot or email.

    Returns:
        {
            'needs_order_number': True/False,
            'needs_verification': True/False,
            'verified': True/False,
            'order_info': {...} or None,
            'response': "message to customer"
        }
    """
    context = context or {}

    # Check if we have a pending verification
    pending_order = context.get('pending_order_number')
    pending_challenge = context.get('pending_challenge')

    # Extract order number from text
    order_number = extract_order_number(text)

    # If we're waiting for verification answer
    if pending_challenge and not order_number:
        # Try to verify with any method (zip, email, or last name)
        answer = text.strip()
        if verify_customer(pending_challenge, answer, method='auto'):
            order = lookup_order(pending_challenge.get('order_number'))
            if order:
                info = get_safe_order_info(order)
                return {
                    'needs_order_number': False,
                    'needs_verification': False,
                    'verified': True,
                    'order_info': info,
                    'response': f"Verified! Here's your order:\n\n{format_order_response(info)}"
                }
        else:
            return {
                'needs_order_number': False,
                'needs_verification': True,
                'verified': False,
                'order_info': None,
                'pending_challenge': pending_challenge,  # Keep challenge for retry
                'response': "That doesn't match our records. You can verify with:\n• Your zip code\n• Your email address\n• Your last name\n\nPlease try again, or contact matt@ineedhemp.com for help."
            }

    # If no order number found
    if not order_number:
        return {
            'needs_order_number': True,
            'needs_verification': False,
            'verified': False,
            'order_info': None,
            'response': "I'd be happy to help with your order! What's your order number? (You can find it in your confirmation email)"
        }

    # Look up the order
    order = lookup_order(order_number)
    if not order:
        return {
            'needs_order_number': True,
            'needs_verification': False,
            'verified': False,
            'order_info': None,
            'response': f"I couldn't find order #{order_number}. Please double-check the number. It should be 5-6 digits from your confirmation email."
        }

    # Generate verification challenge
    challenge = get_verification_challenge(order)

    # Build verification prompt with hints
    zip_hint = challenge.get('zip_hint', '***')
    email_hint = challenge.get('email_hint', '***@***')
    name_hint = challenge.get('name_hint', '***')

    verification_prompt = f"""Found order #{order_number}! For security, please verify your identity with ONE of the following:

• **Zip code** (ends in {zip_hint})
• **Email address** ({email_hint})
• **Last name** ({name_hint})

Just type your answer:"""

    return {
        'needs_order_number': False,
        'needs_verification': True,
        'verified': False,
        'order_info': None,
        'challenge': challenge,  # Store this in session for next message
        'response': verification_prompt
    }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("Order Verification Module")
    print("=" * 40)

    # Test email masking
    print("\nEmail masking tests:")
    print(f"  john@gmail.com -> {mask_email('john@gmail.com')}")
    print(f"  samcaruso11@gmail.com -> {mask_email('samcaruso11@gmail.com')}")
    print(f"  a@b.com -> {mask_email('a@b.com')}")

    # Test order number extraction
    print("\nOrder number extraction:")
    tests = [
        "Where's my order #198900?",
        "Order 199337 status",
        "Can you check order number: 198765",
        "I ordered last week, number 199000"
    ]
    for t in tests:
        print(f"  '{t}' -> {extract_order_number(t)}")
