# Coordinator Servicer class
import json
import grpc
from proto.avspl1t_pb2_grpc import CoordinatorServiceServicer
from proto.avspl1t_pb2 import JobId, Job, Task, Empty

from logic.job import create_job, get_job
from logic.task import assign_next_task, build_task_proto, handle_split_finish, handle_encode_finish, handle_manifest_finish

from datetime import datetime, timezone

CONFIG_FILE = 'config.json'


class CoordinatorServicer(CoordinatorServiceServicer):
    def __init__(self, database, config_file=CONFIG_FILE):
        # set heartbeat timeout from config
        with open(config_file, 'r') as f:
            config = json.load(f)
            self.HEARTBEAT_TIMEOUT = config['heartbeatTimeout']
        self.database = database

    def SubmitJob(self, request, context):
        """
        Submit a job to the coordinator.

        Args:
            request: JobDetails object containing job information.
            context: gRPC context.
        Returns:
            JobId object containing the ID of the submitted job.
        Raises:
            grpc.StatusCode: If there is an error during job submission.
        """
        if not request.HasField("av1_encode_job"):
            # If the request does not contain an AV1EncodeJob field, set the error code and details
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Missing AV1EncodeJob field")
            return JobId()

        # Extract job details from the request
        job = request.av1_encode_job
        job_id = create_job(self.database, job)

        # return the JobId object
        return JobId(id=job_id)

    def GetJob(self, request, context):
        """
        Get the requested job from the database.

        Args:
            request: JobId object containing the job ID.
            context: gRPC context.
        Returns:
            Job object containing job information.
        Raises:
            grpc.StatusCode: If there is an error during job retrieval.
        """
        job = get_job(self.database, request.id)
        if job is None:
            # If no job is found, set the error code and return an empty Job object
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return Job()
        return job

    def GetTask(self, request, context):
        """
        Get the requested task from the database.
        Args:
            request: TaskId object containing the task ID.
            context: gRPC context.
        Returns:
            Task object containing task information.
        Raises:
            grpc.StatusCode: If there is an error during task retrieval.
        """
        with self.database.get_db() as db:
            task_row = assign_next_task(self.database,
                                        request.worker_id, self.HEARTBEAT_TIMEOUT)
            if task_row is None:
                #  If no task found, return an empty Task object
                return Task()

            with self.database.get_db() as db:
                # Find associated job
                job_row = db.execute(
                    """
                    SELECT * FROM jobs WHERE id = ?
                    """,
                    (task_row['job_id'],)).fetchone()

            # Construct the task object based on the task type
            task_proto = build_task_proto(self.database, task_row, job_row)
            if task_proto is None:
                # If task_proto is None, set the error code and return an empty Task object
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Unknown task type")
                return Task()
            return task_proto

    def Heartbeat(self, request, context):
        """
        Update the heartbeat time for a worker.
        Args:
            request: Heartbeat object containing worker ID.
            context: gRPC context.
        Returns:
            Empty object.
        Raises:
            grpc.StatusCode: If there is an error during heartbeat update.
        """
        with self.database.get_db() as db:
            task = db.execute(
                """
                SELECT * FROM tasks WHERE id = ?
                """,
                (request.task_id,)).fetchone()
            if not task:
                # If no task is found, set the error code and return an empty object
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Task not found")
                return Empty()
            if task and task['assigned_worker'] == request.worker_id:
                # Update the last heartbeat time for the task
                db.execute(
                    """
                    UPDATE tasks
                    SET last_heartbeat = ?
                    WHERE id = ?
                    """,
                    (datetime.now(timezone.utc), request.task_id)
                )
            return Empty()

    def FinishTask(self, request, context):
        """
        Finish a task and update its status in the database.
        Args:
            request: FinishTaskRequest object containing task ID and success status.
            context: gRPC context.
        Returns:
            Empty object.
        Raises:
            grpc.StatusCode: If there is an error during task completion.
        """
        with self.database.get_db() as db:
            task = db.execute(
                """
                SELECT * FROM tasks WHERE id = ?
                """,
                (request.task_id,)).fetchone()
            if not task:
                # If no task is found, set the error code and return an empty object
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return Empty()
            if not request.succeeded:
                # If the task failed, mark job as failed, and all associated tasks as completed/canceled
                db.execute(
                    """
                    UPDATE jobs
                    SET status = 'failed'
                    WHERE id = ?
                    """,
                    (request.task_id, )
                )
                db.execute(
                    """
                    UPDATE tasks
                    SET completed = 1
                    WHERE job_id = ?
                    """,
                    (request.task_id,)
                )
                return Empty()

            # If succeeded, mark task as completed
            db.execute(
                """
                UPDATE tasks
                SET completed = 1
                WHERE id = ?
                """,
                (request.task_id,)
            )

            if request.HasField("encode_video_finish_message"):
                # If the task is an encode task, update the output file path
                db.execute(
                    """
                    UPDATE tasks
                    SET output_file = ?
                    WHERE id = ?
                    """,
                    (request.encode_video_finish_message.generated_file.fsfile.path,
                     request.task_id)
                )

            # Additional steps should take place depending on task type
            if task['type'] == 'split':
                handle_split_finish(db, task, request)
            elif task['type'] == 'encode':
                handle_encode_finish(db, task)
            elif task['type'] == 'manifest':
                handle_manifest_finish(db, task, request)
            return Empty()
