# avspl1t

avspl1t is an experimental distributed video encoding system for AV1/HLS, built as a final project for Harvard CS2620 (Introduction to Distributed Computing).

## System Setup, Usage, and Testing

There are three components to the avspl1t system: the coordinator, worker, and client. Each of these has their own notes on setup/usage/testing. To use the avspl1t system, you will need a coordinator instance and at least one worker instance connected to it. You can then configure the client to point to your coordinator instance and use the client to create jobs.

To set up a coordinator server, reference [coordinator/README.md](coordinator/README.md).

To set up a worker, reference [worker/README.md](worker/README.md).

To set up and use the client, reference [client/README.md](client/README.md).

## Documentation

More comprehensive architecture and implementation level documentation (including engineering notebooks) is in the [docs/](docs/) folder. This documentation explains how the avspl1t system works, rather than how to use it. Usage documentation is primarily found in the component-level READMEs linked above.
