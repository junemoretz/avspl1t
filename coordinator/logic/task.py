# Handle Task-level Logic for Coordinator
from datetime import datetime, timezone, timedelta
from logic.utils import timestamp_from_sql
from proto.avspl1t_pb2 import Task, File, FSFile, Folder, FSFolder, SplitVideoTask, EncodeVideoTask, GenerateManifestTask


def assign_next_task(database, worker_id, heartbeat_timeout):
    """
    Assign the next task to a worker.
    Args:
        database (DBLogic): The database logic object.
        worker_id (str): The ID of the worker to assign the task to.
        heartbeat_timeout (int): The timeout for the worker's heartbeat.
    Returns:
        Task: The Task object containing task details.
    """
    now = datetime.now(timezone.utc)
    with database.get_db() as conn:
        with conn.cursor() as cur:
            # Find most recent task that meets the criteria:
            # !completed && (!worker || heartbeat more than heartbeat_timeout ago)
            cur.execute(
                """
                SELECT * FROM tasks 
                WHERE completed = FALSE AND (assigned_worker IS NULL OR last_heartbeat IS NULL OR last_heartbeat < %s) 
                ORDER BY id DESC LIMIT 1""",
                (now - timedelta(seconds=heartbeat_timeout),),
            )
            task = cur.fetchone()

            # No available task meets assignment conditions; return None
            if not task:
                conn.commit()
                return None
            # Else, mark the task as assigned to the worker
            cur.execute(
                "UPDATE tasks SET assigned_worker = %s, last_heartbeat = %s WHERE id = %s",
                (worker_id, now, task['id']),
            )
            conn.commit()
            return task


def build_task_proto(database, task, job):
    """
    Build a Task protobuf object from the task and job details.
    Args:
        database (DBLogic): The database logic object.
        task (Task): The Task object containing task details.
        job (Job): The Job object containing job details.
    Returns:
        Task: The Task protobuf object.
    """
    now = datetime.now(timezone.utc)

    # construct correct task object based on type
    if task['type'] == 'split':
        task_obj = Task(
            split_video_task=SplitVideoTask(
                input_file=File(fsfile=FSFile(path=task['input_file'])),
                output_directory=Folder(
                    fsfolder=FSFolder(path=task['output_dir'])),
                seconds_per_segment=job['seconds_per_segment']
            )
        )
    elif task['type'] == 'encode':
        task_obj = Task(
            encode_video_task=EncodeVideoTask(
                input_file=File(fsfile=FSFile(path=task['input_file'])),
                output_directory=Folder(
                    fsfolder=FSFolder(path=task['output_dir'])),
                crf=task['crf'],
                index=task['task_index'],
            )
        )
    elif task['type'] == 'manifest':
        with database.get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM tasks WHERE job_id = %s AND type = 'encode' AND completed = TRUE ORDER BY task_index ASC
                    """,
                    (task['job_id'],))
                manifest_files = cur.fetchall()

            task_obj = Task(
                generate_manifest_task=GenerateManifestTask(
                    files=[
                        File(
                            fsfile=FSFile(
                                path=et['output_file']),
                        )
                        for et in manifest_files if et['output_file']
                    ],
                    output_directory=Folder(
                        fsfolder=FSFolder(path=task['output_dir'])),
                    seconds_per_segment=job['seconds_per_segment'],
                ),
            )
    else:
        return None

    task_obj.id = str(task['id'])
    task_obj.created_at.CopyFrom(
        timestamp_from_sql(task['last_heartbeat'] or now))
    return task_obj


def handle_split_finish(conn, task, request):
    """
    Handle the completion of a split task.
    Args:
        conn (postgres.Connection): The database connection.
        task (dict): The task details.
        request (Task): The Task object containing task details.
    """
    # Extract and sort file paths first
    file_paths = sorted(
        [f.fsfile.path for f in request.split_video_finish_message.generated_files]
    )

    # Update the task with the output file paths
    for i, path in enumerate(file_paths):
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (job_id, type, input_file, output_dir, crf, task_index)
                VALUES (%s, 'encode', %s, %s, %s, %s)
                """,
                (task['job_id'], path, task['output_dir'], task['crf'], i)
            )


def handle_encode_finish(conn, task):
    """
    Handle the completion of an encode task.
    Args:
        conn (postgres.Connection): The database connection.
        task (dict): The task details.
    """
    # If the task is an encode task, check if all encode tasks are completed
    # and if so, create a manifest task
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM tasks WHERE job_id = %s AND completed = FALSE
            """,
            (task['job_id'],))
        remaining = cur.fetchone()[0]

        if remaining == 0:
            cur.execute(
                """
                INSERT INTO tasks (job_id, type, output_dir) VALUES (%s, 'manifest', %s)
                """,
                (task['job_id'], task['output_dir'])
            )


def handle_manifest_finish(conn, task, request):
    """
    Handle the completion of a manifest task.
    Args:
        conn (postgres.Connection): The database connection.
        task (dict): The task details.
        request (Task): The Task object containing task details.
    """
    if request.HasField("generate_manifest_finish_message"):
        with conn.cursor() as cur:
            # If the task is a manifest task, update the job status to complete
            cur.execute(
                """
                UPDATE tasks
                SET output_file = %s
                WHERE id = %s
                """,
                (request.generate_manifest_finish_message.generated_file.fsfile.path, request.task_id)
            )
            cur.execute(
                """
                UPDATE jobs
                SET status = 'complete',
                    manifest_file = %s
                WHERE id = %s
                """,
                (request.generate_manifest_finish_message.generated_file.fsfile.path,
                 task['job_id'])
            )
