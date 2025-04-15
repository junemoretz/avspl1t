# Implements SplitVideoTask
import subprocess
import tempfile
import shlex
from pathlib import Path
from logic.files import file_to_ext, download_file, upload_file
from proto.avspl1t_pb2 import SplitVideoFinishMessage

def split_video(task):
  with tempfile.TemporaryDirectory() as tmpdirname:
    # Get video file into temp dir
    ext = file_to_ext(task.split_video_task.input_file)
    download_file(task.split_video_task.input_file, tmpdirname + '/input.' + ext)
    # Split with FFmpeg
    secs = task.split_video_task.seconds_per_segment
    cmd = f'ffmpeg -i {tmpdirname}/input.{ext} -c:a copy -c:v h264 -preset ultrafast -crf 17 -map 0:v -map 0:a -reset_timestamps 1 -sc_threshold 0 -g {secs} -force_key_frames "expr:gte(t, n_forced * {secs})" -segment_time {secs} -f segment {tmpdirname}/segment_%03d.mp4'
    subprocess.run(shlex.split(cmd)) 
    # Iterate over output
    pathlist = Path(tmpdirname).glob('segment*')
    files = []
    for path in pathlist:
      upload = upload_file(task.split_video_task.output_directory, path)
      files.append(upload)
    return SplitVideoFinishMessage(generated_files=files)