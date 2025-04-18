import json
import grpc
import time
import os
import threading
import traceback
from logic.splitVideo import split_video
from logic.encodeVideo import encode_video
from logic.generateManifest import generate_manifest
from proto.avspl1t_pb2_grpc import CoordinatorServiceStub
from proto.avspl1t_pb2 import GetTaskMessage, HeartbeatMessage, FinishTaskMessage

TEST_PORT=51515
TEST_WORKER_ID='123'

# Load config file
config = None
worker_id = None
stub = None
if (os.environ.get('TESTING')):
    host = 'localhost'
    port = TEST_PORT
    worker_id = TEST_WORKER_ID
    channel = grpc.insecure_channel(f'{host}:{port}')
    stub = CoordinatorServiceStub(channel)
else:
    with open('config.json', 'r') as f:
        config = json.load(f)
        host = config['host']
        port = config['port']
        worker_id = config['worker_id']
        channel = grpc.insecure_channel(f'{host}:{port}')
        stub = CoordinatorServiceStub(channel)

def getTask():
    task = stub.GetTask(GetTaskMessage(worker_id=worker_id))
    return task

def sendHeartbeat(task_id):
    stub.Heartbeat(HeartbeatMessage(worker_id=worker_id,task_id=task_id))

# Loops every 0.1 seconds, but only sends heartbeat every 5
# This lets the task loop exit without having to wait 5 seconds
def heartbeatLoop(task_id, stop_event):
    value = 0
    while not stop_event.is_set():
        if value == 50:
            sendHeartbeat(task_id)
            print("Sending heartbeat...")
            value = 0
        time.sleep(0.1)
        value += 1

def handleTask(task):
    # start heartbeat
    stop_event = threading.Event()
    heartbeat_thread = threading.Thread(target=heartbeatLoop, args=(task.id, stop_event), daemon=True)
    heartbeat_thread.start()
    response = None
    # switch on type
    try:
        if task.WhichOneof("task") == "split_video_task":
            finish_message = split_video(task)
            response = FinishTaskMessage(worker_id=worker_id,task_id=task.id,succeeded=True,split_video_finish_message=finish_message)
        elif task.WhichOneof("task") == "encode_video_task":
            finish_message = encode_video(task)
            response = FinishTaskMessage(worker_id=worker_id,task_id=task.id,succeeded=True,encode_video_finish_message=finish_message)
        elif task.WhichOneof("task") == "generate_manifest_task":
            finish_message = generate_manifest(task)
            response = FinishTaskMessage(worker_id=worker_id,task_id=task.id,succeeded=True,generate_manifest_finish_message=finish_message)
    except Exception as exc:
        print(exc)
        print(traceback.format_exc())
        response = FinishTaskMessage(worker_id=worker_id,task_id=task.id,succeeded=False)
    # end heartbeat
    stop_event.set()
    heartbeat_thread.join()
    print("Task completed!")
    return response

def sendResponse(response):
    stub.FinishTask(response)

if __name__ == '__main__':
    while True:
        task = getTask()
        if task.id:
            print(f'Got task with ID {task.id}')
            response = handleTask(task)
            sendResponse(response)
        else:
            time.sleep(5)