import sys
import time
import os
import subprocess
import threading
from pathlib import Path

sys.path.append('../')  # Adjust the path to import the main module
from logic.splitVideo import split_video
from proto.avspl1t_pb2 import Task, SplitVideoTask, File, FSFile, Folder, FSFolder

def test_split_video():
  input = str(Path('resources/video.mp4').absolute())
  inputFile = File(fsfile=FSFile(path=input))
  output = str(Path('output').absolute())
  outputFolder = Folder(fsfolder=FSFolder(path=output))
  split_task = SplitVideoTask(input_file=inputFile,output_directory=outputFolder,seconds_per_segment=3)
  task = Task(id="1", split_video_task=split_task)
  split_video(task)
  # Check output
  pathlist = list(Path(output).glob("*"))
  assert len(pathlist) == 4, "Four segments should be generated"
  assert "segment" in str(pathlist[0]), "Segments are named correctly"