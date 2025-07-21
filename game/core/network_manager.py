import psycopg2
import logging
class NetworkManager:
    def __init__(self, db_config):
        """
        Initialize the NetworkManager with the database connection parameters.
        :param db_config: Dictionary with keys 'dbname', 'user', 'password', 'host', 'port'
        """
        self.db_config = db_config
        self.connection = None
        self.cursor = None
        self._connect_to_db()

    def _connect_to_db(self):
        """Establish connection to the PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            print("Connected to the database successfully.")
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")

    def execute_query(self, query, params=None):
        """Execute a single query (INSERT, UPDATE, DELETE)."""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            self.connection.rollback()

    def fetch_one(self, query, params=None):
        """Fetch one record from the database."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return None

    def fetch_all(self, query, params=None):
        """Fetch all records from the database."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return []

    def get_user(self, username):
        """Get a user by username."""
        query = "SELECT * FROM users WHERE username = %s"
        return self.fetch_one(query, (username,))


