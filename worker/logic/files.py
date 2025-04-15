from proto.avspl1t_pb2 import File, FSFile, S3File, Folder, FSFolder, S3Folder
from pathlib import Path
import tempfile
import shutil

def download_s3_file(source, destination):
  pass
  
def upload_s3_file(folder, source):
  pass

def download_fs_file(source, destination):
  shutil.copy(source.path, destination)

def upload_fs_file(folder, source):
  path = shutil.copy(source, folder.path)
  return File(fsfile=FSFile(path=path))

def download_file(source, destination):
  if source.fsfile:
    download_fs_file(source.fsfile, destination)
  elif source.s3file:
    download_s3_file(source.s3file, destination)

def upload_file(folder, source):
  if folder.fsfolder:
    return upload_fs_file(folder.fsfolder, source)
  elif folder.s3folder:
    return upload_s3_file(folder.s3folder, source)

def file_to_ext(file):
  if file.fsfile:
    return file.fsfile.path.split(".")[-1]
  elif file.s3file:
    return file.s3file.path.split(".")[-1]

def file_to_name(file):
  if file.fsfile:
    return file.fsfile.path.split("/")[-1]
  elif file.s3file:
    return file.s3file.path.split("/")[-1]
