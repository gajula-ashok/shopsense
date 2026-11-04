import os
import random
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorStatus
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.warehouse import Warehouse
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.stock_movement import StockMovement
from app.models.interaction import ProductInteraction
from app.utils.security import hash_password

random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ----------------------------------------------------
# 1. CATEGORIES DEFINITIONS (Hierarchy)
# ----------------------------------------------------
CATEGORY_HIERARCHY = [
    # Top-Level Categories
    ("Electronics", None, "Consumer Electronics, Mobiles, Computing & Audio"),
    ("Fashion", None, "Men, Women, Apparel & Footwear"),
    ("Home & Kitchen", None, "Home Appliances, Furniture & Kitchen Essentials"),
    ("Beauty & Personal Care", None, "Skincare, Haircare, Cosmetics & Grooming"),
    ("Sports & Fitness", None, "Gym Gear, Sporting Goods, Fitness Trackers"),
    ("Books", None, "Academic, Fiction, Professional & Educational"),
    ("Grocery", None, "Daily Staples, Beverages, Organic Packaged Foods"),
    # Subcategories
    ("Mobiles", "Electronics", "Smartphones, Feature Phones, 5G Devices"),
    ("Laptops", "Electronics", "Ultrabooks, Gaming Laptops, Workstations"),
    ("Accessories", "Electronics", "Cables, Chargers, Power Banks, Audio Docks"),
    ("Men's Clothing", "Fashion", "Shirts, Jeans, Formal Suits, Ethnic Wear"),
    ("Women's Clothing", "Fashion", "Dresses, Kurtas, Sarees, Western Wear"),
    ("Footwear", "Fashion", "Sneakers, Formal Shoes, Sandals, Sports Shoes"),
    ("Home Appliances", "Home & Kitchen", "Refrigerators, Microwave Ovens, Air Purifiers"),
    ("Furniture", "Home & Kitchen", "Office Chairs, Study Tables, Recliners, Sofas"),
    ("Kitchen Products", "Home & Kitchen", "Cookware Sets, Blenders, Cutlery, Air Fryers")
]

# ----------------------------------------------------
# 2. WAREHOUSES DEFINITIONS (6 Hubs across India)
# ----------------------------------------------------
WAREHOUSES_DATA = [
    {"warehouse_name": "Central Distribution Hub (Delhi NCR)", "location": "Gurugram, Haryana", "capacity": 50000, "contact_phone": "+91 124 555 0101"},
    {"warehouse_name": "West Coast Logistics (Mumbai Mega-Hub)", "location": "Bhiwandi, Maharashtra", "capacity": 65000, "contact_phone": "+91 22 555 0102"},
    {"warehouse_name": "South Fulfillment Center (Bengaluru Tech-Park)", "location": "Whitefield, Bengaluru, Karnataka", "capacity": 55000, "contact_phone": "+91 80 555 0103"},
    {"warehouse_name": "East Coast Fulfillment (Kolkata Port)", "location": "Howrah, West Bengal", "capacity": 35000, "contact_phone": "+91 33 555 0104"},
    {"warehouse_name": "Central Logistics Hub (Hyderabad Deccan)", "location": "Shamshabad, Hyderabad, Telangana", "capacity": 45000, "contact_phone": "+91 40 555 0105"},
    {"warehouse_name": "North Logistics Center (Jaipur)", "location": "Jaipur, Rajasthan", "capacity": 30000, "contact_phone": "+91 141 555 0106"}
]

# ----------------------------------------------------
# 3. 50 REALISTIC INDIAN VENDORS DEFINITIONS
# ----------------------------------------------------
INDIAN_CITIES_STATES = [
    ("Mumbai", "Maharashtra", "400001"),
    ("Bengaluru", "Karnataka", "560001"),
    ("Delhi", "Delhi", "110001"),
    ("Hyderabad", "Telangana", "500001"),
    ("Chennai", "Tamil Nadu", "600001"),
    ("Ahmedabad", "Gujarat", "380001"),
    ("Pune", "Maharashtra", "411001"),
    ("Kolkata", "West Bengal", "700001"),
    ("Jaipur", "Rajasthan", "302001"),
    ("Surat", "Gujarat", "395001"),
    ("Lucknow", "Uttar Pradesh", "226001"),
    ("Chandigarh", "Punjab", "160001"),
    ("Indore", "Madhya Pradesh", "452001"),
    ("Kochi", "Kerala", "682001"),
    ("Coimbatore", "Tamil Nadu", "641001")
]

