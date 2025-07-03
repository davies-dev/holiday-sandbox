#!/usr/bin/env python3
"""
Migration script to add structured game format columns to hand_histories and study_tag_rules tables.
This replaces the simple game_type_pattern and num_players with more structured game_class, game_variant, and table_size.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def run_migration():
    """Add the new structured format columns to both tables."""
    print("=== Migration: Adding Structured Game Format Columns ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Step 1: Add new columns to hand_histories table
        print("Step 1: Adding new columns to hand_histories table...")
        
        # Check if columns already exist in hand_histories
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'hand_histories' 
                AND column_name IN ('game_class', 'game_variant', 'table_size')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]
        
        if 'game_class' not in existing_columns:
            print("Adding game_class column to hand_histories...")
            with db.conn.cursor() as cur:
                cur.execute("ALTER TABLE hand_histories ADD COLUMN game_class VARCHAR(20)")
            db.conn.commit()
            print("[OK] Added game_class column to hand_histories")
        
        if 'game_variant' not in existing_columns:
            print("Adding game_variant column to hand_histories...")
            with db.conn.cursor() as cur:
                cur.execute("ALTER TABLE hand_histories ADD COLUMN game_variant VARCHAR(20)")
            db.conn.commit()
            print("[OK] Added game_variant column to hand_histories")
        
        if 'table_size' not in existing_columns:
            print("Adding table_size column to hand_histories...")
            with db.conn.cursor() as cur:
                cur.execute("ALTER TABLE hand_histories ADD COLUMN table_size VARCHAR(10)")
            db.conn.commit()
            print("[OK] Added table_size column to hand_histories")
        
        # Step 2: Update study_tag_rules table
        print("\nStep 2: Updating study_tag_rules table...")
        
        # Check if new columns already exist in study_tag_rules
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'study_tag_rules' 
                AND column_name IN ('game_class_pattern', 'game_variant_pattern', 'table_size_pattern')
            """)
            existing_rule_columns = [row[0] for row in cur.fetchall()]
        
        # Add new columns to study_tag_rules
        if 'game_class_pattern' not in existing_rule_columns:
            print("Adding game_class_pattern column to study_tag_rules...")
            with db.conn.cursor() as cur:
                cur.execute("ALTER TABLE study_tag_rules ADD COLUMN game_class_pattern VARCHAR(20)")
            db.conn.commit()
            print("[OK] Added game_class_pattern column to study_tag_rules")
        
        if 'game_variant_pattern' not in existing_rule_columns:
            print("Adding game_variant_pattern column to study_tag_rules...")
            with db.conn.cursor() as cur:
                cur.execute("ALTER TABLE study_tag_rules ADD COLUMN game_variant_pattern VARCHAR(20)")
            db.conn.commit()
            print("[OK] Added game_variant_pattern column to study_tag_rules")
        
        if 'table_size_pattern' not in existing_rule_columns:
            print("Adding table_size_pattern column to study_tag_rules...")
            with db.conn.cursor() as cur:
                cur.execute("ALTER TABLE study_tag_rules ADD COLUMN table_size_pattern VARCHAR(10)")
            db.conn.commit()
            print("[OK] Added table_size_pattern column to study_tag_rules")
        
        # Step 3: Drop old columns from study_tag_rules (optional - keep for backward compatibility)
        print("\nStep 3: Checking for old columns to drop...")
        
        # Check if old columns exist
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'study_tag_rules' 
                AND column_name IN ('game_type_pattern', 'num_players')
            """)
            old_columns = [row[0] for row in cur.fetchall()]
        
        if old_columns:
            print(f"Found old columns: {old_columns}")
            print("Note: Old columns are kept for backward compatibility.")
            print("You can manually drop them later if needed:")
            for col in old_columns:
                print(f"  ALTER TABLE study_tag_rules DROP COLUMN {col};")
        
        # Step 4: Verify the changes
        print("\nStep 4: Verifying changes...")
        
        # Check hand_histories columns
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'hand_histories' 
                AND column_name IN ('game_class', 'game_variant', 'table_size')
                ORDER BY column_name
            """)
            hand_columns = cur.fetchall()
        
        print("New hand_histories columns:")
        for col_name, data_type, nullable in hand_columns:
            print(f"  {col_name}: {data_type} (nullable: {nullable})")
        
        # Check study_tag_rules columns
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'study_tag_rules' 
                AND column_name IN ('game_class_pattern', 'game_variant_pattern', 'table_size_pattern')
                ORDER BY column_name
            """)
            rule_columns = cur.fetchall()
        
        print("\nNew study_tag_rules columns:")
        for col_name, data_type, nullable in rule_columns:
            print(f"  {col_name}: {data_type} (nullable: {nullable})")
        
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
    """Rollback the migration by dropping the new columns."""
    print("=== Rollback: Removing Structured Game Format Columns ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Check which columns exist before dropping
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'hand_histories' 
                AND column_name IN ('game_class', 'game_variant', 'table_size')
            """)
            hand_columns = [row[0] for row in cur.fetchall()]
            
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'study_tag_rules' 
                AND column_name IN ('game_class_pattern', 'game_variant_pattern', 'table_size_pattern')
            """)
            rule_columns = [row[0] for row in cur.fetchall()]
        
        if not hand_columns and not rule_columns:
            print("[OK] No columns to rollback. Columns don't exist.")
            return True
        
        # Drop hand_histories columns
        for column in hand_columns:
            print(f"Dropping {column} from hand_histories...")
            with db.conn.cursor() as cur:
                cur.execute(f"ALTER TABLE hand_histories DROP COLUMN {column}")
            print(f"[OK] Dropped {column} column from hand_histories")
        
        # Drop study_tag_rules columns
        for column in rule_columns:
            print(f"Dropping {column} from study_tag_rules...")
            with db.conn.cursor() as cur:
                cur.execute(f"ALTER TABLE study_tag_rules DROP COLUMN {column}")
            print(f"[OK] Dropped {column} column from study_tag_rules")
        
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
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        success = rollback_migration()
    else:
        success = run_migration()
    
    sys.exit(0 if success else 1) 