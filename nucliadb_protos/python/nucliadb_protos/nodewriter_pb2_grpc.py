# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from nucliadb_protos import noderesources_pb2 as nucliadb__protos_dot_noderesources__pb2
from nucliadb_protos import nodewriter_pb2 as nucliadb__protos_dot_nodewriter__pb2


class NodeWriterStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetShard = channel.unary_unary(
                '/nodewriter.NodeWriter/GetShard',
                request_serializer=nucliadb__protos_dot_noderesources__pb2.ShardId.SerializeToString,
                response_deserializer=nucliadb__protos_dot_noderesources__pb2.ShardId.FromString,
                )
        self.NewShard = channel.unary_unary(
                '/nodewriter.NodeWriter/NewShard',
                request_serializer=nucliadb__protos_dot_noderesources__pb2.EmptyQuery.SerializeToString,
                response_deserializer=nucliadb__protos_dot_noderesources__pb2.ShardCreated.FromString,
                )
        self.DeleteShard = channel.unary_unary(
                '/nodewriter.NodeWriter/DeleteShard',
                request_serializer=nucliadb__protos_dot_noderesources__pb2.ShardId.SerializeToString,
                response_deserializer=nucliadb__protos_dot_noderesources__pb2.ShardId.FromString,
                )
        self.ListShards = channel.unary_unary(
                '/nodewriter.NodeWriter/ListShards',
                request_serializer=nucliadb__protos_dot_noderesources__pb2.EmptyQuery.SerializeToString,
                response_deserializer=nucliadb__protos_dot_noderesources__pb2.ShardIds.FromString,
                )
        self.GC = channel.unary_unary(
                '/nodewriter.NodeWriter/GC',
                request_serializer=nucliadb__protos_dot_noderesources__pb2.ShardId.SerializeToString,
                response_deserializer=nucliadb__protos_dot_noderesources__pb2.EmptyResponse.FromString,
                )
        self.SetResource = channel.unary_unary(
                '/nodewriter.NodeWriter/SetResource',
                request_serializer=nucliadb__protos_dot_noderesources__pb2.Resource.SerializeToString,
                response_deserializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
                )
        self.RemoveResource = channel.unary_unary(
                '/nodewriter.NodeWriter/RemoveResource',
                request_serializer=nucliadb__protos_dot_noderesources__pb2.ResourceID.SerializeToString,
                response_deserializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
                )
        self.SetRelations = channel.unary_unary(
                '/nodewriter.NodeWriter/SetRelations',
                request_serializer=nucliadb__protos_dot_nodewriter__pb2.SetRelationsRequest.SerializeToString,
                response_deserializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
                )
        self.DelRelations = channel.unary_unary(
                '/nodewriter.NodeWriter/DelRelations',
                request_serializer=nucliadb__protos_dot_nodewriter__pb2.DelRelationsRequest.SerializeToString,
                response_deserializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
                )
        self.SetVectorsField = channel.unary_unary(
                '/nodewriter.NodeWriter/SetVectorsField',
                request_serializer=nucliadb__protos_dot_nodewriter__pb2.SetVectorFieldRequest.SerializeToString,
                response_deserializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
                )
        self.DelVectorsField = channel.unary_unary(
                '/nodewriter.NodeWriter/DelVectorsField',
                request_serializer=nucliadb__protos_dot_nodewriter__pb2.DelVectorFieldRequest.SerializeToString,
                response_deserializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
                )


class NodeWriterServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetShard(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def NewShard(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteShard(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListShards(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GC(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetResource(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveResource(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetRelations(self, request, context):
        """Graph
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DelRelations(self, request, context):
        """Set relations on a resource
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetVectorsField(self, request, context):
        """Vectors
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DelVectorsField(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NodeWriterServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetShard': grpc.unary_unary_rpc_method_handler(
                    servicer.GetShard,
                    request_deserializer=nucliadb__protos_dot_noderesources__pb2.ShardId.FromString,
                    response_serializer=nucliadb__protos_dot_noderesources__pb2.ShardId.SerializeToString,
            ),
            'NewShard': grpc.unary_unary_rpc_method_handler(
                    servicer.NewShard,
                    request_deserializer=nucliadb__protos_dot_noderesources__pb2.EmptyQuery.FromString,
                    response_serializer=nucliadb__protos_dot_noderesources__pb2.ShardCreated.SerializeToString,
            ),
            'DeleteShard': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteShard,
                    request_deserializer=nucliadb__protos_dot_noderesources__pb2.ShardId.FromString,
                    response_serializer=nucliadb__protos_dot_noderesources__pb2.ShardId.SerializeToString,
            ),
            'ListShards': grpc.unary_unary_rpc_method_handler(
                    servicer.ListShards,
                    request_deserializer=nucliadb__protos_dot_noderesources__pb2.EmptyQuery.FromString,
                    response_serializer=nucliadb__protos_dot_noderesources__pb2.ShardIds.SerializeToString,
            ),
            'GC': grpc.unary_unary_rpc_method_handler(
                    servicer.GC,
                    request_deserializer=nucliadb__protos_dot_noderesources__pb2.ShardId.FromString,
                    response_serializer=nucliadb__protos_dot_noderesources__pb2.EmptyResponse.SerializeToString,
            ),
            'SetResource': grpc.unary_unary_rpc_method_handler(
                    servicer.SetResource,
                    request_deserializer=nucliadb__protos_dot_noderesources__pb2.Resource.FromString,
                    response_serializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.SerializeToString,
            ),
            'RemoveResource': grpc.unary_unary_rpc_method_handler(
                    servicer.RemoveResource,
                    request_deserializer=nucliadb__protos_dot_noderesources__pb2.ResourceID.FromString,
                    response_serializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.SerializeToString,
            ),
            'SetRelations': grpc.unary_unary_rpc_method_handler(
                    servicer.SetRelations,
                    request_deserializer=nucliadb__protos_dot_nodewriter__pb2.SetRelationsRequest.FromString,
                    response_serializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.SerializeToString,
            ),
            'DelRelations': grpc.unary_unary_rpc_method_handler(
                    servicer.DelRelations,
                    request_deserializer=nucliadb__protos_dot_nodewriter__pb2.DelRelationsRequest.FromString,
                    response_serializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.SerializeToString,
            ),
            'SetVectorsField': grpc.unary_unary_rpc_method_handler(
                    servicer.SetVectorsField,
                    request_deserializer=nucliadb__protos_dot_nodewriter__pb2.SetVectorFieldRequest.FromString,
                    response_serializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.SerializeToString,
            ),
            'DelVectorsField': grpc.unary_unary_rpc_method_handler(
                    servicer.DelVectorsField,
                    request_deserializer=nucliadb__protos_dot_nodewriter__pb2.DelVectorFieldRequest.FromString,
                    response_serializer=nucliadb__protos_dot_nodewriter__pb2.OpStatus.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'nodewriter.NodeWriter', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class NodeWriter(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetShard(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/GetShard',
            nucliadb__protos_dot_noderesources__pb2.ShardId.SerializeToString,
            nucliadb__protos_dot_noderesources__pb2.ShardId.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def NewShard(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/NewShard',
            nucliadb__protos_dot_noderesources__pb2.EmptyQuery.SerializeToString,
            nucliadb__protos_dot_noderesources__pb2.ShardCreated.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteShard(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/DeleteShard',
            nucliadb__protos_dot_noderesources__pb2.ShardId.SerializeToString,
            nucliadb__protos_dot_noderesources__pb2.ShardId.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListShards(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/ListShards',
            nucliadb__protos_dot_noderesources__pb2.EmptyQuery.SerializeToString,
            nucliadb__protos_dot_noderesources__pb2.ShardIds.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GC(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/GC',
            nucliadb__protos_dot_noderesources__pb2.ShardId.SerializeToString,
            nucliadb__protos_dot_noderesources__pb2.EmptyResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetResource(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/SetResource',
            nucliadb__protos_dot_noderesources__pb2.Resource.SerializeToString,
            nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RemoveResource(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/RemoveResource',
            nucliadb__protos_dot_noderesources__pb2.ResourceID.SerializeToString,
            nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetRelations(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/SetRelations',
            nucliadb__protos_dot_nodewriter__pb2.SetRelationsRequest.SerializeToString,
            nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DelRelations(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/DelRelations',
            nucliadb__protos_dot_nodewriter__pb2.DelRelationsRequest.SerializeToString,
            nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetVectorsField(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/SetVectorsField',
            nucliadb__protos_dot_nodewriter__pb2.SetVectorFieldRequest.SerializeToString,
            nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DelVectorsField(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeWriter/DelVectorsField',
            nucliadb__protos_dot_nodewriter__pb2.DelVectorFieldRequest.SerializeToString,
            nucliadb__protos_dot_nodewriter__pb2.OpStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class NodeSidecarStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetCount = channel.unary_unary(
                '/nodewriter.NodeSidecar/GetCount',
                request_serializer=nucliadb__protos_dot_noderesources__pb2.ShardId.SerializeToString,
                response_deserializer=nucliadb__protos_dot_nodewriter__pb2.Counter.FromString,
                )


class NodeSidecarServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetCount(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NodeSidecarServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetCount': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCount,
                    request_deserializer=nucliadb__protos_dot_noderesources__pb2.ShardId.FromString,
                    response_serializer=nucliadb__protos_dot_nodewriter__pb2.Counter.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'nodewriter.NodeSidecar', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class NodeSidecar(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetCount(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nodewriter.NodeSidecar/GetCount',
            nucliadb__protos_dot_noderesources__pb2.ShardId.SerializeToString,
            nucliadb__protos_dot_nodewriter__pb2.Counter.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
