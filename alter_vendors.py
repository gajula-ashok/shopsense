import sys
sys.path.insert(0, r"c:\Users\chiru\OneDrive\Desktop\ShopSense")
from app.database import engine
from sqlalchemy import text

sql = """
ALTER TABLE vendors 
ADD COLUMN IF NOT EXISTS business_address VARCHAR(255),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS state VARCHAR(100),
ADD COLUMN IF NOT EXISTS pincode VARCHAR(20),
ADD COLUMN IF NOT EXISTS tax_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS review_notes TEXT,
ADD COLUMN IF NOT EXISTS application_status VARCHAR(50) DEFAULT 'APPROVED';
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()
    print("Columns added successfully!")
