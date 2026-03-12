"""
Main application for Nicholas Rice Ordering System
Author: Nicholas Mwangomba
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import hashlib
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from utils.helpers import *
from utils.auth import Auth
from utils.order_processor import OrderProcessor
from config import *

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌾",
    layout="wide"
)

db = Database()
auth = Auth()
order_processor = OrderProcessor(db)

if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False

# ============================================
# IMPROVED CSS - ALL TEXT VISIBLE, BUTTONS FIXED
# ============================================
st.markdown("""
<style>
    /* Main app background - light */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* ALL headers - GREEN and visible */
    h1, h2, h3, h4, h5, h6 {
        color: #2e7d32 !important;
        font-weight: bold !important;
    }
    
    /* Main title */
    h1 {
        color: #2e7d32 !important;
        font-size: 2.2rem !important;
        border-bottom: 2px solid #2e7d32;
        padding-bottom: 10px;
    }
    
    /* Regular text - black */
    p, li, span, div, .stMarkdown, .stText {
        color: #000000 !important;
    }
    
    /* Sidebar - white background */
    .css-1d391kg, .stSidebar {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Sidebar text - black */
    .stSidebar .stRadio label {
        color: #000000 !important;
        font-size: 16px;
        padding: 8px;
    }
    
    /* FIX 1: ALL BUTTONS - Bright and visible */
    .stButton button {
        background-color: #2e7d32 !important;
        color: white !important;
        font-weight: bold !important;
        border: 2px solid #1b5e20 !important;
        border-radius: 5px !important;
        padding: 10px 20px !important;
        width: 100%;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    .stButton button:hover {
        background-color: #1b5e20 !important;
        border-color: #0a3a0a !important;
        transform: scale(1.02);
    }
    
    /* FIX 2: DROPDOWN SELECTION - Make options visible */
    .stSelectbox select {
        background-color: white !important;
        color: black !important;
        border: 2px solid #2e7d32 !important;
        border-radius: 5px !important;
        padding: 8px !important;
    }
    
    /* Dropdown menu options */
    .stSelectbox option {
        background-color: white !important;
        color: black !important;
        padding: 10px !important;
    }
    
    /* Selected option */
    .stSelectbox select:focus {
        border-color: #1b5e20 !important;
        outline: none !important;
    }
    
    /* FIX 3: TEXT INPUTS - Visible */
    .stTextInput input {
        background-color: white !important;
        color: black !important;
        border: 2px solid #ccc !important;
        border-radius: 5px !important;
        padding: 8px !important;
    }
    
    .stTextInput input:focus {
        border-color: #2e7d32 !important;
    }
    
    /* FIX 4: RADIO BUTTONS - Visible */
    .stRadio label {
        color: black !important;
    }
    
    /* FIX 5: TEXT AREA - Visible */
    .stTextArea textarea {
        background-color: white !important;
        color: black !important;
        border: 2px solid #ccc !important;
        border-radius: 5px !important;
    }
    
    /* FIX 6: NUMBER INPUT - Visible */
    .stNumberInput input {
        background-color: white !important;
        color: black !important;
    }
    
    /* Product cards */
    .product-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .product-card b {
        color: #2e7d32 !important;
        font-size: 1.2rem;
    }
    
    .price-tag {
        color: #2e7d32 !important;
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .info-box b {
        color: #2e7d32 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        margin-top: 30px;
        border: 1px solid #ddd;
        color: #000000 !important;
    }
    
    /* Success messages */
    .stAlert {
        background-color: #d4edda !important;
        color: #155724 !important;
        border-radius: 5px;
        border-left: 5px solid #28a745 !important;
    }
    
    /* Error messages */
    .stAlert[data-baseweb="alert"] {
        background-color: #f8d7da !important;
        color: #721c24 !important;
        border-left: 5px solid #dc3545 !important;
    }
    
    /* Table text */
    table, th, td {
        color: #000000 !important;
    }
    
    /* Metric labels */
    .stMetric label {
        color: #000000 !important;
    }
    
    .stMetric .metric-value {
        color: #2e7d32 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button {
        color: black !important;
        background-color: white !important;
        border: 1px solid #ccc !important;
        border-radius: 5px 5px 0 0 !important;
        padding: 10px 20px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #2e7d32 !important;
        font-weight: bold;
        border-bottom: 3px solid #2e7d32 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        color: #2e7d32 !important;
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## 🌾 Nicholas Rice")
    st.markdown("Quality from Karonga")
    st.divider()
    
    if st.session_state.user:
        menu = st.radio("Menu", ["🏠 Home", "🛒 Order", "📋 My Orders", "🔍 Track", "👤 Profile", "🚪 Logout"])
        st.markdown(f"**Welcome, {st.session_state.user['username']}!**")
        st.markdown(f"**Points:** {st.session_state.user['points']} ⭐")
    else:
        menu = st.radio("Menu", ["🏠 Home", "🛒 Order", "🔍 Track", "🔐 Login", "ℹ️ About"])

# ============================================
# HOME PAGE
# ============================================
if menu == "🏠 Home":
    st.title("🌾 Nicholas Rice Seller")
    st.markdown("**Quality rice from Karonga - Fresh, aromatic, and premium grade**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <b>📍 Mzuzu Direct</b><br>
            Doorstep delivery<br>
            Transport cost added
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <b>📦 Other Districts</b><br>
            CTS/Speed Couriers<br>
            Pay at branch
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
            <b>🏫 MZUNI Campus</b><br>
            Free delivery<br>
            All hostels & villages
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("Our Products")
    
    cols = st.columns(4)
    products = [
        {"size": 1, "price": 4000},
        {"size": 5, "price": 20000},
        {"size": 10, "price": 40000},
        {"size": 20, "price": 80000}
    ]
    
    for idx, p in enumerate(products):
        with cols[idx]:
            st.markdown(f"""
            <div class="product-card">
                <b>{p['size']}kg Rice</b><br>
                <span class="price-tag">MWK {p['price']:,}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Order {p['size']}kg", key=f"home_{p['size']}"):
                st.session_state['order_qty'] = p['size']
                st.rerun()

# ============================================
# ORDER PAGE
# ============================================
elif menu == "🛒 Order":
    st.title("Place Your Order")
    
    qty = st.session_state.get('order_qty', 1)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="product-card">
            <b>{qty}kg Rice</b><br>
            <span class="price-tag">MWK {RICE_PRICES[qty]:,}</span>
        </div>
        """, unsafe_allow_html=True)
        
        new_qty = st.selectbox("Change Quantity", [1,5,10,20], index=[1,5,10,20].index(qty))
        if new_qty != qty:
            st.session_state['order_qty'] = new_qty
            st.rerun()
    
    with col2:
        with st.form("order_form"):
            st.subheader("Your Details")
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone Number *")
            
            st.subheader("Delivery")
            delivery = st.selectbox("Delivery Type", ["Mzuzu Direct", "Other District", "MZUNI Campus"])
            
            transport_cost = 0
            
                       if delivery == "Mzuzu Direct":
                area = st.selectbox("Select Area", [""] + MZUZU_AREAS)
                if area and area != "Other (specify in notes)":
                    transport_cost = get_transport_cost(area)
                    st.info(f"Transport cost: MWK {transport_cost:,}")
                house = st.text_input("House Number *")
                
            elif delivery == "Other District":
                city = st.selectbox("Select City", [""] + list(CTS_BRANCHES.keys()))
                courier = st.radio("Courier Service", ["CTS", "Speed"])
                if courier == "CTS" and city:
                    branch = st.selectbox("Select Branch", [""] + CTS_BRANCHES[city])
                recipient = st.text_input("Recipient Name *")
                
            else:  # MZUNI Campus
                location = st.selectbox("Select Location", [""] + CAMPUS_LOCATIONS)
                if location == "Village":
                    house = st.text_input("House Number *")
                else:
                    room = st.text_input("Room/Block Number *")
            
            st.subheader("Payment")
            payment = st.selectbox("Payment Method", ["Pay on Delivery", "Mobile Money", "Bank Transfer"])
            notes = st.text_area("Special Instructions (Optional)")
            
            total = RICE_PRICES[qty] + transport_cost
            st.markdown(f"""
            <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <b>Total: MWK {total:,}</b>
            </div>
            """, unsafe_allow_html=True)
            
            if st.form_submit_button("✅ Confirm Order", use_container_width=True):
                if name and phone:
                    st.success("Order placed successfully!")
                    st.balloons()
                else:
                    st.error("Please fill all required fields")

# ============================================
# TRACK ORDER PAGE
# ============================================
elif menu == "🔍 Track":
    st.title("Track Order")
    tracking = st.text_input("Enter Order Number or Tracking Number")
    if tracking:
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE order_number=? OR tracking_number=?", (tracking, tracking))
        order = c.fetchone()
        conn.close()
        if order:
            st.success(f"Order #{order['order_number']} found!")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Quantity", f"{order['quantity']}kg")
                st.metric("Total", format_currency(order['total_amount']))
            with col2:
                st.metric("Status", order['order_status'])
                st.metric("Date", order['created_at'][:10])
        else:
            st.error("Order not found")

# ============================================
# LOGIN PAGE
# ============================================
elif menu == "🔐 Login":
    st.title("Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                result = auth.login_user(username, password)
                if result['success']:
                    st.session_state.user = result['user']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Username *")
            new_pwd = st.text_input("Password *", type="password")
            confirm = st.text_input("Confirm Password *", type="password")
            new_phone = st.text_input("Phone Number *")
            new_email = st.text_input("Email (optional)")
            
            if st.form_submit_button("Register", use_container_width=True):
                if new_pwd != confirm:
                    st.error("Passwords do not match")
                elif len(new_pwd) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    result = auth.register_user(new_user, new_pwd, new_phone, new_email)
                    if result['success']:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(result['message'])

# ============================================
# MY ORDERS PAGE
# ============================================
elif menu == "📋 My Orders":
    st.title("My Orders")
    if not st.session_state.user:
        st.warning("Please login first")
    else:
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (st.session_state.user['id'],))
        orders = c.fetchall()
        conn.close()
        
        if orders:
            for order in orders:
                with st.expander(f"Order #{order['order_number']} - {order['created_at'][:10]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Quantity:** {order['quantity']}kg")
                        st.write(f"**Total:** {format_currency(order['total_amount'])}")
                        st.write(f"**Payment:** {order['payment_method']}")
                    with col2:
                        status_color = get_order_status_color(order['order_status'])
                        st.markdown(f"**Status:** <span style='color: {status_color};'>{order['order_status']}</span>", unsafe_allow_html=True)
                        st.write(f"**Tracking:** {order['tracking_number']}")
        else:
            st.info("No orders yet")

# ============================================
# PROFILE PAGE
# ============================================
elif menu == "👤 Profile":
    st.title("Profile")
    if not st.session_state.user:
        st.warning("Please login first")
    else:
        user = st.session_state.user
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Username:** {user['username']}")
            st.write(f"**Phone:** {user['phone']}")
            st.write(f"**Email:** {user.get('email', 'Not set')}")
        with col2:
            st.write(f"**Points:** {user['points']} ⭐")
            st.write(f"**Member since:** {user.get('created_at', 'N/A')[:10]}")

# ============================================
# ABOUT PAGE
# ============================================
elif menu == "ℹ️ About":
    st.title("About")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Nicholas Rice Seller
        - **Location:** Mzuzu, Malawi
        - **Supplier:** Karonga (Quality Rice)
        - **Contact:** 0886 867 758
        - **Email:** mwangombanicholas@gmail.com
        """)
    
    with col2:
        st.markdown("""
        ### Delivery Options
        - **📍 Mzuzu Direct:** Doorstep delivery (transport cost added)
        - **📦 Other Districts:** CTS/Speed couriers (pay at branch)
        - **🏫 MZUNI Campus:** Free delivery to all locations
        """)

# ============================================
# LOGOUT
# ============================================
elif menu == "🚪 Logout":
    st.session_state.user = None
    st.rerun()

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    🌾 Nicholas Rice | Quality from Karonga | 📞 0886 867 758
</div>
""", unsafe_allow_html=True)