VENDOR_TEMPLATES = [
    ("Apex Tech India", "Rajesh Sharma", "Electronics", 12.0),
    ("Aura Ethnic Trends", "Pooja Verma", "Fashion", 10.0),
    ("Heritage Book House", "Manoj Kulkarni", "Books", 8.0),
    ("Urban Home Comforts", "Deepika Iyer", "Home & Kitchen", 11.0),
    ("AyurGlow Herbal Care", "Vikram Rathore", "Beauty & Personal Care", 14.0),
    ("Bharat Electronics Hub", "Amitabh Sen", "Electronics", 12.5),
    ("Vogue Weaves & Silks", "Ananya Deshmukh", "Fashion", 9.5),
    ("KitchenCraft Pro", "Sanjay Aggarwal", "Home & Kitchen", 10.5),
    ("FitNation Gear", "Karan Malhotra", "Sports & Fitness", 11.5),
    ("PureNature Organics", "Sunita Nair", "Grocery", 8.5),
    ("NextGen Gizmos", "Rohan Mehta", "Electronics", 12.0),
    ("Royal Stitch Menswear", "Harish Patel", "Fashion", 10.0),
    ("Pinnacle Gadgets", "Arun Varma", "Electronics", 12.5),
    ("Modern Living Furnishings", "Meenakshi Sundaram", "Home & Kitchen", 11.0),
    ("Glamour Touch Cosmetics", "Sneha Roy", "Beauty & Personal Care", 13.5),
    ("Elite Mobile Mart", "Nikhil Chopra", "Mobiles", 11.0),
    ("IndoFab Casuals", "Divya Pillai", "Men's Clothing", 9.0),
    ("Shree Krishna Traders", "Gopal Das", "Grocery", 7.5),
    ("ProActive Sports India", "Manpreet Singh", "Sports & Fitness", 10.0),
    ("Scholars Gateway Books", "Prof. R. C. Prasad", "Books", 8.0),
    ("Quantum Computech", "Siddharth Jain", "Laptops", 12.5),
    ("Zaveri Style Boutique", "Ritu Singhania", "Women's Clothing", 10.5),
    ("ComfortZone Mattresses", "Naveen Reddy", "Furniture", 11.0),
    ("EverFresh Pantry", "Kavita Hegde", "Grocery", 8.0),
    ("VelvetSkin Botanicals", "Dr. Shalini Gupta", "Beauty & Personal Care", 14.0),
    ("AudioVibe Acoustics", "Tarun Bhasin", "Accessories", 12.0),
    ("StepUp Footwear", "Aditya Mittal", "Footwear", 10.0),
    ("ChefElite Appliances", "Geeta Bhatt", "Kitchen Products", 10.5),
    ("ActiveLife Athleisure", "Varun Dhawan", "Sports & Fitness", 10.0),
    ("PrimePage Publishers", "Sudhir Bannerjee", "Books", 8.5),
    ("Titanium Techworks", "Ashish Joshi", "Electronics", 13.0),
    ("Kalamkari Handlooms", "Padma Rao", "Fashion", 9.5),
    ("CleanNest Solutions", "Kunal Kapoor", "Home Appliances", 11.0),
    ("HerbalRoots Ayurveda", "Vaidya Shrikant", "Beauty & Personal Care", 13.0),
    ("SpeedLink Peripherals", "Praveen Saxena", "Accessories", 11.5),
    ("UrbanDenim Co.", "Mohit Rawat", "Men's Clothing", 10.0),
    ("Gourmet Basket Foods", "Farhan Qureshi", "Grocery", 8.0),
    ("IronCore Fitness", "Gurpreet Singh", "Sports & Fitness", 11.0),
    ("Lumiere Decor & Lamps", "Bhavna Parekh", "Home & Kitchen", 10.5),
    ("Zenith Mobile Hub", "Sachin Patil", "Mobiles", 12.0),
    ("Elegance Sarees & Kurtis", "Swati Chawla", "Women's Clothing", 9.5),
    ("Apex Furniture Studio", "Dinesh Khatri", "Furniture", 11.5),
    ("GlowBio Skincare", "Tanvi Sengupta", "Beauty & Personal Care", 13.5),
    ("PowerTech Batteries", "Rameshwar Dayal", "Accessories", 11.0),
    ("TrendSetter Footwear", "Alok Pandey", "Footwear", 10.0),
    ("MasterChef Cookware", "Leela Krishnan", "Kitchen Products", 10.5),
    ("KnowledgeTree Library", "Devendra Shastri", "Books", 8.0),
    ("PulseTrack Wearables", "Gaurav Ahuja", "Electronics", 12.0),
    ("CozyNest Furnishings", "Bina Agarwal", "Home & Kitchen", 10.0),
    ("Omkar Spices & Staples", "Vallabhbhai Patel", "Grocery", 7.5)
]

