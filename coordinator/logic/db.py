# DB helper functions
import psycopg2.extras
from psycopg2 import sql
import sqlite3
import json
from contextlib import contextmanager
import sys

CONFIG_FILE = 'config.json'
SCHEMA_FILE = 'schema/schema'

ALLOWED_DB_TYPES = ['sqlite', 'postgres']


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

        # Load the configuration file
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            self.db_type = config['databaseType']
            print(f"Database type: {self.db_type}")

            if (self.db_type not in ALLOWED_DB_TYPES):
                print(
                    f"Invalid database type: {self.db_type}. Allowed types are {ALLOWED_DB_TYPES}")
                # Exit the program if the database type is not valid
                sys.exit(1)

            self.db_file = config['databaseFile']

            # Set the schema file based on the database type
            self.schema_file = schema_file + \
                ('_postgres' if self.db_type == 'postgres' else '_sqlite') + '.sql'

            if self.db_type == 'sqlite':
                # SQLite specific settings
                self.db_file += '.db'
            else:
                # PostgreSQL specific settings
                self.postgres_user = config['postgresUser']
                self.postgres_password = config['postgresPassword']
                self.postgres_host = config['postgresHost']
                self.postgres_port = config['postgresPort']

        self.init_db()  # Initialize the database when the class is instantiated

    def connect_postgres(self):
        """
        Connect to the PostgreSQL database.

        Returns:
            postgres.Connection: A connection object to the PostgreSQL database.
        Raises:
            postgres.Error: If there is an error connecting to the PostgreSQL database.
        """
        # Create a connection to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=self.db_file,
            user=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            cursor_factory=psycopg2.extras.DictCursor,
        )
        return conn

    @contextmanager
    def get_db(self):
        """
        Get a connection to the SQLite or PostgreSQL database.

        Returns:
            sqlite3.Connection or postgres.Connection: A connection object to the database.
        Raises:
            sqlite3.Error: If there is an error connecting to the SQLite database.
            postgres.Error: If there is an error connecting to the PostgreSQL database.
        """
        if self.db_type == 'sqlite':
            # SQLite specific connection
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
        else:
            # Create a connection to the PostgreSQL database
            conn = self.connect_postgres()
            conn.autocommit = False  # Disable autocommit mode

        # Use a context manager to handle the connection
        # and ensure it is closed properly
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def ensure_pg_db_exists(self):
        """
        Create PostgreSQL database if it does not exist.
        """
        # Create a connection to the PostgreSQL database
        conn = None
        try:
            conn = self.connect_postgres()
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (self.db_file,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(
                    sql.SQL(
                        "CREATE DATABASE {} WITH ENCODING 'UTF8' TEMPLATE template1")
                    .format(sql.Identifier(self.db_file))
                )
        except psycopg2.errors.DuplicateDatabase:
            pass  # Database already exists
        except Exception as e:
            raise e
        finally:
            if conn is not None:
                conn.close()

    def init_db(self):
        """
        Initialize the database by creating the necessary tables.

        Raises:
            postgres.Error: If there is an error connecting to the PostgreSQL database.
            sqlite3.Error: If there is an error connecting to the SQLite database.
        """
        if self.db_type == 'postgres':
            self.ensure_pg_db_exists()  # Ensure the database exists if using PostgreSQL

            # Create the database and tables using the schema file
            with self.get_db() as conn:
                cur = conn.cursor()
                with open(self.schema_file, 'r') as f:
                    cur.execute(f.read())
        else:  # SQLite
            with self.get_db() as db:
                db.executescript(open(self.schema_file).read())
