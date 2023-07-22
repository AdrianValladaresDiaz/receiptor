import server.proto.ocr_pb2_grpc as pb
import server.proto.ocr_pb2 as types
import grpc
from io import BytesIO
from PIL import Image
import typing as T

def authorize_request(context: grpc.ServicerContext):
    token = None
    for key, value in context.invocation_metadata():
        if key == "authorization":
            token = value
            break
    
    if token is None:
        return False
    
    return True

class ReceiptsServicer(pb.OCRServicer):
    def __init__(self) -> None:
        super().__init__()

    def Ping(self, request: types.PingRequest, context: grpc.ServicerContext):
        print("got ping!")
        return types.PingResponse(message="Pong")
    
    def UploadImage(self, request_iterator: T.Iterator[types.UploadImageRequest], context: grpc.ServicerContext):
        
        print("Received UploadImage request")
        try:
            # Validate the token from the initial request
            request_is_authorized = authorize_request(context)
            if request_is_authorized is False:
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



