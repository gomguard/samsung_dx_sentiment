"""
PostgreSQL Database Manager for TikTok Analysis Pipeline

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


class TikTokDBManager:
    """PostgreSQL Database Manager for TikTok data"""

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
        """Create videos, comments, and keywords tables if they don't exist"""
        try:
            # Create keywords management table
            create_keywords_table = """
            CREATE TABLE IF NOT EXISTS tiktok_keywords (
                id SERIAL PRIMARY KEY,
                keyword VARCHAR(200) UNIQUE NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                max_videos INTEGER DEFAULT 30,
                max_comments_per_video INTEGER DEFAULT 50,
                last_collected_at TIMESTAMP,
                total_videos_collected INTEGER DEFAULT 0,
                total_comments_collected INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Create videos table (equivalent to posts in Instagram)
            create_videos_table = """
            CREATE TABLE IF NOT EXISTS tiktok_videos (
                video_id VARCHAR(100) PRIMARY KEY,
                search_keyword VARCHAR(200),
                search_region VARCHAR(10),
                search_order VARCHAR(20),
                collected_at TIMESTAMP,
                is_hashtag_info BOOLEAN DEFAULT FALSE,

                title TEXT,
                description TEXT,
                channel_id VARCHAR(100),
                channel_title VARCHAR(100),
                published_at TIMESTAMP,
                category_id VARCHAR(50),
                default_language VARCHAR(10),
                default_audio_language VARCHAR(10),
                live_broadcast_content VARCHAR(20),
                tags TEXT,

                thumbnail_default TEXT,
                thumbnail_medium TEXT,
                thumbnail_high TEXT,
                thumbnail_standard TEXT,
                thumbnail_maxres TEXT,

                view_count INTEGER,
                like_count INTEGER,
                dislike_count INTEGER DEFAULT 0,
                favorite_count INTEGER,
                comment_count INTEGER,

                duration_seconds INTEGER,
                duration_iso VARCHAR(50),
                dimension VARCHAR(10),
                definition VARCHAR(10),
                caption VARCHAR(10),
                licensed_content BOOLEAN,
                content_rating TEXT,
                projection VARCHAR(20),
                has_custom_thumbnail BOOLEAN,

                upload_status VARCHAR(20),
                privacy_status VARCHAR(20),
                license VARCHAR(50),
                embeddable BOOLEAN,
                public_stats_viewable BOOLEAN,
                made_for_kids BOOLEAN,
                self_declared_made_for_kids BOOLEAN,

                topic_ids TEXT,
                relevant_topic_ids TEXT,
                topic_categories TEXT,
                recording_date VARCHAR(50),
                location_latitude VARCHAR(50),
                location_longitude VARCHAR(50),
                location_altitude VARCHAR(50),

                channel_subscriber_count INTEGER,
                channel_video_count INTEGER,
                channel_total_view_count INTEGER,
                channel_description TEXT,
                channel_country VARCHAR(10),
                channel_custom_url TEXT,
                channel_published_at VARCHAR(50),

                video_content_summary TEXT,
                comment_text_summary TEXT,
                key_themes TEXT,
                sentiment_summary TEXT,
                platform VARCHAR(20) DEFAULT 'tiktok',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Create comments table
            create_comments_table = """
            CREATE TABLE IF NOT EXISTS tiktok_comments (
                comment_id VARCHAR(100) PRIMARY KEY,
                video_id VARCHAR(100) REFERENCES tiktok_videos(video_id) ON DELETE CASCADE,
                comment_type VARCHAR(20),
                parent_comment_id VARCHAR(100),
                collected_at TIMESTAMP,

                author_display_name VARCHAR(200),
                author_profile_image_url TEXT,
                author_channel_url TEXT,
                author_channel_id VARCHAR(100),

                comment_text_display TEXT,
                comment_text_original TEXT,
                comment_text_length INTEGER,

                like_count INTEGER,
                reply_count INTEGER,
                moderation_status VARCHAR(50),

                published_at TIMESTAMP,
                updated_at TIMESTAMP,

                viewer_rating VARCHAR(20),
                can_rate BOOLEAN,

                sentiment VARCHAR(20),
                sentiment_score FLOAT,
                sentiment_label VARCHAR(50),
                platform VARCHAR(20) DEFAULT 'tiktok',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Create indexes for better query performance
            create_indexes = """
            CREATE INDEX IF NOT EXISTS idx_tiktok_videos_keyword ON tiktok_videos(search_keyword);
            CREATE INDEX IF NOT EXISTS idx_tiktok_videos_published ON tiktok_videos(published_at);
            CREATE INDEX IF NOT EXISTS idx_tiktok_videos_view_count ON tiktok_videos(view_count);
            CREATE INDEX IF NOT EXISTS idx_tiktok_comments_video_id ON tiktok_comments(video_id);
            CREATE INDEX IF NOT EXISTS idx_tiktok_comments_published ON tiktok_comments(published_at);
            """

            # Execute table creation
            self.cursor.execute(create_keywords_table)
            self.cursor.execute(create_videos_table)
            self.cursor.execute(create_comments_table)
            self.cursor.execute(create_indexes)
            self.conn.commit()

            print("TikTok tables created successfully")
            return True

        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            return False

    def insert_videos(self, videos_df: pd.DataFrame) -> int:
        """
        Insert videos into database
        Uses ON CONFLICT to update existing records

        Args:
            videos_df: DataFrame with video data

        Returns:
            Number of videos inserted/updated
        """
        if videos_df.empty:
            return 0

        try:
            # Prepare data
            videos_df = videos_df.copy()

            # Handle timestamps
            timestamp_cols = ['collected_at', 'published_at']
            for col in timestamp_cols:
                if col in videos_df.columns:
                    videos_df[col] = pd.to_datetime(videos_df[col], errors='coerce')

            # Convert to records
            records = videos_df.to_dict('records')

            # Get column names from first record
            if not records:
                return 0

            columns = list(records[0].keys())

            # Build INSERT query with ON CONFLICT UPDATE
            insert_query = sql.SQL("""
                INSERT INTO tiktok_videos ({})
                VALUES ({})
                ON CONFLICT (video_id) DO UPDATE SET
                    {}
            """).format(
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(columns)),
                sql.SQL(', ').join(
                    sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(col), sql.Identifier(col))
                    for col in columns if col != 'video_id'
                )
            )

            # Execute batch insert
            inserted = 0
            for record in records:
                try:
                    values = [record.get(col) for col in columns]
                    self.cursor.execute(insert_query, values)
                    inserted += 1
                except Exception as e:
                    print(f"Error inserting video {record.get('video_id', 'unknown')}: {e}")
                    continue

            self.conn.commit()
            print(f"Inserted/updated {inserted} videos")
            return inserted

        except Exception as e:
            print(f"Error in batch insert videos: {e}")
            self.conn.rollback()
            return 0

    def insert_comments(self, comments_df: pd.DataFrame) -> int:
        """
        Insert comments into database
        Uses ON CONFLICT to update existing records

        Args:
            comments_df: DataFrame with comment data

        Returns:
            Number of comments inserted/updated
        """
        if comments_df.empty:
            return 0

        try:
            # Prepare data
            comments_df = comments_df.copy()

            # Handle timestamps
            timestamp_cols = ['collected_at', 'published_at', 'updated_at']
            for col in timestamp_cols:
                if col in comments_df.columns:
                    comments_df[col] = pd.to_datetime(comments_df[col], errors='coerce')

            # Convert to records
            records = comments_df.to_dict('records')

            if not records:
                return 0

            columns = list(records[0].keys())

            # Build INSERT query with ON CONFLICT UPDATE
            insert_query = sql.SQL("""
                INSERT INTO tiktok_comments ({})
                VALUES ({})
                ON CONFLICT (comment_id) DO UPDATE SET
                    {}
            """).format(
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(columns)),
                sql.SQL(', ').join(
                    sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(col), sql.Identifier(col))
                    for col in columns if col != 'comment_id'
                )
            )

            # Execute batch insert
            inserted = 0
            for record in records:
                try:
                    values = [record.get(col) for col in columns]
                    self.cursor.execute(insert_query, values)
                    inserted += 1
                except Exception as e:
                    print(f"Error inserting comment {record.get('comment_id', 'unknown')}: {e}")
                    continue

            self.conn.commit()
            print(f"Inserted/updated {inserted} comments")
            return inserted

        except Exception as e:
            print(f"Error in batch insert comments: {e}")
            self.conn.rollback()
            return 0

    def get_video_count(self) -> int:
        """Get total number of videos in database"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM tiktok_videos")
            return self.cursor.fetchone()[0]
        except:
            return 0

    def get_comment_count(self) -> int:
        """Get total number of comments in database"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM tiktok_comments")
            return self.cursor.fetchone()[0]
        except:
            return 0

    def get_keyword_stats(self, keyword: str) -> Optional[Dict]:
        """Get statistics for a specific keyword"""
        try:
            self.cursor.execute("""
                SELECT
                    COUNT(*) as video_count,
                    SUM(view_count) as total_views,
                    SUM(like_count) as total_likes,
                    SUM(comment_count) as total_comments,
                    AVG(view_count) as avg_views,
                    AVG(like_count) as avg_likes
                FROM tiktok_videos
                WHERE search_keyword = %s
            """, (keyword,))

            row = self.cursor.fetchone()
            if row:
                return {
                    'video_count': row[0],
                    'total_views': row[1] or 0,
                    'total_likes': row[2] or 0,
                    'total_comments': row[3] or 0,
                    'avg_views': float(row[4]) if row[4] else 0,
                    'avg_likes': float(row[5]) if row[5] else 0
                }
            return None
        except Exception as e:
            print(f"Error getting keyword stats: {e}")
            return None
