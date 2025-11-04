"""
Keyword Management Script

Manage keywords for Instagram data collection:
- Add new keywords
- List all keywords
- Delete keywords
- Activate/Deactivate keywords
- Update keyword settings

Usage:
    python manage_keywords.py add "Samsung TV" --max-posts 30 --max-comments 50
    python manage_keywords.py list
    python manage_keywords.py delete "Samsung TV"
    python manage_keywords.py activate "Samsung TV"
    python manage_keywords.py deactivate "Samsung TV"
"""

import os
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import argparse
import psycopg2
from datetime import datetime

# Import from parent config directory
try:
    from config import secrets
    POSTGRES_HOST = secrets.POSTGRES_HOST
    POSTGRES_PORT = secrets.POSTGRES_PORT
    POSTGRES_USER = secrets.POSTGRES_USER
    POSTGRES_PASSWORD = secrets.POSTGRES_PASSWORD
    POSTGRES_DB = secrets.POSTGRES_DB
except ImportError:
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
    except Exception:
        # Fallback for development
        POSTGRES_HOST = "localhost"
        POSTGRES_PORT = 5432
        POSTGRES_USER = "postgres"
        POSTGRES_PASSWORD = ""
        POSTGRES_DB = "samsung_analysis"


class KeywordManager:
    """Manage keywords for Instagram data collection"""

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

    def add_keyword(self, keyword, max_posts=30, max_comments_per_post=50):
        """Add a new keyword"""
        try:
            # Normalize keyword
            keyword = keyword.lower().strip()

            query = """
            INSERT INTO instagram_keywords
            (keyword, max_posts, max_comments_per_post, status)
            VALUES (%s, %s, %s, 'active')
            ON CONFLICT (keyword) DO UPDATE SET
                max_posts = EXCLUDED.max_posts,
                max_comments_per_post = EXCLUDED.max_comments_per_post,
                status = 'active',
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
            """
            self.cursor.execute(query, (keyword, max_posts, max_comments_per_post))
            keyword_id = self.cursor.fetchone()[0]
            self.conn.commit()

            print(f"[OK] Keyword added: '{keyword}' (ID: {keyword_id})")
            print(f"     Settings: max_posts={max_posts}, max_comments={max_comments_per_post}")
            return True
        except Exception as e:
            print(f"Error adding keyword: {e}")
            self.conn.rollback()
            return False

    def list_keywords(self, show_all=False):
        """List all keywords"""
        try:
            if show_all:
                query = "SELECT * FROM instagram_keywords ORDER BY created_at DESC"
            else:
                query = "SELECT * FROM instagram_keywords WHERE status = 'active' ORDER BY created_at DESC"

            self.cursor.execute(query)
            keywords = self.cursor.fetchall()

            if not keywords:
                print("No keywords found")
                return

            print("\n" + "="*110)
            print(f"{'ID':<5} {'Keyword':<30} {'Status':<10} {'Posts':<8} {'Comments':<10} {'Last Collected':<20} {'Total P/C':<15}")
            print("="*110)

            for row in keywords:
                kid, keyword, status, max_p, max_c, last_coll, total_p, total_c, created, updated = row
                last_coll_str = last_coll.strftime("%Y-%m-%d %H:%M") if last_coll else "Never"
                print(f"{kid:<5} {keyword:<30} {status:<10} {max_p:<8} {max_c:<10} {last_coll_str:<20} {total_p}/{total_c:<14}")

            print("="*110)
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

            query = "DELETE FROM instagram_keywords WHERE keyword = %s RETURNING id"
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
            UPDATE instagram_keywords
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
            SELECT keyword, max_posts, max_comments_per_post
            FROM instagram_keywords
            WHERE status = 'active'
            ORDER BY last_collected_at ASC NULLS FIRST
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting active keywords: {e}")
            return []

    def update_collection_stats(self, keyword, posts_count, comments_count):
        """Update collection statistics for a keyword"""
        try:
            query = """
            UPDATE instagram_keywords
            SET last_collected_at = CURRENT_TIMESTAMP,
                total_posts_collected = total_posts_collected + %s,
                total_comments_collected = total_comments_collected + %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE keyword = %s
            """
            self.cursor.execute(query, (posts_count, comments_count, keyword))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating collection stats: {e}")
            self.conn.rollback()
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Manage keywords for Instagram data collection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a new keyword
  python manage_keywords.py add "Samsung TV" --max-posts 30 --max-comments 50

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
    add_parser.add_argument('keyword', type=str, help='Keyword to add (e.g., "Samsung TV")')
    add_parser.add_argument('--max-posts', type=int, default=30, help='Max posts to collect (default: 30)')
    add_parser.add_argument('--max-comments', type=int, default=50, help='Max comments per post (default: 50)')

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
        manager.add_keyword(args.keyword, args.max_posts, args.max_comments)

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
