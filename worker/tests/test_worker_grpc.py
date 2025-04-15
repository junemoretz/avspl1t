import sys
import time
import os
import subprocess
import threading
from utils import RPCServerForTest

sys.path.append('../')  # Adjust the path to import the main module
from proto.avspl1t_pb2 import FinishTaskMessage, Task

TEST_WORKER_ID='123'

def test_server_interactions():
  os.environ = {'TESTING': 'true'}
  from main import getTask, sendHeartbeat, sendResponse, heartbeatLoop
  # Create test server
  server = RPCServerForTest()
  servicer = server.get_servicer()
  servicer.setTask(Task(id="task1"))
  time.sleep(0.5) # wait for it to start
  # Test all 3 message types
  task = getTask()
  time.sleep(0.1)
  assert task.id == "task1", "Task ID is correct"
  assert servicer.get_task_request.worker_id == TEST_WORKER_ID, "Get task worker ID is correct"
  sendHeartbeat("task1")
  time.sleep(0.1)
  assert servicer.heartbeat_request.worker_id == TEST_WORKER_ID, "Heartbeat worker ID is correct"
  assert servicer.heartbeat_request.task_id == "task1", "Heartbeat task ID is correct"
  sendResponse(FinishTaskMessage(worker_id=TEST_WORKER_ID,task_id="task1",succeeded=True))
  time.sleep(0.1)
  assert servicer.finish_task_request.worker_id == TEST_WORKER_ID, "Finish task worker ID is correct"
  assert servicer.finish_task_request.task_id == "task1", "Finish task task ID is correct"
  assert servicer.finish_task_request.succeeded, "Finish task succeeded is true"
  # Test heartbeat loop
  stop_event = threading.Event()
  heartbeat_thread = threading.Thread(target=heartbeatLoop, args=(task.id, stop_event), daemon=True)
  heartbeat_thread.start()
  time.sleep(6)
  stop_event.set()
  heartbeat_thread.join()
  assert servicer.heartbeat_count == 2, "Correct number of heartbeats sent"
