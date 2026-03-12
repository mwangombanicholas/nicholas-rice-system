"""
Main application for Nicholas Rice Ordering System
Author: Nicholas Mwangomba
Location: Mzuzu, Malawi
Supplier: Karonga (Quality Rice)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from models.database import Database
from utils.helpers import *
from utils.auth import Auth
from utils.order_processor import OrderProcessor
from config import *

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and services
db = Database()
auth = Auth()
order_processor = OrderProcessor(db)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.cart = []
    st.session_state.page = 'home'
    st.session_state.notifications = {}

# Custom CSS - IMPROVED FOR BETTER VISIBILITY
st.markdown("""
<style>
    /* Main text colors */
    .stApp {
        color: #333333;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #2e7d32 !important;
        font-weight: 600 !important;
    }
    
    /* Paragraph text */
    p, li, .stMarkdown {
        color: #333333 !important;
    }
    
    /* Sidebar text */
    .css-1d391kg, .css-1lcbmhc, .stSidebar {
        color: #333333 !important;
    }
    
    /* Sidebar menu items */
    .stRadio label {
        color: #333333 !important;
        font-weight: 500;
    }
    
    /* Metric cards */
    .css-1xarl3l, .stMetric {
        color: #333333 !important;
    }
    
    /* Info boxes */
    .info-box {
        background: #e8f5e9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2e7d32;
        margin: 1rem 0;
        color: #333333;
    }
    
    .transport-box {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
        color: #333333;
    }
    
    /* Product cards */
    .product-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
        margin-bottom: 1rem;
        color: #333333;
    }
    
    .product-card h3 {
        color: #2e7d32 !important;
    }
    
    .product-card p {
        color: #333333 !important;
    }
    
    /* Price tag */
    .price-tag {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e7d32 !important;
        margin: 0.5rem 0;
    }
    
    /* Quality badge */
    .quality-badge {
        background: #ffd700;
        color: #333333 !important;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    /* Supplier badge */
    .supplier-badge {
        background: #2196f3;
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        background: #f8f9fa;
        border-radius: 10px;
        color: #333333;
    }
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #1e3c32, #2e7d32);
        padding: 2rem;
        border-radius: 10px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .main-header h1, .main-header p {
        color: white !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #2e7d32;
        color: white !important;
        font-weight: 600;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    
    .stButton button:hover {
        background-color: #1b5e20;
        color: white !important;
    }
    
    /* Form inputs */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        color: #333333 !important;
        background-color: white;
        border: 1px solid #ddd;
    }
    
    /* Success messages */
    .stAlert {
        color: #333333 !important;
    }
    
    /* Metrics */
    .stMetric label, .stMetric .metric-value {
        color: #333333 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        color: #2e7d32 !important;
        font-weight: 600;
    }
    
    /* Dataframes */
    .dataframe {
        color: #333333 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button {
        color: #333333 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #2e7d32 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x150?text=🌾", width=150)
    st.title(APP_NAME)
    st.markdown(f"*{PRODUCT_DESCRIPTION}*")
    st.markdown(f"📍 **Location:** {YOUR_LOCATION}")
    st.markdown(f"📞 **Phone:** {YOUR_PHONE}")
    
    st.divider()
    
    if st.session_state.is_admin:
        menu = st.radio(
            "Admin Menu",
            ["📊 Dashboard", "📦 Orders", "👥 Users", "📈 Analytics", "⚙️ Settings", "🚪 Logout"]
        )
    else:
        if st.session_state.user:
            menu = st.radio(
                "Menu",
                ["🏠 Home", "🛒 Order Now", "📋 My Orders", "🔍 Track Order", 
                 "🎁 Refer & Earn", "👤 Profile", "🚪 Logout"]
            )
        else:
            menu = st.radio(
                "Menu",
                ["🏠 Home", "🛒 Order Now", "🔍 Track Order", "🔐 Login", "ℹ️ About"]
            )
    
    if st.session_state.user:
        st.divider()
        st.success(f"Welcome, {st.session_state.user['username']}!")
        st.info(f"Points: {st.session_state.user['points']} 🌟")
    
    st.divider()
    st.caption(f"© 2024 {APP_AUTHOR} | Quality Rice from Karonga")

# ============================================
# HOME PAGE
# ============================================
if menu == "🏠 Home":
    # Header with Karonga quality message
    st.markdown(f"""
    <div class="main-header">
        <h1>🌾 {APP_NAME}</h1>
        <p>{PRODUCT_DESCRIPTION}</p>
        <div class="supplier-badge">
            <span>⭐ Quality Rice from Karonga ⭐</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Delivery info boxes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h4>📍 Mzuzu Customers</h4>
            <p><strong>Direct Delivery to Your Home!</strong></p>
            <p>• Transport cost added based on your area</p>
            <p>• We deliver to your doorstep</p>
            <p>• Pay transport fee upon delivery</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="transport-box">
            <h4>📦 Other Districts</h4>
            <p><strong>Via CTS/Speed Couriers</strong></p>
            <p>• You collect at nearest branch</p>
            <p>• Pay courier fees at collection</p>
            <p>• Tracking number provided</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
            <h4>🏫 MZUNI Campus</h4>
            <p><strong>Free Delivery!</strong></p>
            <p>• All hostels and villages</p>
            <p>• No transport cost</p>
            <p>• Delivered to your room</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Products display
    st.subheader("🌟 Our Products - Quality Rice from Karonga")
    st.markdown("*Freshly sourced from Karonga, delivered to you*")
    
    cols = st.columns(4)
    products = [
        {"size": 1, "price": 4000, "desc": "Perfect for students"},
        {"size": 5, "price": 20000, "desc": "Family size, best value"},
        {"size": 10, "price": 40000, "desc": "Great for sharing"},
        {"size": 20, "price": 80000, "desc": "Bulk purchase, save more"}
    ]
    
    for idx, product in enumerate(products):
        with cols[idx]:
            st.markdown(f"""
            <div class="product-card">
                <div class="quality-badge">⭐ Karonga Quality</div>
                <h3>{product['size']}kg Rice</h3>
                <p class="price-tag">{format_currency(product['price'])}</p>
                <p>{product['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Order {product['size']}kg", key=f"home_{product['size']}"):
                st.session_state['order_qty'] = product['size']
                st.rerun()

# ============================================
# ORDER NOW PAGE
# ============================================
elif menu == "🛒 Order Now":
    st.title("🛒 Place Your Order")
    st.markdown(f"*{PRODUCT_DESCRIPTION}*")
    
    quantity = st.session_state.get('order_qty', 1)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image("https://via.placeholder.com/300x300?text=Rice", use_container_width=True)
        st.markdown(f"<h3 style='text-align: center;'>{quantity}kg Karonga Rice</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 24px; color: #2e7d32;'>{format_currency(RICE_PRICES[quantity])}</p>", unsafe_allow_html=True)
        
        new_qty = st.selectbox("Select Quantity", [1, 5, 10, 20], index=[1,5,10,20].index(quantity))
        if new_qty != quantity:
            st.session_state['order_qty'] = new_qty
            st.rerun()
    
    with col2:
        with st.form("order_form"):
            st.subheader("📋 Your Information")
            
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone Number *")
            email = st.text_input("Email (optional)")
            
            st.divider()
            st.subheader("🚚 Delivery Options")
            
            delivery_type = st.radio(
                "Choose Delivery Method *",
                ["Mzuzu Direct Delivery", "Other District (Courier)", "MZUNI Campus (Free)"]
            )
            
            transport_cost = 0
            delivery_location = ""
            delivery_area = ""
            house_number = ""
            courier_service = ""
            cts_branch = ""
            recipient_name = ""
            city = ""
            
            if delivery_type == "Mzuzu Direct Delivery":
                delivery_area = st.selectbox("Select Your Area *", [""] + MZUZU_AREAS)
                if delivery_area and delivery_area != "Other (specify in notes)":
                    transport_cost = get_transport_cost(delivery_area)
                    st.info(f"Transport cost: {format_currency(transport_cost)}")
                house_number = st.text_input("House/Plot Number *")
                
            elif delivery_type == "Other District (Courier)":
                city = st.selectbox("Select City *", [""] + list(CTS_BRANCHES.keys()))
                courier_service = st.radio("Courier Service *", ["CTS", "Speed Couriers"])
                if courier_service == "CTS" and city:
                    cts_branch = st.selectbox("Select CTS Branch *", [""] + CTS_BRANCHES[city])
                recipient_name = st.text_input("Recipient Name (for courier) *")
                delivery_location = city
                
            else:  # Campus
                delivery_location = st.selectbox("Select Location *", [""] + CAMPUS_LOCATIONS)
                if delivery_location == "Village":
                    house_number = st.text_input("House Number *")
                else:
                    delivery_area = st.text_input("Room/Block Number *")
            
            st.divider()
            st.subheader("💳 Payment")
            
            payment_method = st.selectbox(
                "Payment Method *",
                ["", "Pay on Delivery", "Mobile Money", "Bank Transfer"]
            )
            
            notes = st.text_area("Special Instructions (Optional)")
            
            base_price = RICE_PRICES[quantity]
            total = base_price + transport_cost
            
            st.markdown(f"""
            <div style="background: #f0f0f0; padding: 1rem; border-radius: 8px;">
                <h4>Order Summary</h4>
                <p>Rice: {format_currency(base_price)}</p>
                <p>Transport: {format_currency(transport_cost)}</p>
                <p><strong>Total: {format_currency(total)}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("✅ CONFIRM ORDER", use_container_width=True)
            
            if submitted:
                if not all([name, phone, payment_method]):
                    st.error("Please fill all required fields")
                else:
                    order_data = {
                        'user_id': st.session_state.user['id'] if st.session_state.user else None,
                        'customer_name': name,
                        'customer_phone': phone,
                        'customer_email': email,
                        'quantity': quantity,
                        'base_price': base_price,
                        'transport_cost': transport_cost,
                        'total_amount': total,
                        'delivery_type': 'mzuzu_direct' if delivery_type == "Mzuzu Direct Delivery" else ('courier' if delivery_type == "Other District (Courier)" else 'campus'),
                        'delivery_location': delivery_location,
                        'delivery_area': delivery_area,
                        'house_number': house_number,
                        'courier_service': courier_service,
                        'cts_branch': cts_branch,
                        'recipient_name': recipient_name,
                        'payment_method': payment_method,
                        'notes': notes
                    }
                    
                    result = order_processor.process_order(order_data)
                    if result['success']:
                        st.success(f"✅ Order placed! #{result['order_number']}")
                        st.balloons()

# ============================================
# MY ORDERS PAGE
# ============================================
elif menu == "📋 My Orders":
    st.title("📋 My Orders")
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
# TRACK ORDER PAGE
# ============================================
elif menu == "🔍 Track Order":
    st.title("🔍 Track Order")
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
# REFER & EARN PAGE
# ============================================
elif menu == "🎁 Refer & Earn":
    st.title("🎁 Refer & Earn")
    if not st.session_state.user:
        st.warning("Please login first")
    else:
        st.info("Share your referral link with friends. When they order, you get 100 points!")
        referral_code = st.session_state.user.get('referral_code', 'NK123456')
        st.code(f"https://nicholas-rice-system.streamlit.app/?ref={referral_code}")

# ============================================
# PROFILE PAGE
# ============================================
elif menu == "👤 Profile":
    st.title("👤 Profile")
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
            st.write(f"**Points:** {user['points']} 🌟")
            st.write(f"**Member since:** {user['created_at'][:10]}")

# ============================================
# LOGIN PAGE
# ============================================
elif menu == "🔐 Login":
    st.title("🔐 Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login"):
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
        with st.form("register"):
            new_user = st.text_input("Username *")
            new_pwd = st.text_input("Password *", type="password")
            confirm = st.text_input("Confirm Password *", type="password")
            new_phone = st.text_input("Phone Number *")
            new_email = st.text_input("Email (optional)")
            
            if st.form_submit_button("Register", use_container_width=True):
                if new_pwd != confirm:
                    st.error("Passwords don't match")
                elif len(new_pwd) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    result = auth.register_user(new_user, new_pwd, new_phone, new_email)
                    if result['success']:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(result['message'])

# ============================================
# ABOUT PAGE
# ============================================
elif menu == "ℹ️ About":
    st.title("ℹ️ About Us")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Our Story
        We are a rice delivery business based in **Mzuzu**, sourcing premium quality rice directly from **Karonga**.
        
        ### Contact
        * **Phone:** 0886 867 758
        * **Email:** mwangombanicholas@gmail.com
        """)
    with col2:
        st.markdown("""
        ### Delivery Options
        * **📍 Mzuzu Direct** - Doorstep delivery (transport cost added)
        * **📦 Other Districts** - CTS/Speed couriers (pay at branch)
        * **🏫 MZUNI Campus** - Free delivery to all locations
        """)

# ============================================
# ADMIN DASHBOARD
# ============================================
elif menu == "📊 Dashboard" and st.session_state.is_admin:
    st.title("📊 Admin Dashboard")
    stats = db.get_dashboard_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", stats['total_orders'])
    col2.metric("Total Revenue", format_currency(stats['total_revenue']))
    col3.metric("Rice Sold", f"{stats['total_rice']}kg")
    col4.metric("Today's Orders", stats['today_orders'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Pending Orders", stats['pending_orders'])
    col2.metric("Mzuzu Deliveries", stats['mzuzu_pending'])
    col3.metric("Courier Deliveries", stats['courier_pending'])
    
    st.divider()
    st.subheader("Recent Orders")
    
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 20")
    orders = c.fetchall()
    conn.close()
    
    if orders:
        orders_list = []
        for o in orders:
            orders_list.append({
                'Order #': o['order_number'],
                'Customer': o['customer_name'],
                'Phone': o['customer_phone'],
                'Qty': f"{o['quantity']}kg",
                'Total': format_currency(o['total_amount']),
                'Status': o['order_status'],
                'Date': o['created_at'][:16]
            })
        df = pd.DataFrame(orders_list)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No orders yet")

# ============================================
# ADMIN ORDERS PAGE
# ============================================
elif menu == "📦 Orders" and st.session_state.is_admin:
    st.title("📦 All Orders")
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    conn.close()
    
    if orders:
        orders_list = []
        for o in orders:
            orders_list.append({
                'Order #': o['order_number'],
                'Customer': o['customer_name'],
                'Phone': o['customer_phone'],
                'Qty': f"{o['quantity']}kg",
                'Total': format_currency(o['total_amount']),
                'Delivery': o['delivery_type'],
                'Status': o['order_status'],
                'Date': o['created_at'][:16]
            })
        df = pd.DataFrame(orders_list)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No orders yet")

# ============================================
# ADMIN USERS PAGE
# ============================================
elif menu == "👥 Users" and st.session_state.is_admin:
    st.title("👥 Users")
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, email, phone, points, created_at FROM users ORDER BY id DESC")
    users = c.fetchall()
    conn.close()
    
    if users:
        users_list = []
        for u in users:
            users_list.append({
                'ID': u[0],
                'Username': u[1],
                'Email': u[2] or 'N/A',
                'Phone': u[3],
                'Points': u[4],
                'Joined': u[5][:10]
            })
        df = pd.DataFrame(users_list)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No users yet")

# ============================================
# ADMIN ANALYTICS PAGE
# ============================================
elif menu == "📈 Analytics" and st.session_state.is_admin:
    st.title("📈 Analytics")
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT DATE(created_at) as date, COUNT(*) as orders, SUM(total_amount) as revenue FROM orders GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 30")
    data = c.fetchall()
    conn.close()
    
    if data:
        df = pd.DataFrame(data, columns=['Date', 'Orders', 'Revenue'])
        fig = px.line(df, x='Date', y=['Orders', 'Revenue'], title='Daily Sales Trend')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")

# ============================================
# ADMIN SETTINGS PAGE
# ============================================
elif menu == "⚙️ Settings" and st.session_state.is_admin:
    st.title("⚙️ Settings")
    st.info("Settings page coming soon!")

# ============================================
# LOGOUT
# ============================================
elif menu == "🚪 Logout":
    st.session_state.user = None
    st.session_state.is_admin = False
    st.success("Logged out successfully!")
    st.rerun()

# Footer
st.markdown("""
<div class="footer">
    <p>🌾 Quality Rice from Karonga | Mzuzu, Malawi</p>
    <p>📞 0886 867 758 | 📧 mwangombanicholas@gmail.com</p>
</div>
""", unsafe_allow_html=True)
