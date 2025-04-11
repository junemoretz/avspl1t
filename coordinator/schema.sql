-- SQL schema for the coordinator service

DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS jobs;

CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    input_file TEXT NOT NULL,
    output_file TEXT NOT NULL,
    crf INTEGER NOT NULL, -- constate rate factor (encoding quality)
    status TEXT NOT NULL CHECK (status IN ('in_progress', 'complete', 'failed')) DEFAULT 'in_progress',
    manifest_file TEXT, -- path to the generated manifest file (if successful)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- timestamp when job was submitted
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    job_id INTEGER NOT NULL, -- link task to job
    type TEXT NOT NULL CHECK (type IN ('split', 'encode', 'manifest')),
    input_file TEXT,
    output_file TEXT,
    crf INTEGER,  -- constate rate factor (encoding quality); inherited from job
    completed BOOLEAN DEFAULT 0,
    failed BOOLEAN DEFAULT 0,
    assigned_worker TEXT,
    last_heartbeat TIMESTAMP, -- timestamp of the last heartbeat from the worker
    index INTEGER, -- used to order encode tasks
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);