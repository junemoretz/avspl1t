# DB helper functions

import sqlite3
import json

CONFIG_FILE = 'config.json'
SCHEMA_FILE = 'schema.sql'


def get_db():
    """
    Get a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    Raises:
        sqlite3.Error: If there is an error connecting to the database.
    """
    # Load the configuration file
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        db_file = config['databaseFile']
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize the database by creating the necessary tables.

    Raises:
        sqlite3.Error: If there is an error creating the tables.
    """
    with get_db() as db:
        db.executescript(open(SCHEMA_FILE).read())
