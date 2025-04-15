import sys
import time
import os
import subprocess
import threading
from pathlib import Path

sys.path.append('../')  # Adjust the path to import the main module
from logic.splitVideo import split_video
from logic.encodeVideo import encode_video
from proto.avspl1t_pb2 import Task, SplitVideoTask, EncodeVideoTask, File, FSFile, Folder, FSFolder

def test_split_video():
  input = str(Path('resources/video.mp4').absolute())
  inputFile = File(fsfile=FSFile(path=input))
  output = str(Path('output').absolute())
  outputFolder = Folder(fsfolder=FSFolder(path=output))
  split_task = SplitVideoTask(input_file=inputFile,output_directory=outputFolder,seconds_per_segment=3)
  task = Task(id="1", split_video_task=split_task)
  split_video(task)
  # Check output
  pathlist = list(Path(output).glob("segment_*"))
  assert len(pathlist) == 4, "Four segments should be generated"

def test_encode_video():
  input = str(Path('resources/segment_000.ts').absolute())
  inputFile = File(fsfile=FSFile(path=input))
  output = str(Path('output').absolute())
  outputFolder = Folder(fsfolder=FSFolder(path=output))
  encode_task = EncodeVideoTask(input_file=inputFile,output_directory=outputFolder,crf=80)
  task = Task(id="1", encode_video_task=encode_task)
  encode_video(task)
  # Check output
  pathlist = list(Path(output).glob("output_*"))
  assert len(pathlist) == 1, "Encoded segment should be generated"
