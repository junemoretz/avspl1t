from proto.avspl1t_pb2 import File, FSFile, S3File, Folder, FSFolder, S3Folder
from pathlib import Path
import tempfile
import shutil

def download_s3_file(S3File source, Path destination):
  pass
  
def upload_s3_file(S3Folder folder, Path source):
  pass

def download_fs_file(FSFile source, Path destination):
  shutil.copy(source.path, destination)

def upload_fs_file(FSFolder folder, Path source):
  shutil.copy(source, folder.path)

def download_file(File source, Path destination):
  if source.fsfile:
    download_fs_file(source, destination)
  elif source.s3file:
    download_s3_file(source, destination)

def upload_file(Folder folder, Path source):
  if folder.fsfolder:
    upload_fs_file(folder, source)
  elif folder.s3folder:
    upload_s3_file(folder, source)