# avspl1t Coordinator Server Documentation

## Basic Architecture

The coordinator server runs a gRPC API server. Workers and clients both make requests to this server. The coordinator is stateless. All data is stored in an underlying SQL server. In development, SQLite would likely be appropriate for this, and would make automated testing of the coordinator easier! In production, it should be possible to swap this for PostgreSQL, which can be run separately and configured for failover. The coordinator, too, can then fail over - since it is stateless, any coordinator will work equally well, and multiple can be run simultaneously! One condition must be true, though - any database request that could cause race conditions must be in a transaction. This mostly applies to workers requesting a new task - the process of retrieving that task and marking it as in progress must be completed atomically. Other requests shouldn't run into this issue!

The coordinator needs to know very little about the process of actually completing a task. All the coordinator neds to know is how jobs relate to each other and how jobs relate to tasks. The details of this are below!

All API requests are unauthenticated. avspl1t is assumed to be running in a trusted environment, where only trusted code can send requests to the coordinator server (due to, for example, a firewall).

## Data Model

For the most part, the data model of what should be stored in the database matches exactly what is in the protobuf file. There are a few notable exceptions:

- Filesystem data can just be serialized to binary and stored in a binary format in the database. The coordinator doesn't need to understand this data, so building database tables for it is unnecessary!
- Tasks must be linked to jobs and have some other elements, explaned below.
- The percentage complete for a job is calculated, not stored in the database.

All timestamps in the database can be automatically set by the database based on the time of creation.

Some notes on a few specific parts of the data model that might not be self-explanatory from the proto file are below!

### Jobs

The only job supported right now is AV1 encoding. For simplicity, we only have one option, the constant quality (CRF) factor. The resolution will be the same as the input resolution. More encode options could be added here in the future - as a proof of concept system, we have avoided adding unnecessary complexity and focused on demonstrating the baseline functionality.

### Tasks

Tasks in the database must have some extra fields:

- Completed boolean
- Assigned worker ID
- Last heartbeat from worker
- Index (used only for encode tasks, to order them)

Workers don't need to know about these, so they are not stored in the proto file.

## Detailed API Request Specifications

### Submit Job

When a job is submitted by a client, the coordinator should do the following:

- Add a new job to the database, with details matching those of the submitted job. Ask the SQL server to return the generated ID, and store that ID to return to the client.
- Create a SplitVideoTask with details matching the job. The output directory for the task should be the working directory for the job.

### Get Job

Get the requested job from the database and return the details. The percent complete should be 0 if only one task is associated with the job (i.e. it has not yet been split), and [# of completed tasks for the job]/[# of tasks for the job] otherwise, rounded to the nearest integer. This will provide a rough estimate of how much of the encode has been completed.

### Get Task

When a worker requests a task, one should be retrieved from the database and marked as "in progress" for that worker simultaneously. Tasks available to be requested should match the condition `!completed && (!worker || heartbeat more than 15 seconds ago)` - completed tasks should never be given to a worker, and in-progress tasks should only be reassigned if a heartbeat has not been seen recently. The most recently created task matching these should be used. (This is a tradeoff - it essentially means that recently submitted jobs will be resource-starved if older jobs remain in progress. The task allocation strategy is currently chosen for simplicity. New tasks will wait in a queue, rather than attempting to maximize simultaneous progress for all jobs. Advances on this technology could optimize the task allocation strategy for different use cases.)

### Heartbeat

This request should simply update the latest heartbeat time for the submitted task ID so long as the worker ID matches the currently assigned worker on the task.

### Finish Task

In all cases, this should mark the task as finished. Some additional work is also necessary here.

If the task failed, the job it is associated with should be marked as failed, and all tasks associated with that job should be marked as completed (cancelled) to stop work on the job. We assume failures are nonrecoverable and not transient. This is a possible area of future improvement, as is better reporting of the reasons for a failure. For now, this is included as a failsafe to prevent jobs that are impossible to complete from wasting resources.

Additional steps should also take place depending on the type of the completed task.

**Split video task**

Encode tasks should be created. For each generated file in the split video finish message, a new encode task should be created, with the generated file as the input file, the job's output directory as the output directory, and the job's CRF as the CRF. The index on the encode task should be equal to its position in the list of generated files received from the split video task.

**Encode task**

If all other encode tasks are also finished, a generate manifest task should be created. All encode tasks include a File for the created segment in their finish message. These Files should be come the Files for the generate manifest task, in order of the index of the encode task. The output directory for the encode task and generate manifest task should be the same. Ordering is important here and must be maintained.

**Generate manifest task**

After this task completes, the entire job should be marked as complete. The generated manifest file included in the finish message should become the generated manifest file for the entire job.
