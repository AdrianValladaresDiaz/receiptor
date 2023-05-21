import server.proto.ocr_pb2_grpc as pb
import server.proto.ocr_pb2 as types
import grpc
import concurrent.futures


class ReceiptsServicer(pb.OCRServicer):
    def __init__(self) -> None:
        super().__init__()

    def Ping(self, request: types.PingRequest, context: grpc.ServicerContext):
        print("got ping!")
        return types.PingResponse(message="Pong")


class Server:
    def __init__(self) -> None:
        self.servicer = ReceiptsServicer()
        server = grpc.server(
            concurrent.futures.ThreadPoolExecutor(max_workers=10)
        )
        pb.add_OCRServicer_to_server(self.servicer,server)
        server.add_insecure_port('[::]:50051')
        self._server = server

    def start(self)-> "Server":
        print("starting.....")
        self._server.start()
        self._server.wait_for_termination()
        return self

