# avspl1t Coordinator

This folder contains the coordinator server implementation for the avspl1t system. The coordinator server is a Python application that tracks jobs/tasks across the entire system, and is the central point of control for the system.

## Key files

(in progress...)

## Setup

1. Duplicate [config_example.json](config_example.json) and rename to `config.json`.

   - Fill in your configuration details.
   - Note that the `maxWorkers` field controls how many threads the coordinator can use to process incoming gRPC requests at the same time. It **does not** limit the number of worker processes or clients that can connect.

2. Install the python dependencies for the server (this requires `poetry` to be installed):

```
poetry install
```

Note that Poetry dependencies are shared between all components of the avspl1t system. You only need to run this command once, no matter which of the three components you're looking to run.

## Usage

1. Start coordinator (make sure you are in the coordinator folder):

```
poetry run python main.py
```

## Testing

1. Clear your `.db` file (e.g., "test.db") before running the automated tests.

2. Navigate into [tests/](tests/) folder:

```
cd tests
```

3. Start tests:

```
poetry run pytest
```
