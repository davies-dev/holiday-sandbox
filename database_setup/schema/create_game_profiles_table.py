#!/usr/bin/env python3
"""
Migration script to create the game_profiles table and insert initial game profiles.
This table stores predefined game format combinations for easy selection in the UI.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def run_migration():
    """Create the game_profiles table and insert initial data."""
    print("=== Migration: Creating Game Profiles Table ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Step 1: Check if table already exists
        print("Step 1: Checking if game_profiles table exists...")
        
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'game_profiles'
                )
            """)
            table_exists = cur.fetchone()[0]
        
        if table_exists:
            print("[INFO] game_profiles table already exists. Skipping table creation.")
        else:
            print("Creating game_profiles table...")
            
            # Create the game_profiles table
            with db.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE game_profiles (
                        id SERIAL PRIMARY KEY,
                        profile_name VARCHAR(100) UNIQUE NOT NULL,
                        game_class VARCHAR(20),
                        game_variant VARCHAR(20),
                        table_size VARCHAR(10)
                    )
                """)
            db.conn.commit()
            print("[OK] Created game_profiles table")
        
        # Step 2: Insert initial game profiles
        print("\nStep 2: Inserting initial game profiles...")
        
        # Check if profiles already exist
        with db.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM game_profiles")
            existing_count = cur.fetchone()[0]
        
        if existing_count > 0:
            print(f"[INFO] Found {existing_count} existing profiles. Skipping initial data insertion.")
        else:
            print("Inserting initial game profiles...")
            
            initial_profiles = [
                ('Zoom 6-max', 'cash', 'zoom', '6-max'),
                ('Spingo', 'tournament', 'regular', '3-max'),
                ('Live Cash 9-max', 'cash', 'regular', '9-max'),
                ('Online MTT 6-max', 'tournament', 'regular', '6-max'),
                ('Zoom 9-max', 'cash', 'zoom', '9-max'),
                ('Heads-up Cash', 'cash', 'regular', '2-max'),
                ('Heads-up Tournament', 'tournament', 'regular', '2-max')
            ]
            
            with db.conn.cursor() as cur:
                cur.executemany("""
                    INSERT INTO game_profiles (profile_name, game_class, game_variant, table_size) 
                    VALUES (%s, %s, %s, %s)
                """, initial_profiles)
            db.conn.commit()
            print(f"[OK] Inserted {len(initial_profiles)} initial game profiles")
        
        # Step 3: Verify the table structure and data
        print("\nStep 3: Verifying table structure and data...")
        
        # Check table structure
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'game_profiles'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
        
        print("Table structure:")
        for col_name, data_type, nullable, default in columns:
            print(f"  {col_name}: {data_type} (nullable: {nullable}, default: {default})")
        
        # Check data
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT profile_name, game_class, game_variant, table_size 
                FROM game_profiles 
                ORDER BY profile_name
            """)
            profiles = cur.fetchall()
        
        print(f"\nGame profiles ({len(profiles)} total):")
        for profile_name, game_class, game_variant, table_size in profiles:
            print(f"  {profile_name}: {game_class} {game_variant} {table_size}")
        
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
    """Rollback the migration by dropping the game_profiles table."""
    print("=== Rollback: Dropping Game Profiles Table ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Check if table exists
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'game_profiles'
                )
            """)
            table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("[OK] No table to rollback. game_profiles table doesn't exist.")
            return True
        
        # Drop the table
        print("Dropping game_profiles table...")
        with db.conn.cursor() as cur:
            cur.execute("DROP TABLE game_profiles")
        db.conn.commit()
        print("[OK] Dropped game_profiles table")
        
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
    
    parser = argparse.ArgumentParser(description="Create game_profiles table and insert initial data")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback_migration()
    else:
        success = run_migration()
    
    sys.exit(0 if success else 1) 