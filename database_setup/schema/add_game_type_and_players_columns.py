#!/usr/bin/env python3
"""
Migration script to add game_type_pattern and num_players columns to study_tag_rules table.
This extends the rules engine to filter on both game format and player count.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def run_migration():
    """Add the new columns to the study_tag_rules table."""
    print("=== Migration: Adding Game Type and Player Count Columns ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Check if columns already exist
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'study_tag_rules' 
                AND column_name IN ('game_type_pattern', 'num_players')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]
        
        if 'game_type_pattern' in existing_columns and 'num_players' in existing_columns:
            print("[OK] Columns already exist. Migration not needed.")
            return True
        
        # Add the new columns
        with db.conn.cursor() as cur:
            # Add game_type_pattern column if it doesn't exist
            if 'game_type_pattern' not in existing_columns:
                print("Adding game_type_pattern column...")
                cur.execute("""
                    ALTER TABLE study_tag_rules 
                    ADD COLUMN game_type_pattern VARCHAR(50)
                """)
                print("[OK] Added game_type_pattern column")
            
            # Add num_players column if it doesn't exist
            if 'num_players' not in existing_columns:
                print("Adding num_players column...")
                cur.execute("""
                    ALTER TABLE study_tag_rules 
                    ADD COLUMN num_players INT
                """)
                print("[OK] Added num_players column")
        
        db.conn.commit()
        print("[OK] Migration completed successfully!")
        
        # Verify the columns were added
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'study_tag_rules' 
                AND column_name IN ('game_type_pattern', 'num_players')
                ORDER BY column_name
            """)
            columns = cur.fetchall()
            
            print("\nVerification - New columns:")
            for col_name, data_type, is_nullable in columns:
                print(f"  {col_name}: {data_type} (nullable: {is_nullable})")
        
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
    """Rollback the migration by dropping the new columns."""
    print("=== Rollback: Removing Game Type and Player Count Columns ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        with db.conn.cursor() as cur:
            # Check if columns exist before trying to drop them
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'study_tag_rules' 
                AND column_name IN ('game_type_pattern', 'num_players')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]
            
            if not existing_columns:
                print("[OK] No columns to rollback. Columns don't exist.")
                return True
            
            # Drop the columns
            for column in existing_columns:
                print(f"Dropping {column} column...")
                cur.execute(f"ALTER TABLE study_tag_rules DROP COLUMN {column}")
                print(f"[OK] Dropped {column} column")
        
        db.conn.commit()
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
    
    parser = argparse.ArgumentParser(description="Migration script for game type and player count columns")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback_migration()
    else:
        success = run_migration()
    
    sys.exit(0 if success else 1) 