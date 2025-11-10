"""
Remove region_code column from instagram_keywords table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config.db_manager import InstagramDBManager

db = InstagramDBManager()
if db.connect():
    try:
        print("Removing region_code column from instagram_keywords table...")
        db.cursor.execute("ALTER TABLE instagram_keywords DROP COLUMN IF EXISTS region_code")
        db.conn.commit()
        print("[OK] Column removed successfully")

        # Verify
        db.cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'instagram_keywords'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in db.cursor.fetchall()]
        print(f"\nRemaining columns: {columns}")

    except Exception as e:
        print(f"Error: {e}")
        db.conn.rollback()

    db.disconnect()
