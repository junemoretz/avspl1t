# avspl1t Worker Documentation

At a high level, what a worker does is fairly simple - grab a task from the coordinator, do the task, then report back. This document primarily exists to explain what "doing the task" entails for each of the three types of task, as well as the file storage data model and how the worker interacts with it.

## File Storage

All file operations rely on a set of data structures that allow new external storage locations for files to be added without the rest of the code needing to be changed. A file storage location must have File and Folder protobuf messages. A File message should be sufficient for the file to be downloaded or retrieved, and a Folder should exist and be ready to accept uploads or new files. The native filesystem is the simplest example of this, and is the basic file storage location implemented here. All files are retrieved to or from temporary filesystem storage, allowing the rest of the worker to rely on the file storage subsystem to handle the movement of files between temporary storage and the file storage location.

### Amazon S3

The S3 data model includes a set of S3 credentials, which are forwarded to the worker for use when interacting with the S3 APIs. The "endpoint" may not be strictly necessary for S3 itself, but is necessary for S3-compatible APIs - for S3 itself, this will just be `s3.[region].amazonaws.com`. S3 paths can then be used as files and folders for the file storage system.

## Splitting Video Files

The worker should split the video file into equal length pieces, with the length based on the `seconds_per_segment` supplied, with FFmpeg, and upload the newly split video files to the provided output directory. It should return a File for each generated video file.

## Encoding a Segment

Segments should be encoded into H.265 MPEG-2 TS HLS segments using FFmpeg and placed into the output directory, and the generated file should be returned.

## Generating a HLS Manifest

A properly formed HLS manifest should be generated for the supplied files (with some assumptions for the moment about the contents of those files, as they should have been generated by the worker) and placed in the output directory.
