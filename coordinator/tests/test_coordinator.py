import sys

sys.path.append('../')  # Adjust the path to import the main module
from logic.utils import get_path_from_file, get_path_from_folder, file_from_path, folder_from_path
from proto.avspl1t_pb2 import JobDetails, AV1EncodeJob, FinishTaskMessage, SplitVideoFinishMessage, EncodeVideoFinishMessage, GenerateManifestFinishMessage, JobId, GetTaskMessage

# This is a test for the full flow of the Coordinator gRPC service.

# HELPER FUNCTION


def run_full_job_flow(stub, input_path, output_path, use_credentials=False):
    """
    Runs the full job flow from submission to completion.

    :param stub: The gRPC client stub for the CoordinatorService.
    :param input_path: The path to the input video file.
    :param output_path: The path to the output directory.
    :param use_credentials: Whether to use credentials for S3 paths.
    """
    # Create a job
    input_file = file_from_path(input_path, testing=use_credentials)
    output_directory = folder_from_path(output_path, testing=use_credentials)
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
    assert job_id is not None, "Job ID should not be None"

    # Pull the split task
    worker_id = "worker_1"
    task = stub.GetTask(
        GetTaskMessage(
            worker_id=worker_id,
        )
    )
    split_file_path = get_path_from_file(task.split_video_task.input_file)
    assert task is not None, "Task should not be None"
    assert split_file_path == input_path, "Input file path should match"

    # Finish the split task
    stub.FinishTask(
        FinishTaskMessage(
            worker_id=worker_id,
            task_id=task.id,
            succeeded=True,
            split_video_finish_message=SplitVideoFinishMessage(
                generated_files=[
                    file_from_path(f"{output_path}/segment_{i}.mp4", testing=use_credentials) for i in range(3)]
            )
        )
    )

    # Pull and finish encode tasks
    total_tasks = 3
    for i in range(total_tasks):
        encode_task = stub.GetTask(
            GetTaskMessage(
                worker_id=worker_id,
            )
        )
        assert encode_task is not None, "Encode task should not be None"
        assert encode_task.encode_video_task.crf == 23, "CRF should match"
        assert encode_task.encode_video_task.index < total_tasks, f"Index should be less than {total_tasks}"

        stub.FinishTask(
            FinishTaskMessage(
                worker_id=worker_id,
                task_id=encode_task.id,
                succeeded=True,
                encode_video_finish_message=EncodeVideoFinishMessage(
                    generated_file=file_from_path(
                        f"{output_path}/segment_{i}.av1", testing=use_credentials)
                )
            )
        )

    # Pull and finish manifest task
    manifest_task = stub.GetTask(
        GetTaskMessage(
            worker_id=worker_id,
        )
    )
    assert manifest_task is not None, "Manifest task should not be None"
    expected_files = [file_from_path(
        f"{output_path}/segment_{i}.av1", testing=use_credentials) for i in range(3)]
    expected_paths = [get_path_from_file(f) for f in expected_files]
    actual_paths = [
        get_path_from_file(f) for f in manifest_task.generate_manifest_task.files]
    actual_paths = sorted(actual_paths)
    manifest_output_folder = get_path_from_folder(
        manifest_task.generate_manifest_task.output_directory)
    print("EXPECTED:", expected_paths)
    print("ACTUAL:", actual_paths)
    assert actual_paths == expected_paths, "Manifest task should have correct file paths"
    assert manifest_task.generate_manifest_task.seconds_per_segment == 10, "Seconds per segment should match"
    assert manifest_output_folder == output_path, f"Output directory should match, got: {manifest_output_folder}"

    stub.FinishTask(
        FinishTaskMessage(
            worker_id=worker_id,
            task_id=manifest_task.id,
            succeeded=True,
            generate_manifest_finish_message=GenerateManifestFinishMessage(
                generated_file=file_from_path(
                    f"{output_path}/master.m3u8", testing=use_credentials)
            )
        )
    )

    # Check job is marked as complete
    job_status = stub.GetJob(
        JobId(id=job_id)
    )
    assert job_status.finished, "Job should be marked as finished"
    assert job_status.percent_complete == 100, f"Job should be 100% complete"

# TESTS


def test_full_job_flow_local(stub):
    """
    Test the full job flow with local file paths.

    :param stub: The gRPC client stub for the CoordinatorService.
    """
    input_path = "/path/to/input/video.mp4"
    output_path = "/path/to/output/directory"

    run_full_job_flow(stub, input_path, output_path)


def test_full_job_flow_s3(stub):
    """
    Test the full job flow with S3 file paths.

    :param stub: The gRPC client stub for the CoordinatorService.
    """
    input_path = "s3://bucket-name/input/video.mp4"
    output_path = "s3://bucket-name/output/directory"

    run_full_job_flow(stub, input_path, output_path, use_credentials=True)
