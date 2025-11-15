"""
Keyword Management Script

Manage keywords for YouTube data collection:
- Add new keywords
- List all keywords
- Delete keywords
- Activate/Deactivate keywords
- Update keyword settings

Usage:
    python manage_keywords.py add "Samsung TV" --max-videos 50 --max-comments 50
    python manage_keywords.py list
    python manage_keywords.py delete "Samsung TV"
    python manage_keywords.py activate "Samsung TV"
    python manage_keywords.py deactivate "Samsung TV"
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import argparse
import psycopg2
from datetime import datetime
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB


class KeywordManager:
    """Manage keywords for YouTube data collection"""

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
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor()
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

    def add_keyword(self, keyword, max_videos=50, max_comments_per_video=50, region_code='US'):
        """Add a new keyword"""
        try:

            query = """
            INSERT INTO youtube_keywords
            (keyword, max_videos, max_comments_per_video, region_code, status)
            VALUES (%s, %s, %s, %s, 'active')
            ON CONFLICT (keyword) DO UPDATE SET
                max_videos = EXCLUDED.max_videos,
                max_comments_per_video = EXCLUDED.max_comments_per_video,
                region_code = EXCLUDED.region_code,
                status = 'active',
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
            """
            self.cursor.execute(query, (keyword, max_videos, max_comments_per_video, region_code))
            keyword_id = self.cursor.fetchone()[0]
            self.conn.commit()

            print(f"[OK] Keyword added: '{keyword}' (ID: {keyword_id})")
            print(f"     Settings: max_videos={max_videos}, max_comments={max_comments_per_video}, region={region_code}")
            return True
        except Exception as e:
            print(f"Error adding keyword: {e}")
            self.conn.rollback()
            return False

    def list_keywords(self, show_all=False):
        """List all keywords"""
        try:
            if show_all:
                query = "SELECT * FROM youtube_keywords ORDER BY created_at DESC"
            else:
                query = "SELECT * FROM youtube_keywords WHERE status = 'active' ORDER BY created_at DESC"

            self.cursor.execute(query)
            keywords = self.cursor.fetchall()

            if not keywords:
                print("No keywords found")
                return

            print("\n" + "="*120)
            print(f"{'ID':<5} {'Keyword':<30} {'Status':<10} {'Videos':<8} {'Comments':<10} {'Region':<8} {'Last Collected':<20} {'Total V/C':<15}")
            print("="*120)

            for row in keywords:
                kid, keyword, status, max_v, max_c, region, last_coll, total_v, total_c, created, updated = row
                last_coll_str = last_coll.strftime("%Y-%m-%d %H:%M") if last_coll else "Never"
                print(f"{kid:<5} {keyword:<30} {status:<10} {max_v:<8} {max_c:<10} {region:<8} {last_coll_str:<20} {total_v}/{total_c:<14}")

            print("="*120)
            print(f"Total: {len(keywords)} keywords")
            if not show_all:
                print("(Use --all to see inactive keywords)")

        except Exception as e:
            print(f"Error listing keywords: {e}")

    def delete_keyword(self, keyword):
        """Delete a keyword"""
        try:
            # Normalize keyword
            keyword = keyword.lower().strip()

            query = "DELETE FROM youtube_keywords WHERE keyword = %s RETURNING id"
            self.cursor.execute(query, (keyword,))
            result = self.cursor.fetchone()

            if result:
                self.conn.commit()
                print(f"[OK] Keyword deleted: '{keyword}'")
                return True
            else:
                print(f"Keyword not found: '{keyword}'")
                return False
        except Exception as e:
            print(f"Error deleting keyword: {e}")
            self.conn.rollback()
            return False

    def update_status(self, keyword, status):
        """Update keyword status (active/inactive)"""
        try:
            # Normalize keyword
            keyword = keyword.lower().strip()

            query = """
            UPDATE youtube_keywords
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE keyword = %s
            RETURNING id
            """
            self.cursor.execute(query, (status, keyword))
            result = self.cursor.fetchone()

            if result:
                self.conn.commit()
                print(f"[OK] Keyword '{keyword}' status updated to '{status}'")
                return True
            else:
                print(f"Keyword not found: '{keyword}'")
                return False
        except Exception as e:
            print(f"Error updating status: {e}")
            self.conn.rollback()
            return False

    def get_active_keywords(self):
        """Get all active keywords for batch processing"""
        try:
            query = """
            SELECT keyword, max_videos, max_comments_per_video, region_code, category
            FROM youtube_keywords
            WHERE status = 'active'
            ORDER BY last_collected_at ASC NULLS FIRST
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting active keywords: {e}")
            return []

    def update_collection_stats(self, keyword, videos_count, comments_count):
        """Update collection statistics for a keyword"""
        try:
            query = """
            UPDATE youtube_keywords
            SET last_collected_at = CURRENT_TIMESTAMP,
                total_videos_collected = total_videos_collected + %s,
                total_comments_collected = total_comments_collected + %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE keyword = %s
            """
            self.cursor.execute(query, (videos_count, comments_count, keyword))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating collection stats: {e}")
            self.conn.rollback()
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Manage keywords for YouTube data collection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a new keyword
  python manage_keywords.py add "Samsung TV" --max-videos 50 --max-comments 50

  # List all active keywords
  python manage_keywords.py list

  # List all keywords (including inactive)
  python manage_keywords.py list --all

  # Delete a keyword
  python manage_keywords.py delete "Samsung TV"

  # Deactivate a keyword (keep data, stop collection)
  python manage_keywords.py deactivate "Samsung TV"

  # Reactivate a keyword
  python manage_keywords.py activate "Samsung TV"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new keyword')
    add_parser.add_argument('keyword', type=str, help='Keyword to add')
    add_parser.add_argument('--max-videos', type=int, default=50, help='Max videos to collect (default: 50)')
    add_parser.add_argument('--max-comments', type=int, default=50, help='Max comments per video (default: 50)')
    add_parser.add_argument('--region', type=str, default='US', help='Region code (default: US)')

    # List command
    list_parser = subparsers.add_parser('list', help='List all keywords')
    list_parser.add_argument('--all', action='store_true', help='Show all keywords including inactive')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a keyword')
    delete_parser.add_argument('keyword', type=str, help='Keyword to delete')

    # Activate command
    activate_parser = subparsers.add_parser('activate', help='Activate a keyword')
    activate_parser.add_argument('keyword', type=str, help='Keyword to activate')

    # Deactivate command
    deactivate_parser = subparsers.add_parser('deactivate', help='Deactivate a keyword')
    deactivate_parser.add_argument('keyword', type=str, help='Keyword to deactivate')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    manager = KeywordManager()
    if not manager.connect():
        print("Failed to connect to database")
        return

    if args.command == 'add':
        manager.add_keyword(args.keyword, args.max_videos, args.max_comments, args.region)

    elif args.command == 'list':
        manager.list_keywords(show_all=args.all)

    elif args.command == 'delete':
        manager.delete_keyword(args.keyword)

    elif args.command == 'activate':
        manager.update_status(args.keyword, 'active')

    elif args.command == 'deactivate':
        manager.update_status(args.keyword, 'inactive')

    manager.disconnect()


if __name__ == "__main__":
    main()
