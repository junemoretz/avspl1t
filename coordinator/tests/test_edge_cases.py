import sys
import time

sys.path.append('../')  # Adjust the path to import the main module
from logic.utils import file_from_path, folder_from_path, get_path_from_file
from proto.avspl1t_pb2 import JobDetails, AV1EncodeJob, FinishTaskMessage, SplitVideoFinishMessage, JobId, GetTaskMessage

# This is a test for edge cases for the Coordinator gRPC service.


def test_get_job_initial_status(stub):
    """
    Test the initial status of a job after submission.

    :param stub: The gRPC client stub for the CoordinatorService.
    """
    input_path = "/tmp/test_input_initial.mp4"
    output_path = "/tmp/test_output_initial"
    input_file = file_from_path(input_path)
    output_directory = folder_from_path(output_path)

    # Create a job
    job = AV1EncodeJob(
        input_file=input_file,
        output_directory=output_directory,
        working_directory=output_directory,
        crf=22,
        seconds_per_segment=5,
    )

    # Submit the job and check status
    job_id = stub.SubmitJob(JobDetails(av1_encode_job=job)).id
    job_status = stub.GetJob(JobId(id=job_id))

    assert not job_status.finished, "Job should not be finished initially"
    assert job_status.percent_complete == 0, f"Job should be 0% complete initially"


def test_failed_task_marks_job_failed(stub):
    """
    Test that a failed task marks the whole job as failed.

    :param stub: The gRPC client stub for the CoordinatorService.
    """
    input_path = "/tmp/test_fail_input.mp4"
    output_path = "/tmp/test_fail_output"
    input_file = file_from_path(input_path)
    output_directory = folder_from_path(output_path)

    # Create a job
    job = AV1EncodeJob(
        input_file=input_file,
        output_directory=output_directory,
        working_directory=output_directory,
        crf=30,
        seconds_per_segment=6,
    )

    # Submit the job
    job_id = stub.SubmitJob(JobDetails(av1_encode_job=job)).id

    # Pull the split task and mark it as failed
    task = stub.GetTask(GetTaskMessage(worker_id="fail_worker"))
    stub.FinishTask(FinishTaskMessage(
        worker_id="fail_worker",
        task_id=task.id,
        succeeded=False
    ))

    # Pull the job status and check if it is marked as failed
    job_status = stub.GetJob(JobId(id=job_id))
    assert job_status.failed, "Job should be marked as failed after a failed task"
    assert not job_status.finished, "Job should not be finished after a failed task"


def test_duplicate_finish_task_is_idempotent(stub):
    """
    Test that finishing a task twice does not change the job status.

    :param stub: The gRPC client stub for the CoordinatorService.
    """
    input_path = "/tmp/test_dupe_input.mp4"
    output_path = "/tmp/test_dupe_output"
    input_file = file_from_path(input_path)
    output_directory = folder_from_path(output_path)

    # Create a job
    job = AV1EncodeJob(
        input_file=input_file,
        output_directory=output_directory,
        working_directory=output_directory,
        crf=24,
        seconds_per_segment=5,
    )
    # Submit the job
    job_id = stub.SubmitJob(JobDetails(av1_encode_job=job)).id

    # Pull the split task and finish it
    task = stub.GetTask(GetTaskMessage(worker_id="dupe_worker"))
    finish_request = FinishTaskMessage(
        worker_id="dupe_worker",
        task_id=task.id,
        succeeded=True,
        split_video_finish_message=SplitVideoFinishMessage(
            generated_files=[
                file_from_path(f"{output_path}/segment_{i}.mp4")
                for i in range(2)
            ]
        )
    )

    # Finish the split task twice
    stub.FinishTask(finish_request)
    stub.FinishTask(finish_request)

    # Pull the job status and check if it is marked as failed/finished after splitting
    job_status = stub.GetJob(JobId(id=job_id))
    assert not job_status.failed, "Job should not be marked as failed"
    assert not job_status.finished, "Job should not be finished after double call"


def test_heartbeat_and_reassignment(stub):
    """
    Test that a task can be reassigned after a heartbeat timeout.

    :param stub: The gRPC client stub for the CoordinatorService.
    """
    input_path = "/tmp/test_reassign_input.mp4"
    output_path = "/tmp/test_reassign_output"
    input_file = file_from_path(input_path)
    output_directory = folder_from_path(output_path)

    # Create a job
    job = AV1EncodeJob(
        input_file=input_file,
        output_directory=output_directory,
        working_directory=output_directory,
        crf=20,
        seconds_per_segment=4,
    )

    # Submit the job
    stub.SubmitJob(JobDetails(av1_encode_job=job)).id

    # Worker A pulls the task
    task = stub.GetTask(GetTaskMessage(worker_id="worker_A"))
    assert task is not None
    task_id = task.id

    # Wait for heartbeat timeout (assume config uses 1s for test env)
    time.sleep(2)

    # Worker B should be able to claim the task
    reassigned = stub.GetTask(GetTaskMessage(worker_id="worker_B"))
    assert reassigned.id == task_id, "Task should be reassigned to worker_B"
    assert get_path_from_file(
        reassigned.split_video_task.input_file) == input_path, "Input file path should match"
