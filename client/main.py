import click
import json
import grpc
from pathlib import Path
from proto.avspl1t_pb2 import JobDetails, AV1EncodeJob, FSFile, File, Folder, FSFolder, JobId, Job
from proto.avspl1t_pb2_grpc import CoordinatorServiceStub

# Load config file
config = None
stub = None
with open('config.json', 'r') as f:
    config = json.load(f)
    host = config['host']
    port = config['port']
    channel = grpc.insecure_channel(f'{host}:{port}')
    stub = CoordinatorServiceStub(channel)

def validateS3():
    return True

@click.group()
def client():
    pass

@click.command()
@click.option('--input', type=click.Path(exists=True, dir_okay=False, path_type=Path), help='Input video file')
@click.option('--uploadToS3', is_flag=True, help='Upload input file to Amazon S3 before submitting to coordinator')
@click.option('--workingDir', type=click.Path(exists=False, file_okay=False, path_type=Path), help='Working directory')
@click.option('--workingDirS3', help='Working directory (Amazon S3)')
@click.option('--outputDir', type=click.Path(exists=False, file_okay=False, path_type=Path), help='Output directory')
@click.option('--outputDirS3', help='Output directory (Amazon S3)')
@click.option('--secondsPerSegment', default=2, help='Seconds in each generated HLS video segment')
@click.option('--crf', default=28, help='Constant Rate Factor (video quality) - lower is better')
def create(input, uploadtos3, workingdir, workingdirs3, outputdir, outputdirs3, secondspersegment, crf):
    # Input validation
    if ((not 's3' in config or not validateS3()) and (uploadtos3 or workingdirs3 or outputdirs3)):
        click.echo("You must configure S3 in config.json to use S3!")
        return
    if (not input):
        click.echo("An input file is required.")
        return
    if (not workingdir and not workingdirs3):
        click.echo("You must specify a working directory.")
        return
    if (not outputdir and not outputdirs3):
        click.echo("You must specify an output directory.")
        return
    # Create directories if needed
    workingdir.mkdir(parents=True, exist_ok=True)
    outputdir.mkdir(parents=True, exist_ok=True)
    # Construct Protobuf request
    input_protofile = None
    working = None
    output = None
    if not uploadtos3:
        input_protofile = File(fsfile=FSFile(path=str(input)))
    if workingdir:
        working = Folder(fsfolder=FSFolder(path=str(workingdir)))
    if outputdir:
        output = Folder(fsfolder=FSFolder(path=str(outputdir)))
    job = AV1EncodeJob(
        input_file=input_protofile,
        output_directory=output,
        working_directory=working,
        crf=crf,
        seconds_per_segment=secondspersegment,
    )
    # Submit to server
    job_id = stub.SubmitJob(JobDetails(av1_encode_job=job)).id
    # Handle response
    click.echo(f'Job submitted with ID {job_id}')

@click.command()
@click.option('--id', help='Job ID')
def get(id):
    if (not id):
        click.echo("You must specify a job ID.")
        return
    # Construct and submit Protobuf request
    job_status = stub.GetJob(JobId(id=id))
    # Handle response
    if job_status.finished:
        click.echo("Job complete!")
        # TODO include link to manifest
    elif job_status.failed:
        click.echo("Job failed.")
    else:
        click.echo("Job in progress.")
        click.echo(f'Currently {job_status.percent_complete}% complete.')

client.add_command(create)
client.add_command(get)

if __name__ == '__main__':
    if (not config or not 'host' in config or not 'port' in config):
        click.echo("You must have a config.json file with a host and port.")
        exit(1)
    client()