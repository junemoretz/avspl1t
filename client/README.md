# avspl1t Client

This folder contains the client implementation for the avspl1t system, which can be used to submit jobs to the coordinator server and to view their status and results.

## Setup

1. Duplicate [config_example.json](config_example.json) and rename to `config.json`.

   - Fill in your configuration details.
   - The host and port are for the coordinator server to be used.
   - AWS credentials are optional, and are required to enable S3 features.

2. Install the python dependencies (this requires `poetry` to be installed):

```
poetry install
```

Note that Poetry dependencies are shared between all components of the avspl1t system. You only need to run this command once, no matter which of the three components you're looking to run.

## Usage

To run the client, run:

```
poetry run python main.py
```

To this, you can add the commands and flags you desire. Help pages exist to provide more information on the available commands! The following is the basic usage pattern:

```
poetry run python main.py create --input file.mp4 --workingDir /mnt/nas/tmp --outputDir /mnt/nas/output
```

(or:)

```
poetry run python main.py create --input file.mp4 --uploadToS3 --workingDirS3 bucketName:job1-tmp --outputDirS3 bucketName:job1-output
```

Once you've created a job:

```
poetry run python main.py get --id [id]
```

## Testing

(todo!)
