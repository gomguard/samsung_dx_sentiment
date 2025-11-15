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
        """Create videos, comments, and raw data tables if they don't exist"""
        try:
            # Create videos table
            create_videos_table = """
            CREATE TABLE IF NOT EXISTS youtube_videos (
                video_id VARCHAR(50),
                keyword VARCHAR(255) NOT NULL,
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
                category_id VARCHAR(10),
                engagement_rate DECIMAL(10, 4),
                comment_text_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (video_id, keyword)
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
                published_at TIMESTAMP,
                sentiment_score DECIMAL(5, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Create raw videos table (필터링 전 모든 수집 데이터)
            # PRIMARY KEY를 (video_id, created_at)로 설정하여 시계열 데이터 수집 가능
            create_raw_videos_table = """
            CREATE TABLE IF NOT EXISTS youtube_videos_raw (
                video_id VARCHAR(50),
                keyword VARCHAR(255),
                title TEXT,
                description TEXT,
                published_at TIMESTAMP,
                category_id VARCHAR(10),
                category VARCHAR(50),
                channel_id VARCHAR(50),
                channel_title TEXT,
                channel_country VARCHAR(10),
                channel_custom_url TEXT,
                channel_subscriber_count BIGINT,
                channel_video_count INTEGER,
                channel_total_view_count BIGINT,
                view_count BIGINT,
                like_count BIGINT,
                comment_count INTEGER,
                engagement_rate DECIMAL(10, 4),
                quality_filter_passed BOOLEAN,
                filter_fail_reason TEXT,
                created_at TIMESTAMP,
                PRIMARY KEY (video_id, created_at)
            );
            """

            # Create indexes
            create_indexes = """
            CREATE INDEX IF NOT EXISTS idx_comments_video_id ON youtube_comments(video_id);
            CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON youtube_comments(parent_comment_id);
            CREATE INDEX IF NOT EXISTS idx_videos_published_at ON youtube_videos(published_at);
            CREATE INDEX IF NOT EXISTS idx_raw_videos_keyword ON youtube_videos_raw(keyword);
            CREATE INDEX IF NOT EXISTS idx_raw_videos_filter ON youtube_videos_raw(quality_filter_passed);
            CREATE INDEX IF NOT EXISTS idx_raw_videos_created ON youtube_videos_raw(created_at);
            """

            self.cursor.execute(create_videos_table)
            self.cursor.execute(create_comments_table)
            self.cursor.execute(create_raw_videos_table)
            self.cursor.execute(create_indexes)
            self.conn.commit()

            print("Tables created successfully (including youtube_videos_raw)")
            return True

        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            return False

    def insert_raw_videos(self, raw_videos_df: pd.DataFrame, keyword: str) -> int:
        """
        Insert raw videos data (before filtering) into database

        Args:
            raw_videos_df (pd.DataFrame): DataFrame with all collected video data
            keyword (str): Search keyword

        Returns:
            int: Number of rows inserted
        """
        try:
            # Add keyword to dataframe
            raw_videos_df['keyword'] = keyword

            # Select required columns for raw table
            required_columns = [
                'video_id', 'keyword', 'title', 'description', 'published_at',
                'category_id', 'category', 'channel_id', 'channel_title', 'channel_country',
                'channel_custom_url', 'channel_subscriber_count', 'channel_video_count',
                'channel_total_view_count', 'view_count', 'like_count', 'comment_count',
                'engagement_rate', 'quality_filter_passed', 'filter_fail_reason', 'created_at'
            ]

            # Filter to only existing columns
            available_columns = [col for col in required_columns if col in raw_videos_df.columns]
            df_to_insert = raw_videos_df[available_columns].copy()

            # Replace NaN with None
            df_to_insert = df_to_insert.where(pd.notna(df_to_insert), None)

            # Convert to list of tuples
            records = [tuple(row) for row in df_to_insert.values]

            # Create insert query
            columns_str = ', '.join(available_columns)
            placeholders = ', '.join(['%s'] * len(available_columns))

            # 시계열 데이터 수집을 위해 ON CONFLICT DO NOTHING 사용
            # (video_id, created_at)가 PRIMARY KEY이므로 같은 시간에 수집된 중복만 무시
            insert_query = f"""
            INSERT INTO youtube_videos_raw ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT (video_id, created_at) DO NOTHING
            """

            # Execute batch insert
            extras.execute_batch(self.cursor, insert_query, records)
            self.conn.commit()

            print(f"Inserted/Updated {len(records)} raw videos")
            return len(records)

        except Exception as e:
            print(f"Error inserting raw videos: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return 0

    def insert_videos(self, videos_df: pd.DataFrame) -> int:
        """
        Insert videos data into database

        Args:
            videos_df (pd.DataFrame): DataFrame with video data

        Returns:
            int: Number of rows inserted
        """
        try:
            # Select only required columns (video_content_summary 제거됨)
            required_columns = [
                'video_id', 'keyword', 'title', 'description', 'published_at',
                'channel_country', 'channel_custom_url',
                'channel_subscriber_count', 'channel_video_count',
                'view_count', 'like_count', 'comment_count',
                'category_id', 'category', 'engagement_rate',
                'comment_text_summary'
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

            # Create UPDATE clause dynamically (video_id, keyword 제외 - PRIMARY KEY)
            update_columns = [col for col in available_columns if col not in ('video_id', 'keyword')]
            update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])

            insert_query = f"""
            INSERT INTO youtube_videos ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT (video_id, keyword) DO UPDATE SET
                {update_clause}
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
                'comment_text_display', 'like_count', 'reply_count',
                'published_at', 'sentiment_score'
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

            # Create UPDATE clause dynamically (comment_id 제외)
            update_columns = [col for col in available_columns if col != 'comment_id']
            update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])

            insert_query = f"""
            INSERT INTO youtube_comments ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT (comment_id) DO UPDATE SET
                {update_clause}
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
