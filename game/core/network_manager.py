import psycopg2
import logging

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

    def create_user(self, username, password):
        """Create a new user in the database."""
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        self.execute_query(query, (username, password))

    def login_or_register_user(self, username, password):
        """
        Try to login or register a user:
        - If user doesn't exist, create it.
        - If user exists, check password.
        Returns: (success: bool, user_row or error message)
        """
        user = self.get_user(username)
        if user is None:
            # User doesn't exist, register
            self.create_user(username, password)
            user = self.get_user(username)
            return True, user
        else:
            # User exists, verify password
            if user[2] == password:  # Assuming user schema: id, username, password
                return True, user
            else:
                return False, "Incorrect password"

