import click
import json
import grpc
import os
import boto3
from pathlib import Path
from urllib.parse import urlparse
from proto.avspl1t_pb2 import JobDetails, AV1EncodeJob, FSFile, File, Folder, FSFolder, JobId, Job, S3Credentials, S3File, S3Folder
from proto.avspl1t_pb2_grpc import CoordinatorServiceStub

TEST_PORT=51515

# Load config file
config = None
stub = None
with open('config.json', 'r') as f:
    config = json.load(f)
    host = config['host']
    port = config['port']
    if (os.environ.get('TESTING')):
        host = 'localhost'
        port = TEST_PORT
    channel = grpc.insecure_channel(f'{host}:{port}')
    stub = CoordinatorServiceStub(channel)

def validateS3():
    if not 'access_key_id' in config['s3']:
        click.echo("You must specify an access key ID to use S3!")
        exit(1)
    if not 'secret_access_key' in config['s3']:
        click.echo("You must specify a secret access key to use S3!")
        exit(1)
    if not 'region' in config['s3']:
        click.echo("You must specify a region to use S3!")
        exit(1)
    if not 'endpoint' in config['s3']:
        click.echo("You must specify an endpoint to use S3!")
        exit(1)
    return True

def getS3Credentials():
    return S3Credentials(access_key_id=config['s3']['access_key_id'], secret_access_key=config['s3']['secret_access_key'], region=config['s3']['region'], endpoint=config['s3']['endpoint'])

def validateDir(dir):
    dir = dir.strip("/")
    if not ':' in dir:
        click.echo("S3 directories must be in bucket:path format!")
        exit(1)
    return dir

def s3Upload(path, bucket, destPath):
    # Initialize
    client = boto3.client(
        's3',
        aws_access_key_id=getS3Credentials().access_key_id,
        aws_secret_access_key=getS3Credentials().secret_access_key,
        endpoint_url=getS3Credentials().endpoint,
        region_name=getS3Credentials().region
    )
    with path.open("rb") as file:
        with click.progressbar(length=os.stat(path).st_size, label='Uploading input file to S3') as bar:
            def callback(size):
                bar.update(bar._completed_intervals + size)
            client.upload_fileobj(file, bucket, destPath, Callback=callback)

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
@click.option('--crf', default=26, help='Constant Rate Factor (video quality) - lower is better')
def create(input, uploadtos3, workingdir, workingdirs3, outputdir, outputdirs3, secondspersegment, crf):
    # Input validation
    if ((not 's3' in config or not validateS3()) and (uploadtos3 or workingdirs3 or outputdirs3)):
        click.echo("You must configure S3 in config.json to use S3!")
        exit(1)
    if (not input):
        click.echo("An input file is required.")
        exit(1)
    if (not workingdir and not workingdirs3):
        click.echo("You must specify a working directory.")
        exit(1)
    if (not outputdir and not outputdirs3):
        click.echo("You must specify an output directory.")
        exit(1)
    if workingdirs3:
        workingdirs3 = validateDir(workingdirs3)
    if outputdirs3:
        outputdirs3 = validateDir(outputdirs3)
    # Create directories if needed
    if workingdir:
        workingdir.mkdir(parents=True, exist_ok=True)
    if outputdir:
        outputdir.mkdir(parents=True, exist_ok=True)
    # Construct Protobuf request
    input_protofile = None
    working = None
    output = None
    if uploadtos3:
        bucket = workingdirs3.split(':')[0]
        path = workingdirs3.split(':')[1]
        uploadPath = path + "/input" + input.suffix
        s3Upload(input, bucket, uploadPath)
        input_protofile = File(s3file=S3File(bucket=bucket, path=uploadPath, credentials=getS3Credentials()))
    else:
        input_protofile = File(fsfile=FSFile(path=str(input.absolute())))
    if workingdir:
        working = Folder(fsfolder=FSFolder(path=str(workingdir.absolute())))
    else:
        working = Folder(s3folder=S3Folder(bucket=workingdirs3.split(':')[0], path=workingdirs3.split(':')[1], credentials=getS3Credentials()))
    if outputdir:
        output = Folder(fsfolder=FSFolder(path=str(outputdir.absolute())))
    else:
        output = Folder(s3folder=S3Folder(bucket=outputdirs3.split(':')[0], path=outputdirs3.split(':')[1], credentials=getS3Credentials()))
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
        exit(1)
    # Construct and submit Protobuf request
    job_status = stub.GetJob(JobId(id=id))
    # Handle response
    if job_status.finished:
        click.echo("Job complete!")
        outputdir = job_status.job_details.av1_encode_job.output_directory
        if outputdir.WhichOneof("folder") == "fsfolder":
            click.echo(f'The HLS manifest can be found at:\n{outputdir.fsfolder.path}/manifest.m3u8')
        else:
            endpoint = getS3Credentials().endpoint
            bucket = outputdir.s3folder.bucket
            url = urlparse(endpoint)
            click.echo(f'The HLS manifest can be found at:\n{url.scheme}://{bucket}.{url.netloc}/{outputdir.s3folder.path}/manifest.m3u8')
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