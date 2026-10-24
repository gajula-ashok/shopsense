from sqlalchemy import text
from app.database import engine

def show_all_seeded_data():
    print("📋 Fetching active records from your PostgreSQL database...\n")
    
    tables = ["users", "vendors", "products", "inventory"]
    
    # Using your application's native PostgreSQL SQLAlchemy engine configuration
    with engine.connect() as conn:
        for table in tables:
            print(f"--- 🗄️ Table: {table.upper()} ---")
            try:
                # Query table rows dynamically
                result = conn.execute(text(f"SELECT * FROM {table} LIMIT 5;"))
                columns = result.keys()
                rows = result.fetchall()
                
                if not rows:
                    print("  (Empty table)\n")
                    continue
                    
                # Print column headers
                print(f" 🟢 Columns: {', '.join(columns)}")
                
                # Print rows
                for row in rows:
                    print(f"  👉 {dict(zip(columns, row))}")
                print()
                
            except Exception as e:
                print(f" ❌ Could not read table '{table}': {e}\n")

if __name__ == "__main__":
    show_all_seeded_data()
