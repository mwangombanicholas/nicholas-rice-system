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
# IMPROVED CSS - ALL TEXT VISIBLE
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
    
    /* ALL BUTTONS - Bright and visible */
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
    
    /* DROPDOWN SELECTION - Visible */
    .stSelectbox select {
        background-color: white !important;
        color: black !important;
        border: 2px solid #2e7d32 !important;
        border-radius: 5px !important;
        padding: 8px !important;
    }
    
    .stSelectbox option {
        background-color: white !important;
        color: black !important;
        padding: 10px !important;
    }
    
    /* TEXT INPUTS - Visible */
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
    
    /* RADIO BUTTONS - Visible */
    .stRadio label {
        color: black !important;
    }
    
    /* TEXT AREA - Visible */
    .stTextArea textarea {
        background-color: white !important;
        color: black !important;
        border: 2px solid #ccc !important;
        border-radius: 5px !important;
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
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button {
        color: black !important;
        background-color: white !important;
        border: 1px solid #ccc !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #2e7d32 !important;
        font-weight: bold;
        border-bottom: 3px solid #2e7d32 !important;
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
# ORDER PAGE - COMPLETELY FIXED WITH CORRECT OPTIONS
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
            
            # Delivery type selection
            delivery_option = st.radio(
                "Choose Delivery Method",
                ["Mzuzu Direct Delivery", "Other District (Courier)", "MZUNI Campus"]
            )
            
            transport_cost = 0
            delivery_location = ""
            delivery_area = ""
            house = ""
            room = ""
            city = ""
            courier = ""
            branch = ""
            recipient = ""
            location = ""
            
            # ============================================
            # OPTION 1: MZUZU DIRECT DELIVERY
            # ============================================
            if delivery_option == "Mzuzu Direct Delivery":
                st.markdown("**📍 Mzuzu Areas**")
                
                # Mzuzu areas only
                mzuzu_areas = [
                    "Town (City Centre)",
                    "Luwinga",
                    "Katawa",
                    "Zolozolo",
                    "Chibanja",
                    "Mchengautuwa",
                    "Masasa",
                    "Area 1B",
                    "Area 1C",
                    "McDonald's Area",
                    "Mzimba Street",
                    "Chibavi"
                ]
                
                area = st.selectbox("Select Your Area", [""] + mzuzu_areas)
                if area:
                    # Calculate transport cost
                    if area in ["Town (City Centre)", "Masasa", "Area 1B", "Area 1C", "McDonald's Area", "Mzimba Street"]:
                        transport_cost = 2000
                    elif area in ["Luwinga", "Zolozolo"]:
                        transport_cost = 2500
                    elif area in ["Katawa", "Chibanja", "Chibavi"]:
                        transport_cost = 3000
                    elif area == "Mchengautuwa":
                        transport_cost = 3500
                    
                    st.info(f"Transport cost: MWK {transport_cost:,}")
                
                house = st.text_input("House/Plot Number *")
                delivery_location = area
                delivery_area = area
                
            # ============================================
            # OPTION 2: OTHER DISTRICT (COURIER)
            # ============================================
            elif delivery_option == "Other District (Courier)":
                st.markdown("**📦 Courier Delivery to Other Districts**")
                
                # Malawi districts/cities
                malawi_cities = [
                    "Lilongwe",
                    "Blantyre",
                    "Zomba",
                    "Kasungu",
                    "Dedza",
                    "Balaka",
                    "Mangochi",
                    "Ntcheu",
                    "Mchinji",
                    "Chiradzulu",
                    "Thyolo",
                    "Mulanje",
                    "Phalombe",
                    "Chikwawa",
                    "Nsanje",
                    "Nkhotakota",
                    "Rumphi",
                    "Karonga",
                    "Salima"
                ]
                
                city = st.selectbox("Select City", [""] + malawi_cities)
                
                courier = st.radio("Courier Service", ["CTS", "Speed Couriers"])
                
                # CTS branches based on city
                if courier == "CTS" and city:
                    if city == "Lilongwe":
                        branches = ["Gravity Mall", "Chitipi", "Bunda", "Area 23", "Area 49"]
                    elif city == "Blantyre":
                        branches = ["Ginnery Corner", "Ndirande", "Lunzu", "Green Corner", "Limbe", "Bangwe"]
                    elif city == "Zomba":
                        branches = ["3 Miles", "Matawale", "Chikanda"]
                    else:
                        branches = ["Main Branch"]
                    
                    branch = st.selectbox("Select Branch", [""] + branches)
                
                recipient = st.text_input("Recipient Name *")
                delivery_location = city
                
            # ============================================
            # OPTION 3: MZUNI CAMPUS
            # ============================================
            else:  # MZUNI Campus
                st.markdown("**🏫 MZUNI Campus Delivery**")
                
                # MZUNI campus locations only
                mzuni_locations = [
                    "Male Singles Rooms",
                    "Female Singles Rooms",
                    "Chai Hostel",
                    "Norah Hostel",
                    "Kandahar Hostel",
                    "Village"
                ]
                
                location = st.selectbox("Select Location", [""] + mzuni_locations)
                
                if location == "Village":
                    house = st.text_input("House Number *")
                else:
                    room = st.text_input("Room/Block Number *")
                
                delivery_location = location
            
            # ============================================
            # PAYMENT SECTION
            # ============================================
            st.subheader("Payment")
            payment = st.selectbox("Payment Method", ["Pay on Delivery", "Mobile Money", "Bank Transfer"])
            notes = st.text_area("Special Instructions (Optional)")
            
            # Calculate total
            total = RICE_PRICES[qty] + transport_cost
            st.markdown(f"""
            <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <b>Total: MWK {total:,}</b>
            </div>
            """, unsafe_allow_html=True)
            
            # Submit button
            if st.form_submit_button("✅ Confirm Order", use_container_width=True):
                if name and phone:
                    st.success("✅ Order placed successfully!")
                    st.balloons()
                    
                    # Show order summary
                    st.info(f"**Order Summary:** {qty}kg rice to {delivery_location}")
                    if transport_cost > 0:
                        st.info(f"Transport cost: MWK {transport_cost:,}")
                else:
                    st.error("Please fill all required fields")

# ============================================
# TRACK ORDER PAGE
# ============================================
elif menu == "🔍 Track":
    st.title("Track Order")
    tracking = st.text_input("Enter Order Number or Tracking Number")
    if tracking:
        st.info("Order status will appear here")

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
        st.write(f"**Username:** {user['username']}")
        st.write(f"**Phone:** {user['phone']}")
        st.write(f"**Points:** {user['points']} ⭐")

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
