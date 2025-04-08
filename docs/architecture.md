# avspl1t General Architecture

The avspl1t system is segmented into three separate software components, each with their own purpose. This document serves to explain the general architecture of the system.

## Jobs vs. Tasks

These terms are used differently in the avspl1t system, and are critical to understanding it properly.

A "job" is a unit of work which a client would like to be done by the avspl1t system. In the case of an "AV1 encode" job - the only job type the avspl1t system is currently built to understand - the input is a video file and the output is an HLS manifest and a set of AV1-encoded HLS segments. How this job is completed is abstracted away, as far as the client is concerned - all the client needs to know is that by handing the job to the avspl1t coordinator, the job will eventually be completed with the expected result.

A "task" is a unit of work to be performed by a worker. A job will include multiple tasks, and often the completion of one task will prompt the coordinator to create new tasks. For example, an encode job begins with a "split" task, splitting the input file into segments, which is followed by a number of "encode" tasks. Once all of the "encode" tasks are completed, a "generateManifest" task is triggered to finalize the process.

## Coordinator

The coordinator is a central server responsible for managing workloads - receiving them from clients and distributing them to workers. The coordinator is backed by a SQL database server, and uses transactions for all interactions with the database server. The coordinator is built so as to be stateless (all state is in the SQL database) and not to depend on exclusive access to that database. This allows multiple coordinator servers to be run - workers and clients can then be pointed to a load balancer or DNS name in a way that cleanly handles coordinator failover. The underlying database server can then be replicated for failover using mechanisms available from any major SQL server today.

Clients talk to the coordinator to submit jobs and to check the status of jobs. The coordinator then splits the jobs into tasks and distributes them to workers. Workers request tasks from the coordinator, complete the assigned task, and report back with the result.

## Worker

The worker is, for the most part, a simple loop - request a task from the coordinator, perform the task, report back. The worker contains the code to download and upload files and interface with FFmpeg for video encoding. Multiple instances of the worker can (and should!) be run, allowing the benefits of avspl1t's distributed architecture to be realized.

## Client

The client is a piece of software that allows interacting with the job creation and status APIs exposed by the coordinator. In a larger system, the coordinator would likely be connected to another software system, which integrates with these APIs. The client is supplied to allow interacting with the coordinator at a basic level, demonstrating the power and functionality of the system.

## File Storage

File storage is abstracted, such that the same high-level types are used to represent files and folders. Only the client and worker need to understand the file storage types - the coordinator never directly touches any of these files, and only interacts with metadata, and can thus pass them through to and from clients and workers. A file must be able to be downloaded, and a folder must be able to accept uploaded files.

avspl1t currently supports two file storage APIs - the local filesystem and Amazon S3, a commercial object storage service. A distributed filesystem like NFS can be mounted so as to be used like a local filesystem, making this method useful even in distributed settings. Amazon S3 allows code running in different environments to store and retrieve objects, and is also useful as an ultimate destination for encoded video, as it can then be served directly from the location to which it is output by avspl1t (or through a connected CDN). Many other object storage services also offer S3-compatible APIs, making them usable by avspl1t through this method.
