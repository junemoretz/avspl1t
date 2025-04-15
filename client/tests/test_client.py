import sys
import time
import os
import subprocess
from utils import RPCServerForTest

sys.path.append('../')  # Adjust the path to import the main module
from proto.avspl1t_pb2 import JobDetails, AV1EncodeJob, FSFile, File, Folder, FSFolder, JobId, Job

def run_command(command):
  env = dict(os.environ, TESTING='true')
  output = subprocess.check_output(command.split(), cwd='../', env=env, text=True)
  return output

def run_command_error(command):
  env = dict(os.environ, TESTING='true')
  try:
    output = subprocess.check_output(command.split(), cwd='../', env=env)
    return 0
  except subprocess.CalledProcessError as exc:                                                                                                   
    return exc.returncode

def test_create_job():
  # Create test server
  server = RPCServerForTest()
  servicer = server.get_servicer()
  servicer.setSubmitResponse(JobId(id="5"))
  time.sleep(0.5) # wait for it to start
  # Run client
  output = run_command('poetry run python main.py create --input README.md --workingDir tests --outputDir tests')
  time.sleep(0.1)
  # Assertions
  assert "/README.md" in servicer.submit_job_request.av1_encode_job.input_file.fsfile.path, "Input file should be in request"
  assert "/tests" in servicer.submit_job_request.av1_encode_job.working_directory.fsfolder.path, "Working directory should be in request"
  assert "/tests" in servicer.submit_job_request.av1_encode_job.output_directory.fsfolder.path, "Output directory should be in request"
  assert "ID 5" in output, "Output should contain job ID"

def test_create_job_badargs():
  assert run_command_error('poetry run python main.py create --input README.md --workingDir tests') == 1, "Calling without output directory should fail"
  assert run_command_error('poetry run python main.py create --input README.md --outputDir tests') == 1, "Calling without output directory should fail"
  assert run_command_error('poetry run python main.py create --workingDir tests --outputDir tests') == 1, "Calling without input should fail"
  assert run_command_error('poetry run python main.py create --input nonexistent --workingDir tests --outputDir tests') != 0, "Calling with nonexistent input should fail"

def test_get_job_badargs():
  assert run_command_error('poetry run python main.py get') == 1, "Calling without ID should fail"

def test_get_job():
  # Create test server
  server = RPCServerForTest()
  servicer = server.get_servicer()
  servicer.setGetResponse(Job(percent_complete=10))
  time.sleep(0.5) # wait for it to start
  # Run client
  output = run_command('poetry run python main.py get --id 123')
  time.sleep(0.1)
  # Assertions
  assert servicer.get_job_request.id == "123", "Requested job ID should be correct"
  assert "in progress" in output, "Output should include job status"
  assert "10%" in output, "Output should include percent complete"
  servicer.setGetResponse(Job(finished=True))
  time.sleep(0.1)
  output = run_command('poetry run python main.py get --id 123')
  assert "complete" in output, "Output should include job ststus"
  servicer.setGetResponse(Job(failed=True))
  time.sleep(0.1)
  output = run_command('poetry run python main.py get --id 123')
  assert "failed" in output, "Output should include job ststus"
