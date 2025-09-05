
#!/usr/bin/env python3
"""
Migration script to add profile_views table
"""

import os
import psycopg2
from psycopg2.sql import SQL, Identifier

def run_migration():
    """Create profile_views table"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Check if table already exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'profile_views'
            )
        """)
        
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("Creating profile_views table...")
            cur.execute("""
                CREATE TABLE profile_views (
                    id SERIAL PRIMARY KEY,
                    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                    viewer_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    viewer_ip VARCHAR(45),
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
                )
            """)
            
            # Create indexes
            cur.execute("""
                CREATE INDEX idx_profile_views_profile_date 
                ON profile_views (profile_id, created_at)
            """)
            
            print("✓ Created profile_views table and indexes")
        else:
            print("Table profile_views already exists, skipping")
        
        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("🔄 Starting profile views migration...")
    success = run_migration()
    exit(0 if success else 1)
