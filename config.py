"""
Configuration file for Nicholas Rice Ordering System
Author: Nicholas Mwangomba
Location: Mzuzu, Malawi
Supplier: Karonga (Quality Rice)
"""

import os

# Application metadata
APP_NAME = "Nicholas Rice Seller"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Nicholas Mwangomba"
APP_LOCATION = "Mzuzu, Malawi"
APP_SUPPLIER = "Karonga (Quality Rice)"

# Database settings
DATABASE_PATH = "data/rice_shop.db"

# Product prices (MWK) - Quality rice from Karonga
RICE_PRICES = {
    1: 4000,    # 1kg
    5: 20000,   # 5kg
    10: 40000,  # 10kg
    20: 80000   # 20kg
}

# Product description
PRODUCT_DESCRIPTION = "🌾 Quality rice from Karonga - Fresh, aromatic, and premium grade"

# Your location (where you deliver from)
YOUR_LOCATION = "Mzuzu"
YOUR_PHONE = "0886867758"
YOUR_EMAIL = "mwangombanicholas@gmail.com"

# Delivery options
CAMPUS_LOCATIONS = [
    "Male Singles Rooms",
    "Female Singles Rooms", 
    "Chai Hostel",
    "Norah Hostel",
    "Kandahar Hostel",
    "Village"
]

# Mzuzu areas for direct delivery (customer pays transport)
MZUZU_AREAS = [
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
    "Chibavi",
    "Other (specify in notes)"
]

# Transport cost within Mzuzu (paid by customer)
MZUZU_TRANSPORT_COST = {
    "Town (City Centre)": 2000,
    "Luwinga": 2500,
    "Katawa": 3000,
    "Zolozolo": 2500,
    "Chibanja": 3000,
    "Mchengautuwa": 3500,
    "Masasa": 2000,
    "Area 1B": 2000,
    "Area 1C": 2000,
    "McDonald's Area": 2500,
    "Mzimba Street": 2500,
    "Chibavi": 3000,
    "Other": 3500
}

# CTS Courier branches (for other districts)
CTS_BRANCHES = {
    'Lilongwe': ['Gravity Mall', 'Chitipi', 'Bunda', 'Area 23', 'Area 49'],
    'Blantyre': ['Ginnery Corner', 'Ndirande', 'Lunzu', 'Green Corner', 'Limbe', 'Bangwe'],
    'Zomba': ['3 Miles', 'Matawale', 'Chikanda'],
    'Kasungu': ['Main Branch'],
    'Dedza': ['Main Branch'],
    'Balaka': ['Main Branch'],
    'Mangochi': ['Main Branch'],
    'Ntcheu': ['Main Branch'],
    'Mchinji': ['Main Branch'],
    'Chiradzulu': ['Main Branch'],
    'Thyolo': ['Main Branch'],
    'Mulanje': ['Main Branch'],
    'Phalombe': ['Main Branch'],
    'Chikwawa': ['Main Branch'],
    'Nsanje': ['Main Branch'],
    'Nkhotakota': ['Main Branch'],
    'Rumphi': ['Main Branch'],
    'Karonga': ['Main Branch'],  # Your supplier location
    'Salima': ['Main Branch']
}

# Speed Courier cities (for other districts)
SPEED_CITIES = [
    'Lilongwe', 'Blantyre', 'Zomba', 'Kasungu', 
    'Dedza', 'Balaka', 'Mangochi', 'Ntcheu',
    'Mchinji', 'Chiradzulu', 'Thyolo', 'Mulanje',
    'Phalombe', 'Chikwawa', 'Nsanje', 'Nkhotakota',
    'Rumphi', 'Karonga', 'Salima'
]

# Courier fees (for other districts - customer pays at collection)
COURIER_FEE = 0  # We don't charge, customer pays courier directly

# Loyalty points settings
POINTS_PER_100_MWK = 1
POINTS_PER_REFERRAL = 100

# Contact information
ADMIN_EMAIL = "mwangombanicholas@gmail.com"
ADMIN_PHONE = "0886867758"
WHATSAPP_NUMBER = "265886867758"

# Session settings
SESSION_TIMEOUT = 3600

# Security
PASSWORD_MIN_LENGTH = 6

print("✅ Configuration file created successfully!")
print(f"📍 Location: {YOUR_LOCATION}")
print(f"🌾 Supplier: {APP_SUPPLIER}")
