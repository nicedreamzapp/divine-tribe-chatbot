"""
WooCommerce Client - Order lookup and customer verification
Divine Tribe Email Assistant
"""

import os
from woocommerce import API
from typing import Optional, Dict, List
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class WooCommerceClient:
    """Handle all WooCommerce API interactions"""

    def __init__(self):
        self.wcapi = API(
            url=os.getenv('WOOCOMMERCE_URL', 'https://ineedhemp.com'),
            consumer_key=os.getenv('WOOCOMMERCE_KEY', ''),
            consumer_secret=os.getenv('WOOCOMMERCE_SECRET', ''),
            version="wc/v3",
            timeout=30
        )
        print("✅ WooCommerce client initialized")

    def verify_customer(self, order_number: str, zip_code: str = None, last_name: str = None) -> Dict:
        """
        Verify customer identity before revealing order info.
        Requires order_number + zip_code OR order_number + last_name

        Returns: {verified: bool, order: dict or None, error: str or None}
        """
        if not order_number:
            return {'verified': False, 'order': None, 'error': 'Order number required'}

        if not zip_code and not last_name:
            return {'verified': False, 'order': None, 'error': 'Zip code or last name required for verification'}

        try:
            # Fetch the order
            response = self.wcapi.get(f"orders/{order_number}")

            if response.status_code != 200:
                return {'verified': False, 'order': None, 'error': 'Order not found'}

            order = response.json()
            billing = order.get('billing', {})
            shipping = order.get('shipping', {})

            # Get zip codes and last names from order
            billing_zip = billing.get('postcode', '').strip().lower()
            shipping_zip = shipping.get('postcode', '').strip().lower()
            billing_last = billing.get('last_name', '').strip().lower()
            shipping_last = shipping.get('last_name', '').strip().lower()

            # Verify by zip code
            if zip_code:
                zip_code = zip_code.strip().lower()
                if zip_code == billing_zip or zip_code == shipping_zip:
                    return {'verified': True, 'order': order, 'error': None}

            # Verify by last name
            if last_name:
                last_name = last_name.strip().lower()
                if last_name == billing_last or last_name == shipping_last:
                    return {'verified': True, 'order': order, 'error': None}

            return {'verified': False, 'order': None, 'error': 'Verification failed - details do not match'}

        except Exception as e:
            print(f"❌ WooCommerce API error: {e}")
            return {'verified': False, 'order': None, 'error': f'Error looking up order: {str(e)}'}

    def get_order(self, order_number: str) -> Optional[Dict]:
        """
        Get order by order number (internal use - no verification)
        """
        try:
            response = self.wcapi.get(f"orders/{order_number}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Error fetching order {order_number}: {e}")
            return None

    def search_orders_by_email(self, email: str, limit: int = 10) -> List[Dict]:
        """
        Search orders by customer email (for internal use)
        """
        try:
            response = self.wcapi.get("orders", params={
                'search': email,
                'per_page': limit,
                'orderby': 'date',
                'order': 'desc'
            })
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"❌ Error searching orders for {email}: {e}")
            return []

    def get_customer_order_history(self, email: str) -> List[Dict]:
        """
        Get all orders for a customer email (internal use for context)
        """
        orders = self.search_orders_by_email(email, limit=50)
        return [{
            'order_number': o.get('id'),
            'date': o.get('date_created'),
            'status': o.get('status'),
            'total': o.get('total'),
            'items': [item.get('name') for item in o.get('line_items', [])]
        } for o in orders]

    def format_order_status(self, order: Dict) -> str:
        """
        Format order info for customer-friendly response
        """
        order_id = order.get('id')
        status = order.get('status', 'unknown')
        date_created = order.get('date_created', '')[:10]  # Just the date part

        # Get tracking info from meta data if available
        tracking_number = None
        tracking_url = None
        for meta in order.get('meta_data', []):
            if meta.get('key') == '_tracking_number':
                tracking_number = meta.get('value')
            if meta.get('key') == '_tracking_url':
                tracking_url = meta.get('value')

        # Get items
        items = [item.get('name') for item in order.get('line_items', [])]
        items_str = ', '.join(items[:3])
        if len(items) > 3:
            items_str += f' and {len(items) - 3} more items'

        # Build response based on status
        status_messages = {
            'pending': f"Order #{order_id} is pending payment. Please complete checkout to process your order.",
            'processing': f"Order #{order_id} is being prepared! It should ship within 1-3 business days.",
            'on-hold': f"Order #{order_id} is on hold. Please contact us if you have questions.",
            'completed': f"Order #{order_id} has been delivered! We hope you're enjoying your {items_str}.",
            'shipped': f"Order #{order_id} has shipped!",
            'cancelled': f"Order #{order_id} was cancelled.",
            'refunded': f"Order #{order_id} has been refunded.",
            'failed': f"Order #{order_id} payment failed. Please try again or contact us."
        }

        response = status_messages.get(status, f"Order #{order_id} status: {status}")

        # Add tracking if available
        if tracking_number and status in ['shipped', 'completed']:
            response += f"\n\nTracking Number: {tracking_number}"
            if tracking_url:
                response += f"\nTrack your package: {tracking_url}"

        # Add order date
        response += f"\n\nOrder placed: {date_created}"
        response += f"\nItems: {items_str}"

        return response

    def get_recent_orders(self, limit: int = 20) -> List[Dict]:
        """
        Get recent orders (for dashboard/overview)
        """
        try:
            response = self.wcapi.get("orders", params={
                'per_page': limit,
                'orderby': 'date',
                'order': 'desc'
            })
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"❌ Error fetching recent orders: {e}")
            return []

    def get_order_notes(self, order_number: str) -> List[Dict]:
        """
        Get notes/comments on an order
        """
        try:
            response = self.wcapi.get(f"orders/{order_number}/notes")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"❌ Error fetching order notes: {e}")
            return []

    def add_order_note(self, order_number: str, note: str, customer_note: bool = False) -> bool:
        """
        Add a note to an order
        customer_note=True means customer can see it
        """
        try:
            response = self.wcapi.post(f"orders/{order_number}/notes", {
                'note': note,
                'customer_note': customer_note
            })
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Error adding order note: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test if WooCommerce API connection works
        """
        try:
            response = self.wcapi.get("orders", params={'per_page': 1})
            if response.status_code == 200:
                print("✅ WooCommerce API connection successful")
                return True
            else:
                print(f"❌ WooCommerce API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ WooCommerce API connection failed: {e}")
            return False


# Quick test
if __name__ == "__main__":
    client = WooCommerceClient()

    if client.test_connection():
        print("\n📦 Recent orders:")
        orders = client.get_recent_orders(5)
        for order in orders:
            print(f"  #{order.get('id')} - {order.get('status')} - ${order.get('total')}")
    else:
        print("⚠️  Add your WooCommerce API keys to .env file")
