"""
Nicholas Rice Seller - White Background Everywhere
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

# FORCE WHITE BACKGROUND EVERYWHERE
st.markdown("""
<style>
    /* Force white background on everything */
    .stApp, .main, .block-container, .css-1d391kg, .stSidebar {
        background-color: #FFFFFF !important;
    }
    
    /* All text black by default */
    .stApp, .stApp * {
        color: #000000 !important;
    }
    
    /* Headers in green */
    h1, h2, h3, h4, h5, h6 {
        color: #2e7d32 !important;
        font-weight: bold !important;
    }
    
    /* Sidebar */
    .css-1d391kg, .stSidebar, .stSidebar * {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Sidebar menu */
    .stSidebar .stRadio label {
        color: #000000 !important;
        font-size: 16px !important;
        background-color: transparent !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #2e7d32 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: 2px solid #1b5e20 !important;
    }
    
    /* Info boxes */
    .stAlert, .stInfo, .stSuccess, .stWarning {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #2e7d32 !important;
    }
    
    /* Product cards */
    .product-card {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #2e7d32;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Delivery boxes */
    .delivery-box {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #2e7d32;
        margin: 10px 0;
    }
    
    /* Metrics */
    .stMetric {
        background-color: #FFFFFF !important;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #2e7d32;
    }
    
    .stMetric label, .stMetric .metric-value {
        color: #000000 !important;
    }
    
    /* Footer */
    .footer-text {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        text-align: center;
        padding: 20px;
        margin-top: 30px;
        border-top: 2px solid #2e7d32;
    }
    
    /* Form inputs */
    .stTextInput input, .stSelectbox select {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #2e7d32 !important;
    }
    
    /* Dividers */
    hr {
        border: 1px solid #2e7d32 !important;
    }
    
    /* Remove any dark backgrounds */
    div[data-testid="stVerticalBlock"] {
        background-color: #FFFFFF !important;
    }
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
        menu = st.radio("Menu", ["🏠 Home", "📊 Admin Dashboard", "🚪 Logout"])
    else:
        menu = st.radio("Menu", ["🏠 Home", "🔐 Admin Login"])
    
    st.session_state.page = menu
    
    if st.session_state.is_admin:
        st.divider()
        st.markdown(f"**Logged in as:** admin")

# ============================================
# HOME PAGE
# ============================================
if st.session_state.page == "🏠 Home":
    st.markdown("<h1 style='color: #2e7d32;'>🌾 Nicholas Rice Seller</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #000000; font-size: 1.2em;'>Quality rice from Karonga - Fresh, aromatic, and premium grade</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; margin: 10px 0;">
            <h3 style="color: #2e7d32; margin-top: 0;">📍 Mzuzu Direct</h3>
            <p style="color: #000000; margin: 5px 0;">Doorstep delivery</p>
            <p style="color: #000000; margin: 5px 0;">Transport cost added</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #ff9800; margin: 10px 0;">
            <h3 style="color: #ff9800; margin-top: 0;">📦 Other Districts</h3>
            <p style="color: #000000; margin: 5px 0;">CTS/Speed Couriers</p>
            <p style="color: #000000; margin: 5px 0;">Pay at branch</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; margin: 10px 0;">
            <h3 style="color: #2e7d32; margin-top: 0;">🏫 MZUNI Campus</h3>
            <p style="color: #000000; margin: 5px 0;">Free delivery</p>
            <p style="color: #000000; margin: 5px 0;">All hostels & villages</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2e7d32; font-size: 2em; text-align: center;'>🌟 Our Products</h2>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    products = [
        {"kg": 1, "price": 4000, "desc": "Perfect for students"},
        {"kg": 5, "price": 20000, "desc": "Family size, best value"},
        {"kg": 10, "price": 40000, "desc": "Great for sharing"},
        {"kg": 20, "price": 80000, "desc": "Bulk purchase, save more"}
    ]
    
    for i, p in enumerate(products):
        with cols[i]:
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; text-align: center; margin: 10px 0;">
                <h3 style="color: #2e7d32; font-size: 1.8em; margin: 0;">{p['kg']}kg</h3>
                <p style="color: #2e7d32; font-size: 24px; font-weight: bold; margin: 10px 0;">MWK {p['price']:,}</p>
                <p style="color: #000000; font-size: 14px;">{p['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# ADMIN LOGIN PAGE
# ============================================
elif st.session_state.page == "🔐 Admin Login":
    st.markdown("<h1 style='color: #2e7d32;'>🔐 Admin Login</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 30px; border-radius: 10px; border: 2px solid #2e7d32;">
            <h3 style="color: #2e7d32;">Login to Admin Panel</h3>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", value="admin123", type="password")
            
            if st.form_submit_button("Login", use_container_width=True):
                if check_admin(username, password):
                    st.session_state.is_admin = True
                    st.session_state.user = {"username": username}
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 30px; border-radius: 10px; border: 2px solid #2e7d32;">
            <h3 style="color: #2e7d32;">Demo Credentials</h3>
            <p style="color: #000000; font-size: 16px;"><strong>Username:</strong> admin</p>
            <p style="color: #000000; font-size: 16px;"><strong>Password:</strong> admin123</p>
            <p style="color: #000000; font-size: 14px;">Use these to access the admin dashboard.</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# ADMIN DASHBOARD
# ============================================
elif st.session_state.page == "📊 Admin Dashboard" and st.session_state.is_admin:
    st.markdown("<h1 style='color: #2e7d32;'>📊 Admin Dashboard</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 2px solid #2e7d32; margin: 20px 0;">
        <p style="color: #2e7d32; font-size: 1.2em; margin: 0;">✅ Welcome Admin! You are successfully logged in.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; text-align: center;">
            <h3 style="color: #2e7d32; margin: 0;">Total Orders</h3>
            <p style="color: #000000; font-size: 36px; font-weight: bold; margin: 10px 0;">0</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; text-align: center;">
            <h3 style="color: #2e7d32; margin: 0;">Total Revenue</h3>
            <p style="color: #000000; font-size: 36px; font-weight: bold; margin: 10px 0;">MWK 0</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; text-align: center;">
            <h3 style="color: #2e7d32; margin: 0;">Rice Sold</h3>
            <p style="color: #000000; font-size: 36px; font-weight: bold; margin: 10px 0;">0 kg</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #2e7d32;'>Test Notifications</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📱 Test SMS", use_container_width=True):
            st.markdown("""
            <div style="background-color: #FFFFFF; padding: 15px; border-radius: 5px; border: 2px solid #2e7d32; margin: 10px 0;">
                <p style="color: #000000; margin: 0;">📱 SMS test button clicked - configure Twilio to enable</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("📧 Test Email", use_container_width=True):
            st.markdown("""
            <div style="background-color: #FFFFFF; padding: 15px; border-radius: 5px; border: 2px solid #2e7d32; margin: 10px 0;">
                <p style="color: #000000; margin: 0;">📧 Email test button clicked - configure email to enable</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.is_admin = False
        st.session_state.user = None
        st.rerun()

# ============================================
# LOGOUT
# ============================================
elif st.session_state.page == "🚪 Logout":
    st.session_state.is_admin = False
    st.session_state.user = None
    st.session_state.page = "home"
    st.rerun()

# Footer
st.markdown("""
<div style="background-color: #FFFFFF; text-align: center; padding: 20px; margin-top: 30px; border-top: 2px solid #2e7d32;">
    <p style="color: #000000; font-size: 16px;">🌾 Nicholas Rice | Quality from Karonga | 📞 0886 867 758</p>
</div>
""", unsafe_allow_html=True)
