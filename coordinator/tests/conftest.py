import pytest
import grpc
import threading
import time
import json
import sys

sys.path.append('../')  # Adjust the path to import the main module
from main import serve
from proto.avspl1t_pb2_grpc import CoordinatorServiceStub
from logic.db import DBLogic

# SHARED FIXTURES FOR TESTS

CONFIG_FILE = '../config.json'
SCHEMA_FILE = '../schema.sql'


@pytest.fixture(scope="module")
def grpc_server():
    """Fixture to start the gRPC server."""
    db = DBLogic(config_file=CONFIG_FILE, schema_file=SCHEMA_FILE)
    heartbeat = 1  # set manual heartbeat for testing
    server_thread = threading.Thread(
        target=serve, args=(db, f"{CONFIG_FILE}", heartbeat), daemon=True)
    server_thread.start()
    time.sleep(0.5)  # Give the server time to start
    yield


@pytest.fixture
def stub(grpc_server):
    """Fixture to create a gRPC client stub.

    :param grpc_server: The gRPC server fixture.
    :return: A gRPC client stub for the CoordinatorService.
    """
    # read in host and port from config
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        host = config['host']
        port = config['port']
    channel = grpc.insecure_channel(f'{host}:{port}')
    stub = CoordinatorServiceStub(channel)
    yield stub
    channel.close()


@pytest.fixture(autouse=True)
def reset_database():
    """
    Reset the database before each test.
    """
    db = DBLogic(config_file=CONFIG_FILE, schema_file=SCHEMA_FILE)
    with db.get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE tasks, jobs RESTART IDENTITY CASCADE;")
