"""
Test database connection and table creation
"""
from config.db_manager import YouTubeDBManager

print("="*80)
print("PostgreSQL Database Manager Test")
print("="*80)

db = YouTubeDBManager()

# Test connection
print("\n[1/3] Testing connection...")
if db.test_connection():
    print("Connection test successful!")
else:
    print("Connection test failed!")
    exit(1)

# Connect and create tables
print("\n[2/3] Creating tables...")
if db.connect():
    db.create_tables()

    # Get current counts
    print("\n[3/3] Current database stats:")
    print(f"Videos: {db.get_video_count()}")
    print(f"Comments: {db.get_comment_count()}")

    db.disconnect()
else:
    print("Failed to connect to database")
    exit(1)

print("\n" + "="*80)
print("Test completed successfully!")
print("="*80)
