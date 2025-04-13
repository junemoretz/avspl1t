# DB helper functions
import sqlite3
import json

CONFIG_FILE = 'config.json'
SCHEMA_FILE = 'schema.sql'


class DBLogic:
    """
    A class to handle database logic.
    """

    def __init__(self, config_file=CONFIG_FILE, schema_file=SCHEMA_FILE):
        """
        Initialize the DBLogic class with the configuration and schema files.
        Args:
            config_file (str): Path to the configuration file.
            schema_file (str): Path to the schema file.
        """
        self.config_file = config_file
        self.schema_file = schema_file

        self.init_db()  # Initialize the database when the class is instantiated

    def get_db(self):
        """
        Get a connection to the SQLite database.

        Returns:
            sqlite3.Connection: A connection object to the SQLite database.
        Raises:
            sqlite3.Error: If there is an error connecting to the database.
        """
        # Load the configuration file
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            db_file = config['databaseFile']
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """
        Initialize the database by creating the necessary tables.

        Raises:
            sqlite3.Error: If there is an error creating the tables.
        """
        with self.get_db() as db:
            db.executescript(open(self.schema_file).read())
