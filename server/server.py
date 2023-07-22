import server.proto.ocr_pb2_grpc as pb
import server.proto.ocr_pb2 as types
import grpc
import concurrent.futures
import typing
import server.servicer as servicer


class Server:
    def __init__(self) -> None:
        self.servicer = servicer.ReceiptsServicer()
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

