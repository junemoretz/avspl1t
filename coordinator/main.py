# Server Setup
import json
import grpc
import proto.avspl1t_pb2_grpc as avspl1t_pb2_grpc

from concurrent import futures
from service import CoordinatorService
from db import init_db

CONFIG_FILE = 'config.json'


def serve():
    # read in config details
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        host = config['host']
        port = config['port']
        max_workers = config['maxWorkers']
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    avspl1t_pb2_grpc.add_CoordinatorServiceServicer_to_server(
        CoordinatorService(), server
    )
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    print(f"Coordinator server started at {host}:{port}")
    server.wait_for_termination()


if __name__ == '__main__':
    init_db()
    serve()
