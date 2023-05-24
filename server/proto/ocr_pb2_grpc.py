# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import server.proto.ocr_pb2 as ocr__pb2


class OCRStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Ping = channel.unary_unary(
                '/OCR/Ping',
                request_serializer=ocr__pb2.PingRequest.SerializeToString,
                response_deserializer=ocr__pb2.PingResponse.FromString,
                )
        self.UploadImage = channel.stream_unary(
                '/OCR/UploadImage',
                request_serializer=ocr__pb2.UploadImageRequest.SerializeToString,
                response_deserializer=ocr__pb2.UploadImageResponse.FromString,
                )


class OCRServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Ping(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UploadImage(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OCRServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Ping': grpc.unary_unary_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=ocr__pb2.PingRequest.FromString,
                    response_serializer=ocr__pb2.PingResponse.SerializeToString,
            ),
            'UploadImage': grpc.stream_unary_rpc_method_handler(
                    servicer.UploadImage,
                    request_deserializer=ocr__pb2.UploadImageRequest.FromString,
                    response_serializer=ocr__pb2.UploadImageResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'OCR', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class OCR(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/OCR/Ping',
            ocr__pb2.PingRequest.SerializeToString,
            ocr__pb2.PingResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UploadImage(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/OCR/UploadImage',
            ocr__pb2.UploadImageRequest.SerializeToString,
            ocr__pb2.UploadImageResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
