# DB helper functions
import psycopg2.extras
from psycopg2 import sql
import json
from contextlib import contextmanager

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

        # Load the configuration file
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            self.db_file = config['databaseFile']
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
        Get a connection to the SQLite database.

        Returns:
            postgres.Connection: A connection object to the PostgreSQL database.
        Raises:
            postgres.Error: If there is an error connecting to the PostgreSQL database.
        """
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

    def ensure_db_exists(self):
        """
        Create PostgreSQL database if it does not exist.
        """
        # Create a connection to the PostgreSQL database
        conn = None
        try:
            conn = self.connect_postgres()
            conn.autocommit = True
            with conn.cursor() as cur:
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
        """
        self.ensure_db_exists()  # Ensure the database exists
        # Create the database and tables using the schema file
        with self.get_db() as conn:
            with conn.cursor() as cur:
                with open(self.schema_file, 'r') as f:
                    cur.execute(f.read())
