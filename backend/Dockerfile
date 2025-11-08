FROM python:3.9

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install grpcio-tools for protobuf generation
RUN pip install grpcio-tools

# Install net-tools for netstat
RUN apt-get update && apt-get install -y net-tools

COPY backend/. .
COPY simulations /app/simulations
COPY proto /app/proto
COPY test.py /app/test.py

# Create the generated directory and generate protobuf files
RUN python -m grpc_tools.protoc -I/app/proto --python_out=/app --grpc_python_out=/app /app/proto/datavault.proto

CMD ["python", "main.py"]
