## Generating python boilerplate

Should point everything to the same folder, really:

python -m grpc_tools.protoc -I../../protos --python_out=. --pyi_out=. --grpc_python_out=. ../../protos/route_guide.proto