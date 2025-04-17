# Server Setup
import json
import grpc
from proto.avspl1t_pb2_grpc import add_CoordinatorServiceServicer_to_server

from concurrent import futures
from service import CoordinatorServicer
from logic.db import DBLogic

CONFIG_FILE = 'config.json'


def serve(db, config_file=CONFIG_FILE, manual_heartbeat=-1):
    """Serve the gRPC server.
    Args:
        db (DBLogic): The database logic object.
        config_file (str): Path to the configuration file.
        manual_heartbeat (int): Manual heartbeat timeout.
    """
    # read in config details
    with open(config_file, 'r') as f:
        config = json.load(f)
        host = config['host']
        port = config['port']
        max_workers = config['maxWorkers']
        heartbeat_timeout = config['heartbeatTimeout'] if manual_heartbeat == - \
            1 else manual_heartbeat
    # Note: max_workers sets the number of threads used to handle incoming gRPC requests.
    # It does NOT limit the number of worker clients that can connect or run.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    add_CoordinatorServiceServicer_to_server(
        CoordinatorServicer(db, heartbeat_timeout), server
    )
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    print(f"Coordinator server started at {host}:{port}")
    server.wait_for_termination()


if __name__ == '__main__':
    db = DBLogic(config_file=CONFIG_FILE)
    serve(db)
