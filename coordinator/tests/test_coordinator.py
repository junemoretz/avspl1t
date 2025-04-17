import sys

sys.path.append('../')  # Adjust the path to import the main module
from proto.avspl1t_pb2 import JobDetails, AV1EncodeJob, FSFile, File, Folder, FSFolder, FinishTaskMessage, SplitVideoFinishMessage, EncodeVideoFinishMessage, GenerateManifestFinishMessage, JobId, GetTaskMessage

# This is a test for the full flow of the Coordinator gRPC service.


def test_full_job_flow(stub):
    """
    Test the full job flow from submission to completion.

    :param stub: The gRPC client stub for the CoordinatorService.
    """
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
    assert job_id is not None, "Job ID should not be None"

    # Pull the split task
    worker_id = "worker_1"
    task = stub.GetTask(
        GetTaskMessage(
            worker_id=worker_id,
        )
    )
    assert task is not None, "Task should not be None"
    assert task.split_video_task.input_file.fsfile.path == input_path, "Input file path should match"

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
    assert manifest_task is not None, "Manifest task should not be None"
    expected_paths = [f"{output_path}/segment_{i}.av1" for i in range(3)]
    actual_paths = [
        f.fsfile.path for f in manifest_task.generate_manifest_task.files]
    actual_paths = sorted(actual_paths)

    assert actual_paths == expected_paths, "Manifest task should have correct file paths"
    assert manifest_task.generate_manifest_task.seconds_per_segment == 10, "Seconds per segment should match"
    assert manifest_task.generate_manifest_task.output_directory.fsfolder.path == output_path, f"Output directory should match, got: {manifest_task.generate_manifest_task.output_directory.fsfolder.path}"

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
    assert job_status.finished, "Job should be marked as finished"
    assert job_status.percent_complete == 100, f"Job should be 100% complete"
