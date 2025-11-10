"""
Create Instagram Database Tables

Creates all necessary tables for the Instagram analysis pipeline.

Usage:
    python create_database.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from config.db_manager import InstagramDBManager


def main():
    """Create database tables"""
    print("="*80)
    print("Instagram Database Table Creation")
    print("="*80)

    db = InstagramDBManager()

    # Test connection first
    print("\n[1/2] Testing connection...")
    if not db.test_connection():
        print("Failed to connect to database. Please check your settings.")
        return

    # Create tables
    print("\n[2/2] Creating tables...")
    if db.connect():
        if db.create_tables():
            print("\nSuccess! All tables created.")
            print("\nCreated tables:")
            print("  - instagram_hashtags")
            print("  - instagram_posts")
            print("  - instagram_comments")
        else:
            print("\nFailed to create tables.")

        db.disconnect()
    else:
        print("Failed to connect to database")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
