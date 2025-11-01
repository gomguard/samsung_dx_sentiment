"""
Clear all data from database
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

print("="*80)
print("Clearing Database")
print("="*80)

try:
    # Connect to database
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )

    cursor = conn.cursor()

    # Delete all data
    print("Deleting all comments...")
    cursor.execute("DELETE FROM youtube_comments")
    print("Deleting all videos...")
    cursor.execute("DELETE FROM youtube_videos")

    conn.commit()

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("Database cleared successfully!")
    print("="*80)

except Exception as e:
    print(f"Error: {e}")
    exit(1)
