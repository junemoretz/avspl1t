import pytest
import grpc
import threading
import time
import json
import sys

sys.path.append('../')  # Adjust the path to import the main module
from main import serve
from proto.avspl1t_pb2 import JobDetails, AV1EncodeJob, FSFile, File, Folder, FSFolder, FinishTaskMessage, SplitVideoFinishMessage, EncodeVideoFinishMessage, GenerateManifestFinishMessage, JobId, GetTaskMessage
from proto.avspl1t_pb2_grpc import CoordinatorServiceStub
from logic.db import init_db

# This is a test for the Coordinator gRPC service.

CONFIG_FILE = '../config.json'


@pytest.fixture(scope="module")
def grpc_server():
    """Fixture to start the gRPC server."""
    init_db()
    server_thread = threading.Thread(
        target=serve, args=(f"{CONFIG_FILE}",), daemon=True)
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

# TESTS


def test_full_job_flow(stub):
    """Test the full job flow from submission to completion."""
    # Create a job
    input_path = "/path/to/input/file.mp4"
    output_path = "/path/to/output/directory"
    input_file = File(fsfile=FSFile(path=input_path))
    output_directory = Folder(fsfolder=FSFolder(path=output_path))
    job = AV1EncodeJob(
        input_file=input_file,
        output_directory=output_directory,
        working_directory=output_directory,
        crf=23,
        seconds_per_segment=10
    )

    # Submit the job
    job_details = JobDetails(
        av1_encode_job=job,
    )
    job_id = stub.SubmitJob(job_details).id
    assert job_id is not None

    # Pull the split task
    worker_id = "worker_1"
    task = stub.GetTask(
        GetTaskMessage(
            worker_id=worker_id,
        )
    )
    assert task is not None
    assert task.split_video_task.input_file.fsfile.path == input_path

    # Finish the split task
    stub.FinishTask(
        FinishTaskMessage(
            worker_id=worker_id,
            task_id=task.id,
            succeeded=True,
            split_video_finish_message=SplitVideoFinishMessage(
                generated_files=[
                    File(fsfile=FSFile(path=f"{output_path}/segment_{i}.mp4")) for i in range(3)]
            )
        )
    )

    # Pull and finish encode tasks
    for i in range(3):
        encode_task = stub.GetTask(
            GetTaskMessage(
                worker_id=worker_id,
            )
        )
        assert encode_task is not None and encode_task.encode_video_task.crf == 23

        stub.FinishTask(
            FinishTaskMessage(
                worker_id=worker_id,
                task_id=encode_task.id,
                succeeded=True,
                encode_video_finish_message=EncodeVideoFinishMessage(
                    generated_file=File(fsfile=FSFile(
                        path=f"{output_path}/segment_{i}.av1"))
                )
            )
        )

    # Pull and finish manifest task
    manifest_task = stub.GetTask(
        GetTaskMessage(
            worker_id=worker_id,
        )
    )
    assert manifest_task is not None
    expected_paths = [f"{output_path}/segment_{i}.av1" for i in range(3)]
    actual_paths = [
        f.fsfile.path for f in manifest_task.generate_manifest_task.files]
    actual_paths = sorted(actual_paths)

    assert actual_paths == expected_paths

    stub.FinishTask(
        FinishTaskMessage(
            worker_id=worker_id,
            task_id=manifest_task.id,
            succeeded=True,
            generate_manifest_finish_message=GenerateManifestFinishMessage(
                generated_file=File(fsfile=FSFile(
                    path=f"{output_path}/master.m3u8"))
            )
        )
    )

    # Check job is marked as complete
    job_status = stub.GetJob(
        JobId(id=job_id)
    )
    assert job_status.finished
    assert job_status.percent_complete == 100
