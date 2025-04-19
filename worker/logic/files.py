from proto.avspl1t_pb2 import File, FSFile, S3File, Folder, FSFolder, S3Folder
from pathlib import Path
import tempfile
import shutil
import os
import boto3

def download_s3_file(source, destination):
  client = boto3.client(
    's3',
    aws_access_key_id=source.credentials.access_key_id,
    aws_secret_access_key=source.credentials.secret_access_key,
    endpoint_url=source.credentials.endpoint,
    region_name=source.credentials.region
  )
  client.download_file(source.bucket, source.path, destination)
  
def upload_s3_file(folder, source):
  client = boto3.client(
    's3',
    aws_access_key_id=folder.credentials.access_key_id,
    aws_secret_access_key=folder.credentials.secret_access_key,
    endpoint_url=folder.credentials.endpoint,
    region_name=folder.credentials.region
  )
  path = folder.path + "/" + Path(source).name
  with open(source, "rb") as file:
    if 'm3u8' in path:
      client.upload_fileobj(file, folder.bucket, path, ExtraArgs={'ContentType': 'audio/mpegurl'})
    else:
      client.upload_fileobj(file, folder.bucket, path)
  return File(s3file=S3File(bucket=folder.bucket,path=path,credentials=folder.credentials))

def download_fs_file(source, destination):
  shutil.copy(source.path, destination)

def upload_fs_file(folder, source):
  path = shutil.copy(source, folder.path)
  return File(fsfile=FSFile(path=path))

def download_file(source, destination):
  if source.WhichOneof("file") == "fsfile":
    download_fs_file(source.fsfile, destination)
  elif source.WhichOneof("file") == "s3file":
    download_s3_file(source.s3file, destination)

def upload_file(folder, source):
  if folder.WhichOneof("folder") == "fsfolder":
    return upload_fs_file(folder.fsfolder, source)
  elif folder.WhichOneof("folder") == "s3folder":
    return upload_s3_file(folder.s3folder, source)

def file_to_ext(file):
  if file.WhichOneof("file") == "fsfile":
    return file.fsfile.path.split(".")[-1]
  elif file.WhichOneof("file") == "s3file":
    return file.s3file.path.split(".")[-1]

def file_to_name(file):
  if file.WhichOneof("file") == "fsfile":
    return file.fsfile.path.split("/")[-1]
  elif file.WhichOneof("file") == "s3file":
    return file.s3file.path.split("/")[-1]
