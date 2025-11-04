"""
PostgreSQL Database Manager for Instagram Analysis Pipeline

Handles connection, table creation, and data insertion to PostgreSQL database.
"""

import os
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import psycopg2
from psycopg2 import sql, extras
import pandas as pd
from typing import Dict, List, Optional

# Import from parent config directory
try:
    from config import secrets
    POSTGRES_HOST = secrets.POSTGRES_HOST
    POSTGRES_PORT = secrets.POSTGRES_PORT
    POSTGRES_USER = secrets.POSTGRES_USER
    POSTGRES_PASSWORD = secrets.POSTGRES_PASSWORD
    POSTGRES_DB = secrets.POSTGRES_DB
except ImportError as e:
    print(f"Warning: Could not import config.secrets: {e}")
    print("Trying alternative import...")
    try:
        # Try importing from parent config directory
        import importlib.util
        spec = importlib.util.spec_from_file_location("secrets",
            os.path.join(parent_dir, "config", "secrets.py"))
        secrets = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(secrets)
        POSTGRES_HOST = secrets.POSTGRES_HOST
        POSTGRES_PORT = secrets.POSTGRES_PORT
        POSTGRES_USER = secrets.POSTGRES_USER
        POSTGRES_PASSWORD = secrets.POSTGRES_PASSWORD
        POSTGRES_DB = secrets.POSTGRES_DB
        print("Successfully loaded secrets from file path")
    except Exception as e2:
        print(f"Error: Could not load secrets: {e2}")
        # Fallback for development
        POSTGRES_HOST = "localhost"
        POSTGRES_PORT = 5432
        POSTGRES_USER = "postgres"
        POSTGRES_PASSWORD = ""
        POSTGRES_DB = "samsung_analysis"


