# Implements EncodeVideoTask
import subprocess
import tempfile
import shlex
import shutil
from pathlib import Path
from logic.files import file_to_ext, download_file, upload_file
from proto.avspl1t_pb2 import EncodeVideoFinishMessage

def encode_video(task):
  print("Running encode task...")
  with tempfile.TemporaryDirectory() as tmpdirname:
    # Get video file into temp dir
    ext = file_to_ext(task.encode_video_task.input_file)
    download_file(task.encode_video_task.input_file, tmpdirname + '/input.' + ext)
    # Encode with FFmpeg
    # cmd = f'ffmpeg -i {tmpdirname}/input.{ext} -c:a libmp3lame -c:v librav1e -qp {task.encode_video_task.crf} -f hls -copyts -hls_playlist_type vod -movflags +faststart -flags +cgop -hls_list_size 0 -hls_time 1000 -hls_segment_type fmp4 -muxdelay 0 {tmpdirname}/output.m3u8'
    cmd = f'ffmpeg -i {tmpdirname}/input.{ext} -c:a copy -c:v libx265 -crf {task.encode_video_task.crf} -copyts -muxdelay 0 {tmpdirname}/output.ts'
    subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pathlist = list(Path(tmpdirname).glob("*"))
    shutil.copy(tmpdirname + "/output.ts", tmpdirname + "/output_" + str(task.encode_video_task.index) + ".ts")
    # Build output
    #if (task.encode_video_task.index == 0):
    #  upload_file(task.encode_video_task.output_directory, Path(tmpdirname + "/init.mp4"))
    upload = upload_file(task.encode_video_task.output_directory, Path(tmpdirname + "/output_" + str(task.encode_video_task.index) + ".ts"))
    return EncodeVideoFinishMessage(generated_file=upload)