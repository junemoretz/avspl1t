from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp

# Helper functions


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
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if dt.tzinfo is None:
        # If the datetime object is naive, set it to UTC
        dt = dt.replace(tzinfo=timezone.utc)
    timestamp = Timestamp()
    # Convert the datetime object to a Timestamp object
    timestamp.FromDatetime(dt)
    return timestamp
