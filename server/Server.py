import server.proto.ocr_pb2_grpc as pb
import server.proto.ocr_pb2 as types
import grpc
import concurrent.futures
import typing
from io import BytesIO
from PIL import Image


class ReceiptsServicer(pb.OCRServicer):
    def __init__(self) -> None:
        super().__init__()

    def Ping(self, request: types.PingRequest, context: grpc.ServicerContext):
        print("got ping!")
        return types.PingResponse(message="Pong")
    
    def UploadImage(self, request_iterator: typing.Iterator[types.UploadImageRequest], context: grpc.ServicerContext):
        print("Received UploadImage request")
        try:
            # Validate the token from the initial request

            token = None
            for key, value in context.invocation_metadata():
                if key == "authorization":
                    token = value
                    break

            print(f'token: {token!r}')
            if token is None:
                # Token not found, handle the error appropriately
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authorization token")

            # We need to accumulate chunks in a buffer otherwise pillow cant open it
            buffer  = BytesIO()
            count  = 0
            for request in request_iterator:
                count = count + 1
                buffer.write(request.chunk)
            
            # Do something with the complete image
            image = Image.open(buffer)
            print(f"Image is {image}")

            image.save("./image.png")

            return types.UploadImageResponse(message="image processed correctly")
        except Exception as e:
            print(e)
            return types.UploadImageResponse(message="Error encountered")



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

