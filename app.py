
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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c32, #2e7d32);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .product-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
        margin-bottom: 1rem;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .price-tag {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e7d32;
        margin: 0.5rem 0;
    }
    .quality-badge {
        background: #ffd700;
        color: #333;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .info-box {
        background: #e8f5e9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2e7d32;
        margin: 1rem 0;
    }
    .transport-box {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    .supplier-badge {
        background: #2196f3;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        background: #f8f9fa;
        border-radius: 10px;
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
        
        for order in orders:
            with st.expander(f"Order #{order['order_number']}"):
                st.write(f"Quantity: {order['quantity']}kg")
                st.write(f"Total: {format_currency(order['total_amount'])}")
                st.write(f"Status: {order['order_status']}")

# ============================================
# TRACK ORDER PAGE
# ============================================
elif menu == "🔍 Track Order":
    st.title("🔍 Track Order")
    tracking = st.text_input("Enter Order Number")
    if tracking:
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE order_number=?", (tracking,))
        order = c.fetchone()
        conn.close()
        if order:
            st.success(f"Order #{order['order_number']} - {order['order_status']}")
        else:
            st.error("Order not found")

# ============================================
# LOGIN PAGE
# ============================================
elif menu == "🔐 Login":
    st.title("🔐 Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login"):
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                result = auth.login_user(user, pwd)
                if result['success']:
                    st.session_state.user = result['user']
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register"):
            new_user = st.text_input("Username *")
            new_pwd = st.text_input("Password *", type="password")
            confirm = st.text_input("Confirm Password *", type="password")
            new_phone = st.text_input("Phone *")
            new_email = st.text_input("Email")
            
            if st.form_submit_button("Register"):
                if new_pwd != confirm:
                    st.error("Passwords don't match")
                else:
                    result = auth.register_user(new_user, new_pwd, new_phone, new_email)
                    if result['success']:
                        st.success("Registered! Please login.")
                    else:
                        st.error(result['message'])

# ============================================
# ABOUT PAGE
# ============================================
elif menu == "ℹ️ About":
    st.title("ℹ️ About Us")
    st.markdown("""
    ### Our Story
    We are a rice delivery business based in **Mzuzu**, sourcing premium quality rice directly from **Karonga**.
    
    ### Contact
    * Phone: 0886 867 758
    * Email: mwangombanicholas@gmail.com
    """)

# ============================================
# LOGOUT
# ============================================
elif menu == "🚪 Logout":
    st.session_state.user = None
    st.session_state.is_admin = False
    st.rerun()

# ============================================
# ADMIN DASHBOARD
# ============================================
elif menu == "📊 Dashboard" and st.session_state.is_admin:
    st.title("📊 Admin Dashboard")
    stats = db.get_dashboard_stats()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", stats['total_orders'])
    col2.metric("Revenue", format_currency(stats['total_revenue']))
    col3.metric("Rice Sold", f"{stats['total_rice']}kg")

# Footer
st.markdown("""
<div class="footer">
    <p>🌾 Quality Rice from Karonga | Mzuzu, Malawi</p>
    <p>📞 0886 867 758 | 📧 mwangombanicholas@gmail.com</p>
</div>
""", unsafe_allow_html=True)
