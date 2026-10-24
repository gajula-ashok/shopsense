import random
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorStatus
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.transaction import Transaction
from app.utils.security import hash_password

def run_clean_setup():
    # 1. Force drop everything with a completely clean connection slate
    print("🧹 Dropping any conflicting stale tables with CASCADE...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS transactions, inventory, products, vendors, users CASCADE;"))
        conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE;"))
        conn.execute(text("DROP TYPE IF EXISTS vendorstatus CASCADE;"))
        conn.commit()
    
    # 2. Re-create fresh schemas from model definitions
    print("🏗️ Creating fresh database tables with correct columns...")
    Base.metadata.create_all(bind=engine)
    
    # 3. Seed data
    db: Session = SessionLocal()
    try:
        print("🌱 Seeding accounts and profile variables...")
        # 3a. Platform Admin - Sreya Bondili
        admin_user = User(
            full_name="GAJULA ASHOK (Admin)",
            email="chiruashok12@gmail.com",
            password_hash=hash_password("ashok@123"),
            role=UserRole.ADMIN,
            is_active=True
            )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)


        # 3b. Customer Users
        customers_data = [
            ("Alice Johnson (Customer)", "customer@shopsense.com"),
            ("Rahul Verma", "rahul.verma@example.com"),
            ("Priya Patel", "priya.patel@example.com"),
            ("Carlos Mendez", "carlos.m@example.com"),
            ("Ananya Rao", "ananya.rao@example.com"),
        ]
        customer_users = []
        for name, email in customers_data:
            cust = User(
                full_name=name,
                email=email,
                password_hash=hash_password("Customer@123"),
                role=UserRole.CUSTOMER,
                is_active=True
            )
            db.add(cust)
            db.commit()
            db.refresh(cust)
            customer_users.append(cust)

        # 3c. Vendor Accounts
        vendor_profiles_data = [
            ("Apex Electronics", "techworld@example.com", "John Doe", "Electronics", "9876543210", Decimal("12.50"), VendorStatus.ACTIVE),
            ("Aura Fashion Hub", "trendsfashion@example.com", "Sarah Miller", "Fashion", "9876543211", Decimal("10.00"), VendorStatus.ACTIVE),
            ("Book Haven Store", "bookoasis@example.com", "Robert Clark", "Books", "9876543212", Decimal("8.50"), VendorStatus.ACTIVE),
            ("Urban Home Comforts", "homecomforts@example.com", "Emma Watson", "Home & Kitchen", "9876543213", Decimal("11.00"), VendorStatus.ACTIVE),
            ("Glow Cosmetics & Spa", "glowbeauty@example.com", "Priya Sharma", "Beauty & Personal Care", "9876543214", Decimal("14.00"), VendorStatus.ACTIVE),
            ("Nexus Smart Tech", "nexustech@example.com", "David Chen", "Electronics", "9876543215", Decimal("12.00"), VendorStatus.ACTIVE),
            ("Urban Stitch Apparel", "urbanstitch@example.com", "Liam Brown", "Fashion", "9876543216", Decimal("9.50"), VendorStatus.ACTIVE),
            ("Nordic Living Essentials", "nordicliving@example.com", "Olivia Davis", "Home & Kitchen", "9876543217", Decimal("10.50"), VendorStatus.ACTIVE),
            ("PureBotanica Organics", "purebotanica@example.com", "Sophia Taylor", "Beauty & Personal Care", "9876543218", Decimal("13.00"), VendorStatus.PENDING),
            ("Horizon Academic Press", "horizonpress@example.com", "James Wilson", "Books", "9876543219", Decimal("8.00"), VendorStatus.SUSPENDED),
        ]

        vendors = []
        for b_name, email, owner, cat, phone, comm, v_status in vendor_profiles_data:
            v_user = User(
                full_name=owner,
                email=email,
                password_hash=hash_password("Vendor@123"),
                role=UserRole.VENDOR,
                is_active=(v_status != VendorStatus.SUSPENDED)
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
                commission_rate=comm,
                status=v_status,
                user_id=v_user.user_id
            )
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
            vendors.append(vendor)

        print(f"Created {len(vendors)} vendors with associated user accounts.")

        # 3d. Seed Products
        print("Seeding catalog products...")
        products_catalog = [
            ("Noise-Cancelling Wireless Headphones Pro", "Electronics", Decimal("149.99"), 45, 12, 0, "Central Distribution Hub"),
            ("Ultra-Slim RGB Mechanical Keyboard", "Electronics", Decimal("89.50"), 35, 10, 0, "Central Distribution Hub"),
            ("Smartwatch Series 7 Titanium", "Electronics", Decimal("249.00"), 28, 8, 0, "West Coast Logistics"),
            ("Thunderbolt 4 High-Speed USB Dock", "Electronics", Decimal("119.00"), 18, 5, 0, "Central Distribution Hub"),
            ("Organic Cotton Classic Graphic Tee", "Fashion", Decimal("29.99"), 85, 20, 1, "East Coast Fulfillment"),
            ("Classic Slim-Fit Stretch Denim Jeans", "Fashion", Decimal("59.95"), 55, 15, 1, "East Coast Fulfillment"),
            ("Lightweight Waterproof All-Weather Windbreaker", "Fashion", Decimal("89.00"), 38, 10, 1, "Central Distribution Hub"),
            ("Merino Wool Thermal Crewneck Sweater", "Fashion", Decimal("69.50"), 25, 8, 1, "East Coast Fulfillment"),
            ("Data Science & AI Engineering Handbook", "Books", Decimal("49.99"), 65, 15, 2, "Central Distribution Hub"),
            ("Modern Web Architecture with FastAPI & React", "Books", Decimal("39.99"), 45, 10, 2, "Central Distribution Hub"),
            ("The Art of Scalable Cloud Computing", "Books", Decimal("54.50"), 32, 8, 2, "Southern Logistics Center"),
            ("Deep Learning Illustrated (Hardcover Edition)", "Books", Decimal("59.00"), 22, 6, 2, "Central Distribution Hub"),
            ("Ergonomic Lumbar Support Mesh Office Chair", "Home & Kitchen", Decimal("199.99"), 22, 5, 3, "West Coast Logistics"),
            ("Cold Brew Precision Espresso Coffee Maker", "Home & Kitchen", Decimal("74.99"), 30, 8, 3, "Central Distribution Hub"),
            ("Ultrasonic Aroma Diffuser with Ambient LED", "Home & Kitchen", Decimal("34.50"), 6, 10, 3, "Central Distribution Hub"),
            ("Non-Stick Ceramic Cookware 10-Piece Set", "Home & Kitchen", Decimal("129.00"), 15, 5, 3, "Southern Logistics Center"),
            ("Hydrating Vitamin C + Hyaluronic Facial Serum", "Beauty & Personal Care", Decimal("32.00"), 60, 15, 4, "East Coast Fulfillment"),
            ("Organic Herbal Daily Moisturizing Cream", "Beauty & Personal Care", Decimal("26.50"), 42, 10, 4, "East Coast Fulfillment"),
            ("Exfoliating Mineral Himalayan Body Scrub", "Beauty & Personal Care", Decimal("21.99"), 0, 10, 4, "Central Distribution Hub"),
            ("Nourishing Botanical Night Repair Elixir", "Beauty & Personal Care", Decimal("38.00"), 25, 8, 4, "East Coast Fulfillment"),
            ("4K Ultra HD Dual-Monitor Webcam 60FPS", "Electronics", Decimal("119.99"), 20, 5, 5, "West Coast Logistics")
        ]

        for p_name, cat, price, stock, reorder, v_idx, warehouse in products_catalog:
            associated_vendor = vendors[v_idx]
            product = Product(product_name=p_name, category=cat, price=price, vendor_id=associated_vendor.vendor_id)
            db.add(product)
            db.commit()
            db.refresh(product)

            # 🛠️ Updated keys: quantity -> current_stock, warehouse_location -> warehouse
            inventory = Inventory(
                product_id=product.product_id, 
                current_stock=stock, 
                reorder_level=reorder, 
                warehouse=warehouse
            )
            db.add(inventory)
            db.commit()

        print("🚀 ShopSense database setup completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during execution: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_clean_setup()
