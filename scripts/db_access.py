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
