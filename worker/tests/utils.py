import sys
import grpc
import threading
from concurrent import futures

sys.path.append('../')  # Adjust the path to import the main module
from proto.avspl1t_pb2_grpc import add_CoordinatorServiceServicer_to_server, CoordinatorServiceServicer
from proto.avspl1t_pb2 import Task, Empty

PORT=51515

class CoordinatorServicerTesting(CoordinatorServiceServicer):
    def __init__(self):
        self.get_task_request = None
        self.heartbeat_request = None
        self.finish_task_request = None
        self.heartbeat_count = 0
        self.get_task_response = Task()

    def GetTask(self, request, context):
        self.get_task_request = request
        return self.get_task_response

    def Heartbeat(self, request, context):
        self.heartbeat_request = request
        self.heartbeat_count += 1
        return Empty()

    def FinishTask(self, request, context):
        self.finish_task_request = request
        return Empty()

    def setTask(self, response):
        self.get_task_response = response
    
class RPCServerForTest:
    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        add_CoordinatorServiceServicer_to_server(
            self.servicer, server
        )
        server.add_insecure_port(f'localhost:{PORT}')
        server.start()
        self.server = server
        self.stop_event = threading.Event()
        self.stop_event.wait()
        server.stop()
    
    def __init__(self):
        # Set up variables
        self.servicer = CoordinatorServicerTesting()
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()

    def get_servicer(self):
        return self.servicer

    def terminate(self):
        self.stop_event.set()
