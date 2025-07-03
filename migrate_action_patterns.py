# migrate_action_patterns.py
import json
import sys
import os

# Ensure scripts/ is in the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from db_access import DatabaseAccess
from config import DB_PARAMS

def run_migration():
    db = DatabaseAccess(**DB_PARAMS)
    print("Migrating legacy action_patterns into poker_spots...")

    with db.conn.cursor() as cur:
        # Get all postflop patterns from the old table
        cur.execute("SELECT pattern_name, sql_pattern, description, applies_to FROM action_patterns")
        legacy_patterns = cur.fetchall()

        for name, pattern, desc, street in legacy_patterns:
            # 1. Create the main spot entry
            cur.execute(
                """
                INSERT INTO poker_spots (spot_name, description, source)
                VALUES (%s, %s, %s) ON CONFLICT (spot_name) DO NOTHING
                RETURNING id
                """,
                (name, desc or f"Legacy pattern for {street}", "Legacy Action Pattern")
            )
            spot_id_result = cur.fetchone()
            if not spot_id_result:
                print(f"Spot '{name}' already existed. Skipping.")
                continue
            
            spot_id = spot_id_result[0]

            # 2. Create the corresponding rule for this spot
            # The 'applies_to' column tells us which street the pattern is for
            rule_params = {
                "street": street,
                "pattern": pattern
            }
            cur.execute(
                """
                INSERT INTO spot_rules (spot_id, condition_type, condition_params)
                VALUES (%s, %s, %s)
                """,
                (spot_id, 'action_sequence', json.dumps(rule_params))
            )
    
    db.conn.commit()
    db.close()
    print("Migration of action_patterns complete.")

if __name__ == "__main__":
    run_migration() 