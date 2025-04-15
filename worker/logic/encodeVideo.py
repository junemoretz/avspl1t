# Implements EncodeVideoTask
from files import file_to_ext, download_file

def encode_video(task):
  with tempfile.TemporaryDirectory() as tmpdirname:
    # Get video file into temp dir
    #ext = file_to_ext(task.)
    # Encode with FFmpeg
    # Build output
