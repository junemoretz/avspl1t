# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: avspl1t.proto
# Protobuf Python Version: 6.30.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    30,
    1,
    '',
    'avspl1t.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ravspl1t.proto\x12\x0b\x63om.avspl1t\x1a\x1fgoogle/protobuf/timestamp.proto\"c\n\rS3Credentials\x12\x15\n\raccess_key_id\x18\x01 \x01(\t\x12\x19\n\x11secret_access_key\x18\x02 \x01(\t\x12\x0e\n\x06region\x18\x03 \x01(\t\x12\x10\n\x08\x65ndpoint\x18\x04 \x01(\t\"W\n\x06S3File\x12\x0e\n\x06\x62ucket\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\x12/\n\x0b\x63redentials\x18\x03 \x01(\x0b\x32\x1a.com.avspl1t.S3Credentials\"Y\n\x08S3Folder\x12\x0e\n\x06\x62ucket\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\x12/\n\x0b\x63redentials\x18\x03 \x01(\x0b\x32\x1a.com.avspl1t.S3Credentials\"\x16\n\x06\x46SFile\x12\x0c\n\x04path\x18\x01 \x01(\t\"\x18\n\x08\x46SFolder\x12\x0c\n\x04path\x18\x01 \x01(\t\"\\\n\x04\x46ile\x12%\n\x06s3file\x18\x01 \x01(\x0b\x32\x13.com.avspl1t.S3FileH\x00\x12%\n\x06\x66sfile\x18\x02 \x01(\x0b\x32\x13.com.avspl1t.FSFileH\x00\x42\x06\n\x04\x66ile\"h\n\x06\x46older\x12)\n\x08s3folder\x18\x01 \x01(\x0b\x32\x15.com.avspl1t.S3FolderH\x00\x12)\n\x08\x66sfolder\x18\x02 \x01(\x0b\x32\x15.com.avspl1t.FSFolderH\x00\x42\x08\n\x06\x66older\"\xbe\x01\n\x0c\x41V1EncodeJob\x12%\n\ninput_file\x18\x01 \x01(\x0b\x32\x11.com.avspl1t.File\x12.\n\x11working_directory\x18\x02 \x01(\x0b\x32\x13.com.avspl1t.Folder\x12-\n\x10output_directory\x18\x03 \x01(\x0b\x32\x13.com.avspl1t.Folder\x12\x1b\n\x13seconds_per_segment\x18\x04 \x01(\x05\x12\x0b\n\x03\x63rf\x18\x05 \x01(\x05\"H\n\nJobDetails\x12\x33\n\x0e\x61v1_encode_job\x18\x01 \x01(\x0b\x32\x19.com.avspl1t.AV1EncodeJobH\x00\x42\x05\n\x03job\"\xda\x01\n\x03Job\x12\n\n\x02id\x18\x01 \x01(\t\x12\x10\n\x08\x66inished\x18\x02 \x01(\x08\x12\x0e\n\x06\x66\x61iled\x18\x03 \x01(\x08\x12\x18\n\x10percent_complete\x18\x04 \x01(\x05\x12-\n\x12generated_manifest\x18\x05 \x01(\x0b\x32\x11.com.avspl1t.File\x12,\n\x0bjob_details\x18\x06 \x01(\x0b\x32\x17.com.avspl1t.JobDetails\x12.\n\ncreated_at\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x13\n\x05JobId\x12\n\n\x02id\x18\x01 \x01(\t\"\x83\x01\n\x0eSplitVideoTask\x12%\n\ninput_file\x18\x01 \x01(\x0b\x32\x11.com.avspl1t.File\x12-\n\x10output_directory\x18\x02 \x01(\x0b\x32\x13.com.avspl1t.Folder\x12\x1b\n\x13seconds_per_segment\x18\x03 \x01(\x05\"E\n\x17SplitVideoFinishMessage\x12*\n\x0fgenerated_files\x18\x01 \x03(\x0b\x32\x11.com.avspl1t.File\"\x83\x01\n\x0f\x45ncodeVideoTask\x12%\n\ninput_file\x18\x01 \x01(\x0b\x32\x11.com.avspl1t.File\x12-\n\x10output_directory\x18\x02 \x01(\x0b\x32\x13.com.avspl1t.Folder\x12\x0b\n\x03\x63rf\x18\x03 \x01(\x05\x12\r\n\x05index\x18\x04 \x01(\x05\"E\n\x18\x45ncodeVideoFinishMessage\x12)\n\x0egenerated_file\x18\x01 \x01(\x0b\x32\x11.com.avspl1t.File\"g\n\x14GenerateManifestTask\x12 \n\x05\x66iles\x18\x01 \x03(\x0b\x32\x11.com.avspl1t.File\x12-\n\x10output_directory\x18\x02 \x01(\x0b\x32\x13.com.avspl1t.Folder\"J\n\x1dGenerateManifestFinishMessage\x12)\n\x0egenerated_file\x18\x01 \x01(\x0b\x32\x11.com.avspl1t.File\"\x83\x02\n\x04Task\x12\n\n\x02id\x18\x01 \x01(\t\x12\x37\n\x10split_video_task\x18\x02 \x01(\x0b\x32\x1b.com.avspl1t.SplitVideoTaskH\x00\x12\x39\n\x11\x65ncode_video_task\x18\x03 \x01(\x0b\x32\x1c.com.avspl1t.EncodeVideoTaskH\x00\x12\x43\n\x16generate_manifest_task\x18\x04 \x01(\x0b\x32!.com.avspl1t.GenerateManifestTaskH\x00\x12.\n\ncreated_at\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.TimestampB\x06\n\x04task\"#\n\x0eGetTaskMessage\x12\x11\n\tworker_id\x18\x01 \x01(\t\"6\n\x10HeartbeatMessage\x12\x11\n\tworker_id\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\"\xd2\x02\n\x11\x46inishTaskMessage\x12\x11\n\tworker_id\x18\x01 \x01(\t\x12\x0f\n\x07task_id\x18\x02 \x01(\t\x12\x11\n\tsucceeded\x18\x03 \x01(\x08\x12J\n\x1asplit_video_finish_message\x18\x04 \x01(\x0b\x32$.com.avspl1t.SplitVideoFinishMessageH\x00\x12L\n\x1b\x65ncode_video_finish_message\x18\x05 \x01(\x0b\x32%.com.avspl1t.EncodeVideoFinishMessageH\x00\x12V\n generate_manifest_finish_message\x18\x06 \x01(\x0b\x32*.com.avspl1t.GenerateManifestFinishMessageH\x00\x42\x14\n\x12\x61\x64\x64itional_details\"\x07\n\x05\x45mpty2\xbb\x02\n\x12\x43oordinatorService\x12\x38\n\tSubmitJob\x12\x17.com.avspl1t.JobDetails\x1a\x12.com.avspl1t.JobId\x12.\n\x06GetJob\x12\x12.com.avspl1t.JobId\x1a\x10.com.avspl1t.Job\x12\x39\n\x07GetTask\x12\x1b.com.avspl1t.GetTaskMessage\x1a\x11.com.avspl1t.Task\x12>\n\tHeartbeat\x12\x1d.com.avspl1t.HeartbeatMessage\x1a\x12.com.avspl1t.Empty\x12@\n\nFinishTask\x12\x1e.com.avspl1t.FinishTaskMessage\x1a\x12.com.avspl1t.Emptyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'avspl1t_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_S3CREDENTIALS']._serialized_start=63
  _globals['_S3CREDENTIALS']._serialized_end=162
  _globals['_S3FILE']._serialized_start=164
  _globals['_S3FILE']._serialized_end=251
  _globals['_S3FOLDER']._serialized_start=253
  _globals['_S3FOLDER']._serialized_end=342
  _globals['_FSFILE']._serialized_start=344
  _globals['_FSFILE']._serialized_end=366
  _globals['_FSFOLDER']._serialized_start=368
  _globals['_FSFOLDER']._serialized_end=392
  _globals['_FILE']._serialized_start=394
  _globals['_FILE']._serialized_end=486
  _globals['_FOLDER']._serialized_start=488
  _globals['_FOLDER']._serialized_end=592
  _globals['_AV1ENCODEJOB']._serialized_start=595
  _globals['_AV1ENCODEJOB']._serialized_end=785
  _globals['_JOBDETAILS']._serialized_start=787
  _globals['_JOBDETAILS']._serialized_end=859
  _globals['_JOB']._serialized_start=862
  _globals['_JOB']._serialized_end=1080
  _globals['_JOBID']._serialized_start=1082
  _globals['_JOBID']._serialized_end=1101
  _globals['_SPLITVIDEOTASK']._serialized_start=1104
  _globals['_SPLITVIDEOTASK']._serialized_end=1235
  _globals['_SPLITVIDEOFINISHMESSAGE']._serialized_start=1237
  _globals['_SPLITVIDEOFINISHMESSAGE']._serialized_end=1306
  _globals['_ENCODEVIDEOTASK']._serialized_start=1309
  _globals['_ENCODEVIDEOTASK']._serialized_end=1440
  _globals['_ENCODEVIDEOFINISHMESSAGE']._serialized_start=1442
  _globals['_ENCODEVIDEOFINISHMESSAGE']._serialized_end=1511
  _globals['_GENERATEMANIFESTTASK']._serialized_start=1513
  _globals['_GENERATEMANIFESTTASK']._serialized_end=1616
  _globals['_GENERATEMANIFESTFINISHMESSAGE']._serialized_start=1618
  _globals['_GENERATEMANIFESTFINISHMESSAGE']._serialized_end=1692
  _globals['_TASK']._serialized_start=1695
  _globals['_TASK']._serialized_end=1954
  _globals['_GETTASKMESSAGE']._serialized_start=1956
  _globals['_GETTASKMESSAGE']._serialized_end=1991
  _globals['_HEARTBEATMESSAGE']._serialized_start=1993
  _globals['_HEARTBEATMESSAGE']._serialized_end=2047
  _globals['_FINISHTASKMESSAGE']._serialized_start=2050
  _globals['_FINISHTASKMESSAGE']._serialized_end=2388
  _globals['_EMPTY']._serialized_start=2390
  _globals['_EMPTY']._serialized_end=2397
  _globals['_COORDINATORSERVICE']._serialized_start=2400
  _globals['_COORDINATORSERVICE']._serialized_end=2715
# @@protoc_insertion_point(module_scope)
