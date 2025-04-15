# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from . import avspl1t_pb2 as avspl1t__pb2

GRPC_GENERATED_VERSION = '1.71.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in avspl1t_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class CoordinatorServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SubmitJob = channel.unary_unary(
                '/com.avspl1t.CoordinatorService/SubmitJob',
                request_serializer=avspl1t__pb2.JobDetails.SerializeToString,
                response_deserializer=avspl1t__pb2.JobId.FromString,
                _registered_method=True)
        self.GetJob = channel.unary_unary(
                '/com.avspl1t.CoordinatorService/GetJob',
                request_serializer=avspl1t__pb2.JobId.SerializeToString,
                response_deserializer=avspl1t__pb2.Job.FromString,
                _registered_method=True)
        self.GetTask = channel.unary_unary(
                '/com.avspl1t.CoordinatorService/GetTask',
                request_serializer=avspl1t__pb2.GetTaskMessage.SerializeToString,
                response_deserializer=avspl1t__pb2.Task.FromString,
                _registered_method=True)
        self.Heartbeat = channel.unary_unary(
                '/com.avspl1t.CoordinatorService/Heartbeat',
                request_serializer=avspl1t__pb2.HeartbeatMessage.SerializeToString,
                response_deserializer=avspl1t__pb2.Empty.FromString,
                _registered_method=True)
        self.FinishTask = channel.unary_unary(
                '/com.avspl1t.CoordinatorService/FinishTask',
                request_serializer=avspl1t__pb2.FinishTaskMessage.SerializeToString,
                response_deserializer=avspl1t__pb2.Empty.FromString,
                _registered_method=True)


class CoordinatorServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SubmitJob(self, request, context):
        """returns job ID
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetJob(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTask(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Heartbeat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FinishTask(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CoordinatorServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SubmitJob': grpc.unary_unary_rpc_method_handler(
                    servicer.SubmitJob,
                    request_deserializer=avspl1t__pb2.JobDetails.FromString,
                    response_serializer=avspl1t__pb2.JobId.SerializeToString,
            ),
            'GetJob': grpc.unary_unary_rpc_method_handler(
                    servicer.GetJob,
                    request_deserializer=avspl1t__pb2.JobId.FromString,
                    response_serializer=avspl1t__pb2.Job.SerializeToString,
            ),
            'GetTask': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTask,
                    request_deserializer=avspl1t__pb2.GetTaskMessage.FromString,
                    response_serializer=avspl1t__pb2.Task.SerializeToString,
            ),
            'Heartbeat': grpc.unary_unary_rpc_method_handler(
                    servicer.Heartbeat,
                    request_deserializer=avspl1t__pb2.HeartbeatMessage.FromString,
                    response_serializer=avspl1t__pb2.Empty.SerializeToString,
            ),
            'FinishTask': grpc.unary_unary_rpc_method_handler(
                    servicer.FinishTask,
                    request_deserializer=avspl1t__pb2.FinishTaskMessage.FromString,
                    response_serializer=avspl1t__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'com.avspl1t.CoordinatorService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('com.avspl1t.CoordinatorService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class CoordinatorService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SubmitJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.avspl1t.CoordinatorService/SubmitJob',
            avspl1t__pb2.JobDetails.SerializeToString,
            avspl1t__pb2.JobId.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.avspl1t.CoordinatorService/GetJob',
            avspl1t__pb2.JobId.SerializeToString,
            avspl1t__pb2.Job.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetTask(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.avspl1t.CoordinatorService/GetTask',
            avspl1t__pb2.GetTaskMessage.SerializeToString,
            avspl1t__pb2.Task.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Heartbeat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.avspl1t.CoordinatorService/Heartbeat',
            avspl1t__pb2.HeartbeatMessage.SerializeToString,
            avspl1t__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def FinishTask(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/com.avspl1t.CoordinatorService/FinishTask',
            avspl1t__pb2.FinishTaskMessage.SerializeToString,
            avspl1t__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
