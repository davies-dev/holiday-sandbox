import psycopg2
from psycopg2 import sql, OperationalError

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
