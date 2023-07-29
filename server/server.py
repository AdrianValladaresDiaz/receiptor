import server.proto.ocr_pb2_grpc as pb
import grpc
import concurrent.futures
import server.servicer as servicer
import logging

class Server:
    def __init__(self, logger:logging.Logger, port: str) -> None:
        self.servicer = servicer.ReceiptsServicer()
        server = grpc.server(
            concurrent.futures.ThreadPoolExecutor(max_workers=10)
        )
        pb.add_OCRServicer_to_server(self.servicer,server)
        self.port = port
        server.add_insecure_port(self.port)
        self._server = server   
        self.logger = logger

    def start(self)-> "Server":
        self.logger.info(f"starting server in port {self.port}")
        self._server.start()
        self._server.wait_for_termination()
        return self

