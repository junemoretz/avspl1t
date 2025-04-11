# DB helper functions

import sqlite3
import json
from datetime import timezone
from google.protobuf.timestamp_pb2 import Timestamp

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


def timestamp_from_sql(dt):
    """
    Convert a Python datetime object to a google.protobuf.Timestamp object.
    Args:
        dt (datetime.datetime): The datetime object to convert.
    Returns:
        google.protobuf.Timestamp: The converted Timestamp object.
    """
    if not dt:
        # Return a default Timestamp if dt is None
        return Timestamp()
    if dt.tzinfo is None:
        # If the datetime object is naive, set it to UTC
        dt = dt.replace(tzinfo=timezone.utc)
    timestamp = Timestamp()
    # Convert the datetime object to a Timestamp object
    timestamp.FromDatetime(dt)
    return timestamp
