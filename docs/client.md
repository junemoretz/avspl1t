# avspl1t Client Documentation

The avspl1t client provides a command-line based interface for creating and checking the status of avspl1t jobs.

For creating jobs, the client provides a CLI interface allowing the attributes of a job to be specified for submission to avspl1t. This includes a number of useful features. When using local folders for working and output directories, the client will automatically create the folders if they do not exist. A local input file can also be supplied alongside an "upload to S3" option, which will upload the input file to Amazon S3 for use by avspl1t.

Retrieving jobs is also possible via a (simpler) CLI interface, which simply reports on the status of a job, including providing a link to its output manifest if the job is complete.
