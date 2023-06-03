## Generating python boilerplate

Should point everything to the same folder, really:

python -m grpc_tools.protoc -I./proto --python_out=./server/proto --pyi_out=./server/proto --grpc_python_out=./server/proto ./proto/ocr.proto

after running that command update line 5 of ./server/proto/ocr_pb2_grpc.py
with this: import server.proto.ocr_pb2 as ocr__pb2