def generate_and_seed_all():
    print("[START] [Step 1/8] Initializing database session & resetting database cleanly...")
    db: Session = SessionLocal()
    try:
        # 1. Clean drop and recreation
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS product_interactions, stock_movements, transactions, inventory, products, vendors, categories, warehouses, users CASCADE;"))
            conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE;"))
            conn.execute(text("DROP TYPE IF EXISTS vendorstatus CASCADE;"))
            conn.commit()

        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables created with correct schemas and foreign keys.")

        # ----------------------------------------------------
        # 2. SEED ADMIN & CUSTOMER USERS (At least 200 Customers)
        # ----------------------------------------------------
        print("[SEED] [Step 2/8] Creating Platform Admin and 200+ Customer Accounts...")
        admin_user = User(
            full_name="GAJULA ASHOK (Admin)",
            email="chiruashok12@gmail.com",
            password_hash=hash_password("ashok@123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)

        # Indian Names for Customers
        first_names = [
            "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
            "Shaurya", "Atharv", "Advik", "Pranav", "Advaith", "Aaryan", "Dhruv", "Kabir", "Ritvik", "Darsh",
            "Ananya", "Diya", "Saanvi", "Aadhya", "Pari", "Kiara", "Myra", "Riya", "Aarohi", "Anika",
            "Isha", "Kavya", "Navya", "Sneha", "Pooja", "Meera", "Tanvi", "Avani", "Shreya", "Aditi",
            "Rohan", "Rahul", "Sameer", "Karan", "Nikhil", "Siddharth", "Gaurav", "Manish", "Varun", "Abhishek"
        ]
        last_names = [
            "Sharma", "Verma", "Patel", "Reddy", "Rao", "Gupta", "Mehta", "Nair", "Joshi", "Kulkarni",
            "Iyer", "Chopra", "Malhotra", "Singh", "Kumar", "Mishra", "Deshmukh", "Bhat", "Pillai", "Das",
            "Chowdhury", "Sen", "Bose", "Saxena", "Agarwal", "Bansal", "Mittal", "Pandey", "Trivedi", "Shukla"
        ]

        customer_users = []
        # Pre-seed classic demo customer
        c_demo = User(
            full_name="Alice Johnson (Customer)",
            email="customer@shopsense.com",
            password_hash=hash_password("Customer@123"),
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db.add(c_demo)
        customer_users.append(c_demo)

        for i in range(2, 201):
            fn = first_names[(i - 1) % len(first_names)]
            ln = last_names[(i * 3) % len(last_names)]
            c_user = User(
                full_name=f"{fn} {ln}",
                email=f"{fn.lower()}.{ln.lower()}{i}@example.com",
                password_hash=hash_password("Customer@123"),
                role=UserRole.CUSTOMER,
                is_active=True
            )
            db.add(c_user)
            customer_users.append(c_user)

        db.commit()
        for cu in customer_users:
            db.refresh(cu)
        print(f"[OK] Created {len(customer_users)} customers + 1 Admin.")

        # ----------------------------------------------------
        # 3. SEED 6 WAREHOUSES & 16 CATEGORIES
        # ----------------------------------------------------
        print("[WH] [Step 3/8] Seeding 6 Warehouses and 16 Category Hierarchy nodes...")
        warehouses_created = []
        for wh_d in WAREHOUSES_DATA:
            wh = Warehouse(**wh_d)
            db.add(wh)
            warehouses_created.append(wh)
        db.commit()

        cat_lookup = {}
        for c_name, parent_name, c_desc in CATEGORY_HIERARCHY:
            p_id = cat_lookup.get(parent_name)
            cat = Category(category_name=c_name, parent_id=p_id, description=c_desc)
            db.add(cat)
            db.commit()
            db.refresh(cat)
            cat_lookup[c_name] = cat.category_id

        # ----------------------------------------------------
        # 4. SEED EXACTLY 50 VENDORS
        # ----------------------------------------------------
        print("[VENDOR] [Step 4/8] Seeding exactly 50 Vendors with Indian business profiles...")
        vendors_created = []
        vendor_users = []

        for idx, (b_name, owner, cat, comm) in enumerate(VENDOR_TEMPLATES, start=1):
            city, state, pin = INDIAN_CITIES_STATES[(idx - 1) % len(INDIAN_CITIES_STATES)]
            email = f"vendor{idx}@{b_name.lower().replace(' ', '').replace('&', '').replace('.', '')[:12]}.in"
            if idx == 1:
                email = "techworld@example.com"  # Keep demo vendor login active!
                owner = "John Doe (Vendor)"

            phone = f"+91 {random.randint(90000, 99999)} {random.randint(10000, 99999)}"
            # Vendor status: 45 Active, 3 Pending, 2 Suspended/Inactive
            if idx in [46, 47, 48]:
                v_stat = VendorStatus.PENDING
            elif idx in [49, 50]:
                v_stat = VendorStatus.SUSPENDED
            else:
                v_stat = VendorStatus.ACTIVE

            v_user = User(
                full_name=owner,
                email=email,
                password_hash=hash_password("Vendor@123"),
                role=UserRole.VENDOR,
                is_active=(v_stat != VendorStatus.SUSPENDED)
            )
            db.add(v_user)
            db.commit()
            db.refresh(v_user)

            vendor = Vendor(
                business_name=b_name,
                owner_name=owner,
                email=email,
                phone=phone,
                category=cat,
                commission_rate=Decimal(str(comm)),
                status=v_stat,
                user_id=v_user.user_id
            )
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
            vendors_created.append(vendor)

        print(f"[OK] Created {len(vendors_created)} vendors.")

        # ----------------------------------------------------
        # 5. SEED EXACTLY 500 PRODUCTS (10 Products per Vendor)
        # ----------------------------------------------------
        print("[PRODUCT] [Step 5/8] Seeding exactly 500 Products across 50 Vendors (10 products/vendor)...")
        # Realistic Indian Market Product Templates across Categories
        PRODUCT_GENERATORS = {
            "Electronics": [
                ("Noise-Cancelling Wireless Headphones Pro", 2499.00),
                ("Ultra-Slim RGB Mechanical Gaming Keyboard", 1899.00),
                ("High-Speed 65W GaN Fast Charger", 999.00),
                ("Smart Fitness Band with SpO2 Monitor", 1499.00),
                ("Portable Waterproof Bluetooth Speaker 20W", 1799.00),
                ("Heavy-Duty Braided Type-C to Lightning Cable", 399.00),
                ("Thunderbolt 4 Quad-Display USB-C Hub", 3499.00),
                ("Full HD 1080P Dual-Mic Streamer Webcam", 1599.00),
                ("Ergonomic Vertical Wireless Mouse", 849.00),
                ("Surge Protected 6-Way Extension Board", 699.00),
                ("Smart Home WiFi IR Blaster Hub", 799.00),
                ("True Wireless Stereo Earbuds with ANC", 1999.00)
            ],
            "Mobiles": [
                ("Neo 5G Smartphone (8GB/128GB AMOLED)", 18999.00),
                ("Prime Pro 5G Flagship (12GB/256GB)", 32999.00),
                ("Starlight Ultra Smartphone (6GB/128GB)", 13499.00),
                ("Shockproof Military-Grade Armor Case", 349.00),
                ("9H Tempered Glass Screen Protector 2-Pack", 199.00),
                ("Magnetic Wireless Car Phone Mount Charger", 1299.00),
                ("Ultra-Compact 10000mAh Power Bank 22.5W", 1199.00),
                ("Fast Wireless Charging Pad 15W", 899.00),
                ("OTG Dual USB 3.2 Flash Drive 128GB", 899.00),
                ("Selfie Stick Tripod with Bluetooth Shutter", 599.00)
            ],
            "Laptops": [
                ("UltraBook 14-inch Thin & Light Laptop Core i5", 54999.00),
                ("Gaming Beast 15.6-inch RTX 4050 16GB RAM", 74999.00),
                ("Student Study Laptop 15.6-inch Quad-Core", 28999.00),
                ("Water-Resistant Neoprene Laptop Sleeve", 499.00),
                ("Adjustable Aluminum Ergonomic Laptop Stand", 799.00),
                ("Silent Dual-Fan Cooling Pad for Laptops", 999.00),
                ("USB-C to HDMI 4K 60Hz Display Adapter", 699.00),
                ("Wireless Numeric Keypad for Accountants", 599.00),
                ("Anti-Glare Blue Light Filter Screen Protector", 449.00),
                ("Universal 100W Multi-Pin Laptop Adapter", 1899.00)
            ],
            "Fashion": [
                ("Pure Cotton Regular Fit Casual Shirt", 799.00),
                ("Slim-Fit Stretchable Denim Jeans", 1299.00),
                ("Classic Round Neck Graphic T-Shirt", 449.00),
                ("Floral Printed Anarkali Kurta Set", 1499.00),
                ("Banarasi Art Silk Festive Saree with Blouse", 2199.00),
                ("Waterproof Outdoor Hooded Windbreaker", 1899.00),
                ("Genuine Leather Casual Bifold Wallet", 499.00),
                ("Polarized UV400 Aviator Sunglasses", 699.00),
                ("Classic Stainless Steel Analog Watch", 1599.00),
                ("Canvas Casual Everyday Backpack", 899.00),
                ("Unisex Fleece Pullover Winter Hoodie", 1199.00),
                ("Pure Wool Thermal Innerwear Top & Bottom", 899.00)
            ],
            "Men's Clothing": [
                ("Men's Formal Oxford Cotton Shirt", 899.00),
                ("Men's Cotton Chino Trousers Khaki", 1199.00),
                ("Men's Casual Linen Blend Kurta", 799.00),
                ("Men's Athletic Quick-Dry Gym Trackpants", 649.00),
                ("Men's Cotton Boxer Shorts Pack of 3", 499.00),
                ("Men's Reversible Formal Faux-Leather Belt", 449.00),
                ("Men's Breathable Polo Collar T-Shirt", 599.00),
                ("Men's Cotton Cargo Joggers 6-Pockets", 1399.00),
                ("Men's Nehru Jacket Festive Waistcoat", 1299.00),
                ("Men's Sports Compression Active Tights", 599.00)
            ],
            "Women's Clothing": [
                ("Women's Straight Cotton Kurti Mustard Yellow", 699.00),
                ("Women's A-Line Western Midi Dress", 999.00),
                ("Women's High-Rise Denim Skinny Jeans", 1199.00),
                ("Women's Chanderi Silk Zari Border Saree", 1899.00),
                ("Women's Rayon Palazzo Pants Off-White", 499.00),
                ("Women's Seamless Padded Sports Bra", 449.00),
                ("Women's Woolen Cardigan Button-Down Sweater", 1099.00),
                ("Women's Chikankari Embroidered Tunic", 899.00),
                ("Women's Cotton Nightwear Top & Pyjama Set", 799.00),
                ("Women's Satin Formal Office Blouse", 649.00)
            ],
            "Footwear": [
                ("Air-Cushioned Lightweight Running Shoes", 1599.00),
                ("Men's Derby Lace-Up Formal Leather Shoes", 1899.00),
                ("Women's Pointed Block Heel Pumps", 1299.00),
                ("Unisex Eva Lightweight Slip-On Slides", 399.00),
                ("Breathable Mesh Walking Sports Sneakers", 999.00),
                ("Traditional Kolhapuri Handcrafted Chappals", 699.00),
                ("Waterproof Rubber Sole Trekking Boots", 2499.00),
                ("Women's Casual Canvas Slip-On Loafers", 799.00),
                ("Memory Foam Orthopedic Comfort Flip-Flops", 499.00),
                ("Kids Light-Up Active Sports Shoes", 799.00)
            ],
            "Home & Kitchen": [
                ("Ergonomic High-Back Mesh Desk Chair", 5999.00),
                ("Non-Stick Induction Granito Cookware 3-Piece", 1899.00),
                ("Stainless Steel Electric Kettle 1.8 Litre", 749.00),
                ("Ultrasonic Aromatherapy Essential Oil Diffuser", 899.00),
                ("Microfiber Soft Touch King Bedsheet with Pillows", 699.00),
                ("Heavy-Duty 750W Mixer Grinder 3 Jars", 2499.00),
                ("Cold Press Masticating Slow Juicer", 4999.00),
                ("Digital Air Fryer 4.5L with Rapid Heat", 3499.00),
                ("Memory Foam Cervical Orthopedic Bed Pillow", 799.00),
                ("Automatic Cordless Water Dispenser Pump", 349.00)
            ],
            "Home Appliances": [
                ("Energy-Saving BLDC Inverter Ceiling Fan with Remote", 2899.00),
                ("HEPA True Filter Room Air Purifier CADR 250", 6999.00),
                ("Compact 20L Solo Microwave Oven 800W", 4999.00),
                ("Dry Iron with Non-Stick American Teflon Soleplate", 599.00),
                ("Handheld Garment Steam Iron 1200W", 1499.00),
                ("High-Pressure Car Washer Spray Machine 1600W", 3999.00),
                ("Smart Wi-Fi Robot Vacuum Cleaner & Mop", 14999.00),
                ("Insect Mosquito Electronic Trapper Lamp", 499.00),
                ("Under-Sink Water Purifier RO+UV+TDS Mineral", 7999.00),
                ("Rechargeable Portable Handheld Desk Fan", 499.00)
            ],
            "Furniture": [
                ("Engineered Wood Multipurpose Study Computer Table", 3299.00),
                ("Solid Sheesham Wood 4-Seater Dining Table", 12999.00),
                ("Foldable Recliner Relaxation Balcony Chair", 2199.00),
                ("Multi-Tier Wooden Shoe Rack Cabinet with Seat", 1899.00),
                ("Modular 3-Door Wardrobe with Mirror White", 8999.00),
                ("Fabric Upholstered 2-Seater Living Room Sofa", 9999.00),
                ("Space-Saving Wall Mounted Drop-Leaf Table", 1299.00),
                ("Metal Frame Queen Bed with Headboard", 7499.00),
                ("Floating TV Entertainment Wall Unit", 2499.00),
                ("Stackable Plastic Armchairs Pack of 2", 1199.00)
            ],
            "Kitchen Products": [
                ("Tri-Ply Stainless Steel Pressure Cooker 3 Litre", 1799.00),
                ("Hard Anodized Roti Tawa 25cm Non-Toxic", 599.00),
                ("Multi-Purpose Vegetable Chopper & Slicer 900ml", 299.00),
                ("Borosilicate Glass Food Storage Containers Set of 3", 699.00),
                ("Silicone Heat-Resistant Spatula & Spoon Set", 349.00),
                ("Stainless Steel Insulated Water Bottle 1 Litre", 499.00),
                ("Knife Block Set High-Carbon Steel 6-Piece", 899.00),
                ("Rotary Dish Drying Rack with Drainer Tray", 699.00),
                ("Compact Sandwich & Panini Griller 750W", 999.00),
                ("Manual Citrus Juicer & Squeezer Heavy Metal", 399.00)
            ],
            "Beauty & Personal Care": [
                ("Vitamin C + Hyaluronic Acid Brightening Serum", 499.00),
                ("Organic Herbal Tea Tree Anti-Dandruff Shampoo", 349.00),
                ("SPF 50+ PA++++ Dewy Finish Matte Sunscreen Gel", 399.00),
                ("Deep Moisturizing Shea Butter Body Lotion 400ml", 299.00),
                ("Salicylic Acid 2% Gentle Foaming Face Wash", 299.00),
                ("Ayurvedic Bhringraj Herbal Hair Growth Oil 200ml", 399.00),
                ("Matte Waterproof Liquid Lipstick Long-Lasting", 349.00),
                ("Exfoliating Himalayan Coffee Walnut Body Scrub", 399.00),
                ("Professional Hair Straightener Brush 2-in-1", 999.00),
                ("Men's Beard Growth Oil & Softener Balm Combo", 449.00)
            ],
            "Sports & Fitness": [
                ("Eco-Friendly Non-Slip 6mm EVA Yoga Mat with Strap", 499.00),
                ("Adjustable Rubber Coated Dumbbell Set 10KG", 1299.00),
                ("Latex Resistance Loop Exercise Bands Set of 5", 349.00),
                ("High-Speed Ball Bearing Skipping Jump Rope", 249.00),
                ("Muscle Massage Roller Stick for Deep Tissue Relief", 399.00),
                ("Stainless Steel Gym Protein Shaker Bottle 700ml", 349.00),
                ("Wrist Support Weightlifting Padded Gym Gloves", 299.00),
                ("Heavy-Duty Pull-Up Doorway Exercise Bar", 1199.00),
                ("Professional Badminton Racket Carbon Fiber 2-Pack", 1499.00),
                ("Hydration Hydropack Backpack with 2L Bladder", 999.00)
            ],
            "Books": [
                ("Data Structures & Algorithms Made Easy in Python", 599.00),
                ("Modern Cloud Architecture with Microservices & Docker", 649.00),
                ("Atomic Habits for High-Performance Success", 449.00),
                ("The Psychology of Wealth & Financial Freedom", 399.00),
                ("Complete Guide to Machine Learning & Deep Learning", 799.00),
                ("Indian Polity & Governance for Competitive Exams", 499.00),
                ("FastAPI & React Microservices Engineering Blueprint", 699.00),
                ("Clean Code in Enterprise Systems (Indian Edition)", 549.00),
                ("Database Internals & Distributed Systems Design", 849.00),
                ("Ancient Indian Heritage & Architectural Wonders", 499.00)
            ],
            "Grocery": [
                ("Cold-Pressed Virgin Mustard Oil Kachi Ghani 1L", 189.00),
                ("Organic Raw Wild Forest Honey 500g", 349.00),
                ("Premium California Almonds 500g Pouch", 499.00),
                ("Aromatic Royal Basmati Rice aged 2 Years 5KG", 599.00),
                ("Assam Long-Leaf CTC Premium Black Tea 1KG", 389.00),
                ("Organic Unpolished Toor Dal Arhar 1KG", 169.00),
                ("Roasted Salted Cashew Nuts 250g", 299.00),
                ("Ground Roasted South Indian Filter Coffee 200g", 199.00),
                ("Pure Desi Gir Cow A2 Ghee 500ml", 749.00),
                ("Crunchy Dark Chocolate Peanut Butter 1KG", 399.00)
            ]
        }

        products_created = []
        inventory_records = []
        product_counter = 1

        wh_names = [w["warehouse_name"] for w in WAREHOUSES_DATA]

        # Distribute EXACTLY 10 products to each of the 50 vendors = 500 products
        for v_idx, vendor in enumerate(vendors_created, start=1):
            v_cat = vendor.category
            # Pick from matched category pool or fallback to related
            pool = PRODUCT_GENERATORS.get(v_cat, PRODUCT_GENERATORS["Electronics"])
            if len(pool) < 10:
                pool = pool + PRODUCT_GENERATORS["Accessories"]

            # Ensure 10 unique product variations for this vendor
            for p_num in range(1, 11):
                base_name, base_price = pool[(p_num - 1) % len(pool)]
                p_name = f"{base_name} ({vendor.business_name.split()[0]} Edition)" if p_num > 1 else base_name
                # Slightly vary price and stock for realism
                price_val = round(Decimal(str(base_price)) * Decimal(str(random.uniform(0.92, 1.15))), 2)

                # Varied stock conditions:
                # ~15% Out of stock (0)
                # ~25% Low stock (1..reorder)
                # ~50% Available healthy stock (reorder+1..80)
                # ~10% Overstocked (81..150)
                rand_stk_type = random.random()
                reorder_lvl = random.choice([8, 10, 12, 15, 20])

                if rand_stk_type < 0.12:
                    stk = 0
                elif rand_stk_type < 0.35:
                    stk = random.randint(1, reorder_lvl)
                elif rand_stk_type < 0.88:
                    stk = random.randint(reorder_lvl + 5, 75)
                else:
                    stk = random.randint(80, 140)

                assigned_wh = wh_names[(product_counter + v_idx) % len(wh_names)]

                prod = Product(
                    product_name=p_name,
                    category=v_cat,
                    price=price_val,
                    stock=stk,
                    vendor_id=vendor.vendor_id
                )
                db.add(prod)
                db.commit()
                db.refresh(prod)
                products_created.append(prod)

                inv = Inventory(
                    product_id=prod.product_id,
                    current_stock=stk,
                    reorder_level=reorder_lvl,
                    warehouse=assigned_wh
                )
                db.add(inv)
                inventory_records.append(inv)
                product_counter += 1

        db.commit()
        print(f"[OK] Created {len(products_created)} products & {len(inventory_records)} inventory tracking records.")

        # ----------------------------------------------------
        # 6. SEED AT LEAST 5,000 HISTORICAL TRANSACTIONS (12 Months)
        # ----------------------------------------------------
        print("[TX] [Step 6/8] Generating 5,200+ historical transactions spanning 12 months with seasonal and festival patterns...")
        start_date = datetime(2025, 11, 1)
        end_date = datetime(2026, 10, 28)
        total_days = (end_date - start_date).days

        transactions_data = []
        sales_history_data = []

        # Customer buying personas for segmentation & clustering
        # 1..30: High Value Customers (frequent purchases, higher baskets)
        # 31..120: Regular Customers (steady recurring purchases)
        # 121..165: Occasional Customers (festival / promotion buyers)
        # 166..200: Low Activity Customers (1-2 single item orders)
        tx_count = 0

        for c_idx, cust in enumerate(customer_users, start=1):
            if c_idx <= 30:
                orders_count = random.randint(35, 60)
                qty_pool = (2, 5)
            elif c_idx <= 120:
                orders_count = random.randint(18, 30)
                qty_pool = (1, 3)
            elif c_idx <= 165:
                orders_count = random.randint(8, 15)
                qty_pool = (1, 2)
            else:
                orders_count = random.randint(2, 6)
                qty_pool = (1, 2)

            chosen_days = sorted(random.choices(range(total_days), k=orders_count))
            for d in chosen_days:
                tx_dt = start_date + timedelta(
                    days=d,
                    hours=random.randint(9, 22),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )

                # Festival boost around Diwali (Oct/Nov), New Year (Jan), Independence Day (Aug)
                month = tx_dt.month
                is_festive = month in [10, 11, 12, 1]

                chosen_prod = random.choice(products_created)
                qty = random.randint(*qty_pool)
                if is_festive and random.random() < 0.35:
                    qty += 1

                unit_price = float(chosen_prod.price)
                tot_amount = round(unit_price * qty, 2)

                tx = Transaction(
                    product_id=chosen_prod.product_id,
                    vendor_id=chosen_prod.vendor_id,
                    user_id=cust.user_id,
                    quantity=qty,
                    amount=Decimal(str(tot_amount)),
                    transaction_date=tx_dt
                )
                db.add(tx)
                tx_count += 1

                transactions_data.append({
                    "transaction_id": tx_count,
                    "customer_id": cust.user_id,
                    "product_id": chosen_prod.product_id,
                    "vendor_id": chosen_prod.vendor_id,
                    "quantity": qty,
                    "amount": tot_amount,
                    "transaction_date": tx_dt.strftime("%Y-%m-%d %H:%M:%S")
                })

                sales_history_data.append({
                    "date": tx_dt.strftime("%Y-%m-%d"),
                    "product_id": chosen_prod.product_id,
                    "product_name": chosen_prod.product_name,
                    "category": chosen_prod.category,
                    "quantity_sold": qty,
                    "revenue": tot_amount
                })

                if tx_count % 1000 == 0:
                    db.commit()
                    print(f"  ... inserted {tx_count} transactions")

        db.commit()
        print(f"[OK] Created {tx_count} transactions recorded in database.")

        # ----------------------------------------------------
        # 7. SEED AT LEAST 2,000 STOCK MOVEMENTS
        # ----------------------------------------------------
        print("[PRODUCT] [Step 7/8] Recording 2,200+ Stock Movement records (Stock In, Stock Out, Adjustments)...")
        movement_types = ["STOCK_IN", "STOCK_OUT", "SALE", "ADJUSTMENT", "RETURN", "RESTOCK"]
        movements_created = []

        for m_idx in range(1, 2201):
            prod = random.choice(products_created)
            m_type = random.choice(movement_types)
            if m_type in ["STOCK_IN", "RESTOCK", "RETURN"]:
                qty = random.randint(5, 50)
            elif m_type in ["STOCK_OUT", "SALE"]:
                qty = -random.randint(1, 15)
            else:
                qty = random.choice([-5, -2, 2, 5, 10])

            m_dt = start_date + timedelta(days=random.randint(0, total_days))
            wh = random.choice(wh_names)

            sm = StockMovement(
                product_id=prod.product_id,
                quantity=qty,
                movement_type=m_type,
                reference=f"REF-MOV-{m_idx:05d}",
                warehouse=wh,
                created_at=m_dt
            )
            db.add(sm)
            movements_created.append(sm)

            if m_idx % 500 == 0:
                db.commit()

        db.commit()
        print(f"[OK] Created {len(movements_created)} stock movements.")

        # ----------------------------------------------------
        # 8. SEED AT LEAST 3,000 PRODUCT INTERACTIONS (Collaborative Filtering)
        # ----------------------------------------------------
        print("[RATING] [Step 8/8] Generating 3,500+ Customer-Product Ratings & Interactions for Collaborative Filtering...")
        interaction_types = ["RATING", "PURCHASE", "WISHLIST", "VIEW"]
        added_interactions = set()
        interactions_count = 0

        # Cluster tastes:
        # Tech Enthusiasts (Mobiles, Electronics, Laptops): Customers 1..70
        # Fashion & Beauty Lovers: Customers 71..140
        # Home & Kitchen & Grocery Lovers: Customers 141..200
        for cust in customer_users:
            cid = cust.user_id
            if cid <= 70:
                affinity_cats = ["Electronics", "Mobiles", "Laptops", "Accessories"]
            elif cid <= 140:
                affinity_cats = ["Fashion", "Men's Clothing", "Women's Clothing", "Footwear", "Beauty & Personal Care"]
            else:
                affinity_cats = ["Home & Kitchen", "Home Appliances", "Furniture", "Kitchen Products", "Grocery"]

            # Interaction items
            affinity_prods = [p for p in products_created if p.category in affinity_cats]
            other_prods = [p for p in products_created if p.category not in affinity_cats]

            num_interactions = random.randint(16, 25)
            for _ in range(num_interactions):
                if random.random() < 0.78 and affinity_prods:
                    chosen_p = random.choice(affinity_prods)
                    score = round(random.uniform(3.5, 5.0), 1)
                else:
                    chosen_p = random.choice(other_prods)
                    score = round(random.uniform(1.5, 3.5), 1)

                key = (cid, chosen_p.product_id, "RATING")
                if key not in added_interactions:
                    added_interactions.add(key)
                    pi = ProductInteraction(
                        user_id=cid,
                        product_id=chosen_p.product_id,
                        interaction_score=score,
                        interaction_type="RATING"
                    )
                    db.add(pi)
                    interactions_count += 1

        db.commit()
        print(f"[OK] Created {interactions_count} customer-product interactions.")

        # ----------------------------------------------------
        # EXPORT DATASETS TO CSV (data/ folder)
        # ----------------------------------------------------
        print("[FILE] Exporting clean CSV datasets into data/ directory...")
        # 1. products.csv
        pd.DataFrame([{
            "product_id": p.product_id,
            "product_name": p.product_name,
            "category": p.category,
            "price": float(p.price),
            "vendor_id": p.vendor_id,
            "stock": p.stock,
            "sku": f"SKU-{p.category[:3].upper()}-{p.product_id:04d}",
            "created_at": p.created_at
        } for p in products_created]).to_csv(os.path.join(DATA_DIR, "products.csv"), index=False)

        # 2. vendors.csv
        pd.DataFrame([{
            "vendor_id": v.vendor_id,
            "business_name": v.business_name,
            "owner_name": v.owner_name,
            "email": v.email,
            "phone": v.phone,
            "category": v.category,
            "commission_rate": float(v.commission_rate),
            "status": v.status.value,
            "created_at": v.created_at
        } for v in vendors_created]).to_csv(os.path.join(DATA_DIR, "vendors.csv"), index=False)

        # 3. customers.csv
        pd.DataFrame([{
            "customer_id": c.user_id,
            "customer_name": c.full_name,
            "email": c.email,
            "is_active": c.is_active,
            "created_at": c.created_at
        } for c in customer_users]).to_csv(os.path.join(DATA_DIR, "customers.csv"), index=False)

        # 4. warehouses.csv
        pd.DataFrame(WAREHOUSES_DATA).to_csv(os.path.join(DATA_DIR, "warehouses.csv"), index=False)

        # 5. inventory.csv
        pd.DataFrame([{
            "inventory_id": inv.inventory_id,
            "product_id": inv.product_id,
            "current_stock": inv.current_stock,
            "reorder_level": inv.reorder_level,
            "warehouse": inv.warehouse,
            "status": inv.status,
            "updated_at": inv.updated_at
        } for inv in inventory_records]).to_csv(os.path.join(DATA_DIR, "inventory.csv"), index=False)

        # 6. transactions.csv
        pd.DataFrame(transactions_data).to_csv(os.path.join(DATA_DIR, "transactions.csv"), index=False)

        # 7. sales_history.csv
        pd.DataFrame(sales_history_data).to_csv(os.path.join(DATA_DIR, "sales_history.csv"), index=False)

        # 8. interactions.csv
        pd.DataFrame([{
            "customer_id": k[0],
            "product_id": k[1],
            "interaction_type": k[2],
            "interaction_score": pi.interaction_score
        } for k, pi in zip(added_interactions, db.query(ProductInteraction).all())]).to_csv(os.path.join(DATA_DIR, "interactions.csv"), index=False)

        print("[SUCCESS] ALL DATA SEEDING & CSV GENERATION COMPLETED SUCCESSFULLY!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error during seed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    generate_and_seed_all()
