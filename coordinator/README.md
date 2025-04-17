# avspl1t Coordinator

This folder contains the coordinator server implementation for the avspl1t system. The coordinator server is a Python application that tracks jobs/tasks across the entire system, and is the central point of control for the system.

## Key files

(in progress...)

## Setup

1. Duplicate [config_example.json](config_example.json) and rename to `config.json`.

   - Fill in your configuration details.
   - For `postgresUser`, use your computer username.
   - Note that the `maxWorkers` field controls how many threads the coordinator can use to process incoming gRPC requests at the same time. It **does not** limit the number of worker processes or clients that can connect.

2. Install the python dependencies for the server (this requires `poetry` to be installed):

```
poetry install
```

Note that Poetry dependencies are shared between all components of the avspl1t system. You only need to run this command once, no matter which of the three components you're looking to run.

## Usage

1. Start PostgreSQL:

Mac:

```
brew services start postgresql
```

Windows:

```
net start postgresql
```

Linux:

```
sudo systemctl start postgresql
```

2. Create database with your username and database name from `config.json`, e.g.,

```
createdb -U catherineyeh avspl1t
```

if `postgresUser` = catherineyeh, and `databaseFile` = avspl1t. This should only need to be run once.

3. Start coordinator (make sure you are in the coordinator folder):

```
poetry run python main.py
```

## Testing

1. Navigate into [tests/](tests/) folder:

```
cd tests
```

2. Start tests:

```
poetry run pytest
```
