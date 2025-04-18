from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp
from proto.avspl1t_pb2 import File, Folder, S3File, FSFile, S3Folder, FSFolder, S3Credentials

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


def get_path_from_file(file_msg):
    """
    Get the path from a File message depending on whether we're using local or S3 filesystem.
    Args:
        file_msg (File): The File message.
    Returns:
        str: The path of the file.
    Raises:
        ValueError: If the file type is not supported.
    """
    if file_msg.HasField('fsfile'):
        return file_msg.fsfile.path
    elif file_msg.HasField('s3file'):
        return f"s3://{file_msg.s3file.bucket}/{file_msg.s3file.path}"
    else:
        raise ValueError(
            "Unsupported file type. Must be either fsfile or s3file.")


def get_path_from_folder(folder_msg):
    """
    Get the path from a Folder message depending on whether we're using local or S3 filesystem.
    Args:
        folder_msg (Folder): The Folder message.
    Returns:
        str: The path of the folder.
    Raises:
        ValueError: If the folder type is not supported.
    """
    if folder_msg.HasField('fsfolder'):
        return folder_msg.fsfolder.path
    elif folder_msg.HasField('s3folder'):
        return f"s3://{folder_msg.s3folder.bucket}/{folder_msg.s3folder.path}"
    else:
        raise ValueError(
            "Unsupported folder type. Must be either fsfolder or s3folder.")


def file_from_path(path: str, testing: bool = False):
    """
    Create a File message from a path.
    Args:
        path (str): The path of the file.
        testing (bool): Whether to add fake credentials for testing purposes.
    Returns:
        File: The File message.
    """
    if path.startswith("s3://"):  # s3 file
        # Parse: s3://bucket-name/key/path
        no_prefix = path[len("s3://"):]
        bucket, _, key = no_prefix.partition("/")
        file = File(s3file=S3File(bucket=bucket, path=key))
        if testing:
            # Add fake credentials for testing purposes
            file.s3file.credentials.CopyFrom(S3Credentials(
                access_key_id="FAKEACCESSKEY",
                secret_access_key="FAKESECRETKEY",
                region="us-west-1",
                endpoint="https://s3.test.fake"
            ))
        return file
    else:  # local file
        return File(fsfile=FSFile(path=path))


def folder_from_path(path: str, testing: bool = False):
    """
    Create a Folder message from a path.
    Args:
        path (str): The path of the folder.
        testing (bool): Whether to add fake credentials for testing purposes.
    Returns:
        Folder: The Folder message.
    """
    if path.startswith("s3://"):  # s3 folderxw
        # Parse: s3://bucket-name/key/path
        no_prefix = path[len("s3://"):]
        bucket, _, key = no_prefix.partition("/")
        folder = Folder(s3folder=S3Folder(bucket=bucket, path=key))
        if testing:
            # Add fake credentials for testing purposes
            folder.s3folder.credentials.CopyFrom(S3Credentials(
                access_key_id="FAKEACCESSKEY",
                secret_access_key="FAKESECRETKEY",
                region="us-west-1",
                endpoint="https://s3.test.fake"
            ))
        return folder
    else:  # local folder
        return Folder(fsfolder=FSFolder(path=path))
