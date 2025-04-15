# Implements GenerateManifestTask
import tempfile
from logic.files import file_to_name, upload_file
from proto.avspl1t_pb2 import GenerateManifestFinishMessage
from pathlib import Path

def generate_manifest(task):
  print("Running generate manifest task...")
  with tempfile.TemporaryDirectory() as tmpdirname:
    with open(tmpdirname + "/manifest.m3u8", "w") as f:
      f.write(f'#EXTM3u\n#EXT-X-VERSION:7\n#EXT-X-TARGETDURATION:{task.generate_manifest_task.seconds_per_segment}\n#EXT-X-MEDIA-SEQUENCE:0\n#EXT-X-PLAYLIST-TYPE:VOD\n#EXT-X-MAP:URI="init.mp4"\n')
      for file in task.generate_manifest_task.files:
        f.write(f'#EXTINF={task.generate_manifest_task.seconds_per_segment},\n{file_to_name(file)}\n')
      f.write('#EXT-X-ENDLIST\n')
    upload = upload_file(task.generate_manifest_task.output_directory, Path(tmpdirname + "/manifest.m3u8"))
    return GenerateManifestFinishMessage(generated_file=upload)