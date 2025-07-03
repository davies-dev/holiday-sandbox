# migrate_spots.py
import json
import sys
import os

# Ensure scripts/ is in the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from db_access import DatabaseAccess
from config import DB_PARAMS

def run_migration():
    db = DatabaseAccess(**DB_PARAMS)
    print("Starting migration of legacy spots and GTO mappings...")

    with db.conn.cursor() as cur:
        # 1. Read from hand_state_legacy and populate poker_spots & spot_rules
        print("Migrating spots from hand_state_legacy...")
        cur.execute("SELECT state_name, state_value, game_type FROM hand_state_legacy WHERE state_type = 'preflop'")
        legacy_spots = cur.fetchall()

        for spot_name, pf_action_seq, game_type in legacy_spots:
            # Insert into the main spots table
            cur.execute(
                """
                INSERT INTO poker_spots (spot_name, description, source)
                VALUES (%s, %s, %s) ON CONFLICT (spot_name) DO NOTHING
                RETURNING id
                """,
                (spot_name, f"Legacy MPT Spot #{spot_name}", "Modern Poker Theory")
            )
            spot_id_result = cur.fetchone()
            if not spot_id_result:
                # Try to fetch the id if already existed
                cur.execute("SELECT id FROM poker_spots WHERE spot_name = %s", (spot_name,))
                spot_id_result = cur.fetchone()
                if not spot_id_result:
                    print(f"Failed to get spot_id for '{spot_name}', skipping.")
                    continue
            spot_id = spot_id_result[0]

            # Insert the corresponding rule for this spot
            rule_params = {
                "street": "preflop",
                "pattern": pf_action_seq
            }
            cur.execute(
                """
                INSERT INTO spot_rules (spot_id, condition_type, condition_params)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (spot_id, 'action_sequence', json.dumps(rule_params))
            )

        # 2. Read from gto_mappings_legacy and link them as documents
        print("Migrating and linking GTO files from gto_mappings_legacy...")
        cur.execute("SELECT state_name, gto_file_path, description FROM gto_mappings_legacy")
        legacy_mappings = cur.fetchall()

        for spot_name, file_path, description in legacy_mappings:
            # Add the GTO file to the study_documents library
            cur.execute(
                """
                INSERT INTO study_documents (title, file_path, source_info)
                VALUES (%s, %s, %s) ON CONFLICT (file_path) DO UPDATE SET title = EXCLUDED.title
                RETURNING id
                """,
                (description or f"GTO+ for {spot_name}", file_path, "Legacy GTO Import")
            )
            doc_id = cur.fetchone()[0]

            # Find the spot_id and link them
            cur.execute("SELECT id FROM poker_spots WHERE spot_name = %s", (spot_name,))
            spot_id_result = cur.fetchone()
            if spot_id_result:
                spot_id = spot_id_result[0]
                cur.execute(
                    """
                    INSERT INTO spot_document_links (spot_id, document_id, is_default)
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
                    """,
                    (spot_id, doc_id, True)
                )

    db.conn.commit()
    db.close()
    print("Migration complete! The new 'poker_spots' and 'spot_rules' tables are populated.")
    print("You can drop the '_legacy' tables once you confirm the data is correct.")

if __name__ == "__main__":
    run_migration() 