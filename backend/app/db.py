import sqlite3
import os

class DatabaseManager:
    _instance = None

    def __new__(cls, db_path="lab_booking.db"):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.db_path = db_path
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        conn = self.get_connection()
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.close()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def run_schema(self, schema_file_path="backend/db/schema.sql"):
        if not os.path.exists(schema_file_path):
            schema_file_path = os.path.join(os.path.dirname(__file__), "..", "db", "schema.sql")
        
        if os.path.exists(schema_file_path):
            with open(schema_file_path, "r", encoding="utf-8") as f:
                sql = f.read()

            conn = self.get_connection()
            conn.executescript(sql)
            conn.close()
            return True
        return False
