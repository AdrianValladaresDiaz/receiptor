## Generating python boilerplate

Should point everything to the same folder, really:

python -m grpc_tools.protoc -I./proto --python_out=./server/proto --pyi_out=./server/proto --grpc_python_out=./server/proto ./proto/ocr.proto