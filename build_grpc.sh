#!/bin/bash

# This script builds the python grpc files then fixes an import naming issue
file_path="./server/proto/ocr_pb2_grpc.py"
line_number=5
new_content="import server.proto.ocr_pb2 as ocr__pb2"

# Move to env
source ./env/bin/activate

# Build grpc
python -m grpc_tools.protoc -I./proto --python_out=./server/proto --pyi_out=./server/proto --grpc_python_out=./server/proto ./proto/ocr.proto
wait

# Check if the file exists
if [ ! -f "$file_path" ]; then
  echo "File does not exist: $file_path"
  exit 1
fi

# Check if line_number is valid
line_count=$(wc -l < "$file_path")
if [ $line_number -lt 1 ] || [ $line_number -gt $line_count ]; then
  echo "Invalid line number. The file has $line_count lines."
  exit 1
fi

# Update the line
sed -i "${line_number}s/.*/$new_content/" "$file_path"

echo "Line $line_number overwritten successfully."