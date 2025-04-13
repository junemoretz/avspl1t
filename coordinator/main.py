# Server Setup
import json
import grpc
from proto.avspl1t_pb2_grpc import add_CoordinatorServiceServicer_to_server

from concurrent import futures
from service import CoordinatorServicer
from logic.db import init_db
import os

CONFIG_FILE = 'config.json'


def serve(config_file=CONFIG_FILE):
    # read in config details
    with open(config_file, 'r') as f:
        config = json.load(f)
        host = config['host']
        port = config['port']
        max_workers = config['maxWorkers']
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    add_CoordinatorServiceServicer_to_server(
        CoordinatorServicer(config_file=config_file), server
    )
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    print(f"Coordinator server started at {host}:{port}")
    server.wait_for_termination()


if __name__ == '__main__':
    init_db()
    serve()
