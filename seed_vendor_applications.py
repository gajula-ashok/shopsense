import sys
import random
sys.path.insert(0, r"c:\Users\chiru\OneDrive\Desktop\ShopSense")
from app.database import SessionLocal
from app.models.vendor import Vendor, VendorStatus

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

db = SessionLocal()
vendors = db.query(Vendor).order_by(Vendor.vendor_id.asc()).all()

# Status distribution:
# 42 APPROVED (Active vendors)
# 4 PENDING (Applications waiting for admin review: vendors 45, 46, 47, 48)
# 2 MORE_INFO_NEEDED (e.g. vendors 43, 44)
# 2 REJECTED (e.g. vendors 49, 50)

for idx, v in enumerate(vendors, start=1):
    city, state, pin = INDIAN_CITIES_STATES[(idx - 1) % len(INDIAN_CITIES_STATES)]
    v.city = city
    v.state = state
    v.pincode = pin
    v.business_address = f"Plot #{idx * 4}, Industrial Area Phase {idx % 3 + 1}, {city}"
    v.tax_id = f"GSTIN{idx:02d}AAACB{1000 + idx}C1Z{idx % 9 + 1}"

    if idx in [45, 46, 47, 48]:
        v.application_status = "PENDING"
        v.status = VendorStatus.PENDING
        v.review_notes = "Application submitted with GST certificate and sample catalog. Awaiting administrator review."
    elif idx in [43, 44]:
        v.application_status = "MORE_INFO_NEEDED"
        v.status = VendorStatus.PENDING
        v.review_notes = "Administrator request: Please provide an updated warehouse address proof and valid FSSAI/Trade License."
    elif idx in [49, 50]:
        v.application_status = "REJECTED"
        v.status = VendorStatus.SUSPENDED
        v.review_notes = "Rejected: Incomplete business registration documentation and unverified contact number."
    else:
        v.application_status = "APPROVED"
        v.status = VendorStatus.ACTIVE
        v.review_notes = "Application verified and approved. Active marketplace seller."

db.commit()

# Print summary
from sqlalchemy import text
res = db.execute(text("SELECT application_status, count(*) FROM vendors GROUP BY application_status;")).fetchall()
print("Vendor Application Status Summary:")
for r in res:
    print(f"  {r[0]}: {r[1]}")
db.close()
