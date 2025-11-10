"""
Test Instagram Database Connection

Tests the connection to the PostgreSQL database.

Usage:
    python test_db.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from config.db_manager import InstagramDBManager


def main():
    """Test database connection"""
    print("="*80)
    print("Instagram Database Connection Test")
    print("="*80)

    db = InstagramDBManager()

    if db.test_connection():
        print("\n✓ Database connection successful!")

        # Get current stats
        if db.connect():
            print("\nCurrent database statistics:")
            print(f"  Posts: {db.get_post_count()}")
            print(f"  Comments: {db.get_comment_count()}")
            db.disconnect()
    else:
        print("\n✗ Database connection failed!")
        print("\nPlease check:")
        print("  1. PostgreSQL server is running")
        print("  2. Database credentials in config/secrets.py")
        print("  3. Database exists")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
