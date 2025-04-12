# avspl1t Coordinator

This folder contains the coordinator server implementation for the avspl1t system. The coordinator server is a Python application that tracks jobs/tasks across the entire system, and is the central point of control for the system.

## Setup

1. Duplicate [config_example.json](config_example.json) and rename to `config.json`.

   - Fill in your configuration details.

2. Install the python dependencies for the server (this requires `poetry` to be installed):

```
poetry install
```

## Usage

1. Start coordinator (make sure you are in the coordinator folder):

```
poetry run python main.py
```

(in progress)

## Testing

Clear your `.db` file (e.g., "test.db") before running the automated tests.

(in progress)
