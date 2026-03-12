"""
Nicholas Rice Seller - Complete System
Author: Nicholas Mwangomba
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import hashlib
import os
import sys
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from utils.helpers import *
from utils.auth import Auth
from utils.order_processor import OrderProcessor
from config import *

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌾",
    layout="wide"
)

# ============================================
# WHITE BACKGROUND CSS
# ============================================
st.markdown("""
<style>
    /* Force white background everywhere */
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
    }
    
    /* Buttons */
    .stButton button {
        background-color: #2e7d32 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: 2px solid #1b5e20 !important;
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
    
    /* Info boxes */
    .info-box {
        background-color: #FFFFFF !important;
        padding: 15px;
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
    
    /* Form inputs */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #2e7d32 !important;
    }
    
    /* Footer */
    .footer {
        background-color: #FFFFFF !important;
        text-align: center;
        padding: 20px;
        margin-top: 30px;
        border-top: 2px solid #2e7d32;
        color: #000000 !important;
    }
    
    /* Success messages */
    .stAlert {
        background-color: #FFFFFF !important;
        border: 2px solid #2e7d32 !important;
        color: #000000 !important;
    }
    
    /* Dataframes */
    .dataframe {
        background-color: #FFFFFF !important;
        border: 2px solid #2e7d32 !important;
    }
    
    .dataframe th {
        background-color: #2e7d32 !important;
        color: #FFFFFF !important;
    }
    
    .dataframe td {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATABASE INITIALIZATION
# ============================================
db = Database()
auth = Auth()
order_processor = OrderProcessor(db)

# ============================================
# SESSION STATE
# ============================================
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.order_qty = 1
    st.session_state.page = "home"
    st.session_state.cart = []

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## 🌾 Nicholas Rice")
    st.markdown("Quality from Karonga")
    st.divider()
    
    if st.session_state.is_admin:
        options = ["🏠 Home", "🛒 Order", "📋 Orders", "📊 Dashboard", "👥 Users", "📈 Analytics", "🚪 Logout"]
    else:
        if st.session_state.user:
            options = ["🏠 Home", "🛒 Order", "📋 My Orders", "🔍 Track", "👤 Profile", "🚪 Logout"]
        else:
            options = ["🏠 Home", "🛒 Order", "🔍 Track", "🔐 Login", "ℹ️ About"]
    
    menu = st.radio("Menu", options, key="nav")
    st.session_state.page = menu
    
    if st.session_state.user:
        st.divider()
        st.markdown(f"**Welcome, {st.session_state.user['username']}!**")
        st.markdown(f"**Points:** {st.session_state.user['points']} ⭐")

# ============================================
# HOME PAGE
# ============================================
if st.session_state.page == "🏠 Home":
    st.markdown("<h1 style='color: #2e7d32;'>🌾 Nicholas Rice Seller</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #000000; font-size: 1.2em;'>Quality rice from Karonga - Fresh, aromatic, and premium grade</p>", unsafe_allow_html=True)
    
    # Delivery Options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; margin: 10px 0;">
            <h3 style="color: #2e7d32; margin-top: 0;">📍 Mzuzu Direct</h3>
            <p style="color: #000000;">Doorstep delivery • Transport cost added</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Order Mzuzu Direct", key="home_mzuzu", use_container_width=True):
            st.session_state.order_qty = 1
            st.session_state.preset_delivery = "Mzuzu Direct"
            st.session_state.page = "🛒 Order"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #ff9800; margin: 10px 0;">
            <h3 style="color: #ff9800; margin-top: 0;">📦 Other Districts</h3>
            <p style="color: #000000;">CTS/Speed Couriers • Pay at branch</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Order Nationwide", key="home_nation", use_container_width=True):
            st.session_state.order_qty = 1
            st.session_state.preset_delivery = "Nationwide"
            st.session_state.page = "🛒 Order"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; margin: 10px 0;">
            <h3 style="color: #2e7d32; margin-top: 0;">🏫 MZUNI Campus</h3>
            <p style="color: #000000;">Free delivery • All hostels & villages</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Order Campus", key="home_campus", use_container_width=True):
            st.session_state.order_qty = 1
            st.session_state.preset_delivery = "Campus"
            st.session_state.page = "🛒 Order"
            st.rerun()
    
    st.divider()
    st.markdown("<h2 style='color: #2e7d32; text-align: center;'>🌟 Our Products</h2>", unsafe_allow_html=True)
    
    # Products Grid
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
                <p style="color: #000000;">{p['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Order {p['kg']}kg", key=f"home_{p['kg']}", use_container_width=True):
                st.session_state.order_qty = p['kg']
                st.session_state.page = "🛒 Order"
                st.rerun()

# ============================================
# ORDER PAGE
# ============================================
elif st.session_state.page == "🛒 Order":
    st.markdown("<h1 style='color: #2e7d32;'>🛒 Place Your Order</h1>", unsafe_allow_html=True)
    
    qty = st.session_state.get('order_qty', 1)
    preset = st.session_state.get('preset_delivery', None)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; text-align: center;">
            <h2 style="color: #2e7d32;">{qty}kg Rice</h2>
            <p style="color: #2e7d32; font-size: 32px; font-weight: bold;">MWK {RICE_PRICES[qty]:,}</p>
        </div>
        """, unsafe_allow_html=True)
        
        new_qty = st.selectbox("Change Quantity", [1,5,10,20], index=[1,5,10,20].index(qty))
        if new_qty != qty:
            st.session_state.order_qty = new_qty
            st.rerun()
    
    with col2:
        with st.form("order_form"):
            st.markdown("<h3 style='color: #2e7d32;'>Your Details</h3>", unsafe_allow_html=True)
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone Number *")
            
            st.markdown("<h3 style='color: #2e7d32;'>Delivery</h3>", unsafe_allow_html=True)
            
            options = ["Mzuzu Direct", "Nationwide", "Campus"]
            idx = 0
            if preset and preset in options:
                idx = options.index(preset)
            
            delivery = st.radio("Choose Method", options, index=idx)
            
            transport = 0
            location = ""
            
            if delivery == "Mzuzu Direct":
                areas = ["Town", "Luwinga", "Katawa", "Zolozolo", "Chibanja", "Masasa", "Area 1B"]
                area = st.selectbox("Select Area", areas)
                if area == "Town" or area == "Masasa" or area == "Area 1B":
                    transport = 2000
                elif area == "Luwinga" or area == "Zolozolo":
                    transport = 2500
                else:
                    transport = 3000
                st.info(f"Transport: MWK {transport:,}")
                house = st.text_input("House Number *")
                location = f"{area} - {house}"
            
            elif delivery == "Nationwide":
                cities = ["Lilongwe", "Blantyre", "Zomba", "Mzuzu", "Kasungu", "Karonga"]
                city = st.selectbox("Select City", cities)
                courier = st.radio("Courier", ["CTS", "Speed"])
                if courier == "CTS":
                    if city == "Lilongwe":
                        branches = ["Gravity Mall", "Area 23", "Area 49"]
                    elif city == "Blantyre":
                        branches = ["Ginnery", "Limbe"]
                    else:
                        branches = ["Main Branch"]
                    branch = st.selectbox("Select Branch", branches)
                recipient = st.text_input("Recipient Name *")
                location = f"{city} via {courier}"
            
            else:  # Campus
                locations = ["Male Singles", "Female Singles", "Chai", "Norah", "Kandahar", "Village"]
                loc = st.selectbox("Select Location", locations)
                if loc == "Village":
                    house = st.text_input("House Number *")
                else:
                    room = st.text_input("Room Number *")
                location = loc
            
            st.markdown("<h3 style='color: #2e7d32;'>Payment</h3>", unsafe_allow_html=True)
            payment = st.selectbox("Method", ["Pay on Delivery", "Mobile Money", "Bank Transfer"])
            notes = st.text_area("Special Instructions")
            
            total = RICE_PRICES[qty] + transport
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 15px; border-radius: 5px; border: 2px solid #2e7d32; margin: 10px 0;">
                <h4 style="color: #2e7d32;">Total: MWK {total:,}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            if st.form_submit_button("✅ Confirm Order", use_container_width=True):
                if name and phone:
                    st.success("✅ Order placed successfully!")
                    st.balloons()
                    if 'preset_delivery' in st.session_state:
                        del st.session_state.preset_delivery
                else:
                    st.error("Please fill required fields")

# ============================================
# TRACK ORDER PAGE
# ============================================
elif st.session_state.page == "🔍 Track":
    st.markdown("<h1 style='color: #2e7d32;'>🔍 Track Order</h1>", unsafe_allow_html=True)
    tracking = st.text_input("Enter Order Number")
    if tracking:
        st.info("Order status will appear here")

# ============================================
# LOGIN PAGE
# ============================================
elif st.session_state.page == "🔐 Login":
    st.markdown("<h1 style='color: #2e7d32;'>🔐 Login</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login"):
            username = st.text_input("Username")
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
        with st.form("register"):
            new_user = st.text_input("Username")
            new_pwd = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            new_phone = st.text_input("Phone")
            if st.form_submit_button("Register", use_container_width=True):
                if new_pwd != confirm:
                    st.error("Passwords don't match")
                else:
                    result = auth.register_user(new_user, new_pwd, new_phone)
                    if result['success']:
                        st.success("Registered! Please login.")
                    else:
                        st.error(result['message'])

# ============================================
# MY ORDERS PAGE
# ============================================
elif st.session_state.page == "📋 My Orders":
    st.markdown("<h1 style='color: #2e7d32;'>📋 My Orders</h1>", unsafe_allow_html=True)
    if not st.session_state.user:
        st.warning("Please login first")
    else:
        st.info("No orders yet")

# ============================================
# PROFILE PAGE
# ============================================
elif st.session_state.page == "👤 Profile":
    st.markdown("<h1 style='color: #2e7d32;'>👤 Profile</h1>", unsafe_allow_html=True)
    if not st.session_state.user:
        st.warning("Please login first")
    else:
        user = st.session_state.user
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Username:** {user['username']}")
            st.write(f"**Phone:** {user['phone']}")
        with col2:
            st.write(f"**Points:** {user['points']} ⭐")

# ============================================
# ABOUT PAGE
# ============================================
elif st.session_state.page == "ℹ️ About":
    st.markdown("<h1 style='color: #2e7d32;'>ℹ️ About</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Nicholas Rice Seller
        - **Location:** Mzuzu, Malawi
        - **Supplier:** Karonga
        - **Contact:** 0886 867 758
        """)
    with col2:
        st.markdown("""
        ### Delivery
        - **Mzuzu Direct:** Doorstep delivery
        - **Nationwide:** CTS/Speed couriers
        - **Campus:** Free delivery
        """)

# ============================================
# ADMIN DASHBOARD
# ============================================
elif st.session_state.page == "📊 Dashboard" and st.session_state.is_admin:
    st.markdown("<h1 style='color: #2e7d32;'>📊 Admin Dashboard</h1>", unsafe_allow_html=True)
    
    stats = db.get_dashboard_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", stats['total_orders'])
    col2.metric("Revenue", format_currency(stats['total_revenue']))
    col3.metric("Rice Sold", f"{stats['total_rice']}kg")
    col4.metric("Today's Orders", stats['today_orders'])
    
    st.divider()
    st.subheader("Recent Orders")
    
    conn = db.get_connection()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 20").fetchall()
    conn.close()
    
    if orders:
        df = pd.DataFrame(orders, columns=['id','order_number','customer_name','customer_phone',
                                          'quantity','total_amount','status','created_at'])
        st.dataframe(df[['order_number','customer_name','quantity','total_amount','status']])

# ============================================
# ADMIN ORDERS PAGE
# ============================================
elif st.session_state.page == "📋 Orders" and st.session_state.is_admin:
    st.markdown("<h1 style='color: #2e7d32;'>📋 All Orders</h1>", unsafe_allow_html=True)
    conn = db.get_connection()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()
    if orders:
        df = pd.DataFrame(orders)
        st.dataframe(df)

# ============================================
# ADMIN USERS PAGE
# ============================================
elif st.session_state.page == "👥 Users" and st.session_state.is_admin:
    st.markdown("<h1 style='color: #2e7d32;'>👥 Users</h1>", unsafe_allow_html=True)
    conn = db.get_connection()
    users = conn.execute("SELECT id, username, phone, points, created_at FROM users").fetchall()
    conn.close()
    if users:
        df = pd.DataFrame(users, columns=['ID','Username','Phone','Points','Joined'])
        st.dataframe(df)

# ============================================
# ADMIN ANALYTICS PAGE
# ============================================
elif st.session_state.page == "📈 Analytics" and st.session_state.is_admin:
    st.markdown("<h1 style='color: #2e7d32;'>📈 Analytics</h1>", unsafe_allow_html=True)
    st.info("Analytics dashboard coming soon")

# ============================================
# LOGOUT
# ============================================
elif st.session_state.page == "🚪 Logout":
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.page = "home"
    st.rerun()

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    🌾 Nicholas Rice | Quality from Karonga | 📞 0886 867 758
</div>
""", unsafe_allow_html=True)
