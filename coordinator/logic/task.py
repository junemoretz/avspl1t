# Handle Task-level Logic for Coordinator

import json
from datetime import datetime, timezone, timedelta
from db import get_db, timestamp_from_sql
from proto.avspl1t_pb2 import Task, File, FSFile, Folder, FSFolder, SplitVideoTask, EncodeVideoTask, GenerateManifestTask


CONFIG_FILE = 'config.json'

# get heartbeat timeout from config
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)
    HEARTBEAT_TIMEOUT = config['heartbeatTimeout']


def assign_next_task(worker_id):
    """
    Assign the next task to a worker.
    Args:
        worker_id (str): The ID of the worker to assign the task to.
    Returns:
        Task: The Task object containing task details.
    """
    now = datetime.now(timezone.utc)
    with get_db() as db:
        # Retrieve task from the database and mark as "in progress"
        db.execute("BEGIN IMMEDIATE")
        # Find most recent task that meets the criteria:
        # !completed && (!worker || heartbeat more than HEARTBEAT_TIMEOUT ago)
        task = db.execute(
            "SELECT * FROM tasks WHERE completed = 0 AND (assigned_worker IS NULL OR last_heartbeat IS NULL OR last_heartbeat < ?) ORDER BY id DESC LIMIT 1",
            (now - timedelta(seconds=HEARTBEAT_TIMEOUT),),
        ).fetchone()
        # No available task meets assignment conditions; return None
        if not task:
            db.execute("COMMIT")
            return None
         # Else, mark the task as assigned to the worker
        db.execute(
            "UPDATE tasks SET assigned_worker = ?, last_heartbeat = ? WHERE id = ?",
            (worker_id, now, task['id']),
        )
        db.execute("COMMIT")
        return task


def build_task_proto(task, job):
    """
    Build a Task protobuf object from the task and job details.
    Args:
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
                crf=task['crf']
            )
        )
    elif task['type'] == 'manifest':
        with get_db() as db:
            manifest_files = db.execute(
                """
                SELECT * FROM tasks WHERE job_id = ? AND type = 'encode' AND completed = 1 ORDER BY index ASC
                """,
                (task['job_id'],)).fetchall()
            task_obj = Task(
                generate_manifest_task=GenerateManifestTask(
                    files=[
                        File(
                            fsfile=FSFile(
                                path=et['output_file']),
                        )
                        for et in manifest_files if et['output_file']
                    ],
                ),
            )
    else:
        return None

    task_obj.id = str(task['id'])
    task_obj.created_at.CopyFrom(
        timestamp_from_sql(task['last_heartbeat'] or now))
    return task_obj


def handle_split_finish(db, task, request):
    """
    Handle the completion of a split task.
    Args:
        db (sqlite3.Connection): The database connection.
        task (dict): The task details.
        request (Task): The Task object containing task details.
    """
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


def handle_encode_finish(db, task):
    """
    Handle the completion of an encode task.
    Args:
        db (sqlite3.Connection): The database connection.
        task (dict): The task details.
    """
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


def handle_manifest_finish(db, task, request):
    """
    Handle the completion of a manifest task.
    Args:
        db (sqlite3.Connection): The database connection.
        task (dict): The task details.
        request (Task): The Task object containing task details.
    """
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