class InstagramDBManager:
    """PostgreSQL Database Manager for Instagram data"""

    def __init__(self):
        """Initialize database connection"""
        self.connection_params = {
            'host': POSTGRES_HOST,
            'port': POSTGRES_PORT,
            'user': POSTGRES_USER,
            'password': POSTGRES_PASSWORD,
            'dbname': POSTGRES_DB
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor()
            print(f"Connected to PostgreSQL database: {POSTGRES_DB}")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False

    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Disconnected from database")

    def create_tables(self):
        """Create posts, comments, and keywords tables if they don't exist"""
        try:
            # Create keywords management table
            create_keywords_table = """
            CREATE TABLE IF NOT EXISTS instagram_keywords (
                id SERIAL PRIMARY KEY,
                keyword VARCHAR(200) UNIQUE NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                max_posts INTEGER DEFAULT 30,
                max_comments_per_post INTEGER DEFAULT 50,
                last_collected_at TIMESTAMP,
                total_posts_collected INTEGER DEFAULT 0,
                total_comments_collected INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Create posts table
            create_posts_table = """
            CREATE TABLE IF NOT EXISTS instagram_posts (
                post_id VARCHAR(100) PRIMARY KEY,
                keyword VARCHAR(200),
                search_keyword VARCHAR(200),
                collected_at TIMESTAMP,
                author_username VARCHAR(100),
                author_id VARCHAR(100),
                caption TEXT,
                media_type VARCHAR(20),
                media_url TEXT,
                permalink TEXT,
                published_at TIMESTAMP,
                like_count INTEGER,
                comment_count INTEGER,
                play_count INTEGER,
                share_count INTEGER,
                hashtags TEXT,
                mentions TEXT,
                is_video BOOLEAN,
                video_content_summary TEXT,
                comment_text_summary TEXT,
                platform VARCHAR(20) DEFAULT 'instagram',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Create comments table
            create_comments_table = """
            CREATE TABLE IF NOT EXISTS instagram_comments (
                comment_id VARCHAR(100) PRIMARY KEY,
                post_id VARCHAR(100) REFERENCES instagram_posts(post_id) ON DELETE CASCADE,
                comment_text TEXT,
                author_username VARCHAR(100),
                like_count INTEGER,
                published_at TIMESTAMP,
                sentiment VARCHAR(20),
                sentiment_score FLOAT,
                sentiment_label VARCHAR(50),
                platform VARCHAR(20) DEFAULT 'instagram',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Create indexes
            create_indexes = """
            CREATE INDEX IF NOT EXISTS idx_comments_post_id ON instagram_comments(post_id);
            CREATE INDEX IF NOT EXISTS idx_posts_keyword ON instagram_posts(search_keyword);
            CREATE INDEX IF NOT EXISTS idx_posts_published_at ON instagram_posts(published_at);
            CREATE INDEX IF NOT EXISTS idx_keywords_status ON instagram_keywords(status);
            """

            self.cursor.execute(create_keywords_table)
            self.cursor.execute(create_posts_table)
            self.cursor.execute(create_comments_table)
            self.cursor.execute(create_indexes)
            self.conn.commit()

            print("Tables created successfully")
            return True

        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            return False

    def insert_posts(self, posts_df: pd.DataFrame) -> int:
        """
        Insert posts data into database

        Args:
            posts_df (pd.DataFrame): DataFrame with posts data

        Returns:
            int: Number of rows inserted
        """
        try:
            # Select only required columns
            required_columns = [
                'post_id', 'search_keyword', 'collected_at',
                'author_username', 'author_id', 'caption', 'media_type', 'media_url',
                'permalink', 'published_at', 'like_count', 'comment_count', 'play_count',
                'share_count', 'hashtags', 'mentions', 'is_video',
                'video_content_summary', 'comment_text_summary', 'platform'
            ]

            # Filter to only existing columns
            available_columns = [col for col in required_columns if col in posts_df.columns]
            df_to_insert = posts_df[available_columns].copy()

            # Replace NaN with None
            df_to_insert = df_to_insert.where(pd.notna(df_to_insert), None)

            # Convert to list of tuples
            records = [tuple(row) for row in df_to_insert.values]

            # Create insert query
            columns_str = ', '.join(available_columns)
            placeholders = ', '.join(['%s'] * len(available_columns))

            insert_query = f"""
            INSERT INTO instagram_posts ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT (post_id) DO UPDATE SET
                caption = EXCLUDED.caption,
                like_count = EXCLUDED.like_count,
                comment_count = EXCLUDED.comment_count,
                play_count = EXCLUDED.play_count,
                share_count = EXCLUDED.share_count,
                video_content_summary = EXCLUDED.video_content_summary,
                comment_text_summary = EXCLUDED.comment_text_summary,
                updated_at = CURRENT_TIMESTAMP
            """

            # Execute batch insert
            extras.execute_batch(self.cursor, insert_query, records)
            self.conn.commit()

            print(f"Inserted/Updated {len(records)} posts")
            return len(records)

        except Exception as e:
            print(f"Error inserting posts: {e}")
            self.conn.rollback()
            return 0

    def insert_comments(self, comments_df: pd.DataFrame) -> int:
        """
        Insert comments data into database

        Args:
            comments_df (pd.DataFrame): DataFrame with comments data

        Returns:
            int: Number of rows inserted
        """
        try:
            # Select only required columns
            required_columns = [
                'comment_id', 'post_id', 'comment_text', 'author_username',
                'like_count', 'published_at', 'platform'
            ]

            # Add sentiment columns if available
            if 'sentiment' in comments_df.columns:
                required_columns.extend(['sentiment', 'sentiment_score', 'sentiment_label'])

            # Filter to only existing columns
            available_columns = [col for col in required_columns if col in comments_df.columns]
            df_to_insert = comments_df[available_columns].copy()

            # Replace NaN with None
            df_to_insert = df_to_insert.where(pd.notna(df_to_insert), None)

            # Convert to list of tuples
            records = [tuple(row) for row in df_to_insert.values]

            # Create insert query
            columns_str = ', '.join(available_columns)
            placeholders = ', '.join(['%s'] * len(available_columns))

            # Build update clause dynamically
            update_fields = ['comment_text', 'like_count']
            if 'sentiment' in available_columns:
                update_fields.extend(['sentiment', 'sentiment_score', 'sentiment_label'])

            update_clause = ', '.join([f"{field} = EXCLUDED.{field}" for field in update_fields])

            insert_query = f"""
            INSERT INTO instagram_comments ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT (comment_id) DO UPDATE SET
                {update_clause},
                updated_at = CURRENT_TIMESTAMP
            """

            # Execute batch insert
            extras.execute_batch(self.cursor, insert_query, records)
            self.conn.commit()

            print(f"Inserted/Updated {len(records)} comments")
            return len(records)

        except Exception as e:
            print(f"Error inserting comments: {e}")
            self.conn.rollback()
            return 0

    def get_post_count(self) -> int:
        """Get total number of posts in database"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM instagram_posts")
            count = self.cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Error getting post count: {e}")
            return 0

    def get_comment_count(self) -> int:
        """Get total number of comments in database"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM instagram_comments")
            count = self.cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Error getting comment count: {e}")
            return 0

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if self.connect():
                self.cursor.execute("SELECT version();")
                version = self.cursor.fetchone()
                print(f"PostgreSQL version: {version[0]}")
                self.disconnect()
                return True
            return False
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


def main():
    """Test database connection and table creation"""
    print("="*80)
    print("PostgreSQL Database Manager Test (Instagram)")
    print("="*80)

    db = InstagramDBManager()

    # Test connection
    print("\n[1/3] Testing connection...")
    if db.test_connection():
        print("Connection test successful!")
    else:
        print("Connection test failed!")
        return

    # Connect and create tables
    print("\n[2/3] Creating tables...")
    if db.connect():
        db.create_tables()

        # Get current counts
        print("\n[3/3] Current database stats:")
        print(f"Posts: {db.get_post_count()}")
        print(f"Comments: {db.get_comment_count()}")

        db.disconnect()
    else:
        print("Failed to connect to database")

    print("\n" + "="*80)
    print("Test completed")
    print("="*80)


if __name__ == "__main__":
    main()
