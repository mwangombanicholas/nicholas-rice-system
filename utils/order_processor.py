"""
Order processing logic with notifications
Author: Nicholas Mwangomba
"""

from datetime import datetime
from utils.helpers import *
from utils.notifications import NotificationService
from config import *

class OrderProcessor:
    """Handle order creation and processing"""
    
    def __init__(self, db):
        self.db = db
        self.notifier = NotificationService(db)
    
    def process_order(self, order_data):
        """Process a new order and send notifications"""
        
        # Calculate totals
        quantity = order_data['quantity']
        base_price = RICE_PRICES.get(quantity, 4000)
        transport_cost = order_data.get('transport_cost', 0)
        total_amount = base_price + transport_cost
        
        # Generate order number and tracking
        order_number = generate_order_number()
        tracking_number = generate_tracking_number()
        
        # Prepare order for database
        db_order = {
            'user_id': order_data.get('user_id'),
            'customer_name': order_data['customer_name'],
            'customer_phone': order_data['customer_phone'],
            'customer_email': order_data.get('customer_email'),
            'quantity': quantity,
            'base_price': base_price,
            'transport_cost': transport_cost,
            'total_amount': total_amount,
            'delivery_type': order_data['delivery_type'],
            'delivery_location': order_data.get('delivery_location'),
            'delivery_area': order_data.get('delivery_area'),
            'house_number': order_data.get('house_number'),
            'courier_service': order_data.get('courier_service'),
            'cts_branch': order_data.get('cts_branch'),
            'recipient_name': order_data.get('recipient_name'),
            'payment_method': order_data['payment_method'],
            'notes': order_data.get('notes'),
            'tracking_number': tracking_number,
            'order_number': order_number
        }
        
        # Save to database
        order_id = self.db.create_order(db_order)
        
        # Get the full order for notifications
        order = self.db.get_order_by_id(order_id)
        
        # Send notifications
        notification_results = self.notifier.send_order_notifications(order)
        
        return {
            'success': True,
            'order_id': order_id,
            'order_number': order_number,
            'tracking_number': tracking_number,
            'total_amount': total_amount,
            'notifications': notification_results
        }

print("✅ Order processor created successfully!")
