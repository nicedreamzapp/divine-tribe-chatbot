#!/usr/bin/env python3
"""
Privacy Protection Module
Strips PII from data before storage/training
"""

import re
from typing import Dict, Optional


def strip_pii(text: str) -> str:
    """
    Remove personally identifiable information from text.
    Used before saving to training files or logs that could be shared.
    """
    if not text:
        return text

    # Email addresses
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', text)

    # Phone numbers (various formats)
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE]', text)
    text = re.sub(r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}', '[PHONE]', text)
    text = re.sub(r'\+1\s*\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', '[PHONE]', text)

    # Credit card numbers (basic pattern)
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)
    text = re.sub(r'\bXXXX\d{4}\b', '[CARD]', text)

    # SSN
    text = re.sub(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b', '[SSN]', text)

    # Street addresses (basic - catches most US addresses)
    text = re.sub(r'\b\d+\s+[A-Za-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Way|Blvd|Boulevard|Court|Ct|Circle|Cir|Place|Pl|Apt|Suite|Ste|Unit|#)\b[^,\n]*', '[ADDRESS]', text, flags=re.IGNORECASE)

    # Zip codes (5 or 9 digit)
    text = re.sub(r'\b\d{5}(-\d{4})?\b', '[ZIP]', text)

    # Order numbers (preserve these - they're useful for training)
    # Don't strip order numbers

    # Tracking numbers (long alphanumeric strings)
    text = re.sub(r'\b[0-9]{20,}\b', '[TRACKING]', text)
    text = re.sub(r'\b1Z[A-Z0-9]{16}\b', '[TRACKING]', text)  # UPS
    text = re.sub(r'\b94\d{20,}\b', '[TRACKING]', text)  # USPS

    return text


def anonymize_email_for_training(email_data: Dict) -> Dict:
    """
    Create an anonymized version of email data for training.
    Preserves the structure and intent, removes PII.
    """
    anonymized = {
        'subject': strip_pii(email_data.get('subject', '')),
        'body': strip_pii(email_data.get('body', '')),
        'category': email_data.get('category', 'general'),
        'intent': email_data.get('intent', 'unknown'),
        # Don't include: from_email, from_name, customer details
    }
    return anonymized


def anonymize_response_for_training(response: str) -> str:
    """
    Anonymize a response before saving to training data.
    """
    return strip_pii(response)


def hash_email(email: str) -> str:
    """
    Create a one-way hash of an email for tracking without storing the actual email.
    """
    import hashlib
    if not email:
        return ''
    return hashlib.sha256(email.lower().strip().encode()).hexdigest()[:16]


# Customer data that should NEVER go into RAG/CAG
NEVER_INDEX_PATTERNS = [
    r'order\s*#?\s*\d+',  # Order numbers with context
    r'tracking\s*:?\s*\S+',  # Tracking info
    r'shipped\s+to\s+',  # Shipping addresses
    r'billing\s+address',
    r'credit\s+card',
    r'payment\s+method',
    r'refund\s+of\s+\$',
    r'charged\s+\$',
]


def is_safe_for_rag(text: str) -> bool:
    """
    Check if text is safe to add to RAG index.
    Returns False if it contains customer-specific data.
    """
    text_lower = text.lower()
    for pattern in NEVER_INDEX_PATTERNS:
        if re.search(pattern, text_lower):
            return False
    return True


def sanitize_for_logging(data: Dict, fields_to_hash: list = None) -> Dict:
    """
    Sanitize data for logging - hash sensitive fields, strip PII from text.
    """
    if fields_to_hash is None:
        fields_to_hash = ['from_email', 'to_email', 'customer_email']

    sanitized = {}
    for key, value in data.items():
        if key in fields_to_hash and isinstance(value, str):
            sanitized[key] = hash_email(value)
        elif isinstance(value, str):
            sanitized[key] = strip_pii(value)
        else:
            sanitized[key] = value

    return sanitized


# Test
if __name__ == "__main__":
    test_text = """
    Hi, my name is John Smith and my email is john@example.com.
    Please ship to 123 Main Street, Apt 4B, Denver, CO 80202.
    My phone is 555-123-4567 and my order is #198900.
    Tracking: 9400150105797040439178
    """

    print("Original:")
    print(test_text)
    print("\nStripped:")
    print(strip_pii(test_text))
