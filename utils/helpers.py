"""
Helper functions for Nicholas Rice Ordering System
Author: Nicholas Mwangomba
Location: Mzuzu, Malawi
"""

import re
import random
import string
import urllib.parse
from datetime import datetime, timedelta
from config import *

def validate_phone(phone):
    """Validate Malawi phone number"""
    phone = re.sub(r'\D', '', phone)
    patterns = [
        r'^088[0-9]{7}$',  # TNM
        r'^099[0-9]{7}$',  # Airtel
        r'^26588[0-9]{7}$',
        r'^26599[0-9]{7}$'
    ]
    for pattern in patterns:
        if re.match(pattern, phone):
            return True
    return False

def format_phone(phone):
    """Format phone number to international"""
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('0'):
        return '265' + phone[1:]
    return phone

def calculate_total(quantity, transport_cost=0):
    """Calculate total price"""
    base_price = RICE_PRICES.get(quantity, 4000)
    return base_price + transport_cost

def get_transport_cost(area):
    """Get transport cost for Mzuzu area"""
    return MZUZU_TRANSPORT_COST.get(area, 3500)

def format_currency(amount):
    """Format amount as Malawi Kwacha"""
    return f"MWK {amount:,.0f}"

def generate_order_number():
    """Generate order number with NK prefix (Nicholas Karonga)"""
    timestamp = datetime.now().strftime('%y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
    return f"NK{timestamp}{random_str}"

def generate_tracking_number():
    """Generate tracking number"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def generate_referral_code():
    """Generate referral code with NK prefix"""
    return f"NK{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

def calculate_points(amount):
    """Calculate points earned"""
    return int(amount / 100)

def get_delivery_message(delivery_type, location=None):
    """Get delivery instructions message"""
    if delivery_type == 'mzuzu_direct':
        return f"📍 We will deliver to your location in Mzuzu. Transport cost will be added."
    elif delivery_type == 'courier':
        return f"📦 Your rice will be sent via courier. You'll collect at the branch and pay courier fees there."
    else:
        return f"📍 Campus delivery - Free delivery to your location."

def create_whatsapp_link(phone, message):
    """Create WhatsApp link"""
    phone = format_phone(phone)
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{phone}?text={encoded}"

def get_order_status_color(status):
    """Get color for order status"""
    colors = {
        'Pending': 'orange',
        'Processing': 'blue',
        'Delivered': 'green',
        'Cancelled': 'red'
    }
    return colors.get(status, 'gray')

def format_address(delivery_type, area=None, house=None):
    """Format delivery address"""
    if delivery_type == 'mzuzu_direct':
        return f"Mzuzu - {area} ({house})" if house else f"Mzuzu - {area}"
    elif delivery_type == 'courier':
        return f"Courier collection"
    else:
        return f"Campus - {area}"

print("✅ Helper functions created successfully!")
