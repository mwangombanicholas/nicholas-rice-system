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

# Custom CSS - MODERN CLEAN DESIGN
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg, .stSidebar {
        background: white !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Sidebar text */
    .stSidebar .stRadio label {
        color: #2e7d32 !important;
        font-weight: 500;
        font-size: 16px;
        padding: 8px 12px;
        border-radius: 8px;
        transition: all 0.3s;
    }
    
    .stSidebar .stRadio label:hover {
        background: #e8f5e9;
        color: #1b5e20 !important;
    }
    
    /* Main headers */
    h1, h2, h3 {
        color: #2e7d32 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 2.5rem !important;
        border-bottom: 3px solid #2e7d32;
        padding-bottom: 10px;
        display: inline-block;
    }
    
    /* Product cards */
    .product-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(46,125,50,0.15);
    }
    
    .product-card h3 {
        color: #2e7d32 !important;
        font-size: 1.5rem;
        margin: 0.5rem 0;
    }
    
    .price-tag {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2e7d32 !important;
        margin: 0.5rem 0;
    }
    
    /* Quality badge */
    .quality-badge {
        background: #ffd700;
        color: #333 !important;
        padding: 0.25rem 1rem;
        border-radius: 25px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Info boxes */
    .info-box {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #2e7d32;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    .transport-box {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ff9800;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #2e7d32, #1b5e20);
        color: white !important;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s;
        border: 1px solid transparent;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(46,125,50,0.3);
        background: linear-gradient(135deg, #1b5e20, #2e7d32);
    }
    
    /* Form inputs */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 0.6rem !important;
        font-size: 1rem !important;
        transition: all 0.3s !important;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: #2e7d32 !important;
        box-shadow: 0 0 0 3px rgba(46,125,50,0.1) !important;
    }
    
    /* Metrics */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stMetric label {
        color: #666 !important;
        font-weight: 500;
    }
    
    .stMetric .metric-value {
        color: #2e7d32 !important;
        font-weight: 700;
        font-size: 1.8rem;
    }
    
    /* Dataframes */
    .dataframe {
        background: white;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e0e0e0;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #2e7d32, #1b5e20);
        color: white !important;
        font-weight: 600;
        padding: 12px !important;
    }
    
    .dataframe td {
        padding: 10px !important;
        color: #333 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 10px !important;
        border: 1px solid #e0e0e0 !important;
        color: #2e7d32 !important;
        font-weight: 600;
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 10px !important;
        border-left: 5px solid !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
        color: #666;
    }
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #1e3c32, #2e7d32);
        padding: 2.5rem;
        border-radius: 20px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .main-header h1 {
        color: white !important;
        border-bottom: 3px solid #ffd700;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        color: #333 !important;
        font-weight: 500;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #2e7d32 !important;
        color: white !important;
        border-color: #2e7d32 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 2rem; margin: 0; border: none;">🌾</h1>
        <h2 style="color: #2e7d32; margin: 0;">Nicholas Rice</h2>
        <p style="color: #666; font-size: 0.9rem;">Quality from Karonga</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.is_admin:
        menu = st.radio(
            "Admin Menu",
            ["📊 Dashboard", "📦 Orders", "👥 Users", "📈 Analytics", "⚙️ Settings", "🚪 Logout"],
            label_visibility="collapsed"
        )
    else:
        if st.session_state.user:
            menu = st.radio(
                "Menu",
                ["🏠 Home", "🛒 Order", "📋 My Orders", "🔍 Track", "🎁 Refer", "👤 Profile", "🚪 Logout"],
                label_visibility="collapsed"
            )
        else:
            menu = st.radio(
                "Menu",
                ["🏠 Home", "🛒 Order", "🔍 Track", "🔐 Login", "ℹ️ About"],
                label_visibility="collapsed"
            )
    
    if st.session_state.user:
        st.divider()
        st.markdown(f"""
        <div style="background: #e8f5e9; padding: 1rem; border-radius: 10px;">
            <p style="color: #2e7d32; font-weight: 600; margin: 0;">👋 {st.session_state.user['username']}</p>
            <p style="color: #f57c00; font-weight: 600; margin: 0;">⭐ {st.session_state.user['points']} pts</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# HOME PAGE
# ============================================
if menu == "🏠 Home":
    st.markdown(f"""
    <div class="main-header">
        <h1>🌾 {APP_NAME}</h1>
        <p style="font-size: 1.2rem;">{PRODUCT_DESCRIPTION}</p>
        <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 50px; display: inline-block; margin-top: 1rem;">
            <span style="font-weight: 600;">📍 Mzuzu | 📞 0886 867 758</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Delivery options cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0;">📍 Mzuzu</h3>
            <p style="font-size: 1rem;">Doorstep delivery</p>
            <p style="color: #2e7d32; font-weight: 600;">Transport cost added</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="transport-box">
            <h3 style="margin-top: 0;">📦 Nationwide</h3>
            <p style="font-size: 1rem;">CTS/Speed Couriers</p>
            <p style="color: #ff9800; font-weight: 600;">Pay at branch</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0;">🏫 MZUNI</h3>
            <p style="font-size: 1rem;">Campus delivery</p>
            <p style="color: #2e7d32; font-weight: 600;">Free delivery</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("🌟 Our Products")
    
    cols = st.columns(4)
    products = [
        {"size": 1, "price": 4000, "desc": "Perfect for students"},
        {"size": 5, "price": 20000, "desc": "Family size"},
        {"size": 10, "price": 40000, "desc": "Great for sharing"},
        {"size": 20, "price": 80000, "desc": "Bulk purchase"}
    ]
    
    for idx, product in enumerate(products):
        with cols[idx]:
            st.markdown(f"""
            <div class="product-card">
                <div class="quality-badge">⭐ Karonga</div>
                <h3>{product['size']}kg</h3>
                <p class="price-tag">{format_currency(product['price'])}</p>
                <p style="color: #666;">{product['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Order", key=f"home_{product['size']}"):
                st.session_state['order_qty'] = product['size']
                st.rerun()

# ============================================
# ORDER PAGE
# ============================================
elif menu == "🛒 Order":
    st.title("🛒 Place Order")
    
    quantity = st.session_state.get('order_qty', 1)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="product-card" style="padding: 2rem;">
            <div class="quality-badge">⭐ Karonga Quality</div>
            <h2 style="font-size: 2rem;">{quantity}kg</h2>
            <p class="price-tag" style="font-size: 2rem;">{format_currency(RICE_PRICES[quantity])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        new_qty = st.selectbox("Quantity", [1, 5, 10, 20], index=[1,5,10,20].index(quantity))
        if new_qty != quantity:
            st.session_state['order_qty'] = new_qty
            st.rerun()
    
    with col2:
        with st.form("order_form"):
            st.subheader("Your Details")
            name = st.text_input("Full Name")
            phone = st.text_input("Phone")
            
            st.subheader("Delivery")
            delivery_type = st.selectbox(
                "Method",
                ["Mzuzu Direct", "Other District", "MZUNI Campus"]
            )
            
            if delivery_type == "Mzuzu Direct":
                area = st.selectbox("Area", MZUZU_AREAS)
                if area:
                    cost = get_transport_cost(area)
                    st.info(f"Transport: {format_currency(cost)}")
                house = st.text_input("House Number")
            elif delivery_type == "Other District":
                city = st.selectbox("City", list(CTS_BRANCHES.keys()))
                courier = st.radio("Courier", ["CTS", "Speed"])
                if courier == "CTS" and city:
                    branch = st.selectbox("Branch", CTS_BRANCHES[city])
                recipient = st.text_input("Recipient Name")
            else:
                location = st.selectbox("Location", CAMPUS_LOCATIONS)
                if location == "Village":
                    st.text_input("House Number")
                else:
                    st.text_input("Room Number")
            
            st.subheader("Payment")
            payment = st.selectbox("Method", ["Pay on Delivery", "Mobile Money", "Bank Transfer"])
            notes = st.text_area("Notes (optional)")
            
            if st.form_submit_button("✅ Confirm Order", use_container_width=True):
                st.success("Order placed! You'll receive confirmation soon.")
                st.balloons()

# ============================================
# OTHER PAGES (simplified)
# ============================================
elif menu == "🔍 Track":
    st.title("🔍 Track Order")
    tracking = st.text_input("Order Number")
    if tracking:
        st.info("Order status will appear here")

elif menu == "🔐 Login":
    st.title("🔐 Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login"):
            st.text_input("Username")
            st.text_input("Password", type="password")
            st.form_submit_button("Login", use_container_width=True)
    
    with tab2:
        with st.form("register"):
            st.text_input("Username")
            st.text_input("Password", type="password")
            st.text_input("Confirm Password", type="password")
            st.text_input("Phone")
            st.form_submit_button("Register", use_container_width=True)

elif menu == "ℹ️ About":
    st.title("ℹ️ About")
    st.markdown("""
    ### Nicholas Rice Seller
    Quality rice from Karonga, delivered to your doorstep.
    
    **📍 Mzuzu** - Direct delivery
    **📦 Nationwide** - Via courier
    **🏫 MZUNI** - Free campus delivery
    """)

elif menu == "🚪 Logout":
    st.session_state.user = None
    st.session_state.is_admin = False
    st.rerun()

# Footer
st.markdown("""
<div class="footer">
    <p>🌾 Nicholas Rice | Quality from Karonga | 📞 0886 867 758</p>
</div>
""", unsafe_allow_html=True)
