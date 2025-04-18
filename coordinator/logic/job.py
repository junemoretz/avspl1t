# Handle Job-level Logic for Coordinator
from logic.utils import get_path_from_file, get_path_from_folder, timestamp_from_sql
from proto.avspl1t_pb2 import Job, JobDetails, AV1EncodeJob, File, Folder


def create_job(database, ph, job):
    """
    Create a new job in the database.

    Args:
        database (DBLogic): The database logic object.
        ph (str): The placeholder for SQL queries based on the database type.
        job (AV1EncodeJob): The AV1EncodeJob object containing job details.

    Returns:
        str: The ID of the created job.
    """
    input_path = get_path_from_file(job.input_file)
    input_file_proto = job.input_file.SerializeToString()

    output_path = get_path_from_folder(job.output_directory)
    output_dir_proto = job.output_directory.SerializeToString()

    crf = job.crf
    seconds_per_segment = job.seconds_per_segment

    with database.get_db() as conn:
        cur = conn.cursor()
        # add the job to the database
        if database.db_type == "postgres":
            cur.execute(
                f"""
                INSERT INTO jobs (input_file, input_file_proto, output_dir, output_dir_proto, crf, seconds_per_segment) 
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
                RETURNING id
                """,
                (input_path, input_file_proto, output_path,
                 output_dir_proto, crf, seconds_per_segment),
            )

            # get the job ID of the newly created job
            job_id = cur.fetchone()[0]
        else:  # SQLite
            cur.execute(
                f"""
                INSERT INTO jobs (input_file, input_file_proto, output_dir, output_dir_proto, crf, seconds_per_segment) 
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
                """,
                (input_path, input_file_proto, output_path,
                 output_dir_proto, crf, seconds_per_segment),
            )

            # get the job ID of the newly created job
            job_id = cur.execute(
                "SELECT last_insert_rowid()").fetchone()[0]

        # create the split task
        cur.execute(
            f"""
            INSERT INTO tasks (job_id, type, input_file, input_file_proto, output_dir, output_dir_proto, crf) 
            VALUES ({ph}, 'split', {ph}, {ph}, {ph}, {ph}, {ph})
            """,
            (job_id, input_path, input_file_proto,
             output_path, output_dir_proto, crf),
        )

    return str(job_id)


def get_job(database, ph, job_id):
    """
    Get a job by its ID.

    Args:
        database (DBLogic): The database logic object.
        ph (str): The placeholder for SQL queries based on the database type.
        job_id (str): The ID of the job.
    Returns:
        Job: The Job object containing job details.
    """
    with database.get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM jobs WHERE id = {ph}",
            (job_id,),
        )
        job = cur.fetchone()

        if not job:
            return None

        # compute the percent complete
        cur.execute(
            f"SELECT COUNT(*) FROM tasks WHERE job_id = {ph}",
            (job_id,),
        )
        total = cur.fetchone()[0]
        cur.execute(
            f"SELECT COUNT(*) FROM tasks WHERE job_id = {ph} AND completed = TRUE",
            (job_id,),
        )
        completed = cur.fetchone()[0]

        percent_complete = int((completed / total) * 100) if total > 0 else 0

        input_file = File()
        input_file.ParseFromString(job['input_file_proto'])

        output_dir = Folder()
        output_dir.ParseFromString(job['output_dir_proto'])

        manifest_file = File()
        if job['manifest_file_proto']:
            manifest_file.ParseFromString(job['manifest_file_proto'])

        # create a Job object
        job_details = JobDetails(
            av1_encode_job=AV1EncodeJob(
                input_file=input_file,
                output_directory=output_dir,
                working_directory=output_dir,
                crf=job['crf'],
                seconds_per_segment=job['seconds_per_segment'],
            )
        )

        job_obj = Job(
            id=str(job['id']),
            finished=(job['status'] == 'complete'),
            failed=(job['status'] == 'failed'),
            percent_complete=percent_complete,
            generated_manifest=manifest_file,
            job_details=job_details,
            created_at=timestamp_from_sql(job['created_at']),
        )

        return job_obj
