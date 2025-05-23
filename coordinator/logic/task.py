# Handle Task-level Logic for Coordinator
from datetime import datetime, timezone, timedelta
from logic.utils import timestamp_from_sql, get_path_from_file
from proto.avspl1t_pb2 import Task, SplitVideoTask, EncodeVideoTask, GenerateManifestTask, File, Folder


def assign_next_task(database, ph, worker_id, heartbeat_timeout):
    """
    Assign the next task to a worker.
    Args:
        database (DBLogic): The database logic object.
        ph (str): The placeholder for SQL queries based on the database type.
        worker_id (str): The ID of the worker to assign the task to.
        heartbeat_timeout (int): The timeout for the worker's heartbeat.
    Returns:
        Task: The Task object containing task details.
    """
    now = datetime.now(timezone.utc)
    with database.get_db() as conn:
        cur = conn.cursor()
        # Find most recent task that meets the criteria:
        # !completed && (!worker || heartbeat more than heartbeat_timeout ago)
        cur.execute(
            f"""
            SELECT * FROM tasks
            WHERE completed = FALSE AND (assigned_worker IS NULL OR last_heartbeat IS NULL OR last_heartbeat < {ph})
            ORDER BY id DESC LIMIT 1""",
            (now - timedelta(seconds=heartbeat_timeout),),
        )
        task = cur.fetchone()

        # No available task meets assignment conditions; return None
        if not task:
            return None
        # Else, mark the task as assigned to the worker
        cur.execute(
            f"UPDATE tasks SET assigned_worker = {ph}, last_heartbeat = {ph} WHERE id = {ph}",
            (worker_id, now, task['id']),
        )
        print(f"Assigned task {task['id']} to worker {worker_id}")
        return task


def build_task_proto(database, ph, task, job):
    """
    Build a Task protobuf object from the task and job details.
    Args:
        database (DBLogic): The database logic object.
        ph (str): The placeholder for SQL queries based on the database type.
        task (Task): The Task object containing task details.
        job (Job): The Job object containing job details.
    Returns:
        Task: The Task protobuf object.
    """
    now = datetime.now(timezone.utc)

    input_file = File()
    if task['input_file_proto']:
        # only split and encode tasks have input files
        input_file.ParseFromString(task['input_file_proto'])

    output_directory = Folder()
    if task['output_dir_proto']:
        output_directory.ParseFromString(task['output_dir_proto'])

    # construct correct task object based on type
    if task['type'] == 'split':
        task_obj = Task(
            split_video_task=SplitVideoTask(
                input_file=input_file,
                output_directory=output_directory,
                seconds_per_segment=job['seconds_per_segment']
            )
        )
    elif task['type'] == 'encode':
        task_obj = Task(
            encode_video_task=EncodeVideoTask(
                input_file=input_file,
                output_directory=output_directory,
                crf=task['crf'],
                index=task['task_index'],
            )
        )
    elif task['type'] == 'manifest':
        with database.get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT * FROM tasks WHERE job_id = {ph} AND type = 'encode' AND completed = TRUE ORDER BY task_index ASC
                """,
                (task['job_id'],))
            manifest_files = cur.fetchall()

            task_obj = Task(
                generate_manifest_task=GenerateManifestTask(
                    files=[
                        File().FromString(et['output_file_proto'])
                        for et in manifest_files if et['output_file_proto']
                    ],
                    output_directory=output_directory,
                    seconds_per_segment=job['seconds_per_segment'],
                ),
            )
    else:
        return None

    task_obj.id = str(task['id'])
    task_obj.created_at.CopyFrom(
        timestamp_from_sql(task['last_heartbeat'] or now))
    return task_obj


def handle_split_finish(conn, ph, task, request):
    """
    Handle the completion of a split task.
    Args:
        conn (postgres.Connection): The database connection.
        ph (str): The placeholder for SQL queries based on the database type.
        task (dict): The task details.
        request (Task): The Task object containing task details.
    """
    # Update the task with the output file paths
    for i, file_msg in enumerate(request.split_video_finish_message.generated_files):
        path = get_path_from_file(file_msg)
        serialized = file_msg.SerializeToString()

        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO tasks (job_id, type, input_file, input_file_proto, output_dir, output_dir_proto, crf, task_index)
            VALUES ({ph}, 'encode', {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
            """,
            (task['job_id'], path, serialized, task['output_dir_proto'],
             task['output_dir_proto'], task['crf'], i),
        )


def handle_encode_finish(conn, ph, task):
    """
    Handle the completion of an encode task.
    Args:
        conn (postgres.Connection): The database connection.
        task (dict): The task details.
    """
    # If the task is an encode task, check if all encode tasks are completed
    # and if so, create a manifest task
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT COUNT(*) FROM tasks WHERE job_id = {ph} AND completed = FALSE
        """,
        (task['job_id'],))
    remaining = cur.fetchone()[0]

    if remaining == 0:
        cur.execute(
            f"""
            INSERT INTO tasks (job_id, type, output_dir, output_dir_proto) 
            VALUES ({ph}, 'manifest', {ph}, {ph})
            """,
            (task['job_id'], task['output_dir'], task['output_dir_proto'])
        )


def handle_manifest_finish(conn, ph, task, request):
    """
    Handle the completion of a manifest task.
    Args:
        conn (postgres.Connection): The database connection.
        ph (str): The placeholder for SQL queries based on the database type.
        task (dict): The task details.
        request (Task): The Task object containing task details.
    """
    if request.HasField("generate_manifest_finish_message"):
        cur = conn.cursor()
        # If the task is a manifest task, update the job status to complete
        finish_msg_file = request.generate_manifest_finish_message.generated_file
        file_path = get_path_from_file(finish_msg_file)
        file_proto = finish_msg_file.SerializeToString()

        cur.execute(
            f"""
            UPDATE tasks
            SET output_file = {ph}, output_file_proto = {ph}
            WHERE id = {ph}
            """,
            (file_path, file_proto, request.task_id)
        )
        cur.execute(
            f"""
            UPDATE jobs
            SET status = 'complete',
                manifest_file = {ph}, manifest_file_proto = {ph}
            WHERE id = {ph}
            """,
            (file_path,
             file_proto,
             task['job_id'])
        )
