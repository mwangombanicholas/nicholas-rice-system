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

# Simple, clean CSS
st.markdown("""
<style>
    /* Main text - all dark for visibility */
    .stApp, p, h1, h2, h3, h4, h5, h6, label, span, div {
        color: #000000 !important;
    }
    
    /* Sidebar - white background */
    .css-1d391kg, .stSidebar {
        background-color: #ffffff !important;
    }
    
    /* Sidebar text - black */
    .stSidebar .stRadio label {
        color: #000000 !important;
        font-size: 16px;
        padding: 8px;
    }
    
    /* Headers - green */
    h1 {
        color: #2e7d32 !important;
        font-size: 2rem !important;
    }
    
    /* Product cards */
    .product-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        text-align: center;
        margin: 10px 0;
    }
    
    .price-tag {
        color: #2e7d32 !important;
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #2e7d32;
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    /* Input fields */
    .stTextInput input, .stSelectbox select {
        background-color: #ffffff;
        border: 1px solid #ccc;
        color: #000000 !important;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        margin: 10px 0;
        color: #000000 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        background-color: #f5f5f5;
        border-radius: 10px;
        margin-top: 30px;
        color: #000000 !important;
    }
    
    /* Success messages */
    .stAlert {
        background-color: #d4edda !important;
        color: #155724 !important;
    }
    
    /* Error messages */
    .stAlert[data-baseweb="alert"] {
        background-color: #f8d7da !important;
        color: #721c24 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
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

# Home Page
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

# Order Page
elif menu == "🛒 Order":
    st.title("Place Your Order")
    
    qty = st.session_state.get('order_qty', 1)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{qty}kg Rice**")
        st.markdown(f"**Price:** MWK {RICE_PRICES[qty]:,}")
        new_qty = st.selectbox("Change Quantity", [1,5,10,20], index=[1,5,10,20].index(qty))
        if new_qty != qty:
            st.session_state['order_qty'] = new_qty
            st.rerun()
    
    with col2:
        with st.form("order_form"):
            st.text_input("Full Name")
            st.text_input("Phone Number")
            
            delivery = st.selectbox("Delivery Type", ["Mzuzu Direct", "Other District", "MZUNI Campus"])
            
            if delivery == "Mzuzu Direct":
                st.selectbox("Area", MZUZU_AREAS)
                st.text_input("House Number")
            elif delivery == "Other District":
                st.selectbox("City", list(CTS_BRANCHES.keys()))
                st.radio("Courier", ["CTS", "Speed"])
            else:
                st.selectbox("Location", CAMPUS_LOCATIONS)
                st.text_input("Room/House")
            
            st.selectbox("Payment", ["Pay on Delivery", "Mobile Money", "Bank Transfer"])
            
            if st.form_submit_button("Confirm Order"):
                st.success("Order placed successfully!")
                st.balloons()

# Track Order
elif menu == "🔍 Track":
    st.title("Track Order")
    tracking = st.text_input("Enter Order Number")
    if tracking:
        st.info("Order status will appear here")

# Login Page
elif menu == "🔐 Login":
    st.title("Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                st.session_state.user = {"username": username, "points": 0}
                st.rerun()
    
    with tab2:
        with st.form("register"):
            st.text_input("Username")
            st.text_input("Password", type="password")
            st.text_input("Confirm Password", type="password")
            st.text_input("Phone")
            if st.form_submit_button("Register"):
                st.success("Registered successfully! Please login.")

# My Orders
elif menu == "📋 My Orders":
    st.title("My Orders")
    st.info("No orders yet")

# Profile
elif menu == "👤 Profile":
    st.title("Profile")
    if st.session_state.user:
        st.write(f"**Username:** {st.session_state.user['username']}")
        st.write(f"**Points:** {st.session_state.user['points']} ⭐")
    else:
        st.warning("Please login first")

# About
elif menu == "ℹ️ About":
    st.title("About")
    st.markdown("""
    ### Nicholas Rice Seller
    - **Location:** Mzuzu, Malawi
    - **Supplier:** Karonga (Quality Rice)
    - **Contact:** 0886 867 758
    - **Email:** mwangombanicholas@gmail.com
    
    ### Delivery Options
    - **Mzuzu Direct:** Doorstep delivery (transport cost added)
    - **Other Districts:** CTS/Speed couriers (pay at branch)
    - **MZUNI Campus:** Free delivery to all locations
    """)

# Logout
elif menu == "🚪 Logout":
    st.session_state.user = None
    st.rerun()

# Footer
st.markdown("""
<div class="footer">
    🌾 Nicholas Rice | Quality from Karonga | 📞 0886 867 758
</div>
""", unsafe_allow_html=True)
