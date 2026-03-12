"""
Authentication module for Nicholas Rice Ordering System
Author: Nicholas Mwangomba
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from models.database import Database

class Auth:
    """Authentication handler"""
    
    def __init__(self):
        self.db = Database()
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, hashed):
        """Verify password"""
        return self.hash_password(password) == hashed
    
    def create_session_token(self, user_id):
        """Create session token"""
        token = secrets.token_urlsafe(32)
        return token
    
    def register_user(self, username, password, phone, email=None):
        """Register new user"""
        if len(password) < 6:
            return {'success': False, 'message': 'Password must be at least 6 characters'}
        
        conn = self.db.get_connection()
        c = conn.cursor()
        
        try:
            hashed = self.hash_password(password)
            referral_code = f"NK{secrets.token_hex(4).upper()}"
            
            c.execute('''INSERT INTO users 
                        (username, password, email, phone, referral_code)
                        VALUES (?, ?, ?, ?, ?)''',
                     (username, hashed, email, phone, referral_code))
            
            user_id = c.lastrowid
            conn.commit()
            
            # Add welcome points
            c.execute('''INSERT INTO points_history 
                        (user_id, points, action, description)
                        VALUES (?, ?, ?, ?)''',
                     (user_id, 50, 'welcome_bonus', 'Welcome bonus points!'))
            
            c.execute("UPDATE users SET points = points + 50 WHERE id=?", (user_id,))
            conn.commit()
            
            return {'success': True, 'user_id': user_id}
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()
    
    def login_user(self, username, password):
        """Login user"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        hashed = self.hash_password(password)
        c.execute('''SELECT * FROM users 
                    WHERE (username=? OR email=?) AND password=?''',
                 (username, username, hashed))
        
        user = c.fetchone()
        
        if user:
            c.execute('''UPDATE users SET last_login=CURRENT_TIMESTAMP 
                        WHERE id=?''', (user['id'],))
            conn.commit()
            conn.close()
            return {'success': True, 'user': dict(user)}
        
        conn.close()
        return {'success': False, 'message': 'Invalid username or password'}
    
    def login_admin(self, username, password):
        """Login admin"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        hashed = self.hash_password(password)
        c.execute('''SELECT * FROM admins 
                    WHERE username=? AND password=?''',
                 (username, hashed))
        
        admin = c.fetchone()
        
        if admin:
            c.execute('''UPDATE admins SET last_login=CURRENT_TIMESTAMP 
                        WHERE id=?''', (admin['id'],))
            conn.commit()
            conn.close()
            return {'success': True, 'admin': dict(admin)}
        
        conn.close()
        return {'success': False, 'message': 'Invalid admin credentials'}
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        conn.close()
        return dict(user) if user else None

print("✅ Authentication module created successfully!")
