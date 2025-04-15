# avspl1t Worker

This folder contains the worker implementation for the avspl1t system. Worker instances perform the underlying computational work. By spinning up more worker instances, the capacity of the avspl1t system can be increased, and the end-to-end latency of an encode job can be decreased, through splitting the encoding of different segments among an increased number of workers.

## Setup

1. Duplicate [config_example.json](config_example.json) and rename to `config.json`.

   - Fill in your configuration details.
   - The host and port are for the coordinator server to be used.
   - The worker ID must be unique.

2. Install the python dependencies for the server (this requires `poetry` to be installed):

```
poetry install
```

Note that Poetry dependencies are shared between all components of the avspl1t system. You only need to run this command once, no matter which of the three components you're looking to run.

3. Ensure `ffmpeg` is installed.

## Usage

To run the worker, run:

```
poetry run python main.py
```

The worker will continue running until stopped.

## Testing

1. Navigate into [tests/](tests/) folder:

```
cd tests
```

2. Start tests:

```
poetry run pytest
```
