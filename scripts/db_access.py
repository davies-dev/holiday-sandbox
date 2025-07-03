import psycopg2
from psycopg2 import sql, OperationalError
import re
import sys
import os
import fnmatch
import json

# Add parent directory to path to import board_analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from board_analyzer import analyze_board

class DatabaseAccess:
    """
    A simple database access class that encapsulates the connection and
    provides methods for querying hand histories.
    """
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Initializes a new database connection.
        """
        try:
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            print("Database connection established.")
        except OperationalError as e:
            print("Error connecting to the database:", e)
            self.conn = None

    def retrieve_hand_histories(self, limit: int = 100000):
        """
        Retrieves hand histories from the database, ordering by the creation time (descending).

        Args:
            limit (int): Maximum number of rows to retrieve.

        Returns:
            list: A list of rows representing hand histories.
        """
        if not self.conn:
            print("No database connection.")
            return []

        try:
            with self.conn.cursor() as cursor:
                query = sql.SQL("SELECT * FROM hand_histories ORDER BY created_at DESC LIMIT %s")
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
            return rows
        except Exception as e:
            print("Error retrieving hand histories:", e)
            return []

    def close(self):
        """
        Closes the database connection.
        """
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    # GTO+ Mapping Methods
    def insert_gto_mapping(self, state_name, game_type, file_path, description):
        """Insert a GTO+ mapping into the database"""
        if not self.conn:
            print("No database connection.")
            return False
        
        query = """
            INSERT INTO gto_mappings (state_name, game_type, gto_file_path, description)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (state_name, game_type) 
            DO UPDATE SET gto_file_path = EXCLUDED.gto_file_path, 
                          description = EXCLUDED.description
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (state_name, game_type, file_path, description))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting GTO+ mapping: {e}")
            self.conn.rollback()
            return False

    def get_gto_file_path(self, state_name, game_type):
        """Get GTO+ file path for a given state and game type"""
        if not self.conn:
            print("No database connection.")
            return None
        
        query = "SELECT gto_file_path FROM gto_mappings WHERE state_name = %s AND game_type = %s"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (state_name, game_type))
                result = cur.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting GTO+ file path: {e}")
            return None

    def get_all_gto_mappings(self):
        """Get all GTO+ mappings"""
        if not self.conn:
            print("No database connection.")
            return []
        
        query = "SELECT state_name, game_type, gto_file_path, description FROM gto_mappings ORDER BY state_name"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
            return [
                {
                    'state_name': row[0],
                    'game_type': row[1], 
                    'gto_file_path': row[2],
                    'description': row[3]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error getting all GTO+ mappings: {e}")
            return []

    def delete_gto_mapping(self, state_name, game_type):
        """Delete a GTO+ mapping"""
        if not self.conn:
            print("No database connection.")
            return False
        
        query = "DELETE FROM gto_mappings WHERE state_name = %s AND game_type = %s"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (state_name, game_type))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting GTO+ mapping: {e}")
            self.conn.rollback()
            return False

    def get_game_types(self):
        """Get all unique game types from gto_mappings"""
        if not self.conn:
            print("No database connection.")
            return []
        
        query = "SELECT DISTINCT game_type FROM gto_mappings ORDER BY game_type"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"Error getting game types: {e}")
            return []

    # Review System Methods
    def get_or_create_review_data(self, hand_id):
        """Fetches review data for a hand_id. If no entry exists, it creates one."""
        if not self.conn:
            print("No database connection.")
            return None
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT hand_id, review_status FROM hand_reviews WHERE hand_id = %s", (hand_id,))
                data = cur.fetchone()
                if data:
                    return {"hand_id": data[0], "review_status": data[1]}
                else:
                    cur.execute("INSERT INTO hand_reviews (hand_id) VALUES (%s) RETURNING hand_id, review_status", (hand_id,))
                    self.conn.commit()
                    new_data = cur.fetchone()
                    return {"hand_id": new_data[0], "review_status": new_data[1]}
        except Exception as e:
            print(f"Error getting or creating review data: {e}")
            self.conn.rollback()
            return None

    def update_review_status(self, hand_id, status):
        """Updates the review_status for a given hand_id."""
        # Ensure the review entry exists
        self.get_or_create_review_data(hand_id)
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE hand_reviews SET review_status = %s, last_updated = NOW() WHERE hand_id = %s",
                (status, hand_id)
            )
        self.conn.commit()
        print(f"Updated hand {hand_id} status to {status}")

    def add_note_for_hand(self, hand_id, file_path):
        """Adds a new note record for a given hand."""
        if not self.conn:
            print("No database connection.")
            return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO hand_notes (hand_id, note_file_path) VALUES (%s, %s)", (hand_id, file_path))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding note for hand: {e}")
            self.conn.rollback()
            return False

    def get_notes_for_hand(self, hand_id):
        """Retrieves all notes for a given hand, ordered by creation date."""
        if not self.conn:
            print("No database connection.")
            return []
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT note_file_path, created_at FROM hand_notes WHERE hand_id = %s ORDER BY created_at DESC",
                    (hand_id,)
                )
                return cur.fetchall()
        except Exception as e:
            print(f"Error getting notes for hand: {e}")
            return []

    def delete_note_for_hand(self, hand_id, file_path):
        """Deletes a specific note for a hand"""
        if not self.conn:
            print("No database connection.")
            return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM hand_notes WHERE hand_id = %s AND note_file_path = %s", (hand_id, file_path))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting note: {e}")
            self.conn.rollback()
            return False

    def get_all_study_documents(self):
        """Retrieves all study documents from the library."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, title, file_path FROM study_documents ORDER BY title")
            return cur.fetchall()

    def add_study_document(self, title, file_path, source_info=''):
        """Adds a new study document to the library."""
        with self.conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO study_documents (title, file_path, source_info) VALUES (%s, %s, %s)",
                    (title, file_path, source_info)
                )
                self.conn.commit()
                return True
            except Exception as e:
                self.conn.rollback()
                print(f"Error adding study document: {e}")
                return False

    # Tag Management Methods
    def create_tag(self, tag_name, description=''):
        """Creates a new tag in the study_tags table."""
        if not self.conn:
            print("No database connection.")
            return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO study_tags (tag_name, description) VALUES (%s, %s)", (tag_name, description))
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating tag: {e}")
            return False

    def get_all_tags(self):
        """Retrieves all tags from the study_tags table."""
        if not self.conn:
            print("No database connection.")
            return []
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, tag_name FROM study_tags ORDER BY tag_name")
                return cur.fetchall()
        except Exception as e:
            print(f"Error getting all tags: {e}")
            return []

    def get_tags_for_document(self, document_id):
        """Retrieves all tags assigned to a specific document."""
        if not self.conn:
            print("No database connection.")
            return []
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT t.id, t.tag_name
                    FROM study_tags t
                    JOIN study_document_tags sdt ON t.id = sdt.tag_id
                    WHERE sdt.document_id = %s
                    ORDER BY t.tag_name
                """, (document_id,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error getting tags for document: {e}")
            return []

    def assign_tag_to_document(self, document_id, tag_id):
        """Creates a link between a document and a tag."""
        if not self.conn:
            print("No database connection.")
            return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO study_document_tags (document_id, tag_id) VALUES (%s, %s)", (document_id, tag_id))
                self.conn.commit()
                return True
        except Exception as e:  # This will fail if the link already exists
            self.conn.rollback()
            print(f"Error assigning tag: {e}")
            return False

    def remove_tag_from_document(self, document_id, tag_id):
        """Removes a link between a document and a tag."""
        if not self.conn:
            print("No database connection.")
            return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM study_document_tags WHERE document_id = %s AND tag_id = %s", (document_id, tag_id))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error removing tag from document: {e}")
            self.conn.rollback()
            return False

    # Rule Management Methods
    def get_rules_for_tag(self, tag_id):
        """Retrieves all rules for a given tag_id."""
        if not self.conn:
            print("No database connection.")
            return []
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT id, rule_description FROM study_tag_rules WHERE tag_id = %s ORDER BY id",
                    (tag_id,)
                )
                return cur.fetchall()
        except Exception as e:
            print(f"Error getting rules for tag: {e}")
            return []

    def get_rule_details(self, rule_id):
        """Retrieves the full details for a single rule."""
        if not self.conn:
            print("No database connection.")
            return None
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM study_tag_rules WHERE id = %s", (rule_id,))
                data = cur.fetchone()
                if not data: 
                    return None
                # Columns: id, tag_id, desc, pf, f, t, r, created_at, board_texture, min_stack, max_stack, 
                # game_type_pattern, num_players, game_class_pattern, game_variant_pattern, table_size_pattern
                return {
                    "id": data[0], 
                    "tag_id": data[1], 
                    "rule_description": data[2],
                    "pf_pattern": data[3] if data[3] else "", 
                    "flop_pattern": data[4] if data[4] else "",
                    "turn_pattern": data[5] if data[5] else "", 
                    "river_pattern": data[6] if data[6] else "",
                    "board_texture": data[8] if data[8] else "",
                    "min_stack_bb": data[9],
                    "max_stack_bb": data[10],
                    "game_type_pattern": data[11] if len(data) > 11 and data[11] else "",
                    "num_players": data[12] if len(data) > 12 else None,
                    "game_class_pattern": data[13] if len(data) > 13 and data[13] else "",
                    "game_variant_pattern": data[14] if len(data) > 14 and data[14] else "",
                    "table_size_pattern": data[15] if len(data) > 15 and data[15] else ""
                }
        except Exception as e:
            print(f"Error getting rule details: {e}")
            return None

    def save_rule(self, rule_data):
        """Saves a rule to the database. Updates if ID exists, otherwise inserts."""
        if not self.conn:
            print("No database connection.")
            return False
        
        try:
            with self.conn.cursor() as cur:
                rule_id = rule_data.get("id")
                if rule_id:  # Update existing rule
                    cur.execute("""
                        UPDATE study_tag_rules SET rule_description=%s, pf_action_seq_pattern=%s,
                        flop_action_seq_pattern=%s, turn_action_seq_pattern=%s, river_action_seq_pattern=%s,
                        board_texture_pattern=%s, min_effective_stack_bb=%s, max_effective_stack_bb=%s,
                        game_type_pattern=%s, num_players=%s, game_class_pattern=%s, game_variant_pattern=%s, table_size_pattern=%s WHERE id=%s
                    """, (
                        rule_data['rule_description'], rule_data['pf_pattern'], rule_data['flop_pattern'],
                        rule_data['turn_pattern'], rule_data['river_pattern'], rule_data.get('board_texture', ''),
                        rule_data.get('min_stack_bb'), rule_data.get('max_stack_bb'),
                        rule_data.get('game_type_pattern', ''), rule_data.get('num_players'),
                        rule_data.get('game_class_pattern', ''), rule_data.get('game_variant_pattern', ''),
                        rule_data.get('table_size_pattern', ''), rule_id))
                else:  # Insert new rule
                    cur.execute("""
                        INSERT INTO study_tag_rules (tag_id, rule_description, pf_action_seq_pattern,
                        flop_action_seq_pattern, turn_action_seq_pattern, river_action_seq_pattern, board_texture_pattern,
                        min_effective_stack_bb, max_effective_stack_bb, game_type_pattern, num_players,
                        game_class_pattern, game_variant_pattern, table_size_pattern)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        rule_data['tag_id'], rule_data['rule_description'], rule_data['pf_pattern'],
                        rule_data['flop_pattern'], rule_data['turn_pattern'], rule_data['river_pattern'], 
                        rule_data.get('board_texture', ''), rule_data.get('min_stack_bb'), rule_data.get('max_stack_bb'),
                        rule_data.get('game_type_pattern', ''), rule_data.get('num_players'),
                        rule_data.get('game_class_pattern', ''), rule_data.get('game_variant_pattern', ''),
                        rule_data.get('table_size_pattern', '')))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error saving rule: {e}")
            self.conn.rollback()
            return False

    def delete_rule(self, rule_id):
        """Deletes a rule from the database."""
        if not self.conn:
            print("No database connection.")
            return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM study_tag_rules WHERE id = %s", (rule_id,))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting rule: {e}")
            self.conn.rollback()
            return False

    # Rule Matching Methods
    def _check_rule_match(self, rule, hh_data):
        """
        Checks if a hand's data matches a single rule's patterns, now including board texture and stack depth.
        """
        # --- Action Sequence Matching (existing logic) ---
        patterns = {
            "preflop": rule.get('pf_pattern'),
            "flop": rule.get('flop_pattern'),
            "turn": rule.get('turn_pattern'),
            "river": rule.get('river_pattern')
        }
        for street, pattern in patterns.items():
            if not pattern:  # If pattern is None or empty, it's a wildcard
                continue

            action_seq = hh_data.get_simple_action_sequence(street)
            if not re.search(pattern, action_seq):
                return False  # This rule does not match

        # --- Board Texture Matching ---
        texture_pattern = rule.get('board_texture')
        if texture_pattern:
            flop_cards = []
            if hasattr(hh_data, 'flop_cards') and hh_data.flop_cards:
                flop_cards = hh_data.flop_cards
            elif hasattr(hh_data, 'raw_text') and hh_data.raw_text:
                flop_match = re.search(r'\*\*\* FLOP \*\*\* \[([^\]]+)\]', hh_data.raw_text)
                if flop_match:
                    flop_text = flop_match.group(1)
                    flop_cards = [card.strip() for card in flop_text.split()]
            if not flop_cards:
                return False
            board_textures = analyze_board(flop_cards)
            required_textures = {t.strip() for t in texture_pattern.split(',')}
            if not required_textures.issubset(board_textures):
                return False

        # --- Stack Depth Matching ---
        min_stack = rule.get('min_stack_bb')
        max_stack = rule.get('max_stack_bb')
        if min_stack is not None or max_stack is not None:
            effective_stack = getattr(hh_data, 'effective_stack_bb', None)
            if effective_stack is None:
                return False  # Cannot match a stack rule if hand data is missing
            if min_stack is not None and effective_stack < min_stack:
                return False
            if max_stack is not None and effective_stack > max_stack:
                return False
        # --- Structured Game Format Matching ---
        # Get format details from hand data (fallback to old method if get_format_details not available)
        try:
            if hasattr(hh_data, 'get_format_details'):
                details = hh_data.get_format_details()
                hand_game_class = details.get('game_class', '')
                hand_game_variant = details.get('game_variant', '')
                hand_table_size = details.get('table_size', '')
            else:
                # Fallback: try to extract from existing game_type
                hand_game_type = getattr(hh_data, 'game_type', '')
                hand_game_class = 'cash' if 'cash' in hand_game_type.lower() else 'tournament' if 'tournament' in hand_game_type.lower() else ''
                hand_game_variant = 'zoom' if 'zoom' in hand_game_type.lower() else 'regular'
                hand_table_size = '6-max' if '6max' in hand_game_type.lower() else '2-max' if '2max' in hand_game_type.lower() else '9-max' if '9max' in hand_game_type.lower() else ''
        except Exception as e:
            print(f"DEBUG: Error getting format details: {e}")
            hand_game_class = ''
            hand_game_variant = ''
            hand_table_size = ''

        # Check Game Class
        class_pattern = rule.get('game_class_pattern')
        if class_pattern:
            print(f"DEBUG: Game class matching - pattern: '{class_pattern}', hand game_class: '{hand_game_class}'")
            if not fnmatch.fnmatch(hand_game_class, class_pattern):
                print(f"DEBUG: Game class pattern '{class_pattern}' did NOT match hand game_class '{hand_game_class}'")
                return False
            else:
                print(f"DEBUG: Game class pattern '{class_pattern}' matched hand game_class '{hand_game_class}'")

        # Check Game Variant
        variant_pattern = rule.get('game_variant_pattern')
        if variant_pattern:
            print(f"DEBUG: Game variant matching - pattern: '{variant_pattern}', hand game_variant: '{hand_game_variant}'")
            if not fnmatch.fnmatch(hand_game_variant, variant_pattern):
                print(f"DEBUG: Game variant pattern '{variant_pattern}' did NOT match hand game_variant '{hand_game_variant}'")
                return False
            else:
                print(f"DEBUG: Game variant pattern '{variant_pattern}' matched hand game_variant '{hand_game_variant}'")

        # Check Table Size
        size_pattern = rule.get('table_size_pattern')
        if size_pattern:
            print(f"DEBUG: Table size matching - pattern: '{size_pattern}', hand table_size: '{hand_table_size}'")
            if not fnmatch.fnmatch(hand_table_size, size_pattern):
                print(f"DEBUG: Table size pattern '{size_pattern}' did NOT match hand table_size '{hand_table_size}'")
                return False
            else:
                print(f"DEBUG: Table size pattern '{size_pattern}' matched hand table_size '{hand_table_size}'")

        # --- Legacy Game Type Pattern Matching (for backward compatibility) ---
        gt_pattern = rule.get('game_type_pattern')
        if gt_pattern:
            hand_game_type = getattr(hh_data, 'game_type', '')
            print(f"DEBUG: Legacy game type matching - pattern: '{gt_pattern}', hand game_type: '{hand_game_type}'")
            if not fnmatch.fnmatch(hand_game_type, gt_pattern):
                print(f"DEBUG: Legacy game type pattern '{gt_pattern}' did NOT match hand game_type '{hand_game_type}'")
                return False
            else:
                print(f"DEBUG: Legacy game type pattern '{gt_pattern}' matched hand game_type '{hand_game_type}'")

        # --- Legacy Player Count Matching (for backward compatibility) ---
        rule_num_players = rule.get('num_players')
        if rule_num_players is not None:
            hand_num_players = getattr(hh_data, 'number_of_players', None)
            print(f"DEBUG: Legacy player count matching - rule expects: {rule_num_players}, hand has: {hand_num_players}")
            if hand_num_players != rule_num_players:
                print(f"DEBUG: Legacy player count mismatch - expected {rule_num_players}, got {hand_num_players}")
                return False
            else:
                print(f"DEBUG: Legacy player count matched - both are {rule_num_players}")

        return True  # All conditions passed

    def find_relevant_study_documents(self, hh_data):
        """
        Finds all study documents with tags whose rules match the given hand data.
        """
        if not self.conn:
            print("No database connection.")
            return []
        
        try:
            # 1. Fetch all rules from the database
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, tag_id, rule_description, pf_action_seq_pattern, 
                           flop_action_seq_pattern, turn_action_seq_pattern, river_action_seq_pattern,
                           board_texture_pattern, min_effective_stack_bb, max_effective_stack_bb,
                           game_type_pattern, num_players, game_class_pattern, game_variant_pattern, table_size_pattern
                    FROM study_tag_rules
                """)
                all_rules_raw = cur.fetchall()

            all_rules = [{
                "id": r[0], 
                "tag_id": r[1], 
                "rule_description": r[2], 
                "pf_pattern": r[3], 
                "flop_pattern": r[4], 
                "turn_pattern": r[5], 
                "river_pattern": r[6],
                "board_texture": r[7],  # board_texture_pattern column (index 7 in SELECT query)
                "min_stack_bb": r[8],   # min_effective_stack_bb
                "max_stack_bb": r[9],   # max_effective_stack_bb
                "game_type_pattern": r[10] if len(r) > 10 and r[10] else "",  # game_type_pattern
                "num_players": r[11] if len(r) > 11 else None,  # num_players
                "game_class_pattern": r[12] if len(r) > 12 and r[12] else "",  # game_class_pattern
                "game_variant_pattern": r[13] if len(r) > 13 and r[13] else "",  # game_variant_pattern
                "table_size_pattern": r[14] if len(r) > 14 and r[14] else "",  # table_size_pattern
            } for r in all_rules_raw]

            # 2. Find all tags where at least one rule matches
            matching_tag_ids = set()
            for rule in all_rules:
                # Debug: Print rule dict for rules with game type or player count constraints
                if rule.get("game_type_pattern") or rule.get("num_players") is not None:
                    print(f"DEBUG: Checking rule {rule['id']} - game_type_pattern: '{rule.get('game_type_pattern')}', num_players: {rule.get('num_players')}")
                    print(f"DEBUG: Rule dict: {rule}")
                if self._check_rule_match(rule, hh_data):
                    matching_tag_ids.add(rule['tag_id'])
                    print(f"DEBUG: Rule {rule['id']} MATCHED for tag {rule['tag_id']}")
                else:
                    print(f"DEBUG: Rule {rule['id']} did NOT match")

            if not matching_tag_ids:
                return []

            # 3. Find all documents associated with the matching tags
            with self.conn.cursor() as cur:
                # The %s in an IN clause requires a tuple
                tags_tuple = tuple(matching_tag_ids)
                cur.execute("""
                    SELECT DISTINCT d.id, d.title, d.file_path
                    FROM study_documents d
                    JOIN study_document_tags sdt ON d.id = sdt.document_id
                    WHERE sdt.tag_id IN %s
                """, (tags_tuple,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error finding relevant study documents: {e}")
            return []

    # --- New Spot System Methods ---
    def find_spot_for_hand(self, hh_data):
        """
        Finds a defined spot that matches the given hand data.
        Python-side rule matching: for each spot, all its rules must match the hand.
        Currently only supports preflop action sequence, but easily extensible.
        """
        pf_seq = hh_data.get_simple_action_sequence("preflop")
        # You can add more hand properties as needed

        with self.conn.cursor() as cur:
            # Get all spots and their rules
            cur.execute("""
                SELECT p.id, p.spot_name, p.description, r.condition_type, r.condition_params
                FROM poker_spots p
                JOIN spot_rules r ON p.id = r.spot_id
                ORDER BY p.id
            """)
            rows = cur.fetchall()

        # Group rules by spot
        from collections import defaultdict
        spot_rules = defaultdict(list)
        spot_info = {}
        for spot_id, spot_name, description, cond_type, cond_params in rows:
            spot_rules[spot_id].append((cond_type, cond_params))
            spot_info[spot_id] = {"spot_name": spot_name, "description": description, "id": spot_id}

        # Try to match each spot
        for spot_id, rules in spot_rules.items():
            all_match = True
            for cond_type, cond_params in rules:
                if isinstance(cond_params, str):
                    params = json.loads(cond_params)
                else:
                    params = cond_params
                if cond_type == 'action_sequence':
                    # Only preflop for now
                    if params.get("street") == "preflop":
                        if params.get("pattern") != pf_seq:
                            all_match = False
                            break
                # Add more condition types as needed
            if all_match:
                return spot_info[spot_id]
        return None

    def get_documents_for_spot(self, spot_id):
        """Retrieves all linked documents for a given spot_id."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT d.id, d.title, d.file_path, l.is_default
                FROM study_documents d
                JOIN spot_document_links l ON d.id = l.document_id
                WHERE l.spot_id = %s
                ORDER BY l.is_default DESC, d.title
                """,
                (spot_id,)
            )
            return [{"id": r[0], "title": r[1], "file_path": r[2], "is_default": r[3]} for r in cur.fetchall()]

    def create_spot(self, spot_name, description, source, hh_data):
        """Creates a new spot and its initial rule in the database."""
        pf_seq = hh_data.get_simple_action_sequence("preflop")
        try:
            with self.conn.cursor() as cur:
                # Insert the main spot definition
                cur.execute(
                    """
                    INSERT INTO poker_spots (spot_name, description, source)
                    VALUES (%s, %s, %s) RETURNING id
                    """,
                    (spot_name, description, source)
                )
                spot_id = cur.fetchone()[0]

                # Insert the action_sequence rule
                rule_params = json.dumps({"street": "preflop", "pattern": pf_seq})
                cur.execute(
                    "INSERT INTO spot_rules (spot_id, condition_type, condition_params) VALUES (%s, %s, %s)",
                    (spot_id, 'action_sequence', rule_params)
                )
                self.conn.commit()
                return spot_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating spot: {e}")
            return None

    def get_spots_for_dropdowns(self):
        """
        Fetches all spots that are defined by a single action_sequence rule,
        categorized by street. This is perfect for populating the UI dropdowns.
        """
        spots_by_street = {"preflop": {}, "postflop": {}}
        with self.conn.cursor() as cur:
            # This query finds spots that have exactly ONE rule, and that rule
            # is of type 'action_sequence'.
            cur.execute("""
                SELECT s.spot_name, r.condition_params->>'pattern' as sql_pattern, r.condition_params->>'street' as street
                FROM poker_spots s
                JOIN spot_rules r ON s.id = r.spot_id
                WHERE r.id IN (
                    SELECT rule_id FROM (
                        SELECT spot_id, COUNT(*) as rule_count, MIN(id) as rule_id
                        FROM spot_rules
                        GROUP BY spot_id
                        HAVING COUNT(*) = 1
                    ) as single_rules
                ) AND r.condition_type = 'action_sequence'
            """)
            for spot_name, pattern, street in cur.fetchall():
                if street in spots_by_street:
                    spots_by_street[street][spot_name] = pattern
                # Since postflop patterns can apply to F, T, or R, we add them to a general key
                elif street in ['flop', 'turn', 'river']:
                     spots_by_street["postflop"][spot_name] = pattern

        return spots_by_street
