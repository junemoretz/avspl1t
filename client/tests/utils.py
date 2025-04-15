import sys
import grpc
import threading
from concurrent import futures

sys.path.append('../')  # Adjust the path to import the main module
from proto.avspl1t_pb2_grpc import add_CoordinatorServiceServicer_to_server, CoordinatorServiceServicer
from proto.avspl1t_pb2 import JobId, Job

PORT=51515

class CoordinatorServicerTesting(CoordinatorServiceServicer):
    def __init__(self):
        self.submit_job_request = None
        self.submit_job_response = JobId()
        self.get_job_request = None
        self.get_job_response = Job()

    def SubmitJob(self, request, context):
        self.submit_job_request = request
        return self.submit_job_response

    def GetJob(self, request, context):
        self.get_job_request = request
        return self.get_job_response

    def setSubmitResponse(self, response):
        self.submit_job_response = response
    
    def setGetResponse(self, response):
        self.get_job_response = response

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
