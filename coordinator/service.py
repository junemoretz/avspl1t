# Coordinator Servicer class
import json
import grpc
import proto.avspl1t_pb2 as avspl1t_pb2
import proto.avspl1t_pb2_grpc as avspl1t_pb2_grpc

from db import get_db, timestamp_from_sql

from datetime import datetime, timezone, timedelta

CONFIG_FILE = 'config.json'


class CoordinatorService(avspl1t_pb2_grpc.CoordinatorService):
    def __init__(self):
        # set heartbeat timeout from config
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            self.HEARTBEAT_TIMEOUT = config['heartbeatTimeout']

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
        if not request.hasField("av1_encode_job"):
            # If the request does not contain an AV1EncodeJob field, set the error code and details
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Missing AV1EncodeJob field")
            return avspl1t_pb2.JobId()

        # Extract job details from the request
        job = request.av1_encode_job
        input_path = job.input_file.fsfile.path
        output_path = job.output_directory.fsfolder.path
        crf = job.crf
        seconds_per_segment = job.seconds_per_segment

        with get_db() as db:
            # Add new job to the jobs table
            cur = db.execute(
                """
                INSERT INTO jobs (input_file, output_dir, crf, seconds_per_segment)
                VALUES (?, ?, ?, ?) RETURNING id
                """,
                (input_path, output_path, crf, seconds_per_segment)
            )
            # Get the job ID from the result
            job_id = cur.fetchone()[0]
            # Create a split video task and insert it into the tasks table
            db.execute(
                """
                INSERT INTO tasks (job_id, type, input_file, output_dir, crf)
                VALUES (?, 'split', ?, ?, ?)
                """,
                (job_id, input_path, output_path, crf)
            )
        # return the JobId object
        return avspl1t_pb2.JobId(id=str(job_id))

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
        with get_db() as db:
            # Get the job details from the database
            job = db.execute(
                """
                SELECT * FROM jobs WHERE id = ?
                """,
                (request.id,)).fetchone()
            # If no job is found, set the error code and return an empty Job object
            if not job:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return avspl1t_pb2.Job()
            # Get the number of tasks associated with the job
            total_tasks = db.execute(
                """
                SELECT COUNT(*) FROM tasks WHERE job_id = ?
                """,
                (job['id'],)).fetchone()[0]
            # Get the number of completed tasks for the job
            completed_tasks = db.execute(
                """
                SELECT COUNT(*) FROM tasks WHERE job_id = ? AND completed = 1
                """,
                (job['id'],)).fetchone()[0]
            # Calculate the percentage of completion
            percent_complete = 0 if total_tasks == 0 else (round(
                completed_tasks / total_tasks) * 100)
            # Create a Job object with the job details
            job_obj = avspl1t_pb2.Job(
                id=str(job['id']),
                finished=(job['status'] == 'complete'),
                failed=(job['status'] == 'failed'),
                percent_complete=percent_complete,
                generated_manipest=avspl1t_pb2.File(
                    fsfile=avspl1t_pb2.FSFile(path=job['manifest_file'] or '')),
                job_details=avspl1t_pb2.JobDetails(
                    av1_encode_job=avspl1t_pb2.AV1EncodeJob(
                        input_file=avspl1t_pb2.File(
                            fsFile=avspl1t_pb2.FSFile(path=job['input_file'])),
                        output_directory=avspl1t_pb2.Folder(
                            fsFile=avspl1t_pb2.FSFolder(path=job['output_dir'])),
                        working_directory=avspl1t_pb2.Folder(
                            fsFile=avspl1t_pb2.FSFolder(path=job['output_dir'])),
                        crf=job['crf'],
                        seconds_per_segment=job['seconds_per_segment'],
                    )),
                created_at=timestamp_from_sql(job['created_at']),
            )
            return job_obj

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
        with get_db() as db:
            now = datetime.now(timezone.utc)
            # Retrieve task from the database and mark as "in progress"
            db.execute("BEGIN IMMEDIATE")
            # Find most recent task that meets the criteria:
            # !completed && (!worker || heartbeat more than HEARTBEAT_TIMEOUT ago)
            task = db.execute(
                """
                SELECT * FROM tasks
                WHERE completed = 0 AND (assigned_worker IS NULL OR last_heartbeat IS NULL OR last_heartbeat < ?)
                ORDER BY id DESC LIMIT 1
                """,
                (now - timedelta(seconds=self.HEARTBEAT_TIMEOUT,))
            ).fetchone()
            # No available task meets assignment conditions; return empty Task
            if not task:
                db.execute("COMMIT")
                return avspl1t_pb2.Task()
            # Else, mark the task as assigned to the worker
            db.execute(
                """
                UPDATE tasks
                SET assigned_worker = ?, last_heartbeat = ?
                WHERE id = ?
                """,
                (request.worker_id, now, task['id'])
            )
            db.execute("COMMIT")

            # find the job associated with the task
            job = db.execute("""
                SELECT * FROM jobs WHERE id = ?
                """,
                             (task['job_id'],)).fetchone()

            # construct correct task object based on type
            if task['type'] == 'split':
                task_obj = avspl1t_pb2.Task(
                    split_video_task=avspl1t_pb2.SplitVideoTask(
                        input_file=avspl1t_pb2.File(
                            fsfile=avspl1t_pb2.FSFile(path=task['input_file'])),
                        output_directory=avspl1t_pb2.Folder(
                            fsfolder=avspl1t_pb2.FSFolder(path=task['output_dir'])),
                        seconds_per_segment=job['seconds_per_segment'],
                    ),
                )
            elif task['type'] == 'encode':
                task_obj = avspl1t_pb2.Task(
                    encode_video_task=avspl1t_pb2.EncodeVideoTask(
                        input_file=avspl1t_pb2.File(
                            fsfile=avspl1t_pb2.FSFile(path=task['input_file'])),
                        output_directory=avspl1t_pb2.Folder(
                            fsfolder=avspl1t_pb2.FSFolder(path=task['output_dir'])),
                        crf=task['crf'],
                    ),
                )
            elif task['type'] == 'manifest':
                manifest_files = db.execute(
                    """
                    SELECT * FROM tasks WHERE job_id = ? AND type = 'encode' ORDER BY index ASC
                    """,
                    (task['job_id'],)).fetchall()
                task_obj = avspl1t_pb2.Task(
                    generate_manifest_task=avspl1t_pb2.GenerateManifestTask(
                        files=[
                            avspl1t_pb2.File(
                                fsfile=avspl1t_pb2.FSFile(
                                    path=et['output_file']),
                            )
                            for et in manifest_files if et['output_file']
                        ],
                    ),
                )
            else:
                # If the task type is not recognized, set the error code and return an empty Task object
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Unknown task type")
                return avspl1t_pb2.Task()

            task_obj.id = str(task['id'])  # set task ID
            task_obj.created_at = timestamp_from_sql(
                task['last_heartbeat'] or now)

            return task_obj

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
        with get_db() as db:
            task = db.execute(
                """
                SELECT * FROM tasks WHERE id = ?
                """,
                (request.task_id,)).fetchone()
            if not task:
                # If no task is found, set the error code and return an empty object
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return avspl1t_pb2.Empty()
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
            return avspl1t_pb2.Empty()

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
        with get_db() as db:
            task = db.execute(
                """
                SELECT * FROM tasks WHERE id = ?
                """,
                (request.task_id,)).fetchone()
            if not task:
                # If no task is found, set the error code and return an empty object
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return avspl1t_pb2.Empty()
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
                    SET completed = 1, error_message = ?
                    WHERE job_id = ?
                    """,
                    (request.task_id,)
                )
                return avspl1t_pb2.Empty()

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
                    (request.encode_video_finish_message.output_file.fsfile.path,
                     request.task_id)
                )

            # Additional steps should take place depending on task type
            if task['type'] == 'split':
                for i, f in enumerate(request.split_video_finish_message.generated_files):
                    # Add encode tasks for each generated file
                    db.execute(
                        """
                        INSERT INTO tasks (job_id, type, input_file, output_dir, crf, index)
                        VALUES (?, 'encode', ?, ?, ?, ?)
                        """,
                        (task['job_id'], f.fsfile.path,
                            task['output_dir'], task['crf'], i)
                    )
            elif task['type'] == 'encode':
                # If the task is an encode task, check if all encode tasks are completed
                # and if so, create a manifest task
                remaining = db.execute(
                    """
                    SELECT COUNT(*) FROM tasks WHERE job_id = ? AND completed = 0
                    """,
                    (task['job_id'],)).fetchone()[0]
                if remaining == 0:
                    db.execute(
                        """
                        INSERT INTO tasks (job_id, type) VALUES (?, 'manifest')
                        """,
                        (task['job_id'],)
                    )
            elif task['type'] == 'manifest':
                if request.HasField("generate_manifest_finish_message"):
                    # If the task is a manifest task, update the job status to complete
                    db.execute(
                        """
                        UPDATE tasks
                        SET output_file = ?
                        WHERE id = ?
                        """,
                        (request.generate_manifest_finish_message.generated_file.fsfile.path, request.task_id)
                    )
                    db.execute(
                        """
                        UPDATE jobs
                        SET status = 'complete',
                            manifest_file = ?
                        WHERE id = ?
                        """,
                        (request.generate_manifest_finish_message.generated_file.fsfile.path,
                         task['job_id'])
                    )
            return avspl1t_pb2.Empty()
