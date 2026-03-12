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

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌾",
    layout="wide"
)

# ============================================
# DATABASE AND SERVICES INITIALIZATION
# ============================================
db = Database()
auth = Auth()
order_processor = OrderProcessor(db)

# ============================================
# TEMPORARY - RESET ADMIN PASSWORD (REMOVE AFTER USE)
# ============================================
# ============================================
# TEMPORARY - CREATE SIMPLE ADMIN (REMOVE AFTER USE)
# ============================================
try:
    import hashlib
    conn = db.get_connection()
    c = conn.cursor()
    # Delete existing admin
    c.execute("DELETE FROM admins WHERE username='admin'")
    # Create new admin with simple password
    hashed = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT INTO admins (username, password, email, role) VALUES (?, ?, ?, ?)",
              ('admin', hashed, 'mwangombanicholas@gmail.com', 'superadmin'))
    conn.commit()
    conn.close()
    print("✅ Admin reset: username='admin', password='admin123'")
except Exception as e:
    print(f"⚠️ Admin reset error: {e}")
# ============================================
# ============================================

if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.order_qty = 1
    st.session_state.page = "home"

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
    
    /* Clickable delivery boxes */
    .clickable-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .clickable-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(46,125,50,0.2);
        border-color: #2e7d32;
    }
    
    .clickable-box h4 {
        color: #2e7d32 !important;
        margin: 0;
    }
    
    .clickable-box p {
        color: #000000 !important;
        margin: 5px 0 0 0;
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
    
    /* RADIO BUTTONS - Visible */
    .stRadio label {
        color: black !important;
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
    }
    
    /* Debug section styling */
    .debug-box {
        background-color: #f0f0f0;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ff9800;
        margin: 10px 0;
        font-family: monospace;
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
    
    # Menu selection
    if st.session_state.user:
        if st.session_state.is_admin:
            options = ["🏠 Home", "🛒 Order", "📋 My Orders", "🔍 Track", "👤 Profile", "📊 Dashboard", "🚪 Logout"]
        else:
            options = ["🏠 Home", "🛒 Order", "📋 My Orders", "🔍 Track", "👤 Profile", "🚪 Logout"]
    else:
        options = ["🏠 Home", "🛒 Order", "🔍 Track", "🔐 Login", "ℹ️ About"]
    
    selected = st.radio("Menu", options, key="nav")
    st.session_state.page = selected
    
    if st.session_state.user:
        st.divider()
        st.markdown(f"**Welcome, {st.session_state.user['username']}!**")
        st.markdown(f"**Points:** {st.session_state.user['points']} ⭐")

# ============================================
# HOME PAGE
# ============================================
if st.session_state.page == "🏠 Home":
    st.title("🌾 Nicholas Rice Seller")
    st.markdown("**Quality rice from Karonga - Fresh, aromatic, and premium grade**")
    
    # Clickable delivery boxes row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        box_clicked = st.button(
            "📍 Mzuzu Direct\n\nDoorstep delivery\nTransport cost added",
            key="box_mzuzu",
            use_container_width=True
        )
        if box_clicked:
            st.session_state['order_qty'] = 1
            st.session_state['preset_delivery'] = "Mzuzu Direct Delivery"
            st.session_state.page = "🛒 Order"
            st.rerun()
    
    with col2:
        box_clicked = st.button(
            "📦 Other Districts\n\nCTS/Speed Couriers\nPay at branch",
            key="box_other",
            use_container_width=True
        )
        if box_clicked:
            st.session_state['order_qty'] = 1
            st.session_state['preset_delivery'] = "Other District (Courier)"
            st.session_state.page = "🛒 Order"
            st.rerun()
    
    with col3:
        box_clicked = st.button(
            "🏫 MZUNI Campus\n\nFree delivery\nAll hostels & villages",
            key="box_campus",
            use_container_width=True
        )
        if box_clicked:
            st.session_state['order_qty'] = 1
            st.session_state['preset_delivery'] = "MZUNI Campus"
            st.session_state.page = "🛒 Order"
            st.rerun()
    
    st.divider()
    st.subheader("Our Products")
    
    # Products in 4 columns with clickable buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center; margin-bottom: 10px;">
            <b style="color: #2e7d32; font-size: 1.2rem;">1kg Rice</b><br>
            <span style="color: #2e7d32; font-size: 24px; font-weight: bold;">MWK 4,000</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Order 1kg", key="home_1kg", use_container_width=True):
            st.session_state['order_qty'] = 1
            st.session_state.page = "🛒 Order"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center; margin-bottom: 10px;">
            <b style="color: #2e7d32; font-size: 1.2rem;">5kg Rice</b><br>
            <span style="color: #2e7d32; font-size: 24px; font-weight: bold;">MWK 20,000</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Order 5kg", key="home_5kg", use_container_width=True):
            st.session_state['order_qty'] = 5
            st.session_state.page = "🛒 Order"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center; margin-bottom: 10px;">
            <b style="color: #2e7d32; font-size: 1.2rem;">10kg Rice</b><br>
            <span style="color: #2e7d32; font-size: 24px; font-weight: bold;">MWK 40,000</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Order 10kg", key="home_10kg", use_container_width=True):
            st.session_state['order_qty'] = 10
            st.session_state.page = "🛒 Order"
            st.rerun()
    
    with col4:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center; margin-bottom: 10px;">
            <b style="color: #2e7d32; font-size: 1.2rem;">20kg Rice</b><br>
            <span style="color: #2e7d32; font-size: 24px; font-weight: bold;">MWK 80,000</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Order 20kg", key="home_20kg", use_container_width=True):
            st.session_state['order_qty'] = 20
            st.session_state.page = "🛒 Order"
            st.rerun()

# ============================================
# ORDER PAGE
# ============================================
elif st.session_state.page == "🛒 Order":
    st.title("Place Your Order")
    
    qty = st.session_state.get('order_qty', 1)
    preset_delivery = st.session_state.get('preset_delivery', None)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <b style="color: #2e7d32; font-size: 1.5rem;">{qty}kg Rice</b><br>
            <span style="color: #2e7d32; font-size: 32px; font-weight: bold;">MWK {RICE_PRICES[qty]:,}</span>
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
            
            # Delivery options with preset if coming from homepage
            delivery_options = ["Mzuzu Direct Delivery", "Other District (Courier)", "MZUNI Campus"]
            
            if preset_delivery and preset_delivery in delivery_options:
                default_index = delivery_options.index(preset_delivery)
            else:
                default_index = 0
            
            delivery_option = st.radio(
                "Choose Delivery Method",
                delivery_options,
                index=default_index
            )
            
            transport_cost = 0
            delivery_location = ""
            house = ""
            room = ""
            city = ""
            courier = ""
            branch = ""
            recipient = ""
            location = ""
            
            # Mzuzu Direct Delivery
            if delivery_option == "Mzuzu Direct Delivery":
                st.markdown("**📍 Mzuzu Areas**")
                mzuzu_areas = [
                    "Town (City Centre)", "Luwinga", "Katawa", "Zolozolo", "Chibanja",
                    "Mchengautuwa", "Masasa", "Area 1B", "Area 1C", "McDonald's Area",
                    "Mzimba Street", "Chibavi"
                ]
                
                area = st.selectbox("Select Your Area", [""] + mzuzu_areas)
                if area:
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
            
            # Other District (Courier)
            elif delivery_option == "Other District (Courier)":
                st.markdown("**📦 Courier Delivery to Other Districts**")
                
                malawi_cities = [
                    "Lilongwe", "Blantyre", "Zomba", "Kasungu", "Dedza", "Balaka",
                    "Mangochi", "Ntcheu", "Mchinji", "Chiradzulu", "Thyolo", "Mulanje",
                    "Phalombe", "Chikwawa", "Nsanje", "Nkhotakota", "Rumphi", "Karonga", "Salima"
                ]
                
                city = st.selectbox("Select City", [""] + malawi_cities)
                courier = st.radio("Courier Service", ["CTS", "Speed Couriers"])
                
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
            
            # MZUNI Campus
            else:
                st.markdown("**🏫 MZUNI Campus Delivery**")
                
                mzuni_locations = [
                    "Male Singles Rooms", "Female Singles Rooms", "Chai Hostel",
                    "Norah Hostel", "Kandahar Hostel", "Village"
                ]
                
                location = st.selectbox("Select Location", [""] + mzuni_locations)
                
                if location == "Village":
                    house = st.text_input("House Number *")
                else:
                    room = st.text_input("Room/Block Number *")
                
                delivery_location = location
            
            st.subheader("Payment")
            payment = st.selectbox("Payment Method", ["Pay on Delivery", "Mobile Money", "Bank Transfer"])
            notes = st.text_area("Special Instructions (Optional)")
            
            total = RICE_PRICES[qty] + transport_cost
            st.markdown(f"""
            <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <b>Total: MWK {total:,}</b>
            </div>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("✅ Confirm Order", use_container_width=True)
            
            if submitted:
                if name and phone:
                    st.success("✅ Order placed successfully!")
                    st.balloons()
                    
                    # Clear preset delivery
                    if 'preset_delivery' in st.session_state:
                        del st.session_state['preset_delivery']
                else:
                    st.error("Please fill all required fields")

# ============================================
# TRACK ORDER PAGE
# ============================================
elif st.session_state.page == "🔍 Track":
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
elif st.session_state.page == "🔐 Login":
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
                    # Check if admin
                    if username == "admin":
                        st.session_state.is_admin = True
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
elif st.session_state.page == "📋 My Orders":
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
                        st.write(f"**Status:** {order['order_status']}")
                        st.write(f"**Tracking:** {order['tracking_number']}")
        else:
            st.info("No orders yet")

# ============================================
# PROFILE PAGE
# ============================================
elif st.session_state.page == "👤 Profile":
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
elif st.session_state.page == "ℹ️ About":
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
# ADMIN DASHBOARD - WITH SMS TEST BUTTON
# ============================================
elif st.session_state.page == "📊 Dashboard" and st.session_state.is_admin:
    st.title("📊 Admin Dashboard")
    
    # SMS Test Button - Add this at the top of admin dashboard
    st.subheader("📱 Test Notifications")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📱 Test SMS to My Phone", use_container_width=True):
            try:
                from twilio.rest import Client
                # Get credentials from secrets
                twilio_sid = st.secrets["twilio"]["account_sid"]
                twilio_token = st.secrets["twilio"]["auth_token"]
                twilio_phone = st.secrets["twilio"]["phone_number"]
                
                client = Client(twilio_sid, twilio_token)
                
                # Send to your number
                message = client.messages.create(
                    body="Test from Nicholas Rice System!",
                    from_=twilio_phone,
                    to="+265886867758"  # Your number with country code
                )
                st.success(f"✅ SMS sent! Message SID: {message.sid}")
                st.info("Check Twilio Console → Monitor → Message Logs to see status")
            except Exception as e:
                st.error(f"❌ SMS failed: {e}")
    
    with col2:
        if st.button("📧 Test Email", use_container_width=True):
            try:
                import smtplib
                email_sender = st.secrets["email"]["sender"]
                email_password = st.secrets["email"]["password"]
                
                msg = MIMEMultipart()
                msg['From'] = email_sender
                msg['To'] = email_sender
                msg['Subject'] = "Test from Nicholas Rice"
                
                msg.attach(MIMEText("This is a test email from your rice system!", 'plain'))
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email_sender, email_password)
                server.send_message(msg)
                server.quit()
                
                st.success("✅ Test email sent! Check your inbox.")
            except Exception as e:
                st.error(f"❌ Email failed: {e}")
    
    st.divider()
    
    # Get stats
    stats = db.get_dashboard_stats()
    
    # Stats cards
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
# LOGOUT
# ============================================
elif st.session_state.page == "🚪 Logout":
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.page = "🏠 Home"
    st.rerun()

# ============================================
# FOOTER (Always visible)
# ============================================
st.markdown("""
<div class="footer">
    🌾 Nicholas Rice | Quality from Karonga | 📞 0886 867 758
</div>
""", unsafe_allow_html=True)
