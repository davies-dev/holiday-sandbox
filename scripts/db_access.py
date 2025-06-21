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
