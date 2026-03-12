"""
Database models for Nicholas Rice Ordering System
Author: Nicholas Mwangomba
Location: Mzuzu, Malawi
"""

import sqlite3
import hashlib
import uuid
import os
import tempfile
from datetime import datetime
from pathlib import Path

# Use a writable location for the database
DB_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(DB_DIR, 'rice_shop.db')

class Database:
    """Main database handler"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      password TEXT NOT NULL,
                      email TEXT UNIQUE,
                      phone TEXT NOT NULL,
                      address TEXT,
                      city TEXT DEFAULT 'Mzuzu',
                      points INTEGER DEFAULT 0,
                      referral_code TEXT UNIQUE,
                      referred_by INTEGER,
                      is_active BOOLEAN DEFAULT 1,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      last_login TIMESTAMP,
                      FOREIGN KEY (referred_by) REFERENCES users(id))''')
        
        # Orders table
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      order_number TEXT UNIQUE,
                      user_id INTEGER,
                      customer_name TEXT NOT NULL,
                      customer_phone TEXT NOT NULL,
                      customer_email TEXT,
                      quantity INTEGER NOT NULL,
                      base_price INTEGER NOT NULL,
                      transport_cost INTEGER DEFAULT 0,
                      total_amount INTEGER NOT NULL,
                      delivery_type TEXT NOT NULL,
                      delivery_location TEXT,
                      delivery_area TEXT,
                      house_number TEXT,
                      courier_service TEXT,
                      cts_branch TEXT,
                      recipient_name TEXT,
                      payment_method TEXT NOT NULL,
                      payment_status TEXT DEFAULT 'Pending',
                      order_status TEXT DEFAULT 'Pending',
                      points_earned INTEGER DEFAULT 0,
                      points_used INTEGER DEFAULT 0,
                      notes TEXT,
                      tracking_number TEXT,
                      notification_sent BOOLEAN DEFAULT 0,
                      whatsapp_sent BOOLEAN DEFAULT 0,
                      email_sent BOOLEAN DEFAULT 0,
                      sms_sent BOOLEAN DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        # Cart table
        c.execute('''CREATE TABLE IF NOT EXISTS cart
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      session_id TEXT,
                      quantity INTEGER NOT NULL,
                      price INTEGER NOT NULL,
                      added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        # Products table
        c.execute('''CREATE TABLE IF NOT EXISTS products
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      size_kg INTEGER UNIQUE NOT NULL,
                      price INTEGER NOT NULL,
                      description TEXT DEFAULT 'Quality rice from Karonga',
                      image_url TEXT,
                      stock INTEGER DEFAULT 1000,
                      is_active BOOLEAN DEFAULT 1,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Reviews table
        c.execute('''CREATE TABLE IF NOT EXISTS reviews
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      order_id INTEGER,
                      rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                      comment TEXT,
                      is_approved BOOLEAN DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(id),
                      FOREIGN KEY (order_id) REFERENCES orders(id))''')
        
        # Admins table
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      password TEXT NOT NULL,
                      email TEXT UNIQUE,
                      role TEXT DEFAULT 'admin',
                      last_login TIMESTAMP,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Settings table
        c.execute('''CREATE TABLE IF NOT EXISTS settings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      key TEXT UNIQUE NOT NULL,
                      value TEXT,
                      description TEXT,
                      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Points history table
        c.execute('''CREATE TABLE IF NOT EXISTS points_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      points INTEGER,
                      action TEXT,
                      order_id INTEGER,
                      description TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(id),
                      FOREIGN KEY (order_id) REFERENCES orders(id))''')
        
        # Notifications log table
        c.execute('''CREATE TABLE IF NOT EXISTS notification_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      order_id INTEGER,
                      notification_type TEXT,
                      recipient TEXT,
                      status TEXT,
                      message TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (order_id) REFERENCES orders(id))''')
        
        # Insert default admin
        c.execute("SELECT * FROM admins WHERE username='admin'")
        if not c.fetchone():
            hashed = hashlib.sha256("Admin@123".encode()).hexdigest()
            c.execute("INSERT INTO admins (username, password, email, role) VALUES (?, ?, ?, ?)",
                      ('admin', hashed, 'mwangombanicholas@gmail.com', 'superadmin'))
        
        # Insert default products
        from config import RICE_PRICES
        for size, price in RICE_PRICES.items():
            c.execute('''INSERT OR IGNORE INTO products 
                        (name, size_kg, price, description, image_url)
                        VALUES (?, ?, ?, ?, ?)''',
                     (f"{size}kg Karonga Rice", size, price, 
                      f"🌾 Quality rice from Karonga - {size}kg - Fresh and aromatic",
                      f"/static/images/rice-{size}kg.jpg"))
        
        # Insert default settings
        default_settings = [
            ('business_name', 'Nicholas Rice Seller - Mzuzu', 'Business name'),
            ('business_location', 'Mzuzu', 'Your location'),
            ('supplier', 'Karonga (Quality Rice)', 'Rice source'),
            ('admin_phone', '0886867758', 'Admin phone'),
            ('admin_email', 'mwangombanicholas@gmail.com', 'Admin email'),
            ('whatsapp_number', '265886867758', 'WhatsApp number'),
            ('mzuzu_transport_enabled', '1', 'Enable transport cost for Mzuzu'),
            ('courier_enabled', '1', 'Enable courier for other districts'),
            ('stock_alert_threshold', '50', 'Low stock alert'),
            ('enable_sms', '1', 'Enable SMS notifications'),
            ('enable_email', '1', 'Enable email notifications'),
            ('enable_whatsapp', '1', 'Enable WhatsApp notifications')
        ]
        
        for key, value, desc in default_settings:
            c.execute('''INSERT OR IGNORE INTO settings (key, value, description) 
                        VALUES (?, ?, ?)''', (key, value, desc))
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized at {self.db_path}")
    
    def create_order(self, order_data):
        """Create a new order"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Generate order number
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        order_number = f"NK{timestamp}"
        
        try:
            c.execute('''INSERT INTO orders (
                order_number, user_id, customer_name, customer_phone, customer_email,
                quantity, base_price, transport_cost, total_amount,
                delivery_type, delivery_location, delivery_area, house_number,
                courier_service, cts_branch, recipient_name, payment_method,
                notes, tracking_number, order_status,
                notification_sent, whatsapp_sent, email_sent, sms_sent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                order_number,
                order_data.get('user_id'),
                order_data['customer_name'],
                order_data['customer_phone'],
                order_data.get('customer_email'),
                order_data['quantity'],
                order_data['base_price'],
                order_data.get('transport_cost', 0),
                order_data['total_amount'],
                order_data['delivery_type'],
                order_data.get('delivery_location'),
                order_data.get('delivery_area'),
                order_data.get('house_number'),
                order_data.get('courier_service'),
                order_data.get('cts_branch'),
                order_data.get('recipient_name'),
                order_data['payment_method'],
                order_data.get('notes'),
                order_data.get('tracking_number'),
                'Pending',
                0, 0, 0, 0
            ))
            
            order_id = c.lastrowid
            conn.commit()
            return order_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_order_by_id(self, order_id):
        """Get order by ID"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        order = c.fetchone()
        conn.close()
        return order
    
    def update_notification_status(self, order_id, notification_type):
        """Update notification sent status"""
        conn = self.get_connection()
        c = conn.cursor()
        
        if notification_type == 'whatsapp':
            c.execute("UPDATE orders SET whatsapp_sent=1 WHERE id=?", (order_id,))
        elif notification_type == 'email':
            c.execute("UPDATE orders SET email_sent=1 WHERE id=?", (order_id,))
        elif notification_type == 'sms':
            c.execute("UPDATE orders SET sms_sent=1 WHERE id=?", (order_id,))
        
        c.execute('''UPDATE orders SET notification_sent=1 
                    WHERE id=? AND whatsapp_sent=1 AND email_sent=1 AND sms_sent=1''', 
                 (order_id,))
        
        conn.commit()
        conn.close()
    
    def log_notification(self, order_id, notification_type, recipient, status, message):
        """Log notification in database"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO notification_log 
                    (order_id, notification_type, recipient, status, message)
                    VALUES (?, ?, ?, ?, ?)''',
                 (order_id, notification_type, recipient, status, message))
        conn.commit()
        conn.close()
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        conn = self.get_connection()
        c = conn.cursor()
        
        stats = {}
        
        c.execute("SELECT COUNT(*) FROM orders")
        stats['total_orders'] = c.fetchone()[0]
        
        c.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders")
        stats['total_revenue'] = c.fetchone()[0]
        
        c.execute("SELECT COALESCE(SUM(quantity), 0) FROM orders")
        stats['total_rice'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = DATE('now')")
        stats['today_orders'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM orders WHERE order_status='Pending'")
        stats['pending_orders'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM orders WHERE delivery_type='mzuzu_direct' AND order_status='Pending'")
        stats['mzuzu_pending'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM orders WHERE delivery_type='courier' AND order_status='Pending'")
        stats['courier_pending'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM orders WHERE delivery_type='campus' AND order_status='Pending'")
        stats['campus_pending'] = c.fetchone()[0]
        
        conn.close()
        return stats
