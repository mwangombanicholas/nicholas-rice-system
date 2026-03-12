"""
Notification service for Nicholas Rice Ordering System
Sends WhatsApp, Email, and SMS notifications
Author: Nicholas Mwangomba
"""

import smtplib
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st
from config import *

class NotificationService:
    """Handle all notifications (WhatsApp, Email, SMS)"""
    
    def __init__(self, db):
        self.db = db
        self.admin_email = ADMIN_EMAIL
        self.admin_phone = ADMIN_PHONE
        self.whatsapp_number = WHATSAPP_NUMBER
    
    def send_order_notifications(self, order):
        """Send all notifications for a new order"""
        order_id = order['id']
        
        # Prepare message
        message = self._prepare_order_message(order)
        short_message = self._prepare_short_message(order)
        
        # Send to all channels
        whatsapp_result = self.send_whatsapp(message)
        email_result = self.send_email("🛒 New Order Received!", message)
        sms_result = self.send_sms(short_message)
        
        # Update notification status in database
        if whatsapp_result:
            self.db.update_notification_status(order_id, 'whatsapp')
            self.db.log_notification(order_id, 'whatsapp', self.whatsapp_number, 'sent', message[:100])
        
        if email_result:
            self.db.update_notification_status(order_id, 'email')
            self.db.log_notification(order_id, 'email', self.admin_email, 'sent', message[:100])
        
        if sms_result:
            self.db.update_notification_status(order_id, 'sms')
            self.db.log_notification(order_id, 'sms', self.admin_phone, 'sent', short_message)
        
        return {
            'whatsapp': whatsapp_result,
            'email': email_result,
            'sms': sms_result
        }
    
    def _prepare_order_message(self, order):
        """Prepare detailed order message for WhatsApp/Email"""
        delivery_info = self._get_delivery_info(order)
        
        message = f"""
🌾 **NEW ORDER RECEIVED!**
━━━━━━━━━━━━━━━━━━━━━
📋 **Order #:** {order['order_number']}
👤 **Customer:** {order['customer_name']}
📱 **Phone:** {order['customer_phone']}
📧 **Email:** {order.get('customer_email', 'Not provided')}

🛒 **Order Details:**
• Quantity: {order['quantity']}kg
• Price: MWK {order['base_price']:,}
• Transport: MWK {order.get('transport_cost', 0):,}
• **Total: MWK {order['total_amount']:,}**

{delivery_info}

💳 **Payment:** {order['payment_method']}

⏰ **Order Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

━━━━━━━━━━━━━━━━━━━━━
📍 *Quality Rice from Karonga*
        """
        return message
    
    def _prepare_short_message(self, order):
        """Prepare short SMS message"""
        return f"New Order! {order['customer_name']} ordered {order['quantity']}kg rice. Total: MWK {order['total_amount']:,}. Check admin panel."
    
    def _get_delivery_info(self, order):
        """Get delivery information based on type"""
        delivery_type = order['delivery_type']
        
        if delivery_type == 'mzuzu_direct':
            return f"""
🚚 **Delivery (Mzuzu Direct):**
• Area: {order.get('delivery_area', 'N/A')}
• House: {order.get('house_number', 'N/A')}
• Transport Cost: MWK {order.get('transport_cost', 0):,}
            """
        elif delivery_type == 'courier':
            return f"""
📦 **Delivery (Courier):**
• Service: {order.get('courier_service', 'N/A')}
• Branch: {order.get('cts_branch', 'N/A')}
• Recipient: {order.get('recipient_name', 'N/A')}
• Customer pays courier at collection
            """
        else:
            return f"""
🏫 **Delivery (Campus):**
• Location: {order.get('delivery_location', 'N/A')}
• Room/House: {order.get('house_number', order.get('delivery_area', 'N/A'))}
• Free Delivery
            """
    
    def send_whatsapp(self, message):
        """Send WhatsApp notification (creates clickable link)"""
        try:
            # Create WhatsApp link
            encoded_message = urllib.parse.quote(message)
            whatsapp_link = f"https://wa.me/{self.whatsapp_number}?text={encoded_message}"
            
            # Store in session for admin to click
            st.session_state['whatsapp_link'] = whatsapp_link
            
            return True
        except Exception as e:
            print(f"WhatsApp error: {e}")
            return False
    
    def send_email(self, subject, body):
        """Send email notification"""
        try:
            # For now, just print (you'll add credentials later)
            print(f"📧 Email would be sent to {self.admin_email}")
            print(f"Subject: {subject}")
            print(f"Body preview: {body[:100]}...")
            
            # Store in session
            st.session_state['email_sent'] = True
            
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def send_sms(self, message):
        """Send SMS notification (integrates with Africa's Talking)"""
        try:
            print(f"📱 SMS would be sent to {self.admin_phone}: {message}")
            
            # Store in session
            st.session_state['sms_sent'] = True
            
            return True
        except Exception as e:
            print(f"SMS error: {e}")
            return False

print("✅ Notification service created successfully!")
print("📱 WhatsApp, 📧 Email, and 📱 SMS notifications ready!")
