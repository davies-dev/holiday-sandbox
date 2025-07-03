#!/usr/bin/env python3
"""
Backfill script to populate the new structured game format columns for all existing hands.
This script extracts game_class, game_variant, and table_size from existing game_type data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def extract_format_details(game_type, number_of_players):
    """
    Extract structured format details from existing game_type and number_of_players.
    This is a fallback implementation until the hpcursor library is updated.
    """
    game_type_lower = game_type.lower() if game_type else ''
    
    # Extract game class
    if 'cash' in game_type_lower:
        game_class = 'cash'
    elif 'tournament' in game_type_lower or 'mtt' in game_type_lower:
        game_class = 'tournament'
    elif 'sitgo' in game_type_lower or 'sng' in game_type_lower:
        game_class = 'tournament'
    elif 'spingo' in game_type_lower:
        game_class = 'tournament'
    else:
        game_class = 'cash'  # Default assumption
    
    # Extract game variant
    if 'zoom' in game_type_lower:
        game_variant = 'zoom'
    else:
        game_variant = 'regular'
    
    # Extract table size
    if '6max' in game_type_lower or '6-max' in game_type_lower:
        table_size = '6-max'
    elif '2max' in game_type_lower or '2-max' in game_type_lower:
        table_size = '2-max'
    elif '9max' in game_type_lower or '9-max' in game_type_lower:
        table_size = '9-max'
    elif '3max' in game_type_lower or '3-max' in game_type_lower:
        table_size = '3-max'
    elif 'heads' in game_type_lower or 'hu' in game_type_lower:
        table_size = '2-max'
    else:
        # Try to infer from number_of_players
        if number_of_players == 2:
            table_size = '2-max'
        elif number_of_players == 3:
            table_size = '3-max'
        elif number_of_players == 6:
            table_size = '6-max'
        elif number_of_players == 9:
            table_size = '9-max'
        else:
            table_size = '6-max'  # Default assumption
    
    return {
        'game_class': game_class,
        'game_variant': game_variant,
        'table_size': table_size
    }

def run_backfill():
    """Run the backfill process to populate structured format columns."""
    print("=== Starting Backfill for Structured Game Formats ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Check if new columns exist
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'hand_histories' 
                AND column_name IN ('game_class', 'game_variant', 'table_size')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]
        
        if not existing_columns:
            print("[ERROR] New structured format columns not found in hand_histories table.")
            print("Please run the migration script first:")
            print("python database_setup/schema/add_structured_format_columns.py")
            return False
        
        # Find hands that need updating
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT id, game_type, number_of_players 
                FROM hand_histories 
                WHERE game_class IS NULL OR game_variant IS NULL OR table_size IS NULL
            """)
            hands_to_process = cur.fetchall()
        
        if not hands_to_process:
            print("[OK] No hands to update. Backfill may already be complete.")
            return True
        
        print(f"Found {len(hands_to_process)} hands to update.")
        
        # Process hands in batches
        batch_size = 1000
        total_updated = 0
        
        for i in range(0, len(hands_to_process), batch_size):
            batch = hands_to_process[i:i + batch_size]
            updates = []
            
            for hand_id, game_type, number_of_players in batch:
                format_details = extract_format_details(game_type, number_of_players)
                updates.append((
                    format_details['game_class'],
                    format_details['game_variant'], 
                    format_details['table_size'],
                    hand_id
                ))
            
            # Update batch
            with db.conn.cursor() as cur:
                from psycopg2.extras import execute_batch
                sql_update = """
                    UPDATE hand_histories 
                    SET game_class = %s, game_variant = %s, table_size = %s 
                    WHERE id = %s
                """
                execute_batch(cur, sql_update, updates)
                db.conn.commit()
            
            total_updated += len(batch)
            print(f"Updated {total_updated}/{len(hands_to_process)} hands...")
        
        # Verify the update
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) as total_hands,
                       COUNT(game_class) as with_game_class,
                       COUNT(game_variant) as with_game_variant,
                       COUNT(table_size) as with_table_size
                FROM hand_histories
            """)
            result = cur.fetchone()
            total_hands, with_game_class, with_game_variant, with_table_size = result
        
        print(f"\n=== Backfill Results ===")
        print(f"Total hands in database: {total_hands}")
        print(f"Hands with game_class: {with_game_class}")
        print(f"Hands with game_variant: {with_game_variant}")
        print(f"Hands with table_size: {with_table_size}")
        
        # Show some sample data
        print(f"\n=== Sample Data ===")
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT game_type, game_class, game_variant, table_size, number_of_players
                FROM hand_histories 
                WHERE game_class IS NOT NULL
                LIMIT 10
            """)
            samples = cur.fetchall()
            
            for game_type, game_class, game_variant, table_size, num_players in samples:
                print(f"  {game_type} -> {game_class}/{game_variant}/{table_size} ({num_players} players)")
        
        print(f"\n[OK] Backfill completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Backfill failed: {e}")
        if db and db.conn:
            db.conn.rollback()
        return False
    finally:
        if db:
            db.close()

def show_statistics():
    """Show statistics about the current data."""
    print("=== Current Database Statistics ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Check if new columns exist
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'hand_histories' 
                AND column_name IN ('game_class', 'game_variant', 'table_size')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]
        
        if not existing_columns:
            print("[ERROR] New structured format columns not found.")
            return False
        
        # Show current game types
        print("\nCurrent game_type values:")
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT game_type, COUNT(*) as count
                FROM hand_histories 
                WHERE game_type IS NOT NULL
                GROUP BY game_type
                ORDER BY count DESC
                LIMIT 10
            """)
            game_types = cur.fetchall()
            
            for game_type, count in game_types:
                print(f"  '{game_type}': {count} hands")
        
        # Show structured format breakdown
        print(f"\nStructured format breakdown:")
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT game_class, game_variant, table_size, COUNT(*) as count
                FROM hand_histories 
                WHERE game_class IS NOT NULL
                GROUP BY game_class, game_variant, table_size
                ORDER BY count DESC
            """)
            formats = cur.fetchall()
            
            for game_class, game_variant, table_size, count in formats:
                print(f"  {game_class}/{game_variant}/{table_size}: {count} hands")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to get statistics: {e}")
        return False
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--stats":
            success = show_statistics()
        else:
            print("Usage: python backfill_formats.py [--stats]")
            print("  --stats: Show current database statistics")
            sys.exit(1)
    else:
        success = run_backfill()
    
    sys.exit(0 if success else 1) 