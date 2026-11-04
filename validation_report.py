import sys
sys.path.insert(0, r"c:\Users\chiru\OneDrive\Desktop\ShopSense")
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("==================================================")
    print("       SHOPSENSE DATABASE VALIDATION REPORT       ")
    print("==================================================")
    vendors = conn.execute(text("SELECT count(*) FROM vendors;")).scalar()
    products = conn.execute(text("SELECT count(*) FROM products;")).scalar()
    customers = conn.execute(text("SELECT count(*) FROM users WHERE role = 'CUSTOMER';")).scalar()
    total_users = conn.execute(text("SELECT count(*) FROM users;")).scalar()
    warehouses = conn.execute(text("SELECT count(*) FROM warehouses;")).scalar()
    categories = conn.execute(text("SELECT count(*) FROM categories;")).scalar()
    inventory = conn.execute(text("SELECT count(*) FROM inventory;")).scalar()
    transactions = conn.execute(text("SELECT count(*) FROM transactions;")).scalar()
    movements = conn.execute(text("SELECT count(*) FROM stock_movements;")).scalar()
    interactions = conn.execute(text("SELECT count(*) FROM product_interactions;")).scalar()

    print(f"Vendors Count                 : {vendors}")
    print(f"Products Count                : {products}")
    print(f"Customers Count (Role=CUSTOMER: {customers}")
    print(f"Total Users Count             : {total_users}")
    print(f"Warehouses Count              : {warehouses}")
    print(f"Product Categories Count      : {categories}")
    print(f"Inventory Records Count       : {inventory}")
    print(f"Historical Transactions Count : {transactions}")
    print(f"Stock Movement Records Count  : {movements}")
    print(f"Product Interactions Count    : {interactions}")
    print("--------------------------------------------------")
    res = conn.execute(text("SELECT vendor_id, count(*) FROM products GROUP BY vendor_id ORDER BY vendor_id;")).fetchall()
    counts = [r[1] for r in res]
    print(f"Total Vendors with Products   : {len(res)}")
    print(f"Min Products Per Vendor       : {min(counts)}")
    print(f"Max Products Per Vendor       : {max(counts)}")
    print(f"Unique Distribution Set       : {set(counts)} products per vendor")
    print("==================================================")
