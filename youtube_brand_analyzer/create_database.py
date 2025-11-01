"""
Create samsung_dx_sentiment database on PostgreSQL
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config.secrets import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD

print("="*80)
print("Creating samsung_dx_sentiment database")
print("="*80)

try:
    # Connect to postgres default database
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname='postgres'
    )

    # Set autocommit mode
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()

    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'samsung_dx_sentiment'")
    exists = cursor.fetchone()

    if exists:
        print("Database 'samsung_dx_sentiment' already exists!")
    else:
        # Create database
        cursor.execute("CREATE DATABASE samsung_dx_sentiment")
        print("Database 'samsung_dx_sentiment' created successfully!")

    cursor.close()
    conn.close()

    print("="*80)
    print("Done!")
    print("="*80)

except Exception as e:
    print(f"Error: {e}")
    exit(1)
