import psycopg2
import logging
import json

class NetworkManager:
    
    def __init__(self, db_config = {'dbname':'game', 'user':'game_user', 'password':'password', 'host':'localhost','port':'5432'}):
        self.db_config = db_config
        self.connection = None
        self.cursor = None
        self._connect_to_db()

    def _connect_to_db(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor()
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

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
    
    def create_preference(self, uid, uname):
        settings = {
                "USERID": str(uid),
                "PLAYERNAME": str(uname),
                "LEVEL": 1,
                "MASTER_VOL": 0.06,
                "MUSIC_VOL": 0.48,
                "SFX_VOL": 0.48,
                "CONTROLS": {
                    "MOVE_LEFT": 97,
                    "MOVE_RIGHT": 100,
                    "JUMP": 119,
                    "SHOOT": 32
                    }
            }
        self.execute_query("INSERT INTO public.preferences (user_id, settings) VALUES (%s, %s)", (uid, json.dumps(settings),))
        
    def create_player_stats(self, uid):
        self.execute_query("INSERT INTO public.player_stats (user_id) VALUES (%s)", (uid,))
        
    def create_player_levels(self, uid):
        self.execute_query("INSERT INTO public.player_levels (user_id) VALUES (%s)", (uid,))
        
    def create_player_coins(self, uid):
        self.execute_query("INSERT INTO public.player_coins (user_id) VALUES (%s)", (uid,))

    def login_or_register_user(self, username, password):
        user = self.get_user(username)
        if user is None:
            self.create_user(username, password)
            user = self.get_user(username)
            self.create_preference(user[0], user[1])
            self.create_player_stats(user[0])
            self.create_player_levels(user[0])
            self.create_player_coins(user[0])
            return True, user
        else:
            if user[2] == password:
                return True, user
            else:
                return False, "Incorrect password"

    def get_settings(self, uid):
        query = "SELECT settings FROM public.preferences WHERE user_id=%s"
        return self.fetch_one(query, (uid,))
    
    def update_settings(self, uid, settings):
        query = "UPDATE public.preferences SET settings=%s WHERE user_id=%s"
        return self.execute_query(query, (json.dumps(settings), uid,))
    
    def get_user(self, username):
        query = "SELECT * FROM users WHERE username = %s"
        return self.fetch_one(query, (username,))

    def create_user(self, username, password):
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        self.execute_query(query, (username, password))

        
        
        
        
        
        
        
        
        
        
