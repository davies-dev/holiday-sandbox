#!/usr/bin/env python3
"""
Migration script to create the spot_profile_links table for many-to-many relationship
between poker_spots and game_profiles.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def run_migration():
    """Create the spot_profile_links table."""
    print("=== Migration: Creating Spot Profile Links Table ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Step 1: Check if table already exists
        print("Step 1: Checking if spot_profile_links table exists...")
        
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'spot_profile_links'
                )
            """)
            table_exists = cur.fetchone()[0]
        
        if table_exists:
            print("[INFO] spot_profile_links table already exists. Skipping table creation.")
        else:
            print("Creating spot_profile_links table...")
            
            # Create the spot_profile_links table
            with db.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE spot_profile_links (
                        id SERIAL PRIMARY KEY,
                        spot_id INTEGER NOT NULL REFERENCES poker_spots(id) ON DELETE CASCADE,
                        profile_id INTEGER NOT NULL REFERENCES game_profiles(id) ON DELETE CASCADE,
                        UNIQUE(spot_id, profile_id)
                    )
                """)
            db.conn.commit()
            print("[OK] Created spot_profile_links table")
        
        # Step 2: Verify the table structure
        print("\nStep 2: Verifying table structure...")
        
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'spot_profile_links'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
        
        print("Table structure:")
        for col_name, data_type, nullable, default in columns:
            print(f"  {col_name}: {data_type} (nullable: {nullable}, default: {default})")
        
        print("\n[OK] Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        if db and db.conn:
            db.conn.rollback()
        return False
    finally:
        if db:
            db.close()

def rollback_migration():
    """Rollback the migration by dropping the spot_profile_links table."""
    print("=== Rollback: Dropping Spot Profile Links Table ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Check if table exists
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'spot_profile_links'
                )
            """)
            table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("[OK] No table to rollback. spot_profile_links table doesn't exist.")
            return True
        
        # Drop the table
        print("Dropping spot_profile_links table...")
        with db.conn.cursor() as cur:
            cur.execute("DROP TABLE spot_profile_links")
        db.conn.commit()
        print("[OK] Dropped spot_profile_links table")
        
        print("[OK] Rollback completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Rollback failed: {e}")
        if db and db.conn:
            db.conn.rollback()
        return False
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create spot_profile_links table")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback_migration()
    else:
        success = run_migration()
    
    sys.exit(0 if success else 1) 