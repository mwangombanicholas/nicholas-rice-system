"""
Nicholas Rice Seller - Simplified Working Version
Author: Nicholas Mwangomba
"""

import streamlit as st
import hashlib
import sqlite3
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Nicholas Rice Seller",
    page_icon="🌾",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { color: #2e7d32 !important; }
    .stButton button { background-color: #2e7d32 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.page = "home"

# Simple database setup
DB_PATH = 'rice_shop.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create admins table
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  email TEXT)''')
    
    # Create admin user if not exists
    c.execute("SELECT * FROM admins WHERE username='admin'")
    if not c.fetchone():
        hashed = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO admins (username, password, email) VALUES (?, ?, ?)",
                  ('admin', hashed, 'mwangombanicholas@gmail.com'))
    
    conn.commit()
    conn.close()

# Initialize DB
init_db()

# Simple auth function
def check_admin(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, hashed))
    result = c.fetchone()
    conn.close()
    return result is not None

# Sidebar
with st.sidebar:
    st.markdown("## 🌾 Nicholas Rice")
    st.markdown("Quality from Karonga")
    st.divider()
    
    if st.session_state.is_admin:
        menu = st.radio("Menu", ["🏠 Home", "📊 Admin", "🚪 Logout"])
    else:
        menu = st.radio("Menu", ["🏠 Home", "🔐 Admin Login"])
    
    st.session_state.page = menu

# ============================================
# HOME PAGE
# ============================================
if st.session_state.page == "🏠 Home":
    st.title("🌾 Nicholas Rice Seller")
    st.markdown("**Quality rice from Karonga - Fresh, aromatic, and premium grade**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📍 **Mzuzu Direct**\n\nDoorstep delivery\nTransport cost added")
    with col2:
        st.warning("📦 **Other Districts**\n\nCTS/Speed Couriers\nPay at branch")
    with col3:
        st.success("🏫 **MZUNI Campus**\n\nFree delivery\nAll hostels & villages")
    
    st.divider()
    st.subheader("Our Products")
    
    cols = st.columns(4)
    products = [{"kg": 1, "price": 4000}, {"kg": 5, "price": 20000}, 
                {"kg": 10, "price": 40000}, {"kg": 20, "price": 80000}]
    
    for i, p in enumerate(products):
        with cols[i]:
            st.metric(f"{p['kg']}kg Rice", f"MWK {p['price']:,}")

# ============================================
# ADMIN LOGIN PAGE
# ============================================
elif st.session_state.page == "🔐 Admin Login":
    st.title("Admin Login")
    
    with st.form("login_form"):
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", value="admin123", type="password")
        
        if st.form_submit_button("Login", use_container_width=True):
            if check_admin(username, password):
                st.session_state.is_admin = True
                st.session_state.user = {"username": username}
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

# ============================================
# ADMIN DASHBOARD
# ============================================
elif st.session_state.page == "📊 Admin":
    st.title("📊 Admin Dashboard")
    
    st.success(f"Welcome Admin! You are logged in.")
    
    # Test buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📱 Test Login Working", use_container_width=True):
            st.success("✅ Admin login is working!")
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.is_admin = False
            st.session_state.user = None
            st.rerun()
    
    st.divider()
    st.info("Your system is now working! Add your full features back gradually.")

# ============================================
# LOGOUT
# ============================================
elif st.session_state.page == "🚪 Logout":
    st.session_state.is_admin = False
    st.session_state.user = None
    st.session_state.page = "home"
    st.rerun()

# Footer
st.markdown("---")
st.markdown("🌾 Nicholas Rice | Quality from Karonga | 📞 0886 867 758")
