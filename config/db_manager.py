"""
PostgreSQL Database Manager for YouTube Analysis Pipeline

Handles connection, table creation, and data insertion to PostgreSQL database.
"""

import psycopg2
from psycopg2 import sql, extras
import pandas as pd
from typing import Dict, List, Optional
from .secrets import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB
)


class YouTubeDBManager:
    """PostgreSQL Database Manager for YouTube data"""

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
        """Create videos and comments tables if they don't exist"""
        try:
            # Create videos table
            create_videos_table = """
            CREATE TABLE IF NOT EXISTS youtube_videos (
                video_id VARCHAR(50) PRIMARY KEY,
                title TEXT,
                description TEXT,
                published_at TIMESTAMP,
                channel_country VARCHAR(10),
                channel_custom_url TEXT,
                channel_subscriber_count BIGINT,
                channel_video_count INTEGER,
                view_count BIGINT,
                like_count BIGINT,
                comment_count INTEGER,
                video_content_summary TEXT,
                comment_text_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Create comments table
            create_comments_table = """
            CREATE TABLE IF NOT EXISTS youtube_comments (
                comment_id VARCHAR(100) PRIMARY KEY,
                video_id VARCHAR(50) REFERENCES youtube_videos(video_id) ON DELETE CASCADE,
                comment_type VARCHAR(20),
                parent_comment_id VARCHAR(100),
                comment_text_display TEXT,
                like_count INTEGER,
                reply_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Create indexes
            create_indexes = """
            CREATE INDEX IF NOT EXISTS idx_comments_video_id ON youtube_comments(video_id);
            CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON youtube_comments(parent_comment_id);
            CREATE INDEX IF NOT EXISTS idx_videos_published_at ON youtube_videos(published_at);
            """

            self.cursor.execute(create_videos_table)
            self.cursor.execute(create_comments_table)
            self.cursor.execute(create_indexes)
            self.conn.commit()

            print("Tables created successfully")
            return True

        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            return False

    def insert_videos(self, videos_df: pd.DataFrame) -> int:
        """
        Insert videos data into database

        Args:
            videos_df (pd.DataFrame): DataFrame with video data

        Returns:
            int: Number of rows inserted
        """
        try:
            # Select only required columns
            required_columns = [
                'video_id', 'title', 'description', 'published_at',
                'channel_country', 'channel_custom_url',
                'channel_subscriber_count', 'channel_video_count',
                'view_count', 'like_count', 'comment_count',
                'video_content_summary', 'comment_text_summary'
            ]

            # Filter to only existing columns
            available_columns = [col for col in required_columns if col in videos_df.columns]
            df_to_insert = videos_df[available_columns].copy()

            # Replace NaN with None
            df_to_insert = df_to_insert.where(pd.notna(df_to_insert), None)

            # Convert to list of tuples
            records = [tuple(row) for row in df_to_insert.values]

            # Create insert query
            columns_str = ', '.join(available_columns)
            placeholders = ', '.join(['%s'] * len(available_columns))

            insert_query = f"""
            INSERT INTO youtube_videos ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT (video_id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                view_count = EXCLUDED.view_count,
                like_count = EXCLUDED.like_count,
                comment_count = EXCLUDED.comment_count,
                video_content_summary = EXCLUDED.video_content_summary,
                comment_text_summary = EXCLUDED.comment_text_summary,
                updated_at = CURRENT_TIMESTAMP
            """

            # Execute batch insert
            extras.execute_batch(self.cursor, insert_query, records)
            self.conn.commit()

            print(f"Inserted/Updated {len(records)} videos")
            return len(records)

        except Exception as e:
            print(f"Error inserting videos: {e}")
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
                'comment_id', 'video_id', 'comment_type', 'parent_comment_id',
                'comment_text_display', 'like_count', 'reply_count'
            ]

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

            insert_query = f"""
            INSERT INTO youtube_comments ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT (comment_id) DO UPDATE SET
                comment_text_display = EXCLUDED.comment_text_display,
                like_count = EXCLUDED.like_count,
                reply_count = EXCLUDED.reply_count,
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

    def get_video_count(self) -> int:
        """Get total number of videos in database"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM youtube_videos")
            count = self.cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Error getting video count: {e}")
            return 0

    def get_comment_count(self) -> int:
        """Get total number of comments in database"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM youtube_comments")
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
    print("PostgreSQL Database Manager Test")
    print("="*80)

    db = YouTubeDBManager()

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
        print(f"Videos: {db.get_video_count()}")
        print(f"Comments: {db.get_comment_count()}")

        db.disconnect()
    else:
        print("Failed to connect to database")

    print("\n" + "="*80)
    print("Test completed")
    print("="*80)


if __name__ == "__main__":
    main()
