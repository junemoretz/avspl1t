-- PostgreSQL schema for the coordinator service

DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS jobs;

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    input_file TEXT NOT NULL,
    output_dir TEXT NOT NULL,
    crf INTEGER NOT NULL, -- constate rate factor (encoding quality)
    seconds_per_segment INTEGER NOT NULL, -- seconds per segment for splitting
    status TEXT NOT NULL CHECK (status IN ('in_progress', 'complete', 'failed')) DEFAULT 'in_progress',
    manifest_file TEXT, -- path to the generated manifest file (if successful)
    created_at TIMESTAMPTZ DEFAULT now() -- timestamp when job was submitted
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE, -- link task to job
    type TEXT NOT NULL CHECK (type IN ('split', 'encode', 'manifest')),
    input_file TEXT,
    output_dir TEXT,
    output_file TEXT,
    crf INTEGER,  -- constate rate factor (encoding quality); inherited from job
    completed BOOLEAN DEFAULT FALSE,
    failed BOOLEAN DEFAULT FALSE,
    assigned_worker TEXT,
    last_heartbeat TIMESTAMPTZ, -- timestamp of the last heartbeat from the worker
    task_index INTEGER -- used to order encode tasks
);