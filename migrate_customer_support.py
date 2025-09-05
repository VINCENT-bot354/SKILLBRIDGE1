
#!/usr/bin/env python3
"""
Migration script to add customer support columns to admin_settings table
"""

import os
import psycopg2
from psycopg2.sql import SQL, Identifier

def run_migration():
    """Add customer support columns to admin_settings table"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Check if columns already exist
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'admin_settings' 
            AND column_name IN ('support_whatsapp', 'support_phone', 'support_email')
        """)
        
        existing_columns = [row[0] for row in cur.fetchall()]
        
        # Add missing columns
        columns_to_add = [
            ('support_whatsapp', 'VARCHAR(20)'),
            ('support_phone', 'VARCHAR(20)'),
            ('support_email', 'VARCHAR(200)')
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                print(f"Adding column {column_name}...")
                cur.execute(f"""
                    ALTER TABLE admin_settings 
                    ADD COLUMN {column_name} {column_type}
                """)
                print(f"✓ Added {column_name}")
            else:
                print(f"Column {column_name} already exists, skipping")
        
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
    print("🔄 Starting customer support migration...")
    success = run_migration()
    exit(0 if success else 1)
