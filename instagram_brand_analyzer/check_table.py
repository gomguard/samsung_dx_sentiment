import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config.db_manager import InstagramDBManager

db = InstagramDBManager()
if db.connect():
    # Check table structure
    db.cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'instagram_keywords'
        ORDER BY ordinal_position
    """)

    print("\ninstagram_keywords table structure:")
    print("="*60)
    for row in db.cursor.fetchall():
        print(f"{row[0]:<30} {row[1]}")

    # Check data
    db.cursor.execute("SELECT * FROM instagram_keywords LIMIT 5")
    columns = [desc[0] for desc in db.cursor.description]
    print(f"\nColumns: {len(columns)}")
    print(f"Column names: {columns}")

    db.disconnect()
