# Handle Job-level Logic for Coordinator
from logic.utils import timestamp_from_sql
from proto.avspl1t_pb2 import Job, File, FSFile, Folder, FSFolder, JobDetails, AV1EncodeJob


def create_job(database, job):
    """
    Create a new job in the database.

    Args:
        database (DBLogic): The database logic object.
        job (AV1EncodeJob): The AV1EncodeJob object containing job details.

    Returns:
        str: The ID of the created job.
    """
    input_path = job.input_file.fsfile.path
    output_path = job.output_directory.fsfolder.path
    crf = job.crf
    seconds_per_segment = job.seconds_per_segment

    with database.get_db() as conn:
        with conn.cursor() as cur:
            # add the job to the database
            cur.execute(
                """
                INSERT INTO jobs (input_file, output_dir, crf, seconds_per_segment) 
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (input_path, output_path, crf, seconds_per_segment),
            )

            # get the job ID of the newly created job
            job_id = cur.fetchone()[0]

            # create the split task
            cur.execute(
                "INSERT INTO tasks (job_id, type, input_file, output_dir, crf) VALUES (%s, 'split', %s, %s, %s)",
                (job_id, input_path, output_path, crf),
            )

    return str(job_id)


def get_job(database, job_id):
    """
    Get a job by its ID.

    Args:
        database (DBLogic): The database logic object.
        job_id (str): The ID of the job.
    Returns:
        Job: The Job object containing job details.
    """
    with database.get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM jobs WHERE id = %s",
                (job_id,),
            )
            job = cur.fetchone()

            if not job:
                return None

            # compute the percent complete
            cur.execute(
                "SELECT COUNT(*) FROM tasks WHERE job_id = %s",
                (job_id,),
            )
            total = cur.fetchone()[0]
            cur.execute(
                "SELECT COUNT(*) FROM tasks WHERE job_id = %s AND completed = TRUE",
                (job_id,),
            )
            completed = cur.fetchone()[0]

        percent_complete = int((completed / total) * 100) if total > 0 else 0

        # create a Job object
        job_details = JobDetails(
            av1_encode_job=AV1EncodeJob(
                input_file=File(fsfile=FSFile(path=job['input_file'])),
                output_directory=Folder(
                    fsfolder=FSFolder(path=job['output_dir'])),
                working_directory=Folder(
                    fsfolder=FSFolder(path=job['output_dir'])),
                crf=job['crf'],
                seconds_per_segment=job['seconds_per_segment'],
            )
        )

        job_obj = Job(
            id=str(job['id']),
            finished=(job['status'] == 'complete'),
            failed=(job['status'] == 'failed'),
            percent_complete=percent_complete,
            generated_manifest=File(fsfile=FSFile(
                path=job['manifest_file'] or '')),
            job_details=job_details,
            created_at=timestamp_from_sql(job['created_at']),
        )

        return job_obj
